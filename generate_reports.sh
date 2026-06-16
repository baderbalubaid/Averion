#!/bin/bash
# Averion Research Reports Generator
# Run: bash /home/averion/Averion/generate_reports.sh

cd /home/averion/Averion

GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'=' -f2)

echo "================================================"
echo " Averion Research Reports — $(date '+%Y-%m-%d %H:%M')"
echo "================================================"

echo "1️⃣  DCA Research Report + CSVs..."
python3 generate_dca_report.py

echo "2️⃣  Scalper E58 Research Report + CSVs..."
python3 generate_scalper_report.py

echo "3️⃣  Scalper V2 E58v2 Research Report + CSVs..."
python3 generate_scalper_v2_report.py

echo "4️⃣  Pushing to GitHub..."
git add reports/
git commit -m "docs: research reports $(date '+%Y-%m-%d %H:%M')" --allow-empty
git push https://baderbalubaid:${GITHUB_TOKEN}@github.com/baderbalubaid/Averion.git main

echo ""
echo "✅ Done! Reports available at:"
echo ""
echo "📊 DCA Report:"
echo "  https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/RESEARCH_DCA.md"
echo ""
echo "⚡ Scalper E58 Report:"
echo "  https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/RESEARCH_SCALPER.md"
echo ""
echo "⚡ Scalper V2 Report:"
echo "  https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/RESEARCH_SCALPER_V2.md"
echo ""
echo "📁 CSVs (top 5 bots + all trades):"
echo "  DCA RARS:       reports/TOP5_DCA_RARS_BOTS.csv + TRADES.csv"
echo "  DCA Score:      reports/TOP5_DCA_SCORE_BOTS.csv + TRADES.csv"
echo "  Scalper RARS:   reports/TOP5_SCALPER_RARS_BOTS.csv + TRADES.csv"
echo "  Scalper Score:  reports/TOP5_SCALPER_SCORE_BOTS.csv + TRADES.csv"
echo "  ScalperV2 RARS: reports/TOP5_SCALPERV2_RARS_BOTS.csv + TRADES.csv"
echo "  ScalperV2 Score:reports/TOP5_SCALPERV2_SCORE_BOTS.csv + TRADES.csv"
