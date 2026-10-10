#!/bin/bash
# Weekly Satire runner.
# Invoked by launchd (com.huffmanwrites.weekly-satire) every Monday at 07:00 CT.
# RETIRED 2026-10-10: the series is complete — all four installments are
# pre-written and embargoed to their dates — so every firing exits 0 before the
# preflight. See the retirement guard below.
#
# Philip, 2026-10-07: "Set up a weekly task to publish a piece mocking Trump
# start next Monday. End the task 03NOV26." Asked what form each piece should
# take, he chose: "randomly select the choice each week" (the four forms are in
# skills/weekly-satire.md). The masthead is "Weekly Satire".
#
# PUBLISHES. This job goes to production in the same run it writes the file, so a
# gate or build failure ABORTS the push rather than being logged alongside it:
# the gates are the only review the piece gets. The publish tail — preflight
# guard, SESSION_STATE entry, commit, push, push verification, SimpleBrain
# mirror — lives once, in `scripts/publish-report.sh`, which this runner sources.
#
# Why 07:00 Monday: the Monday 13:00-14:00 window already holds site-audit
# (13:00), wiki-check (13:30) and weekly-integrity (14:00). A morning slot keeps
# the piece clear of that cluster and clear of the report jobs (docket Saturday
# 08:00, Senate Sunday 07:00, Chiefs Tuesday 18:30). Sequential fal.ai use is
# moot here because the series uses one fixed hero plate, generated once, not a
# fresh image per run.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded "/Users/<who>/Developer/<repo>" names a
# missing file, python3 exits 2, and the Pages deploy goes red (2026-10-08). A
# test in scripts/test_gates.py holds the rule for every script under scripts/.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$REPO/skills/weekly-satire.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/weekly-satire.out.log"
ERR_LOG="$LOG_DIR/weekly-satire.err.log"
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

# Override for manual test runs: WEEKLY_SATIRE_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${WEEKLY_SATIRE_PROMPT:-Read $SKILL and follow it exactly. Write the Weekly Satire piece for this week. It will be published on this run if every gate passes.}"

# ---------------------------------------------------------------------------
# Retirement guard: the series is complete, and this job no longer writes.
#
# Philip, 2026-10-10: "We need four articles for this project," then, choosing
# to pre-produce rather than publish-weekly, "Pre-produce all four now." All
# four installments are committed as `content/posts/essays/weekly-satire-2026-
# {10-12,10-19,10-26,11-02}.md`, each embargoed to its Monday 07:00 CT date and
# all four reviewed before they ship. There is nothing left for this job to
# write, so it exits 0 on every firing.
#
# Exit 0, and at the very top — before publish_preflight. The preflight deletes
# any file already at $ARTICLE, and $ARTICLE is bound to `weekly-satire-$TODAY.md`
# below, so a firing on 2026-10-19, 10-26 or 11-02 would silently discard that
# week's reviewed installment and could not put anything in its place. The guard
# must therefore precede the preflight, not follow it. Exit 0 rather than an
# error for the same reason the old date guard used it: a non-zero code would
# raise the failure alert every Monday forever, which is how a real alert gets
# learned as noise.
#
# WEEKLY_SATIRE_IGNORE_GUARDS=1 still runs the writer, so the pipeline can be
# exercised without publishing. Pair it with REPORT_DRY_RUN=1 as before; a live
# run sets no such variable, and the scheduled run never reaches the writer.
#
# The plist stays installed and valid (a job with no schedule key fails
# check-plists.py), and the runner keeps every contract the tests read, so this
# is a retirement in place rather than a deletion. If the series is ever revived,
# replace this block with a real start date — do not merely delete it, or the
# preflight's delete-the-old-file behavior returns with it.
# ---------------------------------------------------------------------------
if [ "${WEEKLY_SATIRE_IGNORE_GUARDS:-0}" != "1" ]; then
  echo "$(stamp): the series is complete; all four installments are pre-written, exiting" >> "$OUT_LOG"
  exit 0
fi

# ---------------------------------------------------------------------------
# Date guard: the range this job would have run, from Monday 2026-10-19 through
# Monday 2026-11-02. Reached only under WEEKLY_SATIRE_IGNORE_GUARDS=1, so it is
# the pipeline-exercise path and not a schedule; the retirement guard above is
# what the installed job hits. The END guard is still the self-disable ("End the
# task 03NOV26"): every Monday after 2026-11-02 exits 0.
# ---------------------------------------------------------------------------
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" > "2026-11-02" ]]; then
  echo "$(stamp): the series ended 2026-11-02; self-disabled, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

