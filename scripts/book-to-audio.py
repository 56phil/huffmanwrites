#!/usr/bin/env python3
"""Turn a LaTeX manuscript into narrated audio.

Four stages, each independently runnable:

    book-to-audio.py extract  --book ~/Developer/LaTeX/AllMyBooks/tsc \
                               --out work/tsc/manifest.json
    book-to-audio.py chunk    --manifest work/tsc/manifest.json \
                               --dir work/tsc/chunks
    book-to-audio.py speak    --chunks work/tsc/chunks \
                               --wavdir work/tsc/wav --voice Freya
    book-to-audio.py assemble --manifest work/tsc/manifest.json \
                               --wavdir work/tsc/wav --out work/tsc/out

`extract` turns LaTeX into speakable prose: it resolves the constructs that
the book actually uses (lettrine, chapter quote, pull quote, index, parts),
drops what cannot be read aloud, and records what it dropped. `chunk` splits
each chapter into pieces no larger than the speech backend accepts, always
on a sentence or paragraph boundary, and writes a plan the caller synthesises
from. `assemble` concatenates the rendered chapter audio, masters it to the
delivery spec (mono, 44.1 kHz, 192 kbps CBR, -19 LUFS), and packages an .m4b
with chapter markers.

The synthesis step is deliberately outside this script's core: it is a network
call whose backend differs per environment, and the manifest names each chunk
and the exact path its audio must land at. `speak` exists for the one backend
that can be driven from here without a harness — Ollama's OpenAI-compatible
`/v1/audio/speech` (Phonon) — and writes those paths. Any other backend can
write the same files and skip the stage entirely.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

# Chapters beyond this count would need new ordinals; the manuscript has none.
ORDINALS = (
    "One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve "
    "Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty"
).split()

# Commands whose entire argument is dropped: page furniture, cross-reference
# machinery, and the index (which TTS reads as strings of numbers).
DROP_WITH_ARGS = (
    "label", "index", "addcontentsline", "markboth", "phantomsection",
    "thispagestyle", "pagestyle", "pagenumbering", "setlength", "vspace",
    "hspace", "vfill", "hfill", "cleardoublepage", "newpage", "clearpage",
    "protect", "nocite", "caption", "ref", "pageref", "input", "include",
    "includegraphics", "bibliography", "bibliographystyle", "footnote",
    "hypertarget", "texorpdfstring", "Needspace", "needspace",
    "enlargethispage", "ifthenelse", "boolean",
)
# Commands whose argument is kept as text, unwrapped.
UNWRAP = (
    "textit", "textbf", "emph", "textsc", "textrm", "textsf", "textup",
    "textnormal", "underline", "mbox", "text", "url", "say", "textsuperscript",
    "textsubscript", "MakeUppercase", "MakeLowercase", "hphantom",
)
# Spacing and symbol commands.
SYMBOLS = {
    "ldots": "\u2026", "dots": "\u2026", "textellipsis": "\u2026",
    "textendash": "\u2013", "textemdash": "\u2014", "textquotedblleft": '"',
    "textquotedblright": '"', "textquoteleft": "'", "textquoteright": "'",
    "textbullet": ",", "dag": "\u2020", "S": "\u00a7", "P": "\u00b6",
    "copyright": "\u00a9", "textcopyright": "\u00a9", "euro": "\u20ac",
    "pounds": "\u00a3", "LaTeX": "LaTeX", "TeX": "TeX",
}
SPACING = (" ", "noindent", "indent", "quad", "qquad", "hfil", "hss",
           "centering", "raggedright", "smallskip", "medskip", "bigskip",
           "relax", "ignorespaces", "unskip", "leavevmode", "par")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(text: str) -> str:
    """Drop % comments, but not \\% escapes."""
    return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)


def take_group(text: str, i: int, open_ch: str = "{", close_ch: str = "}") -> tuple[str, int]:
    """Return (contents, index after closing brace) for a balanced group at i."""
    if i >= len(text) or text[i] != open_ch:
        raise ValueError(f"expected {open_ch!r} at {i}")
    depth = 0
    start = i + 1
    j = i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:j], j + 1
        j += 1
    raise ValueError("unbalanced group")


def consume_cmd(text: str, name: str, keep: str = "drop", star: bool = True) -> str:
    """Replace every \\name[opt]{arg} according to `keep`: drop|unwrap|raw."""
    out = []
    i = 0
    needle = "\\" + name
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        # Must be a complete command name: \index is not \indexentry.
        k = j + len(needle)
        if star and text.startswith("*", k):
            k += 1
        if k < len(text) and (text[k].isalpha()):
            out.append(text[i:j + len(needle)])
            i = j + len(needle)
            continue
        out.append(text[i:j])
        # Optional arguments (may repeat).
        n = k
        while n < len(text) and text[n] == "[":
            _, n = take_group(text, n, "[", "]")
        while n < len(text) and text[n] == "{":
            arg, n = take_group(text, n)
            if keep == "unwrap":
                out.append(arg)
        i = n
    return "".join(out)


def lettrine(text: str) -> str:
    """\\lettrine[opts]{A}{rest} -> Arest: the drop cap is the word's first letter."""
    out = []
    i = 0
    needle = "\\lettrine"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        n = j + len(needle)
        while n < len(text) and text[n] == "[":
            _, n = take_group(text, n, "[", "]")
        first, n = take_group(text, n)
        second = ""
        if n < len(text) and text[n] == "{":
            second, n = take_group(text, n)
        out.append(first + second)
        i = n
    return "".join(out)


