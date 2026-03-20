#!/bin/bash
# Content Loop - Daily Review Script
# Analyzes recent content performance and updates knowledge base.
# Schedule: crontab -e → 0 7 * * * /path/to/content-loop/crons/daily-review.sh

set -e

# ── Configuration ──────────────────────────────────────────────
CONTENT_LOOP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$CONTENT_LOOP_DIR/data/daily-review.log"
REPORTS_DIR="$CONTENT_LOOP_DIR/data/reports"
DATE_TAG=$(date +%Y%m%d)
DAYS_TO_ANALYZE=3

cd "$CONTENT_LOOP_DIR"
export PYTHONPATH="$CONTENT_LOOP_DIR/autoresearch:$PYTHONPATH"
mkdir -p "$REPORTS_DIR"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"; }

log "Starting daily content review"

# ── Preflight checks ──────────────────────────────────────────
if [ ! -f "config.yaml" ]; then
    log "ERROR - config.yaml not found"
    exit 1
fi

if [ ! -f "data/run-log.jsonl" ] || [ ! -s "data/run-log.jsonl" ]; then
    log "No post data available — skipping analysis"
    exit 0
fi

PRODUCT=$(python3 -c "
import sys; sys.path.insert(0, 'autoresearch')
from config import Config
print(Config().product)
")
log "Active product: $PRODUCT"

# ── Step 1: Generate performance analysis ─────────────────────
log "Running ${DAYS_TO_ANALYZE}-day performance analysis..."
python3 autoresearch/analyze.py report $DAYS_TO_ANALYZE > "$REPORTS_DIR/daily-${DATE_TAG}.txt" 2>&1

if [ $? -eq 0 ]; then
    log "Analysis completed"
else
    log "ERROR - Analysis failed"
    exit 1
fi

# ── Step 2: Dry-run amendments ────────────────────────────────
log "Checking for knowledge amendments..."
AMENDMENT_OUTPUT=$(python3 autoresearch/amend.py dry-run 2>&1)
echo "$AMENDMENT_OUTPUT" > "data/amendment-preview-${DATE_TAG}.txt"

# ── Step 3: Auto-apply minor changes, flag major ones ─────────
if echo "$AMENDMENT_OUTPUT" | grep -q "Promoted\|Demoted\|Added new"; then
    log "Significant amendments detected — saved to data/pending-amendments-${DATE_TAG}.txt for human review"
    echo "$AMENDMENT_OUTPUT" > "data/pending-amendments-${DATE_TAG}.txt"
else
    log "Applying routine performance updates..."
    python3 autoresearch/amend.py apply >> "$LOG_FILE" 2>&1
fi

# ── Step 4: Generate human-readable summary ───────────────────
log "Generating daily summary..."
python3 -c "
from datetime import datetime

with open('$REPORTS_DIR/daily-${DATE_TAG}.txt') as f:
    report = f.read()

summary = f'''
DAILY CONTENT REVIEW — {datetime.now().strftime('%Y-%m-%d')}
Product: $PRODUCT

{report}

Next Actions:
- Review full report: data/reports/daily-${DATE_TAG}.txt
- Check knowledge updates: knowledge/$PRODUCT/
- Plan today's content based on learnings
'''
print(summary)
with open('data/daily-summary-${DATE_TAG}.txt', 'w') as f:
    f.write(summary)
"

# ── Step 5: Cleanup old files (keep 30 days) ──────────────────
find "$REPORTS_DIR" -name "daily-*.txt" -mtime +30 -delete 2>/dev/null || true
find data -name "amendment-preview-*.txt" -mtime +7 -delete 2>/dev/null || true
find data -name "daily-summary-*.txt" -mtime +30 -delete 2>/dev/null || true

# ── Step 6: Meta-learning health check (weekly on Mondays) ────
if [ "$(date +%u)" -eq 1 ]; then
    log "Running weekly skill health check..."
    python3 autoresearch/meta.py report --days 7 >> "$REPORTS_DIR/skill-health-${DATE_TAG}.txt" 2>&1
    log "Skill health report saved"
fi

log "Daily content review completed"
echo ""
echo "Summary saved: data/daily-summary-${DATE_TAG}.txt"
