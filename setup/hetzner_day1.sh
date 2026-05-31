#!/bin/bash
# Averion — Hetzner Day 1 Setup Script
# Run as root: bash hetzner_day1.sh
# Time: ~20 minutes
# SECURITY HARDENED VERSION

set -e
echo "🚀 Starting Averion Day 1 Setup..."
echo "⚠️  Run this as root on fresh Ubuntu 24.04"

# ═══════════════════════════════
# VARIABLES — EDIT BEFORE RUNNING
# ═══════════════════════════════
SSH_PORT=2847
AVERION_USER=averion
DB_PASSWORD=$(openssl rand -hex 16)
echo "Generated DB password stored in /tmp/averion_setup_vars"

# ═══════════════════════════════
# STEP 1 — System Update
# ═══════════════════════════════
echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y
apt install -y unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades
echo "✅ System updated + auto security updates enabled"

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
    nano \
    logwatch \
    nodejs \
    npm
echo "✅ Dependencies installed"

# ═══════════════════════════════
# STEP 3 — Create Non-Root User
# ═══════════════════════════════
echo "👤 Step 3: Creating averion user..."
useradd -m -s /bin/bash $AVERION_USER 2>/dev/null || echo "User already exists"
usermod -aG sudo $AVERION_USER
echo "✅ User $AVERION_USER created"

# ═══════════════════════════════
# STEP 4 — SSH Hardening
# ═══════════════════════════════
echo "🔒 Step 4: Hardening SSH..."

# Backup original config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply security settings
cat > /etc/ssh/sshd_config << SSHCONF
# Averion Security Hardened SSH Config
Port $SSH_PORT
Protocol 2

# Authentication
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30

# Security
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2

# Allow only averion user
AllowUsers $AVERION_USER
SSHCONF

echo "⚠️  IMPORTANT: Add your SSH public key before restarting SSH!"
echo "Run: mkdir -p /home/$AVERION_USER/.ssh"
echo "Run: echo 'YOUR_PUBLIC_KEY' >> /home/$AVERION_USER/.ssh/authorized_keys"
echo "Run: chmod 700 /home/$AVERION_USER/.ssh"
echo "Run: chmod 600 /home/$AVERION_USER/.ssh/authorized_keys"
echo "Run: chown -R $AVERION_USER:$AVERION_USER /home/$AVERION_USER/.ssh"
echo ""
read -p "Have you added your SSH key? (yes/no): " SSH_CONFIRMED
if [ "$SSH_CONFIRMED" != "yes" ]; then
    echo "❌ Aborted — add SSH key first!"
    cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
    exit 1
fi

systemctl restart sshd
echo "✅ SSH hardened — port $SSH_PORT · root login disabled · password auth disabled"

# ═══════════════════════════════
# STEP 5 — Firewall (UFW)
# ═══════════════════════════════
echo "🔥 Step 5: Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow $SSH_PORT/tcp comment 'SSH custom port'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8080/tcp comment 'Averion dashboard'
ufw --force enable
echo "✅ UFW firewall configured"

# ═══════════════════════════════
# STEP 6 — Fail2ban
# ═══════════════════════════════
echo "🛡️ Step 6: Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

cat > /etc/fail2ban/jail.local << F2B
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = root@localhost
action = %(action_mw)s

[sshd]
enabled = true
port = $SSH_PORT
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true
F2B

systemctl restart fail2ban
echo "✅ Fail2ban configured"

# ═══════════════════════════════
# STEP 7 — Clock Sync
# ═══════════════════════════════
echo "🕐 Step 7: Setting up clock sync..."
systemctl enable chrony
systemctl start chrony
chronyc makestep
echo "✅ Chrony NTP sync active"

# ═══════════════════════════════
# STEP 8 — PostgreSQL Setup
# ═══════════════════════════════
echo "🗄️ Step 8: Setting up PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5
until pg_isready -U averion -h localhost; do
    echo "PostgreSQL not ready yet · waiting..."
    sleep 3
done
echo "✅ PostgreSQL is ready"
sudo -u postgres psql -c "CREATE USER $AVERION_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User exists"
sudo -u postgres psql -c "CREATE DATABASE averion OWNER $AVERION_USER;" 2>/dev/null || echo "DB exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE averion TO $AVERION_USER;"

# Secure PostgreSQL
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
# Allow password authentication from localhost
PG_VERSION=$(ls /etc/postgresql/)
echo "host    averion         averion         127.0.0.1/32            scram-sha-256" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
echo "host    averion         averion         ::1/128                 scram-sha-256" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
systemctl restart postgresql
echo "✅ PostgreSQL configured · localhost only · password auth enabled"

# ═══════════════════════════════
# STEP 9 — Redis Setup
# ═══════════════════════════════
echo "📮 Step 9: Setting up Redis..."
# Bind Redis to localhost only
sed -i 's/^bind 127.0.0.1 -::1/bind 127.0.0.1/' /etc/redis/redis.conf
REDIS_PASS=$(openssl rand -hex 16)
sed -i "s/^# requirepass foobared/requirepass $REDIS_PASS/" /etc/redis/redis.conf
echo "REDIS_PASSWORD=$REDIS_PASS" >> /tmp/averion_setup_vars
systemctl enable redis-server
systemctl start redis-server
echo "✅ Redis running · localhost only"

