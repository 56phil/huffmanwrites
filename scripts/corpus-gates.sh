#!/bin/bash
# The canonical corpus-wide gate set, defined once.
#
# Why this file exists. On 2026-10-08 a comparison of the two jobs that guard the
# whole corpus found that their gate lists had drifted: `weekly-integrity-check.sh`
# ran four phases while the publishing tail ran nine more, and the gate that was
# missing from the weekly job was `check-quote-names.py --online` — the only
# corpus-wide online sweep of quoted name details, and the guard for the exact
# defect CLAUDE.md records as having passed every gate (`"Daniel J. Sullivan
# Jr."`, where the cited page says `Daniel J. Sullivan`). It was added to the
# publishing set on 2026-10-04 and never reached the one job whose whole purpose
# is to sweep content nobody has touched in months.
#
# That is the same failure CLAUDE.md already names for the `featuredOnHome` rule:
# a rule that lives in one runner and not another is a rule that holds only where
# it was written. So the corpus gate set lives here, once, and
# `scripts/test_gates.py` asserts (a) that the weekly job runs this list rather
# than its own copy, and (b) that every `scripts/check-*.py` is invoked by CI or
# by some runner — no gate is orphaned, and none is silently dropped from a job.
#
# Scope, stated plainly: these are the ONLINE corpus gates, the ones no other job
# can run. The deterministic corpus gates (hero paths, render integrity, gallery
# pages, series posts, report frontmatter, content frontmatter, dashes,
# prepositions) run in CI on every push and, per-file, in the publishing tail;
# this file does not duplicate them.
#
# Usage (from a job that has already defined `run` and `run_soft`):
#
#     . "$HERE/corpus-gates.sh"
#     run_corpus_gates run run_soft
#
# `run <label> <cmd...>` must mark the job failed on a non-zero exit; `run_soft`
# must report without failing. Both must log the command's own output.

CORPUS_GATES_LIB=1

# Dispatch one entry. Kept at file scope so it needs no closure over the caller.
# mode is `fatal` or `soft`; `soft` is for a gate whose output is genuinely a
# heuristic a human reads, where a hit must not raise the failure alert.
_corpus_gate() {
  local hard="$1" soft="$2" mode="$3" label="$4"; shift 4
  if [ "$mode" = soft ]; then "$soft" "$label" "$@"; else "$hard" "$label" "$@"; fi
}

run_corpus_gates() {
  local hard="${1:-run}" soft="${2:-run_soft}"

  # links. --check first (offline, cheap, catches placeholders and any
  # re-introduced blocklisted URL), then --online to find real rot. Only a
  # 404/410 or a slug-changing redirect fails a link: timeouts, resets and
  # bot-blocks are reported and do not fail the job.
  _corpus_gate "$hard" "$soft" fatal "links (offline)" python3 scripts/check-links.py --check
  _corpus_gate "$hard" "$soft" fatal "links (online)"  python3 scripts/check-links.py --online --quiet

  # The same sweep WITH --titles, which is the only check in this repo that can
  # catch a link resolving to the WRONG page — a URL that returns 200 and serves
  # an unrelated article, the most dangerous failure class here. The per-file
  # publishing runners run it on the article they just wrote; this is the only
  # place it covers the rest of the corpus, including content nobody has touched
  # in months.
  #
  # Reported, NOT fatal. The comparison is a heuristic (it asks whether the link
  # text shares vocabulary with the page's <title>), and a paraphrase or a page
  # that names its subject differently reads as a mismatch: measured on a 200-URL
  # sample, a Wikiquote author page cited for a book title and an Axios article
  # cited by a quoted line both flagged while being correct. Two noise sources
  # were removed before wiring it in: anchors shorter than MIN_HEADLINE_WORDS are
  # no longer compared, and a bot-wall's "Human Verification" title is no longer
  # read as a title.
  _corpus_gate "$hard" "$soft" soft "links (titles)" python3 scripts/check-links.py --online --titles

  # Quotation wording. Fetches each epigraph's own author-linked URL and requires
  # the quoted words to actually be there after whitespace normalisation. Catches
  # a citation that was right when written and has since been rewritten — the
  # failure mode a 200-only check cannot see.
  _corpus_gate "$hard" "$soft" fatal "quotes (online)" python3 scripts/check-quotes.py --online --quiet

  # Quoted NAME DETAILS (a middle initial or a generational suffix) that appear on
  # none of the pages the citing line links. Added to the publishing set on
  # 2026-10-04 for the `"Daniel J. Sullivan Jr."` defect, and absent from this job
  # until 2026-10-08 — which is why the list now lives in one file.
  #
  # Reported, NOT fatal, for a corpus run: a whole-corpus scan legitimately
  # surfaces quoted link TITLES and sources-list quotations from essays and
  # summaries that cite paywalled or JavaScript-rendered pages, and the gate
  # reports those as "unverified". In a publishing run, where the article cites
  # the pages its own footnotes link, a hit aborts the push.
  _corpus_gate "$hard" "$soft" soft "quote-names (online)" python3 scripts/check-quote-names.py --online

  # Credentials. Two homes that disagree are reported offline; --online also asks
  # each provider whether the resolved key authenticates — fal.ai via a GET on a
  # request id that cannot exist (a live key answers 404, a stale one 401) and
  # SendFox via a GET on /lists (200 live, 401 stale). Neither submits a
  # generation or sends a campaign, so the weekly check costs nothing, and it is
  # the only check here that would have caught the 2026-09-24 stale-key split,
  # where the keychain and ~/.secrets agreed with each other and both were dead.
  _corpus_gate "$hard" "$soft" fatal "secrets (drift)"    python3 scripts/check-secrets.py --quiet
  _corpus_gate "$hard" "$soft" fatal "secrets (liveness)" python3 scripts/check-secrets.py --online --quiet
}
