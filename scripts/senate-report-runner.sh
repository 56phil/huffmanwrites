#!/bin/bash
# Weekly Senate Race Report runner.
# Invoked by launchd (com.huffmanwrites.senate-report) every Sunday at 07:00 CT.
# Self-disables after 2026-11-02 (Election Day: 2026-11-03).
#
# PUBLISHES. Philip, 2026-09-27: "publish weekly reports that have an exit code of
# 0 after passing all gates." The report this job writes goes to production in the
# same run, so a gate or build failure ABORTS the push rather than being logged
# alongside it: the gates are the only review the piece gets. Before that date the
# job filed a `draft: true` page and left it uncommitted.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded "/Users/<who>/Developer/<repo>" names a
# missing file, python3 exits 2, and the Pages deploy goes red (2026-10-08). A
# test in scripts/test_gates.py holds the rule for every script under scripts/.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
# The model has a 1M context window; Claude Code assumes 200k for
# unrecognized model ids. Set the real window so long drafts are not
# auto-compact truncated mid-run.
#
# This var is ALSO the suppression for the noisy part of the "unrecognized
# model" advisory, and it is worth knowing which is which (measured 2026-09-20
# by A/B on this machine):
#   CLAUDE_CODE_MAX_CONTEXT_TOKENS set   -> stderr 109 bytes, long warning ABSENT
#   unset                                 -> stderr 591 bytes, long warning PRESENT
# The long warning is the one that says auto-compact will use 200k, and setting
# the real window removes it.
#
# What remains is a single line the binary writes on EVERY api call when the
# model id is not one Claude Code recognizes:
#   [claude-code:unrecognized_model] {"model":"...","query_source":"sdk"}
# It is emitted by this branch (read from the 2.1.234 binary):
#   H("tengu_api_unrecognized_model", {...}); if (stderrIsTty && SESSION_KIND
#   !== "bg") writeToStderr(line); else log(line, "warn");
# It is telemetry, not an error: it does not affect the exit code, so it cannot
# raise the failure alert (that is gated on $RC). Do NOT try to silence it:
#   - CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1 does not remove it.
#   - CLAUDE_CODE_SESSION_KIND=bg does, but that fakes a background session and
#     changes permission handling, prompt injection and worktree isolation in
#     the same binary. It is suppression with real side effects.
#   - A modelOverrides mapping ({"claude-sonnet-4-5":"deepseek-v4.1-flash:cloud"})
#     does remove it, and is honored, but it makes the session lie about which
#     model is running: the transcript then attributes the draft to
#     claude-sonnet-4-5. Not worth it to hide one diagnostic line.
# The only honest fix is for the API to serve an id Claude Code recognizes.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: SENATE_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${SENATE_REPORT_PROMPT:-Read $SKILL and follow it exactly. Write the Senate race article for this week. It will be published on this run if every gate passes.}"

# Guard: only run on or before 2026-11-02.
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" > "2026-11-02" ]]; then
  echo "$(stamp): past 2026-11-02, job complete, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

# The article path is bound before anything uses it: the preflight guard, the
# gates and the commit all read it, and under `set -u` an unbound expansion is a
# hard failure. Relative to $REPO, which is where we are.
ARTICLE="content/posts/essays/senate-race-report-$TODAY.md"

# Shared publish tail: preflight guard, SESSION_STATE entry, commit, push, push
# verification, and the SimpleBrain mirror. Three jobs share it, so the parts
# that must not drift live in one file. JOB is the label suffix the library
# expands inside publish_article and in every alert; it MUST be bound before the
# source, or the first real publish dies at the SESSION_STATE-entry line under
# `set -u` with "JOB: unbound variable".
JOB="senate-report"
. "$REPO/scripts/publish-report.sh"

# Reachability guard: the writer is useless if the local Ollama server is down.
# Fails loudly here rather than mid-draft on a connection error. See
# scripts/ollama-probe.sh for why this exists and what keeps the server up.
. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

echo "$(stamp): starting Senate race report run" >> "$OUT_LOG"

# Removes a stale file at $ARTICLE before the writer runs, so the post-condition
# is binary: the file exists because this run wrote it, or the run aborts for a
# missing file. Never publishes last week's text under this week's title.
publish_preflight "$ARTICLE"

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

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer exited non-zero; nothing will be published" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "senate-report" "$RC" "writer failed; see $OUT_LOG" || true
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  echo "$(stamp): writer exited 0 but wrote no article at $ARTICLE" >> "$OUT_LOG"
  echo "$(stamp): refusing to treat a missing file as a quiet week" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "senate-report" 1 "no article written; see $OUT_LOG" || true
  exit 1
fi

# Authoritative verification builds, run here rather than by the agent.
# Historically the agent was granted Bash(hugo --gc --minify) as an exact-match
# rule, but any variant it naturally reached for — a redirect, a "&&" compound,
# or a different flag set — was denied by the permission layer, so the Sept 13
# run reported "three attempts were gated" and left the build unrun. Running it
# in the script makes the check deterministic and puts the exit code in the log.
#
# TWO builds, and both matter now that this job publishes. The drafts build is
# what renders the file this run just wrote (the production build has nothing to
# say about it until `draft: false`); the production build is what the deploy
# will actually do, so it is the one that must not fail.
report_build "$ARTICLE"

# Deterministic content gates, run here for the same reason the build is: the
# run summary for 2026-09-20 claimed "check-quotes.py and check-links.py
# --check both pass" when neither script appears in the agent's allow-list, so
# the claim was unverifiable from the log. The gate list itself lives in
# `scripts/publish-report.sh` (run_report_gates) so all three publishing jobs
# run exactly the same set — three copies is how the featuredOnHome rule came
# to live in one skill and not another.
#
# A gate failure ABORTS the publish rather than being noted for review: here the
# gates are the only thing standing between an unreviewed draft and production.
run_report_gates "$ARTICLE" --plate 105-senate-race-report

if [ "$BUILD_FAILED" -ne 0 ] || report_gates_failed; then
  echo "$(stamp): a build or gate failed; NOT PUBLISHING. The article is left in place for review." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "senate-report" 1 "a build or gate failed; see $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# Dry run: everything up to and including verification, then stop. This exists
# because the job publishes, so there is no safe way to exercise the pipeline
# without it. REPORT_DRY_RUN=1 leaves the work in the tree and writes nothing to
# git or SimpleBrain.
publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/senate-detail-XXXXXX")"
{
  echo "- **The week, as the piece frames it:** $(grep -m1 '^\*\*Answer:' "$ARTICLE" | cut -c1-300 || true)"
  echo "- **Data came from \`scripts/fetch-senate-ratings.py\`** (the standing ratings table and \`--sources\`), which the writer is required to read rather than reconstruct: cookpolitical, centerforpolitics and realclearpolitics all refuse automated fetch, so a table assembled from memory is the fabrication path this repo warns about."
} > "$DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"
publish_simplebrain "$ARTICLE" "/Users/prh/Developer/SimpleBrain" "essays"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
