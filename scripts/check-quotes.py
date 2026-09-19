#!/usr/bin/env python3
"""Guard the quotation-citation contract (CONVENTIONS/CLAUDE.md).

Every attribution carried by a piece is an epigraph, and an epigraph makes two
promises: that the words are really the author's, and that a reader can go check.
This gate enforces both.

  1. Quotations from translated works must name the translation. For a classical
     or foreign-language author, the attribution must give a translator (or a
     named rendering/edition), unless it is explicitly labelled a paraphrase.
     "Marcus Aurelius, Meditations, 6.21" is not a citation: 6.21 reads
     "convince or shew me ... gladly change" (Chrystal 1902), "prove and bring
     home to me ... amend" (Haines 1916), and "reprove me ... gladly retract"
     (Casaubon 1634).

  2. Every attribution must be backed by a resolvable URL in the same file,
     pointing at a source that names that author (the ## Sources list, a
     footnote, or inline). A quotation whose wording cannot be linked must be
     labelled a paraphrase or demoted to unquoted prose.

This gate is deliberately BASELINE-AWARE. The site has epigraphs that shipped
before the rule existed; failing the build on them would block every deploy.
scripts/quote-baseline.txt lists the exact attributions that predate the rule,
keyed by a hash of their text. Because the key is the text, editing any of them
removes the exemption: the rule catches up as each file is next touched, which
is the documented policy. No sweep.

Usage:
  check-quotes.py                  # verify (CI)
  check-quotes.py --quiet          # only report problems
  check-quotes.py --update-baseline  # re-bless every current attribution
  check-quotes.py --online         # also fetch each link: 200 + contains the words
  check-quotes.py --file content/posts/digests/foo.md
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
BASELINE = REPO / "scripts" / "quote-baseline.txt"

# Authors whose words reach English through a translation. Membership here means
# "the rendering is translator-dependent", which is the whole reason the rule
# exists. Keep this list to works that are genuinely translated; do not add
# modern English-language authors, who need a source link but no translator.
TRANSLATED_AUTHORS = (
    # Greco-Roman
    "Marcus Aurelius", "Epictetus", "Seneca", "Cicero", "Plutarch", "Homer",
    "Virgil", "Aristotle", "Plato", "Socrates", "Tacitus", "Thucydides",
    "Herodotus", "Diogenes", "Lucretius", "Sophocles", "Euripides",
    "Aeschylus", "Hesiod", "Xenophon", "Plotinus", "Epicurus", "Heraclitus",
    "Parmenides", "Zeno", "Cleanthes", "Musonius Rufus", "Juvenal", "Horace",
    "Ovid", "Catullus", "Sappho", "Pindar", "Demosthenes", "Boethius",
    "Augustine", "Aquinas", "Machiavelli", "Dante", "Montaigne", "Pascal",
    # Modern non-English
    "Goethe", "Nietzsche", "Kafka", "Rilke", "Dostoevsky", "Tolstoy", "Camus",
    "Kierkegaard", "Wittgenstein", "Schopenhauer", "Hegel", "Kant",
    "Descartes", "Spinoza", "Maimonides", "Rumi", "Hafiz", "Ibn", "Sun Tzu",
    "Lao Tzu", "Confucius", "Mencius", "Zhuangzi", "Sima Qian", "Basho",
    "Bashō", "Dazai", "Turgenev", "Chekhov", "Gogol", "Ibsen", "Strindberg",
    "Proust", "Flaubert", "Balzac", "Zola", "Celine", "Céline", "Borges",
    "Garcia Marquez", "García Márquez", "Neruda", "Paz", "Fuentes",
    # Scripture
    "Bible", "Quran", "Koran", "Torah", "Talmud", "Bhagavad Gita", "Upanishad",
    "Dhammapada", "Analects", "Tao Te Ching",
)

# A named translation is any of these. Deliberately permissive: the point is
# that the reader can tell WHICH rendering they are reading, not that a
# particular house format was used.
TRANSLATION_MARK = re.compile(
    r"trans\.|translated\s+by|translation\s+by|trans\.?\s*[A-Z]"
    r"|\b(?:Hays|Haines|Long|Carter|Casaubon|Chrystal|Waterfield|Hard|Gill|"
    r"Robin|Dobbin|Grene|Lattimore|Fagles|Merrill|Wilcox|Slavitt|Hammond|"
    r"Rowe|Reeve|Taylor|Barnes|Shepherd|Gaskell|Hicks|Yonge|Dillon|Seddon|"
    r"Falconer|Rackham|Bury|Moore|Shorey|Jowett|Grube|Cooper|Hutchinson|"
    r"Saunders|Crisp|Broadie|Rowe|Inwood|Gerson|Long|Sedley|Brunschwig)\b",
    re.IGNORECASE,
)
PARAPHRASE_MARK = re.compile(r"paraphras|free\s+rendering|loose\s+rendering|after\b", re.I)

# A line that carries an attribution: the credit after an em/en dash.
ATTRIBUTION = re.compile(r"(?:—|–)\s*(.+?)\s*$")

URL = re.compile(r"https?://[^\s\)\]\"'<>]+")

# Words that appear in attribution segments but are not authorship.
STOPWORDS = {"the", "a", "an", "as", "and", "in", "of", "on", "from", "quoted", "cited"}


def _die(msg: str, code: int = 2) -> "None":
    print(f"quotes: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def normalize(text: str) -> str:
    """Collapse whitespace and drop zero-width characters.

    Mandatory before any substring test: PDFs, HTML, and hard-wrapped text all
    break lines mid-sentence, so a literal test reports false misses on a source
    that does contain the quotation.

    Zero-width characters (U+200B &c.) are stripped for the same reason: MediaWiki
    emits `&#8203;` as a layout crutch, and a zero-width codepoint sitting inside
    a quotation splits it for a substring test while being invisible on screen.
    """
    return re.sub(r"[\u200b-\u200f\ufeff]", "", re.sub(r"\s+", " ", text)).strip()


# Tags that end a block. Replacing these with a SPACE (rather than with nothing)
# keeps adjacent paragraphs from fusing into one run of words. Every other tag is
# inline and must be removed with NO separator, because inserting one splits
# words apart: Wikisource renders a drop cap as `<span>F</span>irst`, which
# tag-with-space stripping turns into "F irst" and thereby fails a correct
# citation for Epictetus, *Discourses* 3.23.
_BLOCK_TAG = re.compile(
    r"</(?:p|div|li|ul|ol|tr|td|th|h[1-6]|blockquote|section|article|pre|table)\s*>"
    r"|<br\s*/?>",
    re.I,
)
_ANY_TAG = re.compile(r"<[^>]+>")


def html_to_text(body: str) -> str:
    """Reduce HTML to comparable text: entities decoded, inline markup removed.

    Three source shapes broke the checker before this existed, each producing a
    false accusation of fabrication against a correct citation:
      - `&#8217;` (Hillsdale encodes the Churchill apostrophe) — fixed by
        `html.unescape`, without which no apostrophe-bearing quote can match;
      - the `<span>F</span>...<span>irst</span>` drop cap, split by a `<style>`
        block that MediaWiki injects BETWEEN the halves of the word — fixed by
        removing script/style bodies with NO separator. Replacing them with a
        space (the obvious choice, and the first one tried) recreates the split
        it was meant to heal;
      - `&quot;` in search-result pages — same as the entity case.
    """
    stripped = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S | re.I)
    spaced = _BLOCK_TAG.sub(" ", stripped)
    return normalize(html.unescape(_ANY_TAG.sub("", spaced)))


_QUOTES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"',
                         "\u201d": '"', "\u2032": "'", "\u02bc": "'"})


def fold(text: str) -> str:
    """Canonicalize for comparison: straighten quotes, fold case, drop trailing
    punctuation, collapse whitespace.

    Typographic vs ASCII apostrophes are the same character to a reader and a
    different one to a substring test. The site writes `enemy's`; Gutenberg's
    Giles translation of *The Art of War* writes `enemy’s`. Failing on that is a
    false accusation. Terminal punctuation is likewise editorial: the site closes
    a Marcus Aurelius sentence with a period where the source has a semicolon
    before a following clause. Neither difference changes a single word, which is
    the only thing this gate is entitled to police.
    """
    return normalize(text.translate(_QUOTES)).lower().rstrip(".,;:!?\"'")


def content_files(only: "str | None") -> "list[Path]":
    if only:
        p = (REPO / only) if not Path(only).is_absolute() else Path(only)
        if not p.is_file():
            _die(f"file not found: {only}")
        return [p]
    # NB: `git ls-files content` only. Adding a trailing "*.md" pathspec makes
    # git match *.md at the repo root too (CLAUDE.md, SESSION_STATE.md), which
    # is how an earlier revision "audited" its own documentation.
    files = subprocess.run(
        ["git", "ls-files", "content"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout.split()
    return [REPO / f for f in files if f.endswith(".md") and f.startswith("content/")]


def author_of(segment: str) -> "str | None":
    """Pull the author name out of an attribution segment.

    'Marcus Aurelius, *Meditations*, 6.21' -> 'Marcus Aurelius'
    'Epictetus, trans. Robin Waterfield'   -> 'Epictetus'
    """
    head = re.split(r"[,(]|—|–", segment, maxsplit=1)[0]
    head = head.replace("*", "").strip()
    # Quotation marks around an attributed name are decoration, not part of the
    # name: `Attributed to a "Chinese Proverb"` extracted the author as
    # `Proverb";`, so the link-binding check searched for a surname that could
    # never appear on a line. Strip them before tokenising.
    head = head.strip("\"'“”‘’").strip()
    head = re.sub(r"^(?:by|from|after|attributed to(?: a| an| the)?|said of|as quoted by)\s+",
                  "", head, flags=re.I).strip()
    head = head.strip("\"'“”‘’").strip()
    if not head or len(head) > 60:
        return None
    words = [w for w in head.split() if w.lower() not in STOPWORDS]
    if not words:
        return None
    # Name-like: starts with a capital, no sentence punctuation.
    if not words[0][:1].isupper() or any(w.endswith(".") and len(w) > 2 for w in words):
        return None
    return " ".join(words[:4])


def surname(author: str) -> str:
    parts = [p for p in re.split(r"\s+", author) if p]
    return parts[-1] if parts else author


def is_translated(author: str) -> bool:
    for known in TRANSLATED_AUTHORS:
        if re.search(r"\b" + re.escape(known) + r"\b", author, re.I):
            return True
    return False


def epigraphs(path: Path) -> "list[dict]":
    """Extract attribution lines and the quotation they credit.

    Precision matters more than recall here: a false positive fails a build on
    prose. Em dashes are common in this corpus, so an attribution must look like
    a credit — short, name-first, and either self-contained (italics, a section
    number, a translator/parenthetical) or sitting directly beneath a quotation.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    out = []
    for i, raw in enumerate(lines):
        seg = raw.strip()
        if not seg:
            continue
        # Headings are not attributions, however many em dashes they carry.
        if seg.startswith("#"):
            continue
        m = ATTRIBUTION.search(seg)
        if not m:
            continue
        attribution = m.group(1).strip()
        if not attribution:
            continue
        # A credit is short; a prose clause after a dash is not. But a LENGTH
        # cap alone is the wrong test, and it produced the worst possible
        # failure: a properly-cited attribution — translator, year and source
        # link — exceeds any fixed limit, so improving a citation made the gate
        # STOP SEEING IT and report OK. The gate went blind exactly where the
        # work was done.
        #
        # The real distinction is structural, not length:
        #   - a CITATION is name-first, followed by optional apparatus
        #     (work, section, translator, link) — no finite verb sentence;
        #   - PROSE after a dash is a full clause with a verb and typically
        #     lower-case continuation.
        # So: allow a long attribution when it leads with a recognizable
        # author and contains no sentence-ending prose, and keep a generous
        # absolute ceiling as a backstop against genuine paragraphs.
        if len(attribution) > 90:
            if len(attribution) > 400:
                continue
            # Markdown links and italics are citation apparatus, not prose.
            stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", attribution)
            stripped = stripped.replace("*", "").strip()
            # A citation may open with an author, or with a work when the
            # credit reads "— *Meditations*, trans. …".
            head = stripped.lstrip("\"'“”*_ ")
            if not head[:1].isupper():
                continue
            # Prose runs on in lower case after the first clause; a citation
            # does not. Reject a bare lower-case sentence tail after a comma
            # that reads as narration rather than apparatus.
            if re.search(r",\s+(?:and|but|which|that|it|this|they|we|he|she)\b", stripped):
                continue
        # Prose colons and slashed lists are not citations. But a colon inside a
        # URL is not prose — `https:` contains one — so a bare `":" in
        # attribution` test rejected EVERY attribution carrying a source link,
        # which is the opposite of intent. Test the colon only outside links.
        text_only = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", attribution)
        text_only = re.sub(r"https?://\S+", "", text_only)
        if ":" in text_only or " / " in text_only:
            continue
        # An all-caps segment is a heading fragment ("THE CANDLE AND THE MIRROR").
        if attribution.replace("*", "").strip().isupper():
            continue
        # A sentence is not a citation.
        if attribution.rstrip("*").endswith("."):
            continue
        author = author_of(attribution)
        if author is None:
            continue

        dash = "—" if "—" in seg else "–"
        pre = seg[: seg.rindex(dash)].strip()

        # The quoted words: inline before the dash, else on the line directly
        # above (tolerating one blank). The lookback STOPS at the first
        # substantive line: wandering further up attaches unrelated prose, which
        # is how headings and section titles got mistaken for epigraphs.
        quote = pre if pre.startswith(("\"", "“", ">", "*", "_", "\u201c")) else ""
        # A bare blockquote or emphasis marker is not a quotation: "> — Author"
        # leaves pre as ">", which would otherwise satisfy the startswith test
        # and skip the lookback entirely.
        if len(normalize(quote).strip("\"'“”*>_ ")) < 15:
            quote = ""
            blanks = 0
            for j in range(i - 1, max(-1, i - 4), -1):
                prev = lines[j].strip()
                if not prev:
                    blanks += 1
                    if blanks > 1:
                        break
                    continue
                if prev.startswith(("\"", "“", ">", "*", "_", "\u201c")):
                    quote = prev
                break

        # REQUIRE a quotation. This is the property that makes a line an
        # attribution rather than a sentence that happens to contain a dash, and
        # it is what stops headings and section titles from being audited.
        if len(normalize(quote).strip("\"'“”*>_ ")) < 15:
            continue

        out.append(
            {
                "path": path,
                "line": i + 1,
                "attribution": attribution,
                "author": author,
                "quote": quote,
                "text": normalize(f"{quote} {attribution}"),
            }
        )
    return out


