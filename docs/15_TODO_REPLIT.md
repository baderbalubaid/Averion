# TODO — Replit Items

> All items below done via Replit terminal only.
> User is NOT a coder — provide exact commands.
> Always push to GitHub after every change.
> One command at a time — verify each result.

---

## Completed Items ✅

| Item | What | File | Status |
|------|------|------|--------|
| 1-3 | Fix endpoints · balance_history table | api.py + db | ✅ |
| 4-6 | Mobile responsive · Home tab · Exchange cards | dashboard | ✅ |
| 7-8 | Settings tab · History tab | dashboard | ✅ |
| 9-10 | Bots tab L1+L2 · positions table | dashboard | ✅ |
| 11-12 | Exchange Detail · Capital chart | dashboard | ✅ |
| 13-15 | Days Open · TP Armed · Queued flags | api.py | ✅ |
| 16-17 | History date range · fees 20% + net profit | dashboard | ✅ |
| 18 | requirements.txt | new file | ✅ |
| 19 | .env.example | new file | ✅ |
| 20 | .gitignore | new file | ✅ |
| 21 | README.md | new file | ✅ |
| 22 | automation/daily_cron.sh | new file | ✅ |
| 23 | automation/weekly_cron.sh | new file | ✅ |

---

## ✅ Item 24 — Bots Tab Flat List (COMPLETE)

### What It Is
Complete redesign of the Bots tab.
Change from grouped-by-exchange layout
to a clean flat list with one row per bot.

### Why Previous Attempts Failed
Terminal paste mode corrupted Python script quotes.
Patching existing file = dangerous.
New approach = write complete new dashboard.html.

### Exact Approach
1. Claude writes complete new dashboard.html from scratch
2. Includes ALL existing tabs unchanged
3. Only Bots tab section is new design
4. Single Python script writes entire file
5. No patching · no find/replace · no quote issues

### New Bots Tab Design

#### Desktop Layout


#### Exchange Badges
- [M] MEXC = Blue #38BDF8
- [B] Binance = Amber #F59E0B
- [K] KuCoin = Green #10D98A
- [O] OKX = White #E2E8F0
- [G] Gate.io = Blue lighter
- [By] Bybit = Orange #FB923C
- [Bg] Bitget = Purple #A78BFA

#### Two Toggles Per Bot (inline)
- T = Trading toggle (opens new positions)
- DCA = DCA toggle (averages existing)
- Green when ON · Gray when OFF

#### Kebab Menu (⋯)
- Edit bot settings
- Duplicate bot
- Delete bot

#### Mobile Layout
- 2-line condensed row
- Both toggles still visible inline
- Exchange badge visible

### How To Start This Item
Tell Claude in new chat:
"Item 24 is COMPLETE — do not work on this.
Read 00_START_HERE.md and 15_TODO_REPLIT.md from GitHub first.
Then help me code it via Replit terminal."

---

## 🔴 Item 25 — After Item 24

Generate updated documentation after Item 24 confirmed working.
Share with ChatGPT and Gemini for review.

---

## 🔴 Item 26 — Dashboard Comment Markers

Add clear section markers to dashboard.html:
- Makes finding sections easy
- Safe terminal editing
- Preparation for Hetzner split

Example markers:


---

## Replit Workflow Rules

1. Always backup before changes:
   python3 -c "import shutil;shutil.copy('dashboard.html','dashboard_backup.html')"

2. Always push after every change:
   git add . && git commit -m "message" && git push https://baderbalubaid:YOUR_TOKEN@github.com/baderbalubaid/Averion.git main

3. Always verify push worked:
   git log --oneline -3

4. Test dashboard after every change:
   Open dashboard URL in browser
   Check all tabs still work
   Check BTC price showing
