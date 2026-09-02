#!/bin/bash
# Weekly Senate Race Report runner.
# Invoked by launchd (com.huffmanwrites.senate-report) every Sunday at 07:00 CT.
# Self-disables after 2026-11-02 (Election Day: 2026-11-03).
set -euo pipefail

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/senate-race-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/senate-report.out.log"
ERR_LOG="$LOG_DIR/senate-report.err.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL,
# so the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_API_KEY="${OPENAI_API_KEY:-}"
export ANTHROPIC_MODEL="deepseek-v4-flash:cloud"

# Override for manual test runs: SENATE_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${SENATE_REPORT_PROMPT:-Read $SKILL and follow it exactly. Draft the Senate race article for this week.}"

# Guard: only run on or before 2026-11-02.
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" > "2026-11-02" ]]; then
  echo "$STAMP: past 2026-11-02, job complete, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

echo "$STAMP: starting Senate race report run" >> "$OUT_LOG"

set +e
claude -p "$PROMPT" \
  -n "senate-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(hugo --gc --minify)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$STAMP: run finished (exit $RC)" >> "$OUT_LOG"
exit "$RC"
