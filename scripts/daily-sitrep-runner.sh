#!/bin/bash
# Daily Global SITREP runner.
# Invoked by launchd (com.huffmanwrites.daily-sitrep) every day at 06:00 CT.
#
# Philip, 2026-10-07: "I want to publish a weekly report every day of the week."
# Asked what shape that meant, he chose "Let's do a global SITREP every day" —
# one recurring series, seven installments a week, rather than a new weekly
# series for each empty weekday. Asked which beats it should cover, he chose
# the courts, the administration and the rule of law, markets and the economy,
# elections and civics, and AI and technology. The world-news beat is implied
# by "global".
#
# PUBLISHES. This job goes to production in the same run it writes the file, so a
# gate or build failure ABORTS the push rather than being logged alongside it:
# with a daily piece there is no review window at all — by the time a human
# could read it, tomorrow's edition is already due. The gates are the entire
# review. The publish tail — preflight guard, SESSION_STATE entry, commit, push,
# push verification, SimpleBrain mirror — lives once, in
# `scripts/publish-report.sh`, which this runner sources.
#
# Why 06:00: the 07:00 Monday cluster (weekly-satire), the 07:00 Sunday
# (senate-report), Saturday 08:00 (docket-weekly-report) and Tuesday 18:30
# (chiefs-weekly-report) all sit above it, and the Monday 13:00-14:00 window
# holds site-audit, wiki-check and weekly-integrity. 06:00 is clear of every
# one of them, every day.
#
# Why the pack is a hard stop. The writer is a headless model session; the one
# thing it can never do is know today's numbers. `scripts/sitrep-pack.py` is the
# only thing in this pipeline that has seen them. Running the writer without its
# pack does not degrade the report, it converts every figure in it into a
# recalled one, and a recalled figure is the fabrication path CLAUDE.md was
# written about. Same rule as the Chiefs job's ESPN pack.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/daily-sitrep.md"
COLLECTOR="$REPO/scripts/sitrep-pack.py"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/daily-sitrep.out.log"
ERR_LOG="$LOG_DIR/daily-sitrep.err.log"
# Timestamp each event as it happens. A single STAMP captured at start would
# stamp every line with the run's start time, which hides how long the run took
# and when verification actually ran.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL, so
# the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
# Policy (Philip, 2026-09-06): no Anthropic or OpenAI resources. The only AI API
# keys available are FAL and Ollama; Ollama may be local or cloud. Auth uses
# OLLAMA_API_KEY from the login keychain (huffmanwrites-ollama), with ~/.secrets
# as fallback.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null)"
[ -z "$OLLAMA_KEY" ] && OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
# The model has a 1M context window; Claude Code assumes 200k for unrecognized
# model ids. Set the real window so a long draft is not auto-compact truncated
# mid-run. The remaining one-line [claude-code:unrecognized_model] note is
# telemetry, is emitted on every call, does not affect the exit code, and is not
# worth faking a background session to hide. See senate-report-runner.sh.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

TODAY="$(date '+%Y-%m-%d')"
PACK="/tmp/sitrep-pack-$TODAY.md"

# Override for manual test runs: SITREP_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them
# and reports the damage as a syntax error far later in the file.
PROMPT="${SITREP_PROMPT:-Read $SKILL and follow it exactly. The briefing pack is at $PACK. Write the Global SITREP for today. It will be published on this run if every gate passes.}"

cd "$REPO"

# The article path is bound before anything uses it: the preflight guard, the
# gates and the commit all read it, and under `set -u` an unbound expansion is a
# hard failure. Relative to $REPO, which is where we are.
ARTICLE="content/posts/sitrep/sitrep-$TODAY.md"

# Shared publish tail: preflight guard, SESSION_STATE entry, commit, push, push
# verification, and the SimpleBrain mirror. JOB is the label suffix the library
# expands inside publish_article and in every alert; it MUST be bound before the
# source, or the first real publish dies at the SESSION_STATE-entry line under
# `set -u` with "JOB: unbound variable".
JOB="daily-sitrep"
. "$REPO/scripts/publish-report.sh"

# Reachability guard: fail loudly and early if the local Ollama server is down.
# A daily job is where this matters most — a silent failure here is not one
# missed edition, it is every edition until someone reads the log. See
# scripts/ollama-probe.sh.
. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

echo "$(stamp): starting daily SITREP run" >> "$OUT_LOG"

# Removes a stale file at $ARTICLE before the writer runs, so the post-condition
# is binary: the file exists because this run wrote it, or the run aborts for a
# missing file. Never publishes yesterday's text under today's title.
publish_preflight "$ARTICLE"

