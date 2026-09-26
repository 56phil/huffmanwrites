#!/bin/bash
# Weekly Kansas City Chiefs report runner.
# Invoked by launchd (com.huffmanwrites.chiefs-weekly-report) every Tuesday at
# 1830 CT, in season only.
#
# Philip, 2026-09-25: "New weekly report job: Every Tuesday, at 1830 CT, publish
# a comprehensive report on the Kansas City Chiefs."
#
# This is the ONLY scheduled job here that publishes without a human gate. The
# other four (Senate, docket, ninety-days, repair-plan) write `draft: true` and
# leave the file uncommitted. Philip asked for "publish" and confirmed it, so
# this runner commits, pushes, and syncs SimpleBrain on its own.
#
# What that changes about the design, and why the shape below is more defensive
# than its siblings:
#
#   1. The gates are the last thing between an unreviewed draft and production,
#      so a gate failure must ABORT the push rather than be logged alongside it.
#      In the drafting jobs a failed gate is a note for Philip; here it is the
#      only review the piece gets.
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

# ---------------------------------------------------------------------------
# Pre-run tree guard.
#
# The runner commits exactly two things: this article and SESSION_STATE.md. Two
# distinct hazards, handled differently because they are not the same hazard.
#
# **SESSION_STATE.md dirty is a refusal.** The runner inserts its entry by
# splitting that file at an anchor, so a file already carrying someone else's
# uncommitted edits would have those edits committed under this run's message
# and attributed to this job. That is someone else's work in this report's
# commit, and there is no safe way to publish around it. Refuse and alert.
#
# **The article path dirty is a clean-up, not a refusal.** A same-day re-run
# legitimately regenerates today's report in place (the skill says so), and a
# crashed earlier run leaves a stale draft at exactly this path. Either way the
# file is about to be written again, and the dangerous outcome is not "it gets
# overwritten" — it is "the writer fails, and the runner then commits a stale
# draft under this run's title". So the stale copy is removed BEFORE the writer
# runs: after that, the file either exists because this run wrote it, or it does
# not exist and the run aborts. Both are correct; neither can publish old text.
# ---------------------------------------------------------------------------
PRE_STATUS="$(git status --porcelain)"
if [ -n "$PRE_STATUS" ]; then
  echo "$(stamp): NOTE — the working tree was not clean before the run:" >> "$OUT_LOG"
  printf '%s\n' "$PRE_STATUS" >> "$OUT_LOG"
fi

if [ -n "$(git status --porcelain -- SESSION_STATE.md)" ]; then
  echo "$(stamp): REFUSING TO RUN — SESSION_STATE.md is already dirty:" >> "$OUT_LOG"
  git status --porcelain -- SESSION_STATE.md >> "$OUT_LOG"
  echo "$(stamp): its uncommitted edits would be committed under this run's message" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 \
    "SESSION_STATE.md was already dirty; see $OUT_LOG" || true
  exit 1
fi

if [ -f "$ARTICLE" ]; then
  echo "$(stamp): removing a pre-existing $ARTICLE so a stale draft cannot be published" >> "$OUT_LOG"
  rm -f "$ARTICLE"
fi

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
# Pre-publication checks on the artifact itself. This is the review the piece
# does not otherwise get. The rules live in `chiefs-report.py --validate` rather
# than in shell here because the date rule needs to parse the frontmatter's own
# offset format (`-05:00`), which macOS `date -j -f` cannot read — it accepts
# `-0500`, fails on `-05:00`, and reports the failure as usage text, so the
# shell version would have silently skipped the most important check. A function
# can also be tested; `scripts/test_gates.py` tests this one.
# ---------------------------------------------------------------------------
set +e
VALIDATE_OUT="$(python3 "$COLLECTOR" --validate "$ARTICLE" 2>&1)"
VALIDATE_RC=$?
set -e
if [ "$VALIDATE_RC" -ne 0 ]; then
  echo "$(stamp): FRONTMATTER CHECK FAILED — NOT PUBLISHING" >> "$OUT_LOG"
  printf '%s\n' "$VALIDATE_OUT" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 \
    "frontmatter check failed; see $OUT_LOG" || true
  exit 1
fi
echo "$(stamp): $VALIDATE_OUT" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# Verification builds, run here rather than by the agent. TWO builds, and the
# second is the one that matters: the production build excludes draft: true
# content, so it says nothing about a draft. Both must pass before the push.
# ---------------------------------------------------------------------------
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
    echo "$BUILD_OUT" >> "$ERR_LOG"
    BUILD_FAILED=1
  else
    echo "$(stamp): build OK [$flags]" >> "$OUT_LOG"
  fi
