#!/usr/bin/env python3
"""
Fill age-group folders with PMC child development articles.
Pipeline: esearch -> efetch JATS XML -> jats_to_markdown -> save .md
Includes retry+backoff for 429 rate limits and resume capability.
"""

import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import time, os, sys, re, json

BASE = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research"

EXISTING_PMC_132_144 = {
    "11120223", "11764674", "11786252", "5369070",
    "6480184", "7662773", "7826314", "7862045"
}

# ── Rate-limited HTTP helper ──────────────────────────────────────
def http_get(url, timeout=30, max_retries=4):
    """GET with retry+backoff on 429."""
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes Research (academic)"})
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 5
                print(f"    429 rate limit, waiting {wait}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise
    raise Exception(f"Failed after {max_retries} retries")


# ── JATS to Markdown converter ────────────────────────────────────
def jats_to_markdown(xml_text, pmcid):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        for marker in ["<?xml", "<article"]:
            idx = xml_text.find(marker)
            if idx >= 0:
                root = ET.fromstring(xml_text[idx:])
                break
        else:
            return f"# PMC{pmcid}\n\nError: Could not parse XML\n"

    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    lines = []

    title_el = root.find(".//article-title")
    if title_el is not None and title_el.text:
        title = " ".join(title_el.itertext()).strip()
        lines.append(f"# {title}\n")

    authors = []
    for c in root.findall(".//contrib[@contrib-type='author']"):
        surname = c.find("name/surname")
        given = c.find("name/given-names")
        if surname is not None and surname.text:
            name = surname.text.strip()
            if given is not None and given.text:
                name = f"{given.text.strip()} {name}"
            authors.append(name)
    if authors:
        lines.append(f"**Authors:** {', '.join(authors[:10])}\n")

    journal = root.find(".//journal-title")
    year_el = root.find(".//pub-date/year")
    doi_el = root.find(".//article-id[@pub-id-type='doi']")
    pmid_el = root.find(".//article-id[@pub-id-type='pmid']")

    meta = []
    if journal is not None and journal.text:
        meta.append(f"*{journal.text.strip()}*")
    if year_el is not None and year_el.text:
        meta.append(year_el.text.strip())
    meta.append(f"PMCID: PMC{pmcid}")
    if pmid_el is not None and pmid_el.text:
        meta.append(f"PMID: {pmid_el.text.strip()}")
    if doi_el is not None and doi_el.text:
        meta.append(f"DOI: {doi_el.text.strip()}")
    lines.append(" | ".join(meta) + "\n")
    lines.append("---\n")

    abstract = root.find(".//abstract")
    if abstract is not None:
        lines.append("## Abstract\n")
        for p in abstract.findall(".//p"):
            text = " ".join(p.itertext()).strip()
            if text:
                lines.append(f"{text}\n")
        lines.append("---\n")

    body = root.find(".//body")
    if body is not None:
        stack = [(body, 2)]
        while stack:
            elem, level = stack.pop(0)
            if elem.tag == "sec":
                title_el = elem.find("title")
                if title_el is not None:
                    title_text = " ".join(title_el.itertext()).strip()
                    if title_text:
                        h = min(level + 1, 5)
                        lines.append(f"\n{'#' * h} {title_text}\n")
                for child in elem:
                    if child.tag == "sec":
                        stack.insert(0, (child, level + 1))
                    elif child.tag == "p":
                        text = " ".join(child.itertext()).strip()
                        if text and len(text) > 20:
                            lines.append(f"{text}\n")
                    elif child.tag in ("list",):
                        for item in child.findall("list-item"):
                            text = " ".join(item.itertext()).strip()
                            if text:
                                lines.append(f"- {text}\n")
            elif elem.tag == "p":
                text = " ".join(elem.itertext()).strip()
                if text and len(text) > 20:
                    lines.append(f"{text}\n")
            else:
                for child in elem:
                    stack.insert(0, (child, level))

    refs = root.findall(".//ref")
    if refs:
        lines.append("\n---\n## References\n")
        for i, ref in enumerate(refs[:50], 1):
            citation = ref.find("element-citation") or ref.find("mixed-citation")
            if citation is None:
                continue
            parts = []
            for pn in citation.findall("person-group[@person-group-type='author']/name"):
                s = pn.find("surname")
                g = pn.find("given-names")
                if s is not None and s.text:
                    name = s.text.strip()
                    if g is not None and g.text:
                        name = f"{g.text.strip()} {name}"
                    parts.append(name)
            art_title = citation.find("article-title")
            if art_title is not None and art_title.text:
                parts.append(f'"{art_title.text.strip()}"')
            source = citation.find("source")
            if source is not None and source.text:
                parts.append(source.text.strip())
            y = citation.find("year")
            if y is not None and y.text:
                parts.append(y.text.strip())
            d = citation.find("pub-id[@pub-id-type='doi']")
            if d is not None and d.text:
                parts.append(f"doi:{d.text.strip()}")
            if parts:
                lines.append(f"{i}. {'. '.join(parts)}\n")

    return "".join(lines)


# ── Entrez API helpers ────────────────────────────────────────────
def esearch(query, db="pmc", retmax=20):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": db, "retmax": str(retmax), "sort": "relevance",
        "term": query + " AND open+access[filter]",
        "retmode": "xml"
    }
    url = base + "?" + urllib.parse.urlencode(params)
    data = http_get(url, timeout=30)
    root = ET.fromstring(data)
    ids = [e.text for e in root.findall(".//Id")]
    return ids


