#!/bin/bash
# Nord Stream watcher runner — invoked by launchd (com.huffmanwrites.nord-stream-watch).
#
# WHY THIS JOB EXISTS. "The Bet He Called a Fact" makes two promises to its
# reader: that a verdict in the Hamburg trial changes what the piece may say, and
# that a public reply from Jeffrey Sachs belongs in the record. Neither has a
# date. The trial's hearings run to February 2027 and Sachs answers his critics
# within days when he answers them at all. Nothing in this repo reads a site it
# does not publish to, so without this the piece would go stale in silence.
#
# A FINDING IS NOT A FAILURE, and the alert says so. The shared channel
# (scripts/alert-failure.sh) is used because a second notification path is how an
# alert gets missed — but the detail line opens with "FINDING (not a failure)",
# so a banner that means "read this, then decide" never reads as "the site
# broke". Exit 3 (a source could not be fetched) is a real failure and alerts
# without that prefix.
#
# END DATE, not a permanent fixture. The trial's scheduled hearings end in
# February 2027; a watcher that outlives its question logs a line a day forever,
# which is the scheduled no-op skill rule 4 warns about. Past 2027-04-30 it exits
# 0 with a line saying so, and the plist comes out when the piece is settled.
#
# NORD_STREAM_WATCH_DRY=1 runs the checker with no state write and prints what it
# would have alerted instead of raising a banner, so the alert path is provable
# without spending it.
set -euo pipefail

# launchd does not source the shell; export the full interactive PATH.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, and a hardcoded repo path names a missing file that
# turns the deploy red (2026-10-08).
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$REPO/scripts/nord-stream-watch.py"
LOG_DIR="${NORD_STREAM_WATCH_LOG_DIR:-$HOME/Library/Logs}"
ALERT="${NORD_STREAM_WATCH_ALERT:-$REPO/scripts/alert-failure.sh}"
STATE="${NORD_STREAM_WATCH_STATE:-$LOG_DIR/nord-stream-watch-state.json}"
OUT_LOG="$LOG_DIR/nord-stream-watch.out.log"
ERR_LOG="$LOG_DIR/nord-stream-watch.err.log"
mkdir -p "$LOG_DIR"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# The end-date guard: zero, with a reason, so it never trains the alert into
# noise. `date +%Y%m%d` is string-comparable at fixed width.
TODAY="$(date '+%Y%m%d')"
if [ "$TODAY" -gt "20270430" ]; then
  echo "$(stamp): past 2027-04-30, the trial's hearing calendar has run out; exiting without checking" >> "$OUT_LOG"
  exit 0
fi

ARGS=(--state "$STATE")
if [ "${NORD_STREAM_WATCH_DRY:-0}" = "1" ]; then
  ARGS+=(--dry-run)
fi
# A caller may pass --seed (record what is there, report nothing).
ARGS+=("$@")

echo "$(stamp): starting Nord Stream watch" >> "$OUT_LOG"

set +e
# `${ARGS[@]+"${ARGS[@]}"}` and not `"${ARGS[@]}"`: under `set -u`, bash 3.2 —
# macOS's /bin/bash, which launchd runs — treats an EMPTY array expansion as an
# unbound variable and aborts before the checker starts.
OUT="$(python3 "$CHECKER" ${ARGS[@]+"${ARGS[@]}"} 2>>"$ERR_LOG")"
RC=$?
set -e

printf '%s\n' "$OUT" >> "$OUT_LOG"
echo "$(stamp): finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  # The checker's first line is the summary; the rest are the findings.
  DETAIL="$(printf '%s\n' "$OUT" | tr '\n' ' ' | sed 's/  */ /g')"
  DETAIL="${DETAIL#nord-stream-watch: }"
  if [ "$RC" -eq 1 ]; then
    DETAIL="FINDING (not a failure) — $DETAIL"
  fi
  if [ "${NORD_STREAM_WATCH_DRY:-0}" = "1" ]; then
    echo "$(stamp): DRY RUN, would alert: $DETAIL" >> "$OUT_LOG"
  else
    "$ALERT" "nord-stream-watch" "$RC" "${DETAIL:-see $OUT_LOG}" || true
  fi
fi

exit "$RC"
