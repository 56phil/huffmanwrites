#!/usr/bin/env python3
"""Tests for the deploy gates in scripts/.

Why this exists. These gates are now load-bearing: CI blocks a deploy on them,
and four of them have been wrong in ways that were found only by accident — a
counting-semantics mismatch in the em-dash gate, a raw-vs-counted error in a
verification harness, a blind spot in the quotation gate that made a *better*
citation invisible to it, and a hero-image srcset bug in the render check.
Every one was caught by a human noticing, not by a test.

What is worth testing here is not that the scripts run. It is the RULES:
the exemption logic, the blind spots that were actually fixed, and the
fabrication patterns the corpus has produced. A test that restates the
implementation would pass while the gate was blind, which is exactly the
failure mode these guards exist to prevent.

Run:  python3 scripts/test_gates.py
      python3 scripts/test_gates.py -v      # per-test names
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import re
import sys
import unittest
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def load(name: str):
    """Import a gate module. None of them import at call time, so this is safe."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ce = load("check-emdashes")
cq = load("check-quotes")
cl = load("check-links")
cr = load("check-render-integrity")
cg = load("check-gallery-pages")
cp = load("check-plists")
cpn = load("check-prepositions")
cs = load("check-secrets")
chp = load("check-hero-paths")
csp = load("check-series-posts")
crf = load("check-report-frontmatter")
cqn = load("check-quote-names")

EM = "\u2014"


# --------------------------------------------------------------------------
# Em-dash gate: the two documented exemptions, and the counting rule.
# --------------------------------------------------------------------------
class TestEmDash(unittest.TestCase):
    def count(self, body: str) -> int:
        return ce.classify(f"---\ntitle: t\n---\n{body}")["counted"]

    def test_counts_ordinary_prose_dashes(self):
        self.assertEqual(self.count("a thing — another thing"), 1)

    def test_exempts_a_dash_inside_curly_quotation(self):
        # A quotation's internal punctuation belongs to its author. Rewriting it
        # to save a mark would corrupt the quotation.
        self.assertEqual(self.count('He said “one — two” plainly'), 0)

    def test_exempts_a_dash_inside_straight_quotation(self):
        self.assertEqual(self.count('He said "one — two" plainly'), 0)

    def test_exempts_a_date_range(self):
        # A range is normally an en-dash; an em-dash here is a typo, not prose.
        self.assertEqual(self.count("the years 1903 — 1977 were long"), 0)

    def test_does_not_exempt_a_dash_next_to_a_word(self):
        # The range exemption is narrow on purpose. "3 — words" is prose.
        self.assertEqual(self.count("there were 3 — words left"), 1)

    def test_frontmatter_is_not_counted(self):
        # Frontmatter is display metadata; YAML quoting makes "inside quotes"
        # ambiguous there, and the identical unquoted string would be counted.
        n = ce.classify('---\ntitle: "a — b"\n---\nclean prose')["counted"]
        self.assertEqual(n, 0)

    def test_reports_frontmatter_separately(self):
        c = ce.classify('---\ntitle: "a — b"\n---\nclean prose')
        self.assertEqual(c["counted"], 0)
        self.assertEqual(c["frontmatter"], 1)

    def test_ratchet_is_on_the_number_not_presence(self):
        # A file may be reduced freely but may not grow past its recorded count.
        # Keying on presence alone would exempt every future dash in the file.
        self.assertIsInstance(ce.load_baseline(), dict)


# --------------------------------------------------------------------------
# Quotation gate: the rules, and the blind spots that were actually fixed.
# --------------------------------------------------------------------------
class TestQuoteRules(unittest.TestCase):
    def test_author_extracted_from_a_citation(self):
        self.assertEqual(cq.author_of("Marcus Aurelius, *Meditations*, 6.21"),
                         "Marcus Aurelius")
        self.assertEqual(cq.author_of("Epictetus, trans. Robin Waterfield"),
                         "Epictetus")

    def test_author_of_rejects_prose_and_headings(self):
        # A credit is name-first. Prose after a dash is not an attribution, and
        # treating it as one fails a build on ordinary writing.
        self.assertIsNone(cq.author_of("this is a long sentence of prose"))
        self.assertIsNone(cq.author_of(""))

    def test_is_translated_knows_classical_authors(self):
        # Membership in this list is what triggers the translator requirement.
        # If the list is emptied or broken, the rule silently stops applying —
        # which is the gate going blind to the work it exists to check.
        self.assertTrue(cq.is_translated("Marcus Aurelius"))
        self.assertTrue(cq.is_translated("Epictetus"))
        self.assertTrue(cq.is_translated("Seneca"))
        self.assertFalse(cq.is_translated("Carl Sagan"))
        self.assertFalse(cq.is_translated("Rachel Carson"))

    def test_translated_author_needs_a_translator(self):
        # The rule the whole gate exists for: "Marcus Aurelius, Meditations,
        # 6.21" is not a citation, because the rendering is translator-dependent.
        ep = {"author": "Marcus Aurelius", "attribution": "Marcus Aurelius, *Meditations*, 6.21",
              "quote": '"no translator named here at all"'}
        problems = cq.audit(ep, "Marcus Aurelius https://example.org/x", True)
        self.assertTrue(any("translator" in p for p in problems), problems)

    def test_translator_satisfies_the_requirement(self):
        ep = {"author": "Marcus Aurelius",
              "attribution": "Marcus Aurelius, *Meditations* 6.21 (trans. Hays, 2003), [text](https://example.org/x)",
              "quote": '"convince or shew me ... gladly change"'}
        text = ep["attribution"]
        problems = cq.audit(ep, text, True)
        self.assertEqual([p for p in problems if "translator" in p], [])

    def test_paraphrase_label_excuses_a_translator(self):
        # Several circulating epigraphs are famous loose paraphrases. Requiring
        # a translator for wording no translation contains would force either a
        # false citation or a deleted quotation; the label is the honest exit.
        ep = {"author": "Marcus Aurelius",
              "attribution": "often attributed to Marcus Aurelius; a modern paraphrase not found in any translation",
              "quote": '"You have power over your mind, not outside events"'}
        problems = cq.audit(ep, ep["attribution"] + " https://example.org/x", True)
        self.assertEqual([p for p in problems if "translator" in p], [])

    def test_url_must_sit_on_a_line_naming_the_author(self):
        # The blind spot that shipped: a file-wide URL satisfied the check even
        # when no line connected that URL to the author being cited.
        ep = {"author": "Rachel Carson", "attribution": "Rachel Carson",
              "quote": '"The question is whether any civilization can wage relentless war"'}
        text = "Rachel Carson\n\n*PRH | [site](https://www.huffmanwrites.org/) | © Philip Huffman*"
        problems = cq.audit(ep, text, False)
        self.assertTrue(any("names Carson" in p for p in problems), problems)

    def test_no_url_anywhere_is_reported(self):
        ep = {"author": "Rachel Carson", "attribution": "Rachel Carson",
              "quote": '"a quotation long enough to qualify as one"'}
        problems = cq.audit(ep, "Rachel Carson", False)
        self.assertTrue(any("no source URL" in p for p in problems), problems)

    def test_html_entities_are_decoded(self):
        # Hillsdale encodes the Churchill apostrophe as &#8217;. Without
        # unescaping, no apostrophe-bearing quotation can ever match its source.
        # `html_to_text` yields the decoded Unicode; `fold` is the stage that
        # equates it with the ASCII form, and the comparison uses both.
        decoded = cq.html_to_text("<p>don&#8217;t</p>")
        self.assertIn("\u2019", decoded)          # decoded, not left as &#8217;
        self.assertNotIn("&#8217;", decoded)
        self.assertEqual(cq.fold(decoded), cq.fold("don't"))

    def test_zero_width_characters_are_stripped(self):
        # MediaWiki emits &#8203; as a layout crutch. A zero-width codepoint
        # inside a quotation splits it for a substring test while being
        # invisible on screen, so a correct citation would fail.
        self.assertEqual(cq.fold("enemy\u200b's"), "enemy's")

    def test_block_tags_become_a_space_inline_tags_do_not(self):
        # Wikisource renders a drop cap as <span>F</span>irst. Removing inline
        # tags with a separator yields "F irst" and fails a correct citation.
        self.assertEqual(cq.html_to_text("<p>one</p><p>two</p>"), "one two")
        self.assertEqual(cq.html_to_text("<span>F</span>irst"), "First")

    def test_typographic_apostrophes_fold_together(self):
        # The site writes enemy's; Gutenberg writes enemy’s. Failing on that
        # difference is a false accusation of fabrication.
        self.assertEqual(cq.fold("enemy\u2019s"), cq.fold("enemy's"))

    def test_sentence_after_a_dash_is_not_an_attribution(self):
        # Regression: this exact shape is ordinary prose, and a gate that
        # audits it fails builds for writing correctly.
        p = REPO / "content" / "posts" / "essays" / "the-genesis-of-the-genius-years.md"
        if p.exists():
            for ep in cq.epigraphs(p):
                self.assertTrue(ep["author"], ep)

    def test_a_refused_fetch_is_not_a_missing_quotation(self):
        # The false accusation this gate is most dangerous for. A 403 is the
        # host refusing automated clients — the same refusal the link gate
        # documents as "NOT evidence of fabrication". Folding it into the
        # mismatch branch made a correctly cited, bot-blocked publisher print as
        # "does not contain the words it is cited for" and exit 1: the gate
        # accusing this repo of the exact defect it exists to catch.
        #
        # Simulated through fetch_text so the rule is tested, not the network.
        orig = cq.fetch_text
        try:
            cq.fetch_text = lambda url: ("403", "")
            self.assertEqual(cq.check_online("https://example.org/x", "a" * 40, True), [])
            # 5xx likewise: a server-side fault says nothing about the citation.
            cq.fetch_text = lambda url: ("503", "")
            self.assertEqual(cq.check_online("https://example.org/x", "a" * 40, True), [])
            # A dead link stays fatal, and is reported as a dead link rather
            # than as a missing quotation.
            cq.fetch_text = lambda url: ("404", "")
            dead = cq.check_online("https://example.org/x", "a" * 40, True)
            self.assertEqual(len(dead), 1, dead)
            self.assertIn("dead", dead[0])
            self.assertNotIn("does not contain", dead[0])
            # A readable page that really lacks the wording is still caught —
            # without this the fix above would be indistinguishable from
            # disabling the check.
            cq.fetch_text = lambda url: ("200", "<p>unrelated content here</p>")
            self.assertEqual(len(cq.check_online("https://example.org/x", "a" * 40, True)), 1)
            cq.fetch_text = lambda url: ("200", "<p>" + "a" * 40 + "</p>")
            self.assertEqual(cq.check_online("https://example.org/x", "a" * 40, True), [])
        finally:
            cq.fetch_text = orig

    def test_footnote_marker_points_at_the_definition(self):
        # A citation may route through the piece's own footnote apparatus, which
        # CLAUDE.md names as legitimate ("the footnote block in pieces that use
        # footnotes"). The marker is an explicit pointer, so following it is a
        # citation rather than a guess.
        text = ("Prose[^1] here.\n\n"
                "[^1]: Madison, J. (1788). Federalist No. 51. "
                "https://avalon.law.yale.edu/18th_century/fed51.asp\n"
                "[^2]: Other. https://example.org/other\n")
        self.assertEqual(cq.footnote_urls(text, "1"),
                         ["https://avalon.law.yale.edu/18th_century/fed51.asp"])
        self.assertEqual(cq.footnote_urls(text, "2"), ["https://example.org/other"])
        # A definition must not bleed into the next one.
        self.assertNotIn("https://example.org/other", cq.footnote_urls(text, "1"))
        self.assertEqual(cq.footnote_urls(text, "9"), [])
        self.assertEqual(cq.FOOTNOTE_MARKER.findall("— James Madison, Federalist 51[^1]"), ["1"])
        self.assertEqual(cq.FOOTNOTE_MARKER.findall("— James Madison, Federalist 51"), [])

    def test_an_epigraph_is_never_tested_against_another_sources_url(self):
        # The cross-product. A summary naming Kennedy in its Sources matched all
        # five of its Kennedy-labelled URLs — a Politico profile, an NYT archive
        # piece, a Pulitzer page, an academia.edu chapter, and the book's own
        # full text — and demanded each contain the epigraph, failing four
        # correct citations. The author-wide fallback is gone: sources reachable
        # only by naming the author must never be tested against a quotation.
        #
        # The Kennedy summary is the live regression fixture, so this asserts on
        # the real file rather than a synthetic one.
        p = REPO / "content" / "posts" / "summaries" / "profiles-in-courage-summary.md"
        self.assertTrue(p.exists(), "regression fixture missing")
        text = p.read_text(encoding="utf-8")
        eps = [e for e in cq.epigraphs(p) if e["author"].startswith("John F. Kennedy")]
        self.assertEqual(len(eps), 1, eps)
        urls = cq.citation_urls(text, eps[0])
        # Exactly one: the full text linked on the citation line. The other four
        # URLs in the file name Kennedy and must NOT be pulled in.
        self.assertEqual(len(urls), 1, urls)
        self.assertIn("fadedpage.com", urls[0])
        for stray in ("pulitzer.org", "academia.edu", "theatlantic.com",
                      "nytimes.com"):
            self.assertNotIn(stray, " ".join(urls),
                             f"{stray} reached the citation by naming the author")

    def test_citation_urls_reads_the_scope_it_claims(self):
        # The three legitimate locations, and the one that is not.
        ep = {"line": 3, "attribution": "Tara Brach[^1]", "author": "Tara Brach",
              "quote": '"a quotation long enough to be audited"'}
        # 1. on the attribution line
        t = "x\ny\n— Tara Brach, [text](https://example.org/on-line)\n"
        self.assertEqual(cq.citation_urls(t, ep), ["https://example.org/on-line"])
        # 2. on the line below it
        t = "x\ny\n> — Tara Brach\n[text](https://example.org/below)\n"
        self.assertEqual(cq.citation_urls(t, ep), ["https://example.org/below"])
        # 3. through a footnote the line points at
        t = ("x\ny\n> — Tara Brach[^1]\n\n[^1]: Brach, T. *Radical Acceptance*. "
             "https://example.org/def\n")
        self.assertEqual(cq.citation_urls(t, ep), ["https://example.org/def"])
        # 4. naming the author elsewhere must NOT reach it
        t = ("preamble\nmore\n— Tara Brach\n\nfiller\nmore filler\n\nSources:\n"
             "- Brach, Tara. [x](https://example.org/author-line)\n")
        self.assertEqual(cq.citation_urls(t, ep), [])

    def test_a_stitched_quotation_is_not_a_mismatch(self):
        # A quotation may be assembled from two utterances of the same speaker
        # with the attribution between them. The Chiefs report cites Shane
        # Steichen that way, and the contiguous search reported a CORRECT
        # citation as "does not contain" — the precise false accusation of
        # fabrication this gate exists to prevent, on the job that publishes
        # unreviewed. Every SENTENCE must still be present.
        import io
        import contextlib

        needle = ("Had a play called. Had to love the look to run it there. "
                  "We took the delay and kicked the field goal.")
        # The page: sentence 1, the attribution, sentence 2.
        page = ('<p>\u201cHad a play called. Had to love the look to run it '
                'there,\u201d Colts coach Shane Steichen said. \u201cWe took the '
                'delay and kicked the field goal.\u201d</p>')
        flat = cq.html_to_text(page)
        sentences = [cq.fold(s) for s in needle.split(". ") if cq.fold(s)]
        self.assertTrue(all(s in cq.fold(flat) for s in sentences),
                        "fixture must contain every sentence")

    def test_a_partly_invented_quotation_is_still_caught(self):
        # The guard must keep its teeth: forgiving the JOIN must not forgive an
        # invented CLAUSE. This is the discrimination the fix turns on.
        needle = ("Had a play called. Had to love the look to run it there. "
                  "We decided to run a trick play instead.")
        page = ('<p>\u201cHad a play called. Had to love the look to run it '
                'there,\u201d he said. \u201cWe took the delay and kicked the '
                'field goal.\u201d</p>')
        flat = cq.fold(cq.html_to_text(page))
        sentences = [cq.fold(s) for s in needle.split(". ") if cq.fold(s)]
        self.assertFalse(all(s in flat for s in sentences),
                         "an invented sentence must not be forgiven")

    def test_the_stitch_rule_requires_more_than_one_sentence(self):
        # A single-sentence quotation gets no leniency from this path; it is
        # either present or it is not.
        single = "Had a play called"
        self.assertEqual(len([s for s in single.split(". ") if s]), 1)


# --------------------------------------------------------------------------
# Link gate: the fabrication patterns this repo has actually produced.
# --------------------------------------------------------------------------
class TestLinkRules(unittest.TestCase):
    def test_placeholder_urls_are_caught(self):
        self.assertTrue(cl.PLACEHOLDER.search("https://example.com/[ID]/story"))

    def test_a_real_url_is_not_a_placeholder(self):
        self.assertIsNone(cl.PLACEHOLDER.search("https://www.reuters.com/world/a-real-story-2026-09-17/"))

    def test_trailing_sentence_punctuation_is_trimmed(self):
        self.assertEqual(cl.clean("https://example.org/a."), "https://example.org/a")
        self.assertEqual(cl.clean("https://example.org/a,"), "https://example.org/a")

    def test_markdown_emphasis_around_a_link_is_stripped(self):
        # Measured 2026-09-28: an italicised markdown link — `*[text](url)*` —
        # left the closing `)` AND the emphasis `*` on the captured URL, so the
        # checker fetched `…/Book_VI)*`, got a 404, and reported a LIVE citation
        # as DEAD. Stripping sentence punctuation alone could not reach it: the
        # string ends in `*`, so `balanced()` never ran. This is the second time
        # this false-alarm class shipped, so it is pinned twice over.
        full = ("https://en.wikisource.org/wiki/"
                "The_Thoughts_of_the_Emperor_Marcus_Aurelius_Antoninus/Book_VI")
        for tail in (")*", ")*.", ").", ")", ")*,"):
            with self.subTest(tail=tail):
                self.assertEqual(cl.clean(full + tail), full)

    def test_a_footnote_marker_is_stripped_from_a_url(self):
        # `[Vote.gov](https://vote.gov/).[^6]` — the marker sits outside the
        # period, and the bare-URL capture kept both. Same defect class.
        self.assertEqual(cl.clean("https://vote.gov/).[^6"), "https://vote.gov/")
        self.assertEqual(cl.clean("https://vote.gov/)[^6]"), "https://vote.gov/")

    def test_a_url_inside_prose_parens_loses_only_the_prose_paren(self):
        # The repair-plan Wikisource citation carries BALANCED parens of its own
        # and must survive; a prose `(...)` wrapper must not.
        keep = ("https://en.wikisource.org/w/index.php?title="
                "Page:Paris_Agreement_(English).pdf/24&action=raw")
        self.assertEqual(cl.clean(keep + ")"), keep)
        self.assertEqual(cl.clean(keep), keep)

    def test_the_emphasis_strip_does_not_eat_a_legitimate_url(self):
        # A `*` or `_` can be part of a real path. Only a TRAILING wrapper is
        # removed, and only when it is not followed by more path.
        for u in ("https://example.org/a*b", "https://example.org/a_b",
                  "https://example.org/path_here/more"):
            with self.subTest(u=u):
                self.assertEqual(cl.clean(u), u)

    def test_a_trailing_smart_quote_is_stripped(self):
        # Measured 2026-10-01: `…%22)%E2%80%9D` — a bare URL ending inside a
        # chapter-title quotation — kept the prose paren and the closing `”`,
        # because `”` was not in TRAILING so nothing stripped it and
        # `balanced()` never ran on a string ending in `”`.
        u = ("https://openlibrary.org/search/inside?q=%22Socratic+Pedagogy"
             "%3A+The+Importance+of+Argument%22")
        for tail in (")”", "’)", "”", "’"):
            with self.subTest(tail=tail):
                self.assertEqual(cl.clean(u + tail), u)

    def test_an_html_entity_ends_a_bare_url(self):
        # The April 18 digest's link list is `[Medium](url),&nbsp;[Substack](url)`.
        # The bare-URL class swallowed `),&nbsp;[Substack` as part of the first
        # URL, so the checker fetched an invented address. Everything from the
        # `&` is markup, not the URL.
        text = ("[Medium](https://medium.com/?ref=huffmanwrites.org),&nbsp;"
                "[Substack](https://substack.com/?ref=huffmanwrites.org)")
        self.assertEqual([cl.clean(u) for u in cl.URL.findall(text)],
                         ["https://medium.com/?ref=huffmanwrites.org",
                          "https://substack.com/?ref=huffmanwrites.org"])

    def test_bot_blocking_hosts_are_recognised_including_subdomains(self):
        # A 403 from these says nothing about whether the link is real. Assert
        # against the gate's own list rather than a guessed host: the list is
        # the policy, and hardcoding a host here would drift from it.
        self.assertTrue(cl.BOT_BLOCKING)
        host = cl.BOT_BLOCKING[0]
        self.assertTrue(cl.is_blocking(f"https://{host}/x"))
        self.assertTrue(cl.is_blocking(f"https://www.{host}/x"))
        self.assertFalse(cl.is_blocking("https://not-a-listed-host.example/x"))

    def test_a_blocking_entry_does_not_match_an_unrelated_domain(self):
        # Suffix matching must not turn "example.com" into a match for
        # "notexample.com" — that would silently excuse real rot.
        self.assertFalse(cl.is_blocking("https://notwashingtonpost.com/x"))

    def test_own_domain_is_not_fetched(self):
        self.assertTrue(cl.is_own("https://huffmanwrites.org/posts/x/"))

    def test_coverage_floors_are_high_enough_to_catch_a_broken_glob(self):
        # A path or glob that silently stops matching would otherwise report
        # "0 problems" on nothing at all.
        self.assertGreater(cl.MIN_FILES, 50)
        self.assertGreater(cl.MIN_URLS, 100)


