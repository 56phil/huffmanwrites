#!/bin/bash
# Release the conclusion of the ground-stop series at 1600Z on 1 December 2026.
# Invoked by launchd (com.huffmanwrites.ground-stop-conclusion-release) at
# 10:00 CT, which is 1600Z in standard time.
#
# WHY A JOB OF ITS OWN. The piece is dated 2026-12-01T10:00:00-06:00 = 1600Z, and
# Hugo builds with `buildFuture: false`, so it appears only in a deploy that runs
# after that minute. No cron in `.github/workflows/hugo.yml` covers 16:00Z — the
# nearest are `0 13 * * *` and `0 5/6 * * *` — and a scheduled fire lands about
# four hours late when it runs at all (measured 2026-10-17). So the release gets a
# trigger that runs at the minute: dispatch the Pages workflow, then require the
# page to answer. Same contract as digest-release, sagan-release and
# veterans-release.
#
# It also mirrors the piece into SimpleBrain once the page answers, through
# `scripts/mirror-post.sh`. A piece published this way never enters
# `publish_article`, which is where the vault mirror lives, and the Sagan
# reflection went unmirrored for two days because of exactly that.
#
# ONE-OFF, so launchd has no Year key and `Month 12 / Day 1` fires every 1
# December forever. DUE is the only date this job releases; any other day exits 0
# with a log line, because a job that alerts every December about a piece it will
# never publish trains its reader to ignore the alert. After the 2026-12-01 run
# there is nothing left for it to do:
#   launchctl bootout gui/"$(id -u)"/com.huffmanwrites.ground-stop-conclusion-release
#   rm ~/Library/LaunchAgents/com.huffmanwrites.ground-stop-conclusion-release.plist
# then update the table in CLAUDE.md. The repo copy and the skill stay as the
# record, as the Senate and Sagan runners did.
#
# THE PREREQUISITE IS THE PIECE. A release job that fires on a date with no
# article publishes nothing and says nothing, which is why every check below
# aborts loudly instead: the file must exist, carry `draft: false`, be the copy
# that is committed and clean in git, and the page must answer afterwards.
#
# Exit 0 when the date does not match, when the page already answers, and when
# the release verified. Exit 3 when the piece is not ready to release — missing,
# a draft, or not the committed copy — which is a condition Philip can act on.
# Exit non-zero from the dispatch or the verification when the release failed.
set -uo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (gh,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB="ground-stop-conclusion-release"
OUT_LOG="$HOME/Library/Logs/ground-stop-conclusion-release.out.log"
ERR_LOG="$HOME/Library/Logs/ground-stop-conclusion-release.err.log"

# The contract. When the piece is drafted, either name the file this or set the
# variable in the plist; the guard names whichever path it looked for.
ARTICLE="${GROUND_STOP_CONCLUSION_ARTICLE:-content/posts/essays/ground-stop-conclusion.md}"
DUE="2026-12-01"
# The clock is injectable so a test can exercise the guards without waiting for a
# date, and so a smoke run can prove the release path on any afternoon.
TODAY="${GROUND_STOP_CONCLUSION_TODAY:-$(date +%F)}"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }
alert() { "$REPO/scripts/alert-failure.sh" "$JOB" "$1" "$2" || true; }

mkdir -p "$(dirname "$OUT_LOG")"

cd "$REPO" || {
  echo "$(stamp): cannot cd to $REPO" >> "$OUT_LOG"
  exit 1
}

log "--- $JOB start"

if [ "$TODAY" != "$DUE" ]; then
  log "not $DUE (clock says $TODAY); nothing to release"
  exit 0
fi

if [ ! -f "$ARTICLE" ]; then
  log "missing $ARTICLE, aborting"
  alert 3 "missing $ARTICLE on the release day; see $OUT_LOG"
  exit 3
fi

if ! grep -q '^draft: false' "$ARTICLE"; then
  log "$ARTICLE is not draft: false, aborting"
  alert 3 "$ARTICLE still carries draft: true on the release day; see $OUT_LOG"
  exit 3
fi

# The published page must be the committed copy. Releasing a working file would
# publish whatever the tree happened to hold at 10:00, and the deploy builds the
# push, not the disk — so an uncommitted edit is a page that will not be there.
if ! git ls-files --error-unmatch "$ARTICLE" >/dev/null 2>&1; then
  log "$ARTICLE is not tracked by git, aborting"
  alert 3 "$ARTICLE is untracked; commit it before the release"
  exit 3
fi
if [ -n "$(git status --porcelain -- "$ARTICLE")" ]; then
  log "$ARTICLE has uncommitted changes, aborting"
  alert 3 "$ARTICLE is modified but not committed; the deploy would not carry it"
  exit 3
fi

# gh carries the token in the login keychain, which a LaunchAgent reaches only
# inside a logged-in GUI session. Without this check a locked keychain surfaces
# as one opaque dispatch failure.
if ! command -v gh >/dev/null 2>&1; then
  log "gh not found on PATH, aborting"
  alert 1 "gh not found on PATH; see $OUT_LOG"
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  log "gh is not authenticated, aborting"
  alert 1 "gh not authenticated; see $ERR_LOG"
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
    alert "$RC" "dispatch failed, exit $RC; see $OUT_LOG"
    exit "$RC"
  fi
  log "dispatched a Pages build for $SHA; verifying the page"

  python3 "$REPO/scripts/verify-published.py" --article "$ARTICLE" >> "$OUT_LOG" 2>> "$ERR_LOG"
  RC=$?
  if [ "$RC" -ne 0 ]; then
    log "--- $JOB done (exit $RC) — the page did not answer"
    alert "$RC" "the page did not answer after the dispatch; see $OUT_LOG"
    exit "$RC"
  fi
fi

# The vault copy. Not part of the release's exit status: the page is live and
# correct either way, and mirror-post.sh alerts on its own failure.
bash "$REPO/scripts/mirror-post.sh" "$ARTICLE" >> "$OUT_LOG" 2>> "$ERR_LOG"
MIRROR_RC=$?
log "mirror-post exit $MIRROR_RC"

log "--- $JOB done (exit 0)"
exit 0
