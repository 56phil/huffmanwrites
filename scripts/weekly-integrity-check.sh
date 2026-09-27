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
# Three phases:
#   1. Deterministic + online link sweep  (scripts/check-links.py)
#   2. Quotation wording verification     (scripts/check-quotes.py --online)
#   3. Credential drift + liveness        (scripts/check-secrets.py --online)
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

run() {
  local label="$1"; shift
  echo "=== $label ($(stamp)) ==="
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

# Report-only variant. For a check that is genuinely a heuristic: its output is
# for a human to read, and its exit code must not raise the failure alert, which
# is what `run` would do. The titles phase uses this — see its note below.
run_soft() {
  local label="$1"; shift
  echo "=== $label ($(stamp)) ==="
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  printf '%s\n' "$out" | tail -80
  echo "--- $label exit $rc (informational; does not fail this job)"
  return 0
}

cd "$REPO" || { "$ALERT" "weekly-integrity" 2 "cannot cd to $REPO"; exit 2; }

# Phase 1: links. --check first (offline, cheap, catches placeholders and any
# re-introduced blocklisted URL), then --online to find real rot. Only a 404/410
# or a slug-changing redirect fails: timeouts, resets and bot-blocks are
# reported but do not fail the job.
run "links (offline)" python3 scripts/check-links.py --check
run "links (online)"  python3 scripts/check-links.py --online --quiet

# Phase 1b: the same sweep WITH --titles, which is the only check in this repo
# that can catch a link resolving to the WRONG page — a URL that returns 200 and
# serves an unrelated article, CLAUDE.md's most dangerous failure class. The
# per-file publishing runners run it on the article they just wrote; this is the
# only place it covers the rest of the corpus, including content nobody has
# touched in months.
#
# Reported, NOT fatal. The comparison is a heuristic (it asks whether the link
# text shares vocabulary with the page's <title>), and a paraphrase or a page
# that names its subject differently reads as a mismatch: measured on a 200-URL
# sample, a Wikiquote author page cited for a book title and an Axios article
# cited by a quoted line both flagged while being correct. A gate that fails on a
# correct citation is worse than one that shows a human the sentence, so this
# phase prints for review and its exit code is ignored. Two noise sources were
# removed before wiring it in: anchors shorter than MIN_HEADLINE_WORDS are no
# longer compared, and a bot-wall's "Human Verification" title is no longer read
# as a title.
run_soft "links (titles)" python3 scripts/check-links.py --online --titles

# Phase 2: quotation wording. Fetches each epigraph's own author-linked URL and
# requires the quoted words to actually be there after whitespace normalisation.
# Catches a citation that was right when written and has since been rewritten —
# the failure mode a 200-only check cannot see.
run "quotes (online)" python3 scripts/check-quotes.py --online --quiet

# Phase 3: credentials. Two homes that disagree are reported offline; --online
# also asks fal.ai whether the resolved key authenticates, via a GET on a
# request id that cannot exist (a live key answers 404, a stale one 401). It
# submits no generation, so the weekly check costs nothing — and it is the only
# check here that would have caught the 2026-09-24 stale-key split, where the
# keychain and ~/.secrets agreed with each other and both were dead.
run "secrets (drift)"  python3 scripts/check-secrets.py --quiet
run "secrets (liveness)" python3 scripts/check-secrets.py --online --quiet

if [ "$rc_total" -ne 0 ]; then
  "$ALERT" "weekly-integrity" 1 "link, citation, or credential problems; see $LOG"
  echo "weekly-integrity: PROBLEMS FOUND"
else
  echo "weekly-integrity: clean"
fi

exit "$rc_total"
