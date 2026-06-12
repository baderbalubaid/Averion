#!/bin/bash
# Averion Research Reports Generator
# Run: bash /home/averion/Averion/generate_reports.sh

cd /home/averion/Averion

# Load token from .env
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'=' -f2)

echo "================================================"
echo " Averion Research Reports — $(date '+%Y-%m-%d %H:%M')"
echo "================================================"

echo "1️⃣  DCA Research Report..."
python3 generate_research_report.py

echo "2️⃣  Scalper Research Report..."
python3 generate_scalper_report.py

echo "3️⃣  Top 25 Trade CSVs..."

echo "4️⃣  Scalper Monthly Results..."
python3 generate_scalper_results.py
python3 generate_top25_csv.py

echo "5  Pushing to GitHub..."
git add reports/RESEARCH_REPORT_FULL.md \
        reports/RESEARCH_REPORT_SCALPER.md \
        reports/TOP20_DCA_RARS_TRADES.csv \
        reports/TOP20_DCA_SCORE_TRADES.csv \
        reports/TOP20_SCALPER_RARS_TRADES.csv \
        reports/TOP20_SCALPER_SCORE_TRADES.csv \
        reports/SCALPER_RESULTS.md
git commit -m "docs: reports $(date '+%Y-%m-%d %H:%M')" --allow-empty
git push https://baderbalubaid:${GITHUB_TOKEN}@github.com/baderbalubaid/Averion.git main

echo ""
echo "✅ Done! Download from GitHub:"
echo "DCA:     https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/RESEARCH_REPORT_FULL.md"
echo "Scalper: https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/RESEARCH_REPORT_SCALPER.md"
echo "DCA RARS CSV:    https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/TOP20_DCA_RARS_TRADES.csv"
echo "DCA Score CSV:   https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/TOP20_DCA_SCORE_TRADES.csv"
echo "Scalper RARS:    https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/TOP20_SCALPER_RARS_TRADES.csv"
echo "Scalper Score:   https://raw.githubusercontent.com/baderbalubaid/Averion/main/reports/TOP20_SCALPER_SCORE_TRADES.csv"
