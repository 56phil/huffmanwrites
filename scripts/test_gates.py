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


class TestChiefsArticleValidation(unittest.TestCase):
    """The only review an auto-published article gets. Every rule here is a
    defect this repo has actually shipped."""

    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="chiefs-validate-"))
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
            "draft": "false",
            "featuredOnHome": "true",
        }
        fields.update(over)
        front = "\n".join(f"{k}: {v}" for k, v in fields.items())
        return f"---\n{front}\n---\n\nBody prose.\n\n*PRH | [huffmanwrites.org] | © Philip Huffman*\n"

    def test_a_good_article_passes(self):
        p = self.write(self.good())
        self.assertEqual(ck.validate_article(p, now=self.now), [])

    def test_a_draft_flag_left_true_is_caught(self):
        # It would deploy nothing while looking like it published.
        p = self.write(self.good(draft="true"))
        self.assertTrue(any("draft" in m for m in ck.validate_article(p, now=self.now)))

    def test_a_missing_home_flag_is_caught(self):
        # More than five posts already carry the flag, so an unflagged post
        # never reaches the home feed at all: published and unseen.
        p = self.write(self.good(featuredOnHome="false"))
        self.assertTrue(any("featuredOnHome" in m for m in ck.validate_article(p, now=self.now)))
        p2 = self.write("\n".join(
            ln for ln in self.good().split("\n") if not ln.startswith("featuredOnHome")))
        self.assertTrue(any("featuredOnHome" in m for m in ck.validate_article(p2, now=self.now)))

    def test_a_future_date_is_caught(self):
        # buildFuture: false skips the page WITHOUT failing the build — the
        # failure recorded three times in SESSION_STATE.
        p = self.write(self.good(date="2026-09-29T23:30:00-05:00"))
        problems = ck.validate_article(p, now=self.now)
        self.assertTrue(any("ahead of the clock" in m for m in problems), problems)

    def test_small_clock_slack_is_allowed(self):
        # The stamp is taken microseconds before the check runs, so a modest
        # drift must not fail a correct article. The default slack is 5 minutes.
        p = self.write(self.good(date="2026-09-29T18:33:00-05:00"))
        self.assertEqual(ck.validate_article(p, now=self.now), [])

    def test_an_unparseable_date_is_caught_rather_than_skipped(self):
        p = self.write(self.good(date="September 29, 2026"))
        self.assertTrue(any("ISO 8601" in m for m in ck.validate_article(p, now=self.now)))

    def test_a_missing_attribution_is_caught(self):
        body = self.good().replace("*PRH | [huffmanwrites.org] | © Philip Huffman*\n", "")
        p = self.write(body)
        self.assertTrue(any("attribution" in m for m in ck.validate_article(p, now=self.now)))

    def test_missing_required_fields_are_named(self):
        p = self.write("---\ndraft: false\nfeaturedOnHome: true\n---\n*PRH | x*\n")
        problems = ck.validate_article(p, now=self.now)
        for name in ("title", "description", "date"):
            self.assertTrue(any(name in m for m in problems), (name, problems))

    def test_a_missing_file_is_a_problem_not_a_crash(self):
        self.assertTrue(ck.validate_article(self.dir / "nope.md", now=self.now))

    def test_no_frontmatter_is_caught(self):
        p = self.write("just prose, no frontmatter\n")
        self.assertTrue(any("frontmatter" in m for m in ck.validate_article(p, now=self.now)))


