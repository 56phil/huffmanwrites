#!/bin/bash
# Weekly federal docket report runner.
# Invoked by launchd (com.huffmanwrites.docket-weekly-report) every Saturday at
# 0800 CT, first run Saturday 2026-10-03.
#
# Philip, 2026-09-25: "I want a weekly summary of these three dockets every
# Saturday beginning 3OCT26." The three are the ones check-docket.py already
# watches (Beatty v. Trump, Phang v. Blanche, and the consolidated D.C. Circuit
# appeal), and the summary is a DRAFT for review, not a published piece.
#
# This is the same shape as the Senate race report: a scheduled agent run that
# drafts a dated article and leaves it uncommitted, with the deterministic
# verification (builds and gates) done by THIS script rather than claimed by the
# agent. The agent cannot run the gates — they are not in its allow-list — so a
# gate result in its summary would be unverifiable. Running them here puts the
# real exit codes in the log where a reader can see them.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/docket-weekly-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/docket-weekly-report.out.log"
ERR_LOG="$LOG_DIR/docket-weekly-report.err.log"
# Timestamp each event as it happens. A single STAMP captured at start would
# stamp every line with the run's start time, which hides how long the run took
# and when verification actually ran.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL, so
# the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
# Policy (Philip, 2026-09-06): no Anthropic or OpenAI resources. The only AI API
# keys available are FAL and Ollama; Ollama may be local or cloud.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null)"
[ -z "$OLLAMA_KEY" ] && OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
# The model has a 1M context window; Claude Code assumes 200k for unrecognized
# model ids. Set the real window so a long draft is not auto-compact truncated
# mid-run. This also suppresses the long "auto-compact will use 200k" advisory;
# the remaining one-line [claude-code:unrecognized_model] note is telemetry, is
# emitted on every call, does not affect the exit code, and is not worth faking
# a background session to hide. See senate-report-runner.sh for the full note.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: DOCKET_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${DOCKET_REPORT_PROMPT:-Read $SKILL and follow it exactly. Draft the weekly docket report for this week.}"

# ---------------------------------------------------------------------------
# Start guard: first scheduled run is Saturday 2026-10-03.
#
# The job was installed on 2026-09-25 and the schedule fires every Saturday, so
# without this it would produce a report on Saturday 2026-09-26 — a week before
# the date Philip asked for. Exiting before that date is what makes "beginning
# 3OCT26" true rather than approximately true. Exit 0, not an error: the job is
# simply not due yet, and a non-zero code here would raise the failure alert
# every week until October, which is how a real alert gets learned as noise.
# ---------------------------------------------------------------------------
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" < "2026-10-03" ]]; then
  echo "$(stamp): before 2026-10-03, first report not due, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

echo "$(stamp): starting weekly docket report run" >> "$OUT_LOG"

set +e
# Bash(python3 scripts/check-docket.py*) is required, not optional: the skill's
# first step calls the script for the week's filings, and it is the single
# source of truth for what is watched. Without the grant the agent would fetch
# the docket pages by hand and could only reconstruct the filing list from
# memory or coverage — the fabrication path CLAUDE.md warns about.
# Bash(pdftotext *) is required for reading the filings it must read.
claude -p "$PROMPT" \
  -n "docket-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(pdftotext *),Bash(python3 scripts/check-docket.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): run finished (exit $RC)" >> "$OUT_LOG"

# Authoritative verification builds, run here rather than by the agent. TWO
# builds, and the second is the one that matters: the production build excludes
# draft:true content, so it says nothing about the draft this job just wrote. A
# draft with a broken shortcode logged "build OK" and would only fail when
# published. The drafts build renders it to a scratch destination so the check
# is real without leaving a draft page in public/, which is what deploys.
DRAFTS_DEST="$(mktemp -d "${TMPDIR:-/tmp}/hugo-drafts-XXXXXX")"
echo "$(stamp): running verification builds" >> "$OUT_LOG"
for flags in "--gc --minify" "--gc --minify --buildDrafts --destination $DRAFTS_DEST"; do
  set +e
  BUILD_OUT="$(hugo $flags 2>&1)"
  BUILD_RC=$?
  set -e
  if [ "$BUILD_RC" -ne 0 ]; then
    echo "$(stamp): build FAILED [$flags] (exit $BUILD_RC)" >> "$OUT_LOG"
    echo "$BUILD_OUT" >> "$ERR_LOG"
    [ "$RC" -eq 0 ] && RC=1
  else
    echo "$(stamp): build OK [$flags]" >> "$OUT_LOG"
  fi
done
rm -rf "$DRAFTS_DEST"

# Deterministic content gates, run here for the same reason the build is: a
# result the agent could not have produced must not be taken from the agent's
# summary. Offline only — the --online variants fetch the whole corpus and do
# not belong in a job that should finish in minutes (that is weekly-integrity's
# job). The two content gates the report can actually trip are the quotation
# gate (every quotation needs a link that contains its wording) and the
# preposition rule adopted the day before this job.
run_gate() {
  local label="$1"; shift
  set +e
  GATE_OUT="$(python3 "$@" 2>&1)"
  GATE_RC=$?
  set -e
  if [ "$GATE_RC" -ne 0 ]; then
    echo "$(stamp): gate FAILED [$label] (exit $GATE_RC)" >> "$OUT_LOG"
    echo "$GATE_OUT" >> "$ERR_LOG"
    [ "$RC" -eq 0 ] && RC=1
  else
    echo "$(stamp): gate OK [$label]" >> "$OUT_LOG"
  fi
}
run_gate "check-quotes"       "$REPO/scripts/check-quotes.py"
run_gate "check-links"        "$REPO/scripts/check-links.py" --check
run_gate "check-emdashes"     "$REPO/scripts/check-emdashes.py" --check
run_gate "check-prepositions" "$REPO/scripts/check-prepositions.py" --check

# Unattended job: a non-zero exit must not leave nothing but a log line. No-op
# on success. `|| true` keeps a missing/failing alert from replacing the job's
# real exit code.
"$REPO/scripts/alert-failure.sh" "docket-weekly-report" "$RC" "see $OUT_LOG" || true

exit "$RC"