done
rm -rf "$DRAFTS_DEST"
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
# --file for the two ratchet gates is deliberate: they are keyed by file, and a
# brand-new file has no baseline entry, so `--check` treats it as a regression
# by construction. The per-file mode is the one that answers the real question —
# is THIS article inside the limit.
# ---------------------------------------------------------------------------
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

# `--online --titles` is the check this job specifically cannot do without, and
# it is deliberately NOT in the other runners. This is the only scheduled job
# whose output publishes unreviewed, and the failure it must not ship is a link
# that resolves to the wrong page — the repo's most dangerous error class. Two
# distinct defects were measured while building this job:
#
#   1. ESPN's bot wall answers a browser User-Agent with 202 and a ~2 KB
#      interstitial for EVERY url, live or dead. Read as 2xx that is a pass, and
#      three dead ESPN links written by the first agent run survived both a
#      whole-corpus sweep and a per-file sweep because of it. check-links.py now
#      detects the challenge and retries with no User-Agent, which makes ESPN
#      links genuinely checkable instead of falsely OK.
#   2. ESPN serves 200 for an INVENTED story id and lands on an unrelated
#      article — `.../story/_/id/99999999999/not-a-real-story` returns 200 with
#      a WNBA playoff ranking. No status code can see that; --titles compares
#      the citation's own link text against the page's <title>.
#
# DEAD links fail this (exit 1 on the gate). A title mismatch does not — it is
# printed for the log, because the comparison is a heuristic and a gate that
# fails a correct citation is worse than one that shows a human the sentence.
run_gate "check-quotes --file"       "$REPO/scripts/check-quotes.py"       --file "$ARTICLE"
run_gate "check-links --check"       "$REPO/scripts/check-links.py"        --check
run_gate "check-links --online"      "$REPO/scripts/check-links.py"        --file "$ARTICLE" --online --titles
run_gate "check-emdashes --file"     "$REPO/scripts/check-emdashes.py"     --file "$ARTICLE"
run_gate "check-prepositions --file" "$REPO/scripts/check-prepositions.py" --file "$ARTICLE"
run_gate "check-render-integrity"    "$REPO/scripts/check-render-integrity.py"
run_gate "check-gallery-pages"       "$REPO/scripts/check-gallery-pages.py"

if [ "$GATE_FAILED" -ne 0 ]; then
  echo "$(stamp): a gate failed; NOT PUBLISHING. The article is left in place for review." >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 "a content gate failed; see $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): all gates OK" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# Dry run: everything up to and including verification, then stop. This exists
# because this job publishes, so there is no safe way to exercise the pipeline
# without it. `CHIEFS_DRY_RUN=1` writes the article, runs both builds and every
# gate, and prints what WOULD be committed and pushed — then leaves the work in
# the tree for inspection and writes nothing to git or SimpleBrain.
#
# It is the mode a test run uses. A pipeline this destructive must be provable
# without being performed.
# ---------------------------------------------------------------------------
if [ "${CHIEFS_DRY_RUN:-0}" = "1" ]; then
  echo "$(stamp): DRY RUN — stopping before the commit. Nothing was published." >> "$OUT_LOG"
  echo "$(stamp): DRY RUN — would commit $ARTICLE and SESSION_STATE.md, then push." >> "$OUT_LOG"
  echo "$(stamp): DRY RUN — article left uncommitted for review: $ARTICLE" >> "$OUT_LOG"
  echo "DRY RUN complete: $ARTICLE passed both builds and all six gates; not committed."
  exit 0
fi

