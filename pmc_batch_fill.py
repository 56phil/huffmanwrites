#!/usr/bin/env python3
"""
Batch fill 4 age-group folders with 10 PMC articles each.
Uses Entrez E-utilities to search, fetch, and convert JATS XML to markdown.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import os

BASE_DIR = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research"

# ─── JATS to Markdown converter ───────────────────────────────────────────

def jats_to_markdown(xml_text, pmcid):
    """Convert JATS XML to readable markdown."""
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

    # Title
    title_el = root.find(".//article-title")
    if title_el is not None and title_el.text:
        title = " ".join(title_el.itertext()).strip()
        lines.append(f"# {title}\n")

    # Authors
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

    # Journal metadata
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

    # Abstract
    abstract = root.find(".//abstract")
    if abstract is not None:
        lines.append("## Abstract\n")
        for p in abstract.findall(".//p"):
            text = " ".join(p.itertext()).strip()
            if text:
                lines.append(f"{text}\n")
        lines.append("---\n")

    # Body
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

    # References
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


# ─── Entrez API helpers ───────────────────────────────────────────────────

HEADERS = {"User-Agent": "Hermes Research (academic; mailto:research@example.com)"}

def pubmed_search(query, retmax=20):
    """Search PMC for open-access articles."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pmc",
        "retmax": str(retmax),
        "sort": "relevance",
        "term": query + " AND open+access[filter]",
        "retmode": "xml",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.parse(resp).getroot()
    ids = [e.text for e in root.findall(".//Id")]
    count_el = root.find(".//Count")
    count = int(count_el.text) if count_el is not None and count_el.text else 0
    return ids, count


def fetch_summaries(pmcids):
    """Fetch article summaries (title, authors, year) for filename generation."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pmc",
        "id": ",".join(pmcids),
        "retmode": "xml",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.parse(resp).getroot()

    summaries = {}
    for ds in root.findall("DocSum"):
        pmcid = ds.find("Id").text
        info = {}
        for item in ds.findall("Item"):
            name = item.get("Name", "")
            if name == "Title":
                info["title"] = item.text or ""
            elif name == "PubDate":
                info["year"] = (item.text or "")[:4]
            elif name == "DOI":
                info["doi"] = item.text or ""
            elif name == "AuthorList":
                authors = []
                for au in item.findall("Item"):
                    if au.text:
                        authors.append(au.text.strip())
                info["authors"] = authors[:3]
        summaries[pmcid] = info
    return summaries


def fetch_jats(pmcid):
    """Fetch full-text JATS XML."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc",
        "id": f"PMC{pmcid}",
        "retmode": "xml",
        "rettype": "full",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def sanitize_filename(title, pmcid, year):
    """Create a safe, descriptive filename."""
    # Take first 60 chars, clean it up
    short = title[:60].strip()
    # Remove punctuation except hyphens and underscores
    import re
    short = re.sub(r'[^\w\s-]', '', short)
    short = re.sub(r'\s+', '_', short.strip())
    if not short:
        short = f"article_{pmcid}"
    if year:
        return f"PMC{pmcid}_{short}_{year}.md"
    return f"PMC{pmcid}_{short}.md"


# ─── Query definitions for each age range ─────────────────────────────────

AGE_QUERIES = {
    "85-96": [
        # ~7-8 years: early elementary, self-regulation and executive function
        '("elementary school" OR "middle childhood") AND (self-regulation OR executive function) AND (children OR child)',
        '("school-age children" OR "7 year" OR "8 year") AND (academic motivation OR school engagement)',
        '("elementary school" OR "middle childhood") AND (peer relationships OR friendship) AND children',
        '("elementary school" OR "school age") AND (moral development OR prosocial behavior) AND children',
        '("elementary school" OR "middle childhood") AND (screen time OR digital media OR media use) AND children',
    ],
    "97-108": [
        # ~8-9 years: upper elementary, identity and autonomy
        '("middle childhood" OR "school age") AND (identity formation OR self-concept) AND children',
        '("middle childhood" OR "elementary") AND (autonomy OR independence) AND (parenting OR parental)',
        '("school age children" OR "8 year" OR "9 year") AND (sleep OR sleep patterns) AND cognition',
        '("middle childhood" OR "elementary") AND (character development OR virtue OR values) AND children',
        '("middle childhood" OR "school age") AND (extracurricular OR after-school activities) AND (outcomes OR development)',
    ],
    "109-120": [
        # ~9-10 years: late elementary/pre-adolescent, peer influence and screen time
        '("late childhood" OR preadolescent OR "pre-adolescent") AND (peer influence OR peer pressure)',
        '("late childhood" OR preadolescent) AND (screen time OR smartphone OR social media) AND (well-being OR mental health)',
        '("late childhood" OR preadolescent) AND (self-regulation OR emotional regulation)',
        '("late childhood" OR preadolescent) AND (identity development OR self-esteem)',
        '("late childhood" OR preadolescent) AND (parenting OR parent-child relationship) AND (adjustment OR well-being)',
    ],
    "121 months and up": [
        # ~10+ years: middle school and beyond, adolescent development
        '("adolescent" OR "early adolescence" OR "middle school") AND (identity formation OR self-identity)',
        '("adolescent" OR "early adolescence") AND (peer influence OR peer relationships) AND (development OR adjustment)',
        '("adolescent" OR "middle school") AND (screen time OR digital media OR social media) AND (mental health OR well-being)',
        '("adolescent" OR "early adolescence") AND (autonomy OR independence) AND (parenting OR family)',
        '("adolescent" OR "middle school") AND (academic motivation OR school engagement)',
    ],
}