def parbox(text: str) -> str:
    """\\parbox[t]{0.95\\linewidth}{content} -> content: the box is a layout."""
    out = []
    i = 0
    needle = "\\parbox"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        n = j + len(needle)
        while n < len(text) and text[n] == "[":
            _, n = take_group(text, n, "[", "]")
        if n < len(text) and text[n] == "{":
            _, n = take_group(text, n)          # width
        if n < len(text) and text[n] == "{":
            content, n = take_group(text, n)
            out.append(content)
        i = n
    return "".join(out)


def chapter_quote(text: str) -> str:
    """\\chapterquote[Author]{quote} -> quote, then the author on its own line."""
    out = []
    i = 0
    needle = "\\chapterquote"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        n = j + len(needle)
        author = ""
        if n < len(text) and text[n] == "[":
            author, n = take_group(text, n, "[", "]")
        quote, n = take_group(text, n)
        out.append(f"\n\n{clean_inline(quote)}\n\n{clean_inline(author)}\n\n")
        i = n
    return "".join(out)


def resolve_conditionals(text: str) -> str:
    """Pick one branch of a print/Kindle switch: audio follows the print book.

    `\\ifkindleEdition A \\else B \\fi` renders B in the PDF, and the PDF is
    what a listener is hearing, so B is the branch that gets narrated. Reading
    both would say the glossary twice.
    """
    pattern = re.compile(r"\\ifkindleEdition(.*?)\\else(.*?)\\fi", re.DOTALL)
    while pattern.search(text):
        text = pattern.sub(lambda m: m.group(2), text)
    return re.sub(r"\\if[a-zA-Z]+.*?\\fi", "", text, flags=re.DOTALL)


def environments(text: str, dropped: list[str]) -> str:
    """Flatten display environments to paragraphs; drop what cannot be read."""
    # Figures, tables and the index machinery are not narratable.
    for env in ("figure", "table", "tabular", "tikzpicture", "thebibliography",
                "multicols", "minipage"):
        pattern = re.compile(r"\\begin\{" + env + r"\*?\}.*?\\end\{" + env + r"\*?\}",
                             re.DOTALL)
        if pattern.search(text):
            dropped.append(env)
        text = pattern.sub("\n\n", text)

    # Type-size environments carry no meaning aloud: keep the text, lose the tag.
    text = re.sub(r"\\(?:begin|end)\{(?:small|footnotesize|large|Large|"
                  r"normalsize|center|flushleft|flushright|sloppypar)\}", "\n\n", text)

    # Pull quotes and plain quotes are read as their own paragraph.
    for env in ("pullquote", "quote", "quotation", "verse", "displayquote"):
        pattern = re.compile(r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}",
                             re.DOTALL)
        text = pattern.sub(lambda m: "\n\n" + m.group(1) + "\n\n", text)

    # Lists: each item becomes a paragraph so the reader pauses between them.
    # A description's \item[Term] keeps its term, or the glossary loses the
    # word being defined.
    for env in ("itemize", "enumerate", "description"):
        pattern = re.compile(r"\\begin\{" + env + r"\}(?:\[[^\]]*\])?(.*?)\\end\{"
                             + env + r"\}", re.DOTALL)
        text = pattern.sub(
            lambda m: "\n\n" + re.sub(r"\\item\s*(?:\[([^\]]*)\])?",
                                      lambda mm: "\n\n" + (mm.group(1) + ": "
                                                           if mm.group(1) else ""),
                                      m.group(1)) + "\n\n", text)

    # Anything left is unfamiliar: keep the body, note it.
    for m in re.finditer(r"\\begin\{([a-zA-Z*]+)\}", text):
        dropped.append("env:" + m.group(1))
    text = re.sub(r"\\begin\{[a-zA-Z*]+\}(?:\[[^\]]*\])?|\\end\{[a-zA-Z*]+\}",
                  "\n\n", text)
    return text



