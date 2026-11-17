#!/bin/bash
# Ground-stop conclusion runner — writes the piece and publishes it, once.
# Invoked by launchd (com.huffmanwrites.ground-stop-conclusion-release) at
# 10:00 CT on 1 December 2026, which is 1600Z.
#
# Philip, 17NOV26: "It is my wish that the article be written as part of the act
# of publishing." So this is a WRITING job, not a release job: the piece is
# written in this run and goes to production in the same run, which is why a
# failed gate ABORTS the push rather than being logged beside it. The gates are
# the only review the piece gets.
#
# The publish tail — preflight guard, SESSION_STATE entry, commit, push, push
# verification, SimpleBrain mirror — lives once, in `scripts/publish-report.sh`,
# which this runner sources. The delivery check needs the page to answer its own
# title after the deploy, so 1600Z is a claim this job keeps or fails on.
#
# ONE-OFF. launchd has no Year key, so `Month 12 / Day 1` fires every 1 December
# forever. DUE below is the only date this job writes; any other day exits 0 with
# a log line, because a job that alerts every December about a series it has
# finished trains its reader to ignore the alert. After the 2026-12-01 run:
#   launchctl bootout gui/"$(id -u)"/com.huffmanwrites.ground-stop-conclusion-release
#   rm ~/Library/LaunchAgents/com.huffmanwrites.ground-stop-conclusion-release.plist
#
# THE PREREQUISITE IS THE RECORD, not the draft. The writer may not recall a
# figure, so the pack has to be current and its citations have to open before the
# run starts: §21 must hold rows and `--audit` must pass. A pack that cannot
# support the piece aborts the run at exit 3, which is the honest failure — the
# alternative is a published article built on a stale ledger.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$REPO/skills/ground-stop-conclusion.md"
PACK="${GROUND_STOP_CONCLUSION_PACK:-$REPO/future-pieces/faa-ground-stop-source-notes.md}"
LOG_DIR="$HOME/Library/Logs"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }
alert() { "$REPO/scripts/alert-failure.sh" "$JOB" "$1" "$2" || true; }

# Provider routing: Claude Code appends /v1/messages to ANTHROPIC_BASE_URL, so
# the base URL must NOT carry a /v1 suffix. Model id must match `ollama list`.
# Policy (Philip, 2026-09-06): no Anthropic or OpenAI resources; Ollama only.
# Both reads tolerate "not found": `security` exits 44 when the item is absent,
# and under `set -e` an assignment inherits that status, which would kill the
# run before its first guard. The `if` form also avoids a bare `[ -z ] && ...`
# leaving a false status behind.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null || true)"
if [ -z "$OLLAMA_KEY" ]; then
  OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2 || true)"
fi
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
# The model has a 1M context window; Claude Code assumes 200k for unrecognized
# ids, which would compact a long draft mid-run. See senate-report-runner.sh.
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

PROMPT="${GROUND_STOP_CONCLUSION_PROMPT:-Read $SKILL and follow it exactly. Write the conclusion of the ground stop series for publication today, using future-pieces/faa-ground-stop-source-notes.md as the source: every figure from its sections 18 to 21, every archive URL from its section 21, and no fact recalled. It will be published in this run if every gate passes.}"

TODAY="${GROUND_STOP_CONCLUSION_TODAY:-$(date '+%Y-%m-%d')}"
DUE="2026-12-01"
IGNORE_GUARDS="${GROUND_STOP_CONCLUSION_IGNORE_GUARDS:-0}"

# A guard bypass is not a licence to publish. IGNORE_GUARDS exists so the
# pipeline can be exercised off its date, and it used to be the whole of the
# guard: a hand run with that one variable set went past the date check with
# publish authority intact — measured 17NOV26, when only the smoke prompt
# ("Reply with exactly SMOKE-OK. Write no file.") kept the piece off the site.
# A run the schedule did not authorise cannot reach publish_article, so the
# bypass now implies the dry run the shared tail already understands.
IGNORED_GUARD=""
if [ "$IGNORE_GUARDS" = "1" ]; then
  export REPORT_DRY_RUN=1
  IGNORED_GUARD="GUARDS IGNORED — GROUND_STOP_CONCLUSION_IGNORE_GUARDS=1 forced REPORT_DRY_RUN=1: this run cannot commit or push"
fi

# A dry run gets its own log file. The 17NOV26 pre-commit smoke wrote
# "--- ground-stop-conclusion start" and "writer finished (exit 0)" into the file
# the schedule writes, and read back afterwards that block is indistinguishable
# from the job firing. A rehearsal is not a run, and the evidence has to say
# which it was without the reader knowing the history.
if [ "${REPORT_DRY_RUN:-0}" = "1" ] || [ "${CHIEFS_DRY_RUN:-0}" = "1" ]; then
  OUT_LOG="$LOG_DIR/ground-stop-conclusion-release.smoke.out.log"
  ERR_LOG="$LOG_DIR/ground-stop-conclusion-release.smoke.err.log"
