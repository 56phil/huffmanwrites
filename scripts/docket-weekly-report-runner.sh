#!/bin/bash
# Weekly federal docket report runner.
# Invoked by launchd (com.huffmanwrites.docket-weekly-report) every Saturday at
# 0800 CT, first run Saturday 2026-10-03.
#
# Philip, 2026-09-25: "I want a weekly summary of these three dockets every
# Saturday beginning 3OCT26." The three are the ones check-docket.py already
# watches (Beatty v. Trump, Phang v. Blanche, and the consolidated D.C. Circuit
# appeal).
#
# PUBLISHES. Philip, 2026-09-27: "publish weekly reports that have an exit code of
# 0 after passing all gates." The report this job writes goes to production in the
# same run, so a gate or build failure ABORTS the push rather than being logged
# alongside it: the gates are the only review the piece gets. Before that date the
# job filed a `draft: true` page and left it uncommitted.
#
# The deterministic verification (builds and gates) is done by THIS script rather
# than claimed by the agent, for the same reason: the agent cannot run the gates
# — they are not in its allow-list — so a gate result in its summary would be
# unverifiable. Running them here puts the real exit codes in the log.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="/Users/prh/Developer/huffmanwrites"
SKILL="$REPO/skills/docket-weekly-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/docket-weekly-report.out.log"
ERR_LOG="$LOG_DIR/docket-weekly-report.err.log"
# Timestamp each event as it happens. A single STAMP captured at start would
# stamp every line with the run's start time, which hides how long the run took
# and when verification actually ran.
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
# model ids. Set the real window so a long draft is not auto-compact truncated
# mid-run. This also suppresses the long "auto-compact will use 200k" advisory;
# the remaining one-line [claude-code:unrecognized_model] note is telemetry, is
# emitted on every call, does not affect the exit code, and is not worth faking
# a background session to hide. See senate-report-runner.sh for the full note.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# Override for manual test runs: DOCKET_REPORT_PROMPT="Reply with exactly: SMOKE-OK"
# Note: no apostrophes inside the ${VAR:-...} default; bash 3.2 mis-parses them.
PROMPT="${DOCKET_REPORT_PROMPT:-Read $SKILL and follow it exactly. Write the weekly docket report for this week. It will be published on this run if every gate passes.}"

# ---------------------------------------------------------------------------
# Start guard: first scheduled run is Saturday 2026-10-03.
#
# The job was installed on 2026-09-25 and the schedule fires every Saturday, so
# without this it would produce a report on Saturday 2026-09-26 — a week before
# the date Philip asked for. Exiting before that date is what makes "beginning
# 3OCT26" true rather than approximately true. Exit 0, not an error: the job is
# simply not due yet, and a non-zero code here would raise the failure alert
# every week until October, which is how a real alert gets learned as noise.
# ---------------------------------------------------------------------------
TODAY="$(date '+%Y-%m-%d')"
if [[ "$TODAY" < "2026-10-03" ]]; then
  echo "$(stamp): before 2026-10-03, first report not due, exiting" >> "$OUT_LOG"
  exit 0
fi

cd "$REPO"

# Bound before anything uses it: the preflight guard, the gates and the commit
# all read it, and under `set -u` an unbound expansion is a hard failure.
ARTICLE="content/posts/essays/docket-report-$TODAY.md"

# Shared publish tail: preflight guard, SESSION_STATE entry, commit, push, push
# verification, and the SimpleBrain mirror.
. "$REPO/scripts/publish-report.sh"

echo "$(stamp): starting weekly docket report run" >> "$OUT_LOG"

# Removes a stale file at $ARTICLE before the writer runs, so the post-condition
# is binary: the file exists because this run wrote it, or the run aborts for a
# missing file. Never publishes last week's text under this week's title.
publish_preflight "$ARTICLE"

set +e
# Bash(python3 scripts/check-docket.py*) is required, not optional: the skill's
# first step calls the script for the week's filings, and it is the single
# source of truth for what is watched. Without the grant the agent would fetch
# the docket pages by hand and could only reconstruct the filing list from
# memory or coverage — the fabrication path CLAUDE.md warns about.
# Bash(pdftotext *) is required for reading the filings it must read.
claude -p "$PROMPT" \
  -n "docket-report-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(pdftotext *),Bash(python3 scripts/check-docket.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer exited non-zero; nothing will be published" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "docket-weekly-report" "$RC" "writer failed; see $OUT_LOG" || true
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  echo "$(stamp): writer exited 0 but wrote no article at $ARTICLE" >> "$OUT_LOG"
  echo "$(stamp): refusing to treat a missing file as a quiet week" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "docket-weekly-report" 1 "no article written; see $OUT_LOG" || true
  exit 1
fi

