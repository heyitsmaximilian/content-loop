# Daily Analytics Review - Cron Job Specification

This cron job runs the daily analysis and amendment cycle that makes the content loop self-improving.

## Cron Schedule

```bash
# Run daily at 7:00 AM (adjust timezone as needed)
0 7 * * * /path/to/daily-review.sh
```

## Script: daily-review.sh

```bash
#!/bin/bash

# Content Loop - Daily Review Script
# Analyzes recent content performance and updates knowledge base

set -e  # Exit on any error

# Configuration
CONTENT_LOOP_DIR="/path/to/content-loop"
LOG_FILE="$CONTENT_LOOP_DIR/data/daily-review.log"
DAYS_TO_ANALYZE=3

# Change to content loop directory
cd "$CONTENT_LOOP_DIR"

# Log start time
echo "$(date): Starting daily content review" >> "$LOG_FILE"

# Step 1: Generate performance analysis
echo "$(date): Running 3-day performance analysis..." >> "$LOG_FILE"
python autoresearch/analyze.py report $DAYS_TO_ANALYZE > "data/reports/daily-$(date +%Y%m%d).md"

if [ $? -eq 0 ]; then
    echo "$(date): Analysis completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ERROR - Analysis failed" >> "$LOG_FILE"
    exit 1
fi

# Step 2: Check if amendments are needed
echo "$(date): Checking for knowledge amendments..." >> "$LOG_FILE"
python autoresearch/amend.py dry-run > "data/amendment-preview-$(date +%Y%m%d).txt"

# Step 3: Apply amendments if confidence is high
# Note: Only auto-apply if changes are minor. Major changes need human review.
AMENDMENT_OUTPUT=$(python autoresearch/amend.py dry-run 2>&1)

# Check if amendments are significant (more than just performance updates)
if echo "$AMENDMENT_OUTPUT" | grep -q "Promoted\|Demoted\|Added new"; then
    echo "$(date): Significant amendments detected - requiring human approval" >> "$LOG_FILE"
    # Send notification but don't auto-apply
    echo "$AMENDMENT_OUTPUT" > "data/pending-amendments-$(date +%Y%m%d).txt"
else
    echo "$(date): Applying routine performance updates..." >> "$LOG_FILE"
    python autoresearch/amend.py apply >> "$LOG_FILE" 2>&1
fi

# Step 4: Generate summary for human review
echo "$(date): Generating daily summary..." >> "$LOG_FILE"
python -c "
import json
from datetime import datetime

# Load latest analysis
with open('data/reports/daily-$(date +%Y%m%d).md', 'r') as f:
    report_content = f.read()

# Extract key metrics for summary
lines = report_content.split('\n')
total_posts = next((line for line in lines if 'Total posts:' in line), 'Unknown')
total_views = next((line for line in lines if 'Total views:' in line), 'Unknown') 
avg_views = next((line for line in lines if 'Average views:' in line), 'Unknown')

# Generate human-readable summary
summary = f'''
📊 DAILY CONTENT REVIEW - {datetime.now().strftime('%Y-%m-%d')}

{total_posts}
{total_views}  
{avg_views}

🏆 Top Performers: $(grep -A 5 'WINNERS:' data/reports/daily-$(date +%Y%m%d).md || echo 'None identified')

❌ Underperformers: $(grep -A 5 'LOSERS:' data/reports/daily-$(date +%Y%m%d).md || echo 'None identified')

💡 Key Recommendations:
$(grep -A 10 'RECOMMENDATIONS:' data/reports/daily-$(date +%Y%m%d).md || echo 'Continue current strategy')

📈 Next Actions:
- Review full report: data/reports/daily-$(date +%Y%m%d).md
- Check knowledge updates: knowledge/
- Plan today's content based on learnings

'''
print(summary)
" > "data/daily-summary-$(date +%Y%m%d).txt"

# Step 5: Cleanup old files (keep last 30 days)
echo "$(date): Cleaning up old reports..." >> "$LOG_FILE"
find data/reports -name "daily-*.md" -mtime +30 -delete 2>/dev/null || true
find data -name "amendment-preview-*.txt" -mtime +7 -delete 2>/dev/null || true
find data -name "daily-summary-*.txt" -mtime +30 -delete 2>/dev/null || true

# Step 6: Send notification (adapt based on your notification system)
if command -v openclaw >/dev/null 2>&1; then
    # If OpenClaw is available, send via message tool
    echo "$(date): Sending notification via OpenClaw..." >> "$LOG_FILE"
    cat "data/daily-summary-$(date +%Y%m%d).txt" | openclaw message send --channel telegram --target user
else
    # Fallback: just log that review is complete
    echo "$(date): Daily review complete - summary available at data/daily-summary-$(date +%Y%m%d).txt" >> "$LOG_FILE"
fi

echo "$(date): Daily content review completed successfully" >> "$LOG_FILE"
```

