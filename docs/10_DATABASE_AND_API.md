# Database and API

> Database schema · API endpoints · technical backend structure.

---

## Database

- SQLite with WAL mode (Write-Ahead Logging)
- WAL allows reads while writing — no blocking
- Located at: averion.db (Replit) · /home/averion/Averion/averion.db (Hetzner)
- Backup daily at 3am → /backups/averion_YYYY-MM-DD.db
- Keep last 7 days of backups only
- Migrate to PostgreSQL at Phase 6 (multi-user)

---

## Current Tables (Phase 1-3)

### positions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique position ID |
| coin | TEXT | e.g. RVN/USDT |
| status | TEXT | open · closed |
| avg_cost | REAL | Weighted average buy price |
| quantity | REAL | Total coin quantity held |
| total_invested | REAL | Total USDT invested |
| dca_count | INTEGER | Number of DCA buys made |
| last_buy_price | REAL | Price of most recent buy |
| tp_armed | BOOLEAN | Trailing TP activated |
| queued | BOOLEAN | In smart queue |
| peak_price | REAL | Highest price seen since TP armed |
| opened_at | DATETIME | When position first opened |
| closed_at | DATETIME | When position closed |

### trades
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique trade ID |
| position_id | INTEGER | Links to positions table |
| coin | TEXT | e.g. RVN/USDT |
| side | TEXT | buy · sell |
| price | REAL | Execution price |
| quantity | REAL | Coin quantity |
| usdt_amount | REAL | USDT value |
| reason | TEXT | entry · dca · tp · manual |
| paper | BOOLEAN | Paper or live trade |
| timestamp | DATETIME | When executed |

### balance_history
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique ID |
| exchange | TEXT | Exchange name |
| value_usdt | REAL | Total balance in USDT |
| recorded_at | DATETIME | Snapshot timestamp |

---

## New Tables (Phase 4-5)

### ohlcv_hourly
- coin · exchange · timestamp · open · high · low · close · volume
- atr_14 · volatility
- 90-day rolling window — oldest deleted as new arrives
- ~28M rows estimated (1,870 coins x 7 exchanges x 90d x 24h)

### coin_history
- coin · real_cap · recorded_cap · category
- volume_24h · confidence_days · recorded_at
- Stores classification history forever

### strategy_versions
- method · version · parameters_json
- date_created · parent_version · cooldown_until

### review_decisions
- date · method · version · change · reasoning
- evidence · hypothesis · confidence
- approved_by · outcome_status

### bots
- id · exchange_id · name · method
- trading_on · dca_on · reserve_floor · resume_threshold
- auto_resume · profit_coin · max_trades · settings_json

### exchanges
- id · user_id · exchange · custom_name
- api_key_enc · secret_enc · uid_fingerprint · active

### reserve_wallets
- id · user_id · balance_usdt
- total_deposited · total_deducted · last_updated

### referrals
- id · referrer_user_id · referred_user_id
- created_at · total_earned

### owner_balance
- accumulated_fees_usdt · last_transfer_date
- last_transfer_amount · total_transferred_all_time

---

## API Endpoints — Current (Phase 3)

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | /dashboard | Serve dashboard.html |
| GET | /status | Bot status + BTC price |
| GET | /positions | Open positions with live P&L |
| GET | /trades | Last 50 trades |
| GET | /history | Closed positions + realized P&L |
| GET | /balance-history | Capital chart data |
| GET | /config | Current config.py values |
| POST | /config | Update config from dashboard |
| POST | /start | Start bot loop |
| POST | /stop | Stop bot loop |
| POST | /positions/{id}/close | Close position (market sell) |
| POST | /positions/{id}/add | Add funds to position |
| POST | /record-balance | Save daily balance snapshot |

---

## API Endpoints — Planned (Phase 5-7)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | /webhooks/tradingview | TradingView open signals |
| GET/POST | /bots | Create · read · update · delete bots |
| GET/POST | /exchanges | Manage exchange connections |
| GET | /research/api/v1/summary | All methods ranked (read-only) |
| GET | /research/api/v1/method/{id} | Single method full history |
| GET | /research/share/{token} | Temporary signed research URL |
| GET | /{ADMIN_PATH} | Admin panel (secret URL from .env) |
| POST | /stripe/webhook | Stripe billing events (Phase 7) |
| GET | /health | Health check endpoint |

---

## Security

- API keys encrypted with Fernet before storing in DB
- Admin URL stored in .env only — never in code
- CORS — non-averion.app domains blocked
- Rate limiting per user on all endpoints
- Research API: read-only GET only — no mutations
- Signed URLs: 7-day expiry for research sharing
- Withdrawal permissions NEVER enabled on exchange API keys

---

## Exchange Connection Flow

1. User enters API key + secret in Add Exchange modal
2. System tests connection via CCXT
3. If valid → encrypt with Fernet → store in DB
4. UID fingerprint captured for anti-fraud Layer 2
5. Exchange appears in Home tab exchange cards
6. Bot can now trade on this exchange

---

## Data Flow Per 60-Second Cycle

1. Fetch live prices for all coins (CCXT)
2. Check each open position:
   a. Has price dropped X% from last buy? → DCA queue
   b. Has price reached TP target? → Arm trailing
   c. Is trailing armed and price pulled back? → Market sell
3. Execute smart queue (one DCA per cycle)
4. Update all P&L calculations
5. Check ST flags on all exchanges
6. Save any new trades to DB
7. Sleep until next cycle

## Virtual Wallet Tables (Phase 5)

### virtual_wallets
- id · user_id · exchange_id
- name (user defined e.g. Long Test 1)
- currency (USDT · RVN · BTC etc)
- allocation_type (fixed · all)
- allocation_amount (fixed amount · null if all)
- current_balance
- created_at · updated_at

### wallet_bot_assignments
- id · wallet_id · bot_id
- assigned_at
- unassigned_at (null if still active)

### wallet_transactions
- id · wallet_id · position_id
- type (deposit · dca_debit · tp_credit · fee_debit)
- amount · balance_after
- created_at

### How bots share capital
- Same wallet = shared balance + shared queue
- Different wallet = isolated balance + isolated queue
- wallet_transactions tracks every movement
- Full audit trail per wallet per bot
