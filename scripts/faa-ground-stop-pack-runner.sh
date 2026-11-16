#!/bin/bash
# Ground-stop pack runner — invoked by launchd (com.huffmanwrites.faa-ground-stop-pack).
#
# WHY THIS JOB EXISTS. `future-pieces/faa-ground-stop-source-notes.md` is the
# record behind a piece on the nationwide ground stop of 13NOV26, and two of its
# facts rot on a clock that nobody was watching. The FAA advisory index keeps 15
# days, so the primary documents die around 29NOV26, before the piece window
# opens; and FlightAware's daily totals are only true once the day closes, so a
# snapshot taken on Friday night reads wrong forever. Philip, 15NOV26: "From now
# on, update the source pack daily until further notice."
#
# FACTS ONLY, NO MODEL. The collector reads two public pages and a capture API
# and writes down what they printed. There is no writer to gate, no allow-list,
# and therefore no Ollama probe: nothing here calls a model. The prose delta
# (§18 of the pack) stays a human or agent job, written by reading §19's log.
#
# NO GIT. The pack is a working file, not a publication. A commit here would
# trigger a Pages build every morning for a note no reader can see, so the job
# leaves the tree dirty and the next real commit carries it. `publish_preflight`
# logs a dirty tree as a NOTE and refuses only on SESSION_STATE.md, so this
# cannot block a publishing run.
#
# EXIT 3 means nothing at all was collected; the alert says so. EXIT 4 means a
# page was read and a required figure did not parse out of it — an empty index
# for a day already past, or a FlightAware page with no cancellation count —
# which is a selector break and invisible in the block itself. A single source
# failing writes `SOURCE UNAVAILABLE` into the entry and still exits 0, because
# an entry that names its gap is honest and a day with no entry is a silent one.
# Both 3 and 4 alert through the shared helper, which is the only path a failure
# may take in this repo.
set -euo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COLLECTOR="$REPO/scripts/faa-ground-stop-pack.py"
LOG_DIR="${GROUND_STOP_PACK_LOG_DIR:-$HOME/Library/Logs}"
ALERT="${GROUND_STOP_PACK_ALERT:-$REPO/scripts/alert-failure.sh}"
OUT_LOG="$LOG_DIR/faa-ground-stop-pack.out.log"
ERR_LOG="$LOG_DIR/faa-ground-stop-pack.err.log"
mkdir -p "$LOG_DIR"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

ARGS=()
if [ "${GROUND_STOP_PACK_DRY:-0}" = "1" ]; then
  ARGS+=(--dry-run)
fi
ARGS+=("$@")

echo "$(stamp): starting ground-stop pack pass" >> "$OUT_LOG"

set +e
OUT="$(python3 "$COLLECTOR" ${ARGS[@]+"${ARGS[@]}"} 2>>"$ERR_LOG")"
RC=$?
set -e

printf '%s\n' "$OUT" >> "$OUT_LOG"
echo "$(stamp): finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  DETAIL="$(printf '%s\n' "$OUT" | tr '\n' ' ' | sed 's/  */ /g')"
  DETAIL="${DETAIL#faa-ground-stop-pack: }"
  if [ "${GROUND_STOP_PACK_DRY:-0}" = "1" ]; then
    echo "$(stamp): DRY RUN, would alert: ${DETAIL:-see $OUT_LOG}" >> "$OUT_LOG"
  else
    "$ALERT" "faa-ground-stop-pack" "$RC" "${DETAIL:-see $OUT_LOG}" || true
  fi
fi

exit "$RC"
