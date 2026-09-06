#!/bin/bash
# Weekly site audit runner.
# Invoked by launchd (com.huffmanwrites.site-audit) every Sunday at 13:00 CT.
# Builds the site, crawls it for broken links, checks the CSP, verifies Hugo
# is current, and writes a report to ~/Library/Logs/site-audit-report.md.
set -euo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (hugo,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
CRAWLER="$REPO/scripts/site-audit-crawler.py"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/site-audit.out.log"
ERR_LOG="$LOG_DIR/site-audit.err.log"
REPORT="$LOG_DIR/site-audit-report.md"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

cd "$REPO"

echo "$STAMP: starting site audit" >> "$OUT_LOG"

# 1. Clean build. --cleanDestinationDir removes stale output (Hugo does not
#    clean public/ by default), so the crawl reflects exactly the current
#    content — no phantom pages from pre-draft builds. A build failure is
#    itself a finding — record it and still crawl whatever public/ contains
#    (stale output) so the report is complete.
set +e
BUILD_OUT="$(hugo --gc --minify --cleanDestinationDir 2>&1)"
BUILD_RC=$?
set -e
if [ "$BUILD_RC" -ne 0 ]; then
  echo "$STAMP: build FAILED (exit $BUILD_RC)" >> "$OUT_LOG"
  echo "$BUILD_OUT" >> "$ERR_LOG"
  BUILD_STATUS="FAILED (exit $BUILD_RC)"
else
  echo "$STAMP: build OK" >> "$OUT_LOG"
  BUILD_STATUS="PASS"
fi

# 2. Crawl and report.
set +e
AUDIT_BUILD_STATUS="$BUILD_STATUS" python3 "$CRAWLER" "$REPO/public" "$REPORT" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$STAMP: audit finished (exit $RC)" >> "$OUT_LOG"
exit "$RC"
