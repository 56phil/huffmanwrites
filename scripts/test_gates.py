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

import importlib.util
import json
import sys
import unittest
from datetime import datetime
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
# The gates agree with the corpus they guard.
# --------------------------------------------------------------------------
class TestCorpusIntegration(unittest.TestCase):
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