def clean_inline(text: str) -> str:
    """Inline LaTeX -> plain prose. Order matters: escapes before commands."""
    text = text.replace("\\\\", "\n")
    text = text.replace("~", " ")
    text = text.replace("\\,", " ").replace("\\;", " ").replace("\\!", "")
    text = text.replace("\\ ", " ")
    for esc, lit in (("\\&", "&"), ("\\%", "%"), ("\\$", "$"), ("\\#", "#"),
                     ("\\_", "_"), ("\\{", "{"), ("\\}", "}"),
                     ("\\textbackslash", "\\")):
        text = text.replace(esc, lit)
    for name in UNWRAP:
        text = consume_cmd(text, name, keep="unwrap")
    for name, glyph in SYMBOLS.items():
        text = re.sub(r"\\" + name + r"(?![a-zA-Z])", glyph.replace("\\", "\\\\"),
                      text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)          # leftover commands
    text = re.sub(r"\\[^a-zA-Z]", "", text)
    text = re.sub(r"[{}]", "", text)

    # Typography: the reader announces punctuation, so normalise the glyphs
    # a typesetter would choose into the marks a speaker would pause at.
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = re.sub(r"``(.*?)''", r'"\1"', text, flags=re.DOTALL)
    text = text.replace("``", '"').replace("''", '"')
    text = text.replace("`", "'")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u00a0", " ")
    text = unicodedata.normalize("NFC", text)
    return text


def tidy(text: str) -> str:
    """Paragraphs separated by one blank line; hard-wrapped source lines joined.

    A LaTeX source wraps mid-sentence, so every single newline inside a
    paragraph is a line break the reader must not hear. Paragraph breaks are
    the blank lines, and only those survive.
    """
    text = re.sub(r"[ \t]+", " ", text)
    paras = []
    for block in re.split(r"\n[ \t]*\n", text):
        joined = re.sub(r"\s*\n\s*", " ", block).strip()
        if not joined:
            continue
        # A paragraph that ends in a colon is a lead-in: a glossary term, or a
        # line introducing a list. The reader must not stop between them.
        if paras and paras[-1].endswith(":"):
            paras[-1] = f"{paras[-1]} {joined}"
        else:
            paras.append(joined)
    return "\n\n".join(paras)


def speakable(text: str) -> str:
    """Final pass: punctuation and symbols the backend reads badly."""
    text = text.replace("\u2026", "...")
    # A part title may carry an escape: "Witness \& Voice" is spoken, not printed.
    text = re.sub(r"\s*&\s*", " and ", text)
    # A spaced em dash is a rhetorical pause; a closed one joins words.
    text = re.sub(r"\s*\u2014\s*", ", ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*,", ",", text)
    return text.strip()


def split_chapter(path: Path) -> dict:
    raw = resolve_conditionals(strip_comments(read(path)))
    dropped: list[str] = []

    title = subtitle = ""
    m = re.search(r"\\chapter\*?\{", raw)
    if m:
        title, _ = take_group(raw, m.end() - 1)
    m = re.search(r"\\chaptersubtitle\{", raw)
    if m:
        subtitle, _ = take_group(raw, m.end() - 1)

    part = ""
    m = re.search(r"\\part\*?\{", raw)
    if m:
        part, _ = take_group(raw, m.end() - 1)

    raw = consume_cmd(raw, "chapter", keep="drop", star=True)
    raw = consume_cmd(raw, "chaptersubtitle", keep="drop")
    raw = consume_cmd(raw, "part", keep="drop", star=True)

    raw = lettrine(raw)
    raw = parbox(raw)
    raw = chapter_quote(raw)
    raw = environments(raw, dropped)
    for name in DROP_WITH_ARGS:
        raw = consume_cmd(raw, name, keep="drop")
    for name in SPACING:
        raw = re.sub(r"\\" + name + r"(?![a-zA-Z])", " ", raw)
    body = tidy(clean_inline(raw))

    return {
        "file": str(path),
        "part": speakable(clean_inline(part)).strip(),
        "title": speakable(clean_inline(title)).strip(),
        "subtitle": speakable(clean_inline(subtitle)).strip(),
        "own_title": bool(title.strip()),
        "body": body,
        "dropped": sorted(set(dropped)),
    }


