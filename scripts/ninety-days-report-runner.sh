#!/bin/bash
# Monthly Ninety-Days Report runner (bond market + S&P 500).
# Invoked by launchd (com.huffmanwrites.ninety-days-report) on the 1st of every month at 07:00 CT.
# Runs indefinitely; remove ~/Library/LaunchAgents/com.huffmanwrites.ninety-days-report.plist to retire.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/ninety-days-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/ninety-days-report.out.log"
ERR_LOG="$LOG_DIR/ninety-days-report.err.log"
# Timestamp each event as it happens: a single STAMP captured at start stamped
# every line with the run's start time, so the log could not show how long the
# two drafts, the hero generations, or the builds took.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

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
# The model has a 1M context window; Claude Code assumes 200k for
# unrecognized model ids. Set the real window so the two drafts are not
# auto-compact truncated mid-run.
#
# This var also suppresses the long half of the "unrecognized model" advisory
# (measured 2026-09-20: set -> 109 bytes of stderr, warning absent; unset -> 591
# bytes, warning present). What remains is one benign telemetry line per API
# call. It does not affect the exit code and cannot raise the failure alert, so
# it is left alone on purpose. See the long note in senate-report-runner.sh for
# the three things that DO silence it and why none is worth doing (one fakes a
# background session; one makes the transcript misattribute the model).
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Image generation: hero pairs call fal.ai (FLUX.1 dev). FAL_KEY from the
# login keychain (huffmanwrites-fal), with ~/.secrets as fallback. The queue
# endpoint is https://queue.fal.run/fal-ai/flux/dev with Authorization: Key $FAL_KEY.
FAL_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-fal -w 2>/dev/null)"
[ -z "$FAL_KEY" ] && FAL_KEY="$(grep -oE 'FAL_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export FAL_KEY="${FAL_KEY:-}"

# Override for manual test runs: NINETY_DAYS_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${NINETY_DAYS_PROMPT:-Read $SKILL and follow it exactly. Draft both ninety-days articles for this month.}"

cd "$REPO"

echo "$(stamp): starting ninety-days report run" >> "$OUT_LOG"

set +e
claude -p "$PROMPT" \
  -n "ninety-days-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(curl *),Bash(magick *),Bash(cwebp *),Bash(jq *),Bash(base64 *),Bash(cp *),Bash(sed *)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): run finished (exit $RC)" >> "$OUT_LOG"

# Authoritative verification builds, run here rather than by the agent.
# The agent's allow-list intentionally omits hugo: an exact-match rule denied
# the redirect and "&&" compound forms the agent naturally reached for, which
# is how the Sept 13 Senate run ended with the build never executed. Two
# checks: the production build (what actually deploys) and the draft-inclusive
# build (proves today's draft:true installments render).
echo "$(stamp): running verification builds" >> "$OUT_LOG"
# The drafts build renders to a scratch destination, not public/. public/ is
# what deploys, and site-audit builds it with --cleanDestinationDir and then
# crawls it — a draft page left there would be crawled as if it were live.
DRAFTS_DEST="$(mktemp -d "${TMPDIR:-/tmp}/hugo-drafts-XXXXXX")"
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

# Unattended job: a non-zero exit used to leave nothing but a log line.
# No-op on success. `|| true` keeps a missing/failing alert from replacing the
# job's real exit code under `set -e`.
"$REPO/scripts/alert-failure.sh" "ninety-days-report" "$RC" "see $OUT_LOG" || true

exit "$RC"