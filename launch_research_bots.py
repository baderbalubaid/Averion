"""
launch_research_bots.py — Creates all 261 research bots in DB
trading_on=FALSE · trades_per_bot=0 until manually enabled
Run once to populate · safe to re-run (skips existing names)
"""

import json
from dotenv import load_dotenv
load_dotenv()
import database as db
db.init_pool()

# ═══════════════════════════════
# SHARED DCA PARAMETERS (identical for all research bots)
# ═══════════════════════════════
DCA = dict(
    user_id=1, exchange_id=2, wallet_id=1,
    direction='long', trading_on=False, dca_on=True,
    base_order=100.0, dca_percent=7.0,
    spacing_multiplier=1.4, size_multiplier=1.5,
    take_profit_percent=5.0, trailing_percent=2.0,
    reserve_floor=50.0, is_paper=True,
    status='open', trades_per_bot=0, trades_per_coin=1,
    order_entry_type='market', order_dca_type='market',
)

# ═══════════════════════════════
# ALL 261 BOTS DEFINITION
# ═══════════════════════════════
BOTS = [

# ── E1 — VWAP + RSI + ATR (12 bots) ──
('E1-1',  'E1', {'rsi_threshold':25,'vwap_pct':4.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-2',  'E1', {'rsi_threshold':30,'vwap_pct':4.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-3',  'E1', {'rsi_threshold':35,'vwap_pct':4.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-4',  'E1', {'rsi_threshold':25,'vwap_pct':3.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-5',  'E1', {'rsi_threshold':30,'vwap_pct':3.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-6',  'E1', {'rsi_threshold':35,'vwap_pct':3.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-7',  'E1', {'rsi_threshold':25,'vwap_pct':2.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-8',  'E1', {'rsi_threshold':30,'vwap_pct':2.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-9',  'E1', {'rsi_threshold':35,'vwap_pct':2.0,'atr_mult':1.5,'bounce_pct':65}),
('E1-10', 'E1', {'rsi_threshold':30,'vwap_pct':3.0,'atr_mult':1.3,'bounce_pct':65}),
('E1-11', 'E1', {'rsi_threshold':30,'vwap_pct':3.0,'atr_mult':1.5,'bounce_pct':55}),
('E1-12', 'E1', {'rsi_threshold':35,'vwap_pct':2.0,'atr_mult':1.3,'bounce_pct':55}),

# ── E2 — Panic Exhaustion (9 bots) ──
('E2-1',  'E2', {'vol_mult':1.5,'bb_sigma':2.0,'recovery_pct':0.5}),
('E2-2',  'E2', {'vol_mult':2.0,'bb_sigma':2.0,'recovery_pct':0.5}),
('E2-3',  'E2', {'vol_mult':3.0,'bb_sigma':2.0,'recovery_pct':0.5}),
('E2-4',  'E2', {'vol_mult':1.5,'bb_sigma':2.5,'recovery_pct':0.5}),
('E2-5',  'E2', {'vol_mult':2.0,'bb_sigma':2.5,'recovery_pct':0.5}),
('E2-6',  'E2', {'vol_mult':3.0,'bb_sigma':2.5,'recovery_pct':0.5}),
('E2-7',  'E2', {'vol_mult':2.0,'bb_sigma':2.0,'recovery_pct':1.0}),
('E2-8',  'E2', {'vol_mult':2.0,'bb_sigma':2.5,'recovery_pct':1.0}),
('E2-9',  'E2', {'vol_mult':3.0,'bb_sigma':2.5,'recovery_pct':1.0}),

# ── E3 — Volume Climax (12 bots) ──
('E3-1',  'E3', {'vol_mult':3.0,'range_atr':2.0,'close_upper':40}),
('E3-2',  'E3', {'vol_mult':4.0,'range_atr':2.0,'close_upper':40}),
('E3-3',  'E3', {'vol_mult':5.0,'range_atr':2.0,'close_upper':40}),
('E3-4',  'E3', {'vol_mult':3.0,'range_atr':2.5,'close_upper':50}),
('E3-5',  'E3', {'vol_mult':4.0,'range_atr':2.5,'close_upper':50}),
('E3-6',  'E3', {'vol_mult':5.0,'range_atr':2.5,'close_upper':50}),
('E3-7',  'E3', {'vol_mult':3.0,'range_atr':3.0,'close_upper':60}),
('E3-8',  'E3', {'vol_mult':4.0,'range_atr':3.0,'close_upper':60}),
('E3-9',  'E3', {'vol_mult':5.0,'range_atr':3.0,'close_upper':60}),
('E3-10', 'E3', {'vol_mult':4.0,'range_atr':2.0,'close_upper':60}),
('E3-11', 'E3', {'vol_mult':4.0,'range_atr':3.0,'close_upper':40}),
('E3-12', 'E3', {'vol_mult':5.0,'range_atr':3.0,'close_upper':50}),

# ── E4 — Time Cycle (9 bots) ──
('E4-1',  'E4', {'sma_period':1}),
('E4-2',  'E4', {'sma_period':1}),
('E4-3',  'E4', {'sma_period':1}),
('E4-4',  'E4', {'sma_period':2}),
('E4-5',  'E4', {'sma_period':2}),
('E4-6',  'E4', {'sma_period':2}),
('E4-7',  'E4', {'sma_period':4}),
('E4-8',  'E4', {'sma_period':4}),
('E4-9',  'E4', {'sma_period':4}),

# ── E5 — Multi-EMA + RSI (12 bots) ──
('E5-1',  'E5', {'macro_ema':144,'pullback_ema':12,'rsi_threshold':35}),
('E5-2',  'E5', {'macro_ema':144,'pullback_ema':24,'rsi_threshold':40}),
('E5-3',  'E5', {'macro_ema':144,'pullback_ema':36,'rsi_threshold':45}),
('E5-4',  'E5', {'macro_ema':168,'pullback_ema':12,'rsi_threshold':35}),
('E5-5',  'E5', {'macro_ema':168,'pullback_ema':24,'rsi_threshold':40}),
('E5-6',  'E5', {'macro_ema':168,'pullback_ema':36,'rsi_threshold':45}),
('E5-7',  'E5', {'macro_ema':200,'pullback_ema':12,'rsi_threshold':35}),
('E5-8',  'E5', {'macro_ema':200,'pullback_ema':24,'rsi_threshold':40}),
('E5-9',  'E5', {'macro_ema':200,'pullback_ema':36,'rsi_threshold':45}),
('E5-10', 'E5', {'macro_ema':168,'pullback_ema':24,'rsi_threshold':35}),
('E5-11', 'E5', {'macro_ema':168,'pullback_ema':24,'rsi_threshold':45}),
('E5-12', 'E5', {'macro_ema':200,'pullback_ema':36,'rsi_threshold':40}),

# ── E6 — Z-Score (9 bots) ──
('E6-1',  'E6', {'z_trigger':-2.0,'lookback':96}),
('E6-2',  'E6', {'z_trigger':-2.5,'lookback':96}),
('E6-3',  'E6', {'z_trigger':-3.0,'lookback':96}),
('E6-4',  'E6', {'z_trigger':-2.0,'lookback':168}),
('E6-5',  'E6', {'z_trigger':-2.5,'lookback':168}),
('E6-6',  'E6', {'z_trigger':-3.0,'lookback':168}),
('E6-7',  'E6', {'z_trigger':-2.0,'lookback':336}),
('E6-8',  'E6', {'z_trigger':-2.5,'lookback':336}),
('E6-9',  'E6', {'z_trigger':-3.0,'lookback':336}),

# ── E7 — Volatility Squeeze (9 bots) ──
('E7-1',  'E7', {'squeeze_hours':8, 'vol_mult':1.0}),
('E7-2',  'E7', {'squeeze_hours':12,'vol_mult':1.0}),
('E7-3',  'E7', {'squeeze_hours':24,'vol_mult':1.0}),
('E7-4',  'E7', {'squeeze_hours':8, 'vol_mult':1.5}),
('E7-5',  'E7', {'squeeze_hours':12,'vol_mult':1.5}),
('E7-6',  'E7', {'squeeze_hours':24,'vol_mult':1.5}),
('E7-7',  'E7', {'squeeze_hours':8, 'vol_mult':2.0}),
('E7-8',  'E7', {'squeeze_hours':12,'vol_mult':2.0}),
('E7-9',  'E7', {'squeeze_hours':24,'vol_mult':2.0}),

# ── E8 — Swing Structure (9 bots) ──
('E8-1',  'E8', {'swing_candles':2,'vwap_period':12}),
('E8-2',  'E8', {'swing_candles':2,'vwap_period':24}),
('E8-3',  'E8', {'swing_candles':2,'vwap_period':48}),
('E8-4',  'E8', {'swing_candles':3,'vwap_period':12}),
('E8-5',  'E8', {'swing_candles':3,'vwap_period':24}),
('E8-6',  'E8', {'swing_candles':3,'vwap_period':48}),
('E8-7',  'E8', {'swing_candles':5,'vwap_period':12}),
('E8-8',  'E8', {'swing_candles':5,'vwap_period':24}),
('E8-9',  'E8', {'swing_candles':5,'vwap_period':48}),

# ── E9 — Candle Decay (9 bots) ──
('E9-1',  'E9', {'red_candles':5,'vol_mult':1.0}),
('E9-2',  'E9', {'red_candles':6,'vol_mult':1.0}),
('E9-3',  'E9', {'red_candles':7,'vol_mult':1.0}),
('E9-4',  'E9', {'red_candles':5,'vol_mult':1.5}),
('E9-5',  'E9', {'red_candles':6,'vol_mult':1.5}),
('E9-6',  'E9', {'red_candles':7,'vol_mult':1.5}),
('E9-7',  'E9', {'red_candles':5,'vol_mult':2.0}),
('E9-8',  'E9', {'red_candles':6,'vol_mult':2.0}),
('E9-9',  'E9', {'red_candles':7,'vol_mult':2.0}),

# ── E10 — Pure Drop (12 bots) ──
('E10-1',  'E10', {'drop_pct':3.0, 'lookback':12}),
('E10-2',  'E10', {'drop_pct':5.0, 'lookback':12}),
('E10-3',  'E10', {'drop_pct':7.0, 'lookback':12}),
('E10-4',  'E10', {'drop_pct':10.0,'lookback':12}),
('E10-5',  'E10', {'drop_pct':15.0,'lookback':12}),
('E10-6',  'E10', {'drop_pct':3.0, 'lookback':24}),
('E10-7',  'E10', {'drop_pct':5.0, 'lookback':24}),
('E10-8',  'E10', {'drop_pct':7.0, 'lookback':24}),
('E10-9',  'E10', {'drop_pct':10.0,'lookback':24}),
('E10-10', 'E10', {'drop_pct':15.0,'lookback':24}),
('E10-11', 'E10', {'drop_pct':5.0, 'lookback':48}),
('E10-12', 'E10', {'drop_pct':10.0,'lookback':48}),

# ── E11 — QFL Base (9 bots) ──
('E11-1',  'E11', {'base_break_pct':2.0}),
('E11-2',  'E11', {'base_break_pct':3.0}),
('E11-3',  'E11', {'base_break_pct':4.0}),
('E11-4',  'E11', {'base_break_pct':5.0}),
('E11-5',  'E11', {'base_break_pct':6.0}),
('E11-6',  'E11', {'base_break_pct':8.0}),
('E11-7',  'E11', {'base_break_pct':10.0}),
('E11-8',  'E11', {'base_break_pct':12.0}),
('E11-9',  'E11', {'base_break_pct':15.0}),

# ── E12 — S/R Reclaim (9 bots) ──
('E12-1',  'E12', {'reclaim_pct':0.5,'touch_count':2,'vol_mult':1.2}),
('E12-2',  'E12', {'reclaim_pct':1.0,'touch_count':2,'vol_mult':1.4}),
('E12-3',  'E12', {'reclaim_pct':1.5,'touch_count':3,'vol_mult':1.6}),
('E12-4',  'E12', {'reclaim_pct':2.0,'touch_count':3,'vol_mult':1.8}),
('E12-5',  'E12', {'reclaim_pct':2.5,'touch_count':4,'vol_mult':2.0}),
('E12-6',  'E12', {'reclaim_pct':3.0,'touch_count':4,'vol_mult':2.2}),
('E12-7',  'E12', {'reclaim_pct':3.5,'touch_count':5,'vol_mult':2.4}),
('E12-8',  'E12', {'reclaim_pct':4.0,'touch_count':5,'vol_mult':2.6}),
('E12-9',  'E12', {'reclaim_pct':5.0,'touch_count':6,'vol_mult':3.0}),

# ── E13 — EMA+MACD+RSI (10 bots) ──
('E13-1',  'E13', {'fast_ema':9, 'slow_ema':21,'rsi_threshold':35}),
('E13-2',  'E13', {'fast_ema':10,'slow_ema':24,'rsi_threshold':37}),
('E13-3',  'E13', {'fast_ema':12,'slow_ema':26,'rsi_threshold':39}),
('E13-4',  'E13', {'fast_ema':14,'slow_ema':30,'rsi_threshold':41}),
('E13-5',  'E13', {'fast_ema':16,'slow_ema':34,'rsi_threshold':43}),
('E13-6',  'E13', {'fast_ema':18,'slow_ema':40,'rsi_threshold':45}),
('E13-7',  'E13', {'fast_ema':20,'slow_ema':50,'rsi_threshold':47}),
('E13-8',  'E13', {'fast_ema':22,'slow_ema':55,'rsi_threshold':49}),
('E13-9',  'E13', {'fast_ema':24,'slow_ema':60,'rsi_threshold':51}),
('E13-10', 'E13', {'fast_ema':26,'slow_ema':70,'rsi_threshold':53}),

# ── E14 — Stoch RSI (9 bots) ──
('E14-1',  'E14', {'stoch_threshold':10,'trend_ema':50, 'recovery_closes':1}),
('E14-2',  'E14', {'stoch_threshold':12,'trend_ema':55, 'recovery_closes':1}),
('E14-3',  'E14', {'stoch_threshold':14,'trend_ema':60, 'recovery_closes':1}),
('E14-4',  'E14', {'stoch_threshold':16,'trend_ema':65, 'recovery_closes':2}),
('E14-5',  'E14', {'stoch_threshold':18,'trend_ema':70, 'recovery_closes':2}),
('E14-6',  'E14', {'stoch_threshold':20,'trend_ema':75, 'recovery_closes':2}),
('E14-7',  'E14', {'stoch_threshold':22,'trend_ema':80, 'recovery_closes':2}),
('E14-8',  'E14', {'stoch_threshold':24,'trend_ema':90, 'recovery_closes':3}),
('E14-9',  'E14', {'stoch_threshold':26,'trend_ema':100,'recovery_closes':3}),

# ── E15 — OBV Divergence (9 bots) ──
('E15-1',  'E15', {'lookback':24,'rsi_threshold':40,'price_drop_pct':3.0}),
('E15-2',  'E15', {'lookback':24,'rsi_threshold':45,'price_drop_pct':5.0}),
('E15-3',  'E15', {'lookback':24,'rsi_threshold':50,'price_drop_pct':7.0}),
('E15-4',  'E15', {'lookback':48,'rsi_threshold':40,'price_drop_pct':3.0}),
('E15-5',  'E15', {'lookback':48,'rsi_threshold':45,'price_drop_pct':5.0}),
('E15-6',  'E15', {'lookback':48,'rsi_threshold':50,'price_drop_pct':7.0}),
('E15-7',  'E15', {'lookback':72,'rsi_threshold':40,'price_drop_pct':5.0}),
('E15-8',  'E15', {'lookback':72,'rsi_threshold':45,'price_drop_pct':7.0}),
('E15-9',  'E15', {'lookback':72,'rsi_threshold':50,'price_drop_pct':10.0}),

# ── E16 — RSI Divergence (9 bots) ──
('E16-1',  'E16', {'lookback':24,'rsi_threshold':35}),
('E16-2',  'E16', {'lookback':24,'rsi_threshold':40}),
('E16-3',  'E16', {'lookback':24,'rsi_threshold':45}),
('E16-4',  'E16', {'lookback':48,'rsi_threshold':35}),
('E16-5',  'E16', {'lookback':48,'rsi_threshold':40}),
('E16-6',  'E16', {'lookback':48,'rsi_threshold':45}),
('E16-7',  'E16', {'lookback':72,'rsi_threshold':35}),
('E16-8',  'E16', {'lookback':72,'rsi_threshold':40}),
('E16-9',  'E16', {'lookback':72,'rsi_threshold':45}),

# ── E17 — Liquidity Sweep (9 bots) ──
('E17-1',  'E17', {'lookback':12,'sweep_pct':0.25,'close_upper':40}),
('E17-2',  'E17', {'lookback':12,'sweep_pct':0.50,'close_upper':50}),
('E17-3',  'E17', {'lookback':12,'sweep_pct':1.00,'close_upper':60}),
('E17-4',  'E17', {'lookback':24,'sweep_pct':0.25,'close_upper':40}),
('E17-5',  'E17', {'lookback':24,'sweep_pct':0.50,'close_upper':50}),
('E17-6',  'E17', {'lookback':24,'sweep_pct':1.00,'close_upper':60}),
('E17-7',  'E17', {'lookback':48,'sweep_pct':0.25,'close_upper':40}),
('E17-8',  'E17', {'lookback':48,'sweep_pct':0.50,'close_upper':50}),
('E17-9',  'E17', {'lookback':48,'sweep_pct':1.00,'close_upper':60}),

# ── E18 — ADX Trend Pullback (9 bots) ──
('E18-1',  'E18', {'adx_min':20,'rsi_threshold':35,'vol_lookback':100}),
('E18-2',  'E18', {'adx_min':20,'rsi_threshold':40,'vol_lookback':100}),
('E18-3',  'E18', {'adx_min':20,'rsi_threshold':45,'vol_lookback':100}),
('E18-4',  'E18', {'adx_min':25,'rsi_threshold':35,'vol_lookback':150}),
('E18-5',  'E18', {'adx_min':25,'rsi_threshold':40,'vol_lookback':150}),
('E18-6',  'E18', {'adx_min':25,'rsi_threshold':45,'vol_lookback':150}),
('E18-7',  'E18', {'adx_min':30,'rsi_threshold':35,'vol_lookback':200}),
('E18-8',  'E18', {'adx_min':30,'rsi_threshold':40,'vol_lookback':200}),
('E18-9',  'E18', {'adx_min':30,'rsi_threshold':45,'vol_lookback':200}),

# ── E18b — Low ADX Ranging (9 bots) ──
('E18b-1', 'E18b', {'adx_max':20,'rsi_threshold':30,'lookback':14}),
('E18b-2', 'E18b', {'adx_max':20,'rsi_threshold':35,'lookback':14}),
('E18b-3', 'E18b', {'adx_max':20,'rsi_threshold':40,'lookback':14}),
('E18b-4', 'E18b', {'adx_max':25,'rsi_threshold':30,'lookback':14}),
('E18b-5', 'E18b', {'adx_max':25,'rsi_threshold':35,'lookback':14}),
('E18b-6', 'E18b', {'adx_max':25,'rsi_threshold':40,'lookback':14}),
('E18b-7', 'E18b', {'adx_max':20,'rsi_threshold':30,'lookback':24}),
('E18b-8', 'E18b', {'adx_max':25,'rsi_threshold':35,'lookback':24}),
('E18b-9', 'E18b', {'adx_max':25,'rsi_threshold':40,'lookback':24}),

# ── E19 — Fibonacci (9 bots) ──
('E19-1',  'E19', {'fib_level':'38.2','lookback':48}),
('E19-2',  'E19', {'fib_level':'50.0','lookback':48}),
('E19-3',  'E19', {'fib_level':'61.8','lookback':48}),
('E19-4',  'E19', {'fib_level':'78.6','lookback':48}),
('E19-5',  'E19', {'fib_level':'38.2','lookback':96}),
('E19-6',  'E19', {'fib_level':'50.0','lookback':96}),
('E19-7',  'E19', {'fib_level':'61.8','lookback':96}),
('E19-8',  'E19', {'fib_level':'78.6','lookback':96}),
('E19-9',  'E19', {'fib_level':'61.8','lookback':168}),

# ── E20 — VPOC (9 bots) ──
('E20-1',  'E20', {'profile_days':30,'buffer_pct':0.0, 'rsi_threshold':0}),
('E20-2',  'E20', {'profile_days':60,'buffer_pct':0.0, 'rsi_threshold':0}),
('E20-3',  'E20', {'profile_days':90,'buffer_pct':0.0, 'rsi_threshold':0}),
('E20-4',  'E20', {'profile_days':30,'buffer_pct':0.5, 'rsi_threshold':35}),
('E20-5',  'E20', {'profile_days':60,'buffer_pct':0.5, 'rsi_threshold':35}),
('E20-6',  'E20', {'profile_days':90,'buffer_pct':0.5, 'rsi_threshold':35}),
('E20-7',  'E20', {'profile_days':60,'buffer_pct':1.0, 'rsi_threshold':0}),
('E20-8',  'E20', {'profile_days':90,'buffer_pct':1.0, 'rsi_threshold':30}),
('E20-9',  'E20', {'profile_days':90,'buffer_pct':0.5, 'rsi_threshold':40}),

# ── E21 — Fair Value Gap (9 bots) ──
('E21-1',  'E21', {'fill_depth':25, 'vol_mult':0}),
('E21-2',  'E21', {'fill_depth':50, 'vol_mult':0}),
('E21-3',  'E21', {'fill_depth':100,'vol_mult':1.2}),
('E21-4',  'E21', {'fill_depth':25, 'vol_mult':0}),
('E21-5',  'E21', {'fill_depth':50, 'vol_mult':0}),
('E21-6',  'E21', {'fill_depth':100,'vol_mult':1.5}),
('E21-7',  'E21', {'fill_depth':50, 'vol_mult':2.0}),
('E21-8',  'E21', {'fill_depth':50, 'vol_mult':0}),
('E21-9',  'E21', {'fill_depth':100,'vol_mult':1.2}),

# ── E22 — Hammer/Engulfing (9 bots) ──
('E22-1',  'E22', {'pattern':'hammer',    'wick_ratio':2.0,'support_proximity':0.5}),
('E22-2',  'E22', {'pattern':'hammer',    'wick_ratio':2.5,'support_proximity':0.5}),
('E22-3',  'E22', {'pattern':'hammer',    'wick_ratio':3.0,'support_proximity':0.5}),
('E22-4',  'E22', {'pattern':'hammer',    'wick_ratio':2.0,'support_proximity':1.0}),
('E22-5',  'E22', {'pattern':'hammer',    'wick_ratio':2.5,'support_proximity':1.0}),
('E22-6',  'E22', {'pattern':'hammer',    'wick_ratio':3.0,'support_proximity':1.0}),
('E22-7',  'E22', {'pattern':'engulfing', 'wick_ratio':0,  'support_proximity':0.5}),
('E22-8',  'E22', {'pattern':'engulfing', 'wick_ratio':0,  'support_proximity':1.0}),
('E22-9',  'E22', {'pattern':'engulfing', 'wick_ratio':0,  'support_proximity':2.0}),

# ── E23 — Relative Strength vs BTC (9 bots) ──
('E23-1',  'E23', {'lookback':24,'min_outperform':2.0,'rsi_threshold':40}),
('E23-2',  'E23', {'lookback':24,'min_outperform':4.0,'rsi_threshold':40}),
('E23-3',  'E23', {'lookback':24,'min_outperform':6.0,'rsi_threshold':40}),
('E23-4',  'E23', {'lookback':48,'min_outperform':2.0,'rsi_threshold':45}),
('E23-5',  'E23', {'lookback':48,'min_outperform':4.0,'rsi_threshold':45}),
('E23-6',  'E23', {'lookback':48,'min_outperform':6.0,'rsi_threshold':45}),
('E23-7',  'E23', {'lookback':72,'min_outperform':2.0,'rsi_threshold':50}),
('E23-8',  'E23', {'lookback':72,'min_outperform':4.0,'rsi_threshold':50}),
('E23-9',  'E23', {'lookback':72,'min_outperform':6.0,'rsi_threshold':50}),

# ── E24 — Funding Rate (9 bots) ──
('E24-1',  'E24', {'funding_threshold':-0.05,'rsi_threshold':35}),
('E24-2',  'E24', {'funding_threshold':-0.10,'rsi_threshold':35}),
('E24-3',  'E24', {'funding_threshold':-0.15,'rsi_threshold':35}),
('E24-4',  'E24', {'funding_threshold':-0.05,'rsi_threshold':40}),
('E24-5',  'E24', {'funding_threshold':-0.10,'rsi_threshold':40}),
('E24-6',  'E24', {'funding_threshold':-0.15,'rsi_threshold':40}),
('E24-7',  'E24', {'funding_threshold':-0.05,'rsi_threshold':35}),
('E24-8',  'E24', {'funding_threshold':-0.10,'rsi_threshold':35}),
('E24-9',  'E24', {'funding_threshold':-0.15,'rsi_threshold':40}),

# ── E25 — Supertrend + RSI (9 bots) ──
('E25-1',  'E25', {'atr_period':10,'atr_mult':2.0,'rsi_threshold':30}),
('E25-2',  'E25', {'atr_period':10,'atr_mult':2.5,'rsi_threshold':35}),
('E25-3',  'E25', {'atr_period':10,'atr_mult':3.0,'rsi_threshold':40}),
('E25-4',  'E25', {'atr_period':14,'atr_mult':2.0,'rsi_threshold':30}),
('E25-5',  'E25', {'atr_period':14,'atr_mult':2.5,'rsi_threshold':35}),
('E25-6',  'E25', {'atr_period':14,'atr_mult':3.0,'rsi_threshold':40}),
('E25-7',  'E25', {'atr_period':20,'atr_mult':2.0,'rsi_threshold':30}),
('E25-8',  'E25', {'atr_period':20,'atr_mult':2.5,'rsi_threshold':35}),
('E25-9',  'E25', {'atr_period':20,'atr_mult':3.0,'rsi_threshold':40}),

# ── BENCHMARKS (5 bots) ──
('BM-BTC-Hold',     'BM_HOLD',    {'coin':'BTC'}),
('BM-ETH-Hold',     'BM_HOLD',    {'coin':'ETH'}),
('BM-SimpleDCA',    'BM_SIMPLE',  {'drop_pct':7.0}),
('BM-RandomEntry',  'BM_RANDOM',  {}),
('BM-StaticSpacing','BM_STATIC',  {'spacing':1.0}),

# ── E26 — Ichimoku Cloud (9 bots) ──
('E26-1',  'E26', {'conversion':9, 'base':26,'rsi_threshold':35}),
('E26-2',  'E26', {'conversion':9, 'base':26,'rsi_threshold':40}),
('E26-3',  'E26', {'conversion':9, 'base':26,'rsi_threshold':45}),
('E26-4',  'E26', {'conversion':12,'base':30,'rsi_threshold':35}),
('E26-5',  'E26', {'conversion':12,'base':30,'rsi_threshold':40}),
('E26-6',  'E26', {'conversion':12,'base':30,'rsi_threshold':45}),
('E26-7',  'E26', {'conversion':9, 'base':26,'rsi_threshold':35}),
('E26-8',  'E26', {'conversion':12,'base':26,'rsi_threshold':35}),
('E26-9',  'E26', {'conversion':9, 'base':30,'rsi_threshold':40}),

]


def create_bots():
    db.init_pool()
    created = 0
    skipped = 0

    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM bots WHERE user_id = 1")
        existing = {r[0] for r in cur.fetchall()}

        for (name, method, params) in BOTS:
            if name in existing:
                skipped += 1
                continue
            cur.execute(
                "INSERT INTO bots ("
                "user_id, exchange_id, wallet_id, name, method, direction,"
                "trading_on, dca_on, base_order, dca_percent,"
                "spacing_multiplier, size_multiplier, take_profit_percent,"
                "trailing_percent, reserve_floor, is_paper, status,"
                "trades_per_bot, trades_per_coin, order_entry_type,"
                "order_dca_type, bot_params"
                ") VALUES ("
                "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
                ") ON CONFLICT DO NOTHING RETURNING id",
                (
                    DCA['user_id'], DCA['exchange_id'], DCA['wallet_id'],
                    name, method, DCA['direction'], DCA['trading_on'],
                    DCA['dca_on'], DCA['base_order'], DCA['dca_percent'],
                    DCA['spacing_multiplier'], DCA['size_multiplier'],
                    DCA['take_profit_percent'], DCA['trailing_percent'],
                    DCA['reserve_floor'], DCA['is_paper'], DCA['status'],
                    DCA['trades_per_bot'], DCA['trades_per_coin'],
                    DCA['order_entry_type'], DCA['order_dca_type'],
                    json.dumps(params)
                )
            )
            row = cur.fetchone()
            if row:
                created += 1
        conn.commit()

    return created, skipped


if __name__ == '__main__':
    print('🚀 Creating 261 research bots...')
    created, skipped = create_bots()
    print(f'✅ Created: {created} · Skipped (existing): {skipped}')

    # Verify
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT method, COUNT(*) as bots
            FROM bots WHERE user_id=1
            AND method != 'E1' OR name LIKE 'E%'
            GROUP BY method ORDER BY method
        """)
        print('\nBots per method:')
        total = 0
        for r in cur.fetchall():
            print(f'  {r[0]:<8} {r[1]} bots')
            total += r[1]
        print(f'\nTotal research bots: {total}')