def build_reading_order(book: Path) -> list[Path]:
    """Read mains/main.tex so the audio follows the book, not the filename sort."""
    main = book / "mains" / "main.tex"
    if not main.exists():
        return sorted((book / "content").rglob("*.tex"))
    order = []
    for line in read(main).splitlines():
        line = strip_comments(line).strip()
        m = re.match(r"\\(?:input|include)\{(.+?)\}", line)
        if m:
            p = book / (m.group(1) if m.group(1).endswith(".tex") else m.group(1) + ".tex")
            if p.exists():
                order.append(p)
    return order


# Front and back matter that a narrator reads, by file stem, and the order to
# read them in. The table of contents, half title, title page, index and
# colophon are page furniture: an audiobook announces its own structure.
FRONT = ["Copyright", "dedication", "epigraph", "foreword", "preface"]
BACK = ["aw", "ack", "ata", "fta", "rl", "glo"]

# \part{} names that are the book's own sections rather than numbered parts.
STRUCTURAL = {"prologue", "epilogue", "interlude", "introduction", "conclusion",
              "preface", "foreword", "afterword", "appendix", "postscript"}


def cmd_extract(args) -> int:
    book = Path(args.book).expanduser()
    content = book / "content"
    files = build_reading_order(book)
    if not files:
        print(f"no \\input order found under {book}", file=sys.stderr)
        return 1

    by_stem = {p.stem: p for p in files}
    if args.main_only:
        wanted = [p for p in files if p.parent.name == "MainMatter"]
    else:
        wanted = [by_stem[s] for s in FRONT if s in by_stem]
        wanted += [p for p in files if p.parent.name == "MainMatter"]
        wanted += [by_stem[s] for s in BACK if s in by_stem]

    chapters = []
    for p in wanted:
        ch = split_chapter(p)
        if not ch["body"].strip() and not ch["title"]:
            continue
        chapters.append(ch)

    if args.first:
        # A book of letters has interludes and part pages between the letters.
        # "--first N" means the first N things that carry a chapter title.
        seen = 0
        trimmed = []
        for ch in chapters:
            if not ch["own_title"]:
                continue
            trimmed.append(ch)
            seen += 1
            if seen == args.first:
                break
        chapters = trimmed

    # Number the numbered chapters, and announce parts where they begin.
    n = 0
    part_seen = ""
    for ch in chapters:
        stem = Path(ch["file"]).stem
        numbered = re.fullmatch(r"c[0-9a-f]", stem) is not None
        if numbered:
            n += 1
            ch["number"] = n
        else:
            ch["number"] = 0
        if ch["part"] and ch["part"] != part_seen:
            ch["announce_part"] = True
            part_seen = ch["part"]
            ch["title"] = ch["title"] or ch["part"]
        else:
            ch["announce_part"] = False

    for ch in chapters:
        # Heading and body are built separately: the heading is what chapter
        # marks and filenames use, and it must be one line. Joining the body in
        # and then truncating produced marks holding half a paragraph.
        heading = []
        if ch.get("announce_part"):
            # "Prologue" is a section of a book, not Part One of one; numbering
            # it would invent structure the print book does not have.
            if ch["part"].lower() in STRUCTURAL:
                heading.append(ch["part"] + ".")
            else:
                heading.append(f"Part {ordinal_for(chapters, ch['part'])}.")
                heading.append(ch["part"] + ".")
        if ch["number"]:
            heading.append(f"Chapter {ORDINALS[ch['number'] - 1]}.")
        if ch["title"] and ch["own_title"]:
            heading.append(sentence(ch["title"]))
        if ch["subtitle"]:
            heading.append(sentence(ch["subtitle"]))
        heading = [" ".join(h.split()) for h in heading]
        ch["heading"] = " ".join(heading)
        if ch["number"]:
            ch["label"] = f"{ch['number']:02d} {ch['title']}"
        elif ch.get("announce_part"):
            ch["label"] = (ch["part"] if ch["part"].lower() in STRUCTURAL
                           else f"Part {ordinal_for(chapters, ch['part'])} {ch['part']}")
        else:
            # An interlude carries prose but no title: name it by its file, or
            # the audio arrives under a placeholder that says nothing.
            ch["label"] = ch["title"] or Path(ch["file"]).stem.replace("-", " ")
        parts = heading + ([ch["body"]] if ch["body"] else [])
        ch["text"] = speakable("\n\n".join(parts))
        ch["words"] = len(ch["text"].split())
        ch["chars"] = len(ch["text"])
        ch["id"] = f"{ch['number']:02d}" if ch["number"] else Path(ch["file"]).stem

    total = sum(c["chars"] for c in chapters)

    # An optional id -> voice map, so a book narrated by several voices carries
    # that fact into the filenames and the chapter marks instead of living in
    # the shell history of whoever ran the render.
    if args.voices:
        voices = json.loads(Path(args.voices).read_text(encoding="utf-8"))
        unknown = {k for k in voices if k not in {c["id"] for c in chapters}}
        if unknown:
            print(f"voice map names unknown chapters: {sorted(unknown)}", file=sys.stderr)
            return 1
        for c in chapters:
            c["voice"] = voices.get(c["id"], "")

    manifest = {
        "book": str(book),
        "title": args.title,
        "author": args.author,
        "chapters": chapters,
        "total_chars": total,
        "total_words": sum(c["words"] for c in chapters),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    print(f"{len(chapters)} chapters, {manifest['total_words']:,} words, "
          f"{total:,} chars (~{total / 950 / 60:.1f} h at 950 chars/min)")
    for c in chapters:
        flag = f"  [{','.join(c['dropped'])}]" if c["dropped"] else ""
        print(f"  {c['id']:>3} {c['title'][:52]:<52} {c['chars']:>6}{flag}")
    return 0


def sentence(text: str) -> str:
    """Close a heading with a full stop unless it already carries terminators."""
    return text if text.rstrip().endswith((".", "?", "!", ":", ";")) else text + "."


def ordinal_for(chapters: list[dict], part: str) -> str:
    """The part's position among the parts that are actually numbered."""
    order = []
    for c in chapters:
        name = c["part"]
        if name and name not in order and name.lower() not in STRUCTURAL:
            order.append(name)
    return ORDINALS[order.index(part)]


def cmd_chunk(args) -> int:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    plan = []
    for ch in manifest["chapters"]:
        heading = (ch.get("heading") or "").strip()
        body = ch["text"]
        if heading and body.startswith(heading):
            body = body[len(heading):].lstrip()
        # The heading gets its own request even when it would fit inside the
        # first body chunk, because a pause between a chapter's title and its
        # first sentence can only be placed at a boundary between audio files.
        pieces: list[tuple[str, str]] = []
        if heading:
            pieces.append((heading, "heading"))
        pieces += [(t, "body") for t in split_for_speech(body, args.limit,
                                                         args.max_words)]
        for i, (text, role) in enumerate(pieces):
            name = f"{ch['id']}-{i:02d}"
            (d / f"{name}.txt").write_text(text, encoding="utf-8")
            plan.append({"name": name, "chapter": ch["id"], "index": i,
                         "role": role, "chars": len(text), "text": text})
    plan_path = d / "plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    print(f"{len(plan)} chunks -> {plan_path}")
    return 0


def split_for_speech(text: str, limit: int, max_words: int = 0) -> list[str]:
    """Split on paragraph, then sentence, boundaries; never mid-sentence.

    `limit` is characters. `max_words` caps a request by words, which is the
    honest bound: the speech backend stops after roughly eighty words whatever
    the character count, and a voice that reads quickly hits that ceiling at a
    smaller string. A character limit tuned for one voice silently truncates
    the tail for a faster one.
    """
    if len(text) <= limit and (not max_words or len(text.split()) <= max_words):
        return [text] if text.strip() else []

    def fits(chunk: str) -> bool:
        return len(chunk) <= limit and (not max_words or len(chunk.split()) <= max_words)

    pieces: list[str] = []
    cur = ""
    for para in text.split("\n\n"):
        if not fits(para):
            for sent in re.split(r"(?<=[.!?])\s+", para):
                if cur and not fits(cur + " " + sent):
                    pieces.append(cur.strip())
                    cur = ""
                cur += sent + " "
            continue
        if cur and not fits(cur + "\n\n" + para):
            pieces.append(cur.strip())
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        pieces.append(cur.strip())
    return pieces


def _post_speech(url: str, body: dict, timeout: float) -> bytes:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cmd_speak(args) -> int:
    """Render every chunk through Ollama's /v1/audio/speech and write the WAVs.

    Resumable: a chunk whose WAV already exists and carries a RIFF header is
    skipped, so a run that dies at chunk 300 costs three hundred chunks of
    nothing. The rate audit at the end is the truncation detector — a request
    the model cut short returns a short file and no error, and only a
    characters-per-second figure well above the voice's own pace shows it.
    """
    plan = json.loads((Path(args.chunks) / "plan.json").read_text(encoding="utf-8"))
    wavdir = Path(args.wavdir)
    wavdir.mkdir(parents=True, exist_ok=True)
    endpoint = args.url.rstrip("/") + "/v1/audio/speech"
    todo = [p for p in plan
            if args.force or not _has_riff(wavdir / f"{p['name']}.wav")]
    if not todo:
        print(f"all {len(plan)} chunks already rendered")
        return 0
    print(f"{len(todo)} of {len(plan)} chunks to render via {args.model}/{args.voice}")

    rates: list[tuple[float, str]] = []
    started = time.time()
    for n, item in enumerate(todo, start=1):
        text = item["text"]
        if len(text) > args.max_chars:
            print(f"  ! {item['name']}: {len(text)} chars exceeds the "
                  f"{args.max_chars}-char request limit", file=sys.stderr)
            return 2
        out = wavdir / f"{item['name']}.wav"
        for attempt in range(1, args.retries + 1):
            try:
                data = _post_speech(
                    endpoint,
                    {"model": args.model, "voice": args.voice, "input": text},
                    args.timeout)
                break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt == args.retries:
                    print(f"  ! {item['name']}: {exc}", file=sys.stderr)
                    return 1
                time.sleep(2 ** attempt)
        if not data.startswith(b"RIFF"):
            print(f"  ! {item['name']}: server returned {len(data)} bytes, not WAV",
                  file=sys.stderr)
            return 1
        out.write_bytes(data)
        dur = probe_duration(out)
        rate = len(text) / dur if dur else 0.0
        rates.append((rate, item["name"]))
        if n % 10 == 0 or n == len(todo):
            print(f"  {n:>4}/{len(todo)} {item['name']:<24} "
                  f"{dur:6.1f}s {rate:5.1f} c/s  "
                  f"[{time.time() - started:5.0f}s elapsed]")

    audio = sum(probe_duration(wavdir / f"{p['name']}.wav") for p in plan
                if _has_riff(wavdir / f"{p['name']}.wav"))
    print(f"\n{audio / 60:.1f} min of audio in {time.time() - started:.0f}s wall")
    # A truncated segment is one that produced far less audio than the voice's
    # own pace allows. Report the top of the distribution, not a pass/fail: the
    # threshold depends on the voice and is set from a measured median.
    if rates:
        rates.sort(reverse=True)
        median = rates[len(rates) // 2][0]
        print(f"chars/sec median {median:.1f}; fastest 5 (truncation suspects):")
        for rate, name in rates[:5]:
            print(f"  {rate:5.1f} c/s  {name}")
        fast = [x for x in rates if x[0] > median * 1.6]
        if fast:
            print(f"  ! {len(fast)} chunk(s) more than 60% above the median — "
                  f"check for truncation: {', '.join(n for _, n in fast[:5])}",
                  file=sys.stderr)
    return 0


def _has_riff(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return fh.read(4) == b"RIFF" and path.stat().st_size > 1024
    except OSError:
        return False


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


# The voice leaves roughly seven tenths of a second of dead air at the end of
# every request. Left in, it is added to whatever gap is asked for: a 0.8 s
# pause arrives as 1.6 s and a reader hears a hesitation nobody specified. Trim
# the edges to 50 ms first, and the number in the flag is the number between
# the words.
EDGE_TRIM = ("silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,"
             "areverse,"
             "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,"
             "areverse")


def probe_rate(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=sample_rate", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return int(out.stdout.strip() or 44100)


def silence(seconds: float, rate: int, path: Path, as_mp3: bool = False) -> Path:
    """A file of digital silence the concat demuxer can join to its neighbours.

    The stream has to match: the demuxer copies packets rather than decoding
    them, so a silence at 44.1 kHz spliced into 24 kHz chapters is a format
    error, not a quiet join. The rate is therefore probed, never assumed.
    """
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
           "-i", f"anullsrc=r={rate}:cl=mono", "-t", f"{seconds:.3f}"]
    if as_mp3:
        cmd += ["-c:a", "libmp3lame", "-b:a", "192k", "-ar", str(rate),
                "-ac", "1", "-write_xing", "0"]
    else:
        cmd += ["-c:a", "pcm_s16le"]
    run(cmd + [str(path)])
    return path


def cmd_assemble(args) -> int:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    wavdir = Path(args.wavdir)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    plan = json.loads((Path(args.chunks) / "plan.json").read_text(encoding="utf-8"))

    by_chapter: dict[str, list[dict]] = {}
    for item in plan:
        by_chapter.setdefault(item["chapter"], []).append(item)

    chapter_gap = max(0.0, args.chapter_gap)
    heading_gap = max(0.0, args.heading_gap)
    chunk_rate = 44100
    for item in plan:
        probe = wavdir / f"{item['name']}.wav"
        if probe.exists():
            chunk_rate = probe_rate(probe)
            break
    heading_silence = (silence(heading_gap, chunk_rate, outdir / "_heading-gap.wav")
                       if heading_gap else None)

    chapter_meta = []
    chapter_files: list[Path] = []
    t = 0.0
    for ch in manifest["chapters"]:
        items = [i for i in by_chapter.get(ch["id"], [])
                 if (wavdir / f"{i['name']}.wav").exists()]
        if not items:
            print(f"  ! no audio for chapter {ch['id']} ({ch['title']})", file=sys.stderr)
            continue
        entries: list[Path] = []
        head_trim = outdir / f"_{ch['id']}-head.wav"
        for pos, item in enumerate(items):
            src = wavdir / f"{item['name']}.wav"
            if (heading_silence and item.get("role") == "heading"
                    and pos < len(items) - 1):
                # Trim the heading first: its own trailing silence is the same
                # seven tenths, and inserting the pause after it untrimmed is
                # how a 0.8 s gap became 1.56 s on the first attempt.
                run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                     "-af", EDGE_TRIM, "-c:a", "pcm_s16le", str(head_trim)])
                entries += [head_trim, heading_silence]
                continue
            entries.append(src)
        listed = outdir / f"_{ch['id']}.txt"
        # ffmpeg resolves a concat list's entries relative to the list, so the
        # entries must be absolute or the render silently looks elsewhere.
        listed.write_text("".join(f"file '{p.resolve()}'\n" for p in entries),
                          encoding="utf-8")
        raw = outdir / f"_{ch['id']}-raw.wav"
        run(["ffmpeg", "-y", "-v", "error",
             "-f", "concat", "-safe", "0",
             "-i", str(listed), "-af", EDGE_TRIM,
             "-c:a", "pcm_s16le", str(raw)])

        # Every file carries its position, because a player that sorts by name
        # must land on the front matter before the prologue, and filenames here
        # are titles that sort no better than the book's own table of contents.
        label = f"{len(chapter_files) + 1:02d} {ch['label']}"
        if ch.get("voice"):
            label += f" - {ch['voice']}"
        mp3 = outdir / f"{safe_name(label)}.mp3"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(raw),
             "-af", "loudnorm=I=-19:TP=-3:LRA=11,"
                    "aresample=44100,"
                    "pan=mono|c0=0.5*c0+0.5*c1" if _is_stereo(raw) else
                    "loudnorm=I=-19:TP=-3:LRA=11,aresample=44100",
             "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "1",
             "-write_xing", "0", str(mp3)])
        dur = probe_duration(mp3)
        # An untitled page (a copyright notice, an interlude) still needs a mark
        # a listener can find: its label, which is what the file is called.
        mark = ch.get("heading") or ch["label"]
        chapter_meta.append((mark + (f" ({ch['voice']})" if ch.get("voice") else ""),
                             t, dur))
        chapter_files.append(mp3)
        t += dur + chapter_gap
        raw.unlink(missing_ok=True)
        listed.unlink()
        head_trim.unlink(missing_ok=True)
        print(f"  {ch['id']:>3} {mp3.name:<60} {dur / 60:6.1f} min")

    # One master file with chapter marks, for direct sale and for players.
    mp3s = [mp3 for mp3 in chapter_files if mp3.exists()]
    gap_file = (silence(chapter_gap, 44100, outdir / "_chapter-gap.mp3", as_mp3=True)
                if chapter_gap and len(mp3s) > 1 else None)
    entries: list[Path] = []
    for i, mp3 in enumerate(mp3s):
        entries.append(mp3)
        if gap_file and i < len(mp3s) - 1:
            entries.append(gap_file)
    concat_list = outdir / "_all.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in entries),
                           encoding="utf-8")
    meta = outdir / "_chapters.txt"
    lines = [";FFMETADATA1",
             f"title={manifest['title']}", f"artist={manifest['author']}",
             f"album={manifest['title']}", "genre=Audiobook"]
    for i, (name, start, dur) in enumerate(chapter_meta):
        # The gap after a chapter belongs to that chapter's mark: a mark that
        # ends where the sound stops leaves a stretch of the file that belongs
        # to nothing, and a player seeking into it shows no chapter at all.
        end = start + dur + (chapter_gap if i < len(chapter_meta) - 1 else 0.0)
        lines += ["[CHAPTER]", "TIMEBASE=1/1000",
                  f"START={int(start * 1000)}", f"END={int(end * 1000)}",
                  f"title={name}"]
    meta.write_text("\n".join(lines) + "\n", encoding="utf-8")

    m4b = outdir / f"{manifest['title']}.m4b"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-i", str(meta),
         "-map_metadata", "1", "-map_chapters", "1",
         "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "1",
         "-f", "ipod", str(m4b)])
    concat_list.unlink()
    for leftover in (gap_file, heading_silence):
        if leftover:
            leftover.unlink(missing_ok=True)
    print(f"\n{m4b}  {probe_duration(m4b) / 3600:.2f} h, {len(chapter_meta)} chapters")
    return 0


