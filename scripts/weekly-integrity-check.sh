#!/bin/bash
# Weekly link + citation integrity check for huffmanwrites.
#
# Why this exists. On 2026-09-19 an audit found five fabricated citations, eight
# quotations with no source locus, and two defects in the checking scripts
# themselves. Every one of them had been sitting in the corpus for months with
# nothing looking at it, because the pre-commit gates run only when content
# changes and the expensive checks (network sweeps, wording verification) were
# deliberately kept out of the deploy path. That is the right call for a build
# gate and the wrong one for content that is already published: citations rot,
# links die, and nothing notices.
#
# So this runs on a schedule instead of on a commit. Network access is fine here
# (nothing is waiting on it), the results go to a log, and anything actionable
# raises the shared failure alert.
#
# The gate list is NOT written out here. It lives in one file,
# `scripts/corpus-gates.sh`, because two copies of it drifted: this job ran four
# phases while the publishing tail ran nine more, and the gate that was missing
# was `check-quote-names.py --online` — the corpus-wide sweep of quoted name
# details, added to the publishing set on 2026-10-04 and never reaching the one
# job that looks at content nobody has touched in months. `scripts/test_gates.py`
# asserts that this job runs that shared list.
#
# Exit codes: 0 clean, 1 problems found, 2 the check could not run.
#
# Usage: weekly-integrity-check.sh [--quiet]
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
ALERT="$HERE/alert-failure.sh"

LOG="$HOME/Library/Logs/weekly-integrity.out.log"
ERR="$HOME/Library/Logs/weekly-integrity.err.log"
mkdir -p "$(dirname "$LOG")"

# Stamp each phase as it runs. A single STAMP captured at start stamped every
# phase header with the same second, so the log could not show which phase was
# slow — and here the phases differ by orders of magnitude (the offline link
# check is instant, the online sweep takes minutes and is the one that times out).
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
rc_total=0

# How much of a phase's output reaches the log.
#
# This is a diagnosis window, and getting it wrong is how a week of failures
# stayed invisible. `check-links.py` prints the DEAD block FIRST and its counts
# LAST, and the counts go to stderr — so in the merged capture the two things
# that matter sit at opposite ends and, depending on buffering, the summary can
# land anywhere. Keeping only `tail -40` therefore logged `--- links (online)
# exit 1` with neither the DEAD block nor the summary line: the record said a
# phase failed and threw away the reason. Measured 2026-09-28 on a run whose
# merged output was 140 lines with the verdict at line 1 and the counts at 138.
#
# So the rule is by outcome, not by position: a phase that FAILS logs its whole
# output (these are bounded, a couple hundred lines at most), and a phase that
# passes logs only its tail. `log_output` keeps that in one place for both
# helpers.
log_output() {
  local out="$1" rc="$2" tail_n="$3"
  if [ "$rc" -ne 0 ]; then
    printf '%s\n' "$out"
    return 0
  fi
  printf '%s\n' "$out" | tail -"$tail_n"
}

run() {
  local label="$1"; shift
  echo "=== $label ($(stamp)) ==="
  # Capture, do NOT pipe. `cmd | tail` makes $? the exit status of tail, so a
  # failing check would report success — the same shape of bug as the gate that
  # reported OK while blind. Run it, keep its status, then show the tail.
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  log_output "$out" "$rc" 40
  echo "--- $label exit $rc"
  [ "$rc" -ne 0 ] && rc_total=1
  return 0
}

# Report-only variant. For a check that is genuinely a heuristic: its output is
# for a human to read, and its exit code must not raise the failure alert, which
# is what `run` would do. The titles phase uses this — see its note below.
run_soft() {
  local label="$1"; shift
  echo "=== $label ($(stamp)) ==="
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  log_output "$out" "$rc" 80
  echo "--- $label exit $rc (informational; does not fail this job)"
  return 0
}

cd "$REPO" || { "$ALERT" "weekly-integrity" 2 "cannot cd to $REPO"; exit 2; }

# The corpus gates. The set, and the rationale for each entry, live in
# `scripts/corpus-gates.sh` — see the header there for why. Two of its entries
# are report-only heuristics (`run_soft`); the rest fail this job.
# shellcheck source=scripts/corpus-gates.sh
. "$HERE/corpus-gates.sh"
run_corpus_gates run run_soft


if [ "$rc_total" -ne 0 ]; then
  "$ALERT" "weekly-integrity" 1 "link, citation, credential, or vault-currency problems; see $LOG"
  echo "weekly-integrity: PROBLEMS FOUND"
else
  echo "weekly-integrity: clean"
fi

exit "$rc_total"
