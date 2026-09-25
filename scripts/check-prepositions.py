#!/usr/bin/env python3
"""Flag sentences ending in a preposition, per the house rule adopted 2026-09-25.

"Never end a sentence with a preposition." This is a house style, not a claim
about English usage: stranding a preposition is idiomatic and often better in
speech. The site's register is formal and the rule is adopted anyway, because
restructuring the sentence tends to produce a tighter one.

Design, and why it is narrow
----------------------------
The failure that matters is a FALSE POSITIVE: a gate that fails a build on
correct writing teaches people to ignore it. So this gate does not attempt to
find every stranded preposition. It looks for a preposition sitting immediately
before terminal punctuation, and only for prepositions drawn from a curated
list.

The list excludes words that are routinely sentence-final as ADVERBS or verb
particles, because those are not stranded prepositions and flagging them would
be wrong:

    "the meeting is over"        over  = adverb
    "as noted above"             above = adverb
    "he walked past"             past  = adverb
    "I haven't seen him since"   since = adverb
    "please log in"              in    = verb particle

A sentence-final preposition may legitimately sit inside a quotation, a code
span, or a URL, and none of those is the editor's prose. Those spans are
removed before matching, for the same reason the em-dash gate exempts
dashes inside quotation marks: rewriting a quotation's grammar to satisfy a
style rule would corrupt the quotation the citation gate exists to protect.

Scope: body prose AND the frontmatter display fields (title, description,
hero_caption, hero_alt), because a stranded preposition in a `description` is
the summary a reader sees in a search result.

Pre-rule occurrences are recorded in scripts/preposition-baseline.txt, keyed by
file path. Like the em-dash ratchet, a file may be reduced freely but may not
grow past its recorded count. The baseline is a promise to look later, not a
licence.

Usage:
  check-prepositions.py                 # report every file with hits
  check-prepositions.py --file <path>   # one file, verbose, with line numbers
  check-prepositions.py --list          # counts per file, corpus-wide
  check-prepositions.py --check         # ratchet against the baseline; exit 1 if over
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
BASELINE = REPO / "scripts" / "preposition-baseline.txt"

# Prepositions that, when sentence-final, are near-always the stranded
# construction.
#
# Deliberately EXCLUDES two groups, because both would flag correct English:
#
#   * words routinely sentence-final as ADVERBS — over ("the meeting is over"),
#     above, before ("has broken hearts before"), through ("the whole way
#     through"), throughout, since, past, along, across, behind, below, down,
#     inside, near, off, out, outside, round, under, up.
#   * "within"/"without", which are sentence-final as adverbs in the set phrase
#     "from within and without".
PREPOSITIONS = (
    "about", "against", "amid", "amidst", "among", "amongst", "at",
    "beneath", "beside", "beyond", "by", "concerning", "considering",
    "despite", "during", "except", "for", "from", "in", "including", "into",
    "of", "on", "onto", "per", "regarding", "to", "toward", "towards",
    "upon", "versus", "via", "with",
)

_ALT = "|".join(PREPOSITIONS)

# Phrasal verbs, as explicit "verb particle" pairs.
#
# A verb-level guard cannot work here: the SAME verb forms a phrasal verb with
# one particle and a prepositional verb with another. "give in" is phrasal;
# "give it to" is not. So the unit of judgement is the pair.
#
# Two boundaries set the list's scope, and both matter for the gate's honesty:
#
#   * Only particles that are BOTH phrasal and prepositional need listing. The
#     adverb-only particles (up, out, off, over, down, away) are absent from
#     PREPOSITIONS entirely, so they never reach this table.
#   * A PREPOSITIONAL verb is NOT listed: "look for", "rely on", "ask for",
#     "think of", "care for" all take an object as a plain preposition, so
#     "what are you looking for?" and "not a defect to be embarrassed about"
#     strand a real preposition and must still be flagged. Listing them would
#     hide the very construction the rule exists to catch. That is why this
#     table holds "in", "on" and "about" and almost nothing else: those are the
#     particles where true phrasal use is common.
#
# The table is one pair per line. It must NOT be built with `.split()`:
# `.split()` splits on whitespace, so "log in" would become the two separate
# tokens "log" and "in" and every pair would be silently destroyed. Parse the
# lines instead — a gate that silently stops matching is the failure mode.
_PHRASAL_PAIRS = frozenset(
    line.strip()
    for line in """
    log in
    sign in
    check in
    chip in
    cash in
    dig in
    drop in
    factor in
    fill in
    give in
    hand in
    join in
    kick in
    lean in
    move in
    opt in
    plug in
    put in
    rein in
    rope in
    settle in
    sit in
    step in
    take in
    trade in
    tune in
    turn in
    weigh in
    zoom in
    break in
    cave in
    fall in
    fit in
    pull in
    set in
    bring in
    buy in
    call in
    come in
    count in
    feed in
    home in
    lock in
    nail in
    phase in
    pour in
    pump in
    send in
    show in
    slot in
    write in
    bog in
    key in
    creep in
    log on
    sign on
    hang on
    hold on
    move on
    pass on
    press on
    put on
    settle on
    step on
    take on
    catch on
    count on
    dawn on
    go on
    keep on
    plan on
    run on
    wait on
    work on
    carry on
    drag on
    feed on
    lean on
    let on
    tell on
    verge on
    urge on
    egg on
    rat on
    look on
    come on
    pile on
    pile in
    keep on
    bring about
    come about
    set about
    go about
    see about
    argue about
    wander about
    """.strip().splitlines()
    if line.strip()
)

# Pronoun/possessive that may sit between a phrasal verb and its particle
# ("would fill IT in"), so the pair may be split by one word.
_INTERVENING = frozenset("""
    it them him her us me you this that these those one
