# Averion — Intelligent DCA Trading

> Automate. Adapt. Grow.

## Quick Start on Hetzner

### 1. Security Baseline
```bash
# Create non-root user
adduser trader
usermod -aG sudo trader

# Disable root SSH
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 8080
ufw enable

# Fail2ban
apt install fail2ban -y
systemctl enable fail2ban
```

### 2. Deploy Code
```bash
# Clone repo
git clone https://TOKEN@github.com/baderbalubaid/Averion.git
cd Averion

# Setup environment
cp .env.example .env
nano .env  # Fill in all values

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Start bot
pm2 start api.py --name averion --interpreter python3
pm2 save
pm2 startup
```

### 3. Setup Cron Jobs
```bash
# Open crontab
crontab -e

# Add these lines:
0 3 * * * /home/trader/Averion/automation/daily_cron.sh
0 4 * * 0 /home/trader/Averion/automation/weekly_cron.sh
```

### 4. Verify Running
```bash
pm2 status
pm2 logs averion
curl http://localhost:8080/status
```

## File Structure (Hetzner — Professional)
## Common Commands
```bash
pm2 restart averion    # Restart bot
pm2 logs averion       # View logs
pm2 stop averion       # Stop bot
git pull && pm2 restart averion  # Deploy update
```

## Emergency
```bash
# Bot not running
pm2 restart averion

# API error (usually CCXT)
pip install ccxt --upgrade --break-system-packages
pm2 restart averion

# Rollback
git revert HEAD
pm2 restart averion
```

## GitHub
- Repo: github.com/baderbalubaid/Averion
- Token: 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

## Dashboard
- Replit: https://bbd72f98-d728-46fe-81c6-af97d0011150-00-1c2g4v036wde1.sisko.replit.dev/dashboard
- Hetzner: https://averion.app/dashboard (after domain setup)
