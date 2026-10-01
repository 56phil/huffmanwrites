#!/bin/bash
# Weekly Kansas City Chiefs report runner.
# Invoked by launchd (com.huffmanwrites.chiefs-weekly-report) every Tuesday at
# 1830 CT, in season only.
#
# Philip, 2026-09-25: "New weekly report job: Every Tuesday, at 1830 CT, publish
# a comprehensive report on the Kansas City Chiefs."
#
# PUBLISHES. This was the first job to do so (Philip, 2026-09-25: "Every Tuesday,
# at 1830 CT, publish a comprehensive report on the Kansas City Chiefs"), and on
# 2026-09-27 Philip extended the same rule to the other weekly reports: "publish
# weekly reports that have an exit code of 0 after passing all gates."
#
# Because all three now publish, the publish tail — preflight guard, SESSION_STATE
# entry, commit, push, push verification, SimpleBrain mirror — lives once, in
# `scripts/publish-report.sh`, which this runner sources. Copying it into three
# runners would give three places to drift, and drift of exactly this kind has
# already shipped: the `featuredOnHome` requirement lived in one skill and not
# another, and five Senate reports published without reaching the home feed.
#
# What that changes about the design, and why the shape below is more defensive
# than its siblings:
#
#   1. The gates are the last thing between an unreviewed draft and production,
#      so a gate failure must ABORT the push rather than be logged alongside it.
#   2. The runner writes SESSION_STATE.md itself, from the real gate results,
#      instead of letting the agent describe them. The agent cannot run the
#      gates (they are deliberately outside its allow-list), so its summary
#      could only ever assert a result it did not produce. Writing the entry
#      here means the numbers in it are the ones in this log.
#   3. It verifies the push landed. `git push` exit 0 after a race with another
#      push does not mean the commit is on the remote, and a report that was
#      written, committed, and never delivered is the failure that looks like
#      success.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/chiefs-weekly-report.md"
COLLECTOR="$REPO/scripts/chiefs-report.py"
SB="/Users/prh/Developer/SimpleBrain"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/chiefs-weekly-report.out.log"
ERR_LOG="$LOG_DIR/chiefs-weekly-report.err.log"
# Timestamp each event as it happens. A single STAMP captured at start stamped
# every line with the run's start time, which hid how long the run took and when
# verification actually ran.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL, so
# the base URL must NOT carry a /v1 suffix (Ollama serves Anthropic-format
# requests at /v1/messages). Model id must match `ollama list` exactly.
# Policy (Philip, 2026-09-06): no Anthropic or OpenAI resources. The only AI API
# keys available are FAL and Ollama; Ollama may be local or cloud.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null)"
[ -z "$OLLAMA_KEY" ] && OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
# The model has a 1M context window; Claude Code assumes 200k for unrecognized
# model ids. Set the real window so a long article is not auto-compact truncated
# mid-run. See senate-report-runner.sh for the full note on the one-line
# [claude-code:unrecognized_model] telemetry this also does not remove.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: CHIEFS_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default. bash 3.2 mis-parses them
# and reports the damage as a syntax error far later in the file, which is how
# this cost a debugging round. The default reads "the weekly Chiefs report"
# rather than "this week's report" for that reason, not for style.
TODAY="$(date '+%Y-%m-%d')"
PROMPT="${CHIEFS_REPORT_PROMPT:-Read $SKILL and follow it exactly. The briefing pack is at /tmp/chiefs-pack-$TODAY.md. Write the weekly Chiefs report.}"

echo "$(stamp): starting Chiefs weekly report run" >> "$OUT_LOG"

cd "$REPO"

# ---------------------------------------------------------------------------
# Season guard. The NFL has no games from February to August, and a weekly
# report with no games is a report with nothing in it — which is precisely when
# an unattended writer invents something to fill the silence. The guard reads
# the league's own published calendar rather than a hardcoded month range, so it
# rolls over by itself next season instead of going quietly stale.
#
# Exit 0, not non-zero: the job is simply not due, and a non-zero code here
# would raise the failure alert every Tuesday for six months, which is how a
# real alert gets learned as noise. Same reasoning as the docket report's start
# guard.
# ---------------------------------------------------------------------------
set +e
STATE_OUT="$(python3 "$COLLECTOR" --season-state 2>&1)"
STATE_RC=$?
set -e
if [ "$STATE_RC" -eq 3 ]; then
  echo "$(stamp): $STATE_OUT — off season, no report, exiting" >> "$OUT_LOG"
  exit 0