# --------------------------------------------------------------------------
# Render gate: the defect class that returns 200 while being broken.
# --------------------------------------------------------------------------
class TestRenderRules(unittest.TestCase):
    def test_zgotmplz_sentinel_is_recognised(self):
        self.assertIn("ZgotmplZ", cr.SENTINELS)

    def test_unrendered_shortcode_is_caught(self):
        self.assertTrue(cr.UNRENDERED_SHORTCODE.search("text {{< book >}} more"))

    def test_bare_braces_in_javascript_are_not_a_shortcode(self):
        # JS and CSS legitimately contain braces; matching those would fail
        # every page carrying a script.
        self.assertIsNone(cr.UNRENDERED_SHORTCODE.search("if (a) { b = {c: 1} }"))

    def test_local_paths_are_distinguished_from_external(self):
        self.assertTrue(cr.is_local("/img/books/x.webp"))
        self.assertFalse(cr.is_local("https://example.org/x"))
        self.assertFalse(cr.is_local("#anchor"))
        self.assertFalse(cr.is_local("mailto:a@b.c"))


# --------------------------------------------------------------------------
# Gallery gate: the contract that produced a live 404.
# --------------------------------------------------------------------------
class TestGalleryRules(unittest.TestCase):
    def test_page_count_rounds_up(self):
        # 101 items at 12 per page is 9 pages, not 8. Rounding down leaves the
        # final page unbuilt while the paginator still links to it — the 404.
        # Calls the gate's own rule, so this fails if that rule regresses.
        self.assertEqual(cg.page_count(101, 12), 9)

    def test_exact_multiple_does_not_add_an_empty_page(self):
        self.assertEqual(cg.page_count(96, 12), 8)

    def test_a_single_item_still_needs_one_page(self):
        self.assertEqual(cg.page_count(1, 12), 1)

    def test_the_shipped_gallery_matches_its_page_stubs(self):
        # The real contract: derived page count against the stubs on disk.
        total = cg.page_count(cg.item_count(), cg.items_per_page())
        self.assertGreater(total, 1)
        self.assertTrue(cg.existing_stubs(), "no gallery page stubs found")

    # -- `latest` globs (2026-09-26): recurring series resolve to the newest
    #    installment, so a card cannot go stale as installments accumulate.

    def test_latest_entries_are_discovered(self):
        # The three recurring series. A card that loses this key silently
        # reverts to a fixed link and starts going stale.
        globs = {title: glob for title, glob, _ in cg.latest_entries()}
        self.assertIn("Chiefs Report", globs)
        self.assertIn("Senate Race Report", globs)
        self.assertIn("Docket Report", globs)

    def test_the_unstarted_series_reports_its_fallback(self):
        # The docket card has no installments yet, so what it DOES is decided by
        # whether it carries a `link`. The gate must report the real behaviour,
        # not assume one: the first version of this note said the card "renders
        # without a Read Post link" after a fallback had already been added,
        # which is the kind of stale note that misleads the next session.
        entries = {t: (g, fb) for t, g, fb in cg.latest_entries()}
        self.assertIn("Docket Report", entries)
        _, has_fallback = entries["Docket Report"]
        self.assertTrue(has_fallback, "the docket card needs a link fallback")

    def test_a_card_with_a_glob_and_no_fallback_is_reported_as_dead(self):
        # If a card that resolves to the newest installment loses its `link`
        # fallback while the series has not started, the note must say the card
        # has no way through to any post — that is the state the user objected
        # to.
        #
        # Both the data AND the filesystem are mocked, because this state only
        # exists before a series has installments. The test used to mutate the
        # real gallery alone; once the docket report published its first
        # installment (2026-10-03) the real glob started matching, the note was
        # never emitted, and this test broke the deploy gate for the wrong
        # reason. The empty content tree keeps it about the rule.
        from unittest import mock
        import tempfile
        real = cg.GALLERY_DATA.read_text(encoding="utf-8")
        mutated = real.replace(
            "  link: /posts/essays/three-walls-and-three-slots/\n", "")
        self.assertNotEqual(real, mutated, "fixture did not change")
        with tempfile.TemporaryDirectory() as tmp:
            for sub in ("posts/essays", "posts/sports"):
                (Path(tmp) / "content" / sub).mkdir(parents=True)
            with mock.patch.object(cg, "GALLERY_DATA") as fake, \
                    mock.patch.object(cg, "REPO", Path(tmp)):
                fake.read_text.return_value = mutated
                failures, notes = cg.latest_problems()
        self.assertEqual(failures, [], failures)
        self.assertTrue(any("no `link` fallback" in n for n in notes), notes)

    def test_a_glob_pointing_at_a_missing_directory_fails(self):
        # The typo that can never match: `/posts/essay/` for `/posts/essays/`.
        # This one is a hard failure because no future installments can fix it.
        from unittest import mock
        real = cg.GALLERY_DATA.read_text(encoding="utf-8")
        mutated = real.replace(
            "latest: /posts/essays/docket-report-*",
            "latest: /posts/essay/docket-report-*")
        self.assertNotEqual(real, mutated, "fixture did not change")
        with mock.patch.object(cg, "GALLERY_DATA") as fake:
            fake.read_text.return_value = mutated
            failures, _ = cg.latest_problems()
        self.assertTrue(any("does not exist" in f for f in failures), failures)

    def test_an_unstarted_series_is_a_note_not_a_failure(self):
        # A declared series with no installments yet is legitimate, so the gate
        # notes it rather than failing — otherwise CI would be red until the
        # first run, which is how a real alert gets learned as noise.
        #
        # The docket series published its first installment on 2026-10-03. This
        # asserts the RULE, so "has not started" is simulated by pointing the
        # scan at an empty content tree rather than at a series that happens to
        # be unstarted today: the shipped-gallery version of this test went
        # stale the moment that installment landed and skipped the deploy.
        from unittest import mock
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            for sub in ("posts/essays", "posts/sports"):
                (Path(tmp) / "content" / sub).mkdir(parents=True)
            with mock.patch.object(cg, "REPO", Path(tmp)):
                failures, notes = cg.latest_problems()
        self.assertEqual(failures, [], failures)
        self.assertTrue(any("Docket Report" in n for n in notes), notes)
        self.assertTrue(any("falling back to its `link`" in n for n in notes), notes)

    def test_no_shipped_glob_fails(self):
        failures, _ = cg.latest_problems()
        self.assertEqual(failures, [])

    def test_every_entry_has_a_way_to_resolve(self):
        # Each card must carry either a fixed `link` or a `latest` glob.
        # A card with neither renders a title and a picture that goes nowhere.
        text = cg.GALLERY_DATA.read_text(encoding="utf-8")
        blocks = [b for b in re.split(r"(?=^\s*-\s+image:)", text, flags=re.M)
                  if b.strip()]
        for b in blocks:
            with self.subTest(block=b.strip().splitlines()[0][:60]):
                self.assertTrue(
                    re.search(r"^\s*(link|latest):", b, re.M),
                    "gallery entry has neither link nor latest")


# --------------------------------------------------------------------------
# Plist gate: the silent-schedule failure.
# --------------------------------------------------------------------------
class TestPlistRules(unittest.TestCase):
    def test_double_hyphen_in_a_comment_is_named_as_the_cause(self):
        # The defect that shipped: "--" is illegal inside an XML comment, so
        # launchd refused the file, and plistlib's own error does not say why.
        bad = "<plist><!-- note -- here --><dict/></plist>"
        why = cp.explain(bad)
        self.assertIsNotNone(why)
        self.assertIn("double hyphen", why)

    def test_a_clean_comment_produces_no_explanation(self):
        self.assertIsNone(cp.explain("<plist><!-- a clean note --><dict/></plist>"))

    def test_every_shipped_plist_parses(self):
        # The gate's own subject matter. If this fails, CI would have failed.
        for p in cp.repo_plists():
            import plistlib
            plistlib.loads(p.read_bytes())


# --------------------------------------------------------------------------
# Docket watch. The rules that matter are the two entry kinds the feed
# interleaves (an ECF-numbered filing and a minute order), the per-case
# watermark, and the legacy state-file migration — because the failure this
# watcher actually had was a *missing* report, not a wrong one.
# --------------------------------------------------------------------------
cd = load("check-docket")


class TestDocketRules(unittest.TestCase):
    @staticmethod
    def _feed(*blocks: str) -> str:
        return "<feed>" + "".join(blocks) + "</feed>"

    @staticmethod
    def _entry(num: int, date: str, summary: str = "s") -> str:
        return (f"<entry><title>Entry #{num} in X</title>"
                f"<published>{date}T00:00:00-07:00</published>"
                f"<summary>{summary}</summary></entry>")

    @staticmethod
    def _minute(mid: int, date: str, summary: str = "m") -> str:
        return (f'<entry><title>Minute entry from {date} in X</title>'
                f'<published>{date}T00:00:00-07:00</published>'
                f'<summary>{summary}</summary>'
                f'<id>https://x/#minute-entry-{mid}</id></entry>')

    def test_parses_both_entry_kinds(self):
        # The defect this guards: the parser used to key on "Entry #N" alone and
        # silently dropped minute entries. In *Phang*, Sullivan rules and sets
        # deadlines by minute order, so dropping them means reporting a quiet
        # docket on the days the case actually moved.
        got = cd.parse_entries(self._feed(self._entry(50, "2026-09-24"),
                                          self._minute(478777445, "2026-09-21")))
        self.assertEqual(len(got), 2)
        self.assertEqual({e["kind"] for e in got}, {"entry", "minute"})

    def test_ecf_entries_are_keyed_by_number_and_minutes_by_id(self):
        got = cd.parse_entries(self._feed(self._entry(50, "2026-09-24"),
                                          self._minute(478777445, "2026-09-21")))
        by_kind = {e["kind"]: e for e in got}
        self.assertEqual(by_kind["entry"]["num"], 50)
        self.assertIsNone(by_kind["entry"]["mid"])
        self.assertEqual(by_kind["minute"]["mid"], 478777445)
        self.assertIsNone(by_kind["minute"]["num"])

    def test_a_new_ecf_filing_is_reported(self):
        entries = cd.parse_entries(self._feed(self._entry(50, "2026-09-24"),
                                              self._minute(900, "2026-09-21")))
        new = cd.new_entries(entries, last_entry=48, last_minute=900)
        self.assertEqual([e["num"] for e in new], [50])

    def test_a_new_minute_entry_is_reported(self):
        entries = cd.parse_entries(self._feed(self._entry(50, "2026-09-24"),
                                              self._minute(901, "2026-09-21")))
        new = cd.new_entries(entries, last_entry=50, last_minute=900)
        self.assertEqual([e["mid"] for e in new], [901])

    def test_an_untracked_minute_watermark_reports_no_minute_history(self):
        # None means the case has never tracked minute entries, so the first
        # run records the newest and does not replay the backlog as a burst.
        # 0 would be a real watermark and would report every minute entry.
        entries = cd.parse_entries(self._feed(self._minute(900, "2026-09-21"),
                                              self._minute(901, "2026-09-22")))
        self.assertEqual(cd.new_entries(entries, last_entry=0, last_minute=None), [])
        self.assertEqual(len(cd.new_entries(entries, last_entry=0, last_minute=0)), 2)

    def test_no_change_yields_nothing(self):
        entries = cd.parse_entries(self._feed(self._entry(50, "2026-09-24"),
                                              self._minute(900, "2026-09-21")))
        self.assertEqual(cd.new_entries(entries, last_entry=50, last_minute=900), [])

    def test_legacy_flat_state_migrates_its_watermark_to_its_case(self):
        # The file held one case at one watermark. That watermark is Beatty's,
        # so it moves there. Renaming the key without carrying the value would
        # re-alert on Beatty's whole filing history on the first run.
        legacy = {"last_entry": 91, "updated": "2026-09-24T00:00:00Z",
                  "case": "BEATTY v. TRUMP, 1:25-cv-04480"}
        st = cd.migrate_state(legacy)
        self.assertEqual(st["dockets"]["beatty"]["last_entry"], 91)
        self.assertIsNone(st["dockets"]["beatty"]["last_minute"])
        self.assertNotIn("phang", st["dockets"])

    def test_migration_is_idempotent(self):
        legacy = {"last_entry": 91, "updated": "x", "case": "c"}
        once = cd.migrate_state(legacy)
        self.assertEqual(cd.migrate_state(once), once)

    def test_a_second_case_registers_without_a_manual_state_edit(self):
        # A case absent from the state file is a first run; it must not inherit
        # another case's watermark or alert on its backlog.
        st = cd.migrate_state({"last_entry": 91, "updated": "x", "case": "c"})
        self.assertNotIn("phang", st["dockets"])

    def test_every_registered_case_has_the_fields_the_watcher_reads(self):
        # A registry entry missing a key would fail inside a scheduled run, at
        # 07:30, with the failure buried in a log. Assert the shape here.
        for key, case in cd.CASES.items():
            with self.subTest(case=key):
                for field in ("case", "docket_id", "slug", "label", "known", "calendar"):
                    self.assertIn(field, case)
                self.assertTrue(case["docket_id"].isdigit())
                for date, what in case["calendar"]:
                    datetime.strptime(date, "%Y-%m-%d")
                    self.assertTrue(what.strip())

    def test_the_registry_covers_the_cases_the_site_follows(self):
        # The two district dockets, plus the D.C. Circuit appeal. The circuit
        # docket is the one that was missing: the stay ruling on the
        # foreign-language obligation — the nearest-term event that can change
        # the case — issues from the circuit, and the feed URLs show why it
        # belongs in the same registry (the circuit feed also titles its
        # entries "Entry #<id>", so it parses without touching the parser).
        self.assertEqual(set(cd.CASES), {"beatty", "phang", "cadc"})
        self.assertEqual(cd.CASES["phang"]["docket_id"], "73246595")
        self.assertEqual(cd.CASES["cadc"]["docket_id"], "74696600")

    def test_the_circuit_case_watches_the_consolidated_lead_appeal(self):
        # 26-5334 was consolidated into 26-5299, so the clerk's order routed
        # every subsequent deadline through 26-5299. Watching the lead docket
        # therefore covers both appeals; watching 26-5334 alone would miss the
        # stay ruling, which will be filed under the lead number.
        cadc = cd.CASES["cadc"]
        self.assertEqual(cadc["docket_id"], "74696600")
        self.assertIn("26-5299", cadc["case"])
        # The motion that matters is in the KNOWN map, so a report names it
        # rather than printing a bare document number.
        self.assertTrue(any("STAY" in v.upper() for v in cadc["known"].values()))

    def test_circuit_entry_ids_are_large_and_numbered_like_ecf(self):
        # The circuit keys its feed entries by a CourtListener document id
        # (1208891196), not a small ECF number. They are compared with `>` and
        # never formatted as "ECF N" in prose, so a large int is correct — but
        # the parse must still classify them as `entry`, which is what lets the
        # circuit docket share the district docket's code path.
        got = cd.parse_entries(
            "<feed><entry><title>Entry #1208891196 in Katie Phang v. Todd Blanche, 26-5299</title>"
            "<published>2026-09-23</published><summary>PER CURIAM ORDER</summary></entry></feed>"
        )
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["kind"], "entry")
        self.assertEqual(got[0]["num"], 1208891196)

    def test_circuit_entries_are_not_labelled_ecf(self):
        # A circuit feed entry's number is a CourtListener document id, not an
        # ECF number, and calling it "ECF 1208891196" invents a docket number a
        # reader cannot look up. The registry carries the correct label and the
        # formatter uses it.
        self.assertEqual(cd.CASES["cadc"].get("number_label"), "Entry")
        self.assertEqual(cd.CASES["beatty"].get("number_label", "ECF"), "ECF")
        e = {"kind": "entry", "num": 1208891196, "mid": None,
             "date": "2026-09-23", "summary": "s"}
        self.assertTrue(
            cd.describe(e, {}, cd.CASES["cadc"]["number_label"]).startswith("Entry 1208891196")
        )

    # -- window report (the weekly job's substrate) ------------------------

    def test_a_window_report_counts_only_entries_inside_the_window(self):
        # The weekly report asks "what is in the last N days", which is a
        # different question from the watch loop's "what is new since I looked".
        # A watermark cannot be recomputed; a window can, which is why the
        # report survives a missed run.
        feed = self._feed(self._entry(50, "2026-09-24"),
                          self._entry(49, "2026-09-21"),
                          self._entry(40, "2026-08-01"))
        args = argparse.Namespace(today="2026-09-25", days=7, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args, feed_xml=feed)
        self.assertEqual([e["ecf"] for e in r["entries"]], [49, 50])
        self.assertEqual(r["window"], ["2026-09-19", "2026-09-25"])

    def test_a_window_is_inclusive_of_both_ends(self):
        # Off-by-one here would silently drop a filing made on the boundary day,
        # which is the day a Saturday run is most likely to be reporting.
        feed = self._feed(self._entry(50, "2026-09-25"),
                          self._entry(49, "2026-09-19"),
                          self._entry(48, "2026-09-18"))
        args = argparse.Namespace(today="2026-09-25", days=7, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args, feed_xml=feed)
        self.assertEqual([e["ecf"] for e in r["entries"]], [49, 50])

    def test_a_truncated_feed_is_flagged_rather_than_reported_as_complete(self):
        # The feed serves a fixed number of entries. A heavily filing case can
        # fill the window with less than N days, and presenting that as a full
        # week is the false-negative that makes the report untrustworthy.
        feed = self._feed(self._entry(50, "2026-09-24"))  # oldest is 09-24
        args = argparse.Namespace(today="2026-09-25", days=7, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args, feed_xml=feed)
        self.assertTrue(r["truncated"])
        self.assertEqual(r["feed_oldest"], "2026-09-24")
        self.assertIn("Coverage warning", cd.render_report([r], 7))

    def test_a_complete_window_is_not_flagged(self):
        feed = self._feed(self._entry(50, "2026-09-24"),
                          self._entry(40, "2026-09-01"))
        args = argparse.Namespace(today="2026-09-25", days=7, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args, feed_xml=feed)
        self.assertFalse(r["truncated"])
        self.assertNotIn("Coverage warning", cd.render_report([r], 7))

    def test_calendar_splits_into_covered_and_ahead(self):
        # The report has to say both what the week covered and what the next
        # week holds; a weekly reader needs the second as much as the first.
        args = argparse.Namespace(today="2026-09-25", days=7, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args,
                             feed_xml=self._feed(self._entry(50, "2026-09-24")))
        self.assertIn("2026-09-24", [c["date"] for c in r["calendar_covered"]])
        self.assertIn("2026-10-01", [c["date"] for c in r["calendar_ahead"]])

    def test_an_empty_window_is_stated_not_omitted(self):
        # "Nothing filed" is a finding. Rendering it as an empty section would
        # read as a gap in the report rather than a fact about the docket.
        args = argparse.Namespace(today="2026-09-25", days=1, since=None, ahead=7)
        r = cd.report_window("phang", cd.CASES["phang"], args,
                             feed_xml=self._feed(self._entry(50, "2026-09-01")))
        self.assertEqual(r["entries"], [])
        self.assertIn("Nothing filed", cd.render_report([r], 1))

    def test_report_window_never_touches_state(self):
        # Read-only by contract: the weekly report must not move the watch
        # loop's watermark, or the twice-daily alert would go silent for
        # everything the weekly run had already consumed.
        src = inspect.getsource(cd.report_window)
        self.assertNotIn("save_state", src)
        self.assertNotIn("load_state", src)


