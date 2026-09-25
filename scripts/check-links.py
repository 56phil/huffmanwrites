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


# An AWS WAF JavaScript challenge, served in place of the page.
#
# Measured on 2026-09-25 against espn.com: with a browser User-Agent every URL —
# a live story and an invented one alike — returned `202`, `Content-Length: 1987`,
# header `x-amzn-waf-action: challenge`, and this body. The checker read that as
# a clean 200-family OK, so three DEAD ESPN links survived a full-corpus sweep
# AND a per-file sweep on the one job that publishes unreviewed.
#
# Two markers, because either alone could drift: the AWS WAF globals in the body,
# and the noscript notice. Matched on the first 4 KB only, which is the read
# budget `probe` pays — the marker sits early in the document.
_WAF_CHALLENGE = re.compile(
    rb"AwsWafIntegration|awsWafCookieDomainList|token\.awswaf\.com"
    rb"|verify that you're not a robot",
    re.I,
)


def is_waf_challenge(body: bytes) -> bool:
    """True when the body is a bot challenge, not the page that was requested."""
    return bool(body) and bool(_WAF_CHALLENGE.search(body[:4096]))


def collect(only: "str | None" = None) -> "dict[str, list[str]]":
    """Map URL -> [files citing it].

    `only` restricts the scan to one file (repo-relative or absolute). That is
    what makes this usable as a pre-publish gate on a single new article: a
    brand-new file is in nobody's corpus yet, so the whole-tree mode cannot see
    it, and the coverage floor would reject a one-file scan as implausibly
    small. See `--file` and `main`.
    """
    out: "dict[str, list[str]]" = {}
    if only:
        p = (REPO / only) if not Path(only).is_absolute() else Path(only)
        if not p.is_file():
            die(f"file not found: {only}")
        paths = [p]
    else:
        paths = sorted(CONTENT.rglob("*.md"))
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            rel = str(path.relative_to(REPO))
        except ValueError:
            # A --file target outside the repo (a temp file, another checkout).
            # The label is cosmetic; the URL set is not.
            rel = str(path)
        for raw in URL.findall(text):
            u = clean(raw)
            if is_own(u):
                continue
            out.setdefault(u, [])
            if rel not in out[u]:
                out[u].append(rel)
    return out


_MD_LINK = re.compile(r"\[([^\]\n]{12,200})\]\(\s*(https?://[^\s\)]+)\s*\)")


def link_texts(only: "str | None" = None) -> "dict[str, str]":
    """Map URL -> the markdown link text that cites it, for headline-like text.

    Only markdown links are read, and only when the anchor text is long enough to
    be a headline. That is the shape a citation takes in this corpus: the link
    text IS the title of the thing being cited. A bare URL, or a link whose text
    is a short label ("here", "the report"), carries nothing to compare, so it is
    skipped rather than guessed at.
    """
    out: "dict[str, str]" = {}
    if only:
        p = (REPO / only) if not Path(only).is_absolute() else Path(only)
        paths = [p] if p.is_file() else []
    else:
        paths = sorted(CONTENT.rglob("*.md"))
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in _MD_LINK.finditer(text):
            anchor, url = m.group(1).strip(), clean(m.group(2))
            if is_own(url):
                continue
            # Prefer the longest anchor seen for a URL: a citation line often
            # repeats the link as both a short label and the full headline.
            if len(anchor) > len(out.get(url, "")):
                out[url] = anchor
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


