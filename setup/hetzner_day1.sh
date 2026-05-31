#!/bin/bash
# Averion — Hetzner Day 1 Setup Script
# Run as root: bash hetzner_day1.sh
# Time: ~15 minutes

set -e
echo "🚀 Starting Averion Day 1 Setup..."

# ═══════════════════════════════
# STEP 1 — System Update
# ═══════════════════════════════
echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y
echo "✅ System updated"

# ═══════════════════════════════
# STEP 2 — Install Dependencies
# ═══════════════════════════════
echo "📦 Step 2: Installing dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-client \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    chrony \
    git \
    ufw \
    curl \
    nano
echo "✅ Dependencies installed"

# ═══════════════════════════════
# STEP 3 — Security Setup
# ═══════════════════════════════
echo "🔒 Step 3: Setting up security..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 8080
ufw --force enable
systemctl enable fail2ban
systemctl start fail2ban
echo "✅ Firewall and fail2ban configured"

# ═══════════════════════════════
# STEP 4 — Clock Sync
# ═══════════════════════════════
echo "🕐 Step 4: Setting up clock sync..."
systemctl enable chrony
systemctl start chrony
chronyc makestep
echo "✅ Chrony NTP sync active"

# ═══════════════════════════════
# STEP 5 — PostgreSQL Setup
# ═══════════════════════════════
echo "🗄️ Step 5: Setting up PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
sudo -u postgres psql -c "CREATE USER averion WITH PASSWORD 'CHANGE_THIS_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE averion OWNER averion;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE averion TO averion;"
echo "✅ PostgreSQL configured"

# ═══════════════════════════════
# STEP 6 — Redis Setup
# ═══════════════════════════════
echo "📮 Step 6: Setting up Redis..."
systemctl enable redis-server
systemctl start redis-server
echo "✅ Redis running"

# ═══════════════════════════════
# STEP 7 — Create Averion User
# ═══════════════════════════════
echo "👤 Step 7: Creating averion user..."
useradd -m -s /bin/bash averion 2>/dev/null || echo "User already exists"
echo "✅ User averion ready"

# ═══════════════════════════════
# STEP 8 — Clone Repository
# ═══════════════════════════════
echo "📥 Step 8: Cloning repository..."
cd /home/averion
git clone https://github.com/baderbalubaid/Averion.git
chown -R averion:averion /home/averion/Averion
echo "✅ Repository cloned"

# ═══════════════════════════════
# STEP 9 — Python Dependencies
# ═══════════════════════════════
echo "🐍 Step 9: Installing Python packages..."
cd /home/averion/Averion
pip3 install -r requirements.txt --break-system-packages
echo "✅ Python packages installed"

# ═══════════════════════════════
# STEP 10 — Database Schema
# ═══════════════════════════════
echo "🗄️ Step 10: Creating database tables..."
psql -U averion -d averion -h localhost < /home/averion/Averion/setup/schema.sql
echo "✅ Database tables created"

# ═══════════════════════════════
# STEP 11 — PM2 Setup
# ═══════════════════════════════
echo "⚙️ Step 11: Setting up PM2..."
npm install -g pm2
pm2 start /home/averion/Averion/main.py --name averion --interpreter python3
pm2 startup
pm2 save
echo "✅ PM2 configured"

# ═══════════════════════════════
# STEP 12 — Cron Jobs
# ═══════════════════════════════
echo "⏰ Step 12: Installing cron jobs..."
(crontab -l 2>/dev/null; echo "0 * * * * /home/averion/Averion/automation/health_check.sh >> /var/log/averion_health.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * /home/averion/Averion/automation/daily_cron.sh >> /var/log/averion_daily.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "30 4 * * 0 /home/averion/Averion/automation/weekly_cron.sh >> /var/log/averion_weekly.log 2>&1") | crontab -
echo "✅ Cron jobs installed"

# ═══════════════════════════════
# STEP 13 — Create Backups Folder
# ═══════════════════════════════
echo "💾 Step 13: Creating backup folder..."
mkdir -p /home/averion/backups
chown averion:averion /home/averion/backups
echo "✅ Backup folder ready"

# ═══════════════════════════════
# DONE
# ═══════════════════════════════
echo ""
echo "🎉 Day 1 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file: cp /home/averion/Averion/setup/env.example /home/averion/Averion/.env"
echo "2. Edit .env: nano /home/averion/Averion/.env"
echo "3. Restart bot: pm2 restart averion"
echo "4. Check status: pm2 status"
echo "5. Continue with Day 2 setup (domain + HTTPS)"
echo ""
echo "Dashboard: http://YOUR_SERVER_IP:8080/dashboard"
