#!/bin/bash
# Shared publish tail for the scheduled weekly report jobs.
#
# SOURCED, not executed: `. "$REPO/scripts/publish-report.sh"`.
#
# Why this exists as a library. Three jobs now publish unattended (Senate,
# docket, Chiefs — Philip, 2026-09-27: "publish weekly reports that have an exit
# code of 0 after passing all gates"). The Chiefs runner had already solved this
# and its comments record why each part is shaped the way it is. Copying that
# shape into two more runners would give three places to drift, and drift of
# exactly this kind has already shipped once: the `featuredOnHome` requirement
# lived in one skill and not another, and five Senate reports published without
# reaching the home feed. So the tail lives here, once, and each runner supplies
# only what is genuinely specific to its series.
#
# What the caller must have set before sourcing:
#   REPO      absolute path to the huffmanwrites checkout
#   OUT_LOG   append-only run log
#   ERR_LOG   append-only error log
#   JOB       the launchd label suffix, e.g. senate-report
# and must define `stamp()` (the library defines it if missing).
#
# Everything below assumes `set -euo pipefail` in the caller and is written to
# survive it: every command that may legitimately fail is guarded, and no
# function changes the caller's exit status on a path that is not a failure.
#
# Dry run. `REPORT_DRY_RUN=1` runs everything up to and including verification and
# then stops without touching git or SimpleBrain. A pipeline that publishes
# unreviewed must be provable without being performed, and with three jobs now
# on this path the switch is generic rather than one job's private flag.
# `REPORT_SKIP_SIMPLEBRAIN=1` skips only the mirror. The Chiefs runner maps its
# historical CHIEFS_* names onto these so its documented behaviour is unchanged.

if ! declare -f stamp >/dev/null 2>&1; then
  stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
fi

# Accept either the generic switch or the job's historical name.
report_dry_run() { [ "${REPORT_DRY_RUN:-0}" = "1" ] || [ "${CHIEFS_DRY_RUN:-0}" = "1" ]; }
report_skip_simplebrain() { [ "${REPORT_SKIP_SIMPLEBRAIN:-0}" = "1" ] || [ "${CHIEFS_SKIP_SIMPLEBRAIN:-0}" = "1" ]; }

# ---------------------------------------------------------------------------
# Pre-run tree guard. Must be called BEFORE the writer runs.
#
# The runner commits exactly two things: the article and SESSION_STATE.md. Two
# distinct hazards, handled differently because they are not the same hazard.
#
# **SESSION_STATE.md dirty is a refusal.** The runner inserts its entry by
# splitting that file at an anchor, so a file already carrying someone else's
# uncommitted edits would have those edits committed under this run's message
# and attributed to this job. That is someone else's work in this report's
# commit, and there is no safe way to publish around it. Refuse and alert.
#
# **The article path dirty is a clean-up, not a refusal.** A same-day re-run
# legitimately regenerates today's report in place, and a crashed earlier run
# leaves a stale file at exactly this path. Either way the file is about to be
# written again, and the dangerous outcome is not "it gets overwritten" — it is
# "the writer fails, and the runner then commits a stale draft under this run's
# title". So the stale copy is removed BEFORE the writer runs: after that the
# file either exists because this run wrote it, or it does not exist and the run
# aborts. Both are correct; neither can publish old text.
# ---------------------------------------------------------------------------
publish_preflight() {
  local article="$1"
  local pre_status
  pre_status="$(git status --porcelain)"
  if [ -n "$pre_status" ]; then
    echo "$(stamp): NOTE — the working tree was not clean before the run:" >> "$OUT_LOG"
    printf '%s\n' "$pre_status" >> "$OUT_LOG"
  fi

  if [ -n "$(git status --porcelain -- SESSION_STATE.md)" ]; then
    echo "$(stamp): REFUSING TO RUN — SESSION_STATE.md is already dirty:" >> "$OUT_LOG"
    git status --porcelain -- SESSION_STATE.md >> "$OUT_LOG"
    echo "$(stamp): its uncommitted edits would be committed under this run's message" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
      "SESSION_STATE.md was already dirty; see $OUT_LOG" || true
    exit 1
  fi

  if [ -f "$article" ]; then
    echo "$(stamp): removing a pre-existing $article so a stale draft cannot be published" >> "$OUT_LOG"
    rm -f "$article"
  fi
}