# The article path is bound before anything uses it: the preflight guard, the
# gates and the commit all read it, and under `set -u` an unbound expansion is a
# hard failure. Relative to $REPO, which is where we are.
ARTICLE="content/posts/essays/weekly-satire-$TODAY.md"

# Shared publish tail: preflight guard, SESSION_STATE entry, commit, push, push
# verification, and the SimpleBrain mirror. JOB is the label suffix the library
# expands inside publish_article and in every alert; it MUST be bound before the
# source, or the first real publish dies at the SESSION_STATE-entry line under
# `set -u` with "JOB: unbound variable".
JOB="weekly-satire"
. "$REPO/scripts/publish-report.sh"

# Reachability guard: fail loudly and early if the local Ollama server is down.
# See scripts/ollama-probe.sh.
. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

echo "$(stamp): starting Weekly Satire run" >> "$OUT_LOG"

# Removes a stale file at $ARTICLE before the writer runs, so the post-condition
# is binary: the file exists because this run wrote it, or the run aborts for a
# missing file. Never publishes last week's text under this week's title.
publish_preflight "$ARTICLE"

set +e
# The writer gets web access to find and READ this week's sources, and Bash(date)
# for the frontmatter, and nothing else: no hugo, no git, no gate scripts, no
# SESSION_STATE. The runner owns the build, the gates, the entry, the commit and
# the push, so a result the writer could not have produced is never taken from
# the writer's summary.
#
# NOTE for a future session: this is the one writing job in the repo whose
# material is selected rather than collected by a script. There is no
# `weekly-satire.py` briefing pack, and there cannot be one, because the subject
# differs every week. The fabrication risk that a pack would remove is therefore
# handled by the skill's rules (fetch before cite; verbatim quotations; no
# recalled-then-supported facts) and by the gate set below, which fails the
# publish on a dead link, a placeholder anchor, a mis-named quotation detail, or
# a sentence-final preposition. If a future session wants to harden this further,
# the lever is a collector that pre-fetches a candidate pool of the week's items
# and forces the writer to select from it — not a longer set of instructions.
claude -p "$PROMPT" \
  -n "weekly-satire-$TODAY" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/check-links.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer FAILED (exit $RC); NOT PUBLISHING." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "writer failed; see $OUT_LOG" || true
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  # The skill explicitly permits the writer to write nothing on a thin week and
  # to exit non-zero instead. That path is caught above. Reaching HERE with no
  # file means the writer exited 0 without producing the piece, which is a
  # failure of the run, not a quiet week.
  echo "$(stamp): writer exited 0 but wrote no $ARTICLE; NOT PUBLISHING." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "no article at $ARTICLE; see $OUT_LOG" || true
  exit 1
fi

# Authoritative verification builds, run here rather than by the agent. TWO
# builds, and both matter: the drafts build renders the file this run just wrote
# (the production build has nothing to say about it until `draft: false`, which
# the frontmatter gate requires); the production build is what the deploy will
# actually do, so it is the one that must not fail.
report_build "$ARTICLE"
if [ "$BUILD_FAILED" -ne 0 ]; then
  echo "$(stamp): a build FAILED; NOT PUBLISHING." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "build failed; see $OUT_LOG" || true
  exit 1
fi

# Deterministic content gates, run here for the same reason the build is: a
# result the agent could not have produced must not be taken from the agent's
# summary. The gate list lives in `scripts/publish-report.sh` (run_report_gates)
# so every publishing job runs exactly the same set.
#
# A gate failure ABORTS the publish rather than being noted for review: here the
# gates are the only thing between an unreviewed draft and production.
run_report_gates "$ARTICLE" --plate 114-weekly-satire

if report_gates_failed; then
  echo "$(stamp): a gate FAILED; NOT PUBLISHING. The article is left in place for review." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "a gate failed; see $OUT_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# Dry run: everything up to and including verification, then stop. This exists
# because the job publishes, so there is no safe way to exercise the pipeline
# without it. REPORT_DRY_RUN=1 leaves the work in the tree and writes nothing to
# git or SimpleBrain.
publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/satire-detail-XXXXXX")"
{
  echo "- **The form, and the week's subject:** written to the brief in \`skills/weekly-satire.md\`; the form is chosen at random from the four the skill lists, and every factual claim is sourced from a page the writer fetched."
  echo "- **Every quotation is verbatim from its fetched source**, and the runner aborts the push on a dead link, a placeholder anchor, or a quoted name detail that appears on none of the pages the citing line links. This is the one writing job whose material is selected rather than collected by a script, so the skill's fetch-before-cite rules are the primary control."
} > "$DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"
publish_simplebrain "$ARTICLE" "/Users/prh/Developer/SimpleBrain" "essays"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