""".split())



# Irregular past tenses, mapped to their base form so a phrasal pair can match
# a sentence that uses the past tense ("the light KEPT on").
_IRREGULAR = {
    "kept": "keep", "crept": "creep", "left": "leave", "slept": "sleep",
    "felt": "feel", "held": "hold", "built": "build", "sent": "send",
    "spent": "spend", "bent": "bend", "lent": "lend", "lost": "lose",
    "made": "make", "took": "take", "gave": "give", "came": "come",
    "went": "go", "got": "get", "put": "put", "set": "set", "ran": "run",
    "sat": "sit", "stood": "stand", "told": "tell", "felt": "feel",
}


def _stem_forms(word: str) -> "set[str]":
    """Inflected forms of a verb, so 'sets' and 'filling' match 'set'/'fill'."""
    w = word.lower()
    forms = {w, w.rstrip("s")}
    # Irregular past tenses whose stem is not recoverable by suffix stripping:
    # "kept" -> "keep", "crept" -> "creep", "left" -> "leave".
    if w in _IRREGULAR:
        forms.add(_IRREGULAR[w])
    for f in list(forms):
        if f.endswith("e"):
            forms.add(f + "d")
            forms.add(f[:-1] + "ing")
        forms.add(f + "s")
        forms.add(f + "ed")
        forms.add(f + "ing")
        if len(f) > 2 and f[-1] == f[-2]:
            forms.add(f[:-1] + "ed")
            forms.add(f[:-1] + "ing")
    return forms




def _is_hyphen_compound(text: str, m) -> bool:
    """True if the matched particle is the tail of a hyphenated compound.

    "passers-by." and "hands-on." contain no stranded preposition: "by" and "on"
    are the second half of a single hyphenated word. The hyphen sits BEFORE the
    particle, so the check looks at the character before the match — the shape
    of `_is_phrasal`, which inspects what precedes, cannot see it.
    """
    start = m.start(1)
    return start > 0 and text[start - 1] == "-"


def _is_phrasal(text_before: str, particle: str) -> bool:
    """True if the words before a particle read as a listed phrasal verb.

    Two separations are handled. A pronoun between verb and particle ("fill IT
    in") needs only the preceding word. A FULL NOUN OBJECT is harder: "kept the
    light on" puts three words between verb and particle, so the verb is not
    adjacent at all. Rather than guess, scan back a few words and accept a
    phrasal pair found there — a stranded preposition is adjacent to its own
    verb's complement by definition, so a pair spanning an intervening noun
    phrase is the phrasal reading.
    """
    words = re.findall(r"[A-Za-z]+", text_before)
    if not words:
        return False
    p = particle.lower()
    # Look back up to four words, and skip a trailing pronoun so "fill it"
    # exposes "fill".
    window = words[-4:]
    if window and window[-1].lower() in _INTERVENING:
        window = window[:-1]
    for verb in window:
        for f in _stem_forms(verb):
            if f"{f} {p}" in _PHRASAL_PAIRS:
                return True
    return False

# Catenatives: a sentence-final "to" after one of these is the INFINITIVE MARKER
# with its verb elided ("even when you don't want to"), not a preposition.
_CATENATIVES = frozenset("""
    able afraid allowed appear apt bound careful certain compelled content
    continue decided delighted due eager easy entitled fail fated fit free
    free glad going gonna got happen have hesitate hope inclined intend keen
    liable like likely long love meant need obliged ought prefer prepared
    ready reluctant resolved seem struggle supposed sure tend trying used
    want willing wish wont
""".split())

# Set phrases that end in a listed preposition but are adverbial, not stranded.
_IDIOMS = (
    re.compile(r"\bto begin$", re.IGNORECASE),
    re.compile(r"\bto start$", re.IGNORECASE),
    re.compile(r"\bit depends$", re.IGNORECASE),
)

# Pronouns/possessives that may sit between a phrasal verb and its particle
# ("would fill IT in", "take THEM out"), so the guard must look past them.
_INTERVENING = frozenset("""
    it them him her us me you this that these those one
""".split())


# A preposition, then optional whitespace, then terminal punctuation.
# The trailing lookahead keeps this from firing mid-sentence: "what he was
# talking about, however, was" has a comma after the word, not a terminator.
_TERMINAL = re.compile(
    rf"\b({_ALT})\s*([.!?])(?=[\s)\]\"'\u201d\u2019]|$)",
    re.IGNORECASE,
)

# Spans that are not the editor's prose.
_QUOTES = re.compile(r"\u201c[^\u201d]*\u201d|\"[^\"]*\"")
_CODE = re.compile(r"`[^`]*`")
# Markdown link: keep the visible text (it is prose the reader sees), drop the
# destination (it is a URL, where the words are not prose).
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_AUTOLINK = re.compile(r"<https?://[^>]*>")
_BARE_URL = re.compile(r"https?://\S+")
# Footnote definitions and HTML comments are apparatus, not sentences.
_FOOTNOTE_DEF = re.compile(r"^\[\^[^\]]+\]:.*$", re.MULTILINE)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# Fenced code blocks: no prose inside.
_FENCED = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)

FRONTMATTER_PROSE_FIELDS = ("title", "description", "hero_caption", "hero_alt")


def split_frontmatter(text: str) -> "tuple[str, str]":
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def _blank(span: str) -> str:
    """Replace a span with spaces, preserving length and newlines.

    Whitespace-joining instead would let "word. Next" become "word. Next" with
    a new sentence boundary lost; keeping the length and the line structure
    means reported line numbers stay correct.
    """
    return "".join("\n" if ch == "\n" else " " for ch in span)


def strip_non_prose(text: str) -> str:
    """Blank out spans whose word order is not the editor's to change."""
    text = _FENCED.sub(lambda m: _blank(m.group(0)), text)
    text = _HTML_COMMENT.sub(lambda m: _blank(m.group(0)), text)
    text = _FOOTNOTE_DEF.sub(lambda m: _blank(m.group(0)), text)
    text = _CODE.sub(lambda m: _blank(m.group(0)), text)
    text = _AUTOLINK.sub(lambda m: _blank(m.group(0)), text)
    text = _MD_LINK.sub(lambda m: _blank(m.group(0)) + m.group(1), text)
    text = _BARE_URL.sub(lambda m: _blank(m.group(0)), text)
    # Quotation spans LAST, so a markdown link inside a quotation is already
    # reduced and the quotation still blanks cleanly.
    text = _QUOTES.sub(lambda m: _blank(m.group(0)), text)
    return text


def frontmatter_prose(front: str) -> str:
    """The display fields a reader sees, as prose."""
    out = []
    for line in front.splitlines():
        m = re.match(r"^\s*([A-Za-z_]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        if m.group(1) not in FRONTMATTER_PROSE_FIELDS:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out.append(value)
    return "\n".join(out)


def find(text: str, base_line: int = 0) -> "list[tuple[int, str, str]]":
    """Return (line_number, matched preposition, the trailing context)."""
    hits = []
    for m in _TERMINAL.finditer(text):
        # Phrasal-verb guard: "Please log in.", "decay sets in.", "fill it in."
        # The particle is not a stranded preposition in any of those.
        before = text[:m.start()].rstrip()
        if _is_hyphen_compound(text, m):
            continue
        if _is_phrasal(before, m.group(1)):
            continue
        prev = re.search(r"([A-Za-z]+)$", before)
        # Catenative guard: "to" after a catenative is the infinitive marker.
        if m.group(1).lower() == "to" and prev and prev.group(1).lower() in _CATENATIVES:
            continue
        # Idiom guard: set phrases that end in a listed preposition adverbially.
        if any(rx.search(before) for rx in _IDIOMS):
            continue
        line = base_line + text.count("\n", 0, m.start()) + 1
        # The sentence's final few words, for a reader to see what to rewrite.
        tail = text[max(0, m.start() - 60):m.end()]
        tail = " ".join(tail.split())
        hits.append((line, m.group(1).lower(), tail))
    return hits


def audit(path: pathlib.Path) -> "list[tuple[int, str, str]]":
    text = path.read_text(encoding="utf-8", errors="replace")
    front, body = split_frontmatter(text)
    hits = find(strip_non_prose(frontmatter_prose(front)))
    body_line = text.count("\n", 0, len(front)) + 1 if front else 0
    hits += find(strip_non_prose(body), body_line)
    return hits


def content_files() -> "list[pathlib.Path]":
    if not CONTENT.is_dir():
        return []
    return sorted(CONTENT.rglob("*.md"))


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_baseline() -> "dict[str, int]":
    out: dict[str, int] = {}
    if not BASELINE.is_file():
        return out
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        try:
            out[parts[0]] = int(parts[1])
        except ValueError:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", help="audit a single file and print every hit")
    ap.add_argument("--list", action="store_true", help="counts per file")
    ap.add_argument("--check", action="store_true",
                    help="ratchet against the baseline; exit 1 if any file grew")
    args = ap.parse_args()

    if args.file:
        p = pathlib.Path(args.file)
        if not p.is_absolute():
            p = REPO / p
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 2
        hits = audit(p)
        if not hits:
            print(f"{rel(p)}: 0 sentence-final preposition(s) — OK")
            return 0
        print(f"{rel(p)}: {len(hits)} sentence-final preposition(s)")
        for line, prep, tail in hits:
            print(f"  {line}: …{tail}")
        return 1

    files = content_files()
    if not files:
        print("prepositions: no content files found — glob broken?", file=sys.stderr)
        return 2

    counts = {rel(p): len(audit(p)) for p in files}
    total = sum(counts.values())

    if args.check:
        baseline = load_baseline()
        over = []
        for path, n in sorted(counts.items()):
            allowed = baseline.get(path, 0)
            if n > allowed:
                over.append((path, n, allowed))
        if over:
            print(f"prepositions: {len(over)} file(s) over baseline")
            for path, n, allowed in over:
                print(f"  {path}: {n} (baseline {allowed})")
            return 1
        print(f"prepositions: OK — no file over its baseline "
              f"({sum(baseline.values())} recorded, 0 currently over)")
        return 0

    if args.list:
        for path, n in sorted(counts.items()):
            if n:
                print(f"{n:>4}  {path}")
        print(f"prepositions: {total} across {sum(1 for n in counts.values() if n)} file(s)")
        return 0

    for path, n in sorted(counts.items()):
        if n:
            print(f"{rel(REPO / path)}: {n}")
    print(f"prepositions: {total} across {len(files)} file(s) scanned")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(141)