# ---------------------------------------------------------------------------
# Write the SESSION_STATE entry, commit the article and the entry together, push,
# and verify the push landed.
#
# The entry is written HERE, from the real gate results, and never by the agent.
# The agent cannot run the gates (they are deliberately outside its allow-list),
# so an entry it authored could only assert a result it did not produce. Every
# claim in the entry below is a line from this log.
#
# `$3` is a file of extra `- **…**` bullet lines specific to the series; the
# standard frame is written once here rather than three times.
#
# The push is verified rather than assumed: `git push` exiting 0 after racing
# another push does not mean the commit landed, and a report that was written,
# committed, and never delivered looks exactly like success in the log.
# ---------------------------------------------------------------------------
publish_article() {
  local article="$1" title="$2" detail_file="$3"
  local wordcount entry_file

  wordcount="$(wc -w < "$article" | tr -d ' ')"
  entry_file="$(mktemp "${TMPDIR:-/tmp}/report-entry-XXXXXX")"
  {
    echo ""
    echo "### Maintenance — $(date '+%B %-d, %Y') — Published the ${JOB} report (automated)"
    echo ""
    echo "Auto-published by \`com.huffmanwrites.${JOB}\` after every gate passed."
    echo "- **Published** \`$article\` — \"$title\", $wordcount words whole-file. \`draft: false\`, \`featuredOnHome: true\`, the series hero plate."
    if [ -s "$detail_file" ]; then
      cat "$detail_file"
    fi
    echo "- **Verified by the runner before the push, not claimed by the writer.** Two builds OK (\`--gc --minify\` for what deploys, and \`--gc --minify --buildDrafts --destination <tmp>\` for the file just written — the production build excludes \`draft: true\` and so cannot see it); every gate OK, including the online link sweep (\`check-links.py --online --titles\`, which fetches each cited URL and compares the page title against the citation's own link text) and the frontmatter gate that requires \`draft: false\` and \`featuredOnHome: true\`. A failure in any of those aborts the push rather than publishing anyway."
    echo "- **SimpleBrain synced** in the same run: raw copy, \`wiki/articles/\` entry, Recent Highlights line, archive move, committed and pushed."
    echo ""
    echo "---"
  } > "$entry_file"

  # Insert at the top of the maintenance entries — after the preamble block and
  # before the first "### Maintenance" heading. Verified by assertion rather than
  # assumed: if the anchor moves, the insert fails loudly instead of writing the
  # entry in the wrong place.
  python3 - "$REPO/SESSION_STATE.md" "$entry_file" <<'PY'
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
  rm -f "$entry_file"
  echo "$(stamp): SESSION_STATE entry inserted" >> "$OUT_LOG"

  # One commit, the article and its entry together. No follow-up commit, per the
  # one-commit-per-publish rule. `git add -A` is deliberately not used: a writer
  # that wandered outside its brief must not get the result into a published
  # commit.
  if ! git add "$article" SESSION_STATE.md; then
    echo "$(stamp): git add failed; nothing was committed" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 "git add failed; see $OUT_LOG" || true
    exit 1
  fi
  if ! git commit -q -m "Publish: $title" \
      -m "Automated weekly report (com.huffmanwrites.$JOB).

Verified by the runner before the push: two builds and every content gate, all
of which must pass or the run aborts. SESSION_STATE entry written by the runner
from those results." >> "$OUT_LOG" 2>> "$ERR_LOG"; then
    echo "$(stamp): git commit failed; nothing was pushed" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 "git commit failed; see $ERR_LOG" || true
    exit 1
  fi
  echo "$(stamp): committed $title" >> "$OUT_LOG"

  local push_rc=0
  git push >> "$OUT_LOG" 2>> "$ERR_LOG" || push_rc=$?
  if [ "$push_rc" -ne 0 ]; then
    echo "$(stamp): push FAILED (exit $push_rc)" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" "$push_rc" "push failed; see $OUT_LOG" || true
    exit "$push_rc"
  fi

  git fetch -q origin main 2>> "$ERR_LOG" || true
  local local_sha remote_sha
  local_sha="$(git rev-parse HEAD)"
  remote_sha="$(git rev-parse origin/main 2>/dev/null || echo none)"
  if [ "$local_sha" != "$remote_sha" ]; then
    echo "$(stamp): push reported success but origin/main is $remote_sha, not $local_sha" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
      "push did not land; origin/main is $remote_sha" || true
    exit 1
  fi
  echo "$(stamp): push verified — origin/main is $local_sha" >> "$OUT_LOG"
}