else
  OUT_LOG="$LOG_DIR/ground-stop-conclusion-release.out.log"
  ERR_LOG="$LOG_DIR/ground-stop-conclusion-release.err.log"
fi

mkdir -p "$LOG_DIR"
cd "$REPO" || { echo "$(stamp): cannot cd to $REPO" >> "$OUT_LOG"; exit 1; }

if [ "$IGNORE_GUARDS" != "1" ] && [ "$TODAY" != "$DUE" ]; then
  log "not $DUE (clock says $TODAY); nothing to write"
  exit 0
fi
if [ -n "$IGNORED_GUARD" ]; then
  log "$IGNORED_GUARD"
fi

ARTICLE="content/posts/essays/ground-stop-conclusion.md"
JOB="ground-stop-conclusion"

# The tail must be sourced with JOB bound: publish_article expands it, and under
# `set -u` an unbound expansion dies at the SESSION_STATE line.
. "$REPO/scripts/publish-report.sh"

if report_dry_run; then
  log "--- $JOB start (DRY RUN — nothing will be committed or pushed)"
else
  log "--- $JOB start"
fi

if [ ! -f "$PACK" ]; then
  log "missing $PACK, aborting"
  alert 3 "the source pack is missing; nothing to write from"
  exit 3
fi
if ! grep -q '^## 21\. ' "$PACK"; then
  log "the pack has no §21 citation list, aborting"
  alert 3 "the pack has no verified citation list; run the collector first"
  exit 3
fi

# The citations the writer is told to copy must open, or the piece ships dead
# links. Run before the writer, so a stale snapshot costs a log line instead of
# an hour of drafting.
if ! python3 "$REPO/scripts/faa-ground-stop-pack.py" --audit >> "$OUT_LOG" 2>> "$ERR_LOG"; then
  log "citation audit failed, aborting before the writer runs"
  alert 3 "the pack's verified citations do not open; see $OUT_LOG"
  exit 3
fi

. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

# Removes a stale file at $ARTICLE, so the post-condition is binary: the file
# exists because this run wrote it, or the run aborts for a missing file. A
# half-finished earlier run must never be published under this one's title.
publish_preflight "$ARTICLE"

set +e
# The writer reads the pack and the skill, and has web access to fetch anything
# it cites that the pack does not already carry. It gets no hugo, no git, no
# gate scripts, no SESSION_STATE: the runner owns the build, the gates, the
# entry, the commit and the push, so a result the writer could not have produced
# is never taken from the writer's summary.
# The two read-only prose checkers are granted because the skill tells the
# writer to run them, and a permission denial is silent (see CLAUDE.md).
claude -p "$PROMPT" \
  -n "ground-stop-conclusion-$TODAY" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/check-links.py*),Bash(python3 scripts/check-emdashes.py*),Bash(python3 scripts/check-prepositions.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

log "writer finished (exit $RC)"
if [ "$RC" -ne 0 ]; then
  log "writer failed, aborting"
  alert "$RC" "the writer exited $RC; see $OUT_LOG"
  exit "$RC"
fi
if [ ! -f "$ARTICLE" ]; then
  log "the writer wrote no file at $ARTICLE, aborting"
  alert 3 "no article was written; see $OUT_LOG"
  exit 3
fi

# Two builds, and both matter: the drafts build renders the file this run just
# wrote, and the production build is what the deploy will actually do.
report_build "$ARTICLE"
if [ "$BUILD_FAILED" -ne 0 ]; then
  log "build failed, aborting"
  alert 1 "the build failed; see $ERR_LOG"
  exit 1
fi

run_report_gates "$ARTICLE" --plate 163-ground-stop-conclusion

# Series-specific and outside the shared list: every archive URL in the piece
# must open as its document, and every advisory it cites must carry an archived
# copy inside the piece. The FAA's index drops a document fifteen days after the
# fact, so a live advisory URL alone becomes a dead footnote.
run_gate "ground-stop-citations" "$REPO/scripts/faa-ground-stop-pack.py" --audit --file "$ARTICLE"

if report_gates_failed; then
  log "a gate failed, aborting the publish"
  alert 4 "a gate failed; the piece is on disk and unpushed. see $OUT_LOG"
  exit 4
fi
log "all gates OK"

publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/conclusion-detail-XXXXXX")"
{
  echo "job: $JOB"
  echo "article: $ARTICLE"
  echo "written and published in the same run; gates passed"
} > "$DETAIL"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"

log "--- $JOB done (exit 0)"
exit 0
