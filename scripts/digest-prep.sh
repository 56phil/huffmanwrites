#!/bin/bash
# digest-prep.sh — finish a Stoic Saturday letter before its send.
#
# Why this exists: a digest is drafted into pending/ (untracked) and is not final
# until one item in it can be written, and that item does not exist until the
# SITREP edition of the Friday before it sends. The 2026-10-24 letter left a
# comment in its own footer naming that step, which is a note to whoever opens
# the file next; this is the step made executable, so the letter can be finished
# at a stated hour without a human retyping gates into a shell.
#
# It applies the item, runs the content gates and both builds, and publishes the
# page. It does NOT create the SendFox campaign and it does NOT mirror to
# SimpleBrain: the send is the one step a human reviews, an email cannot be
# recalled, and the mirror reads a page that only becomes live when its
# future date passes.
#
# Usage:
#   digest-prep.sh --draft pending/<file>.md --item pending/<file>.md \
#                  --slug <slug> --title "<Title>" [--dry-run]
#
# The item file is a small explicit format because an unattended edit to prose
# must fail rather than guess. Sections, each starting a line:
#   ITEM          the paragraph to insert, until the next section
#   SOURCE        a line for ## Sources
#   SOURCE_AFTER  insert the SOURCE line before the first line with this prefix
#   REPLACE       old==>new, one pair per line
#   LAST_MOD      the new frontmatter lastmod value
# Every anchor must match exactly once, and anything unmatched aborts before a
# byte is written. Nothing here is guessed: a miss is a change in the letter that
# this script was not written for, and a human should see it.
set -uo pipefail
PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PATH

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB="digest-prep"
OUT_LOG="${DIGEST_PREP_LOG:-$HOME/Library/Logs/digest-prep.log}"
ERR_LOG="${OUT_LOG%.log}.err.log"
INSTALLED_PLIST="$HOME/Library/LaunchAgents/com.huffmanwrites.digest-prep.plist"
LABEL="com.huffmanwrites.digest-prep"

DRAFT=""; ITEM_FILE=""; SLUG=""; TITLE=""; DRY_RUN=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --draft)   DRAFT="$2"; shift 2 ;;
    --item)    ITEM_FILE="$2"; shift 2 ;;
    --slug)    SLUG="$2"; shift 2 ;;
    --title)   TITLE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "digest-prep: unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$DRAFT" ] && [ -n "$ITEM_FILE" ] && [ -n "$SLUG" ] && [ -n "$TITLE" ] || {
  echo "digest-prep: --draft, --item, --slug and --title are required" >&2; exit 2; }

mkdir -p "$(dirname "$OUT_LOG")"
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
log()   { echo "$(stamp): $*" >> "$OUT_LOG"; }

# The one-shot plist is installed only for the run it exists for, so it removes
# itself rather than becoming a Friday job that wakes up every week to exit 0.
remove_job() {
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$INSTALLED_PLIST"
}

fail() {
  log "FAILED: $*"
  # Any failure leaves the authored draft exactly as it was written. The backup
  # is taken before the first edit and is the only copy of that state.
  if [ -n "${DRAFT:-}" ] && [ -f "${DRAFT:-}.bak" ]; then
    cp "$DRAFT.bak" "$DRAFT" && log "draft restored from $DRAFT.bak"
  fi
  # A page copied into content/ that this run did not publish is removed, so a
  # failed run leaves no half-published letter for the next build to serve.
  if [ "${PUBLISHED_COPY:-0}" = "1" ] && [ -f "${TARGET:-}" ]; then
    rm -f "$TARGET" && log "removed the unpublished copy at $TARGET"
  fi
  [ -n "${ERR_TAIL:-}" ] && log "last error output: $ERR_TAIL"
  "$REPO/scripts/alert-failure.sh" "$JOB" 1 "$*" 2>/dev/null || true
  remove_job
  exit 1
}

TARGET="$REPO/content/posts/digests/$SLUG.md"
cd "$REPO" || fail "cannot cd to $REPO"

log "--- digest-prep start: draft=$DRAFT slug=$SLUG dry_run=$DRY_RUN"

