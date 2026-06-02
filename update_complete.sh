#!/bin/bash
cd ~/workspace

cat docs/00_START_HERE.md \
docs/00_BADER_NOTES.md \
docs/15_TODO_REPLIT.md \
    docs/13_LOCKED_DECISIONS.md \
    docs/16_TODO_HETZNER.md \
    docs/03_TRADING_SYSTEM.md \
    docs/04_RISK_AND_SAFETY.md \
    docs/05_SMART_DCA_ENGINE.md \
    docs/06_BUSINESS_MODEL.md \
    docs/07_DASHBOARD_AND_UI.md \
    docs/08_BOT_CREATION_WIZARD.md \
    docs/09_INFRASTRUCTURE.md \
    docs/10_DATABASE_AND_API.md \
    docs/11_ADMIN_SYSTEM.md \
    docs/12_PHASE_ROADMAP.md \
    docs/14_AI_REVIEWS_AND_RESOLUTIONS.md \
    docs/01_PROJECT_OVERVIEW.md \
    docs/02_BRANDING_AND_VISION.md \
    setup/schema.sql \
    setup/hetzner_day1.sh \
    setup/hetzner_day2.sh \
    setup/DAY1_CHECKLIST.md \
    setup/env.example \
    setup/init_db.py \
setup/launch_research_bots.py \
setup/research_bots.json \
    main.py database.py api.py bot_loop.py \
config.py dca_logic.py write_dashboard.py \
    exchanges.py telegram.py auth.py email_service.py \
    index.html login.html register.html dashboard.html admin.html \
    > averion_COMPLETE.md

echo "✅ Done! $(wc -l < averion_COMPLETE.md) lines"
