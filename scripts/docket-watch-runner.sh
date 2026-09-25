#!/bin/bash
# Federal docket watch runner.
# Invoked by launchd (com.huffmanwrites.docket-watch) twice daily.
#
# Philip, 2026-09-19: "I must keep an eye on this story." (Kennedy Center.)
# Philip, 2026-09-24: "I want to start following the docket ... regarding the
# Epstein files." Both dockets — Beatty v. Trump (No. 1:25-cv-04480) and
# Phang v. Blanche (No. 1:26-cv-01417) — move in day-scale bursts and the
# coverage of each is unreliable, so watch the dockets directly, not the news.
# The checker owns the case registry; this runner stays case-agnostic.
#
# Runs twice a day because filings cluster in the late afternoon and early
# evening (ECF 89 landed at 8:55 p.m.), and because a docket check that misses
# the 6 a.m. CT send window should still run again before the day is out.
#
# Exit-code contract, mirroring the other runners: any non-zero code from the
# checker routes to the shared alert. This matters more here than elsewhere —
# for a watch job, "I could not reach the docket" must never be indistinguishable
# from "nothing was filed."
set -euo pipefail

# launchd does not source the shell; export the full interactive PATH.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
CHECKER="$REPO/scripts/check-docket.py"
ALERT="$REPO/scripts/alert-failure.sh"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/docket-watch.out.log"
ERR_LOG="$LOG_DIR/docket-watch.err.log"
# Timestamp each event as it happens, not once at start: a single STAMP stamped
# every line with the run's start time, which hid how long a check took. For a
# watch job that runs twice daily, "when did this actually look" is the whole
# point of the log.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

echo "$(stamp): starting docket check" >> "$OUT_LOG"

set +e
/usr/bin/python3 "$CHECKER" >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): finished (exit $RC)" >> "$OUT_LOG"

# No-op on success. `|| true` keeps a failing alert from masking the real code.
"$ALERT" "docket-watch" "$RC" "see $OUT_LOG" || true

exit "$RC"
