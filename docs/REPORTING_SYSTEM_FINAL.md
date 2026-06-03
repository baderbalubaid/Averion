## Averion Reporting System — Final (LOCKED)

### Excel Reports: REMOVED
Replaced with structured markdown reports.
Better for AI sharing · no downloads needed.
All pushed to GitHub automatically.

---

## Report 1 — Daily Health Report (LOCKED)

Generated: Daily at 05:00
Location: GitHub /reports/health/YYYY-MM-DD.md
Also: latest.md always points to most recent

Purpose:
Share with any AI to get specific server recommendations.
AI immediately understands server specs · normal ranges · issues.

Format:
---
# Averion Server Health Report
Generated: {date} {time} UTC
Platform: Averion DCA Trading Bot
Server: Hetzner CX23 · 2 vCPU · 4GB RAM · 40GB SSD
Location: Helsinki · Ubuntu 24.04
Bot version: {version} · CCXT: {ccxt_version}
Active users: {users} · Open positions: {positions}

## ⚠️ ATTENTION NEEDED
{list of issues · empty if none = "✅ All systems normal"}

## Server Metrics (Today)
| Metric | Current | 7d Avg | Status |
|--------|---------|--------|--------|
| CPU | {cpu}% | {cpu_7d}% | {status} |
| RAM | {ram}GB/4GB | {ram_7d}GB | {status} |
| Disk | {disk}GB/40GB | - | {status} |
| Loop avg | {loop_avg}s | {loop_7d}s | {status} |
| Loop max | {loop_max}s | - | {status} |
| Positions | {positions} | {pos_7d} | {status} |
| DB size | {db_size}MB | - | {status} |

Status thresholds (Hetzner CX23):
CPU: Normal <30% · Warning >70% · Critical >85%
RAM: Normal <2GB · Warning >3GB · Critical >3.5GB
Loop: Normal <3s · Warning >15s · Critical >30s
Max positions before degradation: ~2,400

## Cron Results (Today)
| Step | Time | Duration | Status | Notes |
|------|------|---------|--------|-------|
| CoinGecko | 03:00 | {dur}s | {status} | {coins} coins |
| CMC | 03:30 | {dur}s | {status} | {coins} coins |
| OHLCV | 04:00 | {dur}s | {status} | {notes} |
| Classify | 04:30 | {dur}s | {status} | {reclassified} reclassified |
| Research | 05:00 | {dur}s | {status} | {notes} |

## 30-Day Rolling Performance
| Date | CPU Avg | RAM | Loop Avg | Positions | Errors |
|------|---------|-----|---------|-----------|--------|
{30 rows of daily data}

## Slowest Operations (Today)
| Operation | Avg | Max | Occurrences |
|-----------|-----|-----|------------|
| OHLCV fetch | {avg}s | {max}s | {count} |
| Bot loop | {avg}s | {max}s | {count} |
| DB query | {avg}s | {max}s | {count} |

## Alerts Today: {count}
{list of alerts with timestamps}

## Context for AI Review
Normal ranges for this server (Hetzner CX23):
- CPU normal 10-30% · Warning >70% · Critical >85%
- RAM normal 1-2GB · Warning >3GB · Critical >3.5GB
- Loop normal 1-3s · Warning >15s · Critical >30s
- Max positions before degradation: ~2,400
- Current capacity: {positions}/{max_capacity} ({pct}%)
- Upgrade available: CX33 (4 vCPU · 8GB · €17.99/mo)

## Notes
[Leave blank - AI fills recommendations here]
---

Admin Health Tab buttons:
[Copy Server Metrics] → copies metrics section only
[Copy Cron Results] → copies cron section only
[Copy 30-Day Log] → copies rolling log only
[Copy All] → copies complete report with all context

---

## Report 2 — Weekly Research Report (LOCKED)

Already locked in: docs/AI_RESEARCH_SYSTEM_BRIEF_FINAL.md
Generated: Every Sunday 05:00
Location: GitHub /reports/research/week-{N}.md

---

## Report 3 — Monthly Summary Report (LOCKED)

