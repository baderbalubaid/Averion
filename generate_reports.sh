#!/bin/bash
# Averion Research Reports Generator
# Run: bash /home/averion/Averion/generate_reports.sh

cd /home/averion/Averion

# Load token from .env
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'=' -f2)
if [ -z "$GITHUB_TOKEN" ]; then
    # Fallback: hardcoded (acceptable since .env is not pushed to GitHub)
    GITHUB_TOKEN="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"
fi

echo "================================================"
echo " Averion Research Reports — $(date '+%Y-%m-%d %H:%M')"
echo "================================================"

echo "1️⃣  DCA Research Report..."
python3 generate_research_report.py

echo "2️⃣  Scalper Research Report..."
python3 generate_scalper_report.py

echo "3️⃣  Top 25 Trade CSVs..."
python3 generate_top25_csv.py

echo "4️⃣  Pushing to GitHub..."
git add docs/RESEARCH_REPORT_FULL.md \
        docs/RESEARCH_REPORT_SCALPER.md \
        docs/TOP20_DCA_TRADES.csv \
        docs/TOP20_SCALPER_TRADES.csv
git commit -m "docs: reports $(date '+%Y-%m-%d %H:%M')" --allow-empty
git push https://baderbalubaid:${GITHUB_TOKEN}@github.com/baderbalubaid/Averion.git main

echo ""
echo "✅ Done! Download from GitHub:"
echo "DCA:     https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/RESEARCH_REPORT_FULL.md"
echo "Scalper: https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/RESEARCH_REPORT_SCALPER.md"
echo "DCA CSV: https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/TOP20_DCA_TRADES.csv"
echo "SC CSV:  https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/TOP20_SCALPER_TRADES.csv"
