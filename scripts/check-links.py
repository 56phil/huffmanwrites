#!/usr/bin/env python3
"""Verify every external URL cited in content/.

The failure this guards against is specific and it has already happened once:
the Forbes approval-rating link in `the-danger-of-a-useless-president.md` was
*constructed* from the pattern of other Forbes URLs rather than verified, and a
placeholder `https://www.washingtonpost.com/style/` sat in a Sources list until
it was caught by hand. A fabricated citation is the worst kind of error a
fact-checked publication can ship, because it looks exactly like a real one.

`--online` fetches every external URL in content/ and reports what it finds.
This is deliberately NOT wired into CI: network access in the deploy path makes
builds flaky, and a 403 from a site that blocks bots is not evidence that a link
is fabricated. Run it before publishing, and periodically.

Verdicts, in order of how much they should worry you:

  DEAD     404/410 — the resource is definitively gone. This is the ONLY status
           that is evidence of rot. Check it.
  REDIRECT the link resolves but lands somewhere else (often a homepage). The
           cited page may not exist; the reader will not see what was promised.
  BLOCKED  401/403/429. The host refuses automated clients as a matter of
           policy. NOT evidence of rot or fabrication — Reuters, the Post and
           Cook all do this.
  UNVERIFIED timeout, connection reset, SSL failure, 5xx, or a 406 content
           negotiation refusal. "We could not look" — a statement about the
           checker, not the citation. Deliberately NOT a failure: conflating it
           with DEAD produced 18 false alarms in one sweep and would train the
           reader to ignore the gate.
  OK       200 with content.

Exit codes: 0 nothing wrong, 1 dead or redirecting links found, 2 fetch error
or coverage floor not met.
"""

from __future__ import annotations

import argparse
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

URL = re.compile(r"https?://[^\s\)\]\"'<>]+")

# Trailing punctuation that markdown prose leaves attached to a URL.
TRAILING = ".,;:!?"

# Hosts that refuse automated clients as a matter of policy. A 403 here is
# expected and says nothing about whether the link is real. Kept explicit so the
# report can distinguish "we could not check" from "this is broken".
#
# Reuters belongs here and was missing: it answers every automated request with
# 401, so 24 perfectly good citations were being reported as DEAD. That is the
# same false-positive class as calling Inside Elections unfetchable — a check
# that cannot see is not evidence that there is nothing to see. Add a host here
# only after confirming the refusal is policy (consistent 401/403/429 across
# different URLs on that host), never merely because one link failed.
BOT_BLOCKING = (
    "cookpolitical.com", "realclearpolitics.com", "centerforpolitics.org",
    "insideelections.com", "washingtonpost.com", "nytimes.com",
    "wsj.com", "bloomberg.com", "economist.com",
    "amazon.com", "substack.com", "natesilver.net", "twitter.com", "x.com",
    "facebook.com", "linkedin.com", "instagram.com",
    # Confirmed 401 to automated clients across multiple URLs:
    "reuters.com", "jp.reuters.com", "marketwatch.com", "ft.com",
)

# Our own domain: checked against the built site in CI, not fetched here.
OWN = ("huffmanwrites.org", "localhost")


