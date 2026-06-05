# Averion Admin Manual
## Owner's Guide — What Matters · What to Watch
### Non-Technical · Plain Language

---

## SECTION 1: YOUR DAILY CHECKS (5 minutes)

Every morning check Telegram Channel 3 for:
Daily Digest sent at 05:00 automatically

Look for these 4 things only:

✅ All green = do nothing · perfect day
🟡 Yellow warnings = note it · watch tomorrow
🔴 Red alerts = action needed (see Section 3)

---

## SECTION 2: YOUR DASHBOARD (what to watch)

Open admin dashboard → Tab 1 (Dashboard)

TOP BAR always shows:
🟢 Bot Running · Loop: 4.2s · Cycle 4,521

Loop time = most important number:
< 5s   = excellent ✅
5-15s  = good ✅
15-30s = watch carefully 🟡
> 30s  = upgrade server soon 🔴

Tab 6 (Health) shows everything detailed:
→ CPU % (should be < 60%)
→ RAM (should be < 70%)
→ Disk (should be < 70%)
→ Loop time chart (last 30 days)

---

## SECTION 3: ALERTS — WHAT THEY MEAN

🔴 RED ALERT (action needed):

"User API key rejected"
→ User's exchange key expired or invalid
→ Their bot paused automatically
→ No action from you · user gets Telegram alert
→ Just log it

"Reserve wallet empty"
→ User ran out of funds
→ Their bot paused automatically
→ No action needed · they get alert

"Bot crashed · auto-restarted"
→ PM2 fixed it automatically
→ Just note it · if happens daily → investigate
→ Check Health tab → Logs section

"Backup failed"
→ ACTION NEEDED
→ Run manual backup immediately
→ Admin Tab 8 → [Backup Now] button

"Disk > 80%"
→ ACTION NEEDED within 48 hours
→ Options: add Hetzner Volume or upgrade server
→ See Section 5

"CPU > 85% for 3+ days"
→ ACTION NEEDED
→ Time to upgrade server
→ See Section 5

---

## SECTION 4: SERVER HEALTH NUMBERS

Your server: Hetzner CX33
4 vCPU · 8GB RAM · 80GB Disk
Cost: €17.99/month

Normal ranges (CX33 with 1,566 research bots):
CPU:  10-40% normal · peak 60% acceptable
RAM:  2-4GB normal · 6GB = getting full
Disk: grows slowly · check monthly
Loop: 4-6s normal · < 15s acceptable

When to upgrade to next server:
ANY of these for 7+ consecutive days:
→ CPU avg > 60%
→ RAM avg > 6GB
→ Loop avg > 15s
→ Disk > 60%

Next server: Hetzner CX43 (€29.99/mo)
After that: AX41 €39/mo → AX52 €59/mo

---

## SECTION 5: HOW TO UPGRADE SERVER (30 min)

⚠️ BEFORE UPGRADING: Verify floating IP exists!
→ Hetzner console → Networking → Floating IPs
→ Must be assigned to current server
→ If missing: create + assign BEFORE upgrade
→ Without it: ALL user API keys break on upgrade



Step 0: VERIFY floating IP exists!
→ Hetzner console → Networking → Floating IPs
→ If none exists: create one and assign to server NOW
→ If none: all user API keys will break on upgrade

Step 1: Hetzner console → your server → Snapshots
→ Click [Create Snapshot]
→ Wait 5-10 minutes (server keeps running)

Step 2: Hetzner console → Servers → [Create Server]
→ Choose: CX43 (or larger)
→ From snapshot: select your snapshot
→ Click Create

Step 3: Wait 5 minutes for new server to start

Step 4: Go to new server → test it works
→ Check admin dashboard
→ Verify bot loop running

Step 5: Hetzner → Floating IPs
→ Reassign floating IP to new server
→ Takes 30 seconds
→ Done!

Step 6: After 48 hours if stable
→ Delete old server

Total cost: you pay for both servers for 2 days
= about €2 overlap cost
Zero downtime · users never notice

---

## SECTION 6: DB STORAGE (what fills up)

DB is stored on your server disk.
DB ≠ RAM or CPU · completely separate.

What takes space:
1. Trade history: 3 years → anonymize → delete year 5
   ~180MB per 100 users per year (tiny)

2. OHLCV data: auto-compressed after 90 days
   ~260MB per year (manageable)

3. Research scores: keeps forever (valuable)
   ~1.1GB per year

4. Logs: auto-deleted (30-90 days)
   Stays small automatically

Total estimate:
1 year · 100 users: ~2-3GB (fine)
1 year · 1,000 users: ~15-20GB (watch)
Disk fills at ~1,000+ users after 2 years

When disk hits 60%:
Option A: Add Hetzner Volume
→ Extra disk attached to server
→ €0.05/GB/month
→ +40GB = €2/month
→ Keeps old server · no migration

Option B: Upgrade to larger server
→ More disk + faster CPU + more RAM
→ Use snapshot method (Section 5)

---

## SECTION 7: RESEARCH BOTS

### Two-Account Structure (Important!)
Your admin account: admin@averionbot.com
Research account: research@averionbot.com (separate)

Research bots run UNDER the research account.
In your admin dashboard Tab 4 (Research):
→ You SEE all 1,566 research bots here
→ They actually run under research@ account
→ Your "My Bots" tab shows only YOUR personal bots
→ This is correct · not a bug

 (what to do)