def linked_authors(text: str) -> "dict[str, list[str]]":
    """Map lowercase surname -> URLs appearing on lines that name it.

    A URL only counts as support for an author if it sits on a line that names
    that author. Checking every URL against every quotation in the file (the
    cross-product) fails spuriously: a file with a dozen sources would demand
    that each one contain each epigraph.
    """
    out: "dict[str, list[str]]" = {}
    for line in text.split("\n"):
        urls = URL.findall(line)
        if not urls:
            continue
        for w in re.findall(r"[A-Z][a-zA-Z\u00C0-\u024F'’\-]+", line):
            out.setdefault(w.lower(), []).extend(urls)
    return out


def audit(ep: dict, text: str, translated: bool) -> "list[str]":
    problems = []
    if translated:
        labelled_para = bool(PARAPHRASE_MARK.search(ep["attribution"]) or
                              PARAPHRASE_MARK.search(ep["quote"]))
        if not labelled_para and not TRANSLATION_MARK.search(ep["attribution"]):
            problems.append(
                f"names no translator — cite as "
                f"`{ep['author']}, <work>, <section> (trans. <Name>, <Year>)`, "
                f"or label it a paraphrase"
            )
    urls = URL.findall(text)
    if not urls:
        problems.append("no source URL anywhere in the file")
    else:
        sur = surname(ep["author"]).lower()
        if sur not in linked_authors(text):
            problems.append(
                f"no URL-bearing line names {surname(ep['author'])} — the link must "
                f"point at a source containing the quoted wording, not a bare page"
            )
    return problems