def page_title(html_text: str) -> str:
    """The <title> of a fetched page, normalized; '' when there is none."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.S | re.I)
    if not m:
        return ""
    import html as _html

    return re.sub(r"\s+", " ", _html.unescape(m.group(1))).strip()


def _words(text: str) -> "list[str]":
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w]


def link_text_matches_title(text: str, title: str, floor: float = 0.34) -> "bool | None":
    """Does a citation's link text share vocabulary with the page it points at?

    Returns None when the question does not apply (too little to compare), True
    on overlap, False on a mismatch.

    This exists because a status code cannot answer the repo's most dangerous
    question. Measured 2026-09-25: ESPN serves **HTTP 200 for an invented story
    id and lands on an unrelated article** —
    `.../story/_/id/99999999999/not-a-real-story` returns 200 with the title
    "Ranking the top 25 WNBA players in the playoffs". Every ordinary check,
    including this file's own status probe, calls that a live link. Only
    comparing the page that came back against the source you meant to cite
    catches it, and that is what this does.

    **Overlap, not sequence.** The first version of this compared a run of four
    *consecutive* words, which is wrong for the job: a publisher's title and a
    citation paraphrase each other and reorder freely. "Colts at Chiefs, box
    score and team statistics" and the page's own "Chiefs 33-30 Colts (Sep 20,
    2026) Box Score - ESPN" share {chiefs, colts, box, score} but no four-word
    run, so a correct citation was flagged. Word *sets* handle the paraphrase,
    the publisher's decorations (" - ESPN"), and the reordering, and they still
    separate a wrong article cleanly: "Peter Thiel and mimetic desire" shares
    nothing with a WNBA playoff ranking.

    `floor` is the share of the citation's own meaningful words that must appear
    somewhere in the title. Two guards keep it from accusing correct work:

      * at least 3 meaningful (non-stopword) words in the link text — below that
        the text is a one- or two-word label ("odds", "game page") with too
        little vocabulary to judge, and the answer is None, not False;
      * short words are matched as-is, but the comparison folds case and strips
        punctuation, since "NFL.com" and "nfl" are the same token to a reader.

    Deliberately permissive, and reported rather than fatal: this prints two
    lines for a person to compare. A gate that fails a build on a correct
    citation is worse than one that shows a human the sentence.
    """
    tw, pw = _words(text), _words(title)
    meaningful = [w for w in tw if w not in _TITLE_STOP]
    if len(meaningful) < 3 or len(pw) < 3:
        return None
    pool = set(pw)
    shared = sum(1 for w in meaningful if w in pool)
    return (shared / len(meaningful)) >= floor


_TITLE_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "at", "by",
    "with", "from", "as", "is", "are", "was", "were", "be", "been", "it", "its",
    "this", "that", "these", "those", "his", "her", "their", "he", "she", "they",
}

# Below this many words, a link's text is a descriptive label ("game page") or a
# short section name, not a headline, and comparing it against the page title
# produces false mismatches. See link_text_matches_title for the measurement.
MIN_HEADLINE_WORDS = 6


def probe_once(url: str, timeout: float, headers: "dict[str, str]") -> "tuple[int, str, bytes, str]":
    """One request. Returns (status, final_url, body_head, error). Never raises."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = b""
            try:
                body = r.read(4096)
            except Exception:
                pass
            return r.status, r.geturl(), body, ""
    except urllib.error.HTTPError as e:
        return e.code, url, b"", f"HTTP {e.code}"
    except socket.timeout:
        return 0, url, b"", "timeout"
    except urllib.error.URLError as e:
        return 0, url, b"", f"unreachable: {str(e.reason)[:40]}"
    except Exception as e:  # noqa: BLE001
        return 0, url, b"", f"{type(e).__name__}: {str(e)[:40]}"


def probe(args: "tuple[str, float]") -> "tuple[str, int, str, str]":
    """Return (url, status, verdict, detail). Never raises."""
    url, timeout = args
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://huffmanwrites.org/",
    }
    code, final, body, err = probe_once(url, timeout, headers)

    # A bot-challenge wall answers a browser User-Agent with a 202 interstitial
    # for EVERY url, live or dead. Measured 2026-09-25 on espn.com: a working
    # story and a made-up one both returned 202 / 1987 bytes /
    # `x-amzn-waf-action: challenge`. Read as a 2xx, that hid three dead ESPN
    # links through a full-corpus sweep and a per-file sweep.
    #
    # The header is what triggers the wall: the SAME url fetched with no
    # User-Agent at all answers truthfully (404 for the bad one, 200 with a
    # ~130-480 KB body for the live ones), which is how scripts/chiefs-report.py
    # reads this host. So a challenge is retried bare before giving up, and that
    # is what makes ESPN citable links actually checkable here.
    #
    # If the bare retry does not produce a decisive answer either — challenged
    # again, refused, or timed out — the verdict is UNVERIFIED, "we could not
    # look". That is deliberately not fatal, for the same reason BLOCKED is not:
    # a wall is not evidence of rot. But it is no longer reported as OK.
    if is_waf_challenge(body):
        code2, final2, body2, err2 = probe_once(url, timeout, {})
        if is_waf_challenge(body2) or code2 == 0:
            return url, code, "UNVERIFIED", (
                "bot challenge (AWS WAF) with and without a User-Agent; "
                "the page was not served")
        code, final, body, err = code2, final2, body2, err2

    if err.startswith("HTTP "):
        code = int(err.split()[1])
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
    if code == 0:
        # A reset, an SSL failure or a DNS blip is "we could not look", not
        # "it is not there". Reporting these as DEAD produced 18 false alarms in
        # one sweep and would have trained the reader to ignore the gate.
        return url, 0, "UNVERIFIED", err or "unreachable"
    if final.rstrip("/") != url.rstrip("/") and code in (200, 301, 302):
        base_final = re.sub(r"^https?://([^/]+)/?$", r"\1", final)
        base_url = re.sub(r"^https?://([^/]+)/?$", r"\1", url)
        if base_final != base_url:
            return url, code, "REDIRECT", f"-> {final}"
    return url, code, "OK", ""