# ---------------------------------------------------------------------------
# SESSION_STATE entry, written by the runner from the results above.
#
# The agent is deliberately not allowed to write this: its summary cannot
# contain a gate result it was unable to produce, so an entry it authored could
# only assert. Written here, every claim in the entry is a line from this log.
#
# This is an explicit exception to the "no per-run SESSION_STATE entry" reading
# of the publish rule, and it is Philip's call (2026-09-25): the auto-publishing
# job records what it published. It is ONE entry per run, written in the same
# shape as every other entry, and it is the reason the file grows by ~25 entries
# a season rather than silently not recording a live publication at all.
# ---------------------------------------------------------------------------
WORDCOUNT="$(wc -w < "$ARTICLE" | tr -d ' ')"
WEEK_LINE="$(grep -m1 '^\*\*Answer:' "$ARTICLE" | cut -c1-300 || true)"
TITLE_LINE="$(grep -m1 '^title: ' "$ARTICLE" | sed 's/^title: *//' | tr -d '\"')"
ENTRY_FILE="$(mktemp "${TMPDIR:-/tmp}/chiefs-entry-XXXXXX")"
{
  echo ""
  echo "### Maintenance — $(date '+%B %-d, %Y') — Published the Chiefs weekly report (automated)"
  echo ""
  echo "Auto-published by \`com.huffmanwrites.chiefs-weekly-report\` (Tuesdays 18:30 CT, in season)."
  echo "- **Published** \`$ARTICLE\` — \"$TITLE_LINE\", $WORDCOUNT words whole-file. \`draft: false\`, \`featuredOnHome: true\`, the series hero plate \`103-chiefs-report\` (the same pair of images for every installment of the season)."
  if [ -n "$WEEK_LINE" ]; then
    echo "- **The week, as the piece frames it:** $WEEK_LINE"
  fi
  echo "- **Verified by the runner before the push, not claimed by the writer.** Both builds OK (\`--gc --minify\` and \`--gc --minify --buildDrafts --destination <tmp>\`); six gates OK (quotes \`--file\`, links \`--check\`, em-dashes \`--file\`, prepositions \`--file\`, render integrity, gallery pages); the frontmatter check (draft false, \`featuredOnHome\` true, no future date, the four series-hero fields present and resolving to real files, attribution present). A failure in any of those aborts the push rather than publishing anyway, which is the difference between this job and the four that file drafts."
  echo "- **Data came from \`scripts/chiefs-report.py\`**, the briefing pack the runner writes before the writer starts: the week's game with both teams' box scores and leaders, every scoring play, both injury reports, the standings and seed list, the season statistics by category, the next game with the feed's own odds and its matchup projection, and two weeks of Chiefs-tagged coverage with its URLs. The writer is not permitted to recall a score or a record. URLs are cited from the feed or from a page the run fetched; a constructed URL is the repo's most dangerous failure and this is the job where one would ship unreviewed."
  echo "- **SimpleBrain synced** in the same run: raw copy, \`wiki/articles/\` entry, Recent Highlights line, archive move, committed and pushed."
  echo ""
  echo "---"
} > "$ENTRY_FILE"

# Insert at the top of the maintenance entries — after the preamble block and
# before the first "### Maintenance" heading — which is where every other entry
# has been added. Verified by assertion rather than assumed: if the anchor moves,
# the insert fails loudly instead of appending the entry in the wrong place.
python3 - "$REPO/SESSION_STATE.md" "$ENTRY_FILE" <<'PY'
import sys, pathlib
state = pathlib.Path(sys.argv[1])
entry = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
text = state.read_text(encoding="utf-8")
anchor = "### Maintenance —"
i = text.find(anchor)
if i < 0:
    sys.exit("SESSION_STATE.md has no '### Maintenance —' anchor; refusing to guess where the entry goes")
state.write_text(text[:i] + entry.lstrip("\n") + "\n" + text[i:], encoding="utf-8")
PY
rm -f "$ENTRY_FILE"
echo "$(stamp): SESSION_STATE entry inserted" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# Publish: one commit, the article and its SESSION_STATE entry together, then
# push. No follow-up commit, per the one-commit-per-publish rule.
# ---------------------------------------------------------------------------
git add "$ARTICLE" SESSION_STATE.md
git commit -q -m "$(printf 'Publish: %s' "$TITLE_LINE")" \
  -m "Automated weekly Chiefs report (com.huffmanwrites.chiefs-weekly-report).

Data: scripts/chiefs-report.py (the briefing pack), verified by the runner
before the push — two builds and six offline gates, all of which must pass or
the run aborts. SESSION_STATE entry written by the runner from those results." \
  >> "$OUT_LOG" 2>> "$ERR_LOG"
echo "$(stamp): committed $TITLE_LINE" >> "$OUT_LOG"

set +e
git push >> "$OUT_LOG" 2>> "$ERR_LOG"
PUSH_RC=$?
set -e
if [ "$PUSH_RC" -ne 0 ]; then
  echo "$(stamp): push FAILED (exit $PUSH_RC)" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" "$PUSH_RC" "push failed; see $OUT_LOG" || true
  exit "$PUSH_RC"
fi

# Verify the push actually landed. Exit 0 from `git push` after racing another
# push does not mean this commit is on the remote, and a published report that
# never reached the remote is indistinguishable from success in the log.
git fetch -q origin main 2>> "$ERR_LOG" || true
LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse origin/main 2>/dev/null || echo none)"
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "$(stamp): push reported success but origin/main is $REMOTE, not $LOCAL" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 \
    "push did not land; origin/main is $REMOTE" || true
  exit 1
