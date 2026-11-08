#!/bin/bash
# Release the embargoed Carl Sagan birthday reflection at midnight CT.
# Invoked by launchd (com.huffmanwrites.sagan-release) on 9 November at 00:02 CT.
#
# Why a job of its own, when the workflow now carries a 06:00Z fire. The piece
# is dated 2026-11-09T00:00:00-06:00 and Hugo builds with `buildFuture: false`,
# so it appears only in a deploy that runs after that hour. Scheduled workflows
# on this repo land about FOUR HOURS LATE (measured 2026-10-17), which for a
# 06:00Z fire means a page asked for at midnight and served around 04:00. A
# midnight release is the request, so the release gets a trigger that runs at
# the minute: this one dispatches the Pages workflow and then requires the page
# to answer, the same contract com.huffmanwrites.digest-release keeps for the
# Saturday letter.
#
# ONE-OFF. launchd has no Year key, so `Month 11 / Day 9` fires every 9 November
# forever. DUE below is the only date this job releases; any other day exits 0
# with a log line, because a job that alerts every year about a piece it will
# never publish trains its reader to ignore the alert. After the 2026-11-09 run
# there is nothing left for it to do, so it is uninstalled then:
#   launchctl bootout gui/"$(id -u)"/com.huffmanwrites.sagan-release
#   rm ~/Library/LaunchAgents/com.huffmanwrites.sagan-release.plist
#
# Exit 0 when the date does not match, when the page already answers, and when
# the release verified. Exit non-zero only when a release was due and did not
# happen, which is the one condition a reader can act on.
set -uo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (gh,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB="sagan-release"
OUT_LOG="$HOME/Library/Logs/sagan-release.out.log"
ERR_LOG="$HOME/Library/Logs/sagan-release.err.log"
ARTICLE="content/posts/essays/the-candle-and-the-dark.md"
DUE="2026-11-09"
# The clock is injectable so a test can exercise the guard without waiting for
# a date, and so a smoke run can prove the release path on any afternoon.
TODAY="${SAGAN_RELEASE_TODAY:-$(date +%F)}"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }

mkdir -p "$(dirname "$OUT_LOG")"

cd "$REPO" || { log "cannot cd to $REPO"; exit 1; }

log "--- sagan-release start"

if [ "$TODAY" != "$DUE" ]; then
  log "not $DUE (clock says $TODAY); nothing to release"
  exit 0
fi

if [ ! -f "$ARTICLE" ]; then
  log "missing $ARTICLE, aborting"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "missing $ARTICLE; see $OUT_LOG" || true
  exit 1
fi

# gh carries the token in the login keychain, which a LaunchAgent reaches only
# inside a logged-in GUI session. Without this check a locked keychain surfaces
# as one opaque dispatch failure.
if ! command -v gh >/dev/null 2>&1; then
  log "gh not found on PATH, aborting"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "gh not found on PATH; see $OUT_LOG" || true
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  log "gh is not authenticated, aborting"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "gh not authenticated; see $ERR_LOG" || true
  exit 1
fi

# launchd runs a missed fire on wake, so a second run around a wake is normal.
if python3 "$REPO/scripts/verify-published.py" --article "$ARTICLE" \
     --tries 1 --delay 0 >> "$OUT_LOG" 2>> "$ERR_LOG"; then
  log "the page already answers; nothing to release"
  exit 0
fi

SHA="$(git rev-parse HEAD)"
bash "$REPO/scripts/republish-pages.sh" "$SHA" >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
if [ "$RC" -ne 0 ]; then
  log "dispatch failed (republish-pages exit $RC), not verifying"
  "$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "dispatch failed, exit $RC; see $OUT_LOG" || true
  exit "$RC"
fi
log "dispatched a Pages build for $SHA; verifying the page"

python3 "$REPO/scripts/verify-published.py" --article "$ARTICLE" >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?

log "--- sagan-release done (exit $RC)"
"$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "see $OUT_LOG" || true
exit "$RC"