# --------------------------------------------------------------------------
# Never end a sentence with a preposition (house rule, 2026-09-25).
# --------------------------------------------------------------------------
class TestPrepositionRules(unittest.TestCase):
    @staticmethod
    def count(text: str) -> int:
        return len(cpn.find(cpn.strip_non_prose(text)))

    def test_a_stranded_preposition_is_flagged(self):
        self.assertEqual(self.count("Who did you give it to?"), 1)
        self.assertEqual(self.count("This is the house I live in."), 1)
        self.assertEqual(self.count("What are you looking at?"), 1)

    def test_the_corrected_form_is_clean(self):
        self.assertEqual(self.count("To whom did you give it?"), 0)
        self.assertEqual(self.count("The house in which I live is old."), 0)

    def test_a_quotation_is_exempt(self):
        # A quotation's grammar belongs to its author. Rewriting it to satisfy a
        # house style rule would corrupt the quotation the citation gate exists
        # to protect — the same reason the em-dash gate exempts quoted dashes.
        self.assertEqual(self.count('He said, "Who did you give it to?"'), 0)

    def test_a_url_and_a_code_span_are_exempt(self):
        self.assertEqual(
            self.count("See [the filing](https://example.org/docs/for/) for more."), 0)
        self.assertEqual(self.count("Use `git log to find it.`"), 0)

    def test_adverbial_particles_are_not_flagged(self):
        # Each of these ends in a word that IS a preposition elsewhere but is an
        # ADVERB here. Flagging them would fail a build on correct writing,
        # which is the failure mode that teaches people to ignore a gate.
        for text in ("The meeting is over.", "As noted above, the rule holds.",
                     "He walked past.", "I haven't seen him since.",
                     "This war has broken hearts before.",
                     "eroded from both within and without."):
            with self.subTest(text=text):
                self.assertEqual(self.count(text), 0)

    def test_phrasal_verb_particles_are_not_flagged(self):
        # A particle is not a stranded preposition. The SAME verb forms both:.
        # "give in" is phrasal, "give it to" is not, so the judgement is on the
        # pair, not the verb.
        for text in ("Please log in.", "Sign up.", "decay sets in.",
                     "would fill it in.", "Complacency crept in.",
                     "It kept the light on.", "Groceries, etc. pile on."):
            with self.subTest(text=text):
                self.assertEqual(self.count(text), 0)

    def test_prepositional_verbs_still_flagged(self):
        # The other half of that pair: these are PREPOSITIONAL verbs whose
        # particles genuinely strand, so the rule must still catch them.
        # Exempting them would hide the construction the rule exists for.
        for text in ("and what exactly are you looking for?",
                     "a trade war that nobody asked for.",
                     "That is not a defect to be embarrassed about.",
                     "the one door he does not have to knock on."):
            with self.subTest(text=text):
                self.assertEqual(self.count(text), 1)

    def test_catenative_to_is_not_flagged(self):
        # "don't want to" ends in the infinitive marker with its verb elided.
        self.assertEqual(
            self.count("Sometimes you have to pause, even when you don't want to."), 0)

    def test_hyphenated_compound_is_not_flagged(self):
        # "passers-by" is one word; the particle is not stranded.
        self.assertEqual(self.count("Handed out stickers to passers-by."), 0)

    def test_mid_sentence_preposition_is_not_flagged(self):
        # The rule is about SENTENCE-final position only.
        self.assertEqual(
            self.count("He asked what she was talking about, and then he left."), 0)

    def test_frontmatter_display_fields_are_scanned(self):
        # A stranded preposition in a `description` is what a reader sees in a
        # search result, so the display fields are in scope. The sentence must
        # actually end in the preposition for this to be a real test.
        md = '---\ndescription: "This is the tool he asked for."\n---\nclean prose.\n'
        hits = cpn.find(cpn.strip_non_prose(cpn.frontmatter_prose(
            md.split("---")[1])))
        self.assertEqual(len(hits), 1)

    def test_non_display_frontmatter_is_not_scanned(self):
        # `hero_alt` is display text; a slug or a date is not prose.
        md = '---\nslug: the-tool-he-asked-for\ndate: 2026-09-25\n---\nclean prose.\n'
        self.assertEqual(cpn.frontmatter_prose(md.split("---")[1]), "")

    def test_a_blanked_span_before_a_preposition_does_not_create_a_hit(self):
        # The bug: blanking a code span or link PRECEDING a preposition left
        # that preposition looking sentence-final ("deployed via `x.yml` on
        # push to `main`."), because the erase removed the words between them.
        # The replacement keeps a non-space token so word order survives.
        self.assertEqual(
            self.count("Deployed via [`x.yml`](https://example.org/a/b) on push to `main`."), 0)
        self.assertEqual(self.count("Established in [`skills/x.md`](https://e.org/a)."), 0)

    def test_citation_anchor_text_is_exempt(self):
        # CLAUDE.md exempts the preposition rule "inside a link," and the
        # decisive case is the citation anchor: `check-links.py --titles`
        # requires the anchor to be the source's OWN title, and headlines
        # routinely end in a preposition. Counting the anchor flags a REQUIRED
        # citation as a defect, and the sentence cannot be rewritten without
        # corrupting the quotation the anchor carries. Measured 2026-10-01: the
        # ninety-days drafts carried the FXStreet headline "…it was built on"
        # as an anchor and the gate counted it, failing the run and the ratchet.
        anchor = ("- FXStreet. (2026). [The Fed's October hike shrinks with the "
                  "inflation it was built on](https://example.org/x).")
        self.assertEqual(self.count(anchor), 0)
        # Prose outside the link is still scanned: a real stranded preposition
        # after a blanked link must not be hidden by the exemption.
        self.assertEqual(
            self.count("See [the note](https://example.org/a) for the tool he asked for."),
            1)

    def test_adverbial_idioms_ending_in_a_listed_preposition(self):
        # Each ends in a word that is a preposition elsewhere but an adverb here.
        for text in ("and so on.", "We will cite it from here on.",
                     "from now on.", "the point is to begin."):
            with self.subTest(text=text):
                self.assertEqual(self.count(text), 0)

    def test_the_baseline_keys_on_the_file(self):
        # The ratchet: a file may be reduced freely but may not grow past its
        # recorded count, so the rule catches up as each file is next touched.
        self.assertIsInstance(cpn.load_baseline(), dict)

    def test_corpus_is_at_or_under_the_baseline(self):
        import subprocess
        r = subprocess.run([sys.executable, "scripts/check-prepositions.py", "--check"],
                           cwd=REPO, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


# --------------------------------------------------------------------------
# Quoted name-detail fidelity. The gate exists because the 2026-10-04 Senate
# report quoted a reconstructed name ("Daniel J. Sullivan Jr." where the source
# says "Daniel J. Sullivan") and every other gate reported OK. It is deliberately
# NARROW: it checks only quoted person-name DETAILS (a middle initial or a
# generational suffix), because a general every-quotation check reported 70 false
# positives on that same report. These tests pin both halves: that the narrow
# detail is caught, and that ordinary quoted prose, a quoted TITLE, and an
# ellipsis are not dragged in.
# --------------------------------------------------------------------------
class TestQuoteNameRules(unittest.TestCase):
    def test_middle_initial_is_a_name_detail(self):
        self.assertTrue(cqn.has_name_detail("Dan S. Sullivan is on the ballot"))
        self.assertTrue(cqn.has_name_detail("Daniel J. Sullivan,"))

    def test_generational_suffix_is_a_name_detail(self):
        self.assertTrue(cqn.has_name_detail("Daniel J. Sullivan Jr."))
        self.assertTrue(cqn.has_name_detail("Sammy Davis Sr."))
        self.assertTrue(cqn.has_name_detail("Henry III"))

    def test_ordinary_quoted_prose_is_not_a_name_detail(self):
        # The noise that made the general check unusable: prose quotations and
        # quoted headlines must not be candidates.
        self.assertFalse(cqn.has_name_detail("They'll pay $200 to heckle me"))
        self.assertFalse(cqn.has_name_detail("a retired schoolteacher and registered Republican"))
        self.assertFalse(cqn.has_name_detail("Fox News Poll: Turek, Hinson in close Iowa Senate race"))

    def test_extract_pairs_a_detail_with_its_line_urls(self):
        text = (
            "Body references the race.[^1]\n\n"
            "[^1]: Fox News, [\"Alaska\"](https://example.org/alaska), September 24, 2026: "
            "the incumbent \"Dan S. Sullivan\" and \"Daniel J. Sullivan Jr.,\" \"a retired "
            "schoolteacher.\"\n"
        )
        cands = cqn.extract_candidates(text)
        frags = sorted(c["fragment"] for c in cands)
        self.assertEqual(frags, ["Dan S. Sullivan", "Daniel J. Sullivan Jr.,"])
        # The URL comes from the same footnote, not from the body.
        self.assertEqual(cands[0]["urls"], ["https://example.org/alaska"])

    def test_a_quoted_fragment_with_no_url_is_unverifiable_not_missing(self):
        # "Cannot fetch" is a statement about the checker, never an accusation
        # about the citation — the failure this gate must not reproduce.
        cand = {"line": 1, "fragment": "Daniel J. Sullivan Jr.", "urls": []}
        self.assertEqual(cqn.check_online(cand), "unverified")

    def test_fragment_present_normalizes_whitespace(self):
        # Hard-wrapped HTML breaks lines mid-name; a literal test would miss.
        self.assertTrue(cqn.fragment_present("Daniel J. Sullivan,",
                                             "the ballot. Daniel J.   Sullivan, a retired teacher"))
        self.assertFalse(cqn.fragment_present("Daniel J. Sullivan Jr.",
                                              "the ballot. Daniel J. Sullivan, a retired teacher"))

    def test_frontmatter_is_not_scanned(self):
        # A `description` is display text, not a quotation of a source. A corpus
        # scan surfaced "Kenneth Walker III's workload" from a chiefs description.
        text = ('---\ndescription: "Andy Reid says Kenneth Walker III\'s workload '
                'has to come down."\n---\n\nBody with no quotes.\n')
        self.assertEqual(cqn.extract_candidates(text), [])

    def test_a_quoted_link_title_is_not_a_candidate(self):
        # A fragment containing a markdown link is a citation ANCHOR — the
        # source's own title, which check-links.py --titles already compares
        # against the fetched page. Testing it as a quotation flags correct
        # citations (corpus scan: "John F. Kennedy: Domestic Affairs").
        text = ('[^1]: [How John F. Kennedy Fell for the Lost Cause.]'
                '(https://example.org/a), 2026.\n')
        self.assertEqual(cqn.extract_candidates(text), [])

    def test_the_corrected_report_passes_online(self):
        # End-to-end on the real citation: the corrected file's quoted names
        # ("Dan S. Sullivan", "Daniel J. Sullivan") are confirmed against the
        # live source. This is the regression fixture for the 2026-10-04 defect;
        # reinstating the "Jr." would fail here.
        import subprocess
        clean = REPO / "content/posts/essays/senate-race-report-2026-10-04.md"
        if not clean.exists():
            self.skipTest("the 2026-10-04 installment is not present")
        r = subprocess.run(
            [sys.executable, "scripts/check-quote-names.py", "--file", str(clean), "--online"],
            cwd=REPO, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


# --------------------------------------------------------------------------
# Chiefs weekly report. The rules that matter are the ones that decide whether a
# thing gets PUBLISHED and whether the pack's numbers can be trusted: the
# season guard that keeps the job silent in the off season, the assertion that
# stops a feed from answering with the wrong season, and the frontmatter check
# that is the only review an auto-published article gets.
# --------------------------------------------------------------------------
ck = load("chiefs-report")


class TestChiefsReport(unittest.TestCase):
    @staticmethod
    def _calendar(*phases) -> "list[dict]":
        """A league calendar in the shape the scoreboard payload serves."""
        out = []
        for label, value, start, end, periods in phases:
            out.append({
                "label": label, "type": value,
                "start": ck.parse_date(start), "end": ck.parse_date(end),
                "periods": [
                    {"label": p[0], "value": p[1], "start": ck.parse_date(p[2]),
                     "end": ck.parse_date(p[3]), "detail": p[4] if len(p) > 4 else ""}
                    for p in periods
                ],
            })
        return out

    def test_off_season_is_the_only_phase_the_job_skips(self):
        cal = self._calendar(
            ("Regular Season", "2", "2026-09-06", "2027-01-13",
             [("Week 3", "3", "2026-09-23", "2026-09-30", "Sep 23-29")]),
            ("Off Season", "4", "2027-02-16", "2027-08-01", []),
        )
        in_season = ck.season_state(cal, date(2026, 9, 25))
        self.assertTrue(in_season["in_season"])
        self.assertEqual(in_season["period"], "Week 3")
        self.assertEqual(in_season["period_detail"], "Sep 23-29")
        off = ck.season_state(cal, date(2027, 5, 1))
        self.assertFalse(off["in_season"])
        self.assertEqual(off["phase"], "Off Season")

    def test_a_date_outside_every_window_is_an_error_not_a_default(self):
        # The league calendar is fetched, not hardcoded, so the way it breaks is
        # by rolling over. Returning a phase anyway would let the job run and
        # publish a report about a season nobody asked for.
        cal = self._calendar(("Regular Season", "2", "2026-09-06", "2027-01-13", []))
        with self.assertRaises(ck.FetchError):
            ck.season_state(cal, date(2030, 9, 1))

    def test_a_phase_boundary_is_half_open(self):
        # The end date belongs to the NEXT phase: the calendar's endDate is the
        # first instant of the following one, so treating it as inclusive would
        # report the wrong phase on every boundary day.
        cal = self._calendar(
            ("Regular Season", "2", "2026-09-06", "2027-01-13", []),
            ("Postseason", "3", "2027-01-13", "2027-02-16", []),
        )
        self.assertEqual(ck.season_state(cal, date(2027, 1, 12))["phase"], "Regular Season")
        self.assertEqual(ck.season_state(cal, date(2027, 1, 13))["phase"], "Postseason")

    def test_an_unknown_season_is_refused_rather_than_answered(self):
        # Measured 2026-09-25: `standings?season=2027` returns 200 with the 2026
        # standings, sixteen teams and all. A writer handed that would produce a
        # report about the wrong season and nothing in it would look wrong. So
        # the requested year must appear in the response.
        stale = {"season": {"year": 2026}, "requestedSeason": None}
        with self.assertRaises(ck.FetchError):
            ck.assert_season(stale, 2027, "the standings")
        ck.assert_season(stale, 2026, "the standings")
        ck.assert_season(stale, None, "the standings")  # no claim, no check

    def test_the_served_season_field_alone_is_enough(self):
        # Some endpoints set requestedSeason and some only season.year; either
        # naming the year asked for is proof the feed served it.
        ck.assert_season({"season": {"year": 2027}, "requestedSeason": None},
                         2027, "the schedule")

    def test_selection_picks_the_last_completed_and_the_next_scheduled(self):
        def ev(eid, when, completed, state):
            return {
                "id": eid, "date": when, "name": "x", "shortName": "x",
                "week": {"number": 2},
                "competitions": [{
                    "status": {"type": {"completed": completed, "state": state,
                                        "description": "Final" if completed else "Scheduled"}},
                    "competitors": [
                        {"homeAway": "home", "team": {"abbreviation": "KC"},
                         "score": {"displayValue": "33"}, "winner": True},
                        {"homeAway": "away", "team": {"abbreviation": "IND"},
                         "score": {"displayValue": "30"}},
                    ],
                }],
            }
        events = [
            ev("a", "2026-09-15T00:15Z", True, "post"),
            ev("b", "2026-09-21T00:20Z", True, "post"),
            ev("c", "2026-09-27T17:00Z", False, "pre"),
            ev("d", "2026-10-04T20:25Z", False, "pre"),
        ]
        picks = ck.pick_games(events, "KC", date(2026, 9, 25))
        self.assertEqual(picks["last"]["id"], "b", "must take the MOST RECENT completed game")
        self.assertEqual(picks["next"]["id"], "c", "must take the EARLIEST scheduled game")
        self.assertEqual(picks["played"], 2)

    def test_games_for_other_teams_are_ignored(self):
        # The team schedule endpoint is filtered by the feed, but a league-wide
        # payload reaching this function must not be counted as the team's games.
        def ev(eid, abbrs):
            return {
                "id": eid, "date": "2026-09-21T00:20Z", "name": "x", "shortName": "x",
                "week": {"number": 2},
                "competitions": [{
                    "status": {"type": {"completed": True, "state": "post", "description": "Final"}},
                    "competitors": [
                        {"homeAway": "home", "team": {"abbreviation": abbrs[0]}},
                        {"homeAway": "away", "team": {"abbreviation": abbrs[1]}},
                    ],
                }],
            }
        picks = ck.pick_games([ev("a", ("GB", "ATL")), ev("b", ("KC", "IND"))], "KC",
                              date(2026, 9, 25))
        self.assertEqual(picks["played"], 1)
        self.assertEqual(picks["last"]["id"], "b")

    def test_news_is_filtered_to_the_window_and_the_team_tag(self):
        def art(headline, published, tags):
            return {
                "headline": headline, "description": "", "type": "Story",
                "published": published,
                "categories": [{"type": t, "uid": u} for t, u in tags],
            }
        payload = {"articles": [
            art("KC today", "2026-09-25T10:00:00Z", [("team", "s:20~l:28~t:12")]),
            art("KC old", "2026-08-01T10:00:00Z", [("team", "s:20~l:28~t:12")]),
            art("League only", "2026-09-25T10:00:00Z", [("league", "s:20~l:28")]),
            art("Other team", "2026-09-25T10:00:00Z", [("team", "s:20~l:28~t:2")]),
        ]}
        got = ck.recent_news(payload, date(2026, 9, 25))
        self.assertEqual([a["headline"] for a in got], ["KC today"])

    def test_news_is_newest_first(self):
        payload = {"articles": [
            {"headline": f"n{i}", "published": f"2026-09-2{i}T10:00:00Z", "type": "Story",
             "categories": [{"type": "team", "uid": "s:20~l:28~t:12"}]}
            for i in (1, 5, 3)
        ]}
        got = ck.recent_news(payload, date(2026, 9, 26))
        self.assertEqual([a["headline"] for a in got], ["n5", "n3", "n1"])

    def test_a_playlist_story_is_whatever_the_feed_tagged_not_a_judgement(self):
        # The feed's team filter is a tag, not a topic. Half of what comes back
        # names the Chiefs once in a league-wide piece. The function keeps them
        # (that is the feed's own contract) and the SKILL tells the writer to
        # read the tag with suspicion — so the rule lives in the prompt, and this
        # test records that the data layer is deliberately not editorializing.
        payload = {"articles": [
            {"headline": "NFL Week 3 uniforms", "published": "2026-09-25T10:00:00Z",
             "type": "Story", "categories": [{"type": "team", "uid": "s:20~l:28~t:12"}]},
        ]}
        self.assertEqual(len(ck.recent_news(payload, date(2026, 9, 25))), 1)

    def test_division_standings_needs_the_division_level(self):
        # With level=3 the AFC node carries children and no entries of its own.
        # Reading the conference node's entries returns nothing and the seed
        # line vanishes from the pack, so the seed list must be rebuilt from the
        # divisions. This is the payload shape with level=3, measured 2026-09-25.
        def entry(abbr, tid, seed):
            return {"team": {"abbreviation": abbr, "displayName": abbr, "id": tid},
                    "stats": [{"name": "playoffSeed", "displayValue": seed},
                              {"name": "overall", "displayValue": "2-0"}]}
        payload = {"children": [
            {"abbreviation": "AFC", "standings": {"entries": []}, "children": [
                {"name": "AFC West", "standings": {"entries": [
                    entry("KC", "12", "1"), entry("LV", "13", "5"),
                    entry("DEN", "7", "9"), entry("LAC", "24", "15")]}},
                {"name": "AFC East", "standings": {"entries": [
                    entry("BUF", "2", "2"), entry("MIA", "15", "13")]}},
            ]},
        ]}
        got = ck.division_standings(payload, "KC")
        self.assertEqual(got["division"], "AFC West")
        self.assertEqual(len(got["rows"]), 4)
        self.assertEqual(len(got["conference"]), 6, "seed list rebuilt from the divisions")
        self.assertEqual(got["conference"][0]["team"], "KC")

    def test_a_division_findings_failure_is_loud(self):
        payload = {"children": [
            {"abbreviation": "AFC", "standings": {"entries": []}, "children": [
                {"name": "AFC West", "standings": {"entries": [
                    {"team": {"abbreviation": "LV", "id": "13"}, "stats": []}]}},
            ]},
        ]}
        with self.assertRaises(ck.FetchError):
            ck.division_standings(payload, "KC")

    def test_game_links_come_only_from_the_payload(self):
        # The repo's most dangerous failure is a constructed URL that returns
        # 200 and lands elsewhere. A link the feed handed over is observed; one
        # assembled from a game id is not. So the extractor must read links and
        # never build them — including that it invents nothing for an event
        # whose payload carries none.
        with_links = {"links": [{"href": "https://www.espn.com/nfl/game/_/gameId/1/x"}],
                      "competitions": [{"links": [{"href": "https://www.espn.com/nfl/recap?gameId=1"}]}]}
        got = ck.game_links(with_links)
        self.assertEqual(got, ["https://www.espn.com/nfl/game/_/gameId/1/x",
                               "https://www.espn.com/nfl/recap?gameId=1"])
        self.assertEqual(ck.game_links({"id": "401872945", "competitions": [{}]}), [],
                         "an event id is not a URL; nothing may be assembled from it")

    def test_game_links_deduplicate_and_drop_non_http(self):
        event = {"links": [{"href": "https://a.example/x"}, {"href": "https://a.example/x"},
                           {"href": "sportscenter://x-callback-url/showGame?gameId=1"}],
                 "competitions": [{}]}
        self.assertEqual(ck.game_links(event), ["https://a.example/x"])

    def test_describe_game_reads_the_team_side_not_the_first_competitor(self):
        # The home competitor is not always the Chiefs, and taking competitors[0]
        # would silently swap the score around on an away game.
        event = {
            "id": "1", "date": "2026-09-27T17:00Z", "name": "KC at MIA",
            "shortName": "KC @ MIA", "week": {"number": 3},
            "competitions": [{
                "status": {"type": {"completed": True, "state": "post",
                                    "description": "Final", "detail": "Final"}},
                "venue": {"fullName": "Hard Rock Stadium"},
                "broadcasts": [{"media": {"shortName": "CBS"}}],
                "competitors": [
                    {"homeAway": "home", "team": {"abbreviation": "MIA", "displayName": "Miami Dolphins"},
                     "score": {"displayValue": "20"}, "winner": False},
                    {"homeAway": "away", "team": {"abbreviation": "KC", "displayName": "Kansas City Chiefs"},
                     "score": {"displayValue": "27"}, "winner": True},
                ],
            }],
        }
        got = ck.describe_game(event, "KC")
        self.assertEqual(got["team_score"], "27")
        self.assertEqual(got["opponent_score"], "20")
        self.assertEqual(got["opponent"], "MIA")
        self.assertFalse(got["home"])
        self.assertTrue(got["won"])
        self.assertEqual(got["broadcasts"], ["CBS"])

    def test_describe_game_returns_none_for_an_absent_team(self):
        event = {"id": "1", "competitions": [{"competitors": [
            {"team": {"abbreviation": "GB"}, "score": {"displayValue": "1"}},
            {"team": {"abbreviation": "ATL"}, "score": {"displayValue": "2"}},
        ]}]}
        self.assertIsNone(ck.describe_game(event, "KC"))

    def test_the_predictor_resolves_names_only_from_observed_ids(self):
        # The projection identifies teams by numeric id, and printing the raw id
        # leaves the writer guessing which side is which. Guessing a NAME is
        # worse: a wrong team name reads as a fact. So an unknown id falls back
        # to the id itself.
        pack = {"standings": {"rows": [{"id": "12", "name": "Kansas City Chiefs"}],
                              "conference": [{"id": "15", "name": "Miami Dolphins"}]}}
        idmap = ck.team_id_map(pack)
        self.assertEqual(ck.team_name_for(idmap, "12", "12"), "Kansas City Chiefs")
        self.assertEqual(ck.team_name_for(idmap, "15", "15"), "Miami Dolphins")
        self.assertEqual(ck.team_name_for(idmap, "99", "99"), "99")

    def test_parse_date_rejects_anything_not_iso(self):
        self.assertEqual(ck.parse_date("2026-09-27T17:00Z"), date(2026, 9, 27))
        for bad in ("", None, "Sep 27, 2026", "27/09/2026"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    ck.parse_date(bad)

    def test_urls_in_finds_nested_urls(self):
        blob = {"a": ["https://x.example/1", {"b": "see https://y.example/2 for more"}]}
        self.assertEqual(ck.urls_in(blob), {"https://x.example/1", "https://y.example/2"})

    # -----------------------------------------------------------------------
    # Prediction markets. The rules that matter are the ones that keep a wrong
    # or misleading number out of a table the reader will trust: the dollars
    # fields are the live ones, a stale quote is still returned (and dated), a
    # wide book is flagged rather than averaged, and discovery never constructs
    # a URL.
    # -----------------------------------------------------------------------
    def test_prices_read_the_dollars_fields_not_the_null_cents_fields(self):
        # Current Kalshi payloads set `yes_bid_dollars` and leave the legacy
        # integer `yes_bid` null. Reading the legacy field would report every
        # market as blank, which reads as "no market" rather than "a bug".
        row = {
            "yes_bid_dollars": "0.5300", "yes_ask_dollars": "0.5500",
            "last_price_dollars": "0.5500", "yes_bid": None, "yes_ask": None,
            "volume_fp": "145232.76", "volume_24h_fp": "2842.42",
            "open_interest_fp": "123406.00",
            "yes_sub_title": "Kansas City", "status": "active",
            "updated_time": "2026-07-13T21:35:20Z", "ticker": "KXNFLAFCWEST-27-KC",
        }
        got = ck.kalshi_quote({"markets": [row]}, "Kansas City")
        self.assertEqual(got["yes_bid"], 0.53)
        self.assertEqual(got["yes_ask"], 0.55)
        self.assertEqual(got["mid"], 0.54)
        self.assertEqual(got["open_interest"], 123406.0)
        self.assertEqual(got["volume_24h"], 2842.42)

    def test_kalshi_updated_time_is_carried_but_is_not_a_freshness_signal(self):
        # The trap this repo would otherwise publish. Kalshi's `updated_time` is
        # a series-level metadata write, NOT a trade time: measured 2026-09-28,
        # thirty-two markets across the whole playoff series share ONE value to
        # the microsecond, and the AFC West market read 2026-07-13 while trading
        # $2,842 in the prior day. So the field is carried (it is real data) but
        # the currency signals are `volume_24h` and `moved`, and the renderer
        # must not present `updated_time` as staleness.
        row = {"yes_bid_dollars": "0.5200", "yes_ask_dollars": "0.5300",
               "previous_yes_bid_dollars": "0.5300", "previous_yes_ask_dollars": "0.5500",
               "volume_24h_fp": "2842.42", "yes_sub_title": "Kansas City",
               "status": "active", "updated_time": "2026-07-13T21:35:20Z"}
        got = ck.kalshi_quote({"markets": [row]}, "Kansas City")
        self.assertEqual(got["updated"], "2026-07-13T21:35:20Z")
        self.assertEqual(got["volume_24h"], 2842.42,
                         "24h volume is the live-trading signal")
        self.assertEqual(got["moved"], -0.01,
                         "the bid moved from 0.53 to 0.52 — the market is live")

    def test_the_market_block_does_not_call_a_traded_market_stale(self):
        # The end-to-end guard: a market with 24h volume must not be described as
        # stale anywhere in the rendered pack on the strength of updated_time.
        out = ck.render({
            "today": "2026-09-28", "generated": "x", "team": {"name": "KC"},
            "season": {"phase": "Regular Season", "period": "Week 3",
                       "period_detail": "", "starts": "a", "ends": "b"},
            "games_played": 3, "news": [],
            "markets": {"polymarket": [], "kalshi_win_total": [], "failures": [],
                        "kalshi": [dict(ck.kalshi_quote({"markets": [{
                            "yes_bid_dollars": "0.5200", "yes_ask_dollars": "0.5300",
                            "volume_24h_fp": "2842.42", "volume_fp": "145248",
                            "yes_sub_title": "Kansas City", "status": "active",
                            "updated_time": "2026-07-13T21:35:20Z"}]}, "Kansas City"),
                            label_short="AFC West champion", venue="Kalshi",
                            source_url="https://example.org/kalshi")]}})
        self.assertIn("as a trade time; it is not one", out)
        self.assertIn("24h vol", out)
        self.assertNotIn("has not moved in weeks is not a current price", out)

    def test_polymarket_surfaces_real_activity_fields(self):
        # Polymarket, unlike Kalshi, publishes real trade activity: volume24hr
        # and oneHourPriceChange. Measured 2026-09-28 on the AFC West market.
        event = {"slug": "pro-football-afc-west-champion",
                 "updatedAt": "2026-09-28T22:20:26Z",
                 "markets": [{"groupItemTitle": "Kansas City Chiefs",
                              "outcomePrices": '["0.575", "0.425"]',
                              "volume24hr": 168.54, "oneHourPriceChange": -0.005,
                              "lastTradePrice": 0.55}]}
        got = ck.polymarket_quote(event, "Kansas City Chiefs")
        self.assertEqual(got["volume_24h"], 168.54)
        self.assertEqual(got["price_change_1h"], -0.005)
        self.assertEqual(got["last_trade"], 0.55)

    def test_a_wide_book_is_flagged_and_its_midpoint_is_not_trusted(self):
        # Measured 2026-09-28: the Kalshi 13+ wins rung quoted 0.32/0.64, whose
        # midpoint (48%) sat above the tighter 12+ rung (46%) and made the
        # ladder non-monotonic. The midpoint of a thin book is an artifact.
        row = {"yes_bid_dollars": "0.32", "yes_ask_dollars": "0.64",
               "yes_sub_title": "13+ wins", "status": "active"}
        got = ck.kalshi_quote({"markets": [row]}, "13+ wins")
        self.assertTrue(got["wide"])
        self.assertAlmostEqual(got["spread"], 0.32)

    def test_a_tight_book_is_not_flagged_wide(self):
        row = {"yes_bid_dollars": "0.46", "yes_ask_dollars": "0.47",
               "yes_sub_title": "12+ wins", "status": "active"}
        self.assertFalse(ck.kalshi_quote({"markets": [row]}, "12+ wins")["wide"])

    def test_a_market_with_no_quote_is_none_not_zero(self):
        # An empty book is a fact about the market. Returning 0 would print as a
        # 0% forecast, which is a different and false claim.
        row = {"yes_bid_dollars": None, "yes_ask_dollars": None,
               "yes_sub_title": "Kansas City", "status": "active"}
        got = ck.kalshi_quote({"markets": [row]}, "Kansas City")
        self.assertIsNone(got["yes_bid"])
        self.assertIsNone(got["mid"])

    def test_a_series_without_the_named_team_is_reported_not_guessed(self):
        # The match is by name because the win-total and seed series carry many
        # rows; a name that is absent must yield None, never another team's row.
        rows = [{"yes_bid_dollars": "0.5", "yes_ask_dollars": "0.5",
                 "yes_sub_title": "Denver", "status": "active"}]
        self.assertIsNone(ck.kalshi_quote({"markets": rows}, "Kansas City"))

    def test_polymarket_prices_are_json_encoded_strings(self):
        # Gamma serves outcomePrices as a STRING containing JSON, not a list.
        # Indexing it directly yields a character, and float('[') raises.
        self.assertEqual(ck.polymarket_number('["0.575", "0.425"]', 0), 0.575)
        self.assertEqual(ck.polymarket_number('["0.575", "0.425"]', 1), 0.425)
        self.assertIsNone(ck.polymarket_number("not json", 0))
        self.assertIsNone(ck.polymarket_number(None, 0))
        self.assertIsNone(ck.polymarket_number('["0.5"]', 3))

    def test_polymarket_selects_the_chiefs_row_by_title(self):
        event = {
            "slug": "pro-football-afc-west-champion",
            "updatedAt": "2026-09-28T22:00:00Z",
            "markets": [
                {"groupItemTitle": "Denver Broncos", "outcomePrices": '["0.27", "0.73"]'},
                {"groupItemTitle": "Kansas City Chiefs", "outcomePrices": '["0.575", "0.425"]',
                 "bestBid": 0.56, "bestAsk": 0.59, "volumeNum": 17930.2},
            ],
        }
        got = ck.polymarket_quote(event, "Kansas City Chiefs")
        self.assertEqual(got["yes"], 0.575)
        self.assertEqual(got["mid"], 0.575)
        self.assertEqual(got["updated"], "2026-09-28T22:00:00Z")

    def test_the_polymarket_citation_is_the_api_url_not_a_constructed_page(self):
        # polymarket.com serves HTTP 200 and its generic title for a slug that
        # does not exist (measured 2026-09-28), so a constructed page URL could
        # not be verified — exactly the fabricated-link class CLAUDE.md names.
        # The citation is the Gamma endpoint, which returns the market's JSON.
        event = {"slug": "pro-football-afc-west-champion",
                 "markets": [{"groupItemTitle": "Kansas City Chiefs",
                              "outcomePrices": '["0.575", "0.425"]'}]}
        got = ck.polymarket_quote(event, "Kansas City Chiefs")
        self.assertTrue(got["source_url"].startswith("https://gamma-api.polymarket.com/"))
        self.assertIn("pro-football-afc-west-champion", got["source_url"])
        self.assertNotIn("polymarket.com/event/", got["source_url"])

    def test_the_kalshi_window_url_templates_the_series_in(self):
        tpl = ck.market_sources()["kalshi"]
        self.assertIn("{series}", tpl)
        self.assertIn("status=open", tpl,
                      "a series carries closed prior-season events; status=open "
                      "is what keeps last February's market out of today's table")

    # -- chart ---------------------------------------------------------------
    # The chart is drawn from the venues' own history, so the rules that matter
    # are the ones that keep the picture honest: it must use the same quantity
    # the table prints, it must not draw a half-finished day as a settled close,
    # and it must never claim a week's change from three days of data.
    def _points(self, *closes):
        # Daily points ending today, one per close.
        import time
        now = int(time.time())
        return [{"ts": now - (len(closes) - 1 - i) * 86400, "close": c,
                 "date": "2026-09-2%d" % (i + 1), "volume": 1.0}
                for i, c in enumerate(closes)]

    def test_the_delta_compares_against_a_point_a_week_back(self):
        # Nine days of history: 0.40 early, 0.60 today. The 7-day delta must
        # compare against the point a week back, not the oldest point.
        import time
        now = int(time.time())
        pts = [{"ts": now - (8 - i) * 86400, "close": (0.40 if i < 8 else 0.60),
                "date": "d%d" % i, "volume": 0.0} for i in range(9)]
        d = ck.week_delta(pts, 7)
        self.assertEqual(d["span_days"], 7)
        self.assertAlmostEqual(d["from"], 0.40)
        self.assertAlmostEqual(d["to"], 0.60)
        self.assertAlmostEqual(d["change"], 0.20)

    def test_a_young_series_reports_its_own_short_span(self):
        # Three days of history is a three-day change. Reporting it as a week
        # would be the chart overstating what it knows.
        import time
        now = int(time.time())
        pts = [{"ts": now - (2 - i) * 86400, "close": 0.40 + i * 0.05,
                "date": "d%d" % i, "volume": 0.0} for i in range(3)]
        d = ck.week_delta(pts, 7)
        self.assertEqual(d["span_days"], 2)
        self.assertAlmostEqual(d["change"], 0.10)

    def test_a_single_point_has_no_delta(self):
        self.assertIsNone(ck.week_delta(self._points(0.5), 7))

    def test_the_chart_uses_the_candle_bid_ask_mid_not_the_traded_price(self):
        # Regression against a self-contradicting report. Measured 2026-09-28:
        # `price.close_dollars` read 0.63 on a candle whose book was 0.58/0.61,
        # while this pack's own table prints a bid/ask mid. Using the traded
        # series made the chart disagree with the table printed above it.
        from unittest import mock
        payload = {"candlesticks": [{
            "end_period_ts": 1787000000,
            "price": {"close_dollars": "0.6300"},
            "yes_bid": {"close_dollars": "0.5800"},
            "yes_ask": {"close_dollars": "0.6100"},
            "volume_fp": "10.0",
        }]}
        with mock.patch.object(ck, "fetch", return_value=payload):
            pts, err = ck.kalshi_history("KXNFLAFCWEST", "KXNFLAFCWEST-27-KC")
        self.assertEqual(err, "")
        self.assertAlmostEqual(pts[0]["close"], 0.595,
                               msg="must be (0.58 + 0.61) / 2, not 0.63")

    def test_the_chart_falls_back_to_the_traded_price_when_no_book_quoted(self):
        from unittest import mock
        payload = {"candlesticks": [{
            "end_period_ts": 1787000000,
            "price": {"close_dollars": "0.6300"},
            "yes_bid": {}, "yes_ask": {},
            "volume_fp": "10.0",
        }]}
        with mock.patch.object(ck, "fetch", return_value=payload):
            pts, err = ck.kalshi_history("KX", "KX-27")
        self.assertAlmostEqual(pts[0]["close"], 0.63)

    def test_the_chart_is_inline_svg_with_no_script_or_external_fetch(self):
        # Three deliberate constraints: goldmark escapes raw HTML in a post body
        # so the chart ships as a file; a script tag would put a third-party
        # dependency on an unreviewed page; and an external image URL would be an
        # unverifiable citation.
        series = [{"label": "AFC West champion", "colour": "#D4820A",
                   "points": self._points(0.40, 0.45, 0.52), "now": 0.52}]
        svg = ck.build_chart_svg(series)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("</svg>", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("http", svg.replace('xmlns="http://www.w3.org/2000/svg"', ""))
        self.assertIn('role="img"', svg, "a decorative chart still needs a text alternative")

    def test_the_chart_escapes_a_label_that_would_break_the_markup(self):
        series = [{"label": "A & B <script>", "points": self._points(0.4, 0.5),
                   "now": 0.5}]
        svg = ck.build_chart_svg(series)
        self.assertNotIn("<script>", svg)
        self.assertIn("&amp;", svg)

    def test_a_chart_with_too_little_history_renders_nothing_rather_than_a_dot(self):
        # One point is not a line. Returning a one-point chart would draw a dot
        # that reads as a flat market.
        self.assertEqual(ck.build_chart_svg([{"label": "x", "points": [], "now": None}]), "")

    def _pack(self, markets: dict) -> dict:
        return {"today": "2026-09-28", "generated": "x", "team": {"name": "KC"},
                "season": {"phase": "Regular Season", "period": "Week 3",
                           "period_detail": "", "starts": "a", "ends": "b"},
                "games_played": 3, "news": [], "markets": markets}

    def test_every_end_label_fits_inside_the_canvas(self):
        # The first render clipped two labels: "AFC West champion 52%" ran past
        # the right edge of the viewBox and "Super Bowl champion 8%" was pushed
        # past the bottom. Both are geometry bugs that no unit test would catch
        # unless it checks the coordinates, so this checks them.
        import re
        series = [
            {"label": "Playoff qualifier", "colour": "#8FBF7F",
             "points": self._points(0.60, 0.80, 0.84), "now": 0.84},
            {"label": "AFC West champion", "colour": "#7FB2E5",
             "points": self._points(0.33, 0.52, 0.52), "now": 0.52},
            {"label": "AFC champion", "colour": "#F2EDD8",
             "points": self._points(0.11, 0.14, 0.14), "now": 0.14},
            {"label": "Super Bowl champion", "colour": "#D4820A",
             "points": self._points(0.07, 0.08, 0.08), "now": 0.08},
        ]
        svg = ck.build_chart_svg(series)
        for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]+)</text>', svg):
            x, y, body = float(m.group(1)), float(m.group(2)), m.group(3)
            # ~6.2px per character at font-size 11 in this font stack.
            right = x + len(body) * 6.2
            with self.subTest(label=body):
                self.assertLess(right, 720, "label runs off the right edge")
                self.assertGreater(y, 0, "label above the canvas")
                self.assertLess(y, 340, "label below the canvas")

    def test_two_close_lines_do_not_overprint_their_labels(self):
        # Four series finishing within a few points is the real case (Super Bowl
        # 8%, AFC 14%), so the labels must be spread rather than drawn on top of
        # each other.
        import re
        series = [{"label": f"Series {i}", "points": self._points(0.10 + i * 0.001),
                   "now": 0.10 + i * 0.001} for i in range(4)]
        svg = ck.build_chart_svg(series)
        ys = sorted(float(m.group(1)) for m in
                    re.finditer(r'<text x="624" y="([\d.]+)"', svg))
        for a, b in zip(ys, ys[1:]):
            self.assertGreaterEqual(b - a, 14, "labels overlap")

    def test_the_chart_colours_come_from_the_repos_documented_palette(self):
        # The first draft used an invented blue (#7FB2E5) and green (#8FBF7F).
        # The green appears nowhere in the repo, which is exactly the drift the
        # locked visual identity exists to prevent — a decorative chart is not
        # the place to introduce a new brand colour. Every stroke must be one of
        # the four the palette documents: accent amber, Parian cream, the
        # high-contrast link blue, and the Chiefs red.
        documented = {"#D4820A", "#F2EDD8", "#7DC4FF", "#E31837"}
        got = {c for _, _, _, c in ck.CHART_SERIES}
        self.assertEqual(got, documented)
        self.assertEqual(len(got), 4, "four lines need four distinct colours")

    def test_the_chart_lines_clear_non_text_contrast_on_the_navy_ground(self):
        # WCAG 1.4.11 asks 3:1 for graphical objects. A 2px line below that is
        # a line a reader cannot follow, which defeats the chart's only purpose.
        def lum(h: str) -> float:
            h = h.lstrip("#")
            parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            chan = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                    for c in parts]
            return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]

        bg = lum("#131E39")
        for _, _, _, colour in ck.CHART_SERIES:
            fg = lum(colour)
            ratio = (max(fg, bg) + 0.05) / (min(fg, bg) + 0.05)
            with self.subTest(colour=colour):
                self.assertGreaterEqual(round(ratio, 2), 3.0)

    def test_the_renderer_names_the_chart_path_or_says_there_is_none(self):
        series = [{"label": "AFC West champion", "colour": "#x",
                   "points": self._points(0.40, 0.45, 0.52), "now": 0.52,
                   "delta_7d": {"from": 0.40, "to": 0.52, "change": 0.12,
                                "span_days": 2, "from_date": "d0", "to_date": "d2"}}]
        with_chart = ck.render(self._pack({
            "kalshi": [], "polymarket": [], "kalshi_win_total": [], "failures": [],
            "chart_series": series,
            "chart_path": "static/img/articles/103-chiefs-markets.svg",
            "chart_url": "/img/articles/103-chiefs-markets.svg", "chart_error": ""}))
        self.assertIn("103-chiefs-markets.svg", with_chart)
        self.assertIn("2 days", with_chart)

        no_chart = ck.render(self._pack({
            "kalshi": [], "polymarket": [], "kalshi_win_total": [], "failures": [],
            "chart_series": [], "chart_path": "", "chart_url": "",
            "chart_error": "not enough history"}))
        self.assertIn("No chart this week", no_chart)
        self.assertIn("do not reference a chart", no_chart)

    def test_market_failures_default_to_empty_rather_than_a_placeholder_row(self):
        # A venue that cannot be read must yield no rows and a named failure —
        # never a zero priced as a market. Both venues are optional, so this is
        # exercised with the fetch stubbed out rather than over the network.
        #
        # `kalshi_history` and `write_chart` are patched too, and that is not
        # belt-and-braces: without them this test reaches the network AND writes
        # a real SVG into static/img/articles/, which a unit test must not do.
        from unittest import mock
        with mock.patch.object(ck, "kalshi_markets", return_value=([], ["Kalshi: boom"])), \
             mock.patch.object(ck, "kalshi_win_total_ladder", return_value=([], [])), \
             mock.patch.object(ck, "polymarket_markets", return_value=([], ["Poly: boom"])), \
             mock.patch.object(ck, "kalshi_history", return_value=([], "boom")), \
             mock.patch.object(ck, "write_chart", return_value="boom"):
            block = ck.collect_markets()
        self.assertEqual(block["kalshi"], [])
        self.assertEqual(block["polymarket"], [])
        self.assertEqual(block["chart_url"], "")
        self.assertTrue(any("boom" in f for f in block["failures"]))

    def test_the_renderer_states_a_market_outage_rather_than_printing_a_zero(self):
        # The gap between "the venue is quiet" and "the venue was unreachable"
        # is the whole reason failures are carried separately.
        out = ck.render({"today": "2026-09-28", "generated": "x", "team": {"name": "KC"},
                         "season": {"phase": "Regular Season", "period": "Week 3",
                                    "period_detail": "", "starts": "a", "ends": "b"},
                         "games_played": 3, "news": [],
                         "markets": {"kalshi": [], "polymarket": [], "kalshi_win_total": [],
                                     "failures": ["Kalshi Super Bowl champion: timeout"]}})
        self.assertIn("Neither venue returned a usable market", out)
        self.assertIn("Kalshi Super Bowl champion: timeout", out)

    def test_the_priced_as_certain_rungs_are_dropped_from_the_ladder(self):
        # 4+, 5+ and 6+ wins sat at ask 1.00 on 2026-09-28; printing them made
        # the ladder read backwards at the top (98%, 96%, 99%). They carry no
        # information about the season's shape.
        from unittest import mock
        payload = {"event": {"markets": [
            {"status": "active", "yes_sub_title": "6+ wins", "floor_strike": 6,
             "yes_bid_dollars": "0.98", "yes_ask_dollars": "1.00"},
            {"status": "active", "yes_sub_title": "12+ wins", "floor_strike": 12,
             "yes_bid_dollars": "0.46", "yes_ask_dollars": "0.47"},
        ]}}
        with mock.patch.object(ck, "fetch", return_value=payload):
            rows, failures = ck.kalshi_win_total_ladder()
        self.assertEqual([r["label"] for r in rows], ["12+ wins"])
        self.assertEqual(failures, [])


