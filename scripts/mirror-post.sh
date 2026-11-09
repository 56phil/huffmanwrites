#!/bin/bash
# Mirror ONE published post into the SimpleBrain vault, by hand.
#
#   scripts/mirror-post.sh content/posts/essays/the-candle-and-the-dark.md
#
# Why this exists. The scheduled jobs get the mirror from `publish_article`, which
# now calls it immediately after the push is verified. A piece published BY HAND —
# an essay, the post-election Senate capstone, a Repair Plan revision — never
# enters that function, so its mirror depended on someone remembering a five-step
# flow (raw copy, wiki entry, highlights line, archive move, commit and push).
# That is the step that failed on 2026-11-09: the Sagan reflection shipped at
# midnight and the vault did not have it until the Monday vault-currency gate
# named the file. So the flow is a command, and it runs the SAME function the tail
# runs rather than a second copy of it.
#
# It does not mirror a file that is not yet on `main`: the vault records what the
# site published, and mirroring an uncommitted draft would put text in the vault
# that no reader can open. Commit and push the article first, as one commit with
# its SESSION_STATE entry.
#
# It does not touch git in the huffmanwrites repo. It changes only the vault: one
# commit there, pushed by the shared tail.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$HOME/Library/Logs"
mkdir -p "$LOG_DIR"
OUT_LOG="$LOG_DIR/mirror-post.out.log"
ERR_LOG="$LOG_DIR/mirror-post.err.log"

# The shared library refuses to load unless JOB is bound: it expands JOB inside
# publish_simplebrain and in every alert. Bound before the source, or the first
# real run dies with "JOB: unbound variable" under `set -u`.
JOB="mirror-post"
. "$REPO/scripts/publish-report.sh"

usage() {
  echo "usage: $(basename "$0") <path relative to the repo root, e.g. content/posts/essays/<slug>.md>" >&2
  exit "${1:-2}"
}

[ "$#" -eq 1 ] || usage
case "$1" in
  -h|--help) usage 0 ;;
esac

article="${1#"$REPO"/}"
[ -f "$REPO/$article" ] || { echo "no such file: $article" >&2; exit 2; }

case "$article" in
  content/posts/*/*.md) ;;
  *) echo "$article is not content/posts/<section>/<name>.md, so the mirror cannot say where the raw copy belongs" >&2
     exit 2 ;;
esac

# Published means committed and pushed. Both are checked against the local file
# rather than assumed, because the failure this guards is subtle: a file edited
# after its push would be mirrored in a form the site never served.
if ! git -C "$REPO" ls-files --error-unmatch "$article" >/dev/null 2>&1; then
  echo "$article is not tracked by this repository yet; commit it before mirroring" >&2
  exit 2
fi
if [ -n "$(git -C "$REPO" status --porcelain -- "$article")" ]; then
  echo "$article has uncommitted changes; the vault mirrors what the site serves, not what is in the working tree" >&2
  exit 2
fi
head_sha="$(git -C "$REPO" rev-parse HEAD)"
git -C "$REPO" fetch -q origin main 2>>"$ERR_LOG" || true
if [ "$head_sha" != "$(git -C "$REPO" rev-parse origin/main 2>/dev/null || echo none)" ]; then
  echo "HEAD is $head_sha but origin/main is not; push the article first, then mirror it" >&2
  exit 2
fi

# The page itself is checked, not the commit: an article can be on `main` and still
# be a 404 (a stalled deploy), and the daily-sitrep runs of 06NOV26 and 08NOV26 both
# reached `main` without being served. verify_published's own vocabulary is kept:
# 1 absent, 3 unconfirmed.
live_rc=0
out="$(python3 "$REPO/scripts/verify-published.py" --article "$article" 2>>"$ERR_LOG")" || live_rc=$?
if [ "$live_rc" -ne 0 ]; then
  echo "not mirroring: the site does not serve $article yet — ${out#verify-published: }" >&2
  exit "$live_rc"
fi

echo "$(stamp): mirror-post start — $article" >> "$OUT_LOG"
sb_rc=0
publish_simplebrain "$article" "${SIMPLEBRAIN_ROOT:-$HOME/SimpleBrain}" || sb_rc=$?
echo "$(stamp): mirror-post finished (exit $sb_rc)" >> "$OUT_LOG"

if [ "$sb_rc" -eq 0 ]; then
  if report_skip_simplebrain; then
    # `REPORT_SKIP_SIMPLEBRAIN=1` is a testing switch, and a command that answers
    # "mirrored" when it copied nothing is the kind of claim this repo bans.
    echo "mirror SKIPPED (REPORT_SKIP_SIMPLEBRAIN=1): $article — nothing was copied"
  else
    echo "mirrored: $article (log: $OUT_LOG)"
  fi
else
  echo "mirror INCOMPLETE: $article — see $OUT_LOG" >&2
fi
exit "$sb_rc"