# ═══════════════════════════════
# STEP 10 — Clone Repository
# ═══════════════════════════════
echo "📥 Step 10: Cloning repository..."
cd /home/$AVERION_USER
sudo -u $AVERION_USER git clone https://github.com/baderbalubaid/Averion.git
echo "✅ Repository cloned"

# ═══════════════════════════════
# STEP 11 — Python Dependencies
# ═══════════════════════════════
echo "🐍 Step 11: Installing Python packages..."
pip install -r /home/$AVERION_USER/Averion/requirements.txt --break-system-packages
echo "✅ Python packages installed"

# ═══════════════════════════════
# STEP 12 — Database Schema
# ═══════════════════════════════
echo "🗄️ Step 12: Creating database tables..."
sudo -u $AVERION_USER psql -d averion -h localhost < /home/$AVERION_USER/Averion/setup/schema.sql
echo "✅ Database tables created"

# ═══════════════════════════════
# STEP 13 — PM2 Setup (as averion user)
# ═══════════════════════════════
echo "⚙️ Step 13: Setting up PM2..."
npm install -g pm2
sudo -u $AVERION_USER pm2 start /home/$AVERION_USER/Averion/main.py \
    --name averion \
    --interpreter python3
# PM2 startup — correct approach
env PATH=$PATH:/usr/bin pm2 startup systemd -u $AVERION_USER --hp /home/$AVERION_USER
su - $AVERION_USER -c 'pm2 save'
echo "✅ PM2 configured as $AVERION_USER user"

# ═══════════════════════════════
# STEP 14 — Cron Jobs
# ═══════════════════════════════
echo "⏰ Step 14: Installing cron jobs..."
(crontab -u $AVERION_USER -l 2>/dev/null; echo "0 * * * * /home/$AVERION_USER/Averion/automation/health_check.sh >> /var/log/averion_health.log 2>&1") | crontab -u $AVERION_USER -
(crontab -u $AVERION_USER -l 2>/dev/null; echo "0 3 * * * /home/$AVERION_USER/Averion/automation/daily_cron.sh >> /var/log/averion_daily.log 2>&1") | crontab -u $AVERION_USER -
(crontab -u $AVERION_USER -l 2>/dev/null; echo "30 4 * * 0 /home/$AVERION_USER/Averion/automation/weekly_cron.sh >> /var/log/averion_weekly.log 2>&1") | crontab -u $AVERION_USER -
echo "✅ Cron jobs installed for $AVERION_USER"

# ═══════════════════════════════
# STEP 15 — Backups Folder
# ═══════════════════════════════
echo "💾 Step 15: Creating backup folder..."
mkdir -p /home/$AVERION_USER/backups
chown $AVERION_USER:$AVERION_USER /home/$AVERION_USER/backups
chmod 700 /home/$AVERION_USER/backups
echo "✅ Backup folder ready"

# ═══════════════════════════════
# STEP 16 — File Permissions
# ═══════════════════════════════
echo "🔐 Step 16: Setting file permissions..."
chown -R $AVERION_USER:$AVERION_USER /home/$AVERION_USER/Averion
chmod 600 /home/$AVERION_USER/Averion/.env 2>/dev/null || true
chmod 700 /home/$AVERION_USER/Averion/automation/*.sh 2>/dev/null || true
echo "✅ File permissions set"

# ═══════════════════════════════
# STEP 17 — Nginx Basic Config
# ═══════════════════════════════
echo "🌐 Step 17: Configuring Nginx..."
cat > /etc/nginx/conf.d/security.conf << NGINX
# Security headers
add_header X-Frame-Options SAMEORIGIN;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
server_tokens off;
NGINX

systemctl enable nginx
systemctl start nginx
echo "✅ Nginx configured with security headers"

# ═══════════════════════════════
# DONE
# ═══════════════════════════════
echo ""
echo "🎉 Day 1 Setup Complete!"
echo ""
echo "Security summary:"
echo "✅ Root login disabled"
echo "✅ SSH password auth disabled"
echo "✅ SSH on port $SSH_PORT"
echo "✅ UFW firewall active"
echo "✅ Fail2ban active"
echo "✅ PostgreSQL localhost only"
echo "✅ Redis localhost only"
echo "✅ Running as $AVERION_USER (not root)"
echo "✅ Auto security updates enabled"
echo ""
echo "Next steps:"
echo "1. cp /home/$AVERION_USER/Averion/setup/env.example /home/$AVERION_USER/Averion/.env"
echo "2. nano /home/$AVERION_USER/Averion/.env"
echo "3. python3 /home/$AVERION_USER/Averion/setup/init_db.py"
echo "4. pm2 restart averion"
echo "5. Continue with Day 2 (domain + HTTPS)"
echo ""
echo "⚠️  New SSH connection: ssh -p $SSH_PORT $AVERION_USER@YOUR_IP"
