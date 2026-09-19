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
# Two phases:
#   1. Deterministic + online link sweep  (scripts/check-links.py)
#   2. Quotation wording verification     (scripts/check-quotes.py --online)
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

STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"
rc_total=0

run() {
  local label="$1"; shift
  echo "=== $label ($STAMP) ==="
  # Capture, do NOT pipe. `cmd | tail` makes $? the exit status of tail, so a
  # failing check would report success — the same shape of bug as the gate that
  # reported OK while blind. Run it, keep its status, then show the tail.
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  printf '%s\n' "$out" | tail -40
  echo "--- $label exit $rc"
  [ "$rc" -ne 0 ] && rc_total=1
  return 0
}

cd "$REPO" || { "$ALERT" "weekly-integrity" 2 "cannot cd to $REPO"; exit 2; }

# Phase 1: links. --check first (offline, cheap, catches placeholders and any
# re-introduced blocklisted URL), then --online to find real rot. Only a 404/410
# or a slug-changing redirect fails: timeouts, resets and bot-blocks are
# reported but do not fail the job.
run "links (offline)" python3 scripts/check-links.py --check
run "links (online)"  python3 scripts/check-links.py --online --quiet

# Phase 2: quotation wording. Fetches each epigraph's own author-linked URL and
# requires the quoted words to actually be there after whitespace normalisation.
# Catches a citation that was right when written and has since been rewritten —
# the failure mode a 200-only check cannot see.
run "quotes (online)" python3 scripts/check-quotes.py --online --quiet

if [ "$rc_total" -ne 0 ]; then
  "$ALERT" "weekly-integrity" 1 "link or citation problems; see $LOG"
  echo "weekly-integrity: PROBLEMS FOUND"
else
  echo "weekly-integrity: clean"
fi

exit "$rc_total"