fi
if [ "$STATE_RC" -ne 0 ]; then
  echo "$(stamp): could not determine the league phase (exit $STATE_RC): $STATE_OUT" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" "$STATE_RC" \
    "could not read the league calendar; see $OUT_LOG" || true
  exit "$STATE_RC"
fi
echo "$(stamp): $STATE_OUT" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# Briefing pack. Deterministic and read here rather than left to the agent, for
# the same reason the docket report runs check-docket.py: the pack is the single
# source of truth for the week's numbers, and an agent that fetched ESPN itself
# could only reconstruct them from memory. A pack failure is a hard stop —
# running the writer without its data is how a fabricated score gets published.
# ---------------------------------------------------------------------------
PACK="/tmp/chiefs-pack-$TODAY.md"
set +e
python3 "$COLLECTOR" > "$PACK" 2>> "$ERR_LOG"
PACK_RC=$?
set -e
if [ "$PACK_RC" -ne 0 ]; then
  echo "$(stamp): briefing pack FAILED (exit $PACK_RC)" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" "$PACK_RC" \
    "the briefing pack could not be fetched; see $ERR_LOG" || true
  exit "$PACK_RC"
fi
echo "$(stamp): briefing pack written to $PACK ($(wc -l < "$PACK" | tr -d ' ') lines)" >> "$OUT_LOG"

# The article path is defined here, before the writer runs, because the guard
# below and the commit at the end both need it and it must not be able to change
# between them.
ARTICLE="content/posts/sports/chiefs-report-$TODAY.md"

# Shared publish tail. Sourcing it here means the preflight guard, the
# SESSION_STATE entry, the commit, the push, the push verification and the
# SimpleBrain mirror are the same code the Senate and docket jobs run.
JOB="chiefs-weekly-report"
. "$REPO/scripts/publish-report.sh"

# ---------------------------------------------------------------------------
# Pre-run tree guard: see the long note in scripts/publish-report.sh. Two
# hazards, handled differently — a dirty SESSION_STATE.md is a refusal (someone
# else's edits would be committed under this run's message), and a stale file at
# $ARTICLE is a clean-up (the dangerous outcome is the writer failing and the
# runner then committing old text under this run's title).
# ---------------------------------------------------------------------------
publish_preflight "$ARTICLE"

set +e
# Bash(python3 scripts/chiefs-report.py*) is required, not optional: the skill's
# first step re-runs the collector for specific fields, and without the grant
# the writer would fetch ESPN pages by hand and could only reconstruct the
# numbers from memory — the fabrication path CLAUDE.md warns about.
claude -p "$PROMPT" \
  -n "chiefs-report-$TODAY" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/chiefs-report.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer exited non-zero; nothing will be published" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" "$RC" "writer failed; see $OUT_LOG" || true
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  echo "$(stamp): writer exited 0 but wrote no article at $ARTICLE" >> "$OUT_LOG"
  echo "$(stamp): refusing to treat a missing file as a quiet week" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 "no article written; see $OUT_LOG" || true
  exit 1
fi

# ---------------------------------------------------------------------------
# Pre-publication checks on the artifact itself are part of the gate set below,
# in `scripts/check-report-frontmatter.py`. They used to live in
# `chiefs-report.py --validate`; they moved when the Senate and docket jobs
# started publishing too, so that one gate covers all three rather than three
# copies drifting apart. The rules are the same ones: draft false,
# `featuredOnHome` true, a date not ahead of the clock, the series hero present
# and resolving to real files, and the closing attribution.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Verification builds, run here rather than by the agent. TWO builds, and the
# second is the one that matters: the production build excludes draft: true
# content, so it says nothing about a draft. Both must pass before the push.
# Shared with the other publishing runners (see scripts/publish-report.sh).
# ---------------------------------------------------------------------------
report_build "$ARTICLE"
if [ "$BUILD_FAILED" -ne 0 ]; then
  echo "$(stamp): a build failed; not publishing" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 "a build failed; see $ERR_LOG" || true
  exit 1
fi

