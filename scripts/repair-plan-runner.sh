#!/bin/bash
# Quarterly repair-plan revision runner.
# Invoked by launchd (com.huffmanwrites.repair-plan) on the first day of each
# quarter at 07:00 CT: January 1, April 1, July 1, October 1.
# Runs indefinitely; remove ~/Library/LaunchAgents/com.huffmanwrites.repair-plan.plist to retire.
#
# Why quarterly, and why this job exists at all (Philip, 2026-09-24):
# the repair plan is a live document whose value is entirely in its dated
# claims. Every one of them moves on a known clock — the UNFCCC revocation
# window closes 2027-02-27, UNESCO's withdrawal lands 2026-12-31, the four
# Schedule Policy/Career cases are pending, the emergency declarations renew
# each January 20, and the five bills it recommends are all still in committee.
# A plan recommending an act that has become impossible is worse than no plan.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo, pdftotext). Export the full interactive PATH.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/repair-plan-quarterly.md"
PLAN="$REPO/future-pieces/repair-plan-48th-president.md"
ALERT="$REPO/scripts/alert-failure.sh"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/repair-plan.out.log"
ERR_LOG="$LOG_DIR/repair-plan.err.log"
# Timestamp each event as it happens: a single STAMP captured at start stamped
# every line with the run's start time, hiding how long the research took.
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
# The model has a 1M context window; Claude Code assumes 200k for unrecognized
# model ids. Set the real window so the fact-check pass does not truncate.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: REPAIR_PLAN_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${REPAIR_PLAN_PROMPT:-Read $SKILL and follow it exactly. Run the quarterly revision pass on $PLAN.}"

cd "$REPO"

echo "$(stamp): starting repair-plan revision" >> "$OUT_LOG"

# Record the pre-run state so the log shows exactly what the pass touched, and
# so a run that changes nothing is distinguishable from a run that failed.
PRE_DIRTY="$(git -C "$REPO" status --porcelain -- "$PLAN" | wc -l | tr -d ' ')"
PRE_HASH="$(md5 -q "$PLAN" 2>/dev/null || echo unknown)"
echo "$(stamp): pre-run plan md5 $PRE_HASH; tree dirty for plan: $PRE_DIRTY" >> "$OUT_LOG"

set +e
claude -p "$PROMPT" \
  -n "repair-plan-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(curl *),Bash(pdftotext *),Bash(python3 scripts/*),Bash(md5 *),Bash(jq *),Bash(sed *),Bash(grep *),Bash(mkdir *),Bash(ls *),Bash(git -C /Users/prh/Developer/huffmanwrites status *),Bash(git -C /Users/prh/Developer/huffmanwrites diff *)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

POST_HASH="$(md5 -q "$PLAN" 2>/dev/null || echo unknown)"
echo "$(stamp): run finished (exit $RC); plan md5 $POST_HASH" >> "$OUT_LOG"

if [ "$PRE_HASH" = "$POST_HASH" ]; then
  echo "$(stamp): NOTE: plan is byte-identical to pre-run state; the pass changed nothing" >> "$OUT_LOG"
fi

# Gate the artifact, not the model's report about it. The agent has python3
# access to scripts/, but a model that believes it complied is not evidence
# that it did, and both of these are cheap.
if [ "$RC" -eq 0 ]; then
  echo "$(stamp): running gate checks" >> "$OUT_LOG"
  set +e
  /usr/bin/python3 "$REPO/scripts/check-emdashes.py" --file "$PLAN" >> "$OUT_LOG" 2>> "$ERR_LOG"
  EM_RC=$?
  /usr/bin/python3 "$REPO/scripts/check-links.py" --check >> "$OUT_LOG" 2>> "$ERR_LOG"
  LK_RC=$?
  set -e
  echo "$(stamp): gates: emdashes=$EM_RC links=$LK_RC" >> "$OUT_LOG"
  [ "$EM_RC" -ne 0 ] && [ "$RC" -eq 0 ] && RC="$EM_RC"
  [ "$LK_RC" -ne 0 ] && [ "$RC" -eq 0 ] && RC="$LK_RC"
fi

# Working-tree state is the deliverable. The skill deliberately does NOT commit
# or push: a quarterly pass that silently rewrote a governing plan into git
# history would be the opposite of reviewable. Report the diff so Philip can see
# what the pass did without opening the log.
if [ "$RC" -eq 0 ]; then
  echo "$(stamp): --- change summary (uncommitted, for review) ---" >> "$OUT_LOG"
  set +e
  git -C "$REPO" --no-pager diff --stat -- "$PLAN" >> "$OUT_LOG" 2>> "$ERR_LOG"
  echo "$(stamp): --- end change summary ---" >> "$OUT_LOG"
  set -e
fi

# Unattended job: a non-zero exit used to leave nothing but a log line.
# No-op on success. `|| true` keeps a missing/failing alert from replacing the
# job's real exit code under `set -e`.
"$ALERT" "repair-plan" "$RC" "see $OUT_LOG" || true

exit "$RC"