def signature(ep: dict) -> str:
    return hashlib.sha1(ep["text"].encode("utf-8")).hexdigest()[:12]


def load_baseline() -> "dict[str, str]":
    """Map 'file\\tsha1_12' -> attribution.

    The key MUST include the hash. Keying on the file alone would exempt every
    attribution in a file forever, including ones added after the rule — the
    hash is what makes the exemption text-specific, so editing a quotation
    withdraws its exemption and the rule applies on next touch.
    """
    if not BASELINE.is_file():
        return {}
    out = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) >= 2:
            out[f"{parts[0]}\t{parts[1]}"] = parts[2] if len(parts) > 2 else ""
    return out


def write_baseline(entries: "list[tuple[str, str, str]]") -> None:
    body = [
        "# Quotations that predate the citation rule (CLAUDE.md).",
        "# Keyed by file + a hash of the quoted text, so editing one removes its",
        "# exemption and the rule applies on next touch. Never hand-edit;",
        "# regenerate with: scripts/check-quotes.py --update-baseline",
        "#",
        "# file\tsha1_12\tattribution",
    ]
    for path, sig, display in sorted(entries):
        body.append(f"{path}\t{sig}\t{display}")
    BASELINE.write_text("\n".join(body) + "\n", encoding="utf-8")


def fetch_text(url: str) -> "tuple[str, str]":
    """Return (http_code, text). Never raises on binary — PDFs and the like.

    subprocess with text=True decodes stdout as UTF-8 and raises on a PDF's
    bytes, which is exactly the source type this check most needs to read. So
    fetch bytes, then extract text with pdftotext when the payload is a PDF.
    """
    # --compressed is load-bearing, not a nicety. Some hosts (quoteinvestigator.com
    # is one) force gzip on every response regardless of Accept-Encoding, so
    # without it curl hands back raw DEFLATE bytes. Decoding those as UTF-8 yields
    # mojibake in which the quotation obviously cannot be found, and the checker
    # reports a correct citation as a fabricated one -- a false accusation of
    # exactly the thing this gate exists to catch. Verified: the QI page for the
    # "best time to plant a tree" adage is 17 KB of gzip without this flag and
    # 84 KB of searchable HTML with it.
    r = subprocess.run(
        ["curl", "-sL", "--compressed", "--max-time", "25", "-A", "Mozilla/5.0",
         "-w", "\n@@%{http_code}", url],
        capture_output=True,
    )
    raw = r.stdout
    code = raw.rsplit(b"@@", 1)[-1].strip().decode("ascii", "replace")
    body = raw.rsplit(b"\n@@", 1)[0]

    if body[:5] == b"%PDF-":
        tmp = Path("/tmp") / f"quotecheck-{hashlib.sha1(url.encode()).hexdigest()[:10]}.pdf"
        tmp.write_bytes(body)
        if shutil.which("pdftotext"):
            p = subprocess.run(["pdftotext", str(tmp), "-"], capture_output=True)
            tmp.unlink(missing_ok=True)
            return code, p.stdout.decode("utf-8", "replace")
        tmp.unlink(missing_ok=True)
        return code, ""

    return code, body.decode("utf-8", "replace")


