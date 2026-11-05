#!/bin/bash
# Musk money report runner. ONE OFF, Sunday 2026-12-06 10:00 CT.
# Invoked by launchd (com.huffmanwrites.musk-money-report).
#
# Philip, 2026-11-05: "Add the job. Schedule it for 1000 06DEC."
#
# The piece is the definitive accounting the brief in
# future-pieces/musk-midterm-spending.md was written to wait for: how much the
# 2026 cycle's money from Elon Musk actually came to, what it bought, and what
# the filings show about who sent it. December 3 is the first day a committee
# total exists (the Post-General report covers 10/15 to 11/23 and is due then),
# and December 6 is the Sunday inside the brief's recommended December 4 to 12
# window.
#
# PUBLISHES. The gates are the only review this piece gets, so a gate or build
# failure ABORTS the push rather than being logged beside it.
#
# Two things are specific to this job and neither is optional:
#
#   1. The collector runs HERE, before the writer, and the writer may not recall
#      a figure. `scripts/fec-spending-pack.py` reads the FEC's own API; the
#      writer reads the pack. That is the same rule the SITREP and the Chiefs
#      report live under, and it matters more here: every number in this piece
#      is a claim about a named person's money.
#   2. The Post-General filing is a hard prerequisite, not a hope. If no `30G`
#      report is in the API, the piece's premise does not exist yet and the run
#      aborts with an alert rather than publishing a total assembled from press
#      tallies. Exit 3, which is a failure the reader must see, not exit 0.
set -euo pipefail

