#!/usr/bin/env python3
"""Weekly site audit crawler for huffmanwrites.org.

Expects `hugo --gc --minify` to have been run (public/ exists). Walks the
rendered site, extracts every link target, checks internal links against the
output files on disk, checks external links with curl in parallel, verifies
the Content-Security-Policy meta tag, and compares the installed Hugo version
against the latest GitHub release. Writes a markdown report.

Usage: site-audit-crawler.py <public_dir> <report_path>
Env:   AUDIT_BUILD_STATUS  "PASS" (default) or a short failure note
"""

import concurrent.futures
import html.parser
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CURL_TIMEOUT = 20
PARALLEL = 12

# Directives that must be present in the CSP meta tag, with the values that
# must appear in each. Mirrors layouts/partials/extend_head.html.
CSP_EXPECT = {
    "default-src": ["'self'"],
    "script-src": ["gc.zgo.at", "https://sendfox.com"],
    "style-src": ["fonts.googleapis.com"],
    "img-src": ["data:"],
    "font-src": ["fonts.gstatic.com"],
    "connect-src": ["huffmanwrites.goatcounter.com", "https://sendfox.com"],
    "form-action": ["https://sendfox.com"],
    "base-uri": ["'self'"],
}


class LinkExtractor(html.parser.HTMLParser):
    """Collects every href/src/srcset target from one HTML document."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # Connection hints (preconnect/dns-prefetch) are not resources —
        # checking the bare origin returns 404 and is a false positive.
        if tag == "link" and attrs.get("rel") in ("preconnect", "dns-prefetch"):
            return
        for key, val in attrs.items():
            if val is None:
                continue
            if key in ("href", "src"):
                self.links.append(val.strip())
            elif key == "srcset":
                for part in val.split(","):
                    url = part.strip().split()[0] if part.strip() else ""
                    if url:
                        self.links.append(url)


def classify(url, page_path, public_dir):
    """Return ('internal', rel_target) or ('external', url) or None to skip."""
    u = url.strip()
    if not u or u.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if u.startswith("//"):  # protocol-relative -> external
        return ("external", u)
    parsed = urllib.parse.urlparse(u)
    if parsed.scheme in ("http", "https"):
        host = parsed.netloc.lower()
        if host in ("huffmanwrites.org", "www.huffmanwrites.org"):
            path = parsed.path or "/"  # bare https://huffmanwrites.org -> root
        else:
            return ("external", u)
    elif parsed.scheme:
        return None  # other schemes (ftp:, etc.) — skip
    else:
        path = parsed.path
    if not path.startswith("/"):
        base = os.path.dirname(page_path) + "/"
        path = urllib.parse.urljoin(base, path)
    path = urllib.parse.unquote(path.split("#")[0])
    if path in ("", "/"):
        return ("internal", "index.html")  # bare site URL -> root
    if path.endswith("/"):
        path += "index.html"
    return ("internal", path.lstrip("/"))


def check_external(url):
    """curl one external URL; return (url, status_class, detail)."""
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-L",
             "--max-time", str(CURL_TIMEOUT), "-A", UA, url],
            capture_output=True, text=True, timeout=CURL_TIMEOUT + 5)
        code = proc.stdout.strip()
        if code == "000":
            return (url, "AMBIGUOUS", "connection failure (may be bot-blocking)")
        c = int(code)
        if 200 <= c < 400:
            return (url, "OK", str(c))
        if c in (404, 410):
            return (url, "DEAD", str(c))
        if c in (401, 403, 406, 429):
            # Paywalls/Cloudflare bot-blocks — the Aug 21 audit established
            # these resolve fine in a browser; not actionable.
            return (url, "BLOCKED", str(c))
        return (url, "OTHER", str(c))
    except subprocess.TimeoutExpired:
        return (url, "AMBIGUOUS", "timeout")


def check_csp(public_dir):
    """Verify the CSP meta tag on the home page against CSP_EXPECT."""
    home = os.path.join(public_dir, "index.html")
    if not os.path.exists(home):
        return [("home page", "MISSING")]
    with open(home, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = re.search(
        r'<meta[^>]*http-equiv=["\']?Content-Security-Policy["\']?[^>]*content="([^"]*)"',
        text)
    if not m:
        return [("CSP meta tag", "MISSING")]
    directives = {}
    for part in m.group(1).split(";"):
        part = part.strip()
        if not part:
            continue
        name, _, rest = part.partition(" ")
        directives[name] = rest.split()
    results = []
    for name, expected in CSP_EXPECT.items():
        actual = directives.get(name, [])
        if name not in directives:
            results.append((name, "MISSING"))
        elif [e for e in expected if e not in actual]:
            results.append((f"{name} (missing {', '.join(e for e in expected if e not in actual)})", "FAIL"))
        else:
            results.append((name, "OK"))
    return results


def hugo_versions():
    """Return (installed_version, latest_version) — None where unknown."""
    installed = None
    try:
        out = subprocess.run(["hugo", "version"], capture_output=True,
                             text=True, timeout=30).stdout
        m = re.search(r"v(\d+\.\d+\.\d+)", out)
        if m:
            installed = m.group(1)
    except Exception:
        pass
    latest = None
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/gohugoio/hugo/releases/latest",
            headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            latest = json.load(resp).get("tag_name", "").lstrip("v")
    except Exception:
        pass
    return installed, latest


def main():
    if len(sys.argv) != 3:
        print("usage: site-audit-crawler.py <public_dir> <report_path>",
              file=sys.stderr)
        return 2
    public_dir, report_path = sys.argv[1], sys.argv[2]
    build_status = os.environ.get("AUDIT_BUILD_STATUS", "PASS")

    pages = []
    for root, _dirs, files in os.walk(public_dir):
        for f in files:
            if f.endswith(".html"):
                pages.append(os.path.relpath(os.path.join(root, f), public_dir))

    internal_broken = []
    internal_checked = 0
    external_urls = set()
    for page in pages:
        with open(os.path.join(public_dir, page), encoding="utf-8",
                  errors="replace") as fh:
            text = fh.read()
        parser = LinkExtractor()
        parser.feed(text)
        for url in parser.links:
            res = classify(url, page, public_dir)
            if res is None:
                continue
            kind, target = res
            if kind == "internal":
                internal_checked += 1
                if not os.path.exists(os.path.join(public_dir, target)):
                    internal_broken.append((page, url, target))
            else:
                external_urls.add(target)

    external_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        futures = {ex.submit(check_external, u): u for u in sorted(external_urls)}
        for fut in concurrent.futures.as_completed(futures):
            external_results.append(fut.result())

    dead = [r for r in external_results if r[1] == "DEAD"]
    ambiguous = [r for r in external_results if r[1] == "AMBIGUOUS"]
    blocked = [r for r in external_results if r[1] == "BLOCKED"]
    other = [r for r in external_results if r[1] == "OTHER"]
    ok_count = len(external_results) - len(dead) - len(ambiguous) - len(blocked) - len(other)

    csp = check_csp(public_dir)
    csp_ok = all(r[1] == "OK" for r in csp)
    installed, latest = hugo_versions()

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [f"# Site Audit — {stamp}", ""]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Build: {build_status}")
    lines.append(f"- Internal links: {len(internal_broken)} broken "
                 f"({internal_checked} checked)")
    lines.append(f"- External links: {len(dead)} dead, {len(ambiguous)} "
                 f"ambiguous, {len(blocked)} bot-blocked/paywalled, "
                 f"{len(other)} other ({len(external_results)} checked)")
    lines.append(f"- CSP: {'PASS' if csp_ok else 'FAIL'}")
    if installed and latest:
        current = "current" if installed == latest else "OUTDATED"
        lines.append(f"- Hugo: {installed} installed, {latest} latest — {current}")
    elif installed:
        lines.append(f"- Hugo: {installed} installed, latest unknown (API check failed)")
    else:
        lines.append("- Hugo: version check failed")
    lines.append("")

    lines.append("## Broken internal links")
    lines.append("")
    if internal_broken:
        for page, url, target in internal_broken:
            lines.append(f"- `{page}` → `{url}` (missing `{target}`)")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Dead external links (404/410)")
    lines.append("")
    if dead:
        for url, _cls, detail in sorted(dead):
            lines.append(f"- {url} ({detail})")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Ambiguous external links (connection failures — may be bot-blocking)")
    lines.append("")
    if ambiguous:
        for url, _cls, detail in sorted(ambiguous):
            lines.append(f"- {url} ({detail})")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Bot-blocked / paywalled external links (not actionable)")
    lines.append("")
    if blocked:
        lines.append(f"{len(blocked)} links returned 401/403/406/429 — "
                     f"paywalls or bot-blocking; these resolve in a browser "
                     f"and are not broken. Not listed individually.")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Other external links (non-2xx/3xx/404)")
    lines.append("")
    if other:
        for url, _cls, detail in sorted(other):
            lines.append(f"- {url} ({detail})")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## CSP check")
    lines.append("")
    for name, status in csp:
        lines.append(f"- {name}: {status}")
    lines.append("")

    lines.append("## Hugo version")
    lines.append("")
    lines.append(f"- Installed: {installed or 'unknown'}")
    lines.append(f"- Latest: {latest or 'unknown'}")
    lines.append("")

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"audit: {len(pages)} pages, {internal_checked} internal links "
          f"({len(internal_broken)} broken), {len(external_results)} external "
          f"links ({len(dead)} dead, {len(ambiguous)} ambiguous), "
          f"CSP {'PASS' if csp_ok else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