# ---------------------------------------------------------------------------
# SimpleBrain mirror, per the post-commit flow in CLAUDE.md. Run as a second
# agent session because the translate step is generative (the wiki entry is a
# condensation, not a copy), and then VERIFIED here rather than taken on trust:
# the wiki file must exist, the raw file must have moved to the archive, the
# highlights line must be present, and the tree must be clean and level with its
# remote.
#
# $1 article (path relative to REPO) · $2 SimpleBrain root
# $3 content subdir under the section root (e.g. essays, sports)
#
# A SimpleBrain failure does NOT fail the site publish: the article is already
# live and correct, and this is the secondary mirror. It is alerted so it is
# visible rather than silent.
# ---------------------------------------------------------------------------
publish_simplebrain() {
  local article="$1" sb="$2" subdir="$3"
  local slug sb_rc sb_fail=0

  slug="$(basename "$article" .md)"

  if report_skip_simplebrain; then
    echo "$(stamp): SimpleBrain sync skipped (REPORT_SKIP_SIMPLEBRAIN=1)" >> "$OUT_LOG"
    return 0
  fi

  mkdir -p "$sb/raw/content/posts/$subdir"
  cp "$REPO/$article" "$sb/raw/content/posts/$subdir/"

  local sb_prompt
  sb_prompt="Read $sb/translate.md and follow it, then follow the post-commit SimpleBrain flow in $REPO/CLAUDE.md. The raw file is $sb/raw/content/posts/$subdir/$slug.md. Write the translated entry to $sb/wiki/articles/$slug.md, add a [$slug](articles/$slug.md) line to the Recent Highlights section of $sb/wiki/index.md (prune the oldest highlight if the list grows past 7), move the raw file to $sb/archive/, then commit the SimpleBrain repo. Do not push; the runner pushes."
  sb_rc=0
  claude -p "$sb_prompt" \
    -n "$JOB-simplebrain-$(date '+%Y-%m-%d')" \
    --permission-mode acceptEdits \
    --add-dir "$sb" \
    --allowedTools "Read,Write,Edit,Glob,Grep,Bash(mkdir *),Bash(mv *),Bash(git -C $sb *),Bash(diff *),Bash(cmp *)" \
    >> "$OUT_LOG" 2>> "$ERR_LOG" || sb_rc=$?
  echo "$(stamp): SimpleBrain translate finished (exit $sb_rc)" >> "$OUT_LOG"

  [ -f "$sb/wiki/articles/$slug.md" ] \
    || { echo "$(stamp): SimpleBrain FAILED — no wiki entry written" >> "$OUT_LOG"; sb_fail=1; }
  [ -f "$sb/raw/content/posts/$subdir/$slug.md" ] \
    && { echo "$(stamp): SimpleBrain FAILED — the raw file is still in raw/" >> "$OUT_LOG"; sb_fail=1; }
  [ -f "$sb/archive/$slug.md" ] \
    || { echo "$(stamp): SimpleBrain FAILED — no archived raw copy" >> "$OUT_LOG"; sb_fail=1; }
  grep -q "articles/$slug" "$sb/wiki/index.md" \
    || { echo "$(stamp): SimpleBrain FAILED — no Recent Highlights line" >> "$OUT_LOG"; sb_fail=1; }
  if [ -n "$(git -C "$sb" status --porcelain)" ]; then
    echo "$(stamp): SimpleBrain FAILED — uncommitted changes left behind:" >> "$OUT_LOG"
    git -C "$sb" status --porcelain >> "$OUT_LOG"
    sb_fail=1
  fi

  if [ "$sb_fail" -eq 0 ]; then
    local sb_push_rc=0
    git -C "$sb" push >> "$OUT_LOG" 2>> "$ERR_LOG" || sb_push_rc=$?
    if [ "$sb_push_rc" -ne 0 ]; then
      echo "$(stamp): SimpleBrain push failed (exit $sb_push_rc)" >> "$OUT_LOG"
      sb_fail=1
    else
      echo "$(stamp): SimpleBrain pushed" >> "$OUT_LOG"
    fi
  fi

  if [ "$sb_fail" -ne 0 ]; then
    echo "$(stamp): SimpleBrain sync incomplete — the site publish stands" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
      "SimpleBrain sync incomplete; the site publish succeeded. See $OUT_LOG" || true
  fi
  return 0
}

# ---------------------------------------------------------------------------
# The dry-run stop. Called after verification and before publish_article, so a
# dry run exercises everything except the parts that touch git.
# ---------------------------------------------------------------------------
publish_dry_run_stop() {
  local article="$1"
  if ! report_dry_run; then
    return 1
  fi
  echo "$(stamp): DRY RUN — stopping before the commit. Nothing was published." >> "$OUT_LOG"
  echo "$(stamp): DRY RUN — would commit $article and SESSION_STATE.md, then push." >> "$OUT_LOG"
  echo "$(stamp): DRY RUN — article left uncommitted for review: $article" >> "$OUT_LOG"
  echo "DRY RUN complete: $article passed both builds and every gate; not committed."
  return 0
}