## Setup Instructions

1. **Make the script executable:**
   ```bash
   chmod +x daily-review.sh
   ```

2. **Test the script manually:**
   ```bash
   ./daily-review.sh
   ```

3. **Add to crontab:**
   ```bash
   crontab -e
   # Add this line (adjust path and time):
   0 7 * * * /path/to/content-loop/daily-review.sh
   ```

4. **Verify cron is running:**
   ```bash
   crontab -l
   ```

## Notification Integration

### With OpenClaw Messaging
If you're running OpenClaw, the script can send daily summaries via Telegram:

```bash
# In daily-review.sh, replace the notification section with:
cat "data/daily-summary-$(date +%Y%m%d).txt" | openclaw message send --target telegram
```

### With Email (Alternative)
```bash
# Add to daily-review.sh for email notifications:
if command -v mail >/dev/null 2>&1; then
    cat "data/daily-summary-$(date +%Y%m%d).txt" | mail -s "Daily Content Review" your@email.com
fi
```

### With Webhook (Alternative)
```bash
# Add to daily-review.sh for webhook notifications:
curl -X POST https://your-webhook-url.com/content-review \
     -H "Content-Type: application/json" \
     -d "$(cat data/daily-summary-$(date +%Y%m%d).txt | jq -R -s .)"
```

## Output Files

The daily review generates these files:

### `data/reports/daily-YYYYMMDD.md`
Full analysis report with:
- Performance metrics for last 3 days
- Hook performance rankings  
- Winner/loser identification
- Specific recommendations

### `data/daily-summary-YYYYMMDD.txt`
Human-readable summary with:
- Key metrics at a glance
- Top performers and underperformers
- Actionable next steps
- Links to detailed reports

### `data/amendment-preview-YYYYMMDD.txt`
Preview of knowledge changes:
- What would be promoted/demoted
- New patterns identified
- Confidence levels for changes

### `data/pending-amendments-YYYYMMDD.txt`
Significant changes requiring approval:
- Major hook reclassifications
- New high performers
- Controversial demotions

## Error Handling

### Common Issues

**Analysis fails - not enough data:**
```bash
if [ ! -s "data/run-log.jsonl" ]; then
    echo "$(date): No post data available - skipping analysis" >> "$LOG_FILE"
    exit 0
fi
```

**Knowledge files missing:**
```bash
for file in knowledge/hooks.md knowledge/images.md knowledge/ctas.md; do
    if [ ! -f "$file" ]; then
        echo "$(date): ERROR - Missing $file" >> "$LOG_FILE"
        exit 1
    fi
done
```

**Disk space issues:**
```bash
# Check available space before generating reports
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -lt 100000 ]; then  # Less than 100MB
    echo "$(date): WARNING - Low disk space" >> "$LOG_FILE"
    # Clean up old files more aggressively
    find data -mtime +7 -delete 2>/dev/null || true
fi
```

## Customization Options

### Adjust Analysis Period
```bash
# For more responsive learning (daily)
DAYS_TO_ANALYZE=1

# For more stable patterns (weekly)  
DAYS_TO_ANALYZE=7
```

### Change Auto-Amendment Threshold
```bash
# More conservative (manual approval for most changes)
AUTO_APPLY_THRESHOLD="performance_updates_only"

# More aggressive (auto-apply more changes)
AUTO_APPLY_THRESHOLD="minor_and_performance"
```

### Multiple Time Zones
```bash
# Run at different times for different regions
0 7 * * * /path/to/daily-review.sh  # US East
0 13 * * * /path/to/daily-review.sh # Europe  
0 20 * * * /path/to/daily-review.sh # Asia
```

## Monitoring the Cron Job

### Check if it's running:
```bash
# View cron log
grep CRON /var/log/syslog

# Check daily review log
tail -n 20 /path/to/content-loop/data/daily-review.log

# Verify reports are being generated
ls -la /path/to/content-loop/data/reports/
```

### Health Check Script:
```bash
#!/bin/bash
# check-daily-review.sh

EXPECTED_FILE="/path/to/content-loop/data/reports/daily-$(date +%Y%m%d).md"

if [ -f "$EXPECTED_FILE" ]; then
    echo "✅ Daily review ran successfully"
    echo "Latest summary:"
    cat "/path/to/content-loop/data/daily-summary-$(date +%Y%m%d).txt"
else
    echo "❌ Daily review failed or didn't run"
    echo "Check log: /path/to/content-loop/data/daily-review.log"
fi
```

---

*This cron job is the heartbeat of the content loop - it ensures your content gets smarter every single day.*