def safe_name(text: str) -> str:
    """A chapter title is prose; a filename is not. Keep it portable."""
    cleaned = re.sub(r'[?:/*"<>|\\]', "", text).strip()
    return re.sub(r"\s+", " ", cleaned)[:90]


def _is_stereo(path: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=channels", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return out.stdout.strip() not in ("", "1")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract")
    e.add_argument("--book", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--title", default="")
    e.add_argument("--author", default="Philip Huffman")
    e.add_argument("--main-only", action="store_true",
                   help="skip front and back matter, keep only the main matter")
    e.add_argument("--first", type=int, default=0,
                   help="keep only the first N chapters that carry a title")
    e.add_argument("--voices", default="",
                   help="JSON file mapping chapter id to the voice that reads it")
    e.set_defaults(func=cmd_extract)

    c = sub.add_parser("chunk")
    c.add_argument("--manifest", required=True)
    c.add_argument("--dir", required=True)
    c.add_argument("--limit", type=int, default=13000)
    c.add_argument("--max-words", type=int, default=0,
                   help="cap each request by words; the speech backend stops "
                        "after roughly eighty regardless of character count")
    c.set_defaults(func=cmd_chunk)

    s = sub.add_parser("speak")
    s.add_argument("--chunks", required=True)
    s.add_argument("--wavdir", required=True)
    s.add_argument("--url", default="http://localhost:11434",
                   help="Ollama base URL; the speech endpoint is /v1/audio/speech")
    s.add_argument("--model", default="phonon")
    s.add_argument("--voice", default="default")
    s.add_argument("--max-chars", type=int, default=4096,
                   help="the request limit the backend enforces; Phonon's is 4096")
    s.add_argument("--timeout", type=float, default=600.0)
    s.add_argument("--retries", type=int, default=3)
    s.add_argument("--force", action="store_true",
                   help="re-render chunks that already have audio")
    s.set_defaults(func=cmd_speak)

    a = sub.add_parser("assemble")
    a.add_argument("--manifest", required=True)
    a.add_argument("--chunks", required=True)
    a.add_argument("--wavdir", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--chapter-gap", type=float, default=2.0,
                   help="silence between chapters in the master, in seconds")
    a.add_argument("--heading-gap", type=float, default=0.8,
                   help="silence between a chapter's heading and its first "
                        "sentence, in seconds (the heading needs its own chunk)")
    a.set_defaults(func=cmd_assemble)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
