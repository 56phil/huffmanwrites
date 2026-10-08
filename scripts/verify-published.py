#!/usr/bin/env python3
"""Verify that a published article is actually served by the live site.

WHY THIS EXISTS. `publish_article` verifies that the PUSH landed — that
`origin/main` equals the local HEAD. That is not delivery. The Pages workflow
can fail after the push, and on 2026-10-08 it did: every commit after 11:51Z
reached `main` while no deploy landed, because one gate test executed a runner
that had a developer's home path baked into it. A report written, committed,
pushed and never served looks exactly like success in the log — the failure mode
the push check itself was written for, one step further along.

For the daily SITREP that state is caught by `scripts/sitrep-watchdog.py`, which
watches for it from the outside. For the weekly series nothing looked at all.
This is that check, run by the publishing tail in the run that published the
piece, so a report that is on `main` and not on the site is reported while the
job still has someone's attention.

Two rules are the watchdog's, for the same reasons:

  * A 200 is not evidence that the page is the one asked for, so the page's own
    `<title>` must carry the article's title. A host can serve 200 for an
    unrelated page — ESPN does exactly that for an invented story id.
  * A 404 immediately after a push is the expected state, not a finding: the
    deploy has not landed yet. The check therefore retries for a bounded window
    before it calls an absence settled.

URL and expected title are both read from the article itself — `content/posts/
<...>/<slug>.md` is served at `/posts/<...>/<slug>/`, and the frontmatter
`title` is what the page's `<title>` carries — so a series cannot pass by
checking a page that is not the piece it just published.

Exit codes match the watchdog's vocabulary, so an alert reads the same whichever
checker raised it:

    0  the site serves the article
    1  it does not, and the absence is settled (404 throughout)
    3  the site could not be read, or answered with a page that is not this
       article, so the deploy is unconfirmed
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parent.parent

# The canonical host: hugo.toml's baseURL and static/CNAME. Not www — the site
# answers there too, but a URL this repo writes names huffmanwrites.org.
BASE_URL = "https://huffmanwrites.org"

UA = "huffmanwrites-verify-published/1.0 (+https://huffmanwrites.org)"
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)

# 24 checks 15 seconds apart: a deploy is normally live about a minute after the
# push, and a queued build (the workflow cancels in progress under one Pages
# concurrency group) is the case the margin is for. The window is stated in the
# failure sentence so a slow-but-fine deploy is read as such rather than as a
# verdict.
TRIES = 24
DELAY = 15
TIMEOUT = 20


@dataclass
class Page:
    """What the fetch turned out to be.

    `status is None` means the request failed rather than answered — "we could
    not look" and "it is not there" need different sentences and different exit
    codes, the same distinction the docket watcher and the SITREP watchdog make.
    """

    status: int | None = None
    error: str = ""
    title: str | None = None
    body: str = ""

    def serves(self, expected: str) -> bool:
        """Does this page carry the article, by its own <title>?

        The title is compared, not the body, because the body is a build of
        everything on the page; when there is no title to read the body is the
        fallback rather than a verdict of OK.
        """
        if self.status != 200:
            return False
        haystack = self.title if self.title is not None else self.body
        return fold(expected) in fold(haystack)


def fold(text: str) -> str:
    """Unescape and collapse whitespace so a title can be compared as prose.

    Hugo escapes what it must in a `<title>` (`&` as `&amp;`) and hard-wraps
    nothing, but a title written across lines in frontmatter arrives here with
    the newline still in it, and a literal substring test would call that a miss.
    """
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def post_url(article: str, base: str = BASE_URL) -> str:
    """The URL Hugo serves `article` at.

    Derived rather than passed in: a URL typed alongside the article is a URL
    that can name a different piece, which is the whole class of defect this
    check exists to catch.
    """
    parts = PurePosixPath(article).parts
    for i in range(len(parts) - 1):
        if parts[i] == "content" and parts[i + 1] == "posts":
            rest = list(parts[i + 2:])
            if not rest:
                break
            rest[-1] = re.sub(r"\.md$", "", rest[-1])
            return f"{base.rstrip('/')}/posts/{'/'.join(rest)}/"
    raise SystemExit(
        f"verify-published: {article} is not under content/posts/, so its URL "
        "cannot be derived; refusing to guess which page to check"
    )


def frontmatter_title(text: str) -> str:
    """The article's own `title:` — the string the page's <title> must carry."""
    m = re.search(r"^title:[ \t]*(.+)$", text, re.M)
    if not m:
        raise SystemExit("verify-published: the article has no `title:` frontmatter")
    title = m.group(1).strip()
    if len(title) >= 2 and title[0] == title[-1] and title[0] in "\"'":
        title = title[1:-1]
    return title


def fetch(url: str, timeout: int = TIMEOUT) -> Page:
    """Fetch the page. A failure is a Page with an error and no status.

    The User-Agent is sent because GitHub Pages serves a bot-ish client
    normally, unlike the ESPN endpoints CLAUDE.md records, which answer a
    browser and refuse a default client.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            m = TITLE_RE.search(body)
            return Page(
                status=resp.status,
                title=(fold(m.group(1)) if m else None),
                body=body,
            )
    except urllib.error.HTTPError as exc:
        return Page(status=exc.code, error=f"HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001 - any transport failure is "unconfirmed"
        return Page(status=None, error=f"{exc.__class__.__name__}: {exc}")


def verify(
    article: str,
    expected: str,
    url: str,
    tries: int = TRIES,
    delay: int = DELAY,
    timeout: int = TIMEOUT,
    fetch_fn=fetch,
) -> tuple[int, str]:
    """Poll until the site serves the article, or the window closes.

    `fetch_fn` is a parameter rather than a module call so the decision can be
    tested against a stub — the cases that matter (a 404 for six minutes, a 200
    that is the wrong page, a site that cannot be read) are all impossible to
    stage against the real one.
    """
    window = tries * delay
    page = Page()
    for attempt in range(1, tries + 1):
        page = fetch_fn(url, timeout)
        if page.serves(expected):
            return 0, f'verify-published: {url} serves "{expected}" (check {attempt})'
        if attempt < tries:
            time.sleep(delay)

    if page.status == 404:
        return 1, (
            f"verify-published: {url} is 404 on all {tries} checks over {window}s; "
            f"{article} is on main but the deploy did not land"
        )
    if page.status is not None:
        return 3, (
            f"verify-published: {url} answered HTTP {page.status} with a page whose "
            f"own title is not \"{expected}\" on all {tries} checks over {window}s; "
            "the wrong page is at that address"
        )
    return 3, (
        f"verify-published: {url} could not be read on any of {tries} checks over "
        f"{window}s ({page.error or 'no response'}); the deploy is unconfirmed"
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify that a published article is served by the live site."
    )
    ap.add_argument("--article", required=True,
                    help="the article path, e.g. content/posts/essays/report-x.md")
    ap.add_argument("--base-url", default=BASE_URL,
                    help=f"site root to check (default {BASE_URL})")
    ap.add_argument("--tries", type=int, default=TRIES, help=f"checks (default {TRIES})")
    ap.add_argument("--delay", type=int, default=DELAY,
                    help=f"seconds between checks (default {DELAY})")
    ap.add_argument("--timeout", type=int, default=TIMEOUT,
                    help=f"seconds per request (default {TIMEOUT})")
    args = ap.parse_args()

    path = Path(args.article)
    text = path.read_text(encoding="utf-8") if path.is_file() else (
        (REPO / args.article).read_text(encoding="utf-8")
        if (REPO / args.article).is_file()
        else None
    )
    if text is None:
        raise SystemExit(f"verify-published: no such article: {args.article}")

    expected = frontmatter_title(text)
    url = post_url(args.article, args.base_url)
    code, sentence = verify(args.article, expected, url,
                            tries=args.tries, delay=args.delay, timeout=args.timeout)
    print(sentence)
    return code


if __name__ == "__main__":
    sys.exit(main())
