#!/bin/bash
# Weekly SimpleBrain wiki check & fix runner.
# Invoked by launchd (com.huffmanwrites.wiki-check) every Monday at 13:30 CT.
# Runs the wiki-check-and-fix audit prompt against the SimpleBrain repo.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude).
# Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

SB="/Users/prh/Developer/SimpleBrain"
PROMPT_FILE="$SB/prompts/wiki-check-and-fix.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/wiki-check.out.log"
ERR_LOG="$LOG_DIR/wiki-check.err.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL,
# so the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
# Policy (Philip, 2026-09-06): no Anthropic or OpenAI resources. The only AI
# API keys available are FAL and Ollama; Ollama may be local or cloud. Auth
# uses OLLAMA_API_KEY from the login keychain (huffmanwrites-ollama), with
# ~/.secrets as fallback. Without it, ANTHROPIC_API_KEY is empty and claude
# falls back to the OAuth login.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null)"
[ -z "$OLLAMA_KEY" ] && OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4-flash:cloud"

# Override for manual test runs: WIKI_CHECK_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${WIKI_CHECK_PROMPT:-Read $PROMPT_FILE and follow it exactly. Run the wiki check and fix pass on the SimpleBrain repo at $SB.}"

cd "$SB"

echo "$STAMP: starting wiki check & fix run" >> "$OUT_LOG"

set +e
claude -p "$PROMPT" \
  -n "wiki-check-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,Bash(git -C /Users/prh/Developer/SimpleBrain *),Bash(md5 *),Bash(cmp *),Bash(diff *),Bash(mv *),Bash(rm *),Bash(mkdir *)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$STAMP: run finished (exit $RC)" >> "$OUT_LOG"
exit "$RC"