Generated: 1st of every month at 05:00
Location: GitHub /reports/monthly/YYYY-MM.md

Format:
---
# Averion Monthly Summary
Month: {month} {year}
Generated: {date} 05:00 UTC
Platform: Averion DCA Trading Bot
Server: Hetzner CX23 · 2 vCPU · 4GB RAM

## ⚠️ ATTENTION NEEDED
{issues · empty = "✅ All systems normal"}

## Platform Growth
| Metric | This Month | Last Month | Change |
|--------|-----------|-----------|--------|
| Users | {n} | {n} | {pct}% |
| Active bots | {n} | {n} | {pct}% |
| Trades closed | {n} | {n} | {pct}% |
| Win rate | {pct}% | {pct}% | {diff}% |
| Open positions | {n} | {n} | {pct}% |

## Financial
| Item | Amount |
|------|--------|
| Gross profit (all users) | ${amount} |
| Fees collected (20%) | ${amount} |
| Outstanding fees | ${amount} |
| Owner wallet balance | ${amount} |
| Referral payouts | ${amount} |

## Top 5 Performing Coins
| Coin | Trades | Win% | Avg Profit | Avg DCAs |
|------|--------|------|-----------|---------|
{5 rows}

## Top 5 Worst Coins
| Coin | Trades | Win% | Avg Loss | Avg DCAs |
|------|--------|------|---------|---------|
{5 rows}

## Server Health Summary
| Metric | Monthly Avg | Max | Days above threshold |
|--------|------------|-----|---------------------|
| CPU | {avg}% | {max}% | {days} days |
| RAM | {avg}GB | {max}GB | {days} days |
| Loop | {avg}s | {max}s | {days} days |
| Errors | {avg}/day | {max}/day | - |

## Research Summary
Champion changes this month: {count}
Bull champion: {method} {change_note}
Bear champion: {method} {change_note}
Sideways champion: {method} {change_note}
Best method overall: {method} RARS {score}

## Context for AI Review
Monthly summary of Averion automated DCA platform.
Server: Hetzner CX23 · Normal max: 2,400 positions
This month peak: {peak} positions ({pct}% capacity)
Upgrade trigger: >80% for 7+ consecutive days

## Notes
[Leave blank - AI fills recommendations here]
---

Admin Health Tab button:
[Copy Monthly Summary] → copies complete report

---

## Report Storage (LOCKED)

GitHub structure:
/reports/
 health/
   latest.md (always most recent)
   2026-06-03.md
   2026-06-02.md
   ...
 research/
   latest.md
   week-23.md
   week-22.md
   ...
 monthly/
   latest.md
   2026-06.md
   2026-05.md
   ...

Retention:
Health reports: keep last 90 days
Research reports: keep forever
Monthly reports: keep forever

---

## Admin Dashboard Buttons (LOCKED)

Health Tab:
[Copy Server Metrics] → server section only
[Copy Cron Results] → cron section only
[Copy 30-Day Log] → rolling log only
[Copy Slow Operations] → performance section only
[Copy All] → complete daily health report

Monthly tab:
[Copy Monthly Summary] → complete monthly report

Research Tab:
[Download Last Weekly Report]
[Download Full Report Day 1 to Today]
[Generate Now]

---

## Key Design Principles (LOCKED)

Every report has:
1. Header: platform · server specs · current state
2. Attention section: problems FIRST (most important)
3. Data tables: current vs normal vs threshold
4. Context section: what is normal for THIS server
5. Notes section: BLANK · AI fills recommendations

Why this works:
AI immediately knows:
→ What platform this is
→ What server specs
→ What numbers are normal vs abnormal
→ What specific action to take

Result: specific fixes · not generic advice
Example: "Your CX23 loop time 34s with 2,300 positions
means you need CX33 upgrade immediately"
Not: "check your server performance"

---

## Removed: Excel Reports

Reason: markdown is better for AI sharing
All data covered by 3 markdown reports
No downloads · no spreadsheets · instant sharing
GitHub URL shareable with any AI in seconds
