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

Run:  python3 scripts/run-gate-tests.py
      python3 scripts/run-gate-tests.py -v      # per-test names
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
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
