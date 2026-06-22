"""
live_scalper_engine.py — Live Scalper Engine
Completely separate from research. Writes to live_positions only.
Reads bot configs from DB (S58 bots, is_template=FALSE, trading_on=TRUE).
Imports shared signal logic from scalper_signals.py.
"""
import threading
import time
from collections import defaultdict, deque
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from scalper_signals import check_entry_signal, check_stop_loss, calc_pnl, get_btc_regime

# Refresh bot list every N seconds
BOT_REFRESH_INTERVAL = 60

class LiveScalperEngine:
    def __init__(self):
        db.init_pool()
        self.price_history = defaultdict(lambda: deque(maxlen=1000))
        self.active = {}        # {(bot_id, coin): position_data}
        self.cooldowns = {}     # {(bot_id, coin): timestamp}
        self.live_bots = []     # loaded from DB
        self._lock = threading.Lock()
        import redis as _redis
        self.r = _redis.Redis(host='localhost', port=6379, decode_responses=True)
        self._load_bots()
        self._cleanup_stuck_positions()
        self._start_cleanup_thread()
        self._start_bot_refresh_thread()
        print(f'✅ LiveScalperEngine initialized · {len(self.live_bots)} active bots')

    def _load_bots(self):
        """Load active S58 live bots from DB."""
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT b.id, b.name, b.user_id, b.base_order,
                           b.bot_params::text, b.wallet_id,
                           b.trades_per_bot, b.entry_method,
                           b.reserve_floor, b.resume_threshold,
                           b.auto_resume, b.floor_paused,
                           vw.current_balance
                    FROM bots b
                    LEFT JOIN virtual_wallets vw ON b.wallet_id = vw.id
                    WHERE b.method='S58'
                    AND b.is_template=FALSE
                    AND b.is_research=FALSE
                    AND b.trading_on=TRUE
                    AND b.status='open'
                    AND b.status!='deleted'
                """)
                rows = cur.fetchall()

            import json
            bots = []
            for bot_id, name, user_id, base_order, params_raw, wallet_id, trades_per_bot, db_entry_method, reserve_floor, resume_threshold, auto_resume, floor_paused, current_balance in rows:
                try:
                    p = json.loads(params_raw) if params_raw else {}
                except:
                    p = {}
                entry_method = db_entry_method or p.get('entry_method', 'fixed')
                bots.append({
                    'id': bot_id,
                    'name': name,
                    'user_id': user_id,
                    'base_order': float(base_order or 2),
                    'trigger_pct': float(p.get('trigger_pct', 10)),
                    'window_sec': float(p.get('window_sec', 5)),
                    'hold_sec': int(p.get('hold_sec', 30)),
                    'stop_loss_pct': p.get('stop_loss_pct'),
                    'wallet_id': wallet_id,
                    'trades_per_bot': int(trades_per_bot or 999),
                    'entry_method': entry_method,
                    'smart_mode': entry_method == 'smart',
                    'reserve_floor': float(reserve_floor) if reserve_floor is not None else None,
                    'resume_threshold': float(resume_threshold) if resume_threshold is not None else None,
                    'auto_resume': auto_resume if auto_resume is not None else True,
                    'floor_paused': db.check_and_update_floor_state(
                        bot_id, name, float(current_balance or 0),
                        float(reserve_floor) if reserve_floor is not None else None,
                        float(resume_threshold) if resume_threshold is not None else None,
                        auto_resume if auto_resume is not None else True,
                        floor_paused or False
                    ),
                    'account_in_debt': db.is_reserve_in_debt(user_id),
                })
            # Load current scalper champion for smart-mode bots
            scalper_champion = None
            try:
                import redis as _r
                import json as _j2
                _rc = _r.Redis(host='localhost', port=6379, decode_responses=True)
                btc_raw = _rc.get('btc:regime_data')
                regime = _j2.loads(btc_raw).get('btc_regime','bear') if btc_raw else 'bear'
                with db.get_db() as _conn2:
                    _cur2 = _conn2.cursor()
                    _cur2.execute("""
                        SELECT ch.method_id, b.bot_params, b.method
                        FROM champion_history ch
                        LEFT JOIN bots b ON b.name=ch.method_id
                        WHERE ch.is_active_champion=TRUE
                        AND ch.system_type='SCALPER'
                        AND ch.regime=%s
                    """, (regime,))
                    row = _cur2.fetchone()
                    if row:
                        scalper_champion = {
                            'bot_name': row[0],
                            'bot_params': row[1] or {},
                            'method_family': row[2] or row[0],
                        }
            except Exception as _ce:
                print(f'⚠️ Scalper champion lookup failed: {_ce}')

            # Inject champion params into smart-mode bots
            for bot in bots:
                if bot.get('smart_mode') and scalper_champion:
                    cp = scalper_champion['bot_params']
                    bot['trigger_pct'] = float(cp.get('trigger_pct', bot['trigger_pct']))
                    bot['window_sec'] = float(cp.get('window_sec', bot['window_sec']))
                    bot['hold_sec'] = int(cp.get('hold_sec', bot['hold_sec']))
                    bot['stop_loss_pct'] = cp.get('stop_loss_pct', bot['stop_loss_pct'])
                    bot['_champion'] = scalper_champion
                    print(f'🧠 Scalper Smart: {bot["name"]} using champion {scalper_champion["bot_name"]}')

            self.live_bots = bots
            print(f'🔄 LiveScalper: loaded {len(bots)} bots')
        except Exception as e:
            print(f'⚠️ LiveScalper bot load error: {e}')

    def _start_bot_refresh_thread(self):
        """Refresh bot list periodically to pick up new/stopped bots."""
        def refresh_loop():
            while True:
                time.sleep(BOT_REFRESH_INTERVAL)
                try:
                    self._load_bots()
                except Exception as e:
                    # FIXED June 20 2026 - same failure class as the
                    # live DCA outage found earlier today: an
                    # uncaught exception here would silently kill
                    # this thread forever, freezing self.live_bots at
                    # whatever it last loaded, with zero visibility.
                    print(f'\u26a0\ufe0f Scalper refresh_loop error (continuing): {e}')
        t = threading.Thread(target=refresh_loop, daemon=True)
        t.start()

    def _cleanup_stuck_positions(self):
        """Close positions stuck longer than 2x hold_seconds."""
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, coin, entry_price, hold_seconds, base_order,
                           EXTRACT(EPOCH FROM (NOW() - entry_time))::int as seconds_open
                    FROM live_positions
                    WHERE status='open'
                    AND EXTRACT(EPOCH FROM (NOW() - entry_time)) > hold_seconds * 2
                """)
                stuck = cur.fetchall()

            closed = 0
            for pos_id, coin, entry_price, hold_sec, base_order, seconds_open in stuck:
                history = self.price_history.get(coin)
                exit_price = float(history[-1][1]) if history else float(entry_price)
                pnl_pct, pnl_usdt = calc_pnl(float(entry_price), exit_price, float(base_order or 2))
                with db.get_db() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE live_positions SET
                            exit_price=%s, exit_time=NOW(),
                            pnl_pct=%s, pnl_usdt=%s,
                            exit_reason='timer_recovery', status='closed'
                        WHERE id=%s
                    """, (exit_price, pnl_pct, pnl_usdt, pos_id))
                closed += 1
            if closed > 0:
                print(f'🔧 LiveScalper: cleaned {closed} stuck positions')
        except Exception as e:
            print(f'⚠️ LiveScalper cleanup error: {e}')

    def _start_cleanup_thread(self):
        def cleanup_loop():
            while True:
                time.sleep(30)
                try:
                    self._cleanup_stuck_positions()
                except Exception as e:
                    print(f'\u26a0\ufe0f Scalper cleanup_loop error (continuing): {e}')
        t = threading.Thread(target=cleanup_loop, daemon=True)
        t.start()

    def on_price(self, coin, price):
        """Called by WebSocket on every price update."""
        now = time.time()
        self.price_history[coin].append((now, price))

        for bot in self.live_bots:
            self._check_entry(bot, coin, price, now)

        self._update_active(coin, price, now)

    def _check_entry(self, bot, coin, price, now):
        # Reserve floor gate (ADDED June 20 2026) - never opens a new
        # entry while floor_paused, which was already computed once
        # per bot-refresh cycle in _load_bots, not on every tick.
        if bot.get('floor_paused'):
            return
        # Account-level reserve debt gate (ADDED June 20 2026) -
        # separate mechanism, also computed once per refresh cycle.
        if bot.get('account_in_debt'):
            return
        import system_gates
        if not system_gates.is_new_trade_allowed(
            'scalper', exchange_name=bot.get('exchange_name'),
            is_research=bot.get('is_research', False)
        ):
            return
        key = (bot['id'], coin)
        # Skip if already have open position for this bot+coin
        with self._lock:
            if key in self.active:
                return
        # Use shared signal logic
        bot_signal = {
            'name': str(bot['id']),
            'trigger_pct': bot['trigger_pct'],
            'window_sec': bot['window_sec'],
            'hold_sec': bot['hold_sec'],
            'stop_loss_pct': bot.get('stop_loss_pct'),
        }
        jump_pct = check_entry_signal(
            bot_signal, coin, price, now,
            self.price_history, self.active, self.cooldowns
        )
        if jump_pct is not None:
            self._open_position(bot, coin, price, jump_pct, now)

    def _open_position(self, bot, coin, price, trigger_jump, now):
        key = (bot['id'], coin)
        try:
            btc_price, btc_sma50, btc_24h, btc_regime, btc_dom = get_btc_regime(self.r)
            base_order = float(bot['base_order'])
            with db.get_db() as conn:
                cur = conn.cursor()

                # Check wallet balance — bot stays ON but skips if insufficient funds
                wallet_id = bot.get('wallet_id')
                if wallet_id:
                    cur.execute("""
                        SELECT current_balance FROM virtual_wallets
                        WHERE id=%s FOR UPDATE
                    """, (wallet_id,))
                    row = cur.fetchone()
                    if not row or float(row[0]) < base_order:
                        return  # No funds — skip trade silently

                    available = float(row[0])
                    new_balance = available - base_order

                    # Deduct from wallet
                    cur.execute("""
                        UPDATE virtual_wallets
                        SET current_balance=%s,
                            committed_usdt=committed_usdt + %s,
                            updated_at=NOW()
                        WHERE id=%s
                    """, (new_balance, base_order, wallet_id))

                cur.execute("""
                    INSERT INTO live_positions
                        (bot_id, user_id, coin, entry_price, hold_seconds,
                         trigger_jump_pct, trigger_window_sec,
                         stop_loss_pct, base_order, status,
                         btc_price_at_entry, btc_sma50_at_entry,
                         btc_24h_change_pct, btc_regime, btc_dominance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'open',
                            %s, %s, %s, %s, %s)
                    RETURNING id
                """, (bot['id'], bot['user_id'], coin, price,
                      bot['hold_sec'], trigger_jump, bot['window_sec'],
                      bot.get('stop_loss_pct'), base_order,
                      btc_price, btc_sma50, btc_24h, btc_regime, btc_dom))
                pos_id = cur.fetchone()[0]

                # Log wallet transaction
                if wallet_id:
                    cur.execute("""
                        INSERT INTO wallet_transactions
                            (wallet_id, position_id, type, amount,
                             balance_before, balance_after, reference_type, note)
                        VALUES (%s, %s, 'debit', %s, %s, %s, 'scalper', %s)
                    """, (wallet_id, pos_id, base_order,
                            available, new_balance, f'Open {coin}'))

            with self._lock:
                self.active[key] = {
                    'pos_id': pos_id,
                    'entry_price': price,
                    'entry_time': now,
                    'hold_sec': bot['hold_sec'],
                    'wallet_id': bot.get('wallet_id'),
                    'base_order': base_order,
                    'stop_loss_pct': bot.get('stop_loss_pct'),
                    'base_order': bot['base_order'],
                    'max_profit': 0.0,
                    'max_loss': 0.0,
                    'user_id': bot['user_id'],
                    'bot_name': bot['name'],
                }

            print(f'⚡ LIVE SCALP OPEN: {bot["name"]} {coin} @ ${price:.8f} jump={trigger_jump:.2f}%')

            # Schedule auto-exit. Wrapped (ADDED June 20 2026) so an
            # uncaught exception in _exit_position when this timer
            # fires can't leave the position silently stuck open
            # forever with just an unseen stderr traceback.
            def _safe_exit():
                try:
                    self._exit_position(key, 'timer')
                except Exception as e:
                    print(f'\u26a0\ufe0f Scalper timer-exit error for {key}: {e}')
            t = threading.Timer(bot['hold_sec'], _safe_exit)
            t.daemon = True
            t.start()

        except Exception as e:
            print(f'⚠️ LiveScalper open error: {e}')

    def _update_active(self, coin, price, now):
        with self._lock:
            keys_to_exit = []
            for key, pos in self.active.items():
                if key[1] != coin:
                    continue
                entry = pos['entry_price']
                if entry == 0:
                    continue
                pnl_pct = (price - entry) / entry * 100
                pos['max_profit'] = max(pos['max_profit'], pnl_pct)
                pos['max_loss'] = min(pos['max_loss'], pnl_pct)
                pos_data = {
                    'entry_price': entry,
                    'stop_loss_pct': pos.get('stop_loss_pct'),
                }
                if check_stop_loss(pos_data, price):
                    keys_to_exit.append((key, 'stop_loss'))

        for key, reason in keys_to_exit:
            self._exit_position(key, reason)

    def _exit_position(self, key, reason):
        with self._lock:
            pos = self.active.pop(key, None)
        if pos is None:
            return

        coin = key[1]
        history = self.price_history.get(coin)
        exit_price = float(history[-1][1]) if history else pos['entry_price']
        pnl_pct, pnl_usdt = calc_pnl(pos['entry_price'], exit_price, pos['base_order'])

        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE live_positions SET
                        exit_price=%s, exit_time=NOW(),
                        max_profit_seen=%s, max_loss_seen=%s,
                        pnl_pct=%s, pnl_usdt=%s,
                        exit_reason=%s, status='closed'
                    WHERE id=%s
                """, (exit_price, pos['max_profit'], pos['max_loss'],
                      pnl_pct, pnl_usdt, reason, pos['pos_id']))

                # Return funds to wallet
                wallet_id = pos.get('wallet_id')
                base_order = float(pos.get('base_order', 2))
                if wallet_id:
                    cur.execute("""
                        SELECT current_balance FROM virtual_wallets WHERE id=%s
                    """, (wallet_id,))
                    row = cur.fetchone()
                    if row:
                        available = float(row[0])
                        returned = base_order + float(pnl_usdt)
                        new_balance = available + returned
                        cur.execute("""
                            UPDATE virtual_wallets
                            SET current_balance=%s,
                                committed_usdt=GREATEST(0, committed_usdt - %s),
                                updated_at=NOW()
                            WHERE id=%s
                        """, (new_balance, base_order, wallet_id))
                        cur.execute("""
                            INSERT INTO wallet_transactions
                                (wallet_id, position_id, type, amount,
                                 balance_before, balance_after, reference_type, note)
                            VALUES (%s, %s, 'credit', %s, %s, %s, 'scalper', %s)
                        """, (wallet_id, pos['pos_id'], returned,
                                available, new_balance,
                                f'Close {key[1]} {reason} pnl={pnl_pct:.2f}%'))
                conn.commit()

            # Deduct performance fee on profit. ADDED June 20 2026 -
            # scalper had ZERO fee collection before this, confirmed
            # via grep. Same rule as DCA: 20% default, respects
            # is_zero_fee/fee_override, skips research/admin accounts.
            if float(pnl_usdt) > 0:
                try:
                    user_id = pos.get('user_id')
                    if user_id:
                        with db.get_db() as _fc:
                            _cur = _fc.cursor()
                            _cur.execute("""
                                SELECT is_research_account, is_admin,
                                       is_zero_fee, fee_override
                                FROM users WHERE id=%s
                            """, (user_id,))
                            _urow = _cur.fetchone()
                        _skip_fee = _urow and (_urow[0] or _urow[1] or _urow[2])
                        if not _skip_fee:
                            _fee_pct = float(_urow[3]) if _urow and _urow[3] is not None else 20.0
                            fee = float(pnl_usdt) * (_fee_pct / 100)
                            db.deduct_performance_fee(user_id, pos['pos_id'], fee, float(pnl_usdt))
                            print(f'💰 Scalper fee: {pos.get("bot_name")} ${fee:.4f} ({_fee_pct}%)')
                except Exception as _fee_e:
                    print(f'⚠️ Scalper fee deduction error: {_fee_e}')

            # Set cooldown 5 min
            self.cooldowns[key] = time.time() + 300

            emoji = '💚' if pnl_pct > 0 else '❤️'
            print(f'{emoji} LIVE SCALP CLOSE: {key[0]} {coin} {reason} pnl={pnl_pct:.2f}% (${pnl_usdt:.4f})')

        except Exception as e:
            print(f'⚠️ LiveScalper exit error: {e}')


# ── Global instance ──
_live_scalper = None

def get_live_scalper():
    global _live_scalper
    if _live_scalper is None:
        _live_scalper = LiveScalperEngine()
    return _live_scalper

def on_price_update(coin, price):
    """Called from WebSocket price handler."""
    try:
        get_live_scalper().on_price(coin, price)
    except Exception as e:
        pass
