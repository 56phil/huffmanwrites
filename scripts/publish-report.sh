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

# The caller MUST have bound JOB before sourcing. The library expands it inside
# publish_article (the SESSION_STATE entry, the commit message) and in every
# alert-failure.sh call, all under the caller's `set -u`. Naming it here turns an
# unbound JOB into a sentence about the contract instead of the cryptic
# "publish-report.sh: line 250: JOB: unbound variable" the docket and senate
# runners produced on their first real publish (2026-10-03) — a failure that
# happens only when the pipeline runs to completion, after the writer and every
# gate have already succeeded, so a dry run can never surface it.
: "${JOB:?publish-report.sh requires JOB (the launchd label suffix) to be set by the caller}"

# Accept either the generic switch or the job's historical name.
report_dry_run() { [ "${REPORT_DRY_RUN:-0}" = "1" ] || [ "${CHIEFS_DRY_RUN:-0}" = "1" ]; }
report_skip_simplebrain() { [ "${REPORT_SKIP_SIMPLEBRAIN:-0}" = "1" ] || [ "${CHIEFS_SKIP_SIMPLEBRAIN:-0}" = "1" ]; }

# ---------------------------------------------------------------------------
# The content gate list, in ONE place.
#
# This moved here from the three runners because the gate sets had already
# drifted. The ninety-days runner ran only the offline link check and the four
# prose gates, so when its run added two gallery cards across a page boundary
# with no page stub on 2026-10-01, `check-gallery-pages` — which would have
# caught the 404 before a deploy — was not in its list and the defect was
# invisible to the job that caused it. A gate nobody runs is a gate that does
# not exist, and three copies of a list is how the featuredOnHome rule came to
# live in one skill and not another.
#
# `run_report_gates <article> [--plate <basename>] [--published]`
#
#   default (no --published)  the set for a series that PUBLISHES (Senate,
#                             docket, Chiefs). Includes the online link sweep
#                             with --titles, the frontmatter gate, the
#                             corpus-wide hero check, the render check, the
#                             gallery check, and the series-post check.
#   --published               force the publishing set (currently the default).
#   --plate <basename>        pin the series hero plate (e.g. 105-senate-race-report).
#
# The ninety-days job is a DRAFTING job whose pieces are not a declared series,
# so it does not call this; it runs the prose and link gates on the whole corpus
# via report_gate() instead (see its runner). A series that later publishes can
# adopt this function unchanged.
#
# A gate failure sets GATE_FAILED=1; the caller decides what that costs (abort
# the push in a publishing job).
# ---------------------------------------------------------------------------
GATE_FAILED=0
run_gate() {
  local label="$1"; shift
  local out rc
  set +e
  out="$(python3 "$@" 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    echo "$(stamp): gate FAILED [$label] (exit $rc)" >> "$OUT_LOG"
    printf '%s\n' "$out" >> "$ERR_LOG"
    GATE_FAILED=1
  else
    echo "$(stamp): gate OK [$label]" >> "$OUT_LOG"
  fi
}

