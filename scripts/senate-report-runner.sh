#!/bin/bash
# Weekly Senate Race Report runner.
# Invoked by launchd (com.huffmanwrites.senate-report) every Sunday at 07:00 CT.
# Self-disables after 2026-11-02 (Election Day: 2026-11-03).
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/senate-race-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/senate-report.out.log"
ERR_LOG="$LOG_DIR/senate-report.err.log"
# Timestamp each event as it happens. A single STAMP captured at start stamped
# every line with the run's start time, so the log could not show how long a run
# took or when verification actually ran: the 2026-09-20 run logged "build OK"
# at 07:00:05 while the draft being verified was written at 07:08:36.
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
# unrecognized model ids. Set the real window so long drafts are not
# auto-compact truncated mid-run.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: SENATE_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${SENATE_REPORT_PROMPT:-Read $SKILL and follow it exactly. Draft the Senate race article for this week.}"

# Guard: only run on or before 2026-11-02.
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" > "2026-11-02" ]]; then
  echo "$(stamp): past 2026-11-02, job complete, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

echo "$(stamp): starting Senate race report run" >> "$OUT_LOG"

set +e
# Bash(python3 *) is required, not optional: the skill's own steps call
# scripts/fetch-senate-ratings.py for the standing ratings table and for
# --sources. Without the grant the agent can only reconstruct that table from
# secondary sources, which is exactly the fabrication path CLAUDE.md warns
# about (the table is supposed to come from the script, because cookpolitical,
# centerforpolitics and realclearpolitics all 403 automated fetch). It was
# omitted here and worked only because this machine's untracked
# .claude/settings.local.json happens to allow `Bash(python3 -c ' *)` — a
# machine-local grant an unattended run must not depend on.
claude -p "$PROMPT" \
  -n "senate-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/fetch-senate-ratings.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): run finished (exit $RC)" >> "$OUT_LOG"

# Authoritative verification builds, run here rather than by the agent.
# Historically the agent was granted Bash(hugo --gc --minify) as an exact-match
# rule, but any variant it naturally reached for — a redirect, a "&&" compound,
# or a different flag set — was denied by the permission layer, so the Sept 13
# run reported "three attempts were gated" and left the build unrun. Running it
# in the script makes the check deterministic and puts the exit code in the log.
#
# TWO builds, and the second is the one that matters here. The production build
# excludes draft:true content, so it says nothing about the draft this job just
# wrote — a draft with a broken shortcode logged "build OK" and would only fail
# when published. The drafts build renders it to a scratch destination so the
# check is real without leaving a draft page in public/, which is what deploys
# (site-audit builds public/ with --cleanDestinationDir, and a stray draft page
# there would be crawled as if live).
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

# Deterministic content gates, run here for the same reason the build is: the
# run summary for 2026-09-20 claimed "check-quotes.py and check-links.py
# --check both pass" when neither script appears in the agent's allow-list, so
# the claim was unverifiable from the log. Running them in the script puts the
# real result where a reader can see it. Offline only -- the --online variants
# fetch the whole corpus and do not belong in a job that should finish in
# minutes (that is weekly-integrity's job).
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
run_gate "check-quotes"  "$REPO/scripts/check-quotes.py"
run_gate "check-links"   "$REPO/scripts/check-links.py" --check

# Unattended job: a non-zero exit used to leave nothing but a log line. On
# 2026-09-06 this job exited 127 then 1 and nobody saw it. No-op on success.
# `|| true` keeps a missing/failing alert from replacing the job's real exit code.
"$REPO/scripts/alert-failure.sh" "senate-report" "$RC" "see $OUT_LOG" || true

exit "$RC"