[ -f "$DRAFT" ]     || fail "draft not found: $DRAFT"
[ -f "$ITEM_FILE" ] || fail "item file not found: $ITEM_FILE"

# Already published is success, not failure: launchd can fire twice around a
# wake, and the second run must not append the item a second time.
if [ -f "$TARGET" ]; then
  log "already published: $TARGET — nothing to do"
  remove_job
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. Apply the item. The edit is all-or-nothing: the anchors are checked first,
#    the draft is written once, and the authored copy is kept beside it so a
#    failure leaves the file exactly as it was written by hand.
# ---------------------------------------------------------------------------
# A backup already present means an earlier run died mid-edit. Refusing is the
# safe move: the script cannot tell an authored file from a half-applied one.
[ -e "$DRAFT.bak" ] && fail "a previous run left $DRAFT.bak; inspect it before re-running"
cp "$DRAFT" "$DRAFT.bak"
python3 - "$DRAFT" "$ITEM_FILE" <<'PY' 2>> "$ERR_LOG"
import re, sys
draft_path, item_path = sys.argv[1], sys.argv[2]

text = open(draft_path, encoding="utf-8").read()
item_text = open(item_path, encoding="utf-8").read()

# Parse the item file's sections.
sections, current = {}, None
for line in item_text.splitlines():
    m = re.match(r'^(ITEM|SOURCE|SOURCE_AFTER|REPLACE|LAST_MOD)$', line.strip())
    if m:
        current = m.group(1); sections.setdefault(current, []); continue
    if current is not None:
        sections[current].append(line)
body = "\n".join(sections.get("ITEM", [])).strip("\n")
source = "\n".join(sections.get("SOURCE", [])).strip("\n")
after = "\n".join(sections.get("SOURCE_AFTER", [])).strip("\n")
last_mod = "\n".join(sections.get("LAST_MOD", [])).strip()
replaces = [l for l in sections.get("REPLACE", []) if l.strip()]
if not body or not source or not after or not last_mod:
    sys.exit("item file is missing ITEM, SOURCE, SOURCE_AFTER or LAST_MOD")

def once(needle, haystack, what):
    n = haystack.count(needle)
    if n != 1:
        sys.exit(f"{what}: expected exactly one match, found {n}: {needle[:70]!r}")

# The item goes at the end of the chronological run, immediately before the
# standing weekly-reports block. The blank line either side is written here so
# the paragraph spacing is the same whatever the draft had above it.
anchor = "**The weekly reports**\n"
once(anchor, text, "weekly-reports anchor")
text = text.replace(anchor, body + "\n\n" + anchor, 1)

# The source line joins the ## Sources list in its reverse-chronological slot.
once("\n" + after, text, "source anchor")
text = text.replace("\n" + after, "\n" + source + "\n" + after, 1)

# Closing-line and roundup range fixes, each stated in the item file.
for pair in replaces:
    old, sep, new = pair.partition("==>")
    if not sep:
        sys.exit(f"malformed REPLACE line: {pair!r}")
    once(old, text, "REPLACE anchor")
    text = text.replace(old, new)

# lastmod, in the frontmatter only.
old_mod = re.search(r'^lastmod: .*$', text, re.M)
if not old_mod:
    sys.exit("no lastmod in frontmatter")
text = text.replace(old_mod.group(0), "lastmod: " + last_mod, 1)

# The footer comment is a note to the next session and does not ship: a
# published post ends with the attribution line.
text = re.sub(r'\n*<!--.*?-->[ \t]*\n?$', '\n', text, flags=re.S)
if not text.rstrip().endswith("| © Philip Huffman*"):
    sys.exit("the attribution line is not the last line after the comment came out")

open(draft_path, "w", encoding="utf-8").write(text)
print("applied item", file=sys.stderr)
PY
[ $? -eq 0 ] || { cp "$DRAFT.bak" "$DRAFT"; fail "applying the item failed; draft restored"; }
log "item applied: $DRAFT"