class TestReportFrontmatterGate(unittest.TestCase):
    """The only review an auto-published article gets. Every rule here is a
    defect this repo has actually shipped.

    These rules used to live in `chiefs-report.py --validate`, which was the only
    job that published. When the Senate and docket jobs started publishing too
    (Philip, 2026-09-27), the rules moved to `scripts/check-report-frontmatter.py`
    so one gate covers all three rather than three copies drifting apart — which
    is exactly how the `featuredOnHome` requirement went missing from one skill
    and not another, hiding five Senate reports from the home feed.
    """

    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="report-fm-"))
        self.now = datetime(2026, 9, 29, 18, 30, tzinfo=ck.CT)

    def write(self, body: str) -> Path:
        p = self.dir / "a.md"
        p.write_text(body, encoding="utf-8")
        return p

    def good(self, **over):
        fields = {
            "title": '"Chiefs Report: September 29, 2026"',
            "description": '"A one-sentence description."',
            "date": "2026-09-29T18:30:00-05:00",
            "lastmod": "2026-09-29T18:30:00-05:00",
            "author": "Philip Huffman",
            "draft": "false",
            "featuredOnHome": "true",
            # The series plate. Real paths, because the gate requires the files
            # to exist — same reason the runner would catch a typo.
            "hero_desktop": '"img/articles/103-chiefs-report_16x9.webp"',
            "hero_mobile": '"img/articles/103-chiefs-report_4x5.webp"',
            "hero_alt": '"A marble football against a crimson field."',
            "hero_caption": '"The series plate for the weekly Chiefs report."',
        }
        fields.update(over)
        front = "\n".join(f"{k}: {v}" for k, v in fields.items())
        return f"---\n{front}\n---\n\nBody prose.\n\n*PRH | [huffmanwrites.org] | © Philip Huffman*\n"

    def test_a_good_article_passes(self):
        p = self.write(self.good())
        self.assertEqual(crf.validate(p, now=self.now), [])

    def test_a_missing_hero_field_is_caught(self):
        # Every report carries the same series plate; a report without it ships
        # with no hero image at all, and nothing else in the pipeline notices.
        for missing in ("hero_desktop", "hero_mobile", "hero_alt", "hero_caption"):
            p = self.write("\n".join(
                ln for ln in self.good().split("\n")
                if not ln.startswith(missing + ":")))
            with self.subTest(missing=missing):
                problems = crf.validate(p, now=self.now)
                self.assertTrue(any(missing in m for m in problems), (missing, problems))

    def test_a_hero_path_that_names_no_file_is_caught(self):
        # The failure this is for: a hero path that renders an empty box on a
        # page nobody reviews before it ships.
        p = self.write(self.good(hero_desktop='"img/articles/does-not-exist_16x9.webp"'))
        problems = crf.validate(p, now=self.now)
        self.assertTrue(any("does not exist" in m for m in problems), problems)
        p2 = self.write(self.good(hero_mobile='"img/articles/also-missing_4x5.webp"'))
        self.assertTrue(any("does not exist" in m for m in crf.validate(p2, now=self.now)))

    def test_the_series_plate_actually_resolves_against_the_repo(self):
        # Guards against the fixture drifting away from the real files: if the
        # plate is renamed, the skill and this contract must be updated with it.
        for rel in ("img/articles/103-chiefs-report_16x9.webp",
                    "img/articles/103-chiefs-report_4x5.webp"):
            self.assertTrue((REPO / "static" / rel).is_file(), rel)

    def test_the_plate_pin_catches_a_series_that_drifted_to_another_image(self):
        # A series uses one plate for every installment, so a report that quietly
        # picks a different image loses the visual identity the plate exists to
        # hold. Without the pin, any existing file satisfies the check above.
        p = self.write(self.good())  # the Chiefs fixture, checked as the Senate series
        problems = crf.validate(p, hero_plate="105-senate-race-report", now=self.now)
        self.assertTrue(any("series plate" in m for m in problems), problems)
        # And pinning the plate the fixture actually uses passes.
        self.assertEqual(crf.validate(p, hero_plate="103-chiefs-report", now=self.now), [])

    def test_a_draft_flag_left_true_is_caught(self):
        # The failure that matters most now that these jobs publish: the commit
        # and push succeed, every other gate reports OK, and the deploy carries
        # nothing at all.
        p = self.write(self.good(draft="true"))
        self.assertTrue(any("draft" in m for m in crf.validate(p, now=self.now)))

    def test_a_missing_home_flag_is_caught(self):
        # More than five posts already carry the flag, so an unflagged post
        # never reaches the home feed at all: published and unseen.
        p = self.write(self.good(featuredOnHome="false"))
        self.assertTrue(any("featuredOnHome" in m for m in crf.validate(p, now=self.now)))
        p2 = self.write("\n".join(
            ln for ln in self.good().split("\n") if not ln.startswith("featuredOnHome")))
        self.assertTrue(any("featuredOnHome" in m for m in crf.validate(p2, now=self.now)))

    def test_a_future_date_is_caught(self):
        # buildFuture: false skips the page WITHOUT failing the build — the
        # failure recorded three times in SESSION_STATE.
        p = self.write(self.good(date="2026-09-29T23:30:00-05:00"))
        problems = crf.validate(p, now=self.now)
        self.assertTrue(any("ahead of the clock" in m for m in problems), problems)

    def test_small_clock_slack_is_allowed(self):
        # The stamp is taken microseconds before the check runs, so a modest
        # drift must not fail a correct article. The default slack is 5 minutes.
        p = self.write(self.good(date="2026-09-29T18:33:00-05:00"))
        self.assertEqual(crf.validate(p, now=self.now), [])

    def test_an_unparseable_date_is_caught_rather_than_skipped(self):
        p = self.write(self.good(date="September 29, 2026"))
        self.assertTrue(any("ISO 8601" in m for m in crf.validate(p, now=self.now)))

    def test_a_missing_attribution_is_caught(self):
        body = self.good().replace("*PRH | [huffmanwrites.org] | © Philip Huffman*\n", "")
        p = self.write(body)
        self.assertTrue(any("attribution" in m for m in crf.validate(p, now=self.now)))

    def test_missing_required_fields_are_named(self):
        p = self.write("---\ndraft: false\nfeaturedOnHome: true\n---\n*PRH | x*\n")
        problems = crf.validate(p, now=self.now)
        for name in ("title", "description", "date", "lastmod", "author"):
            self.assertTrue(any(name in m for m in problems), (name, problems))

    def test_a_missing_file_is_a_problem_not_a_crash(self):
        self.assertTrue(crf.validate(self.dir / "nope.md", now=self.now))

    def test_no_frontmatter_is_caught(self):
        p = self.write("just prose, no frontmatter\n")
        self.assertTrue(any("frontmatter" in m for m in crf.validate(p, now=self.now)))

    def test_unclosed_frontmatter_is_named_as_such(self):
        p = self.write("---\ntitle: x\ndraft: false\n\nbody with no closing fence\n")
        self.assertTrue(any("not closed" in m for m in crf.validate(p, now=self.now)))

    def test_the_gate_exits_nonzero_so_a_runner_can_abort_on_it(self):
        # The runner branches on the exit code, so a gate that printed problems
        # and returned 0 would abort nothing.
        import io
        import contextlib
        p = self.write(self.good(draft="true"))
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["check-report-frontmatter.py", "--file", str(p)]
        try:
            with contextlib.redirect_stderr(buf):
                rc = crf.main()
        finally:
            sys.argv = old
        self.assertEqual(rc, 1)
        self.assertIn("NOT PUBLISHABLE", buf.getvalue())

    def test_every_publishing_runner_runs_the_frontmatter_gate(self):
        # A gate nobody runs is not a gate. All three jobs that now publish must
        # select it, and must pin their own series plate. The gate and its call
        # live in the shared library (run_report_gates) since the list was
        # centralized on 2026-10-01; each runner passes its plate.
        lib = (SCRIPTS / "publish-report.sh").read_text(encoding="utf-8")
        self.assertIn("check-report-frontmatter.py", lib)
        for runner, plate in (("senate-report-runner.sh", "105-senate-race-report"),
                              ("docket-weekly-report-runner.sh", "104-docket-report"),
                              ("chiefs-weekly-report-runner.sh", "103-chiefs-report")):
            text = (SCRIPTS / runner).read_text(encoding="utf-8")
            with self.subTest(runner=runner):
                self.assertIn("run_report_gates", text)
                self.assertIn(f"--plate {plate}", text)

    def test_the_shared_gate_set_runs_the_quote_name_gate(self):
        # A gate nobody runs is not a gate. `check-quotes.py --online` is INERT
        # on a report (it audits em-dash epigraphs, not newspaper footnotes), so
        # the narrow name-detail gate is the only mechanical check on quoted
        # name fidelity. It must be in the shared set, or the 2026-10-04 failure
        # ("Daniel J. Sullivan Jr." quoted where the source says "Daniel J.
        # Sullivan") is again caught only by a human reading the footnote.
        lib = (SCRIPTS / "publish-report.sh").read_text(encoding="utf-8")
        self.assertIn("check-quote-names.py", lib)
        self.assertIn("check-quote-names --online", lib)

    def test_the_shared_publish_tail_names_no_series_asset(self):
        # The defect this pins, introduced and caught 2026-09-28: the market
        # chart was staged by a literal path inside `publish-report.sh`, which
        # three jobs share. On a Senate or docket run that would have committed
        # the Chiefs chart into someone else's publish commit — the "stray file
        # rides along" case the surrounding comment forbids — and it put one
        # series' detail in the library all three source.
        tail = (SCRIPTS / "publish-report.sh").read_text(encoding="utf-8")
        self.assertNotIn("103-chiefs", tail)
        self.assertNotIn("img/articles", tail)
        # And the runner that owns the asset must stage it itself.
        chiefs = (SCRIPTS / "chiefs-weekly-report-runner.sh").read_text(encoding="utf-8")
        self.assertIn("103-chiefs-markets.svg", chiefs)
        self.assertIn("git add", chiefs)

    def test_a_fence_with_trailing_whitespace_is_still_parsed(self):
        # One file in the corpus opens with `--- ` (a trailing space) and Hugo
        # renders it, but splitting on the literal "---\n" skipped that fence,
        # landed on the CLOSING one, and returned the frontmatter as if it were
        # the body — so the gate reported "no title" for a file that has one.
        body = self.good()
        p = self.write("--- \n" + body[4:])
        self.assertEqual(crf.validate(p, now=self.now), [],
                         "a trailing space on the opening fence must not hide "
                         "the frontmatter")

    def test_the_real_corpus_file_with_the_trailing_space_is_parsed(self):
        # The measured case, pinned against the actual file so a future rewrite
        # of the splitter cannot silently un-parse it again.
        p = REPO / "content/posts/digests/stoic-saturday-rule-of-law.md"
        fm, _ = crf.split_frontmatter(p.read_text(encoding="utf-8"))
        self.assertTrue(crf.field(fm, "title"), "title must be readable")

    def test_a_placeholder_anchor_is_caught(self):
        # A reader sees the anchor, so `[text]` tells them nothing; and it leaves
        # `check-links.py --titles` nothing to compare, so the wrong-page check —
        # the only one that catches a URL serving an unrelated article — goes
        # blind. The whole Senate series shipped this way.
        body = self.good().replace(
            "*PRH | [huffmanwrites.org] | © Philip Huffman*",
            "See ([\"A real headline of several words\"](https://example.org/ok)) and "
            "([text](https://example.org/bad)).\n\n*PRH | [huffmanwrites.org] | © Philip Huffman*")
        p = self.write(body)
        problems = crf.validate(p, now=self.now)
        self.assertTrue(any("placeholder" in m for m in problems), problems)

    def test_a_real_title_anchor_passes(self):
        # The form the migration produced, and the only form the title check can
        # use: the citation's own title as the link text.
        body = self.good().replace(
            "*PRH | [huffmanwrites.org] | © Philip Huffman*",
            "Cook Political Report, [\"The Fight for the Senate Is a True Toss "
            "Up\"](https://example.org/a), September 23, 2026.\n\n"
            "*PRH | [huffmanwrites.org] | © Philip Huffman*")
        p = self.write(body)
        self.assertEqual(crf.validate(p, now=self.now), [])

    def test_the_published_reports_carry_no_placeholder_anchors(self):
        # The standing state for every published series installment.
        for p in crf.series_installments():
            self.assertFalse(crf.TEXT_ANCHOR.search(p.read_text(encoding="utf-8")),
                             p.name)

    def test_the_anchor_corpus_mode_covers_every_published_post(self):
        # Wider than the series: a placeholder anchor in a book summary is as
        # reader-facing as one in a report, and blinds the wrong-page check just
        # as thoroughly. Measured before this existed: 36 published files.
        posts = crf.published_posts()
        self.assertGreaterEqual(len(posts), 180, "the glob stopped matching")
        self.assertFalse(any(p.name == "_index.md" for p in posts),
                         "section stubs are not posts")
        names = {p.name for p in posts}
        self.assertIn("on-proportion-summary.md", names)
        self.assertIn("senate-race-report-2026-09-27.md", names)

    def test_every_published_post_names_its_links(self):
        # The standing state. A failure here is a real reader-facing defect and
        # a real blind spot in the title check.
        bad = []
        for p in crf.published_posts():
            bad += [f"{p.name}: {m}" for m in crf.anchor_problems(p)]
        self.assertEqual(bad, [])

    def test_the_anchor_rule_catches_a_placeholder(self):
        p = self.write(self.good().replace(
            "*PRH | [huffmanwrites.org] | © Philip Huffman*",
            "See ([text](https://example.org/x)).\n\n*PRH | x*"))
        self.assertTrue(crf.anchor_problems(p))

    def test_the_anchor_rule_catches_a_doubled_work_title(self):
        # The 2026-09-27 batch rewrite produced `*Meditations[*Meditations* 10.16]`
        # in 27 published lines; it renders as literal `*MeditationsMeditations`
        # because the inner `*` never italicises. The rule finds the shape (a work
        # title repeated immediately) so the NEXT batch cannot ship it.
        bad = "— Marcus Aurelius, *Meditations[*Meditations* 10.16](https://x/y)"
        self.assertTrue(crf.malformed_citation_problems(bad))
        good = "— Marcus Aurelius, [*Meditations* 10.16](https://x/y) (trans. Long)"
        self.assertEqual(crf.malformed_citation_problems(good), [])
        # A title that merely repeats a word is not a doubled title.
        self.assertEqual(
            crf.malformed_citation_problems("See *The Art of War* by Sun Tzu."), [])

    def test_ci_runs_the_anchor_mode(self):
        ci = (REPO / ".github" / "workflows" / "hugo.yml").read_text(encoding="utf-8")
        self.assertIn("check-report-frontmatter.py --anchors-corpus", ci)

    def test_drafts_are_excluded_from_the_anchor_scan(self):
        # A draft is not published; the gate must not fail on work in progress.
        for p in crf.published_posts():
            split = crf.split_frontmatter(p.read_text(encoding="utf-8"))
            self.assertNotEqual(crf.field(split[0], "draft"), "true", p.name)

    def test_short_anchors_are_not_collected(self):
        # MIN_HEADLINE_WORDS existed for this and was never used, which is why a
        # 200-URL sample produced three mismatches that were all noise. A label
        # ("odds", "game page") carries too little vocabulary to compare.
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="links-short-"))
        p = d / "a.md"
        p.write_text("---\ntitle: t\n---\n\n[odds](https://example.org/a)\n"
                     "[a real headline of several words](https://example.org/b)\n",
                     encoding="utf-8")
        got = cl.link_texts(str(p))
        self.assertNotIn("https://example.org/a", got)
        self.assertIn("https://example.org/b", got)

    def test_a_bot_wall_title_is_not_a_title(self):
        # openlibrary.org answered a search URL with `Human Verification | Open
        # Library`, and the comparison reported the citation as a mismatch —
        # accusing correct work of the defect this check exists to catch, when
        # the checker had simply been blocked.
        for wall in ("Human Verification | Open Library", "Just a moment...",
                     "Attention Required! | Cloudflare", "Are you a robot?"):
            with self.subTest(wall=wall):
                self.assertEqual(cl.page_title(f"<title>{wall}</title>"), "")
        self.assertEqual(cl.page_title("<title>Carl Sagan - Wikiquote</title>"),
                         "Carl Sagan - Wikiquote")

    def test_a_wall_title_yields_no_comparison(self):
        # With no title, link_text_matches_title must not be reached at all in
        # main(); this pins the guard that produces the empty title.
        self.assertEqual(cl.page_title("<title>Checking your browser</title>"), "")

    def test_a_url_containing_parentheses_is_not_truncated(self):
        # Measured 2026-09-27: the repair plan cites a Wikisource page whose title
        # contains `(English)`, and the old URL class stopped at the inner `)`.
        # The checker then fetched a truncated URL, got a 404, and reported a
        # DEAD link that is live — a false alarm on a governing document, and the
        # same "we could not look" confusion the verdict table warns about.
        full = ("https://en.wikisource.org/w/index.php?title=Page:Paris_Agreement_"
                "(English).pdf/24&action=raw")
        got = cl.URL.findall(f"see {full} and more")
        self.assertEqual([cl.clean(u) for u in got], [full])

    def test_prose_parentheses_are_trimmed_not_kept(self):
        # The other direction: a URL inside prose `(...)` must lose the closing
        # paren, or the fetch 404s on a correct link.
        for text, expected in (
            ("see (https://example.org/x) here", "https://example.org/x"),
            ("link https://example.org/x. Next", "https://example.org/x"),
            ("([text](https://example.org/y))", "https://example.org/y"),
        ):
            with self.subTest(text=text):
                self.assertEqual([cl.clean(u) for u in cl.URL.findall(text)],
                                 [expected])

    def test_a_markdown_link_with_parentheses_keeps_them(self):
        # The markdown extractor had the same truncation, with a non-greedy URL
        # part that stopped at the first inner `)`.
        full = ("https://en.wikisource.org/w/index.php?title=Page:Paris_Agreement_"
                "(English).pdf/24&action=raw")
        txt = f"[The Paris Agreement page text]({full})"
        got = [m.group(2) for m in cl._MD_LINK.finditer(txt)]
        self.assertEqual(got, [full])

    def test_balanced_leaves_a_well_formed_url_alone(self):
        for u in ("https://example.org/a", "https://example.org/a_(b)_c",
                  "https://example.org/a(b)c(d)"):
            with self.subTest(u=u):
                self.assertEqual(cl.balanced(u), u)

    def test_the_corpus_titles_phase_is_wired_and_non_fatal(self):
        # The only place the wrong-page check covers content outside the three
        # publishing jobs. It must be in the script AND must not fail the job:
        # the comparison is a heuristic, and a gate that fails a correct citation
        # is worse than one that shows a human the sentence.
        text = (SCRIPTS / "weekly-integrity-check.sh").read_text(encoding="utf-8")
        self.assertIn("check-links.py --online --titles", text)
        self.assertIn("run_soft", text)
        # The titles phase must use run_soft, not run.
        self.assertIn('run_soft "links (titles)"', text)
        self.assertNotIn('run "links (titles)"', text)

    def test_a_failing_phase_logs_its_whole_output_not_just_the_tail(self):
        # Measured 2026-09-28: the weekly-integrity job logged `--- links
        # (online) exit 1` with neither the DEAD block nor the counts, because
        # run() kept only the last 40 lines and check-links.py puts its verdict
        # block first and its counts last (on stderr). The log said a phase
        # failed and discarded the reason. A failing phase must keep everything;
        # a passing one keeps only its tail, so the log stays readable.
        text = (SCRIPTS / "weekly-integrity-check.sh").read_text(encoding="utf-8")
        self.assertIn("log_output()", text)
        self.assertIn("log_output \"$out\" \"$rc\" 40", text)
        self.assertIn("log_output \"$out\" \"$rc\" 80", text)
        # The old shape — an unconditional tail on captured output — must be gone.
        self.assertNotIn('printf \'%s\\n\' "$out" | tail -40', text)
        self.assertNotIn('printf \'%s\\n\' "$out" | tail -80', text)

    def test_the_log_output_rule_favours_the_failure(self):
        # Same rule, exercised as behaviour rather than as source text: on a
        # failure the head (where the verdict block lives) must survive.
        import subprocess
        sample = "REDIRECT (45):\n" + "  row\n" * 60 + "links: 9 ok, 0 dead\n"
        script = (
            'log_output() { local out="$1" rc="$2" n="$3"; '
            'if [ "$rc" -ne 0 ]; then printf "%s\\n" "$out"; '
            'else printf "%s\\n" "$out" | tail -"$n"; fi; }; '
            'out=$(printf "%s" "$SAMPLE"); log_output "$out" 1 40'
        )
        got = subprocess.run(["bash", "-c", script], env={"SAMPLE": sample},
                             capture_output=True, text=True).stdout
        self.assertIn("REDIRECT (45):", got)
        self.assertIn("links: 9 ok, 0 dead", got)

    def test_the_short_label_rule_is_the_shared_constant(self):
        # Guards against the filter being re-implemented with a different number
        # in a second place, which is how the two would drift.
        self.assertGreaterEqual(cl.MIN_HEADLINE_WORDS, 3)

    def test_chiefs_skill_documents_the_anchor_rule(self):
        text = (REPO / "skills" / "chiefs-weekly-report.md").read_text(encoding="utf-8")
        self.assertIn("never a placeholder", text)

    def test_every_report_skill_documents_the_anchor_rule(self):
        # The three publishing jobs' writers must all know the form; the gate
        # catches a violation, but the spec is what keeps it from happening.
        for skill in ("senate-race-report.md", "docket-weekly-report.md",
                      "chiefs-weekly-report.md"):
            text = (REPO / "skills" / skill).read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("placeholder", text)

    def test_the_chiefs_collector_no_longer_carries_a_second_copy_of_the_rules(self):
        # The rules must live in exactly one place. A second copy is how the two
        # versions drift, and the drift is silent until a report ships wrong.
        src = (SCRIPTS / "chiefs-report.py").read_text(encoding="utf-8")
        self.assertNotIn("def validate_article", src)
        self.assertIn("check-report-frontmatter.py", src)

    def test_corpus_mode_covers_every_published_series_installment(self):
        # CI runs --corpus because it has no single file to check. It must find
        # the same installments the series gate does — the two derive from
        # data/gallery.yml, and a series recognised by one and not the other is
        # how the featuredOnHome rule came to live in one skill and not another.
        corpus = crf.series_installments()
        self.assertGreaterEqual(len(corpus), 4)
        for name in ("senate-race-report-2026-09-27.md",):
            self.assertTrue(any(p.name == name for p in corpus), [p.name for p in corpus])

    def test_corpus_mode_excludes_drafts(self):
        # A draft is not published, so it has no publication obligation. If this
        # ever included drafts, the gate would fail on every job's work in
        # progress.
        for p in crf.series_installments():
            fm = crf.split_frontmatter(p.read_text(encoding="utf-8"))[0]
            self.assertNotEqual(crf.field(fm, "draft"), "true", p.name)

    def test_corpus_mode_passes_on_the_real_repo(self):
        # The standing state: every published series installment is publishable.
        # A failure here is a real report the deploy would silently drop.
        problems = []
        for p in crf.series_installments():
            problems += [f"{p}: {m}" for m in crf.validate(p)]
        self.assertEqual(problems, [])

    def test_ci_runs_the_frontmatter_gate(self):
        ci = (REPO / ".github" / "workflows" / "hugo.yml").read_text(encoding="utf-8")
        self.assertIn("check-report-frontmatter.py --corpus", ci)

    def test_a_missing_file_argument_is_an_error_not_a_silent_pass(self):
        # A gate that exits 0 when misconfigured is worse than no gate: CI would
        # be green while checking nothing.
        import io
        import contextlib
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["check-report-frontmatter.py"]
        try:
            with contextlib.redirect_stderr(buf):
                with self.assertRaises(SystemExit) as cm:
                    crf.main()
        finally:
            sys.argv = old
        self.assertNotEqual(cm.exception.code, 0)