run_report_gates() {
  local article="$1"; shift
  local plate="" want_published=1
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --plate) plate="$2"; shift 2 ;;
      --draft) want_published=0; shift ;;
      *) shift ;;
    esac
  done
  GATE_FAILED=0

  # The frontmatter gate reads the artifact the way a publisher does. `draft:
  # true` left in place is the failure that matters most: commit and push would
  # succeed, every other gate would report OK, and the deploy would carry
  # nothing. `--hero-plate` pins the series plate, which the skill says to copy
  # verbatim — this is what makes "verbatim" checkable rather than trusted.
  #
  # `check-content-frontmatter.py` then reads EVERY content file, the same way
  # `check-hero-paths` below does: `lastmod` on the post being published, and the
  # fields the book pages depend on. It runs in CI, which is too late for a
  # runner: a job that omits `lastmod` would commit, push, report every gate
  # green, and fail the DEPLOY — the article is on `main` and the site does not
  # carry it. Added 2026-10-08, the day the corpus-wide gate was written.
  if [ "$want_published" -eq 1 ]; then
    if [ -n "$plate" ]; then
      run_gate "check-report-frontmatter" "$REPO/scripts/check-report-frontmatter.py" \
        --file "$article" --hero-plate "$plate"
    else
      run_gate "check-report-frontmatter" "$REPO/scripts/check-report-frontmatter.py" \
        --file "$article"
    fi
    run_gate "check-content-frontmatter" "$REPO/scripts/check-content-frontmatter.py"
  fi

  run_gate "check-quotes --file"     "$REPO/scripts/check-quotes.py"       --file "$article"
  # The NARROW half of quotation fidelity. `check-quotes.py --online` is inert on
  # a report: it audits epigraph-shaped attributions (`"quote" — Author`) and a
  # newspaper footnote is not that shape, so it scans this article as "0
  # attributions" and verifies nothing. This gate checks the one thing that is
  # both checkable and was actually wrong — a quoted person-name DETAIL (middle
  # initial or generational suffix) that does not appear on any page the line
  # cites. The 2026-10-04 report quoted "Daniel J. Sullivan Jr." where the source
  # says "Daniel J. Sullivan"; every other gate reported OK. A general
  # every-quotation check was tried and rejected: it reported 70 false positives
  # on that same report (titles, ellipses, paywalled pages), and a gate that
  # fails correct reports is worse than none.
  run_gate "check-quote-names --online" "$REPO/scripts/check-quote-names.py" --file "$article" --online
  run_gate "check-links --check"     "$REPO/scripts/check-links.py"        --check
  # `--online --titles` is not optional for a publishing job. It fetches every
  # URL the report cites and compares the page's own <title> against the
  # citation's link text — the ONLY check in this repo that catches a link
  # resolving to the wrong page, CLAUDE.md's most dangerous failure, invisible
  # to a status code because the URL returns 200. A corpus sweep cannot see a
  # brand-new file, so it must run here, scoped with --file. DEAD links fail
  # this; a title mismatch is printed for the log and does not, because the
  # comparison is a heuristic and failing a correct citation is worse.
  run_gate "check-links --online"    "$REPO/scripts/check-links.py"        --file "$article" --online --titles
  run_gate "check-emdashes --file"   "$REPO/scripts/check-emdashes.py"     --file "$article"
  run_gate "check-prepositions --file" "$REPO/scripts/check-prepositions.py" --file "$article"
  # Corpus-wide hero check: the frontmatter gate reads this article's own paths,
  # and this reads every hero in content/, so a path already broken elsewhere
  # cannot ride along into a deploy.
  run_gate "check-hero-paths"        "$REPO/scripts/check-hero-paths.py"
  run_gate "check-render-integrity"  "$REPO/scripts/check-render-integrity.py"
  # NOTE: the corpus entries below are the deterministic set. The ONLINE corpus
  # set — the one only the weekly job can run — lives once in
  # `scripts/corpus-gates.sh`, and `test_gates.py` asserts that job runs it and
  # that no gate is orphaned. A gate added here but not there (or the reverse)
  # is how `check-quote-names.py` guarded the publishing path for four days and
  # nothing else.
  # A new gallery card can cross a page boundary and leave every gallery link to
  # that page pointing at a 404. This is the gate the ninety-days run lacked.
  run_gate "check-gallery-pages"     "$REPO/scripts/check-gallery-pages.py"
  # A published installment of a series must carry `featuredOnHome: true`, or it
  # reaches no reader from the home page: the feed takes its five Recent Posts
  # from flagged posts only, and more than five are already flagged.
  run_gate "check-series-posts"      "$REPO/scripts/check-series-posts.py" --file "$article"
}
report_gates_failed() { [ "$GATE_FAILED" -ne 0 ]; }