def check_online(url: str, needle: str, quiet: bool) -> "list[str]":
    """Fetch one URL; require HTTP 200 and the quoted wording (normalized).

    Some source types cannot be read by a plain fetch even though they are
    perfectly good citations: Internet Archive `/details/` pages are canvas
    viewers, `openlibrary.org/search/inside` renders results in JavaScript, and
    a PDF needs extraction. Treating "I could not read this" as "the words are
    not there" would fail correct citations — the same conflation that made the
    link checker call 18 live links dead. Those return a distinct code so the
    caller can report them as unverified rather than failed.
    """
    fails = []
    try:
        code, body = fetch_text(url)
    except Exception as exc:  # network/tooling
        # Cannot fetch is not the same as did not contain. A transient network
        # failure (HTTP 000, reset, timeout) says something about the checker's
        # circumstances, not about the citation.
        if not quiet:
            print(f"quotes:   could not fetch — {url} ({str(exc)[:40]})")
        return []
    if code != "200":
        # Founders Online answers an automated fetch with 202 Accepted and an
        # empty body, then serves the document normally; the National Archives
        # uses 202 as a queue signal. Treating it as a failure wrongly failed a
        # verified Jefferson citation. Any 2xx means the resource is live.
        if code.startswith("2"):
            return fails
        if code in ("000", "", None):
            if not quiet:
                print(f"quotes:   could not fetch — {url} ({code})")
            return []
        return [f"{url}: HTTP {code}"]

    # A 200 with an empty body is not "the wording is absent" — it is "we got
    # nothing to search". quoteinvestigator.com serves exactly that for some
    # URLs (its `/2014/09/14/keep-going/` page returns 200, 0 bytes) while
    # serving others in full. Testing the empty string would fail the citation
    # for the checker's own empty read. Report it as unverified instead.
    if not body.strip():
        if not quiet:
            print(f"quotes:   empty body at HTTP 200, cannot verify — {url}")
        return []

    # Unreadable-by-design source types: report, do not fail.
    UNREADABLE = (
        "archive.org/details/",        # canvas viewer, no text in HTML
        "openlibrary.org/search/inside",  # JS-rendered results
    )
    flat = html_to_text(body)
    n = fold(needle)
    if any(u in url for u in UNREADABLE):
        if n in fold(flat):
            if not quiet:
                print(f"quotes:   checked (unreadable source, stripped) — {url}")
        elif not quiet:
            print(f"quotes:   unreadable source, cannot verify — {url}")
        # Return in BOTH branches. The wording can only be tested against
        # stripped HTML here (the results are JS-rendered), so falling through to
        # a stricter test would fail a correct citation for a source that simply
        # cannot be read the ordinary way — and did: the Fiedler crystal-ball
        # citation was failed by exactly that fall-through even though the words
        # are present once the tags come off.
        return []

    # Compare on folded text: apostrophes straightened, case dropped, entity
    # references decoded, inline tags removed. See fold() and html_to_text() for
    # why each of those is a false-accusation class rather than a leniency.
    if len(n) >= 25 and n not in fold(flat):
        fails.append(f"{url}: does not contain {needle[:60]!r}")
    if not quiet:
        print(f"quotes:   checked {url}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description="Guard the quotation-citation contract.")
    ap.add_argument("--file", help="check a single file instead of the whole tree")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    ap.add_argument("--online", action="store_true",
                    help="fetch each link and verify HTTP 200 + wording")
    ap.add_argument("--update-baseline", action="store_true",
                    help="re-bless every current attribution as pre-rule")
    args = ap.parse_args()

    baseline = load_baseline()
    files = content_files(args.file)
    if not files:
        _die("no content files found — is this the site repo?")

    blessed: "list[tuple[str, str, str]]" = []
    violations: "list[tuple[dict, list[str]]]" = []
    total = 0

    for path in files:
        rel = str(path.relative_to(REPO))
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for ep in epigraphs(path):
            total += 1
            sig = signature(ep)
            # --update-baseline blesses EVERY current attribution, including the
            # non-compliant ones. That is the point of the flag: it records the
            # pre-rule state so the build passes while each file is fixed as it
            # is next touched. Blessing only the compliant ones would make the
            # flag useless — the debt is the thing being recorded.
            blessed.append((rel, sig, ep["attribution"][:80]))
            if f"{rel}\t{sig}" in baseline:
                continue
            probs = audit(ep, text, is_translated(ep["author"]))
            if probs:
                violations.append((ep, probs))

    if args.update_baseline:
        write_baseline(blessed)
        print(
            f"quotes: baseline updated — {len(blessed)} attribution(s) blessed "
            f"({len(violations)} of them non-compliant, now exempt until edited)"
        )
        return 0

    if not args.quiet:
        print(f"quotes: scanned {len(files)} files, {total} attributions")

    if args.online:
        # Verify each epigraph against the URLs on ITS OWN citation line — not
        # against every URL in the file, and not against every URL belonging to
        # the same author.
        #
        # Both narrower scopes matter. File-wide is a cross-product: a file with
        # a dozen sources would demand each one contain each quotation. Author-wide
        # is subtler and is what actually broke: a digest with two Sagan quotes and
        # two Sagan links tested each quote against both links, so a perfectly
        # correct citation failed because the OTHER Sagan URL legitimately did not
        # contain this quotation. The attribution line a quote sits on is the only
        # scope that means anything — that line IS the citation.
        checked = 0
        online_fails: "list[str]" = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            lines = text.split("\n")
            for ep in epigraphs(path):
                q = normalize(ep["quote"]).strip("\"'“”*>_ ")
                if len(q) < 25:
                    continue
                # URLs on the attribution line itself, plus the line above it
                # (short-form posts put the quote and the credit on one line, and
                # some put the link on the line after).
                idx = ep["line"] - 1
                window = "\n".join(lines[max(0, idx - 1): idx + 2])
                urls = sorted(set(URL.findall(window)))
                if not urls:
                    # No link on the citation line: fall back to the author's
                    # lines, which is the weakest scope that still checks
                    # something, and report it as the weaker check it is.
                    by_author = linked_authors(text)
                    urls = sorted(set(by_author.get(surname(ep["author"]).lower(), [])))
                for url in urls:
                    checked += 1
                    # COLLECT, do not abort. Returning on the first failure meant
                    # one run could only ever reveal one bad citation: fixing it
                    # and re-running exposed the next, so a corpus-wide audit took
                    # as many cycles as there were defects and looked like a
                    # whack-a-mole rather than a sweep. Every failure is already
                    # known by the time the loop ends; report them together.
                    for err in check_online(url, q, args.quiet):
                        online_fails.append(
                            f"{path.relative_to(REPO)}:{ep['line']}: {err}"
                        )
        if online_fails:
            print(f"quotes: FAIL — {len(online_fails)} citation(s) do not contain "
                  f"the words they are cited for:", file=sys.stderr)
            for f in online_fails:
                print(f"  {f}", file=sys.stderr)
            return 1
        if not args.quiet:
            print(f"quotes: verified {checked} epigraph link(s) online")

    if violations:
        print(
            f"quotes: FAIL — {len(violations)} attribution(s) lack a checkable source",
            file=sys.stderr,
        )
        for ep, probs in violations:
            rel = ep["path"].relative_to(REPO)
            print(f"\n  {rel}:{ep['line']}  — {ep['author']}", file=sys.stderr)
            print(f"    {ep['attribution'][:100]}", file=sys.stderr)
            for p in probs:
                print(f"    -> {p}", file=sys.stderr)
        print(
            "\n  Quotations from translated works must name the translation, and\n"
            "  every attribution needs a URL pointing at a source that contains\n"
            "  the quoted wording. See CLAUDE.md. If this attribution predates the\n"
            "  rule, run: scripts/check-quotes.py --update-baseline",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(f"quotes: OK — all attributions checkable ({len(baseline)} pre-rule)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