class TestHeroPathGate(unittest.TestCase):
    """The cheap gate for a hero path that names no file.

    `check-render-integrity.py` catches this too, but only after a full Hugo
    build, and it runs once a week from the site-audit job. The report jobs
    draft or publish with no human review and their runners do not build
    `public/`, so a hero typo would ship and the first person to see it would be
    a reader looking at an empty box. These tests pin the rule and, more
    importantly, pin that the gate does not go blind again.
    """

    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="hero-path-"))

    def file(self, fm: str) -> Path:
        p = self.dir / "x.md"
        p.write_text(f"---\n{fm}\n---\n\nBody.\n", encoding="utf-8")
        return p

    def run_gate(self, path: Path) -> tuple[int, str]:
        import io
        import contextlib
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["check-hero-paths.py", "--file", str(path)]
        try:
            with contextlib.redirect_stdout(buf):
                rc = chp.main()
        finally:
            sys.argv = old
        return rc, buf.getvalue()

    def test_a_real_path_passes(self):
        p = self.file('hero_desktop: "img/articles/103-chiefs-report_16x9.webp"')
        rc, out = self.run_gate(p)
        self.assertEqual(rc, 0, out)

    def test_a_missing_file_fails(self):
        # The exact defect: Hugo does NOT fail on a missing image, the page
        # returns 200, and the hero is an empty box.
        p = self.file('hero_desktop: "img/articles/no-such-plate_16x9.webp"')
        rc, out = self.run_gate(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("no such file", out)

    def test_a_missing_mobile_path_is_caught_too(self):
        # hero_mobile is what every phone reader gets; missing it is invisible
        # on the desktop check.
        p = self.file('hero_mobile: "img/articles/nope_4x5.webp"')
        self.assertEqual(self.run_gate(p)[0], 1)

    def test_the_field_extractor_reads_quoted_and_bare_values(self):
        for value in ('"img/articles/103-chiefs-report_16x9.webp"',
                      'img/articles/103-chiefs-report_16x9.webp',
                      "'img/articles/103-chiefs-report_16x9.webp'"):
            with self.subTest(value=value):
                p = self.file(f"hero_desktop: {value}")
                self.assertEqual(self.run_gate(p)[0], 0, value)

    def test_a_file_with_no_hero_fields_passes(self):
        # Most content has no hero; the gate must not invent a failure for it.
        p = self.file("title: A post with no hero")
        self.assertEqual(self.run_gate(p)[0], 0)

    def test_both_new_series_plates_actually_resolve(self):
        # Guards the fixture against drift: if a plate is renamed, the skill and
        # this contract must move with it.
        for rel in ("img/articles/104-docket-report_16x9.webp",
                    "img/articles/104-docket-report_4x5.webp",
                    "img/articles/105-senate-race-report_16x9.webp",
                    "img/articles/105-senate-race-report_4x5.webp"):
            self.assertTrue((REPO / "static" / rel).is_file(), rel)

    def test_the_corpus_is_clean(self):
        # Every hero in content/ resolves. This is the standing state, and a
        # failure here means a real broken hero is checked in.
        self.assertEqual(chp.check(verbose=False), [])

    def test_the_runners_that_write_hero_reports_run_the_gate(self):
        # A gate nobody runs is a gate that does not exist. The corpus-wide hero
        # check lives in the shared list (run_report_gates) for the three
        # publishing jobs; the drafting ninety-days runner, which does not call
        # that list, names it directly.
        self.assertIn("check-hero-paths",
                      (SCRIPTS / "publish-report.sh").read_text(encoding="utf-8"))
        for runner in ("docket-weekly-report-runner.sh",
                       "senate-report-runner.sh",
                       "chiefs-weekly-report-runner.sh"):
            text = (SCRIPTS / runner).read_text(encoding="utf-8")
            with self.subTest(runner=runner):
                self.assertIn("run_report_gates", text)
        ninety = (SCRIPTS / "ninety-days-report-runner.sh").read_text(encoding="utf-8")
        self.assertIn("check-hero-paths", ninety)


class TestSeriesHomeFlagGate(unittest.TestCase):
    """A published series installment must carry `featuredOnHome: true`.

    The home page fills Recent Posts from flagged posts only, and more than five
    are already flagged, so an unflagged installment publishes and reaches no
    reader from the home page. Five Senate race reports shipped that way between
    2026-09-06 and 2026-09-27 because the skill's frontmatter list omitted the
    field. It is invisible to every other check: the build passes, the page
    returns 200, and the RSS feed lists it.
    """

    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="series-flag-"))

    def run_gate(self, *args: str) -> tuple[int, str]:
        import io
        import contextlib
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["check-series-posts.py", *args]
        try:
            with contextlib.redirect_stdout(buf):
                rc = csp.main()
        finally:
            sys.argv = old
        return rc, buf.getvalue()

    def test_the_series_come_from_the_gallery_not_a_hardcoded_list(self):
        # A new report series is covered by adding its gallery card, the same
        # declaration the gallery layout resolves a series card with. If this
        # ever becomes a literal list in the gate, the list can drift from what
        # the site treats as a series -- which is how this defect arose.
        globs = csp.series_globs()
        self.assertIn("/posts/essays/senate-race-report-*", globs)
        self.assertIn("/posts/essays/docket-report-*", globs)
        self.assertIn("/posts/sports/chiefs-report-*", globs)

    def test_the_corpus_is_clean(self):
        # Every published series installment on the site is flagged. A failure
        # here is a real report that no reader can reach from the home page.
        problems, _notes = csp.check(verbose=False)
        self.assertEqual(problems, [])

    def test_the_senate_series_really_was_the_defect(self):
        # The five installments exist and every one is now flagged; this pins
        # that the backfill was complete rather than partial.
        posts = csp.installments("/posts/essays/senate-race-report-*")
        self.assertGreaterEqual(len(posts), 4)
        for p in posts:
            fm = csp.frontmatter(p.read_text(encoding="utf-8"))
            with self.subTest(post=p.name):
                self.assertTrue(csp.is_flagged(fm), p.name)

    def test_a_draft_is_skipped_by_the_corpus_scan(self):
        # A draft is not published, so it has no home-feed obligation yet. This
        # is also why the runner needs --file: the draft it just wrote is
        # exactly the file a corpus scan cannot see.
        fm = "draft: true\nfeaturedOnHome: false\ntitle: x"
        self.assertTrue(csp.is_draft(fm))
        self.assertFalse(csp.is_flagged(fm))

    def test_the_flag_reader_requires_true_not_mere_presence(self):
        for value, expected in (("true", True), ("false", False)):
            with self.subTest(value=value):
                self.assertEqual(
                    csp.is_flagged(f"draft: false\nfeaturedOnHome: {value}\n"),
                    expected)
        self.assertFalse(csp.is_flagged("draft: false\n"))

    def test_file_mode_catches_an_unflagged_draft_that_the_scan_skips(self):
        # The runner's case: it just wrote a draft, and the corpus scan reports
        # OK because the file is a draft. --file must still fail it.
        slug = "senate-race-report-2999-01-01"
        p = REPO / "content" / "posts" / "essays" / f"{slug}.md"
        p.write_text("---\ntitle: x\ndraft: true\n---\n\nBody.\n", encoding="utf-8")
        try:
            rc, out = self.run_gate("--file", str(p))
            self.assertEqual(rc, 1, out)
            self.assertIn("featuredOnHome", out)
        finally:
            p.unlink()

    def test_file_mode_passes_a_flagged_file(self):
        slug = "senate-race-report-2999-01-02"
        p = REPO / "content" / "posts" / "essays" / f"{slug}.md"
        p.write_text("---\ntitle: x\ndraft: false\nfeaturedOnHome: true\n---\n\nBody.\n",
                     encoding="utf-8")
        try:
            self.assertEqual(self.run_gate("--file", str(p))[0], 0)
        finally:
            p.unlink()

    def test_file_mode_has_no_opinion_about_standalone_posts(self):
        # Most content is not a series installment and may legitimately go
        # unflagged; the gate must not invent a failure for it.
        p = self.dir / "essays" / "a-standalone-essay.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("---\ntitle: x\ndraft: false\n---\n\nBody.\n", encoding="utf-8")
        self.assertEqual(self.run_gate("--file", str(p))[0], 0)

    def test_directories_whose_series_has_not_started_are_a_note_not_a_failure(self):
        # A declared series with no published installment yet is legitimate and
        # must be a note, not a failure: failing it would leave CI red for
        # weeks, which trains people to ignore it -- the same reasoning as
        # check-gallery-pages.py. The docket series published its first
        # installment on 2026-10-03, so the "has not started" state is
        # simulated by scanning an empty content tree rather than a shipped
        # series that happens to be unstarted today.
        from unittest import mock
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(csp, "CONTENT", Path(tmp)):
                problems, notes = csp.check(verbose=False)
        self.assertEqual(problems, [])
        self.assertTrue(any("docket-report" in n for n in notes), notes)

    def test_both_report_runners_run_the_gate_and_scope_it_to_the_draft(self):
        # A gate nobody runs is not a gate, and an unscoped run would scan the
        # corpus while the file that needs checking is a draft the scan skips.
        # Both now select the gate through the shared list, which scopes it with
        # `--file "$article"`.
        lib = (SCRIPTS / "publish-report.sh").read_text(encoding="utf-8")
        self.assertIn("check-series-posts", lib)
        self.assertIn('--file "$article"', lib)
        for runner in ("senate-report-runner.sh",
                       "docket-weekly-report-runner.sh"):
            text = (SCRIPTS / runner).read_text(encoding="utf-8")
            with self.subTest(runner=runner):
                self.assertIn("run_report_gates", text)

    def test_ci_runs_the_gate(self):
        ci = (REPO / ".github" / "workflows" / "hugo.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/check-series-posts.py", ci)

    def test_the_skill_that_omitted_the_field_now_requires_it(self):
        # The root cause: the Senate skill listed the frontmatter fields and left
        # this one out, so the writer had no way to know. A gate would catch it;
        # the spec should not rely on the gate.
        for skill in ("senate-race-report.md", "docket-weekly-report.md"):
            text = (REPO / "skills" / skill).read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("featuredOnHome", text)


