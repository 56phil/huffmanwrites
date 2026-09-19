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
    """Collapse whitespace.

    Mandatory before any substring test: PDFs, HTML, and hard-wrapped text all
    break lines mid-sentence, so a literal test reports false misses on a source
    that does contain the quotation.
    """
    return re.sub(r"\s+", " ", text).strip()


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
    head = re.sub(r"^(?:by|from|after)\s+", "", head, flags=re.I).strip()
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
        # A credit is short. Prose clauses after a dash are not.
        if not attribution or len(attribution) > 90:
            continue
        # Prose colons and slashed lists are not citations.
        if ":" in attribution or " / " in attribution:
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
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0",
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
    """Fetch one URL; require HTTP 200 and the quoted wording (normalized)."""
    fails = []
    try:
        code, body = fetch_text(url)
    except Exception as exc:  # network/tooling
        return [f"{url}: fetch failed ({exc})"]
    if code != "200":
        return [f"{url}: HTTP {code}"]
    flat = normalize(body)
    n = normalize(needle)
    if len(n) >= 25 and n not in flat:
        fails.append(f"{url}: does not contain {n[:60]!r}")
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
        # Verify each epigraph against only the URLs that its own author's
        # line(s) carry. Never the cross-product: a file with many sources would
        # otherwise demand that every source contain every quotation.
        checked = 0
        for path in files:
            text = path.read_text(encoding="utf-8")
            by_author = linked_authors(text)
            for ep in epigraphs(path):
                q = normalize(ep["quote"]).strip("\"'“”*>_ ")
                if len(q) < 25:
                    continue
                for url in sorted(set(by_author.get(surname(ep["author"]).lower(), []))):
                    checked += 1
                    for err in check_online(url, q, args.quiet):
                        print(
                            f"quotes: FAIL — {path.relative_to(REPO)}:{ep['line']}: {err}",
                            file=sys.stderr,
                        )
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
