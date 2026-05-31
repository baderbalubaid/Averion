import psycopg2
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

# Colors
DARK = 'FF0E0E1C'
GREEN = 'FF10D98A'
RED = 'FFF4645F'
AMBER = 'FFFFA500'
WHITE = 'FFFFFFFF'
GRAY = 'FF888888'

def style_header(cell, bg=DARK, fg=WHITE, bold=True):
    cell.font = Font(color=fg, bold=bold, name='Calibri')
    cell.fill = PatternFill(fill_type='solid', fgColor=bg)
    cell.alignment = Alignment(horizontal='center', vertical='center')

def generate_report():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    wb = openpyxl.Workbook()

    # ═══════════════════════════
    # SHEET 1 — Daily Summary
    # ═══════════════════════════
    ws1 = wb.active
    ws1.title = 'Daily Summary'
    ws1.column_dimensions['A'].width = 25
    ws1.column_dimensions['B'].width = 20

    ws1['A1'] = f'Averion Daily Report — {today}'
    ws1['A1'].font = Font(bold=True, size=14, name='Calibri')
    ws1.merge_cells('A1:B1')

    headers = ['Metric', 'Value']
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=2, column=col, value=h)
        style_header(cell)

    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open'")
    open_pos = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM positions 
        WHERE status='closed' AND DATE(closed_at) = %s
    """, (today,))
    closed_today = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=TRUE
    """)
    paper_open = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=FALSE
    """)
    live_open = cur.fetchone()[0]

    rows = [
        ('Open Positions', open_pos),
        ('Live Open', live_open),
        ('Paper Open', paper_open),
        ('Closed Today', closed_today),
        ('Report Date', str(today)),
        ('Generated At', str(datetime.utcnow().strftime('%H:%M UTC'))),
    ]

    for i, (label, value) in enumerate(rows, 3):
        ws1.cell(row=i, column=1, value=label)
        ws1.cell(row=i, column=2, value=value)

    # ═══════════════════════════
    # SHEET 2 — Open Positions
    # ═══════════════════════════
    ws2 = wb.create_sheet('Open Positions')
    headers2 = ['Coin', 'Direction', 'Avg Cost', 'DCA Count',
                 'Total Invested', 'Current Loss%', 'Opened At', 'Exchange']
    
    for col, h in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col, value=h)
        style_header(cell)
        ws2.column_dimensions[get_column_letter(col)].width = 18

    cur.execute("""
        SELECT p.coin, p.direction, p.avg_cost, p.dca_count,
               p.total_invested, p.opened_at, e.exchange
        FROM positions p
        JOIN exchanges e ON e.id = p.exchange_id
        WHERE p.status = 'open'
        ORDER BY p.total_invested DESC
    """)

    for row_idx, row in enumerate(cur.fetchall(), 2):
        coin, direction, avg_cost, dca_count, invested, opened_at, exchange = row
        ws2.cell(row=row_idx, column=1, value=coin)
        ws2.cell(row=row_idx, column=2, value=direction)
        ws2.cell(row=row_idx, column=3, value=float(avg_cost) if avg_cost else 0)
        ws2.cell(row=row_idx, column=4, value=dca_count)
        ws2.cell(row=row_idx, column=5, value=float(invested) if invested else 0)
        ws2.cell(row=row_idx, column=6, value='N/A')
        ws2.cell(row=row_idx, column=7, value=str(opened_at))
        ws2.cell(row=row_idx, column=8, value=exchange)

    # ═══════════════════════════
    # SHEET 3 — Closed Today
    # ═══════════════════════════
    ws3 = wb.create_sheet('Closed Today')
    headers3 = ['Coin', 'Direction', 'Entry Price', 'Exit Price',
                 'DCA Count', 'Invested', 'Profit', 'Hold Time', 'Exchange']

    for col, h in enumerate(headers3, 1):
        cell = ws3.cell(row=1, column=col, value=h)
        style_header(cell)
        ws3.column_dimensions[get_column_letter(col)].width = 18

    cur.execute("""
        SELECT p.coin, p.direction, p.avg_cost, p.dca_count,
               p.total_invested, p.opened_at, p.closed_at, e.exchange
        FROM positions p
        JOIN exchanges e ON e.id = p.exchange_id
        WHERE p.status = 'closed'
        AND DATE(p.closed_at) = %s
        ORDER BY p.closed_at DESC
    """, (today,))

    for row_idx, row in enumerate(cur.fetchall(), 2):
        coin, direction, avg_cost, dca_count, invested, opened_at, closed_at, exchange = row
        hold_hours = round((closed_at - opened_at).total_seconds() / 3600, 1) if closed_at and opened_at else 0
        ws3.cell(row=row_idx, column=1, value=coin)
        ws3.cell(row=row_idx, column=2, value=direction)
        ws3.cell(row=row_idx, column=3, value=float(avg_cost) if avg_cost else 0)
        ws3.cell(row=row_idx, column=4, value='N/A')
        ws3.cell(row=row_idx, column=5, value=dca_count)
        ws3.cell(row=row_idx, column=6, value=float(invested) if invested else 0)
        ws3.cell(row=row_idx, column=7, value='N/A')
        ws3.cell(row=row_idx, column=8, value=f'{hold_hours}h')
        ws3.cell(row=row_idx, column=9, value=exchange)

    # ═══════════════════════════
    # SHEET 4 — Platform Stats
    # ═══════════════════════════
    ws4 = wb.create_sheet('Platform Stats')
    ws4['A1'] = 'Platform Statistics'
    ws4['A1'].font = Font(bold=True, size=14)

    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin=FALSE")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bots WHERE status='active'")
    total_bots = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(balance_usdt),0) FROM reserve_wallets")
    total_reserve = float(cur.fetchone()[0])

    platform_rows = [
        ('Total Users', total_users),
        ('Active Bots', total_bots),
        ('Total Reserve Balance', f'${total_reserve:.2f}'),
        ('Report Date', str(today)),
    ]

    for i, (label, value) in enumerate(platform_rows, 3):
        ws4.cell(row=i, column=1, value=label)
        ws4.cell(row=i, column=2, value=value)

    conn.close()

    # Save file
    os.makedirs('reports', exist_ok=True)
    filename = f'reports/averion_report_{today}.xlsx'
    wb.save(filename)
    print(f'✅ Excel report saved: {filename}')

if __name__ == '__main__':
    generate_report()
