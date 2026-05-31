#!/bin/bash
# Averion — Hetzner Day 2 Setup Script
# Run after Day 1 is complete
# Requirements: domain DNS already pointing to server IP
# Run as root: bash hetzner_day2.sh

set -e
echo "🚀 Starting Averion Day 2 Setup..."

# ═══════════════════════════════
# VARIABLES — EDIT THESE FIRST
# ═══════════════════════════════
DOMAIN="averion.app"
EMAIL="your-email@gmail.com"

# ═══════════════════════════════
# STEP 1 — Nginx Configuration
# ═══════════════════════════════
echo "🌐 Step 1: Configuring Nginx..."
cat > /etc/nginx/sites-available/averion << NGINX
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/averion /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "✅ Nginx configured"

# ═══════════════════════════════
# STEP 2 — HTTPS Certificate
# ═══════════════════════════════
echo "🔐 Step 2: Getting HTTPS certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
echo "✅ HTTPS certificate installed"

# ═══════════════════════════════
# STEP 3 — Auto-renew Certificate
# ═══════════════════════════════
echo "🔄 Step 3: Setting up auto-renew..."
(crontab -l 2>/dev/null; echo "0 12 * * * certbot renew --quiet") | crontab -
echo "✅ Certificate auto-renew configured"

# ═══════════════════════════════
# STEP 4 — GitHub Actions Deploy Key
# ═══════════════════════════════
echo "🔑 Step 4: Setting up GitHub Actions..."
ssh-keygen -t ed25519 -C "averion-deploy" -f /root/.ssh/averion_deploy -N ""
echo ""
echo "Add this PUBLIC key to GitHub repo Settings → Deploy Keys:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat /root/.ssh/averion_deploy.pub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add this PRIVATE key to GitHub repo Settings → Secrets → HETZNER_SSH_KEY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat /root/.ssh/averion_deploy
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════
# STEP 5 — Test Live Order
# ═══════════════════════════════
echo ""
echo "🧪 Step 5: Ready for live order test"
echo "To test live trading:"
echo "1. Edit .env: nano /home/averion/Averion/.env"
echo "2. Set PAPER_MODE=false"
echo "3. Restart: pm2 restart averion"
echo "4. Open dashboard and verify red LIVE banner"
echo "5. Watch for first \$1 test order on MEXC"
echo "6. Set PAPER_MODE=true after test"
echo "7. Restart: pm2 restart averion"

# ═══════════════════════════════
# DONE
# ═══════════════════════════════
echo ""
echo "🎉 Day 2 Setup Complete!"
echo ""
echo "Your dashboard: https://$DOMAIN/dashboard"
echo "Admin panel: https://$DOMAIN/\$ADMIN_PATH"
echo ""
echo "Next steps:"
echo "1. Add GitHub deploy keys (shown above)"
echo "2. Setup UptimeRobot monitoring"
echo "3. Test live \$1 order on MEXC"
echo "4. Start 107 paper research bots"