def die(msg: str, code: int = 2) -> "None":
    print(f"links: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def clean(url: str) -> str:
    return url.rstrip(TRAILING)


# Minimum plausible corpus. Used by every mode so a gate can never print a
# clean result for an empty or mis-targeted scan. Set well below current actual
# counts (200 files, ~750 URLs) so ordinary content growth never trips it, but
# high enough that a broken path or glob does.
MIN_FILES = 100
MIN_URLS = 200


def _die_floor(msg: str) -> "None":
    print(f"links: ERROR: coverage floor not met — {msg}", file=sys.stderr)
    sys.exit(2)


def host_of(url: str) -> str:
    m = re.match(r"https?://([^/:]+)", url)
    return (m.group(1) if m else "").lower()


def is_blocking(url: str) -> bool:
    h = host_of(url)
    return any(h == b or h.endswith("." + b) for b in BOT_BLOCKING)


def is_own(url: str) -> bool:
    h = host_of(url)
    return any(h == o or h.endswith("." + o) for o in OWN)


def collect() -> "dict[str, list[str]]":
    """Map URL -> [files citing it]."""
    out: "dict[str, list[str]]" = {}
    for path in sorted(CONTENT.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for raw in URL.findall(text):
            u = clean(raw)
            if is_own(u):
                continue
            rel = str(path.relative_to(REPO))
            out.setdefault(u, [])
            if rel not in out[u]:
                out[u].append(rel)
    return out


# A URL still carrying its template placeholder. Deterministic, offline, and
# the exact signature of "I meant to come back and fill this in."
#
# Applied to the RAW line, not to an extracted URL token. That distinction is
# load-bearing: the URL extractor excludes `]` from its character class (so a
# markdown link `[text](url)` tokenises cleanly), which silently truncates
# `https://arxiv.org/abs/[ID]` to `https://arxiv.org/abs/[ID` and makes a
# bracket-balanced pattern unmatchable. Detecting on raw text means an
# extraction quirk can never hide a placeholder again — which is exactly what
# happened when this gate reported OK on a file that still contained one.
PLACEHOLDER = re.compile(
    # The gap may not cross whitespace or a delimiter that ends a URL token
    # (`)`, `]`, `,`, quote, angle bracket). Without that bound the gap runs
    # from a real URL into unrelated markdown — `https://medium.com/?ref=x),[Substack]`
    # matched and was reported as a placeholder it was not.
    #
    # The bracket rule also must not fire inside a URL FRAGMENT. Wikiquote
    # anchors legitimately end in `_[Episode_1]` — a working link, e.g.
    # `en.wikiquote.org/wiki/Carl_Sagan#The_Shores_of_the_Cosmic_Ocean_[Episode_1]`
    # — which this pattern rejected as a placeholder. Excluding `#` from the gap
    # keeps the scan in the path, where a bracketed placeholder actually lives.
    r"https?://[^\s#)\]\"'<>,]*?(?:"
    r"\[[A-Za-z_]+\]?|"        # [ID] or a truncated [ID
    r"\{[^}]*\}?|"             # {id}
    r"<[^>]*>?|"               # <NUMBER>
    r"\bTODO\b|\bFIXME\b|\bXXX\b|"
    r"example\.(?:com|org|net)|placeholder|/\.\.\."
    r")",
    re.I,
)

# A host that is plainly not a real publisher of news analysis.
NOT_A_SOURCE = re.compile(r"https?://(?:www\.)?(?:zombo\.com|invalid|localhost\.[a-z])", re.I)


def blocklisted() -> "set[str]":
    """URLs proven fabricated. Deterministic gate; see check-links-blocklist.txt."""
    path = REPO / "scripts" / "check-links-blocklist.txt"
    if not path.is_file():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def deterministic_scan() -> int:
    """Offline checks that must pass in CI. No network, no excuses."""
    bad_block = blocklisted()
    placeholder_hits: "list[tuple[str, str]]" = []
    blocked_hits: "list[tuple[str, str]]" = []

    # Coverage floor. Every gate in this repo exists because a detector once
    # reported OK while blind to the thing it existed to find. The cheapest
    # guard against that is to refuse to say OK unless a plausible amount of
    # input was actually examined: a moved directory, a bad glob, or a refactor
    # that stops the scan matching would otherwise print a clean bill of health.
    scanned = 0
    urls_seen = 0

    for path in sorted(CONTENT.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        scanned += 1
        rel = str(path.relative_to(REPO))
        # Placeholders: scan every line, on raw text.
        for i, line in enumerate(text.split("\n"), 1):
            m = PLACEHOLDER.search(line)
            if m:
                placeholder_hits.append((f"{rel}:{i}", m.group(0)))
        # Blocklist: scan extracted URLs, which is exact-match by design.
        for raw in URL.findall(text):
            u = clean(raw)
            urls_seen += 1
            if NOT_A_SOURCE.search(u):
                placeholder_hits.append((rel, u))
            if u in bad_block:
                blocked_hits.append((rel, u))

    if scanned < MIN_FILES or urls_seen < MIN_URLS:
        _die_floor(f"examined only {scanned} file(s) and {urls_seen} URL(s); "
                   f"expected at least {MIN_FILES} and {MIN_URLS}. The scan is "
                   f"not seeing the corpus, so a pass would be meaningless.")

    if placeholder_hits:
        print(f"links: FAIL — {len(placeholder_hits)} URL(s) still carry a "
              f"placeholder:", file=sys.stderr)
        for where, u in placeholder_hits:
            print(f"  {where}\n      {u}", file=sys.stderr)

    if blocked_hits:
        print(f"links: FAIL — {len(blocked_hits)} citation(s) previously proven "
              f"fabricated have returned:", file=sys.stderr)
        for where, u in blocked_hits:
            print(f"  {where}\n      {u}", file=sys.stderr)

    if placeholder_hits or blocked_hits:
        print(
            "\n  A URL that resolves to a DIFFERENT article is a fabrication even\n"
            "  though the link returns 200 — that is the failure this guards.\n"
            "  See CLAUDE.md §Citations, and scripts/check-links-blocklist.txt.",
            file=sys.stderr,
        )
        return 1

    print(f"links: OK — no placeholder or blocklisted URLs "
          f"({len(bad_block)} known-bad recorded)")
    return 0


def probe(args: "tuple[str, float]") -> "tuple[str, int, str, str]":
    """Return (url, status, verdict, detail). Never raises."""
    url, timeout = args
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://huffmanwrites.org/",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            code = r.status
            final = r.geturl()
            # Read a little so the redirect chain resolves, but do not slurp
            # whole PDFs into memory for a status check.
            try:
                r.read(2048)
            except Exception:
                pass
        if final.rstrip("/") != url.rstrip("/") and code in (200, 301, 302):
            base_final = re.sub(r"^https?://([^/]+)/?$", r"\1", final)
            base_url = re.sub(r"^https?://([^/]+)/?$", r"\1", url)
            if base_final != base_url:
                return url, code, "REDIRECT", f"-> {final}"
        return url, code, "OK", ""
    except urllib.error.HTTPError as e:
        code = e.code
        # 401 belongs in the blocked family alongside 403/429. A paywalled or
        # bot-hostile host answers automated clients with 401 Unauthorized —
        # Reuters does this on every URL — and treating that as DEAD reported 24
        # perfectly good citations as broken. The host list alone was not enough:
        # adding Reuters to BOT_BLOCKING changed nothing, because this branch
        # never consulted the list for a 401. The status code, not just the host,
        # decides whether "we were refused" or "this is gone".
        if code in (401, 403, 429) and is_blocking(url):
            return url, code, "BLOCKED", "host refuses automated clients"
        if code in (401, 403, 429):
            return url, code, "BLOCKED", f"{code} (not a known bot-blocker)"
        if code in (404, 410):
            # The ONLY status that is definitive evidence the resource is gone.
            return url, code, "DEAD", f"HTTP {code}"
        if code == 406:
            # A content-negotiation refusal, not a missing page. arXiv answers
            # an Accept header it dislikes this way on PDF URLs that exist.
            return url, code, "UNVERIFIED", "406 content negotiation refused"
        return url, code, "UNVERIFIED", f"HTTP {code} (server-side)"
    except socket.timeout:
        return url, 0, "UNVERIFIED", "timeout — host may be refusing us"
    except urllib.error.URLError as e:
        # A reset, an SSL failure or a DNS blip is "we could not look", not
        # "it is not there". Reporting these as DEAD produced 18 false alarms in
        # one sweep (Washington Post timeouts, Open Library resets) and would
        # have trained the reader to ignore the gate.
        reason = str(e.reason)
        return url, 0, "UNVERIFIED", f"unreachable: {reason[:40]}"
    except Exception as e:  # noqa: BLE001 - report, never crash the sweep
        return url, 0, "UNVERIFIED", f"{type(e).__name__}: {str(e)[:40]}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify external URLs cited in content/.")
    ap.add_argument("--online", action="store_true",
                    help="actually fetch every URL (no network means no check)")
    ap.add_argument("--check", action="store_true",
                    help="offline CI gate: placeholders + blocklist only")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.check:
        return deterministic_scan()

    table = collect()
    if not args.online:
        for u, files in sorted(table.items()):
            print(f"{u}\n    {', '.join(files)}")
        print(f"\nlinks: {len(table)} external URL(s) across "
              f"{len({f for v in table.values() for f in v})} file(s). "
              f"Re-run with --online to verify them.", file=sys.stderr)
        return 0

    if not table:
        print("links: no external URLs in content/", file=sys.stderr)
        return 0

    if len(table) < MIN_URLS:
        _die_floor(f"found only {len(table)} external URL(s) in content/; "
                   f"expected at least {MIN_URLS}. The sweep is not seeing the "
                   f"corpus, so a clean result would be meaningless.")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(probe, [(u, args.timeout) for u in table]))

    dead = [r for r in results if r[2] == "DEAD"]
    redir = [r for r in results if r[2] == "REDIRECT"]
    blocked = [r for r in results if r[2] == "BLOCKED"]
    unver = [r for r in results if r[2] == "UNVERIFIED"]
    ok = [r for r in results if r[2] == "OK"]

    if args.json:
        import json
        print(json.dumps([{"url": u, "status": s, "verdict": v, "detail": d,
                           "files": table[u]} for u, s, v, d in results], indent=2))
        return 1 if (dead or redir) else 0

    for label, rows in (("DEAD", dead), ("REDIRECT", redir)):
        if not rows:
            continue
        print(f"\n{label} ({len(rows)}):")
        for u, s, v, d in sorted(rows):
            print(f"  {u}\n      {d}")
            print(f"      cited in: {', '.join(table[u])}")

    if blocked and not args.quiet:
        print(f"\nBLOCKED ({len(blocked)}) — host refuses automated clients; "
              f"not evidence of fabrication:")
        for u, s, v, d in sorted(blocked):
            print(f"  [{s}] {u}")

    if unver and not args.quiet:
        print(f"\nUNVERIFIED ({len(unver)}) — could not be checked "
              f"(timeout / reset / server error); NOT evidence of rot:")
        for u, s, v, d in sorted(unver):
            print(f"  [{s}] {u}\n      {d}")

    print(f"\nlinks: {len(ok)} ok, {len(redir)} redirecting, {len(dead)} dead, "
          f"{len(blocked)} blocked, {len(unver)} unverified (of {len(results)}).",
          file=sys.stderr)

    # DEAD is 404/410 — the resource is gone. REDIRECT is reported but not fatal:
    # the slug-changed redirects in this corpus are cosmetic (a site moved a path
    # and kept serving the page), and failing on them would make the job noisy
    # enough to ignore. The fabrication signature is a redirect, so it still
    # appears prominently in the report for a human to read.
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
