#!/bin/bash
cd /home/averion/Averion
echo "Generating DCA report..."
python3 generate_research_report.py

echo "Generating Scalper report..."
python3 generate_scalper_report.py

echo "Generating Top 25 CSV reports..."
python3 generate_top25_csv.py

echo "Pushing to GitHub..."
git add docs/RESEARCH_REPORT_FULL.md docs/RESEARCH_REPORT_SCALPER.md docs/TOP25_DCA_TRADES.csv docs/TOP25_SCALPER_TRADES.csv
git commit -m "docs: regenerate research reports $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo "✅ Done! Download from:"
echo "DCA: https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/RESEARCH_REPORT_FULL.md"
echo "Scalper: https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/RESEARCH_REPORT_SCALPER.md"
