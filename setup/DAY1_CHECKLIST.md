# Averion — Hetzner Day 1 Checklist
> Follow in exact order. Check each item before moving to next.
> All commands in hetzner_day1.sh — run that first!

---

## BEFORE YOU START
- [ ] Hetzner ID verification complete
- [ ] Server IP address noted
- [ ] GitHub token ready (in Replit .env)
- [ ] Telegram bot created (@BotFather)
- [ ] Telegram admin chat ID noted
- [ ] NOWPayments account created
- [ ] TRC20 wallet address ready

---

## PHASE 1 — Server Access (5 min)
- [ ] SSH into server: ssh root@YOUR_IP
- [ ] Note server IP address
- [ ] Add your SSH public key to server before running script!
- [ ] Run Day 1 script (asks to confirm SSH key added)
- [ ] After setup: ssh -p 2847 averion@YOUR_IP

## PHASE 2 — Run Day 1 Script (15 min)
- [ ] Clone repo: git clone https://github.com/baderbalubaid/Averion.git
- [ ] Run script: bash Averion/setup/hetzner_day1.sh
- [ ] Confirm: "Day 1 Setup Complete!" message shown
- [ ] Verify PostgreSQL running: systemctl status postgresql
- [ ] Verify Redis running: systemctl status redis-server
- [ ] Verify PM2 running: pm2 status

## PHASE 3 — Environment Setup (10 min)
- [ ] Copy env: cp /home/averion/Averion/setup/env.example /home/averion/Averion/.env
- [ ] Generate Fernet key:
      python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
- [ ] Edit .env: nano /home/averion/Averion/.env
- [ ] Fill in: DB_PASSWORD (strong password)
- [ ] Fill in: ADMIN_PATH (random string e.g. ops-x7k2m)
- [ ] Fill in: ADMIN_PASSWORD
- [ ] Fill in: OWNER_WALLET_TRC20
- [ ] Fill in: TELEGRAM_BOT_TOKEN
- [ ] Fill in: TELEGRAM_ADMIN_CHAT_ID
- [ ] Fill in: FERNET_KEY (from step above)
- [ ] Fill in: GITHUB_TOKEN
- [ ] Confirm PAPER_MODE=true
- [ ] Save and exit: Ctrl+X → Y → Enter

## PHASE 4 — Database Setup (5 min)
- [ ] Run schema: psql -U averion -d averion -h localhost < /home/averion/Averion/setup/schema.sql
- [ ] Initialize DB: python3 /home/averion/Averion/setup/init_db.py
- [ ] Should see: all tables ✅ (no errors in output)
- [ ] Admin user created ✅

## PHASE 5 — Bot Startup (5 min)
- [ ] Restart bot with .env: pm2 restart averion
- [ ] Check logs: pm2 logs averion --lines 20
- [ ] Verify no errors in logs
- [ ] Test dashboard: curl http://localhost:8080/status
- [ ] Should return: running + BTC price

## PHASE 6 — Cron Jobs (5 min)
- [ ] Verify cron installed: crontab -l
- [ ] Should see 3 cron jobs:
      * Health check every hour
      * Daily cron at 3am
      * Weekly cron Sunday 4:30am
