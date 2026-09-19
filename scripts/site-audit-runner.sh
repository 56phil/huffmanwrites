#!/bin/bash
# Weekly site audit runner.
# Invoked by launchd (com.huffmanwrites.site-audit) every Monday at 13:00 CT.
# Builds the site, crawls it for broken links, checks the CSP, verifies Hugo
# is current, and writes a report to ~/Library/Logs/site-audit-report.md.
set -euo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (hugo,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
CRAWLER="$REPO/scripts/site-audit-crawler.py"
GALLERY_GUARD="$REPO/scripts/check-gallery-pages.py"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/site-audit.out.log"
ERR_LOG="$LOG_DIR/site-audit.err.log"
REPORT="$LOG_DIR/site-audit-report.md"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

cd "$REPO"

echo "$STAMP: starting site audit" >> "$OUT_LOG"

# 0. Gallery pagination contract. The layout derives its page count from
#    data/gallery.yml, but Hugo only builds /gallery/page/N/ when the stub
#    content/gallery/page/N.md exists. Nothing else reconciles the two, so a
#    gallery item added past a page boundary silently produces a link to a
#    404. That is what happened on 2026-09-18 (commit 2fe605b, page 9).
#    This is a definite breakage, not a cosmetic report line, so it forces a
#    non-zero exit and therefore an alert. The crawl still runs so the report
#    stays complete.
set +e
GALLERY_OUT="$(python3 "$GALLERY_GUARD" 2>&1)"
GALLERY_RC=$?
set -e
if [ "$GALLERY_RC" -ne 0 ]; then
  echo "$STAMP: gallery pagination FAILED (exit $GALLERY_RC)" >> "$OUT_LOG"
  echo "$GALLERY_OUT" >> "$ERR_LOG"
else
  echo "$STAMP: gallery pagination OK" >> "$OUT_LOG"
fi

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

# Fold the gallery contract into the exit code. The crawler always returns 0
# (it reports broken links rather than failing on them), so without this the
# only way a missing page stub could surface was someone reading the report.
[ "$GALLERY_RC" -ne 0 ] && RC=1

echo "$STAMP: audit finished (exit $RC)" >> "$OUT_LOG"

# Unattended job: a non-zero exit used to leave nothing but a log line.
# No-op on success. `|| true` keeps a missing/failing alert from replacing the
# job's real exit code under `set -e`.
"$REPO/scripts/alert-failure.sh" "site-audit" "$RC" "see $OUT_LOG" || true

exit "$RC"
