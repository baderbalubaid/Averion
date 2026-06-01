import psycopg2
import os
import subprocess
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

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def analyze_coingecko(rows):
    if len(rows) < 3:
        return None
    durations = [r['duration'] for r in rows
                 if r['step'] == 'coingecko' and r['duration']]
    if len(durations) < 3:
        return None
    if durations[-1] > durations[0] * 1.2:
        pct = round((durations[-1] - durations[0]) / durations[0] * 100)
        return {
            'level': '🟡 WARNING',
            'title': 'CoinGecko response time degrading',
            'data': f'{durations[0]:.1f}s → {durations[-1]:.1f}s (+{pct}%)',
            'cause': 'Rate limiting starting or API slowdown',
            'fix': 'Increase sleep between pages from 1.5s to 3s\n'
                   '   Or register new free API key at coingecko.com'
        }
    return None

def analyze_bot_crashes(rows):
    from collections import Counter
    bot_crashes = Counter()
    bot_errors = {}
    for r in rows:
        if r['event_type'] == 'crash':
            bot_crashes[r['bot_id']] += 1
            bot_errors[r['bot_id']] = r['error_message']
    issues = []
    for bot_id, count in bot_crashes.items():
        if count >= 2:
            issues.append({
                'level': '🟡 WARNING',
                'title': f'Bot #{bot_id} crashed {count} times',
                'data': f'Error: {bot_errors.get(bot_id, "unknown")}',
                'cause': 'Coding issue (not server — other bots fine)',
                'fix': f'Check Bot #{bot_id} · update CCXT · verify coin pair still active'
            })
    return issues

def analyze_server_trend(rows):
    if len(rows) < 3:
        return None
    first_cpu = rows[0]['cpu_percent']
    last_cpu = rows[-1]['cpu_percent']
    if last_cpu > 70:
        return {
            'level': '🔴 CRITICAL',
            'title': f'CPU critically high: {last_cpu}%',
            'data': f'Trend: {first_cpu}% → {last_cpu}% over {len(rows)} days',
            'cause': 'Too many bots for current server size',
            'fix': 'Upgrade to Hetzner CX33 €7.49/mo (4 vCPU · 8GB RAM)\n'
                   '   Or reduce number of active bots temporarily'
        }
    elif last_cpu > first_cpu * 1.15:
        return {
            'level': '🟢 INFO',
            'title': f'CPU increasing: {first_cpu}% → {last_cpu}%',
            'data': f'Over {len(rows)} days',
            'cause': 'More bots added recently · normal growth',
            'fix': f'Monitor · upgrade if reaches 70%\n'
                   f'   Next tier: CX33 €7.49/mo'
        }
    return None

def analyze_cycle_time(rows):
    if len(rows) < 3:
        return None
    first = rows[0]['bot_cycle_time']
    last = rows[-1]['bot_cycle_time']
    if first and last and last > first * 2:
        return {
            'level': '🟡 WARNING',
            'title': f'Bot cycle time doubled: {first}s → {last}s',
            'data': f'Over {len(rows)} days',
            'cause': 'Too many bots or slow exchange responses',
            'fix': 'Check exchange API latency · consider server upgrade'
        }
    return None

def generate_analysis(health_rows, timing_rows, bot_rows):
    issues = {'🔴 CRITICAL': [], '🟡 WARNING': [], '🟢 INFO': []}

    # CoinGecko trend
    cg = analyze_coingecko(timing_rows)
    if cg:
        issues[cg['level']].append(cg)

    # Bot crashes
    crashes = analyze_bot_crashes(bot_rows)
    for c in crashes:
        issues[c['level']].append(c)

    # Server trend
    server = analyze_server_trend(health_rows)
    if server:
        issues[server['level']].append(server)

    # Cycle time
    cycle = analyze_cycle_time(health_rows)
    if cycle:
        issues[cycle['level']].append(cycle)

    return issues

def format_analysis(issues):
    lines = ['## ⚠️ AUTO-ANALYSIS — Read This First\n']
    lines.append('> Generated automatically · Claude confirms and gives exact fix\n')

    for level in ['🔴 CRITICAL', '🟡 WARNING', '🟢 INFO']:
        lines.append(f'\n### {level}')
        if not issues[level]:
            lines.append('None ✅')
        else:
            for i, issue in enumerate(issues[level], 1):
                lines.append(f'\n{i}. **{issue["title"]}**')
                lines.append(f'   - Data: {issue["data"]}')
                lines.append(f'   - Likely cause: {issue["cause"]}')
                lines.append(f'   - Recommendation: {issue["fix"]}')
    return '\n'.join(lines)

def format_health_table(rows):
    lines = [
        '\n## System Health (Last 30 days · daily)',
        '| Date | CPU | RAM | Disk | Cycle | Bots | Positions |',
        '|------|-----|-----|------|-------|------|-----------|'
    ]
    for r in rows[-30:]:
        date = str(r['recorded_at'])[:10]
        lines.append(
            f"| {date} | {r['cpu_percent']}% | {r['ram_percent']}% | "
            f"{r['disk_percent']}% | {r['bot_cycle_time']}s | "
            f"{r['active_bots']} | {r['open_positions']} |"
        )
    return '\n'.join(lines)

