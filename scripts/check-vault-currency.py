#!/usr/bin/env python3
"""Every published post must have a counterpart in the vault at ~/SimpleBrain.

Why this exists. Every publishing runner mirrors the article it just published
into a separate vault repo (`~/SimpleBrain`): the post goes to
`raw/content/posts/<section>/`, is translated into `wiki/articles/<slug>.md`,
and the raw file is then moved to `archive/`. That mirror step runs AFTER the
runner's post-push delivery check (`scripts/verify-published.py`), so when the
delivery check fails the run exits 1 and the mirror never happens.

On 2026-10-09 that is exactly what occurred. The daily SITREP run committed and
pushed `content/posts/sitrep/sitrep-2026-10-09.md`, the deploy did not land, the
delivery check found the page 404 and exited 1, and the mirror step was skipped:
the edition was published and never reached the vault. Nothing in either repo
could see it — the site build was green from the publishing side, the vault's own
`wiki-check` only audits pages that exist, and no job watches for a post that
should have a vault counterpart and does not. It was found by hand on 2026-10-10
and repaired. This gate is that watch.

The rule, and its scope. Every file under `content/posts/` that is meant to be
discoverable and durable — not a section `_index.md`, not a `draft: true`, and,
when `--since` is given, dated on or after that floor — must have a counterpart
somewhere under the vault whose file **stem** equals the post's stem. Stem, not
path: the vault does not mirror Hugo's tree (`raw/content/posts/<section>/<slug>.md`
becomes `archive/<slug>.md` and `wiki/articles/<slug>.md`), so a path comparison
would report every published post as missing. Any subfolder and any extension
counts, because the vault holds a `.md` translation, the raw `.md`, and
occasionally an image of the same stem.

The scope is `content/posts/` and nothing else, because the mirroring rule is the
publishing path: the site's publishing runners are what mirror an article into
the vault, and they write under `content/posts/`. The rest of `content/` is the
site's own furniture — `about.md`, `credo.md`, `mission.md`, `now.md`,
`search.md`, the `content/gallery/page/N.md` pagination stubs — which no runner
mirrors and which has no counterpart to be behind. Restricting the walk also
disposes of a stem collision: every Hugo book page is `books/<slug>/index.md`
(stem `index`), and the vault's own `wiki/index.md` shares that stem, so a
whole-`content/` walk would have silently "covered" every book by accident.

An embargoed post is not yet due. This repo publishes embargoed pieces: the
Stoic Saturday digest is committed the day before with `draft: false` and a
`date:` of 06:00 the next morning, and it sits in exactly that state overnight.
It is published to no one yet, so it has no counterpart to be behind, and the
gate must not name it as a miss. A post whose `date:` is after the present moment
is therefore excluded; `--now` pins the clock so a test asserts the rule rather
than today's date.

This is a LOCAL-ONLY gate. It reads a repo that lives on this machine and
nowhere else, so on a machine without the vault (CI, a fresh clone) it exits 0
with a note rather than failing: a gate that cannot run is not a gate that found
something. It is offline, stdlib-only, and deterministic. `--content`, `--vault`
and `--now` are injectable so the tests can pin every input against `tempfile`
trees and a fixed clock.

Paths whose components begin with `.` (`.git`, `.serena`, …) are not searched:
a `.git/index` file would otherwise lend its stem to every Hugo book page,
whose own file is `index.md` (stem `index`), and mask a real miss. Hidden data is
not vault content.

Exit codes:
  0  every examined post has a vault counterpart (or there is nothing to check)
  1  at least one examined post has no counterpart
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
HOME_VAULT = Path.home() / "SimpleBrain"

DRAFT_RE = re.compile(r"^draft:\s*true\s*$", re.M)
# `date:` with an optional time (`2026-10-11T06:00:00-05:00`), so an embargoed
# post dated 06:00 tomorrow is compared at the moment it lifts, not at midnight.
DATE_RE = re.compile(
    r"^date:\s*['\"]?(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?",
    re.M,
)


def frontmatter(text: str) -> str:
    """The leading `---` block, or "" when the file has none."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else ""