fi
echo "$(stamp): push verified — origin/main is $LOCAL" >> "$OUT_LOG"

# ---------------------------------------------------------------------------
# SimpleBrain, per the post-commit flow in CLAUDE.md. Run as a second agent
# session because the translate step is generative (the wiki entry is a
# condensation, not a copy), and then VERIFIED here rather than taken on trust:
# the wiki file must exist, the raw file must have moved to the archive, and the
# SimpleBrain tree must be clean and level with its remote.
# ---------------------------------------------------------------------------
if [ "${CHIEFS_SKIP_SIMPLEBRAIN:-0}" = "1" ]; then
  echo "$(stamp): SimpleBrain sync skipped (CHIEFS_SKIP_SIMPLEBRAIN=1)" >> "$OUT_LOG"
else
  mkdir -p "$SB/raw/content/posts/sports"
  cp "$REPO/$ARTICLE" "$SB/raw/content/posts/sports/"
  SB_PROMPT="Read $SB/translate.md and follow it, then follow the post-commit SimpleBrain flow in /Users/prh/Developer/huffmanwrites/CLAUDE.md. The raw file is $SB/raw/content/posts/sports/chiefs-report-$TODAY.md. Write the translated entry to $SB/wiki/articles/chiefs-report-$TODAY.md, add a [[articles/chiefs-report-$TODAY|Title]] line to the Recent Highlights section of $SB/wiki/index.md (prune the oldest highlight if the list grows past 7), move the raw file to $SB/archive/, then commit the SimpleBrain repo. Do not push; the runner pushes."
  set +e
  claude -p "$SB_PROMPT" \
    -n "chiefs-simplebrain-$TODAY" \
    --permission-mode acceptEdits \
    --add-dir "$SB" \
    --allowedTools "Read,Write,Edit,Glob,Grep,Bash(mkdir *),Bash(mv *),Bash(git -C $SB *),Bash(diff *),Bash(cmp *)" \
    >> "$OUT_LOG" 2>> "$ERR_LOG"
  SB_RC=$?
  set -e
  echo "$(stamp): SimpleBrain translate finished (exit $SB_RC)" >> "$OUT_LOG"

  SB_FAIL=0
  [ -f "$SB/wiki/articles/chiefs-report-$TODAY.md" ] || { echo "$(stamp): SimpleBrain FAILED — no wiki entry written" >> "$OUT_LOG"; SB_FAIL=1; }
  [ -f "$SB/raw/content/posts/sports/chiefs-report-$TODAY.md" ] \
    && { echo "$(stamp): SimpleBrain FAILED — the raw file is still in raw/" >> "$OUT_LOG"; SB_FAIL=1; }
  [ -f "$SB/archive/chiefs-report-$TODAY.md" ] || { echo "$(stamp): SimpleBrain FAILED — no archived raw copy" >> "$OUT_LOG"; SB_FAIL=1; }
  grep -q "articles/chiefs-report-$TODAY" "$SB/wiki/index.md" \
    || { echo "$(stamp): SimpleBrain FAILED — no Recent Highlights line" >> "$OUT_LOG"; SB_FAIL=1; }
  if [ -n "$(git -C "$SB" status --porcelain)" ]; then
    echo "$(stamp): SimpleBrain FAILED — uncommitted changes left behind:" >> "$OUT_LOG"
    git -C "$SB" status --porcelain >> "$OUT_LOG"
    SB_FAIL=1
  fi

  if [ "$SB_FAIL" -eq 0 ]; then
    set +e
    git -C "$SB" push >> "$OUT_LOG" 2>> "$ERR_LOG"
    SB_PUSH_RC=$?
    set -e
    if [ "$SB_PUSH_RC" -ne 0 ]; then
      echo "$(stamp): SimpleBrain push failed (exit $SB_PUSH_RC)" >> "$OUT_LOG"
      SB_FAIL=1
    else
      echo "$(stamp): SimpleBrain pushed" >> "$OUT_LOG"
    fi
  fi

  # A SimpleBrain failure does NOT fail the site publish: the article is already
  # live and correct, and this is the secondary mirror. It is alerted so it is
  # visible rather than silent.
  if [ "$SB_FAIL" -ne 0 ]; then
    echo "$(stamp): SimpleBrain sync incomplete — the site publish stands" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "chiefs-weekly-report" 1 \
      "SimpleBrain sync incomplete; the site publish succeeded. See $OUT_LOG" || true
  fi
fi

echo "$(stamp): run finished (exit 0)" >> "$OUT_LOG"
exit 0