# Authoritative verification builds, run here rather than by the agent. TWO
# builds, and both matter now that this job publishes. The drafts build renders
# the file this run just wrote (the production build has nothing to say about it
# until `draft: false`, which the frontmatter gate requires); the production
# build is what the deploy will actually do, so it is the one that must not fail.
DRAFTS_DEST="$(mktemp -d "${TMPDIR:-/tmp}/hugo-drafts-XXXXXX")"
echo "$(stamp): running verification builds" >> "$OUT_LOG"
BUILD_FAILED=0
for flags in "--gc --minify" "--gc --minify --buildDrafts --destination $DRAFTS_DEST"; do
  set +e
  BUILD_OUT="$(hugo $flags 2>&1)"
  BUILD_RC=$?
  set -e
  if [ "$BUILD_RC" -ne 0 ]; then
    echo "$(stamp): build FAILED [$flags] (exit $BUILD_RC)" >> "$OUT_LOG"
    printf '%s\n' "$BUILD_OUT" >> "$ERR_LOG"
    BUILD_FAILED=1
  else
    echo "$(stamp): build OK [$flags]" >> "$OUT_LOG"
  fi
done
rm -rf "$DRAFTS_DEST"

# Deterministic content gates, run here for the same reason the build is: a
# result the agent could not have produced must not be taken from the agent's
# summary.
#
# A gate failure now ABORTS the publish rather than being noted for review. That
# is the change publishing brings: in a drafting job a failed gate is a note for
# Philip, and here it is the only thing between an unreviewed draft and
# production.
GATE_FAILED=0
run_gate() {
  local label="$1"; shift
  set +e
  GATE_OUT="$(python3 "$@" 2>&1)"
  GATE_RC=$?
  set -e
  if [ "$GATE_RC" -ne 0 ]; then
    echo "$(stamp): gate FAILED [$label] (exit $GATE_RC)" >> "$OUT_LOG"
    printf '%s\n' "$GATE_OUT" >> "$ERR_LOG"
    GATE_FAILED=1
  else
    echo "$(stamp): gate OK [$label]" >> "$OUT_LOG"
  fi
}

# The frontmatter gate reads the artifact the way a publisher does. `draft: true`
# left in place is the failure that would matter most here: commit and push would
# succeed, every other gate would report OK, and the deploy would carry nothing.
run_gate "check-report-frontmatter" "$REPO/scripts/check-report-frontmatter.py" \
  --file "$ARTICLE" --hero-plate 104-docket-report
run_gate "check-quotes --file"     "$REPO/scripts/check-quotes.py"       --file "$ARTICLE"
run_gate "check-links --check"     "$REPO/scripts/check-links.py"        --check
# `--online --titles` is new here and it is not optional for a publishing job.
# It fetches every URL this report cites and compares the page's own <title>
# against the citation's link text, which is the ONLY check in this repo that can
# catch a link resolving to the wrong page -- CLAUDE.md's most dangerous failure,
# invisible to a status code because the URL returns 200. Court and agency
# documents are the citations this report leans on, and a wrong one is exactly
# the failure that looks checkable. DEAD links fail this; a title mismatch is
# printed for the log and does not.
run_gate "check-links --online"    "$REPO/scripts/check-links.py"        --file "$ARTICLE" --online --titles
run_gate "check-emdashes --file"   "$REPO/scripts/check-emdashes.py"     --file "$ARTICLE"
run_gate "check-prepositions --file" "$REPO/scripts/check-prepositions.py" --file "$ARTICLE"
# The corpus-wide hero check: the frontmatter gate above reads this article's own
# paths, and this one reads every hero in content/, so a path already broken
# elsewhere cannot ride along into a deploy.
run_gate "check-hero-paths"        "$REPO/scripts/check-hero-paths.py"
run_gate "check-render-integrity"  "$REPO/scripts/check-render-integrity.py"
run_gate "check-gallery-pages"     "$REPO/scripts/check-gallery-pages.py"
# A published installment of a series must carry `featuredOnHome: true`, or it
# reaches no reader from the home page: the feed takes its five Recent Posts from
# flagged posts only, and more than five are already flagged.
run_gate "check-series-posts"      "$REPO/scripts/check-series-posts.py" --file "$ARTICLE"

if [ "$BUILD_FAILED" -ne 0 ] || [ "$GATE_FAILED" -ne 0 ]; then
  echo "$(stamp): a build or gate failed; NOT PUBLISHING. The article is left in place for review." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "docket-weekly-report" 1 "a build or gate failed; see $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# Dry run: everything up to and including verification, then stop. This exists
# because the job publishes, so there is no safe way to exercise the pipeline
# without it.
publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/docket-detail-XXXXXX")"
{
  echo "- **The filings came from \`scripts/check-docket.py\`**, the same registry the docket watcher reads, because the three watched dockets are declared there and nowhere else. The writer is required to read the script rather than reconstruct the filing list from coverage."
} > "$DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"
publish_simplebrain "$ARTICLE" "/Users/prh/Developer/SimpleBrain" "essays"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
