#!/bin/bash
# Essay-currency runner — invoked by launchd (com.huffmanwrites.essay-watch).
#
# WHY THIS JOB EXISTS. "The Year the Floor Moved" opens on a Mississippi margin
# that a call will replace, and both 4 November essays rest on facts that expire:
# two uncalled Senate seats in one, two day-count series in the other. Philip,
# 2026-11-04: "Keep those essays current without any prompting from me." A
# watcher that only alerts would make the prompting his job again, so this one
# applies the amendment itself — but only in the shape that needs no judgement:
# a dated note appended below the essay, quoting the headline that carries the
# news and linking to it. The verified prose above it is never edited, so no gate
# has to adjudicate new argument, and the note's claim is a string the online
# link check can confirm.
#
# THE GATES ARE THE REVIEW, so a failure ABORTS the push. There is no human in
# this loop; a note that fails a gate must not reach a reader, and reverting the
# edit is what keeps a failed run from leaving a half-amended essay in the tree
# for the next publishing job to sweep into its own commit.
#
# ESSAY_WATCH_DRY=1 applies the notes, runs every gate and every build, and stops
# before the commit — the only way to prove the amend path without performing it.
set -euo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$REPO/scripts/essay-watch.py"
LOG_DIR="${ESSAY_WATCH_LOG_DIR:-$HOME/Library/Logs}"
ALERT="${ESSAY_WATCH_ALERT:-$REPO/scripts/alert-failure.sh}"
JOB="essay-watch"
OUT_LOG="$LOG_DIR/essay-watch.out.log"
ERR_LOG="$LOG_DIR/essay-watch.err.log"
mkdir -p "$LOG_DIR"

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }
dry() { [ "${ESSAY_WATCH_DRY:-0}" = "1" ]; }

cd "$REPO"
echo "$(stamp): starting essay watch" >> "$OUT_LOG"

# ---- 1. what has expired ---------------------------------------------------
set +e
FINDINGS="$(python3 "$CHECKER" --json 2>>"$ERR_LOG")"
FIND_RC=$?
set -e
printf '%s\n' "$FINDINGS" >> "$OUT_LOG"
if [ "$FIND_RC" -eq 3 ]; then
  echo "$(stamp): every source was unreadable; nothing can be said" >> "$OUT_LOG"
  "$ALERT" "$JOB" 3 "no source could be read; see $OUT_LOG" || true
  exit 3
fi

if [ -z "$FINDINGS" ] || [ "$FINDINGS" = "[]" ]; then
  echo "$(stamp): nothing expired; exiting" >> "$OUT_LOG"
  exit 0
fi

IDS="$(printf '%s' "$FINDINGS" | python3 -c 'import json,sys; print(" ".join(f["id"] for f in json.load(sys.stdin)))')"
# The essays each finding amends, read from the checker's own registry so the
# mapping lives in one place.
TOUCHED="$(python3 - "$REPO" $IDS <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("ew", pathlib.Path(sys.argv[1]) / "scripts" / "essay-watch.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ids = set(sys.argv[2:])
for w in mod.WATCHES:
    if w["id"] in ids:
        print(w["essay"])
PY
)"
TOUCHED="$(printf '%s\n' "$TOUCHED" | sort -u)"
echo "$(stamp): amending $TOUCHED for: $IDS" >> "$OUT_LOG"

# ---- 2. apply the notes ----------------------------------------------------
for id in $IDS; do
  python3 "$CHECKER" --apply "$id" >> "$OUT_LOG" 2>>"$ERR_LOG" || {
    rc=$?
    echo "$(stamp): apply failed for $id (exit $rc)" >> "$OUT_LOG"
    git checkout -- $TOUCHED 2>/dev/null || true
    "$ALERT" "$JOB" "$rc" "apply failed for $id; see $OUT_LOG" || true
    exit "$rc"
  }
done