def post_datetime(fm: str):
    """The file's `date:` as a naive `datetime.datetime`, or None if absent.

    Timezone offsets are dropped, not converted: the embargo boundary is the
    morning of a day, and a local-only gate compares against the local clock.
    """
    m = DATE_RE.search(fm)
    if not m:
        return None
    import datetime as _dt
    try:
        return _dt.datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)),
            int(m.group(4) or 0), int(m.group(5) or 0), int(m.group(6) or 0),
        )
    except ValueError:
        return None


def is_draft(fm: str) -> bool:
    return DRAFT_RE.search(fm) is not None


def examined(content: Path, since, now):
    """`content/posts` files this gate must find in the vault: (path, stem) pairs.

    The walk is restricted to `content/posts/`, the publishing path the runners
    mirror (see the module docstring). Skipped within it: `_index.md` (a section
    index, mirrored by the site build, not by a publishing runner), `draft: true`
    (never published, so never mirrored), a post dated after `now` (embargoed:
    committed `draft: false` with a `date:` still in the future, so it is
    published to no one yet and has no counterpart to be behind), and — when
    `since` is set — anything dated before the floor or with no parseable date at
    all (it cannot satisfy `>= since`).
    """
    if not content.is_dir():
        return None
    out = []
    for path in sorted((content / "posts").rglob("*.md")):
        if path.name == "_index.md":
            continue
        fm = frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
        if is_draft(fm):
            continue
        dt = post_datetime(fm)
        if dt is not None and dt > now:
            continue  # embargoed: not published yet
        if since is not None:
            if dt is None or dt.date() < since:
                continue
        out.append((path, path.stem))
    return out


def vault_stems(vault: Path) -> "set[str]":
    """Stems of every visible file under the vault, at any depth."""
    stems = set()
    for p in vault.rglob("*"):
        if not p.is_file():
            continue
        if any(part.startswith(".") for part in p.relative_to(vault).parts):
            continue
        stems.add(p.stem)
    return stems


def rel_of(path: Path) -> str:
    """Repo-relative for display; a path outside the repo is shown as given."""
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--content", default=str(CONTENT),
                    help="site content root; only its posts/ subtree is examined "
                         "(default: <repo>/content)")
    ap.add_argument("--vault", default=str(HOME_VAULT),
                    help="vault to search for counterparts (default: ~/SimpleBrain)")
    ap.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                    help="examine only posts dated on or after this day")
    ap.add_argument("--now", default=None, metavar="ISO",
                    help="ISO datetime to treat as the wall clock, so a test can "
                         "pin it instead of inheriting it (embargoed posts are those "
                         "dated after it)")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    import datetime as _dt
    since = None
    if args.since:
        since = _dt.date.fromisoformat(args.since)
    if args.now:
        try:
            now = _dt.datetime.fromisoformat(args.now)
        except ValueError:
            raise SystemExit(
                f"vault-currency: --now wants an ISO datetime, got {args.now!r}")
        now = now.replace(tzinfo=None)  # compare naively, against the local clock
    else:
        now = _dt.datetime.now()

    content = Path(args.content)
    vault = Path(args.vault)

    posts = examined(content, since, now)
    if posts is None:
        print(f"vault-currency: skipped — content directory {content} does not "
              f"exist (nothing to check)")
        print("coverage: 0 posts")
        return 0

    if not vault.is_dir():
        # Local-only gate. CI and any machine without the vault have no mirror
        # to be behind, so this is not a finding there.
        if not args.quiet:
            print(f"vault-currency: skipped — vault {vault} does not exist "
                  f"(local-only gate; nothing to compare against)")
        print(f"coverage: {len(posts)} posts")
        return 0

    stems = vault_stems(vault)
    misses = [(p, stem) for p, stem in posts if stem not in stems]

    if misses:
        print(f"vault-currency: {len(misses)} published post(s) have no counterpart "
              f"under {vault}:")
        for path, stem in misses:
            print(f"  {rel_of(path)}: no file in the vault has stem '{stem}'")
        print(f"coverage: {len(posts)} posts")
        return 1

    if not args.quiet:
        print(f"vault-currency: OK — every examined post has a vault counterpart "
              f"({len(posts)} post(s))")
    print(f"coverage: {len(posts)} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