def collect_unique_ids(age_folder, queries, target_count=10):
    """Run multiple searches to collect enough unique article IDs."""
    all_ids = set()
    for query in queries:
        if len(all_ids) >= target_count + 5:
            break
        try:
            ids, count = pubmed_search(query, retmax=8)
            print(f"  Query: {query[:80]}... -> {len(ids)} results (total: {count})")
            for pid in ids:
                all_ids.add(pid)
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(1)
    # Get up to target_count + some buffer
    result = list(all_ids)[:target_count + 5]
    print(f"  Collected {len(result)} unique IDs for {age_folder}")
    return result


def download_folder(age_folder, target_count=10):
    """Download and save articles for one age folder."""
    folder_path = os.path.join(BASE_DIR, age_folder)
    os.makedirs(folder_path, exist_ok=True)

    # Check existing files
    existing = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    existing_ids = set()
    for f in existing:
        # Extract PMC ID from filename
        import re
        m = re.match(r'PMC(\d+)', f)
        if m:
            existing_ids.add(m.group(1))

    print(f"\n{'='*60}")
    print(f"FOLDER: {age_folder} ({len(existing)} existing .md files)")
    print(f"{'='*60}")

    needed = target_count - len(existing)
    if needed <= 0:
        print(f"  Already has {len(existing)} articles. Skipping.")
        return

    queries = AGE_QUERIES.get(age_folder, [])
    pmcids = collect_unique_ids(age_folder, queries, needed)

    # Filter out already-downloaded
    pmcids = [p for p in pmcids if p not in existing_ids]
    if len(pmcids) > needed:
        pmcids = pmcids[:needed]

    print(f"  Need to download: {len(pmcids)} articles")

    if not pmcids:
        print("  Nothing to download.")
        return

    # Fetch summaries for filenames
    print("  Fetching summaries...")
    time.sleep(0.5)
    summaries = {}
    try:
        summaries = fetch_summaries(pmcids)
    except Exception as e:
        print(f"  Summary fetch error: {e}")

    # Download each article
    for i, pmcid in enumerate(pmcids):
        print(f"  [{i+1}/{len(pmcids)}] Downloading PMC{pmcid}...")
        try:
            xml_text = fetch_jats(pmcid)
            md_text = jats_to_markdown(xml_text, pmcid)

            # Create filename
            info = summaries.get(pmcid, {})
            title = info.get("title", "")
            year = info.get("year", "")
            filename = sanitize_filename(title, pmcid, year)
            filepath = os.path.join(folder_path, filename)

            # Use Python file ops to handle apostrophes
            with open(filepath, 'w') as f:
                f.write(md_text)

            print(f"    Saved: {filename} ({len(md_text)} chars)")
            time.sleep(0.5)

        except Exception as e:
            print(f"    ERROR downloading PMC{pmcid}: {e}")
            time.sleep(1)

    # Final count
    final = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    print(f"  FINAL: {len(final)} articles in {age_folder}")


if __name__ == "__main__":
    folders = ["85-96", "97-108", "109-120", "121 months and up"]
    for folder in folders:
        try:
            download_folder(folder, target_count=10)
        except Exception as e:
            print(f"FATAL error for {folder}: {e}")

    # Report
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    for folder in folders:
        folder_path = os.path.join(BASE_DIR, folder)
        files = sorted([f for f in os.listdir(folder_path) if f.endswith('.md')])
        print(f"\n{folder}: {len(files)} articles")
        for f in files:
            print(f"  {f}")
