#!/bin/bash
# SITREP watchdog runner — invoked by launchd (com.huffmanwrites.sitrep-watchdog).
#
# WHY THIS JOB EXISTS. Every other job in this repo alerts when it FAILS. The
# daily SITREP is the only one that publishes every day, and the failure that
# matters most for it is not a failure at all: a run that never happens. launchd
# writes no line for a job that did not fire, the shared alert is only reachable
# from inside a run, and the reader finds an empty morning. A machine that is off
# at 06:00 gets no catch-up, because StartCalendarInterval does not run a missed
# event at boot. Nothing else in the pipeline can see the absence. Philip asked
# for this watchdog on 2026-10-08, the day after the first edition shipped.
#
# Exit-code contract, mirroring docket-watch-runner.sh: a non-zero code from the
# checker routes to the shared alert, and the checker's own sentence is the
# alert's detail, so the banner says WHICH half is missing — no file anywhere, or
# a file with a 404 page, which need different fixes — rather than "something is
# wrong".
#
# `SITREP_WATCHDOG_DRY=1` runs the checker with the dedup state disabled and
# prints what it would have alerted instead of raising a banner. A watcher whose
# whole job is raising one banner a day must be provable without spending it.
set -euo pipefail

# launchd does not source the shell; export the full interactive PATH.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
CHECKER="$REPO/scripts/sitrep-watchdog.py"
# Both paths are overridable so the tests can exercise this runner end to end —
# the dedup, the alert routing, the empty-ARGS hazard — without posting a banner
# on the desktop or writing into the real log. `scripts/ollama-probe.sh` takes
# the same approach to its own alert for the same reason.
LOG_DIR="${SITREP_WATCHDOG_LOG_DIR:-$HOME/Library/Logs}"
ALERT="${SITREP_WATCHDOG_ALERT:-$REPO/scripts/alert-failure.sh}"
OUT_LOG="$LOG_DIR/sitrep-watchdog.out.log"
ERR_LOG="$LOG_DIR/sitrep-watchdog.err.log"
# Create it rather than assume it: under `set -e` a failed redirection kills the
# run before the checker starts, and for a watchdog that is the worst possible
# failure — the alert about a missing edition never gets raised. The real path
# always exists; the overridden one in a test does not.
mkdir -p "$LOG_DIR"
# Timestamp each event as it happens: this job runs several times a day, and
# "when did it actually look" is the whole point of a watch job's log.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

ARGS=()
if [ "${SITREP_WATCHDOG_DRY:-0}" = "1" ]; then
  # No state writes in a dry run: the checker's dedup would otherwise record an
  # alert that was never raised, and the day's real check would stay silent.
  ARGS+=(--no-state)
fi

echo "$(stamp): starting SITREP watchdog" >> "$OUT_LOG"

set +e
# `${ARGS[@]+"${ARGS[@]}"}` and not `"${ARGS[@]}"`: under `set -u`, bash 3.2 —
# macOS's /bin/bash, which is what launchd runs — treats the expansion of an
# EMPTY array as an unbound variable and aborts the script. This runner's very
# first load-time fire died that way, exiting 1 before the checker ran, which
# raised a banner for a job that had not started. The guard form is the portable
# one; `scripts/corpus-gates.sh` passes functions as arguments for the same
# version's sake.
OUT="$(python3 "$CHECKER" ${ARGS[@]+"${ARGS[@]}"} "$@" 2>>"$ERR_LOG")"
RC=$?
set -e

printf '%s\n' "$OUT" >> "$OUT_LOG"
echo "$(stamp): finished (exit $RC)" >> "$OUT_LOG"

# No-op on success. `|| true` keeps a failing alert from masking the real code.
if [ "$RC" -ne 0 ]; then
  DETAIL="$(printf '%s\n' "$OUT" | tail -n 1)"
  DETAIL="${DETAIL#sitrep-watchdog: }"
  if [ "${SITREP_WATCHDOG_DRY:-0}" = "1" ]; then
    echo "$(stamp): DRY RUN — would alert: $DETAIL" >> "$OUT_LOG"
  else
    "$ALERT" "sitrep-watchdog" "$RC" "${DETAIL:-see $OUT_LOG}" || true
  fi
fi

exit "$RC"
