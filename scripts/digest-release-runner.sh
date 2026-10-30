#!/bin/bash
# Release the embargoed Stoic Saturday page.
# Invoked by launchd (com.huffmanwrites.digest-release) every Saturday at 06:05 CT.
#
# Why a job of its own. The letter's page is dated to its send hour and Hugo
# builds with `buildFuture: false`, so it is published by whatever deploy runs
# after that hour. Until 2026-10-31 that deploy was the daily SITREP's push,
# which made the newsletter's URL depend on a different article's job: a SITREP
# abort left the letter 404 while its campaign was already scheduled. This job
# dispatches the Pages workflow itself and then requires the page to answer.
#
# Deliberately not a cron in .github/workflows/hugo.yml: scheduled workflows on
# this repo land about four hours late (measured 2026-10-17, when the 11:00Z
# fire did not run at all), so a cron cannot serve a 06:15 send.
#
# Nothing to release is success, not failure: the letter is weekly and its page
# may not exist for a given date. Exiting non-zero there would alert every
# Saturday about a condition the reader cannot act on.
set -uo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (gh,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB="digest-release"
OUT_LOG="$HOME/Library/Logs/digest-release.out.log"
ERR_LOG="$HOME/Library/Logs/digest-release.err.log"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }

mkdir -p "$(dirname "$OUT_LOG")"

cd "$REPO" || { log "cannot cd to $REPO"; "$REPO/scripts/alert-failure.sh" "$JOB" 1 "cannot cd to $REPO"; exit 1; }

log "--- digest-release start"

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

set +e
python3 "$REPO/scripts/digest-release.py" "$@" >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

log "--- digest-release done (exit $RC)"

# Unattended job: a non-zero exit leaves more than a log line. No-op on success.
"$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "see $OUT_LOG" || true

exit "$RC"
