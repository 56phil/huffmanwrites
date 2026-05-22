#!/usr/bin/env python3
"""
Fetch FULL TEXT open-access articles from PMC and key institutional sources.
Uses PMC OA subset, EFetch with rettype=pmc for XML full text.
Also tries to fetch classic papers and institutional publications.
"""

import os, json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re

OUTPUT_DIR = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research/0-12-months/"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ncbi_request(endpoint, params):
    url = NCBI_BASE + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchBot/1.0 (academic)"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                # Try UTF-8 first, then latin-1
                try:
                    return data.decode("utf-8")
                except UnicodeDecodeError:
                    return data.decode("latin-1")
        except Exception as e:
            if attempt == 2: raise
            time.sleep(2)

def search_pmc(query, retmax=5):
    """Search PMC for open-access articles."""
    params = {
        "db": "pmc",
        "term": query,
        "retmax": str(retmax),
        "retmode": "json",
        "sort": "relevance"
    }
    data = ncbi_request("esearch.fcgi", params)
    result = json.loads(data)
    return result.get("esearchresult", {}).get("idlist", [])

def get_pmc_fulltext(pmcid):
    """Download full text XML from PMC."""
    params = {"db": "pmc", "id": pmcid, "rettype": "xml", "retmode": "xml"}
    return ncbi_request("efetch.fcgi", params)

def parse_pmc_fulltext(xml_data):
    """Extract title, authors, abstract, and body text from PMC XML."""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        # Try to clean the XML
        xml_data = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]', '', xml_data)
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError:
            return None
    
    ns = {"pmc": "http://www.ncbi.nlm.nih.gov/pmc/", 
          "xlink": "http://www.w3.org/1999/xlink",
          "mml": "http://www.w3.org/1998/Math/MathML"}
    
    # Article metadata
    front = root.find(".//front")
    if front is None:
        return None
    
    article_meta = front.find(".//article-meta")
    
    # Title
    title = ""
    title_group = article_meta.find(".//title-group")
    if title_group is not None:
        title_el = title_group.find(".//article-title")
        if title_el is not None:
            title = "".join(title_el.itertext()).strip()
    
    # Authors
    authors = []
    for contrib in article_meta.findall(".//contrib"):
        surname = contrib.find(".//surname")
        given = contrib.find(".//given-names")
        if surname is not None:
            name = ""
            if given is not None:
                name = "".join(given.itertext()).strip() + " "
            name += "".join(surname.itertext()).strip()
            authors.append(name)
    
    # Journal
    journal = ""
    journal_el = article_meta.find(".//journal-title")
    if journal_el is not None:
        journal = "".join(journal_el.itertext()).strip()
    
    # Year
    year = ""
    pub_date = article_meta.find(".//pub-date")
    if pub_date is not None:
        year_el = pub_date.find("year")
        if year_el is not None:
            year = year_el.text or ""
    
    # DOI
    doi = ""
    for eid in article_meta.findall(".//article-id"):
        if eid.get("pub-id-type") == "doi":
            doi = eid.text or ""
    
    # Abstract
    abstract_parts = []
    abstract = article_meta.find(".//abstract")
    if abstract is not None:
        for abs_el in abstract.iter():
            if abs_el.tag.endswith("title"):
                abstract_parts.append(f"**{''.join(abs_el.itertext()).strip()}:** ")
            elif abs_el.tag.endswith("p"):
                abstract_parts.append("".join(abs_el.itertext()).strip() + "\n\n")
    
    abstract_text = "".join(abstract_parts) if abstract_parts else "No abstract available."
    
    # Body text
    body_parts = []
    body = root.find(".//body")
    if body is not None:
        for sec in body.findall(".//sec"):
            sec_title = sec.find("title")
            if sec_title is not None:
                sec_title_text = "".join(sec_title.itertext()).strip()
                body_parts.append(f"\n## {sec_title_text}\n\n")
            for p in sec.findall(".//p"):
                p_text = "".join(p.itertext()).strip()
                if p_text:
                    body_parts.append(p_text + "\n\n")
    
    # If no body found, try to extract from all paragraphs
    if not body_parts and body is not None:
        for p in body.findall(".//p"):
            p_text = "".join(p.itertext()).strip()
            if p_text:
                body_parts.append(p_text + "\n\n")
    
    body_text = "".join(body_parts)
    
    return {
        "title": title,
        "authors": ", ".join(authors[:6]),
        "journal": journal,
        "year": year,
        "doi": doi,
        "pmcid": "",
        "abstract": abstract_text,
        "body": body_text
    }

def download_pmc_pdf(pmcid, output_path):
    """Try direct PDF download."""
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "ResearchBot/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            if data and len(data) > 10000:  # Real PDF
                with open(output_path, "wb") as f:
                    f.write(data)
                return True
    except: pass
    return False

def sanitize(name):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    while "__" in safe: safe = safe.replace("__", "_")
    if len(safe) > 80: safe = safe[:80]
    return safe.strip("_ ")