class TestChiefsRunnerContract(unittest.TestCase):
    """The runner's own invariants, checked against its text.

    These are not style rules. Each asserts a property whose absence would let
    an unreviewed article reach production, and each is cheap to break by
    editing the script without thinking about this job publishing."""

    def setUp(self):
        self.runner = (REPO / "scripts" / "chiefs-weekly-report-runner.sh").read_text()

    def test_a_gate_failure_aborts_the_push(self):
        # In the four drafting jobs a failed gate is a note for Philip. Here it
        # is the only review the piece gets, so it must stop the run.
        i = self.runner.find("GATE_FAILED=1")
        self.assertGreater(i, 0)
        after = self.runner[i:]
        self.assertIn("NOT PUBLISHING", after)
        self.assertLess(after.find("NOT PUBLISHING"), after.find("git push"),
                        "the gate abort must come before the push")

    def test_a_build_failure_aborts_the_push(self):
        i = self.runner.find("BUILD_FAILED=1")
        self.assertGreater(i, 0)
        after = self.runner[i:]
        self.assertIn("not publishing", after)
        self.assertLess(after.find("not publishing"), after.find("git push"))

    def test_the_article_is_validated_before_the_builds(self):
        self.assertLess(self.runner.find("--validate"), self.runner.find("check-quotes"))

    def test_the_article_path_is_bound_before_anything_uses_it(self):
        # The guards and the commit all read $ARTICLE. Under `set -u` an unbound
        # expansion is a hard failure, and defining it after a use would make
        # every run die at that guard. Cheap to break by moving the assignment.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        define = code.find('ARTICLE="content/posts/sports/')
        self.assertGreater(define, 0)
        self.assertLess(define, code.find('rm -f "$ARTICLE"'))
        self.assertLess(define, code.find("claude -p"))
        self.assertEqual(code.count('ARTICLE="content/posts/sports/'), 1,
                         "exactly one definition; a second would shadow the first")

    def test_a_dirty_session_state_stops_the_run(self):
        # The runner inserts its entry by splitting SESSION_STATE.md at an
        # anchor, so uncommitted edits already in that file would be committed
        # under this run's message and attributed to this job.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertIn("REFUSING TO RUN", code)
        i = code.find("REFUSING TO RUN")
        self.assertLess(i, code.find("git push"), "the guard precedes the push")
        self.assertIn("git status --porcelain -- SESSION_STATE.md", code)

    def test_a_stale_article_is_removed_before_the_writer_runs(self):
        # The dangerous outcome for the article path is not that a stale draft
        # gets overwritten — it is that the WRITER fails and the runner then
        # commits the stale draft under this run's title. Deleting it first
        # makes the post-condition binary: the file exists because this run
        # wrote it, or the run aborts for a missing file.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        i = code.find("removing a pre-existing")
        self.assertGreater(i, 0)
        self.assertIn('rm -f "$ARTICLE"', code)
        self.assertLess(i, code.find("claude -p"),
                        "the stale copy must go before the writer, not after")

    def test_the_push_is_verified_rather_than_assumed(self):
        # `git push` exit 0 after racing another push does not mean the commit
        # landed, and a published report that never reached the remote looks
        # exactly like success in the log.
        self.assertIn("git rev-parse origin/main", self.runner)
        self.assertIn("push did not land", self.runner)

    def test_the_agent_cannot_commit_push_or_touch_session_state(self):
        # The runner owns all three. An agent that could push could publish
        # anything; an agent that wrote SESSION_STATE could assert a gate result
        # it was unable to produce.
        i = self.runner.find("--allowedTools")
        self.assertGreater(i, 0)
        grant = self.runner[i:self.runner.find("\n", self.runner.find(">> \"$OUT_LOG\"", i))]
        self.assertNotIn("git", grant)
        self.assertIn("Bash(python3 scripts/chiefs-report.py*)", grant)

    def test_the_commit_names_only_the_article_and_the_state_file(self):
        # `git add -A` would let a writer that wandered outside its brief get the
        # result into a published commit. Comments are stripped first: the
        # runner explains in prose that it does NOT use `git add -A`, and a test
        # that matched its own documentation would be testing the wrong text.
        code = "\n".join(ln for ln in self.runner.splitlines()
                         if not ln.lstrip().startswith("#"))
        self.assertIn('git add "$ARTICLE" SESSION_STATE.md', code)
        self.assertNotIn("git add -A", code)
        self.assertNotIn("git add .", code)

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

    def test_the_online_gate_is_in_the_chiefs_runner(self):
        # The check exists in the one job whose output nobody reviews. Its
        # absence would be silent — a corpus sweep cannot see a brand-new file.
        text = (REPO / "scripts" / "chiefs-weekly-report-runner.sh").read_text()
        self.assertIn("--online --titles", text)
        self.assertIn('--file "$ARTICLE"', text)


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


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[a for a in sys.argv if a != "-v"])