# launchd does not source the shell, so PATH misses ~/.local/bin (claude) and
# /opt/homebrew/bin (hugo). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded path names a missing file.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$REPO/skills/musk-money-report.md"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/musk-money-report.out.log"
ERR_LOG="$LOG_DIR/musk-money-report.err.log"
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Provider routing: Ollama serves Anthropic-format requests at /v1/messages, so
# ANTHROPIC_BASE_URL must NOT carry a /v1 suffix. Policy (Philip, 2026-09-06): no
# Anthropic or OpenAI resources.
OLLAMA_KEY="$(security find-generic-password -a "$USER" -s huffmanwrites-ollama -w 2>/dev/null)"
[ -z "$OLLAMA_KEY" ] && OLLAMA_KEY="$(grep -oE 'OLLAMA_API_KEY="[^"]+"' "$HOME/.secrets" 2>/dev/null | head -1 | cut -d'"' -f2)"
export ANTHROPIC_API_KEY="${OLLAMA_KEY:-}"
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_MODEL="deepseek-v4.1-flash:cloud"
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1048576

# The one date this job is for. launchd has no `Year` key, so its dict fires on
# December 6 every year; this guard is what makes the job one-off, and it exits 0
# because a job that alerts every December 6 forever is a job whose alerts get
# ignored.
REPORT_DATE="2026-12-06"
TODAY="$(date '+%Y-%m-%d')"
if [ "$TODAY" != "$REPORT_DATE" ] && [ "${MUSK_MONEY_IGNORE_DATE_GUARD:-0}" != "1" ]; then
  echo "$(stamp): not the report date (wanted $REPORT_DATE, today is $TODAY); nothing to do" >> "$OUT_LOG"
  exit 0
fi
# Override for exercising the pipeline before the date. Pair it with
# REPORT_DRY_RUN=1, which stops before the commit: this job publishes
# unreviewed, so its build-and-gate tail should not first run in production.
[ "${MUSK_MONEY_IGNORE_DATE_GUARD:-0}" = "1" ] && \
  echo "$(stamp): date guard overridden (MUSK_MONEY_IGNORE_DATE_GUARD=1)" >> "$OUT_LOG"

cd "$REPO"

# Bound before anything uses it: the preflight guard, the gates and the commit
# all read it, and under `set -u` an unbound expansion is a hard failure.
ARTICLE="content/posts/civics/the-musk-money.md"

# JOB must be bound before the source: the library expands it inside
# publish_article and in every alert, and the first real publish is where an
# unbound one dies.
JOB="musk-money-report"
. "$REPO/scripts/publish-report.sh"

. "$REPO/scripts/ollama-probe.sh"
ollama_require "$JOB" "$OUT_LOG" || exit 1

echo "$(stamp): starting musk money run" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# 1. The collector. Before the writer, always, and its exit code decides.
#
# `fec-spending-pack.py` prints identity, Form 3X summary filings, Musk's
# itemized Schedule A receipts and Schedule E totals per committee, with
# SOURCE UNAVAILABLE for a failed source and a coverage line. A pack that read
# nothing must not become a piece.
# ---------------------------------------------------------------------------
# The pack is written per run to a dated path, never into the repo: it is a
# working file the writer reads, not source. Re-running collects it again, which
# is correct — a pack describes one filing state, and reusing a stale one would
# put yesterday's numbers in today's article.
PACK="${TMPDIR:-/tmp}/musk-money-pack-$REPORT_DATE.txt"
set +e
python3 "$REPO/scripts/fec-spending-pack.py" > "$PACK" 2>> "$ERR_LOG"
PACK_RC=$?
set -e
echo "$(stamp): collector finished (exit $PACK_RC), pack at $PACK" >> "$OUT_LOG"

if [ "$PACK_RC" -ne 0 ] || [ ! -s "$PACK" ]; then
  echo "$(stamp): collector failed (exit $PACK_RC); aborting without a writer" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "FEC pack failed (exit $PACK_RC) on $REPORT_DATE; no piece"
  exit 1
fi

# The Post-General report is the whole reason for the date: report type `30G`,
# covering 10/15 through 11/23, due 2026-12-03. Absent it there is no cycle total
# and the piece would have to fall back on press tallies, which is the failure the
# brief was written to avoid.
if ! grep -Eq '(^|[[:space:]])30G([[:space:]]|$)' "$PACK"; then
  echo "$(stamp): no 30G (Post-General) filing in the pack; the cycle total does not exist yet" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 3 "no Post-General 30G filing in the API on $REPORT_DATE; re-run when it lands"
  exit 3
fi

# The itemization status is recorded rather than assumed: Texas PAC's $158m Q3
# receipt had a zero-row Schedule A on 2026-11-05, and whether the Post-General
# report names the payer is the single fact that decides what the piece may say.
if grep -Eq 'Musk receipts: 0 itemized rows' "$PACK"; then
  ITEMIZATION="still no itemized Musk receipt on at least one committee"
else
  ITEMIZATION="every watched committee carries itemized Musk receipts"
fi
echo "$(stamp): $ITEMIZATION" >> "$OUT_LOG"

# The stale-file guard: after this the article either exists because this run
# wrote it, or the run aborts. Never publishes an old draft under this title.
publish_preflight "$ARTICLE"

# ---------------------------------------------------------------------------
# 2. The writer. Narrow allow-list: the pack, the skill, one article file.
# No git, no hugo, no SESSION_STATE.md, because the runner owns all three.
# The two prose checkers ARE granted, so the writer can fix its own draft before
# finishing; a permission denial is silent, which is how three publishing runs
# once aborted on a stranded preposition and cost a manual recovery each time.
# ---------------------------------------------------------------------------
# Override for a smoke test: MUSK_MONEY_PROMPT="Reply with exactly: SMOKE-OK"
PROMPT="${MUSK_MONEY_PROMPT:-Read $SKILL and follow it exactly. The collector pack for this run is at $PACK and every figure must come from it; you may not recall one. Write the article to $ARTICLE. It will be published on this run if every gate passes.}"

set +e
claude -p "$PROMPT" \
  -n "musk-money-$(date '+%Y-%m-%d')" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Bash(date *),Bash(mkdir *),Bash(python3 scripts/check-emdashes.py*),Bash(python3 scripts/check-prepositions.py*)" \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): writer finished (exit $RC)" >> "$OUT_LOG"

if [ "$RC" -ne 0 ]; then
  echo "$(stamp): writer failed (exit $RC); aborting" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" "$RC" "writer failed; no piece published"
  exit "$RC"
fi

if [ ! -f "$ARTICLE" ]; then
  echo "$(stamp): writer produced no file at $ARTICLE; aborting" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "writer exited 0 but wrote no article"
  exit 1
fi

# ---------------------------------------------------------------------------
# 3. Verification, run here rather than taken from the writer's summary. TWO
# builds: the production build is what the deploy does, and the drafts build
# renders the file this run just wrote.
# ---------------------------------------------------------------------------
report_build "$ARTICLE"
run_report_gates "$ARTICLE" --plate 152-musk-money

if [ "$BUILD_FAILED" -ne 0 ] || report_gates_failed; then
  echo "$(stamp): verification failed (build=$BUILD_FAILED); aborting the push" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "gates or build failed; piece not published"
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# Dry run: everything up to and including verification, then stop before git.
publish_dry_run_stop "$ARTICLE" && exit 0

DETAIL="$(mktemp "${TMPDIR:-/tmp}/musk-money-detail-XXXXXX")"
{
  echo "- **Collected by \`scripts/fec-spending-pack.py\`** before the writer ran (exit $PACK_RC). Every figure in the piece came from the FEC API, not from press tallies."
  echo "- **The Post-General \`30G\` filing was present** in the pack, which is the date rule: the cycle total does not exist until it lands."
  echo "- **Itemization at publish:** $ITEMIZATION."
} > "$DETAIL"

TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '"')"
publish_article "$ARTICLE" "$TITLE_LINE" "$DETAIL"
rm -f "$DETAIL"
publish_simplebrain "$ARTICLE" "/Users/prh/Developer/SimpleBrain" "civics"

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