# The two verification builds every report job runs. TWO, and both matters: the
# production build excludes `draft: true`, so it says nothing about the file a
# drafting job just wrote; the drafts build renders that file to a scratch
# destination (not public/, which deploys and which site-audit crawls).
# `report_build <article>` sets BUILD_FAILED.
report_build() {
  local article="$1"
  local dest
  dest="$(mktemp -d "${TMPDIR:-/tmp}/hugo-drafts-XXXXXX")"
  BUILD_FAILED=0
  echo "$(stamp): running verification builds" >> "$OUT_LOG"
  local flags out rc
  for flags in "--gc --minify" "--gc --minify --buildDrafts --destination $dest"; do
    set +e
    out="$(hugo $flags 2>&1)"
    rc=$?
    set -e
    if [ "$rc" -ne 0 ]; then
      echo "$(stamp): build FAILED [$flags] (exit $rc)" >> "$OUT_LOG"
      printf '%s\n' "$out" >> "$ERR_LOG"
      BUILD_FAILED=1
    else
      echo "$(stamp): build OK [$flags]" >> "$OUT_LOG"
    fi
  done
  rm -rf "$dest"
}

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
    # A dry run never reaches publish_article, so it never commits
    # SESSION_STATE.md and the hazard this guard exists for cannot occur.
    # Refusing anyway would make an off-date dry run (see the docket start-guard
    # override) impossible while any unrelated work sits in the tree, and a
    # pipeline that cannot be exercised is the thing the override is for.
    if report_dry_run; then
      echo "$(stamp): SESSION_STATE.md is dirty, but this is a DRY RUN — nothing will be committed." >> "$OUT_LOG"
    else
      echo "$(stamp): REFUSING TO RUN — SESSION_STATE.md is already dirty:" >> "$OUT_LOG"
      git status --porcelain -- SESSION_STATE.md >> "$OUT_LOG"
      echo "$(stamp): its uncommitted edits would be committed under this run's message" >> "$OUT_LOG"
      "$REPO/scripts/alert-failure.sh" "$JOB" 1 \
        "SESSION_STATE.md was already dirty; see $OUT_LOG" || true
      exit 1
    fi
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
# **Except the SimpleBrain line, and the exception is deliberate.** The mirror
# runs AFTER this function, because it is the last thing the runner does, so at
# the moment the entry is written the runner has not yet observed whether it
# worked. The first version of this line asserted "SimpleBrain synced … committed
# and pushed" unconditionally, which made the entry predict rather than report —
# a claim of exactly the kind this function exists to prevent, in the one place
# the reader is told to trust. It was caught on 2026-10-07 by the SimpleBrain
# agent itself, which read the entry and noted that the step it described had not
# yet run. Ordering the mirror first would let the entry report it, but that path
# cannot be exercised by a dry run and changing it would be first tested in
# production. So the line states what the runner does, names where the outcome
# is, and asserts nothing it has not seen.
#
# The delivery check (`scripts/verify-published.py`, added 2026-10-08) runs after
# this entry has been committed, for the same structural reason, and is written
# in the same shape: it states what the runner does and names the log, so the
# entry never has to be corrected to match an outcome it could not have seen.
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
    echo "- **Delivery is verified, not assumed.** After the push is confirmed the runner fetches the piece at its own URL and requires the page's own \`<title>\` to carry the article's \`title\` (\`scripts/verify-published.py\`, the rule \`sitrep-watchdog.py\` applies from the outside), retrying for a bounded window because a 404 is expected until the deploy lands. A settled absence raises the shared alert and fails the run: the article is on \`main\` and no reader has it. The outcome is in \`$OUT_LOG\`."
    echo "- **SimpleBrain mirror** runs immediately after this push: raw copy, \`wiki/articles/\` entry, Recent Highlights line, archive move, committed and pushed. The runner verifies all five and alerts if any did not happen; the outcome is in \`$OUT_LOG\`."
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
  #
  # A series that legitimately writes something besides its article names those
  # paths in PUBLISH_EXTRA_PATHS (space-separated), and they are added by name
  # here — never by wildcard, which would carry a stray file. The Chief's market
  # chart was the first, staged by its runner before this call; the docket job's
  # `scripts/check-docket.py` `known`-map growth is the second, and it MUST ride
  # along or the registry's memory is lost every week. Naming a series' asset
  # path literally in this shared file was a mistake once recorded: it would
  # have staged the Chiefs chart inside a Senate or docket publish commit. The
  # variable keeps that separation — each runner supplies its own.
  if ! git add "$article" SESSION_STATE.md ${PUBLISH_EXTRA_PATHS:-}; then
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

  # The push landed; that is not the same as delivered. `git push` reaching
  # origin says the commit is on `main` and says nothing about whether the Pages
  # workflow built it, and on 2026-10-08 three consecutive runs reached `main`
  # while no deploy landed for a day. So the piece is fetched at its OWN URL and
  # the page's own `<title>` must carry the article's title: the rule
  # scripts/sitrep-watchdog.py applies from the outside, applied here in the run
  # that published it. A 404 is expected until the deploy lands, so the checker
  # retries for a bounded window before it calls an absence settled.
  #
  # A settled absence alerts and fails the run. The article is on `main` and no
  # reader has it, which is not a log line; the mirror is skipped the way it
  # would be for any other abort in the tail. `exit "$live_rc"` keeps the
  # checker's vocabulary (1 absent, 3 unconfirmed) in the runner's exit code.
  local live_out live_rc=0
  live_out="$(python3 "$REPO/scripts/verify-published.py" --article "$article" 2>>"$ERR_LOG")" || live_rc=$?
  printf '%s\n' "$live_out" >> "$OUT_LOG"
  if [ "$live_rc" -ne 0 ]; then
    echo "$(stamp): live verification FAILED (exit $live_rc)" >> "$OUT_LOG"
    "$REPO/scripts/alert-failure.sh" "$JOB" "$live_rc" \
      "published to main but not served: ${live_out#verify-published: }" || true
    exit "$live_rc"
  fi
  echo "$(stamp): live verification OK — the site serves the article" >> "$OUT_LOG"
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
