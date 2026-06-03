
## Bot State Machine & Reserve Floor — Final (LOCKED)

---

## TP Rule (LOCKED · ABSOLUTE)

TP is ALWAYS ON · no exceptions · ever.
No toggle · not shown to customer · not mentioned in UI.
TP fires regardless of: reserve balance · bot status · floor settings · any condition.
Reason: TP = profit → 20% fee → owner income → customer profit.
TP is common sense · never needs explanation.

Customer bot controls show ONLY:
[T toggle] = Trading (new positions)
[DCA toggle] = DCA averaging
TP: silent · always active · never displayed

---

## Reserve Floor System (LOCKED)

Each bot has its OWN independent floor.
Set in bot creation wizard Step 6.
Each bot evaluated independently against its own floor.

Fields per bot:
reserve_floor: minimum USDT never touched
resume_threshold: must be higher than floor
auto_resume: ON (default) or OFF

---

## Bot State Machine (LOCKED)

STATE 1 — Normal (reserve > floor):
→ Trading: ON (new positions open freely)
→ DCA: ON (existing positions average down)
→ TP: ALWAYS ON
→ Queue: active · scores all positions

STATE 2 — Floor Hit (reserve <= floor):
→ Trading: OFF (no new positions)
→ DCA: ON (existing positions keep averaging)
→ TP: ALWAYS ON
→ Queue: DCA only · no new entry signals checked
→ Snapshot: saved (bot status at moment of pause)
→ Telegram: floor hit notification sent

STATE 3 — Zero Capital:
→ Trading: OFF
→ DCA: fires ONLY when capital available (queue tries every 60s)
→ TP: ALWAYS ON (fires when price hits target)
→ When TP fires → capital freed → queue rescores immediately
→ Platform works silently · no intervention needed

STATE 4 — Resumed (reserve > threshold):
→ Auto-Resume ON → Trading back ON automatically
→ Snapshot restored · everything continues from where paused
→ Auto-Resume OFF → stays paused · user resumes manually
→ Telegram: resumed notification sent

---

## Per-Bot Independence Example (LOCKED)

Bot A: floor=$50 · threshold=$75
Bot B: floor=$30 · threshold=$50
Reserve: $500

Reserve drops to $50:
→ Bot A: Trading OFF · DCA ON · TP ON
→ Bot B: Trading ON · DCA ON · TP ON (still above $30)
→ Telegram: "Bot A paused · DCA continues"

Bot A DCAs fire · reserve drops to $30:
→ Bot A: Trading OFF · DCA ON · TP ON
→ Bot B: Trading OFF · DCA ON · TP ON
→ Telegram: "Bot B paused · DCA continues"

TP fires on Bot A position:
→ Profit + 20% fee collected
→ Capital freed → reserve rises to $55
→ Bot B threshold = $50 → $55 > $50 → Bot B resumes ✅
→ Telegram: "Bot B resumed ✅"

Reserve rises to $80:
→ Bot A threshold = $75 → $80 > $75 → Bot A resumes ✅
→ Telegram: "Bot A resumed ✅"
→ All bots trading normally again

Customer never touched anything ✅

---

## True Set and Forget (LOCKED)

Customer deposits $500 · sets floors · walks away:
Week 1: trading normally
Week 4: some bots hit floor · DCA continues · TP always on
Week 6: TP fires → capital freed → bots resume automatically
Week 8: trading normally again
Month 3: same cycle continues

Customer gets Telegram updates · never needs to log in.
Only optional intervention:
→ Top up if wants faster recovery
→ Change floor/threshold if wants different behavior
Both always optional · never mandatory.

---

## Notifications (LOCKED)

Floor hit (per bot):
🟡 BOT PAUSED · Trading OFF
Bot: My BTC Bot
Reserve: $50.00 (floor reached)
DCA still active on existing positions
Resume at: $75.00
[Top Up] to resume faster

Bot resumed automatically:
🟢 BOT RESUMED
Bot: My BTC Bot
Reserve: $80.00 ✅
Trading restored automatically

All bots paused (zero capital):
🔴 ALL BOTS PAUSED
Reserve: $0.00
Waiting for positions to close (TP)
[Top Up] to resume immediately

Weekly reminder (once per week · not daily):
🟡 REMINDER: Bots still paused
Bot: My BTC Bot · Reserve: $12.30
Need $75.00 to resume
[Top Up]

---

## System Design Implications (LOCKED)

Bot loop checks every 60 seconds:
1. Is reserve > bot floor? → Trading allowed
2. Is capital available for DCA? → DCA fires
3. Has TP price been reached? → ALWAYS checked · ALWAYS fires
4. Is reserve > threshold + auto_resume ON? → Resume Trading

TP check: independent of all other conditions
TP never blocked by: floor · capital · status · any setting