def format_timing_table(rows):
    lines = [
        '\n## Cron Performance (Last 30 days)',
        '| Date | Step | Duration | Records | Status | Error |',
        '|------|------|----------|---------|--------|-------|'
    ]
    for r in rows[-100:]:
        date = str(r['completed_at'])[:10]
        status = '✅' if r['status'] == 'success' else '❌'
        error = (r['error_message'] or '')[:50]
        lines.append(
            f"| {date} | {r['step']} | {r['duration_seconds']}s | "
            f"{r['records_processed']} | {status} | {error} |"
        )
    return '\n'.join(lines)

def format_bot_events(rows):
    lines = [
        '\n## Bot Events (Last 30 days)',
        '| Date | Bot | Event | Coin | Error | Resolved |',
        '|------|-----|-------|------|-------|----------|'
    ]
    for r in rows[-100:]:
        date = str(r['recorded_at'])[:10]
        resolved = '✅' if r['resolved'] else '❌'
        error = (r['error_message'] or '')[:60]
        lines.append(
            f"| {date} | #{r['bot_id']} | {r['event_type']} | "
            f"{r['coin'] or '-'} | {error} | {resolved} |"
        )
    return '\n'.join(lines)

def format_trade_events(rows):
    lines = [
        '\n## Trade Events (Last 30 days)',
        '| Date | Position | Bot | Coin | Issue | Detail | Resolved |',
        '|------|----------|-----|------|-------|--------|----------|'
    ]
    for r in rows[-100:]:
        date = str(r['recorded_at'])[:10]
        resolved = '✅' if r['resolved'] else '❌'
        detail = (r['details'] or '')[:50]
        lines.append(
            f"| {date} | #{r['position_id']} | #{r['bot_id']} | "
            f"{r['coin'] or '-'} | {r['issue_type']} | {detail} | {resolved} |"
        )
    return '\n'.join(lines)

def generate_report():
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Fetch system health
        cur.execute("""
            SELECT * FROM system_health
            WHERE recorded_at > %s
            ORDER BY recorded_at ASC
        """, (cutoff,))
        cols = [d[0] for d in cur.description]
        health_rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        # Fetch timing
        cur.execute("""
            SELECT * FROM performance_timing
            WHERE completed_at > %s
            ORDER BY completed_at ASC
        """, (cutoff,))
        cols = [d[0] for d in cur.description]
        timing_rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        # Fetch bot events
        cur.execute("""
            SELECT * FROM bot_events
            WHERE recorded_at > %s
            ORDER BY recorded_at ASC
        """, (cutoff,))
        cols = [d[0] for d in cur.description]
        bot_rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        # Fetch trade events
        cur.execute("""
            SELECT * FROM trade_events
            WHERE recorded_at > %s
            ORDER BY recorded_at ASC
        """, (cutoff,))
        cols = [d[0] for d in cur.description]
        trade_rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        conn.close()

    except Exception as e:
        print(f'DB error: {e}')
        health_rows = timing_rows = bot_rows = trade_rows = []

    # Generate analysis
    issues = generate_analysis(health_rows, timing_rows, bot_rows)

    # Build markdown
    lines = [
        '# Averion Diagnostics Report',
        f'**Generated:** {now.strftime("%Y-%m-%d %H:%M UTC")}',
        f'**Server:** Hetzner CX23 · Helsinki',
        f'**Period:** Last 30 days',
        '',
        '> Share this URL with Claude for instant diagnosis:',
        '> https://raw.githubusercontent.com/baderbalubaid/Averion/main/diagnostics/latest.md',
        '',
        '---',
        '',
        format_analysis(issues),
        '',
        '---',
        '',
        format_health_table(health_rows) if health_rows else '## System Health\nNo data yet',
        '',
        format_timing_table(timing_rows) if timing_rows else '## Cron Performance\nNo data yet',
        '',
        format_bot_events(bot_rows) if bot_rows else '## Bot Events\nNo events recorded',
        '',
        format_trade_events(trade_rows) if trade_rows else '## Trade Events\nNo events recorded',
        '',
        '---',
        '',
        '## Server Upgrade Guide',
        '| Tier | Cost | vCPU | RAM | Upgrade When |',
        '|------|------|------|-----|--------------|',
        '| CX23 | €3.99/mo | 2 | 4GB | Current |',
        '| CX33 | €7.49/mo | 4 | 8GB | CPU >70% sustained |',
        '| CX43 | €16.49/mo | 8 | 16GB | CPU >70% on CX33 |',
        '| CX53 | €32.99/mo | 16 | 32GB | Large user base |',
    ]

    report = '\n'.join(lines)

    # Save locally
    os.makedirs('diagnostics', exist_ok=True)
    with open('diagnostics/latest.md', 'w') as f:
        f.write(report)
    print('✅ Diagnostics report generated')

    # Push to GitHub
    try:
        subprocess.run(['git', 'add', 'diagnostics/latest.md'], check=True)
        subprocess.run(['git', 'commit', '-m', f'diagnostics: update {now.date()}'],
                      check=True)
        subprocess.run([
            'git', 'push',
            f'https://baderbalubaid:{GITHUB_TOKEN}@github.com/baderbalubaid/Averion.git',
            'main'
        ], check=True)
        print('✅ Diagnostics pushed to GitHub')
    except Exception as e:
        print(f'⚠️ Push failed: {e}')

if __name__ == '__main__':
    generate_report()