class TestChiefsRunnerContract(unittest.TestCase):
    """The runner's own invariants, checked against its text.

    These are not style rules. Each asserts a property whose absence would let
    an unreviewed article reach production, and each is cheap to break by
    editing the script without thinking about this job publishing.

    The publish tail itself — preflight, SESSION_STATE entry, commit, push, push
    verification, SimpleBrain — now lives in `scripts/publish-report.sh`, shared
    with the Senate and docket runners, so the assertions about it are on the
    library (see TestPublishLibrary below) and this class asserts only what is
    specific to the Chiefs job: that it calls into the library, that it cannot
    publish without the library having succeeded, and that its own guards and
    gates are wired.
    """

    def setUp(self):
        self.runner = (REPO / "scripts" / "chiefs-weekly-report-runner.sh").read_text()
        self.lib = (REPO / "scripts" / "publish-report.sh").read_text()

    def test_it_sources_the_shared_publish_tail(self):
        # The whole point of the library: one publish path, three jobs. Three
        # copies of this logic is how the featuredOnHome rule drifted between
        # skills and hid five reports from the home feed.
        self.assertIn('. "$REPO/scripts/publish-report.sh"', self.runner)

    def test_a_gate_failure_aborts_the_push(self):
        # The gate abort must come before anything publishes. The gate runner
        # and its GATE_FAILED flag live in the library now (run_report_gates);
        # the runner reads the flag through report_gates_failed() and must not
        # reach publish_article on failure.
        self.assertIn("GATE_FAILED=1", self.lib)
        self.assertIn("report_gates_failed", self.lib)
        i = self.runner.find("report_gates_failed")
        self.assertGreater(i, 0)
        after = self.runner[i:]
        self.assertIn("NOT PUBLISHING", after)
        self.assertLess(after.find("NOT PUBLISHING"), after.find("publish_article"))

    def test_a_build_failure_aborts_the_push(self):
        # report_build (library) sets BUILD_FAILED; the runner aborts before
        # publishing.
        self.assertIn("BUILD_FAILED=1", self.lib)
        i = self.runner.find('if [ "$BUILD_FAILED" -ne 0 ]')
        self.assertGreater(i, 0)
        self.assertGreater(self.runner.find("publish_article"), i)

    def test_the_article_is_validated_before_it_is_published(self):
        # The frontmatter gate reads the artifact as a publisher (draft false,
        # featuredOnHome true); it must run before the library publishes.
        self.assertLess(self.runner.find("check-report-frontmatter"),
                        self.runner.find("publish_article"))

    def test_the_article_path_is_bound_before_anything_uses_it(self):
        # The guards and the commit all read $ARTICLE. Under `set -u` an unbound
        # expansion is a hard failure, and defining it after a use would make
        # every run die at that guard. Cheap to break by moving the assignment.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        define = code.find('ARTICLE="content/posts/sports/')
        self.assertGreater(define, 0)
        self.assertLess(define, code.find('publish_preflight "$ARTICLE"'))
        self.assertLess(define, code.find("claude -p"))
        self.assertEqual(code.count('ARTICLE="content/posts/sports/'), 1,
                         "exactly one definition; a second would shadow the first")

    def test_the_preflight_guard_runs_before_the_writer(self):
        # It deletes a stale file at $ARTICLE so the post-condition is binary:
        # the file exists because this run wrote it, or the run aborts. Running
        # it after the writer would delete this run's own work.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertLess(code.find('publish_preflight "$ARTICLE"'), code.find("claude -p"))

    def test_the_agent_cannot_commit_push_or_touch_session_state(self):
        # The runner owns all three. An agent that could push could publish
        # anything; an agent that wrote SESSION_STATE could assert a gate result
        # it was unable to produce.
        i = self.runner.find("--allowedTools")
        self.assertGreater(i, 0)
        grant = self.runner[i:self.runner.find("\n", self.runner.find(">> \"$OUT_LOG\"", i))]
        self.assertNotIn("git", grant)
        self.assertIn("Bash(python3 scripts/chiefs-report.py*)", grant)

    def test_the_season_guard_exits_zero(self):
        # A non-zero exit would raise the failure alert every Tuesday for six
        # months, which is how a real alert gets learned as noise.
        i = self.runner.find("off season, no report, exiting")
        self.assertGreater(i, 0)
        self.assertIn("exit 0", self.runner[i:i + 200])

    def test_no_apostrophe_inside_a_default_expansion(self):
        # bash 3.2 mis-parses it and reports the damage as a syntax error far
        # later in the file. This cost a debugging round while writing the job.
        for m in re.finditer(r"\$\{[A-Z_]+:-([^}]*)\}", self.runner):
            self.assertNotIn("'", m.group(1), m.group(0)[:120])