# ---------------------------------------------------------------------------
# Briefing pack. Deterministic, collected here rather than left to the agent,
# for the same reason the Chiefs runner collects ESPN itself: the pack is the
# single source of truth for the day's numbers, and a writer that fetched them
# on its own could only reconstruct them from memory.
#
# A pack failure is a hard stop, not a degraded run. The collector exits 0 with
# per-source `SOURCE UNAVAILABLE` lines when individual hosts fail — that is a
# report with a gap in it, which is honest — and non-zero only when it collected
# nothing at all, which is not a report.
# ---------------------------------------------------------------------------
set +e
python3 "$COLLECTOR" --out "$PACK" 2>> "$ERR_LOG"
PACK_RC=$?
set -e
if [ "$PACK_RC" -ne 0 ]; then
  echo "$(stamp): briefing pack FAILED (exit $PACK_RC) — NOT PUBLISHING" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" "$PACK_RC" \
    "the SITREP briefing pack could not be collected; no article was written. See $ERR_LOG" || true
  exit "$PACK_RC"
fi
PACK_LINES="$(wc -l < "$PACK" | tr -d ' ')"
PACK_MISSING="$(grep -c 'SOURCE UNAVAILABLE' "$PACK" || true)"
echo "$(stamp): briefing pack written to $PACK ($PACK_LINES lines, $PACK_MISSING source(s) unavailable)" >> "$OUT_LOG"

set +e
# Bash(python3 scripts/sitrep-pack.py*) is required, not optional: the skill's
# steps re-run the collector for specific fields rather than quoting a pack it
# read once. Without the grant the writer would fetch the Federal Register and
# the Treasury by hand and could only reconstruct the numbers from memory —
# exactly the fabrication path CLAUDE.md warns about.
claude -p "$PROMPT" \
  -n "daily-sitrep-$TODAY" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/sitrep-pack.py*),Bash(python3 scripts/check-emdashes.py*),Bash(python3 scripts/check-prepositions.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer FAILED (exit $RC) — NOT PUBLISHING" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" "$RC" \
    "the SITREP writer exited non-zero; see $ERR_LOG" || true
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  echo "$(stamp): writer exited 0 but wrote no article at $ARTICLE — NOT PUBLISHING" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
    "the SITREP writer produced no article; see $OUT_LOG" || true
  exit 1
fi

# Authoritative verification builds, run here rather than by the agent. TWO
# builds, and both matter: the drafts build renders the file this run just wrote
# (the production build has nothing to say about it until `draft: false`, which
# the frontmatter gate requires); the production build is what the deploy will
# actually do, so it is the one that must not fail.
report_build "$ARTICLE"
if [ "$BUILD_FAILED" -ne 0 ]; then
  echo "$(stamp): a verification build failed — NOT PUBLISHING" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
    "a verification build failed; nothing was published. See $ERR_LOG" || true
  exit 1
fi

# Deterministic content gates, run here for the same reason the build is: a
# result the agent could not have produced must not be taken from the agent's
# summary. The gate list lives in `scripts/publish-report.sh` (run_report_gates)
# so every publishing job runs exactly the same set.
#
# A gate failure ABORTS the publish rather than being noted for review: here the
# gates are the only thing between an unreviewed draft and production, and there
# is no next-day human pass to catch what they miss.
run_report_gates "$ARTICLE" --plate 115-sitrep

if report_gates_failed; then
  echo "$(stamp): one or more gates failed — NOT PUBLISHING" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
    "a content gate failed; nothing was published. See $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# Dry run: everything up to and including verification, then stop. This exists
# because the job publishes, so there is no safe way to exercise the pipeline
# without it. REPORT_DRY_RUN=1 leaves the work in the tree and writes nothing to
# git or SimpleBrain.
publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/sitrep-detail-XXXXXX")"
{
  echo "- **The pack behind it:** $PACK_LINES lines from \`scripts/sitrep-pack.py\`, $PACK_MISSING source(s) unavailable on this run. The Federal Register, the CourtListener search API, the U.S. Treasury daily yield curve, FiscalData, CNBC's quote service, the BLS public API and Polymarket's Gamma API supply it; the writer may not recall a figure, so every number in the piece is one the collector fetched. The world-news and AI-news beats have no collector and were fetched and cited by the writer."
} > "$DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"
publish_simplebrain "$ARTICLE" "/Users/prh/Developer/SimpleBrain" "sitrep"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