Your 1,566 research bots run automatically.
You don't need to do anything normally.

Weekly on Sunday morning:
→ Check Telegram Channel 2 for research report
→ Shows which methods winning
→ Shows current champions

Monthly:
→ Download health report from GitHub
→ Share with Claude: "analyze my research data"
→ Get recommendations

When research shows a new champion:
→ Telegram notification
→ Smart DCA auto-switches if toggle ON
→ Nothing needed from you

Only time you need to act:
→ Increase trades per bot (Research Tab)
→ Start with 0 → 1 → 5 → 10 gradually

---

## SECTION 8: LOOP MODE SWITCH

Start: LOOP_MODE=asyncio (default)
Upgrade when: loop consistently > 15s after CX43

How to switch:
Admin Tab 8 (Controls) → Loop Mode → [Workers]
PM2 restarts automatically
7 exchange workers start
Takes 30 seconds · zero downtime

When to switch:
1. Upgrade server to CX43+ first
2. Verify server stable for 3 days
3. Then switch loop mode
Never switch during high activity

---

## SECTION 9: FIRST CUSTOMER CHECKLIST

Before accepting first real customer:
□ Paper trading stable 30+ days
□ Loop time consistently < 15s
□ Zero critical alerts for 7 days
□ All cron steps green for 7 days
□ Backup tested (restore verified)
□ Floating IP confirmed working
□ Legal docs published (Terms · Privacy · Risk)
□ Landing page live
□ averionbot.com domain active
□ Support email working

---

## SECTION 10: EMERGENCY CONTACTS

If everything breaks:
1. Check PM2: pm2 status
2. Check DB: systemctl status postgresql
3. Check logs: pm2 logs averion-live --lines 50
4. Share health report with Claude
5. Claude guides you step by step

Health report URL (always fresh):
https://github.com/baderbalubaid/Averion/blob/main/reports/health/latest.md

Share this URL with Claude when asking for help.
Claude immediately understands your server state.

---

## SECTION 11: MONTHLY ROUTINE (30 min/month)

Week 1:
→ Check research report (Sunday auto-generated)
→ Review top 3 performing methods
→ Note any concerning patterns

Week 2:
→ Download monthly health report
→ Share with Claude for analysis
→ Apply any recommendations

Week 3:
→ Review user activity (Users Tab)
→ Check any suspended accounts
→ Review outstanding fees

Week 4:
→ Verify backup integrity
→ Check disk usage trend
→ Plan server upgrade if needed
→ Review monthly revenue

---

## QUICK REFERENCE CARD

Loop time < 15s   = ✅ healthy
CPU < 60%         = ✅ healthy
RAM < 70%         = ✅ healthy
Disk < 70%        = ✅ healthy

Loop > 30s        = 🔴 upgrade server
CPU > 85% (7 days)= 🔴 upgrade server
RAM > 85%         = 🔴 upgrade server
Disk > 80%        = 🔴 add volume or upgrade

Server upgrade cost: €17.99 → €29.99 → €39 → €59
Add volume cost: +40GB = €2/month extra
Both options available in Hetzner console

---

## SECTION 12: DATA & STORAGE

Your DB stays small automatically:

Data deleted automatically:
→ Customer trades: after 3 years (tax done)
→ Research old data: after 2 years
→ Server logs: after 30 days
→ OHLCV old data: after 2 years

Data kept forever (tiny):
→ Champion history (few KB total)
→ Financial records 5 years (regulations)

DB size estimate:
Today: ~1GB
1 year: ~3GB
5 years: stabilizes at 5-10GB max
Never grows out of control

Tax reports:
Generated automatically January 1st
Sent to all users via Telegram + email
You also receive platform summary
Available 3 years then auto-deleted

Monthly cleanup runs automatically:
1st of month at 02:00
Cleans old data · frees space
You receive Telegram report of space freed

---

## SECTION 13: COMMON CUSTOMER ISSUES

### "My bot hasn't opened a trade in 3 days"
Check:
1. Is signal waiting? Bot detail → Entry Method status
2. Is reserve empty? Check reserve balance
3. Is exchange connected? Settings → Exchanges → Test
4. Is coin in top X? Daily classification at 04:30
5. Explanation: "Smart DCA waits for signal · avg 6-24h"

### "I got charged a fee but I lost money"
Check:
1. Was THIS specific trade profitable?
2. Fee = 20% of that trade's profit only
3. Other trades may be at loss · fee charged per profitable trade
4. Check: History tab → click trade → see fee column

### "My reserve is empty but I didn't get an alert"
Check:
1. Was Telegram connected? Alert only via Telegram
2. Check Admin → Users → that user → reserve history
3. Possible: fees auto-deducted faster than expected
4. Explain: fees deduct immediately when trade closes

### "I want a refund of my reserve wallet"
Policy: Reserve wallet balance is NON-REFUNDABLE
(used exclusively for platform fees)
Tell customer: "Reserve funds pay your performance fees.
We cannot refund as they cover services already rendered."
Exception: if NO trades ever made → goodwill decision yours

### "I deposited but balance didn't update"
Check:
1. Admin Tab 8 → Deposits → look for pending/failed
2. Check NOWPayments dashboard for that payment
3. Wait 1 hour (hourly polling fallback)
4. Manual match: [Match Deposit] button in Admin
