#!/bin/bash
# Release the embargoed Veterans Day reflection at 1100Z on 11 November.
# Invoked by launchd (com.huffmanwrites.veterans-release) at 05:02 CT.
#
# Why a job of its own. The piece is dated 2026-11-11T05:00:00-06:00, which is
# 1100Z, and Hugo builds with `buildFuture: false`, so it appears only in a deploy
# that runs after that minute. 1100Z is the `0 11 * * *` fire, and a scheduled
# fire here lands about FOUR HOURS LATE when it runs at all (measured 2026-10-17);
# the next push after it is the SITREP at about 06:04 CT, which is 12:04Z. So the
# release gets a trigger that runs at the minute: this dispatches the Pages
# workflow and then requires the page to answer, the contract digest-release and
# sagan-release keep.
#
# It also mirrors the piece into SimpleBrain once the page answers, with
# `scripts/mirror-post.sh`. A piece published by hand never enters
# `publish_article`, which is the function that mirrors; without this the vault
# would owe the piece until the Monday vault-currency gate named it, which is
# exactly what happened to the Sagan reflection on 2026-11-09. The mirror runs
# last and its failure does not fail the release: the page is already live.
#
# ONE-OFF. launchd has no Year key, so `Month 11 / Day 11` fires every 11 November
# forever. DUE below is the only date this job releases; any other day exits 0
# with a log line, because a job that alerts every year about a piece it will
# never publish trains its reader to ignore the alert. After the 2026-11-11 run
# there is nothing left for it to do, so it is uninstalled then:
#   launchctl bootout gui/"$(id -u)"/com.huffmanwrites.veterans-release
#   rm ~/Library/LaunchAgents/com.huffmanwrites.veterans-release.plist
#
# Exit 0 when the date does not match, when the page already answers, and when
# the release verified. Exit non-zero only when a release was due and did not
# happen, which is the one condition a reader can act on.
set -uo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (gh,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB="veterans-release"
OUT_LOG="$HOME/Library/Logs/veterans-release.out.log"
ERR_LOG="$HOME/Library/Logs/veterans-release.err.log"
ARTICLE="content/posts/essays/the-eleventh-hour.md"
DUE="2026-11-11"
# The clock is injectable so a test can exercise the guard without waiting for a
# date, and so a smoke run can prove the release path on any afternoon.
TODAY="${VETERANS_RELEASE_TODAY:-$(date +%F)}"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }

mkdir -p "$(dirname "$OUT_LOG")"

cd "$REPO" || {
  echo "$(stamp): cannot cd to $REPO" >> "$OUT_LOG"
  exit 1
}

log "--- veterans-release start"

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
already_live=0
if python3 "$REPO/scripts/verify-published.py" --article "$ARTICLE" \
     --tries 1 --delay 0 >> "$OUT_LOG" 2>> "$ERR_LOG"; then
  log "the page already answers; nothing to dispatch"
  already_live=1
fi

if [ "$already_live" -eq 0 ]; then
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
  if [ "$RC" -ne 0 ]; then
    log "--- veterans-release done (exit $RC) — the page did not answer"
    "$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "see $OUT_LOG" || true
    exit "$RC"
  fi
fi

# The vault copy. Not part of the release's exit status: the page is live and
# correct either way, and mirror-post.sh alerts on its own failure.
bash "$REPO/scripts/mirror-post.sh" "$ARTICLE" >> "$OUT_LOG" 2>> "$ERR_LOG"
MIRROR_RC=$?
log "mirror-post exit $MIRROR_RC"

log "--- veterans-release done (exit 0)"
"$REPO/scripts/alert-failure.sh" "$JOB" 0 "see $OUT_LOG" || true
exit 0