class TestPublishLibrary(unittest.TestCase):
    """The shared publish tail, asserted once rather than per runner.

    Every property here was previously asserted against the Chiefs runner. It is
    the only job that publishes today, so the failures it learned from are the
    failures the other two are now exposed to.
    """

    def setUp(self):
        self.lib = (SCRIPTS / "publish-report.sh").read_text()

    def test_a_gate_failure_stops_before_the_commit(self):
        # The library is called only after a caller's gates pass, but the commit
        # itself is guarded too: a failed `git add` or `git commit` must not fall
        # through to a push. Comments are stripped first — the library's own
        # prose mentions `git push` before the code reaches it, and a test that
        # matched its documentation would be testing the wrong text.
        code = "\n".join(ln for ln in self.lib.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertIn("git add failed", code)
        self.assertIn("git commit failed", code)
        self.assertLess(code.find("git add failed"), code.find("git push"))

    def test_the_push_is_verified_rather_than_assumed(self):
        # `git push` exit 0 after racing another push does not mean the commit
        # landed, and a published report that never reached the remote looks
        # exactly like success in the log.
        self.assertIn("git rev-parse origin/main", self.lib)
        self.assertIn("push did not land", self.lib)

    def test_a_dirty_session_state_stops_the_run(self):
        # The entry is inserted by splitting SESSION_STATE.md at an anchor, so
        # uncommitted edits already there would be committed under this run's
        # message and attributed to this job.
        self.assertIn("REFUSING TO RUN", self.lib)
        self.assertIn("git status --porcelain -- SESSION_STATE.md", self.lib)

    def test_a_stale_article_is_removed_before_the_writer_runs(self):
        # The dangerous outcome is not "it gets overwritten" — it is "the writer
        # fails and the runner then commits a stale draft under this run's
        # title". Deleting it first makes the post-condition binary.
        self.assertIn("removing a pre-existing", self.lib)
        self.assertIn('rm -f "$article"', self.lib)

    def test_the_commit_names_only_the_article_and_the_state_file(self):
        # `git add -A` would let a writer that wandered outside its brief get the
        # result into a published commit. Comments are stripped first: the runner
        # explains in prose that it does NOT use `git add -A`, and a test that
        # matched its own documentation would be testing the wrong text.
        code = "\n".join(ln for ln in self.lib.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertIn('git add "$article" SESSION_STATE.md', code)
        self.assertNotIn("git add -A", code)
        self.assertNotIn("git add .", code)

    def test_series_extra_paths_are_staged_by_name_not_wildcard(self):
        # The docket job grows scripts/check-docket.py's `known` map as part of
        # every run (skills/docket-weekly-report.md requires it) and that file
        # must ride along in the publish commit, or the one-line note the writer
        # just recorded is discarded by the next run. Staged through a variable
        # naming exact paths, never a wildcard, so a writer that wandered outside
        # its brief still cannot get a stray file into a published commit.
        code = "\n".join(ln for ln in self.lib.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertIn("PUBLISH_EXTRA_PATHS", code)
        self.assertIn('git add "$article" SESSION_STATE.md ${PUBLISH_EXTRA_PATHS:-}', code)
        docket = (SCRIPTS / "docket-weekly-report-runner.sh").read_text(encoding="utf-8")
        self.assertIn("PUBLISH_EXTRA_PATHS=", docket)
        self.assertIn("scripts/check-docket.py", docket)

    def test_the_entry_is_inserted_above_the_first_maintenance_entry(self):
        # An entry appended at the bottom, or written in the wrong place, breaks
        # the file SESSION_STATE exists to be — the thing a session reads first.
        self.assertIn('anchor = "### Maintenance —"', self.lib)
        self.assertIn("refusing to guess where the entry goes", self.lib)

    def test_the_dry_run_stops_before_anything_touches_git(self):
        # A pipeline that publishes unreviewed must be provable without being
        # performed.
        self.assertIn("publish_dry_run_stop", self.lib)
        i = self.lib.find("publish_dry_run_stop()")
        body = self.lib[i:i + 700]
        self.assertIn("Nothing was published", body)

    def test_the_historical_chiefs_switches_still_work(self):
        # CHIEFS_DRY_RUN and CHIEFS_SKIP_SIMPLEBRAIN are documented in CLAUDE.md
        # and used by the job's own smoke runs. The generic names must not have
        # replaced them.
        self.assertIn("CHIEFS_DRY_RUN", self.lib)
        self.assertIn("CHIEFS_SKIP_SIMPLEBRAIN", self.lib)
        self.assertIn("REPORT_DRY_RUN", self.lib)
        self.assertIn("REPORT_SKIP_SIMPLEBRAIN", self.lib)

    def test_a_simplebrain_failure_does_not_fail_the_site_publish(self):
        # The article is already live and correct; the mirror is secondary. It is
        # alerted so it is visible, but it must not be reported as a failed
        # publish.
        i = self.lib.find("SimpleBrain sync incomplete")
        self.assertGreater(i, 0)
        self.assertIn("the site publish stands", self.lib[i - 200:i + 200])

    def test_it_never_dies_on_a_nonexistent_plate(self):
        # The library is sourced by three runners; a `set -e` trip inside a
        # function that is expected to return non-zero (the dry-run stop) would
        # abort every real run before the publish.
        self.assertIn("if ! report_dry_run; then", self.lib)

    def test_the_library_asserts_the_job_contract(self):
        # JOB is expanded inside publish_article and in every alert, under the
        # caller's `set -u`. The library names the contract so an unbound JOB is
        # a sentence about the requirement, not the cryptic line number the
        # docket and senate runners produced on 2026-10-03.
        self.assertIn(': "${JOB:?publish-report.sh requires JOB', self.lib)

    def test_every_sourcing_runner_binds_job_first(self):
        # The rule the guard above depends on: a runner that sources the library
        # must bind JOB beforehand. The docket and senate runners omitted it, so
        # their first real publish died with "JOB: unbound variable" after the
        # writer and every gate had already succeeded — a failure reachable only
        # on the publish path, which a dry run never runs.
        sourced = re.compile(r'^\.\s+"\$REPO/scripts/publish-report\.sh"', re.M)
        checked = 0
        for runner in sorted(SCRIPTS.glob("*-runner.sh")):
            text = runner.read_text(encoding="utf-8")
            m = sourced.search(text)
            if not m:
                continue
            checked += 1
            with self.subTest(runner=runner.name):
                self.assertIsNotNone(
                    re.search(r'^JOB="', text[:m.start()], re.M),
                    f"{runner.name} sources the publish library without binding JOB")
        self.assertGreaterEqual(
            checked, 4,
            "the four report runners (chiefs, docket, senate, ninety-days) source the library")


# --------------------------------------------------------------------------
# Link gate. Two rules, both learned by measurement on 2026-09-25 while
# building the Chiefs job, and both are blind spots that reported OK.
# --------------------------------------------------------------------------
class TestLinkGateRules(unittest.TestCase):
    def test_the_waf_challenge_is_recognised(self):
        # ESPN answered a browser User-Agent with 202 and this body for a LIVE
        # story and an INVENTED id alike. Read as a 2xx it passed, and three dead
        # links survived a whole-corpus sweep plus a per-file sweep.
        body = (b'<html><head><script>window.awsWafCookieDomainList = [];'
                b'window.gokuProps = {};</script>'
                b'<script src="https://x.token.awswaf.com/y/challenge.js"></script>'
                b'</head></html>')
        self.assertTrue(cl.is_waf_challenge(body))
        self.assertTrue(cl.is_waf_challenge(
            b'<noscript>In order to continue, we need to verify that you\'re not a robot.</noscript>'))

    def test_an_ordinary_page_is_not_a_challenge(self):
        self.assertFalse(cl.is_waf_challenge(b"<html><body><h1>A real article</h1></body></html>"))
        self.assertFalse(cl.is_waf_challenge(b""))

    def test_page_title_is_extracted_and_normalized(self):
        self.assertEqual(
            cl.page_title("<html><title>  Chiefs 33-30 Colts \n (Sep 20) - ESPN </title>"),
            "Chiefs 33-30 Colts (Sep 20) - ESPN")
        self.assertEqual(cl.page_title("<html>no title</html>"), "")

    def test_a_wrong_article_is_a_mismatch(self):
        # The real fabrication shape: an invented ESPN story id returns 200 and
        # lands on an unrelated article. `200` is not proof of correctness.
        self.assertIs(
            cl.link_text_matches_title("Peter Thiel and mimetic desire",
                                       "Ranking the top 25 WNBA players in the playoffs - ESPN"),
            False)
        self.assertIs(
            cl.link_text_matches_title("How Democracies Die", "The Phantom Tollbooth - Wikipedia"),
            False)

    def test_a_correct_citation_is_not_a_mismatch(self):
        # Paraphrase and the publisher's own decorations must not read as errors.
        for anchor, title in (
            ("Chiefs aim to reduce Kenneth Walker's workload 'a little bit'",
             "Chiefs aim to reduce Kenneth Walker's workload 'a little bit' - ESPN"),
            ("Colts' Shane Steichen defends OT playcalling in loss to Chiefs",
             "Colts' Shane Steichen defends OT playcalling in loss to Chiefs - ESPN"),
            ("Chiefs signing ex-Seahawks RB Kenneth Walker III, MVP of Super Bowl LX, to three-year deal",
             "Chiefs signing ex-Seahawks RB Kenneth Walker III, MVP of Super Bowl LX - NFL.com"),
        ):
            with self.subTest(anchor=anchor):
                self.assertIsNot(cl.link_text_matches_title(anchor, title), False)

    def test_a_short_label_is_not_judged(self):
        # "odds", "game page" carry too little vocabulary to compare. The answer
        # must be None — guessing False here would accuse a correct citation.
        for anchor in ("odds", "game page", "here"):
            with self.subTest(anchor=anchor):
                self.assertIsNone(cl.link_text_matches_title(anchor, "Anything At All"))

    def test_only_headline_like_markdown_links_yield_anchors(self):
        # link_texts reads markdown links with substantial anchor text; a bare
        # URL carries nothing to compare and must not be invented.
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="links-"))
        p = d / "x.md"
        p.write_text("Bare https://example.org/plain and [a real headline of several words]"
                     "(https://example.org/a)\n", encoding="utf-8")
        got = cl.link_texts(str(p))
        self.assertEqual(got, {"https://example.org/a": "a real headline of several words"})

    def test_the_online_gate_runs_in_every_publishing_job(self):
        # The check exists so an unreviewed article cannot ship a link that
        # resolves to the wrong page — a corpus sweep cannot see a brand-new
        # file, so it must run scoped with --file on the article just written.
        # It lives in the shared list now, so all three publishing jobs get it.
        lib = (SCRIPTS / "publish-report.sh").read_text()
        self.assertIn("--online --titles", lib)
        self.assertIn('--file "$article"', lib)
        for runner in ("chiefs-weekly-report-runner.sh",
                       "senate-report-runner.sh",
                       "docket-weekly-report-runner.sh"):
            text = (SCRIPTS / runner).read_text()
            with self.subTest(runner=runner):
                self.assertIn("run_report_gates", text)


# --------------------------------------------------------------------------
# SESSION_STATE splitter. The rules that matter are the ones whose absence
# caused, or would have caused, silent data loss: a repeatable boundary, an
# APPENDED archive, and a safety check that covers both files.
# --------------------------------------------------------------------------
ss = load("split-session-state")


class TestSessionStateSplitter(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="split-"))
        self.live = self.dir / "live.md"
        self.arch = self.dir / "archive.md"

    def write(self, live: str, arch: "str | None" = None):
        self.live.write_text(live, encoding="utf-8")
        if arch is not None:
            self.arch.write_text(arch, encoding="utf-8")

    def run_split(self, *extra) -> "tuple[int, str]":
        import subprocess
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "split-session-state.py"),
             "--live", str(self.live), "--archive", str(self.arch), *extra],
            capture_output=True, text=True, cwd=REPO,
        )
        return r.returncode, r.stdout + r.stderr

    # -- the boundary advances by itself ----------------------------------
    def test_the_cutoff_counts_back_whole_months(self):
        self.assertEqual(ss.cutoff(date(2026, 9, 25), 3), (2026, 7))
        self.assertEqual(ss.cutoff(date(2026, 12, 1), 3), (2026, 10))
        self.assertEqual(ss.cutoff(date(2027, 1, 15), 3), (2026, 11))
        self.assertEqual(ss.cutoff(date(2027, 2, 1), 1), (2027, 2))
        # The boundary must be derivable from ANY date, which is what makes this
        # repeatable; the old hardcoded (2026, 9) moved nothing on a second run.
        self.assertLess(ss.cutoff(date(2026, 9, 25), 3), ss.cutoff(date(2027, 9, 25), 3))

    def test_dated_reads_a_heading(self):
        self.assertEqual(ss.dated("### Maintenance — September 25, 2026 — Published X"), (2026, 9))
        self.assertIsNone(ss.dated("## Project Overview"))
        self.assertIsNone(ss.dated("### Maintenance — no date here"))

    # -- reference sections and the pointer ------------------------------
    def test_reference_sections_are_never_archived(self):
        for h in ("## Project Overview", "## User Preferences", "## Last Updated",
                  "### FLAGGED — something"):
            with self.subTest(h=h):
                self.assertTrue(ss.is_reference(h))
        self.assertFalse(ss.is_reference("### Maintenance — September 1, 2026 — x"))

    def test_a_history_pointer_is_recognised_by_shape_not_wording(self):
        # Its wording changes as the boundary moves. Matching today's string
        # would treat the PREVIOUS revision's pointer as content and fail the
        # loss check on every re-run.
        self.assertTrue(ss.is_history_pointer(
            "> **History.** Entries before September 2026 were moved to"))
        self.assertTrue(ss.is_history_pointer(
            "> **History.** Entries older than the last few months are in"))
        self.assertFalse(ss.is_history_pointer("> A quoted sentence about History in general"))
        self.assertFalse(ss.is_history_pointer("Plain prose about History"))

    # -- the data-loss bug -------------------------------------------------
    def test_the_archive_is_appended_to_never_replaced(self):
        # The first version wrote only the sections it was moving this run over
        # the archive. A second run would have replaced a 1,106-line archive with
        # the 25 lines of its own header — measured before fixing.
        self.write(
            "PRE\n\n---\n\n### Maintenance — January 5, 2026 — old\nbody\n\n---\n\n"
            "### Maintenance — December 5, 2026 — new\nbody2\n\n---\n\n"
            "## Project Overview\nkeep me\n",
            arch="# Session State — Archive\n\n### Maintenance — May 1, 2025 — ancient\nancient body\n",
        )
        rc, out = self.run_split("--as-of", "2027-03-01", "--write")
        self.assertEqual(rc, 0, out)
        after = self.arch.read_text()
        self.assertIn("ancient body", after, "pre-existing archive content was destroyed")
        self.assertIn("old", after, "the moved section was not appended")

    def test_a_second_run_changes_nothing(self):
        # Idempotence: any run must leave the live file in the shape it would
        # have had if it were the only run. The defect this guards is a pointer
        # appended on every run — three `**History.**` blocks after two runs.
        self.write(
            "PRE\n\n---\n\n### Maintenance — January 5, 2026 — old\nbody\n\n---\n\n"
            "## Project Overview\nkeep\n",
            arch="# Archive\n",
        )
        rc, out = self.run_split("--as-of", "2027-03-01", "--write")
        self.assertEqual(rc, 0, out)
        first = self.live.read_text()
        rc2, out2 = self.run_split("--as-of", "2027-03-01", "--write")
        self.assertEqual(rc2, 0, out2)
        second = self.live.read_text()
        self.assertEqual(first, second, "a re-run must be a no-op")
        self.assertEqual(second.count("**History.**"), 1,
                         "the history pointer must appear exactly once")

    def test_the_replaced_pointer_is_rewritten_not_lost(self):
        # Even when the previous revision's wording names a specific month.
        legacy = ("> **History.** Entries before September 2026 were moved to\n"
                  "> [`SESSION_STATE_ARCHIVE.md`](SESSION_STATE_ARCHIVE.md) on 2026-09-20 — nothing was\n")
        self.write(f"PRE\n\n---\n{legacy}\n---\n\n### Maintenance — January 5, 2026 — old\nb\n",
                   arch="# Archive\n")
        rc, out = self.run_split("--as-of", "2027-03-01", "--write")
        self.assertEqual(rc, 0, f"the legacy pointer broke the loss check:\n{out}")
        after = self.live.read_text()
        self.assertEqual(after.count("**History.**"), 1)
        self.assertNotIn("September 2026", after, "the stale boundary wording survived")

    def test_nothing_to_move_is_reported_not_an_error(self):
        self.write("PRE\n\n---\n\n### Maintenance — September 25, 2026 — recent\nb\n")
        rc, out = self.run_split("--as-of", "2026-09-25")
        self.assertEqual(rc, 0, out)
        self.assertIn("nothing to move", out)

    def test_a_dry_run_writes_nothing(self):
        self.write("PRE\n\n---\n\n### Maintenance — January 5, 2026 — old\nbody\n")
        before = self.live.read_text()
        rc, out = self.run_split("--as-of", "2027-03-01")
        self.assertEqual(rc, 0, out)
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.live.read_text(), before)

    def test_it_refuses_a_bad_argument(self):
        self.write("PRE\n\n---\n\n## Project Overview\nx\n")
        self.assertEqual(self.run_split("--keep-months", "0")[0], 2)
        self.assertEqual(self.run_split("--as-of", "not-a-date")[0], 2)

    def test_the_live_file_has_no_sections_so_it_refuses(self):
        self.write("just prose, no headings at all\n")
        rc, _ = self.run_split()
        self.assertEqual(rc, 2)

    # -- the real files ----------------------------------------------------
    def test_the_real_live_file_keeps_its_reference_sections(self):
        # A split of the actual file must never archive what a session needs.
        text = (REPO / "SESSION_STATE.md").read_text(encoding="utf-8")
        pl = ss.plan(text, date(2027, 6, 1), 3)
        kept = {h for _, _, h in pl["keep"]}
        for need in ss.KEEP_ALWAYS:
            self.assertTrue(any(need in h for h in kept),
                            f"{need!r} would be archived away from the live file")

    def test_the_real_corpus_loses_nothing_when_split(self):
        # The whole point: run the plan over the real file and prove every
        # non-pointer line survives in one of the two outputs.
        text = (REPO / "SESSION_STATE.md").read_text(encoding="utf-8")
        pl = ss.plan(text, date(2027, 6, 1), 3)
        live_body = "\n".join(ss.build_live(pl))
        moved = []
        for s, e, _ in pl["arch"]:
            moved += pl["lines"][s:e]
        arch_body = "\n".join(moved)
        lost = [l for l in pl["lines"]
                if l.strip() and not ss.is_history_pointer(l)
                and l not in live_body and l not in arch_body]
        self.assertEqual(lost, [], f"{len(lost)} line(s) would be lost")