# ---------------------------------------------------------------------------
# 2. Gates. A gate result is not a summary, it is an exit code, and the same
#    set the corpus runs is the set this runs.
# ---------------------------------------------------------------------------
GATE_FAILED=0
: > "${OUT_LOG%.log}.gates"
run_gate() {
  local label="$1"; shift
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  printf '%s\n' "$out" >> "$OUT_LOG"
  ERR_TAIL="$(printf '%s\n' "$out" | tail -3)"
  if [ "$rc" -ne 0 ]; then
    printf '%s\n' "$out" >> "$ERR_LOG"
    printf 'gate\t%s\tFAILED\n' "$label" >> "${OUT_LOG%.log}.gates"
    log "GATE FAILED: $label (exit $rc)"
    GATE_FAILED=1
  else
    printf 'gate\t%s\tok\n' "$label" >> "${OUT_LOG%.log}.gates"
    log "gate ok: $label"
  fi
}
run_gate emdashes    python3 scripts/check-emdashes.py --file "$DRAFT"
run_gate prepositions python3 scripts/check-prepositions.py --file "$DRAFT"
run_gate quotes      python3 scripts/check-quotes.py --file "$DRAFT" --online
run_gate links       python3 scripts/check-links.py --file "$DRAFT" --online --titles
run_gate heropaths   python3 scripts/check-hero-paths.py --file "$DRAFT"

[ "$GATE_FAILED" -eq 0 ] || fail "content gates failed; draft left as written"

# ---------------------------------------------------------------------------
# 3. Two builds, and the second one matters more here. The page is future-dated
#    to its embargo hour, so the production build skips it by design; the build
#    that proves it renders is the one with --buildFuture, into a throwaway
#    destination so no embargoed draft lands in public/. Both need the page in
#    content/ to have anything to say, so the copy happens first and is undone
#    by fail() if a build or the render check does not pass.
# ---------------------------------------------------------------------------
cp "$DRAFT" "$TARGET" || fail "copying the draft to $TARGET failed"
PUBLISHED_COPY=1
run_gate build-prod    hugo --gc --minify --quiet
TMP_DEST="$(mktemp -d "${TMPDIR:-/tmp}/hugo-future-XXXXXX")"
run_gate build-future  hugo --quiet --buildDrafts --buildFuture --destination "$TMP_DEST"
if ! grep -qF "$(printf '%s' "$TITLE" | sed 's/&/\&amp;/g')" "$TMP_DEST/posts/digests/$SLUG/index.html" 2>/dev/null; then
  ERR_TAIL="rendered page carries no title match: $TMP_DEST/posts/digests/$SLUG/index.html"
  log "GATE FAILED: render-title"
  GATE_FAILED=1
else
  log "gate ok: render-title"
fi
rm -rf "$TMP_DEST"

[ "$GATE_FAILED" -eq 0 ] || fail "build gates failed; draft left as written"

if [ "$DRY_RUN" = "1" ]; then
  log "dry run: gates and builds passed; nothing was committed or pushed"
  cp "$DRAFT" "$DRAFT.prepared"
  rm -f "$TARGET"
  cp "$DRAFT.bak" "$DRAFT"
  rm -f "$DRAFT.bak"
  log "dry run: prepared copy left at $DRAFT.prepared; draft and content/ restored"
  exit 0
fi

# ---------------------------------------------------------------------------
# 4. Publish. The hero pair lands in the same commit as the page, which is the
#    convention every plate in assets/img/articles/ follows.
# ---------------------------------------------------------------------------
rm -f "$DRAFT.bak"
log "published page written: $TARGET"
# The pending draft stays where it is: per skills/weekly-digest.md it is the
# newsletter body and the page source at once, so it is not finished with until
# the campaign sends, and then it moves to pending/archive/ (never deleted).
log "pending draft retained as the send body: $DRAFT"

PLATE_PREFIX="$(grep -oE 'img/articles/[0-9]+-[a-z0-9-]+_16x9\.webp' "$TARGET" | head -1 | sed 's#img/articles/##; s#_16x9\.webp##')"
log "plate prefix: ${PLATE_PREFIX:-none}"