# ---- 3. the gates ----------------------------------------------------------
gate() {
  local label="$1"; shift
  local out rc=0
  set +e
  out="$("$@" 2>&1)"; rc=$?
  set -e
  printf '%s\n' "$out" >> "$OUT_LOG"
  if [ "$rc" -ne 0 ]; then
    echo "$(stamp): GATE FAILED — $label (exit $rc)" >> "$OUT_LOG"
    git checkout -- $TOUCHED 2>/dev/null || true
    "$ALERT" "$JOB" "$rc" "gate failed: $label; see $OUT_LOG" || true
    exit "$rc"
  fi
  echo "$(stamp): gate OK — $label" >> "$OUT_LOG"
}

for article in $TOUCHED; do
  gate "em-dashes ($article)"  python3 scripts/check-emdashes.py --file "$article"
  gate "prepositions ($article)" python3 scripts/check-prepositions.py --file "$article"
  gate "quotations ($article)" python3 scripts/check-quotes.py --file "$article"
  # --online --titles is not optional here: the note's whole claim is that the
  # headline quoted is the headline that page carries.
  gate "links ($article)"      python3 scripts/check-links.py --file "$article" --online --titles
done
gate "frontmatter"         python3 scripts/check-content-frontmatter.py
gate "hero paths"          python3 scripts/check-hero-paths.py
gate "attribution"         python3 scripts/check-report-frontmatter.py --attribution-corpus

# ---- 4. the two builds -----------------------------------------------------
gate "build (production)" bash -c 'hugo --gc --minify >/dev/null'
TMPDEST="$(mktemp -d "${TMPDIR:-/tmp}/essay-watch-XXXXXX")"
gate "build (drafts)" bash -c "hugo --gc --minify --buildDrafts --destination '$TMPDEST' >/dev/null"
rm -rf "$TMPDEST"

# ---- 5. publish, or stop short --------------------------------------------
if dry; then
  echo "$(stamp): DRY RUN — every gate passed, nothing committed" >> "$OUT_LOG"
  exit 0
fi

ENTRY="$(mktemp "${TMPDIR:-/tmp}/essay-watch-entry-XXXXXX")"
{
  echo ""
  echo "### Maintenance — $(date '+%B %-d, %Y') — Amended a published essay (automated)"
  echo ""
  echo "Written by \`com.huffmanwrites.essay-watch\` after every gate passed."
  echo "- **Amended:** $(printf '%s ' $TOUCHED)"
  echo "- **Triggers:** $IDS"
  printf '%s\n' "$FINDINGS"
  echo "- The note is appended below the essay and above the closing attribution, quoting the headline that carries the news."
} > "$ENTRY"
python3 - "$REPO" "$ENTRY" <<'PY'
import sys, pathlib
repo, entry = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).read_text()
state = repo / "SESSION_STATE.md"
text = state.read_text()
anchor = "### Maintenance —"
i = text.find(anchor)
state.write_text(text[:i] + entry.rstrip("\n") + "\n\n---\n\n" + text[i:])
PY
rm -f "$ENTRY"

git add $TOUCHED SESSION_STATE.md
git commit -q -m "Amend: $(printf '%s ' $TOUCHED | sed 's/ $//')" \
  || { echo "$(stamp): nothing to commit" >> "$OUT_LOG"; exit 0; }
if ! git push >> "$OUT_LOG" 2>>"$ERR_LOG"; then
  echo "$(stamp): push FAILED" >> "$OUT_LOG"
  "$ALERT" "$JOB" 1 "push failed; see $OUT_LOG" || true
  exit 1
fi
echo "$(stamp): pushed" >> "$OUT_LOG"

# The push is not the delivery. Fetch each amended essay at its own URL.
for article in $TOUCHED; do
  set +e
  out="$(python3 scripts/verify-published.py --article "$article" 2>>"$ERR_LOG")"; rc=$?
  set -e
  printf '%s\n' "$out" >> "$OUT_LOG"
  if [ "$rc" -ne 0 ]; then
    echo "$(stamp): live verification FAILED for $article" >> "$OUT_LOG"
    "$ALERT" "$JOB" "$rc" "amended on main but not served: $article" || true
    exit "$rc"
  fi
done
echo "$(stamp): finished" >> "$OUT_LOG"
exit 0
