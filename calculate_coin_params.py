"""
calculate_coin_params.py — Dynamic Coin Parameter Calculator
Runs daily · calculates optimal DCA/TP/trailing per coin per category
Uses 90 days hourly OHLCV data from DB

Category limits (from spec):
Mega:  spacing 2-8%   · TP 1-5%   · trail 0.5-2%
Large: spacing 5-12%  · TP 2-7%   · trail 1-3%
Mid:   spacing 7-18%  · TP 4-10%  · trail 1.5-4%
Small: spacing 10-25% · TP 5-15%  · trail 2-6%
Micro: spacing 15-40% · TP 8-20%  · trail 3-8%
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
import numpy as np
from datetime import datetime

db.init_pool()

# Category limits per spec
CATEGORY_LIMITS = {
    'mega':  {'spacing': (2, 8),   'tp': (1, 5),   'trail': (0.5, 2.0), 'size': (1.1, 1.8)},
    'large': {'spacing': (5, 12),  'tp': (2, 7),   'trail': (1.0, 3.0), 'size': (1.2, 2.2)},
    'mid':   {'spacing': (7, 18),  'tp': (4, 10),  'trail': (1.5, 4.0), 'size': (1.3, 2.8)},
    'small': {'spacing': (10, 25), 'tp': (5, 15),  'trail': (2.0, 6.0), 'size': (1.5, 3.5)},
    'micro': {'spacing': (15, 40), 'tp': (8, 20),  'trail': (3.0, 8.0), 'size': (2.0, 5.0)},
}

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def calculate_params_for_coin(coin, ohlcv_rows, category):
    """Calculate optimal DCA/TP/trail from OHLCV data."""
    if not ohlcv_rows or len(ohlcv_rows) < 24:
        return None

    limits = CATEGORY_LIMITS.get(category, CATEGORY_LIMITS['micro'])

    closes = np.array([float(r[4]) for r in ohlcv_rows])
    highs  = np.array([float(r[2]) for r in ohlcv_rows])
    lows   = np.array([float(r[3]) for r in ohlcv_rows])

    # ATR-14
    tr = np.maximum(highs[1:] - lows[1:],
         np.maximum(np.abs(highs[1:] - closes[:-1]),
                    np.abs(lows[1:] - closes[:-1])))
    atr_14 = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
    atr_pct = (atr_14 / closes[-1] * 100) if closes[-1] > 0 else 0

    # Median drop before bounce (spacing)
    drops = []
    for i in range(1, len(closes)):
        if closes[i] < closes[i-1] and closes[i-1] > 0:
            drop = (closes[i-1] - closes[i]) / closes[i-1] * 100
            if drop > 0.1:
                drops.append(drop)
    median_drop = np.median(drops) if drops else atr_pct * 1.5

    # Calculate spacing: ATR×1.5 vs median_drop×0.85 → lower
    spacing_atr    = atr_pct * 1.5
    spacing_median = median_drop * 0.85
    spacing_raw    = min(spacing_atr, spacing_median)
    spacing        = clamp(round(spacing_raw, 1), *limits['spacing'])

    # Median recovery after drop (TP)
    recoveries = []
    for i in range(2, len(closes)):
        if closes[i] > closes[i-1] and closes[i-1] < closes[i-2]:
            recovery = (closes[i] - closes[i-1]) / closes[i-1] * 100
            if recovery > 0.1:
                recoveries.append(recovery)
    median_recovery = np.median(recoveries) if recoveries else spacing * 0.7
    tp_raw  = median_recovery * 0.8
    tp      = clamp(round(tp_raw, 1), *limits['tp'])

    # Trailing: ATR-based
    trail_raw = atr_pct * 0.8
    trail     = clamp(round(trail_raw, 1), *limits['trail'])

    # Volatility
    returns    = np.diff(closes) / closes[:-1] * 100
    volatility = round(float(np.std(returns)), 2)

    return {
        'dca_spacing':     spacing,
        'take_profit_pct': tp,
        'trailing_pct':    trail,
        'size_mult':       round(clamp(1 + atr_pct/10, *limits['size']), 2),
        'atr_14':          round(float(atr_14), 8),
        'median_drop':     round(float(median_drop), 2),
        'median_recovery': round(float(median_recovery), 2),
        'volatility_pct':  volatility,
        'data_quality':    'calculated' if len(ohlcv_rows) >= 720 else 'partial',
    }

def run():
    print(f'⚙️  Calculating coin parameters — {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    # Get all classified coins
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (coin) coin, category
            FROM coin_history
            ORDER BY coin, id DESC
        """)
        coins = cur.fetchall()

    print(f'Processing {len(coins)} coins...')

    calculated = 0
    estimated  = 0
    errors     = 0

    for coin, category in coins:
        try:
            # Get OHLCV data
            rows = db.get_ohlcv(coin, 'mexc', limit=720)  # 30 days hourly

            if rows and len(rows) >= 24:
                params = calculate_params_for_coin(coin, rows, category)
            else:
                params = None

            if not params:
                # Use category defaults
                limits = CATEGORY_LIMITS.get(category, CATEGORY_LIMITS['micro'])
                params = {
                    'dca_spacing':     round((limits['spacing'][0] + limits['spacing'][1]) / 2, 1),
                    'take_profit_pct': round((limits['tp'][0] + limits['tp'][1]) / 2, 1),
                    'trailing_pct':    round((limits['trail'][0] + limits['trail'][1]) / 2, 1),
                    'size_mult':       round((limits['size'][0] + limits['size'][1]) / 2, 1),
                    'atr_14':          None,
                    'median_drop':     None,
                    'median_recovery': None,
                    'volatility_pct':  None,
                    'data_quality':    'estimated',
                }
                estimated += 1
            else:
                calculated += 1

            with db.get_db() as conn:
                cur = conn.cursor()
                # Convert numpy types to Python native
                for k in params:
                    if params[k] is not None and hasattr(params[k], '__float__'):
                        v = float(params[k])
                        import math
                        params[k] = None if (math.isnan(v) or math.isinf(v)) else v
                cur.execute("""
                    INSERT INTO coin_parameters
                        (coin, exchange, category, dca_spacing, take_profit_pct,
                         trailing_pct, size_mult, atr_14, median_drop,
                         median_recovery, volatility_pct, data_quality, calculated_at)
                    VALUES (%s, 'MEXC', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (coin, exchange) DO UPDATE SET
                        category        = EXCLUDED.category,
                        dca_spacing     = EXCLUDED.dca_spacing,
                        take_profit_pct = EXCLUDED.take_profit_pct,
                        trailing_pct    = EXCLUDED.trailing_pct,
                        size_mult       = EXCLUDED.size_mult,
                        atr_14          = EXCLUDED.atr_14,
                        median_drop     = EXCLUDED.median_drop,
                        median_recovery = EXCLUDED.median_recovery,
                        volatility_pct  = EXCLUDED.volatility_pct,
                        data_quality    = EXCLUDED.data_quality,
                        calculated_at   = NOW()
                """, (coin, category,
                      params['dca_spacing'], params['take_profit_pct'],
                      params['trailing_pct'], params['size_mult'],
                      params['atr_14'], params['median_drop'],
                      params['median_recovery'], params['volatility_pct'],
                      params['data_quality']))

        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f'  ⚠️ {coin}: {e}')

    print(f'\n✅ Done!')
    print(f'  Calculated: {calculated} coins (OHLCV data)')
    print(f'  Estimated:  {estimated} coins (category defaults)')
    print(f'  Errors:     {errors}')

    # Show sample
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT coin, category, dca_spacing, take_profit_pct, trailing_pct, data_quality
            FROM coin_parameters
            ORDER BY category, coin
            LIMIT 10
        """)
        print(f'\n📊 Sample parameters:')
        print(f'{"Coin":<10} {"Cat":<8} {"DCA%":<8} {"TP%":<8} {"Trail%":<8} {"Quality"}')
        print('-'*55)
        for r in cur.fetchall():
            print(f'{r[0]:<10} {r[1]:<8} {r[2]:<8} {r[3]:<8} {r[4]:<8} {r[5]}')

if __name__ == '__main__':
    run()