def save_fulltext_md(article, pmcid, output_path):
    """Save full text as markdown."""
    authors_str = article.get("authors", "Unknown")
    if len(authors_str) > 6:
        authors_str += " et al."
    
    body = article.get("body", "")
    word_count = len(body.split()) if body else 0
    
    md = f"""# {article.get('title', 'Untitled')}

**Authors:** {article.get('authors', 'Unknown')}
**Journal:** {article.get('journal', 'Unknown')}
**Year:** {article.get('year', 'Unknown')}
**PMCID:** {pmcid}
**DOI:** {article.get('doi', 'N/A')}
**Word Count (body):** {word_count}

## Abstract

{article.get('abstract', 'No abstract available.')}

## Full Text (Body)

{body}

---
*Source: PubMed Central. Full text available at: https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    return True

def process_pmc(query_name, query_string, max_results=3):
    """Search PMC, download full text where possible."""
    print(f"\n{'='*70}")
    print(f"PMC SEARCH: {query_name}")
    print(f"Query: {query_string}")
    print(f"{'='*70}")
    
    pmcids = search_pmc(query_string, max_results)
    print(f"Found {len(pmcids)} results: {pmcids}")
    
    for i, pmcid in enumerate(pmcids):
        print(f"\n  [{i+1}] PMC{pmcid}: Fetching full text...")
        time.sleep(0.5)
        
        # Try PDF first
        fname_pdf = os.path.join(OUTPUT_DIR, f"PMC{pmcid}.pdf")
        pdf_ok = download_pmc_pdf(pmcid, fname_pdf)
        
        if pdf_ok:
            # Get metadata from PMC to rename
            time.sleep(0.3)
            xml_data = get_pmc_fulltext(pmcid)
            article = parse_pmc_fulltext(xml_data)
            if article and article.get("title"):
                new_name = sanitize(article["title"])
                new_path = os.path.join(OUTPUT_DIR, f"{new_name}.pdf")
                os.rename(fname_pdf, new_path)
                print(f"    -> PDF saved: {os.path.basename(new_path)} ({os.path.getsize(new_path):,} bytes)")
                # Also save metadata
                md_name = os.path.join(OUTPUT_DIR, f"{new_name}_info.md")
                save_fulltext_md(article, pmcid, md_name)
            else:
                print(f"    -> PDF saved: PMC{pmcid}.pdf ({os.path.getsize(fname_pdf):,} bytes)")
        else:
            # Get full text XML
            xml_data = get_pmc_fulltext(pmcid)
            if not xml_data or len(xml_data) < 100:
                print(f"    -> Failed to get content (response too small)")
                continue
            
            article = parse_pmc_fulltext(xml_data)
            if article is None:
                print(f"    -> Failed to parse XML")
                continue
            
            fname = sanitize(article["title"])
            if not fname:
                fname = f"PMC{pmcid}"
            
            md_path = os.path.join(OUTPUT_DIR, f"{fname}.md")
            save_fulltext_md(article, pmcid, md_path)
            
            wc = len(article.get("body", "").split()) if article.get("body") else 0
            title_short = article["title"][:70]
            print(f"    -> Full text MD ({wc} words): {os.path.basename(md_path)}")
            print(f"       Title: {title_short}...")

# ═══════════════════════════════════════════════════════
# SEARCH PMC OPEN ACCESS
# ═══════════════════════════════════════════════════════

queries = [
    # 1. Attachment theory - infant-specific
    ("Infant Attachment Development",
     '(infant[Title] OR infancy[Title]) AND ("attachment"[Title] OR "strange situation"[Title] OR "maternal sensitivity"[Title]) AND "open access"[filter]',
     3),
    
    # 2. Emotional regulation - infancy
    ("Infant Emotion Regulation",
     '(infant[Title] OR infancy[Title]) AND ("emotion regulation"[Title] OR "emotional" OR "self-regulation"[Title]) AND "open access"[filter]',
     3),
    
    # 3. Parent-infant bonding
    ("Parent-Infant Bonding",
     '(infant[Title]) AND ("bonding"[Title] OR "parent-infant"[Title] OR "mother-infant"[Title]) AND "open access"[filter]',
     3),
    
    # 4. Still-face / co-regulation
    ("Still-Face Co-Regulation",
     '(infant[Title]) AND ("still face"[Title] OR "co-regulation"[Title] OR "synchrony"[Title]) AND "open access"[filter]',
     3),
]

for name, query, max_r in queries:
    process_pmc(name, query, max_r)
    time.sleep(1)

# ═══════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════

print(f"\n{'='*70}")
print("ALL SAVED FILES:")
print(f"{'='*70}")
print(f"Output: {OUTPUT_DIR}\n")

for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(fpath)
    ext = f.split('.')[-1].upper()
    marker = "FULL" if size > 5000 else "abs "
    print(f"  [{ext} {marker}] {f} ({size:,} bytes)")

# Count full-text articles
full_text_count = sum(1 for f in os.listdir(OUTPUT_DIR) if os.path.getsize(os.path.join(OUTPUT_DIR, f)) > 5000)
print(f"\nTotal files: {len(os.listdir(OUTPUT_DIR))}")
print(f"Full text files (likely complete): {full_text_count}")
