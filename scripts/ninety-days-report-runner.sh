#!/bin/bash
# Monthly Ninety-Days Report runner (bond market + S&P 500).
# Invoked by launchd (com.huffmanwrites.ninety-days-report) on the 1st of every month at 07:00 CT.
# Runs indefinitely; remove ~/Library/LaunchAgents/com.huffmanwrites.ninety-days-report.plist to retire.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded "/Users/<who>/Developer/<repo>" names a
# missing file, python3 exits 2, and the Pages deploy goes red (2026-10-08). A
# test in scripts/test_gates.py holds the rule for every script under scripts/.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
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

# The shared publish library, sourced for its reusable pieces — the two-build
# verifier and the gate runner — even though this job does not publish (it
# drafts). Sourcing it also defines JOB for the alert below and keeps one
# definition of `run_gate` across all four report jobs.
JOB="ninety-days-report"
. "$REPO/scripts/publish-report.sh"

# Reachability guard: fail loudly and early if the local Ollama server is down.
# See scripts/ollama-probe.sh.
. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

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
# Two builds, run through the shared library so all four report jobs verify
# identically. The drafts build renders to a scratch destination, not public/:
# public/ is what deploys, and site-audit builds it with --cleanDestinationDir
# and then crawls it — a draft page left there would be crawled as if live. A
# build failure sets RC, which the alert at the bottom reports.
report_build ""
if [ "$BUILD_FAILED" -ne 0 ] && [ "$RC" -eq 0 ]; then RC=1; fi

# Deterministic content gates. Both articles cite market data, and until
# 2026-09-27 this runner ran no link check at all — not even the offline one —
# so a fabricated or placeholder URL in either piece would have sat unnoticed
# until a human read the file. The offline link check is instant; --online is
# deliberately not run here, because these are drafts a person reviews before
# publishing and the corpus-wide network sweep belongs to weekly-integrity.
#
# This job DRAFTS, so it does not call run_report_gates(): that set includes
# check-report-frontmatter, whose `draft: false` rule does not apply to files
# that are intentionally still drafts. But the corpus-wide gates that ARE
# relevant to a drafting job were missing here through 2026-10-01 — the run that
# added two gallery cards across a page boundary left no page stub, and
# `check-gallery-pages` was not in this list, so a deploy 404 was invisible to
# the job that caused it. They are added now.
#
# The four prose/link gates run corpus-wide (--check) because these drafts have
# no baseline entry yet; the rest are the same scripts the publishing jobs run.
run_gate "check-links"        "$REPO/scripts/check-links.py" --check
run_gate "check-quotes"       "$REPO/scripts/check-quotes.py"
run_gate "check-emdashes"     "$REPO/scripts/check-emdashes.py" --check
run_gate "check-prepositions" "$REPO/scripts/check-prepositions.py" --check
run_gate "check-hero-paths"   "$REPO/scripts/check-hero-paths.py"
run_gate "check-gallery-pages" "$REPO/scripts/check-gallery-pages.py"
run_gate "check-render-integrity" "$REPO/scripts/check-render-integrity.py"
[ "$GATE_FAILED" -ne 0 ] && [ "$RC" -eq 0 ] && RC=1

# Unattended job: a non-zero exit used to leave nothing but a log line.
# No-op on success. `|| true` keeps a missing/failing alert from replacing the
# job's real exit code under `set -e`.
"$REPO/scripts/alert-failure.sh" "ninety-days-report" "$RC" "see $OUT_LOG" || true

exit "$RC"