- [ ] Make scripts executable:
      chmod +x /home/averion/Averion/automation/*.sh

## PHASE 7 — Security (5 min)
- [ ] Verify firewall: ufw status
- [ ] Should show: 2847 · 80 · 443 · 8080 ALLOW
- [ ] Verify fail2ban: systemctl status fail2ban
- [ ] Verify chrony: chronyc tracking

## PHASE 8 — GitHub Actions (5 min)
- [ ] Go to: github.com/baderbalubaid/Averion/settings/secrets/actions
- [ ] Add secret: HETZNER_IP = your server IP
- [ ] Add secret: HETZNER_SSH_KEY = your SSH private key
- [ ] Test: make small change → git push → verify auto-deploy

## PHASE 9 — Monitoring (5 min)
- [ ] Create UptimeRobot account: uptimerobot.com
- [ ] Add monitor:
      Type: HTTP(S)
      URL: http://YOUR_IP:8080/status
      Interval: 5 minutes
      Alert: Telegram + Email
- [ ] Verify monitor shows green

## PHASE 10 — Final Verification (5 min)
- [ ] Open dashboard: http://YOUR_IP:8080/dashboard
- [ ] Verify BTC price showing
- [ ] Verify all tabs working
- [ ] Verify paper mode active (PAPER badge visible)
- [ ] Send test Telegram message manually
- [ ] Check PM2: pm2 status → averion = online

---

## DAY 1 COMPLETE ✅
Total time: ~55 minutes

Next: Day 2 Checklist (domain + HTTPS + live test)

---

## DAY 2 CHECKLIST

## PHASE 11 — Domain (30 min wait)
- [ ] Buy averionbot.com domain
- [ ] Point A record to Hetzner IP
- [ ] Wait for DNS propagation (check: dig averionbot.com)

## PHASE 12 — Run Day 2 Script (10 min)
- [ ] Edit domain: nano /home/averion/Averion/setup/hetzner_day2.sh
- [ ] Change DOMAIN="averionbot.com"
- [ ] Change EMAIL="your@email.com"
- [ ] Run: bash /home/averion/Averion/setup/hetzner_day2.sh
- [ ] Verify HTTPS: https://averionbot.com/dashboard

## PHASE 13 — Live Order Test (10 min)
- [ ] Edit .env: PAPER_MODE=false
- [ ] Restart: pm2 restart averion
- [ ] Verify red LIVE banner in dashboard
- [ ] Wait for first $1 order on MEXC
- [ ] Confirm order on MEXC exchange website
- [ ] Set PAPER_MODE=true
- [ ] Restart: pm2 restart averion
- [ ] Verify PAPER badge back

## PHASE 14 — Research Bots (30 min)
- [ ] Set up 144 paper research bots
- [ ] Start with 10 trades per bot limit
- [ ] Monitor loop time: pm2 logs averion
- [ ] Verify all bots running in dashboard

---

## DAY 2 COMPLETE ✅
Platform is live! 6 month research period begins.

---

## IMPORTANT NOTES — Lessons Learned

### Python Packages
- Always use: pip install -r requirements.txt --break-system-packages
- Never use pip3 on Hetzner — use pip only
- requirements.txt has exact pinned versions — never change without testing
- If asked "Install Replit tools?" → type n (Hetzner only question)
- Do NOT run pip install without --break-system-packages on Ubuntu 24.04

### File Paths
- Never hardcode /home/user/ — use os.path.expanduser('~/') or os.getcwd()
- Replit path = /home/runner/workspace/
- Hetzner path = /home/averion/Averion/
- Always use relative paths in scripts when possible

### Git Push
- Always use: source .env first to load GITHUB_TOKEN
- Push command: git push https://baderbalubaid:$GITHUB_TOKEN@github.com/baderbalubaid/Averion.git main
- If push rejected for secrets: go to GitHub security URL and allow
- If authentication failed: token may be expired — generate new one

### Database
- Always run schema.sql BEFORE init_db.py
- PostgreSQL user = averion · database = averion
- Connection: psql -U averion -d averion -h localhost
- If connection refused: systemctl start postgresql

### Excel Reports
- Generated daily at 4am automatically
- Saved to: /home/averion/Averion/reports/
- Download via SCP: scp root@IP:/home/averion/Averion/reports/latest.xlsx .
- Open in Excel or Google Sheets
- Never rename columns — AI workflows depend on stable names

## Email Deliverability Setup (Day 2 — CRITICAL)

Do this right after buying averionbot.com domain:

### Step 1 — Verify domain in Resend
- Login to resend.com
- Domains → Add Domain → averionbot.com
- Resend will give you DNS records to add

### Step 2 — Add DNS records in domain registrar
Copy these 3 records from Resend dashboard and add to your DNS:

SPF:
- Type: TXT · Name: @ · Value: v=spf1 include:spf.resend.com ~all

DKIM:
- Type: TXT · Name: resend._domainkey
- Value: (copy exact value from Resend dashboard)

DMARC:
- Type: TXT · Name: _dmarc
- Value: v=DMARC1; p=none; rua=mailto:admin@averionbot.com


### Step 3 — Verify in Resend dashboard
- Wait 10-30 minutes for DNS propagation
- Resend dashboard → Domain → Verify
- All 3 records must show ✅

### Step 4 — Test email
- Send test from Resend dashboard
- Check inbox AND junk
- If junk → check DNS records again

### Why This Matters
- Without SPF/DKIM → emails go to junk
- With proper setup → mostly inbox
- New domain takes 2-3 months to build reputation
- Resend has best deliverability of free email services