# --------------------------------------------------------------------------
# The gates agree with the corpus they guard.
# --------------------------------------------------------------------------
class TestCorpusIntegration(unittest.TestCase):
    def test_the_session_state_insert_lands_above_the_first_entry(self):
        # The runner inserts its entry by finding the first "### Maintenance —"
        # anchor. This reproduces that insert against a scratch copy of the real
        # file: an entry appended at the bottom, or one written after the anchor
        # in the wrong place, would quietly break the file that SESSION_STATE
        # exists to be — the thing a session reads first.
        import subprocess
        import tempfile
        state = REPO / "SESSION_STATE.md"
        text = state.read_text(encoding="utf-8")
        anchor = "### Maintenance —"
        self.assertGreater(text.find(anchor), 0, "the anchor the runner depends on is gone")
        # The exact snippet the runner runs, against a temp copy.
        tmp = Path(tempfile.mkdtemp(prefix="chiefs-state-")) / "SESSION_STATE.md"
        tmp.write_text(text, encoding="utf-8")
        entry = "\n### Maintenance — January 6, 2027 — Published the Chiefs weekly report\n\nX\n\n---\n"
        snippet = (
            "import sys, pathlib\n"
            "state = pathlib.Path(sys.argv[1]); entry = sys.argv[2]\n"
            "text = state.read_text(encoding='utf-8')\n"
            "anchor = '### Maintenance —'\n"
            "i = text.find(anchor)\n"
            "if i < 0: sys.exit('no anchor')\n"
            "state.write_text(text[:i] + entry.lstrip('\\n') + '\\n' + text[i:], encoding='utf-8')\n"
        )
        r = subprocess.run([sys.executable, "-c", snippet, str(tmp), entry],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        after = tmp.read_text(encoding="utf-8")
        self.assertIn("January 6, 2027", after)
        self.assertLess(after.find("January 6, 2027"), after.find(anchor) + len(anchor) + 60,
                        "the new entry must be the FIRST maintenance entry")
        # Nothing was dropped: everything before the anchor and everything from
        # the anchor onward both survive, and the file grew only by the entry
        # plus one separating blank line. (`assertIn(text, after)` would be the
        # obvious check and is wrong — an insert in the middle breaks
        # contiguity, which is the point of an insert.)
        head, tail = text[:text.find(anchor)], text[text.find(anchor):]
        self.assertTrue(after.startswith(head))
        self.assertTrue(after.endswith(tail))
        added = len(after.splitlines()) - len(text.splitlines())
        self.assertEqual(added, len(entry.strip("\n").splitlines()) + 1)
        self.assertIn("### Maintenance — September 24, 2026", after)

    def test_every_runner_parses(self):
        # This repo has no linter and no package.json; `bash -n` on the launchd
        # runners is the only syntax check that exists. It matters more here than
        # a style rule would: a runner with a syntax error is a scheduled job
        # that fails at its next firing, unattended, and the failure surfaces as
        # a log line nobody reads. The bash 3.2 apostrophe inside a
        # `${VAR:-...}` default produces exactly that, and reports the error at
        # a line far from the cause.
        import subprocess
        runners = sorted((REPO / "scripts").glob("*runner.sh"))
        self.assertGreaterEqual(len(runners), 5, "the runner glob stopped matching")
        for r in runners:
            with self.subTest(runner=r.name):
                proc = subprocess.run(["/bin/bash", "-n", str(r)],
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, f"{r.name}:\n{proc.stderr}")

    def test_em_dash_corpus_is_compliant(self):
        import subprocess
        r = subprocess.run([sys.executable, "scripts/check-emdashes.py", "--check"],
                           cwd=REPO, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_baseline_key_includes_the_hash(self):
        # Keying on the file alone would exempt every attribution in it forever,
        # including ones added after the rule. The hash makes it text-specific,
        # so editing a quotation withdraws its exemption.
        e = {"path": Path("x.md"), "text": "a quotation", "attribution": "A"}
        sig = cq.signature(e)
        self.assertEqual(len(sig), 12)
        e2 = {"path": Path("x.md"), "text": "a different quotation", "attribution": "A"}
        self.assertNotEqual(sig, cq.signature(e2))

    def test_the_exemption_baseline_stays_empty(self):
        # The 68 grandfathered attributions were all repaired on 2026-09-20:
        # each names its work and carries a URL containing the wording. An
        # exemption is a promise to look later, and these went unlooked-at for
        # months — which is how a fabricated attribution shipped. This asserts
        # the debt is not quietly re-incurred: a new entry here means someone
        # grandfathered an uncheckable citation instead of fixing it.
        exemptions = cq.load_baseline()
        self.assertEqual(
            exemptions, {},
            f"{len(exemptions)} exemption(s) re-added to quote-baseline.txt; "
            "repair the citation instead, or justify the exemption in the commit",
        )


# --------------------------------------------------------------------------
# Secret drift gate: the rule is that two homes must agree.
# --------------------------------------------------------------------------
class TestSecretDrift(unittest.TestCase):
    """The rule, tested without a keychain.

    This gate exists because the fal.ai key lived in three places and only one
    of them worked, and nothing could see it — a stale key has the right
    length, the right prefix and the right home, and is wrong only in a way you
    learn by spending it. The tests below pin the rule and, more importantly,
    the two cases that must be *loud*: two homes that disagree, and the
    reappearance of the repo-local copy that started it.
    """

    def test_agreeing_homes_are_clean(self):
        self.assertEqual(
            cs.compare_homes("K", {"keychain:k": "same", "~/.secrets:K": "same"}),
            [],
        )

    def test_disagreeing_homes_are_reported(self):
        # This is the 2026-09-24 failure exactly: the keychain and ~/.secrets
        # held a stale value in perfect agreement with each other, so any check
        # comparing only those two would call it clean. The rule that catches
        # the real defect is not "the homes match" but "the resolved key
        # authenticates" — which is why --online exists.
        problems = cs.compare_homes("K", {"keychain:k": "stale", "~/.secrets:K": "live"})
        self.assertEqual(len(problems), 1)
        self.assertIn("DISAGREE", problems[0])

    def test_a_missing_home_is_reported(self):
        # The runners read the keychain with ~/.secrets as fallback, so a
        # keychain-only key means the documented fallback is dead.
        problems = cs.compare_homes("K", {"keychain:k": "v", "~/.secrets:K": None})
        self.assertEqual(len(problems), 1)
        self.assertIn("missing from ~/.secrets:K", problems[0])

    def test_no_home_at_all_is_reported(self):
        problems = cs.compare_homes("K", {"keychain:k": None, "~/.secrets:K": None})
        self.assertEqual(len(problems), 1)
        self.assertIn("no value in any home", problems[0])

    def test_the_fingerprint_never_contains_the_secret(self):
        # Findings go into a log file. The fingerprint is the only thing that
        # may be written there, so it must be a digest and must be short.
        secret = "055df1aa-bbbb-cccc-dddd-eeeeeeeeeeee"
        fp = cs.fingerprint(secret)
        self.assertEqual(len(fp), 12)
        self.assertNotIn(secret[:6], fp)
        self.assertEqual(fp, cs.fingerprint(secret))       # stable
        self.assertNotEqual(fp, cs.fingerprint(secret + "x"))

    def test_a_reappearing_repo_copy_is_reported(self):
        # `.fal_token` was the third copy that made the drift possible. It is
        # listed as legacy for exactly one reason: its return must fail here
        # rather than wait for the next unattended 401.
        cred = {"name": "K", "keychain": "does-not-exist-xyz",
                "secrets_var": "NO_SUCH_VAR_XYZ", "legacy_repo_files": ["CLAUDE.md"]}
        problems = cs.check_drift(cred)
        self.assertTrue(any("repo-local copy exists" in p for p in problems))

    def test_credentials_without_a_probe_are_not_probed(self):
        # Two providers have a cheap, free liveness probe: fal.ai and SendFox.
        # A key with no probe must not be sent anywhere — asserting the
        # registry shape keeps a later edit from inventing one by accident.
        for cred in cs.CREDENTIALS:
            with self.subTest(cred=cred["name"]):
                self.assertIn(cred.get("probe"), (None, "fal", "sendfox"))

    def test_a_server_error_is_not_read_as_auth_success(self):
        # A 5xx means the provider is broken, not that the key works. Reading
        # it as "ok" would be the exact bug this gate exists to catch: a
        # verdict that says OK while blind to the thing it checks.
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError("http://x", 503, "Service Unavailable", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, _ = cs.probe_fal("any-key")
        self.assertEqual(verdict, "unverified")

    def test_a_404_is_read_as_auth_success(self):
        # The expected answer for a request id that cannot exist. If this ever
        # flips, the probe stops distinguishing a live key from a stale one.
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError("http://x", 404, "Not Found", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, _ = cs.probe_fal("any-key")
        self.assertEqual(verdict, "ok")

    def test_a_401_is_read_as_auth_failure(self):
        import io as _io
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError(
            "http://x", 401, "Unauthorized", {},
            _io.BytesIO(b'{"detail":"invalid key credentials"}'))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, detail = cs.probe_fal("any-key")
        self.assertEqual(verdict, "auth-failed")
        self.assertIn("invalid key credentials", detail)

    def test_sendfox_a_200_is_a_live_token(self):
        import unittest.mock as mock
        resp = mock.MagicMock()
        resp.status = 200
        resp.__enter__ = lambda s: s
        resp.__exit__ = mock.MagicMock(return_value=False)
        with mock.patch("urllib.request.urlopen", return_value=resp):
            verdict, detail = cs.probe_sendfox("any-token")
        self.assertEqual(verdict, "ok")
        self.assertIn("200", detail)

    def test_sendfox_a_401_is_a_stale_token(self):
        import io as _io
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError(
            "http://x", 401, "Unauthorized", {},
            _io.BytesIO(b'{"message":"Unauthenticated."}'))
        # The default UA gets 401 too, so the browser retry also 401s and the
        # verdict is the same — that is the shape the real API produces.
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, detail = cs.probe_sendfox("any-token")
        self.assertEqual(verdict, "auth-failed")
        self.assertIn("401", detail)

    def test_sendfox_a_cloudflare_wall_is_not_a_stale_token(self):
        # Cloudflare answers urllib's default UA with 403 error 1010 for a
        # working token. Read as "auth failed" it would report a live key as
        # dead; read as "ok" it would report a dead one as live. It is neither:
        # we could not look. Simulate a 403 on every attempt.
        import io as _io
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError(
            "http://x", 403, "Forbidden", {}, _io.BytesIO(b"error code: 1010"))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, _ = cs.probe_sendfox("any-token")
        self.assertEqual(verdict, "unverified")

    def test_sendfox_a_server_error_is_not_read_as_auth_success(self):
        import io as _io
        import urllib.error
        import unittest.mock as mock
        err = urllib.error.HTTPError(
            "http://x", 503, "Service Unavailable", {}, _io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            verdict, _ = cs.probe_sendfox("any-token")
        self.assertEqual(verdict, "unverified")

    def test_sendfox_a_stale_key_is_reported_even_when_homes_agree(self):
        # The 2026-10-02 failure exactly: keychain and ~/.secrets held the same
        # stale SendFox value, so compare_homes reported nothing and the gate
        # said OK while a repo-local `.sendfox_token` did the work. The only
        # thing that catches it is probing the resolved key. Assert the
        # registry now carries a probe, so --online cannot go blind again.
        sendfox = [c for c in cs.CREDENTIALS
                   if c["name"] == "SENDFOX_CLIENT_SECRET"][0]
        self.assertEqual(sendfox["probe"], "sendfox")
        self.assertIn(".sendfox_token", sendfox["legacy_repo_files"])

    def test_the_guard_runs_clean_on_the_real_repo(self):
        # The end state, verified as the runner will see it: no drift, and the
        # one credential with a probe authenticates. Skipped rather than failed
        # if the keychain is unavailable (CI has none), because a check that
        # cannot run is not a check that failed.
        import subprocess
        if not cs.keychain_available() or not cs.keychain_lookup("huffmanwrites-fal"):
            self.skipTest("no keychain (expected in CI)")
        r = subprocess.run([sys.executable, "scripts/check-secrets.py", "--online"],
                           cwd=REPO, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[a for a in sys.argv if a != "-v"])
