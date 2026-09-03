#!/bin/bash
# Monthly Ninety-Days Report runner (bond market + S&P 500).
# Invoked by launchd (com.huffmanwrites.ninety-days-report) on the 1st of every month at 07:00 CT.
# Runs indefinitely; remove ~/Library/LaunchAgents/com.huffmanwrites.ninety-days-report.plist to retire.
set -euo pipefail

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/ninety-days-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/ninety-days-report.out.log"
ERR_LOG="$LOG_DIR/ninety-days-report.err.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL,
# so the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_API_KEY="${OPENAI_API_KEY:-}"
export ANTHROPIC_MODEL="deepseek-v4-flash:cloud"

# Image generation: hero pairs call the real OpenAI API. Extract the key from
# .zshrc (launchd does not source it) and make sure OPENAI_BASE_URL is NOT set,
# because the shell default points at the local Ollama proxy, which serves no
# images API. api.openai.com is the default when the variable is absent.
OPENAI_KEY="$(grep -oE 'OPENAI_API_KEY="[^"]+"' "$HOME/.zshrc" | head -1 | cut -d'"' -f2)"
export OPENAI_API_KEY="${OPENAI_KEY:-}"
unset OPENAI_BASE_URL || true

# Override for manual test runs: NINETY_DAYS_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${NINETY_DAYS_PROMPT:-Read $SKILL and follow it exactly. Draft both ninety-days articles for this month.}"

cd "$REPO"

echo "$STAMP: starting ninety-days report run" >> "$OUT_LOG"

set +e
claude -p "$PROMPT" \
  -n "ninety-days-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(hugo --gc --minify --buildDrafts),Bash(curl *),Bash(magick *),Bash(cwebp *),Bash(jq *),Bash(base64 *),Bash(cp *),Bash(sed *)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$STAMP: run finished (exit $RC)" >> "$OUT_LOG"
exit "$RC"