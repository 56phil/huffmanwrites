#!/bin/bash
# Ask GitHub for one more deploy of a commit that is already on `main`.
#
# Usage: republish-pages.sh <commit-sha>
#
# WHY THIS EXISTS. `publish-report.sh`'s delivery check waits six minutes for the
# Pages workflow the push triggered, and six minutes is right for a deploy that
# is merely queued. It is not enough for a run that has STOPPED, and that is what
# happened on 08NOV26: run 42478502979 spent nine and a half minutes inside its
# FIRST step — `wget` of the Hugo .deb — so the edition was on `main`, every gate
# had passed, `git push` was confirmed, and the site served 404 until a human
# re-dispatched the workflow by hand at 06:13. A wait cannot cover a run that is
# not progressing; a dispatch can, because the workflow's concurrency group
# (`pages-live`, `cancel-in-progress: true`) cancels the stuck run and starts a
# fresh one on another runner.
#
# WHAT IT REFUSES TO DO.
#   * It does not decide that a page is missing. The caller has already watched a
#     full verification window close.
#   * It does not retry a build that FAILED. The same commit fails the same way,
#     and on 06NOV26 that is exactly what happened: a source page was rewritten
#     under a quotation, `check-quote-names --online` went red, and every deploy
#     failed for eighteen hours. Naming the failure is worth more than a second
#     attempt, so a failed run exits 4 and the caller alerts with that sentence.
#   * It never touches the repository. The commit is on `main`, which is the only
#     thing a Pages build needs; no rebase, no empty commit, no second push.
#
# Exit codes: 0  a build was dispatched (or is already on its way)
#             2  no commit given
#             3  the state could not be read — gh missing, unauthenticated, or
#                unable to answer; the caller must not read this as "no deploy"
#             4  the deploy for this commit failed, and a dispatch cannot help
set -uo pipefail

SHA="${1:-}"
if [ -z "$SHA" ]; then
  echo "usage: republish-pages.sh <commit-sha>"
  exit 2
fi

# A FULL 40-character sha, because `gh run list --commit` matches on the exact
# value and silently returns nothing for an abbreviation — which this script
# would then read as "no run exists" and answer with a dispatch. Measured on
# 08NOV26 while smoke-testing the failed-build path: `republish-pages.sh 16125f3`
# dispatched a build for the current head instead of reporting that commit's
# failed run. The caller always has the full sha (`git rev-parse HEAD`), so the
# guard costs nothing and removes a way to spend a real dispatch on a typo.
if [ "${#SHA}" -ne 40 ] || [ -n "${SHA//[0-9a-f]/}" ]; then
  echo "not a full 40-character commit sha: $SHA"
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not on PATH, so no deploy can be requested"
  exit 3
fi

# `gh run list --commit` is the only query that answers the question that
# matters: what did CI do with THIS commit. A repository-wide "is anything
# running" would read a pull-request run as this deploy, and the PR lane is a
# different concurrency group.
if ! runs=$(gh run list --commit "$SHA" --workflow hugo.yml --limit 10 \
      --json status,conclusion,createdAt 2>&1); then
  echo "gh could not list runs for ${SHA:0:7}: $runs"
  exit 3
fi

read -r verdict detail <<<"$(printf '%s' "$runs" | python3 -c '
import json, sys

# Only the NEWEST run for the commit is judged. `gh run list` returns newest
# first, and a commit accumulates runs as incidents are worked: on 08NOV26 the
# same commit has a cancelled run and a successful one, and a rule that read
# "any failure in the list" would have called that commit broken forever.
LIVE = {"queued", "in_progress", "waiting", "pending", "requested"}
FAILED = {"failure", "timed_out", "startup_failure", "action_required"}

try:
    runs = json.load(sys.stdin)
except Exception:
    print("unknown could-not-parse")
    raise SystemExit(0)

if not runs:
    print("absent no-run-for-this-commit")
    raise SystemExit(0)

newest = runs[0]
status = newest.get("status") or "unknown"
conclusion = newest.get("conclusion") or ""
if status in LIVE:
    print("running", status)
elif conclusion in FAILED:
    print("failed", conclusion)
elif conclusion == "success":
    print("absent-succeeded succeeded")
else:
    # cancelled, skipped, or a state this list does not name: nothing is
    # building the commit, so a fresh build is what delivers it.
    print("absent", conclusion or status)
')"

case "$verdict" in
  failed)
    echo "the deploy for ${SHA:0:7} concluded ${detail}; a dispatch would fail the same way"
    exit 4
    ;;
  unknown)
    echo "the deploy state for ${SHA:0:7} could not be parsed from gh's answer"
    exit 3
    ;;
esac

# The run is stuck, superseded, or absent. Either way a fresh build is what
# delivers the commit, and the concurrency group makes the dispatch safe: it
# cancels whatever is still hanging in the same lane and starts clean.
if ! out=$(gh workflow run hugo.yml --ref main 2>&1); then
  echo "gh refused to dispatch hugo.yml: $out"
  exit 3
fi

case "$verdict" in
  running) echo "dispatched a fresh Pages build for ${SHA:0:7}; the previous run was still ${detail} after a full verification window" ;;
  absent-succeeded) echo "dispatched a fresh Pages build for ${SHA:0:7}; its earlier run succeeded and the site still did not carry the page" ;;
  absent) echo "dispatched a fresh Pages build for ${SHA:0:7}; its most recent run concluded ${detail}" ;;
  *) echo "dispatched a fresh Pages build for ${SHA:0:7}" ;;
esac
exit 0