def probe_with_title(args: "tuple[str, float]") -> "tuple[str, int, str, str, str]":
    """probe(), plus the fetched page's <title>. Same contract; never raises.

    Kept separate from `probe` so the existing verdict logic — and its tests —
    stay untouched. This one adds the one thing a status code cannot provide:
    the page that was actually served, which is what exposes a link that
    resolves to the wrong article.
    """
    url, timeout = args
    status, verdict, detail = None, None, None
    title = ""
    # probe() already knows how to get a decision out of a challenge wall; this
    # mirrors its bare-retry so the title comes from the page, not the interstitial.
    code, final, body, err = probe_once(url, timeout, {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://huffmanwrites.org/",
    })
    if is_waf_challenge(body):
        c2, f2, b2, e2 = probe_once(url, timeout, {})
        if not is_waf_challenge(b2) and c2 != 0:
            code, final, body, err = c2, f2, b2, e2
    if body and not is_waf_challenge(body):
        title = page_title(body.decode("utf-8", "replace"))
    url2, code2, verdict2, detail2 = probe((url, timeout))
    return url2, code2, verdict2, detail2, title


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify external URLs cited in content/.")
    ap.add_argument("--online", action="store_true",
                    help="actually fetch every URL (no network means no check)")
    ap.add_argument("--check", action="store_true",
                    help="offline CI gate: placeholders + blocklist only")
    ap.add_argument("--file", help="scan one file instead of the whole tree "
                                   "(for a pre-publish check on a new article)")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--titles", action="store_true",
                    help="also fetch each page's <title> and report a citation "
                         "whose link text does not appear in it (the check for a "
                         "link that resolves to the WRONG article)")
    args = ap.parse_args()

    if args.check:
        return deterministic_scan()

    table = collect(args.file)
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

    # The coverage floor guards a whole-corpus sweep against a broken glob. It
    # must NOT apply to --file, where a single new article legitimately cites a
    # dozen URLs — refusing that would make the one mode built for pre-publish
    # checking useless. A file scan is instead floored at ONE, which still
    # catches an extraction that finds nothing at all.
    if args.file:
        if len(table) < 1:
            _die_floor(f"found no external URL(s) in {args.file}; if that is "
                       f"wrong, the extractor is not seeing the file")
    elif len(table) < MIN_URLS:
        _die_floor(f"found only {len(table)} external URL(s) in content/; "
                   f"expected at least {MIN_URLS}. The sweep is not seeing the "
                   f"corpus, so a clean result would be meaningless.")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        if args.titles:
            titled = list(pool.map(probe_with_title, [(u, args.timeout) for u in table]))
            results = [(u, s, v, d) for u, s, v, d, _ in titled]
            titles = {u: t for u, _, _, _, t in titled}
        else:
            results = list(pool.map(probe, [(u, args.timeout) for u in table]))
            titles = {}

    dead = [r for r in results if r[2] == "DEAD"]
    redir = [r for r in results if r[2] == "REDIRECT"]
    blocked = [r for r in results if r[2] == "BLOCKED"]
    unver = [r for r in results if r[2] == "UNVERIFIED"]
    ok = [r for r in results if r[2] == "OK"]

    # Citations whose link text does not appear in the page they point at. The
    # fabrication class no status code can catch (see link_text_matches_title).
    # Reported always, fatal never: the comparison is heuristic, and a gate that
    # fails a build on a correct citation is worse than one that shows a human
    # the sentence.
    mismatches: "list[tuple[str, str, str]]" = []
    if args.titles:
        anchors = link_texts(args.file)
        for u, s, v, d in results:
            if v not in ("OK", "REDIRECT"):
                continue
            anchor, title = anchors.get(u), titles.get(u, "")
            if not anchor or not title:
                continue
            hit = link_text_matches_title(anchor, title)
            if hit is False:
                mismatches.append((u, anchor, title))

    if args.json:
        import json
        print(json.dumps([{"url": u, "status": s, "verdict": v, "detail": d,
                           "title": titles.get(u, ""), "files": table[u]}
                          for u, s, v, d in results], indent=2))
        return 1 if (dead or redir) else 0

    if mismatches:
        print(f"\nTITLE MISMATCH ({len(mismatches)}) — the link resolves, but the "
              f"page it serves is not the one the link text names. This is the "
              f"fabrication signature no status code can see; read each one:")
        for u, anchor, title in mismatches:
            print(f"  {u}")
            print(f"      link text : {anchor[:110]}")
            print(f"      page title: {title[:110]}")

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
