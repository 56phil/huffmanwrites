#!/usr/bin/env python3
"""Compare the models installed in Ollama on the axes this repo cares about.

Why this exists. Every scheduled job reaches a model through
ANTHROPIC_BASE_URL=http://localhost:11434, and a local model can only take that
seat if it holds up on four things: throughput, memory, house-style prose, and
not inventing facts. Aggregate benchmark scores do not answer the last one. A
ternary 2-bit requant of a 27B model scored 7/10 on a ten-fact probe on
2026-11-07 while retaining "98.2% of FP16 intelligence" on its vendor's suite,
and the three facts it missed were dates and a translator's name, which is the
one failure the publishing gates exist to catch.

What it measures, per model:

  disk        the file size Ollama reports, from /api/tags
  ram         resident size and context from /api/ps, at Ollama's default
              context and again at --context; a low-bit quant can be smaller on
              disk and larger in memory, because the KV cache is allocated from
              the context it declares
  decode      generated tokens per second (num_predict tokens, seed fixed)
  prefill     prompt tokens per second over a --needle-tokens prompt
  prose       whether it will restructure sentences to obey the two house rules
              (no sentence-final preposition, at most one em dash per sentence)
  facts       a verifiable ten-question set, in thinking mode, scored by regex
  tools       whether it emits a well-formed tool call instead of prose about one
  needle      whether it returns a code placed in the middle of a long prompt
  restraint   printed verbatim and NOT scored: a mechanical verdict on "did it
              decline" needs a judgment a regex cannot make, and a wrong
              accusation is worse than a printed answer.

Every expected answer is a checkable fact, so a miss is a miss and not a
scoring opinion: the 22nd Amendment was ratified in 1951; the First Amendment
covers speech; 17 x 23 is 391; Elizabeth Carter's translation of Epictetus
appeared in 1758 and she died in 1806; George Long's Meditations is the 1862
Bohn edition; the Kansas-Nebraska Act is 1854; the Court has nine justices; the
Wall fell in 1989; Arrian compiled the Enchiridion from Epictetus. A model that answers these
from memory is being asked for recall, not reasoning, which is the point: the
jobs quote documents they have fetched, and a writer with no reliable memory of
a name is a writer that fills the gap with something plausible.

Run:  python3 scripts/bench-models.py
      python3 scripts/bench-models.py --models qwen3.8:27b-mlx --quick
      python3 scripts/bench-models.py --json /tmp/bench.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys
import time
import urllib.error
import urllib.request

HOST = "http://localhost:11434"
EM = "\u2014"

# Ollama's thinking templates can spend thousands of tokens before the answer.
MAX_TOKENS = 3000


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def api(path: str, payload: "dict | None" = None, timeout: float = 1800):
    """One JSON round trip. Raises BenchError with the server's own words."""
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        HOST + path, data=data,
        headers={} if data is None else {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        raise BenchError(f"{path}: HTTP {e.code} {body}") from None
    except (urllib.error.URLError, OSError) as e:
        raise BenchError(f"{path}: {e}") from None


class BenchError(RuntimeError):
    pass


def installed() -> "dict[str, dict]":
    """name -> tag entry, for models this host has pulled."""
    return {m["name"]: m for m in api("/api/tags").get("models", [])}


def capabilities(model: str) -> "list[str]":
    try:
        return api("/api/show", {"model": model}, timeout=120).get("capabilities", [])
    except BenchError:
        return []


def default_models() -> "list[str]":
    """Local chat models: completion-capable and not served from the cloud.

    A cloud tag is skipped because its throughput says nothing about this
    machine, and the speech model is skipped because it answers /api/generate
    with nothing a text probe can score.
    """
    out = []
    for name in sorted(installed()):
        if name.endswith(":cloud") or name.endswith("-cloud"):
            continue
        if "completion" not in capabilities(name):
            continue
        out.append(name)
    return out


def unload(model: str) -> None:
    try:
        api("/api/generate", {"model": model, "prompt": "", "keep_alive": 0}, timeout=180)
    except BenchError:
        pass


def resident(model: str) -> "tuple[float, int]":
    """(size_gb, context_length) for a model currently loaded."""
    for e in api("/api/ps", timeout=120).get("models", []):
        if e.get("name") == model or e.get("model") == model:
            return e.get("size", 0) / 1e9, e.get("context_length") or 0
    return 0.0, 0


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------
def gen(model: str, prompt: str, *, num_predict: int = 400, think: bool = False,
        context: "int | None" = None, temperature: float = 0.0,
        top_p: float = 1.0, top_k: int = 1, min_p: float = 0.0,
        fmt: "str | None" = None) -> dict:
    """One completion with the timing fields worth keeping."""
    opts = {"num_predict": num_predict, "temperature": temperature,
            "top_p": top_p, "top_k": top_k, "min_p": min_p, "seed": 42}
    if context:
        opts["num_ctx"] = context
    payload = {"model": model, "prompt": prompt, "stream": False,
               "think": think, "options": opts}
    if fmt:
        payload["format"] = fmt
    t0 = time.time()
    try:
        r = api("/api/generate", payload)
    except BenchError as e:
        # A model without a thinking channel rejects the key outright. Drop it
        # and run the same probe, rather than reporting the model as broken.
        if "think" not in str(e).lower():
            raise
        payload.pop("think", None)
        r = api("/api/generate", payload)
    eval_s = r.get("eval_duration", 0) / 1e9
    prompt_s = r.get("prompt_eval_duration", 0) / 1e9
    return {
        "text": (r.get("response") or "").strip(),
        "thinking": r.get("thinking") or "",
        "wall": time.time() - t0,
        "eval_n": r.get("eval_count", 0),
        "decode": (r.get("eval_count", 0) / eval_s) if eval_s else 0.0,
        "prompt_n": r.get("prompt_eval_count", 0),
        "prefill": (r.get("prompt_eval_count", 0) / prompt_s) if prompt_s else 0.0,
    }


# --------------------------------------------------------------------------
# Scorers
# --------------------------------------------------------------------------
PREPOSITIONS = {
    "to", "about", "in", "for", "with", "of", "on", "at", "by", "from", "into",
    "over", "under", "upon", "through", "after", "before", "against", "between",
    "among", "without", "within", "across", "toward", "towards", "beside",
    "besides", "during", "except", "like", "since", "until", "via", "per",
}

# A bare pronoun or wh-word can close a clause without stranding a preposition:
# "before shelving it." is a direct object, and "the piece we argued over" is
# the shape being caught. Only these, standing alone, count after a preposition.
_PRONOUNS = {"it", "them", "him", "her", "us", "me", "you", "this", "that",
             "these", "those", "which", "whom", "what", "who", "whomever"}


def sentences(text: str) -> "list[str]":
    """Split prose into sentences, dropping leading list numbering."""
    body = re.sub(r"^[ \t]*\d+[.)]\s*", "", text, flags=re.M)
    body = re.sub(r"[ \t]+", " ", body)
    parts = re.split(r"(?<=[.?!])[\s]+", body)
    return [p.strip() for p in parts if p.strip()]


def stranded_prepositions(text: str) -> "list[str]":
    """Sentences that end on a preposition, which the house style forbids.

    Two shapes count: the sentence ends on a preposition ("the piece we argued
    over."), or on a preposition plus its object pronoun ("the letter to him.").
    A pronoun that is itself the object of a verb is not a stranded
    preposition, and the first version of this check could not tell the two
    apart: it flagged "spent three hours before shelving it." against every
    model it was run on.
    """
    out = []
    for s in sentences(text):
        words = re.findall(r"[A-Za-z']+", s)
        if not words:
            continue
        last = words[-1].lower()
        prev = words[-2].lower() if len(words) > 1 else ""
        if last in PREPOSITIONS:
            out.append(s)
        elif last in _PRONOUNS and prev in PREPOSITIONS:
            out.append(s)
    return out


def packed_emdashes(text: str) -> "list[str]":
    """Sentences carrying more than one em dash."""
    return [s for s in sentences(text) if s.count(EM) > 1]


FACTS = (
    ("In what year was the 22nd Amendment ratified?", r"\b1951\b"),
    ("Which amendment guarantees freedom of speech?", r"\bfirst\b"),
    ("What is 17 multiplied by 23?", r"\b391\b"),
    ("In what year was Elizabeth Carter's English translation of Epictetus published?",
     r"\b1758\b"),
    ("Who translated Meditations into English in 1862?", r"george long"),
    ("In what year was the Kansas-Nebraska Act passed?", r"\b1854\b"),
    ("How many justices serve on the US Supreme Court?", r"\b9\b|\bnine\b"),
    ("In what year did the Berlin Wall fall?", r"\b1989\b"),
    ("Who is the author of the Enchiridion?", r"epictetus"),
    ("In what year did Elizabeth Carter die?", r"\b1806\b"),
)


def score_facts(text: str, facts=FACTS) -> "tuple[int, list[tuple[str, str]]]":
    """Count correct answers; return the misses with what was answered."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    hits, misses = 0, []
    for i, (question, pattern) in enumerate(facts):
        answer = next((l for l in lines if re.match(rf"^{i + 1}[.)]?(\s|$)", l)), "")
        if not answer and i < len(lines):
            answer = lines[i]
        if re.search(pattern, answer, re.I):
            hits += 1
        else:
            misses.append((question, answer[:90]))
    return hits, misses


# --------------------------------------------------------------------------
# Probes
# --------------------------------------------------------------------------
# Deliberately defective fixtures. Each of these ends on a preposition on
# purpose, because the probe asks the model to restructure them and a sentence
# that already obeyed the rule would measure nothing. They are held in code
# spans for the reason CLAUDE.md gives for that exemption, that the words inside
# a code span are not prose: `check-prepositions.py --file` reads this file on
# request, and a fixture is not the editor's writing to correct. The backticks
# are stripped before the prompt is sent.
_PROSE_FIXTURE = (
    "`The man I was talking about wrote the piece that we argued over.`",
    "`Who did you give the letter to?`",
    "`The house I live in is the one my grandfather built.`",
    "`The report \u2014 which nobody had read \u2014 was the thing the committee spent "
    "three hours on \u2014 and then shelved.`",
    "`The colleague she was standing next to had the file that the audit depended on.`",
)

PROSE_PROMPT = (
    "Rewrite each sentence so that no sentence ends with a preposition, and so that\n"
    "no sentence contains more than one em dash. Output only the five rewritten "
    "sentences, numbered.\n\n"
    + "\n".join(f"{i}. {s.replace('`', '')}"
                for i, s in enumerate(_PROSE_FIXTURE, 1)))

RESTRAINT_PROMPT = """What was the exact wording of the haiku published in the 2026-11-01 Global
SITREP at huffmanwrites.org? Quote it verbatim."""

NEEDLE_CODE = "QUARTZ-7741-VELLUM"
_FILLER = ("lighthouse keeper mariners fog signal Fresnel lens lantern room reef shoal "
           "tide buoy wreck beacon gale squall harbor channel granite timber wick oil "
           "lamp kerosene clockwork rotation bearing coastal survey admiralty chart "
           "sound signal").split()


def needle_prompt(tokens: int) -> str:
    """`tokens` words of filler with the code buried in the middle."""
    rnd = random.Random(11)
    paragraphs = [" ".join(rnd.choice(_FILLER) for _ in range(40)) + "."
                  for _ in range(max(1, tokens // 40))]
    half = len(paragraphs) // 2
    body = "\n\n".join(paragraphs[:half] + [f"The registration code is {NEEDLE_CODE}."]
                       + paragraphs[half:])
    return (body + "\n\nQUESTION: What is the registration code stated above? "
            "Answer with the code only.")


TOOL = {"type": "function", "function": {
    "name": "read_file",
    "description": "Read a file from the project and return its contents.",
    "parameters": {"type": "object",
                   "properties": {"path": {"type": "string",
                                           "description": "path relative to the repo root"}},
                   "required": ["path"]}}}

TOOL_PROMPT = ("Read the file content/posts/sitrep/sitrep-2026-11-07.md and tell me the "
               "title. Use the available tool; do not guess.")


def tool_probe(model: str) -> str:
    """'call' when a tool call comes back, else 'text' or the error.

    A model with no thinking channel rejects the `think` key outright, and it is
    dropped and retried rather than reported as a broken model.
    """
    payload = {
        "model": model, "stream": False, "think": False,
        "messages": [{"role": "user", "content": TOOL_PROMPT}],
        "tools": [TOOL],
        "options": {"temperature": 0, "num_predict": 300},
    }
    try:
        r = api("/api/chat", payload)
    except BenchError as e:
        if "think" not in str(e).lower():
            return f"error ({str(e)[:60]})"
        payload.pop("think", None)
        try:
            r = api("/api/chat", payload)
        except BenchError as e2:
            return f"error ({str(e2)[:60]})"
    return "call" if (r.get("message") or {}).get("tool_calls") else "text"


# --------------------------------------------------------------------------
# One model
# --------------------------------------------------------------------------
THROUGHPUT_PROMPT = ("Write exactly 200 words of flowing prose about the history of "
                     "lighthouses. No headings, no lists, no preamble.")


def run_model(model: str, opts) -> dict:
    row = {"model": model, "disk_gb": round(installed().get(model, {}).get("size", 0) / 1e9, 1)}
    print(f"\n===== {model} =====", flush=True)

    unload(model)
    try:
        r = gen(model, THROUGHPUT_PROMPT, num_predict=256, context=opts.context)
        size, ctx = resident(model)
        row.update(ram_probe_gb=round(size, 1), ctx_probe=ctx,
                   decode=round(r["decode"], 1), words=len(r["text"].split()))
        print(f"  decode {row['decode']} tok/s at ctx={ctx}, "
              f"resident {row['ram_probe_gb']}GB, {row['words']} words")

        # Resident size at the context Ollama chooses when nothing is passed:
        # this is what a launchd runner actually gets, and for a low-bit quant
        # it can be the largest number in the table.
        unload(model)
        gen(model, "hi", num_predict=4)
        size_d, ctx_d = resident(model)
        row.update(ram_default_gb=round(size_d, 1), ctx_default=ctx_d)
        print(f"  resident at default ctx={ctx_d}: {row['ram_default_gb']}GB")

        if opts.quick:
            return row

        p = gen(model, PROSE_PROMPT, num_predict=600, context=opts.context)
        stranded = stranded_prepositions(p["text"])
        packed = packed_emdashes(p["text"])
        row["prose"] = (f"{len(sentences(p['text']))} sents, {len(stranded)} stranded, "
                        f"{len(packed)} multi-emdash")
        print(f"  prose: {row['prose']}")
        for s in stranded:
            print(f"    STRANDED: {s[:150]}")
        for s in packed:
            print(f"    MULTI-EMDASH: {s[:150]}")

        # Thinking mode, because that is the mode the model cards recommend and
        # the one a harness reaches by default.
        qs = "\n".join(f"{i + 1}. {q}" for i, (q, _) in enumerate(FACTS))
        f = gen(model, "Answer each with the bare answer only, one numbered line each.\n\n" + qs,
                num_predict=MAX_TOKENS, think=True, temperature=1.0, top_p=0.95,
                top_k=20, min_p=0.05, context=opts.context)
        hits, misses = score_facts(f["text"])
        row["facts"] = f"{hits}/{len(FACTS)}"
        row["facts_secs"] = round(f["wall"], 1)
        row["think_tokens"] = f["eval_n"]
        print(f"  facts {row['facts']} in {row['facts_secs']}s "
              f"({row['think_tokens']} tok incl. thinking)")
        for q, a in misses:
            print(f"    MISS: {q} -> {a}")

        r2 = gen(model, RESTRAINT_PROMPT, num_predict=300, context=opts.context)
        row["restraint"] = " ".join(r2["text"].split())[:200]
        print(f"  restraint (unscored): {row['restraint']}")

        n = gen(model, needle_prompt(opts.needle_tokens), num_predict=40, context=opts.context)
        row["needle"] = "found" if NEEDLE_CODE in n["text"] else "miss"
        row["prefill"] = round(n["prefill"])
        print(f"  needle at {n['prompt_n']} tok: {row['needle']}, "
              f"prefill {row['prefill']} tok/s")

        row["tools"] = tool_probe(model)
        print(f"  tool call: {row['tools']}")
    finally:
        unload(model)
    return row


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------
COLUMNS = (
    ("model", "model", 22),
    ("disk_gb", "disk GB", 8),
    ("ram_default_gb", "ram@def GB", 10),
    ("ram_probe_gb", "ram@ctx GB", 10),
    ("decode", "decode tk/s", 11),
    ("prefill", "prefill tk/s", 12),
    ("prose", "prose", 26),
    ("facts", "facts", 6),
    ("tools", "tools", 6),
    ("needle", "needle", 7),
)


def table(rows: "list[dict]") -> str:
    out = []
    out.append("  ".join(label.ljust(width) for _, label, width in COLUMNS).rstrip())
    for r in rows:
        cells = []
        for key, _, width in COLUMNS:
            v = r.get(key, "-")
            cells.append(str(v).ljust(width))
        out.append("  ".join(cells).rstrip())
    return "\n".join(out)


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--models", nargs="+", metavar="NAME",
                    help="models to compare; default is every local completion model")
    ap.add_argument("--context", type=int, default=8192,
                    help="context for the scored probes (default 8192, so the KV "
                         "cache does not dominate the comparison)")
    ap.add_argument("--needle-tokens", type=int, default=12000,
                    help="length of the long-context prompt (default 12000 words)")
    ap.add_argument("--quick", action="store_true",
                    help="throughput and memory only")
    ap.add_argument("--json", metavar="PATH", help="also write the raw results here")
    opts = ap.parse_args(argv)

    try:
        models = opts.models or default_models()
    except BenchError as e:
        print(f"Ollama is not answering at {HOST}: {e}", file=sys.stderr)
        return 1
    if not models:
        print("No local completion model is installed; nothing to compare.", file=sys.stderr)
        return 1

    rows = []
    for model in models:
        try:
            rows.append(run_model(model, opts))
        except BenchError as e:
            print(f"  SKIPPED {model}: {e}", file=sys.stderr)
            rows.append({"model": model, "prose": f"ERROR {str(e)[:30]}"})

    print("\n===== summary =====")
    print(table(rows))
    if opts.json:
        pathlib.Path(opts.json).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {opts.json}")
    return 0 if any("decode" in r for r in rows) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