def esummary(pmcids):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pmc",
        "id": ",".join(pmcids),
        "retmode": "xml"
    }
    url = base + "?" + urllib.parse.urlencode(params)
    data = http_get(url, timeout=30)
    root = ET.fromstring(data)
    summaries = {}
    for ds in root.findall(".//DocSum"):
        pid = ds.find("Id").text
        title_el = ds.find(".//Item[@Name='Title']")
        pubdate_el = ds.find(".//Item[@Name='PubDate']")
        source_el = ds.find(".//Item[@Name='Source']")
        title = title_el.text if title_el is not None else ""
        summaries[pid] = {
            "title": title[:120] if title else "Untitled",
            "pubdate": pubdate_el.text if pubdate_el is not None else "",
            "source": source_el.text if source_el is not None else ""
        }
    return summaries


def efetch(pmcid):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc",
        "id": f"PMC{pmcid}",
        "retmode": "xml",
        "rettype": "full"
    }
    url = base + "?" + urllib.parse.urlencode(params)
    return http_get(url, timeout=60).decode("utf-8", errors="replace")


def slugify(title):
    slug = re.sub(r'[^a-zA-Z0-9_ -]', '', title)[:80]
    slug = re.sub(r'\s+', '_', slug.strip())
    return slug or "article"


# ── Main pipeline ─────────────────────────────────────────────────
def fill_folder(folder, query, needed, existing_ids=None):
    folder_path = os.path.join(BASE, folder)
    os.makedirs(folder_path, exist_ok=True)

    if existing_ids is None:
        existing_ids = set()

    print(f"\n{'='*60}")
    print(f"FOLDER: {folder} — need {needed} articles")
    print(f"QUERY: {query}")
    print(f"{'='*60}")

    # Count already-downloaded PMC files (for resume)
    already = {f.replace("PMC", "").replace(".md", "")
               for f in os.listdir(folder_path)
               if f.startswith("PMC") and f.endswith(".md")}
    print(f"  Already have {len(already)} PMC files: {sorted(already)}")

    # Search
    all_ids = esearch(query, retmax=min(needed * 3, 30))
    candidate_ids = [pid for pid in all_ids
                     if pid not in existing_ids and pid not in already]
    print(f"  Found {len(all_ids)} results, {len(candidate_ids)} new (after dedup + resume)")

    downloaded = len(already)

    for pmcid in candidate_ids:
        if downloaded >= needed:
            break

        filename = f"PMC{pmcid}.md"
        filepath = os.path.join(folder_path, filename)

        print(f"  [{downloaded+1}/{needed}] Fetching PMC{pmcid}...")
        try:
            xml_text = efetch(pmcid)
            time.sleep(1.5)
        except Exception as e:
            print(f"    ERROR fetching: {e}")
            time.sleep(2)
            continue

        try:
            md_text = jats_to_markdown(xml_text, pmcid)
        except Exception as e:
            print(f"    ERROR converting: {e}")
            time.sleep(1)
            continue

        if len(md_text) < 200:
            print(f"    WARN: Short output ({len(md_text)} chars), skipping")
            time.sleep(1)
            continue

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
            downloaded += 1
            print(f"    SAVED: {filename} ({len(md_text)} chars)")
        except Exception as e:
            print(f"    ERROR saving: {e}")

        time.sleep(1.5)

    print(f"  DONE: {downloaded}/{needed} total articles in {folder}")
    return downloaded


# ── RUN ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tasks = [
        ("0-12", "infant development parenting attachment maternal sensitivity sleep regulation", 10, None),
        ("13-24", "toddler social emotional development parenting attachment self regulation", 10, None),
        ("25-36", "toddler self regulation executive function parenting language development autonomy", 10, None),
        ("13-36-months", "toddler prosocial behavior autonomy parenting social competence empathy", 10, None),
        ("132-144", "early adolescent development parenting autonomy character prosocial identity self regulation", 10, EXISTING_PMC_132_144),
    ]

    total = 0
    for folder, query, needed, existing in tasks:
        n = fill_folder(folder, query, needed, existing)
        total += n
        # Wait between folders to avoid rate limit
        if tasks.index((folder, query, needed, existing)) < len(tasks) - 1:
            print("  Waiting 5s before next folder...")
            time.sleep(5)

    print(f"\n{'='*60}")
    print(f"TOTAL: {total} articles across 5 folders")
    print(f"{'='*60}")