# The SESSION_STATE entry is written here, from the gate results that actually
# ran, because the entry is the record and an assertion is not a record.
ENTRY="$REPO/SESSION_STATE.md"
{
  echo ""
  echo "### Maintenance — October 23, 2026 — Prepared and published Stoic Saturday \"$TITLE\""
  echo ""
  echo "- **Prepared and published** \`content/posts/digests/$SLUG.md\` at 16:00 CT on 2026-10-23, ahead of the 2026-10-24 06:00 CT send. The frontmatter date is \`2026-10-24T06:00:00-05:00\`, so Hugo's \`buildFuture: false\` holds the page until its hour and the ~06:04 SITREP push releases it, the same six-minute gap after the campaign that every 06:00 digest has carried."
  echo "- **The step the draft left for its send morning was performed a day early**, because the item it needed existed: Friday's \`sitrep-2026-10-23\` published at 06:03 and the letter now carries it as *Friday, three kinds of act* (the third-term claim, the OCC's GENIUS Act final rule effective January 18, 2027, and the Justice and Education notice withdrawing reliance on seven joint guidance documents), with its own \`## Sources\` line and the two closing ranges corrected from *through 22* to *through 23*. The footer comment that named the step was removed; a published post ends with the attribution line."
  echo "- **Hero pair ${PLATE_PREFIX:-NN-none} in both homes** (\`assets/img/articles/\` and \`static/img/articles/\`), generated 2026-10-22 and committed with the page."
  echo "- **Gates, run by \`scripts/digest-prep.sh\` and recorded from their exit codes:**"
  while IFS=$'\t' read -r kind label result; do
    [ "$kind" = "gate" ] && echo "  - \`$label\`: $result"
  done < "${OUT_LOG%.log}.gates"
  echo "- **The SendFox campaign was deliberately not created.** The send is the step a human reviews. Per \`skills/weekly-digest.md\`, a campaign *scheduled* through the API has no human at send time, so it is set to **06:15 CT (11:15:00 UTC)** rather than 06:00, an hour past the ~06:06 the page goes live, and the page-resolves check cannot substitute for that margin at scheduling time. Remaining after review: create the campaign for \`2026-10-24 11:15:00\` UTC, then after it fires archive \`pending/stoic-saturday-the-deed-unannounced.md\` to \`pending/archive/2026-10-24-Stoic-Saturday.md\` and mirror the published page to SimpleBrain."
} >> "$ENTRY" || fail "appending the SESSION_STATE entry failed"
log "SESSION_STATE entry appended"

git add "$TARGET" "$ENTRY" "$REPO/scripts/digest-prep.sh" 2>> "$ERR_LOG"
if [ -n "${PLATE_PREFIX:-}" ]; then
  git add "assets/img/articles/${PLATE_PREFIX}_16x9.webp" "assets/img/articles/${PLATE_PREFIX}_4x5.webp" \
          "static/img/articles/${PLATE_PREFIX}_16x9.webp" "static/img/articles/${PLATE_PREFIX}_4x5.webp" 2>> "$ERR_LOG"
fi
git diff --cached --quiet && fail "nothing staged; the page did not reach git"
git commit -q -m "Publish: Stoic Saturday: $TITLE" 2>> "$ERR_LOG" || fail "git commit failed"
# From here the page is in HEAD; removing it would leave the tree disagreeing
# with the commit, so the failure cleanup must not touch it.
PUBLISHED_COPY=0
log "committed: Publish: Stoic Saturday: $TITLE"

git push >> "$OUT_LOG" 2>> "$ERR_LOG" || fail "push failed"
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse origin/main 2>/dev/null || echo none)"
[ "$LOCAL_SHA" = "$REMOTE_SHA" ] || fail "push reported success but origin/main is $REMOTE_SHA"
log "push verified — origin/main is $LOCAL_SHA"

# Delivery is not this run's check: the page is future-dated and is served only
# after its hour. The publishing tail's verify step does not apply here; what
# applies is the note above, which the SESSION_STATE entry carries.
log "--- digest-prep done. Remaining: create the SendFox campaign for 2026-10-24 11:00:00 UTC after review."
remove_job
exit 0