# ---------------------------------------------------------------------------
# Deterministic content gates. Unlike the drafting jobs, a gate failure here
# STOPS the push. This piece is going to production without a human reading it,
# so the gates are the review, and a gate result the agent could not have
# produced must not be left to the agent's summary.
#
# The list lives in `scripts/publish-report.sh` (run_report_gates), shared with
# the Senate and docket jobs. It already included `check-hero-paths`, which this
# runner's own list had drifted to omit, and it is the one place a new gate has
# to be added for all three.
# ---------------------------------------------------------------------------
run_report_gates "$ARTICLE" --plate 103-chiefs-report

if report_gates_failed; then
  echo "$(stamp): a gate failed; NOT PUBLISHING. The article is left in place for review." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 "a content gate failed; see $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# Dry run: everything up to and including verification, then stop. This exists
# because this job publishes, so there is no safe way to exercise the pipeline
# without it. `REPORT_DRY_RUN=1` (and the historical `CHIEFS_DRY_RUN=1`) writes
# the article, runs both builds and every gate, and prints what WOULD be
# committed and pushed — then leaves the work in the tree for inspection and
# writes nothing to git or SimpleBrain. A pipeline this destructive must be
# provable without being performed.
# ---------------------------------------------------------------------------
publish_dry_run_stop "$ARTICLE" && exit 0

# ---------------------------------------------------------------------------
# The market chart is a generated asset, so it is staged HERE, before the shared
# tail commits. Two reasons it is this runner's job and not the library's:
#
#   1. It belongs to this series. `publish-report.sh` is shared by three jobs,
#      and naming a Chiefs asset path inside it would have staged the Chiefs
#      chart into a Senate or docket publish commit.
#   2. Only the collector knows where it writes. The path is asserted against
#      the tree rather than assumed: if the collector's `CHART_PATH` ever moves,
#      this adds nothing and the next gate fails loudly instead of the chart
#      silently going missing from the deploy.
#
# A missing chart is not fatal — the collector already omits the figure from the
# pack when it cannot draw one, so the writer will not have referenced it. It is
# logged so a chart that stops being generated is visible rather than silent.
# ---------------------------------------------------------------------------
CHART="static/img/articles/103-chiefs-markets.svg"
if [ -f "$CHART" ]; then
  if git add "$CHART"; then
    echo "$(stamp): staged the market chart ($CHART)" >> "$OUT_LOG"
  else
    echo "$(stamp): could not stage $CHART; publishing without it" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 "could not stage the market chart; see $OUT_LOG" || true
  fi
else
  echo "$(stamp): no market chart at $CHART; the report publishes without the figure" >> "$OUT_LOG"
fi

# ---------------------------------------------------------------------------
# SESSION_STATE entry, commit, push, push verification — written and performed
# by `scripts/publish-report.sh` from the results above, so all three publishing
# jobs record and deliver their output identically.
#
# The agent is deliberately not allowed to write the entry: its summary cannot
# contain a gate result it was unable to produce, so an entry it authored could
# only assert. Written from this log, every claim in the entry is a line in it.
# ---------------------------------------------------------------------------
CHIEFS_DETAIL="$(mktemp "${TMPDIR:-/tmp}/chiefs-detail-XXXXXX")"
{
  WEEK_LINE="$(grep -m1 '^\*\*Answer:' "$ARTICLE" | cut -c1-300 || true)"
  if [ -n "$WEEK_LINE" ]; then
    echo "- **The week, as the piece frames it:** $WEEK_LINE"
  fi
  echo "- **Data came from \`scripts/chiefs-report.py\`**, the briefing pack the runner writes before the writer starts: the week's game with both teams' box scores and leaders, every scoring play, both injury reports, the standings and seed list, the season statistics by category, the next game with the feed's own odds and its matchup projection, and two weeks of Chiefs-tagged coverage with its URLs. The writer is not permitted to recall a score or a record. URLs are cited from the feed or from a page the run fetched; a constructed URL is the repo's most dangerous failure and this is the job where one would ship unreviewed."
} > "$CHIEFS_DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '\"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$CHIEFS_DETAIL"
rm -f "$CHIEFS_DETAIL"

# ---------------------------------------------------------------------------
# SimpleBrain, per the post-commit flow in CLAUDE.md, run and verified by the
# shared tail. A SimpleBrain failure does NOT fail the site publish: the article
# is already live, and this is the secondary mirror. It is alerted so it is
# visible rather than silent.
# ---------------------------------------------------------------------------
publish_simplebrain "$ARTICLE" "$SB" "sports"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
