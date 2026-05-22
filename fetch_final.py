#!/usr/bin/env python3
"""
Final pass: search for key papers with full text, focusing on:
- Emotional regulation development in infancy (a gap in coverage)
- Try to get full text for parent-infant synchrony (Feldman)
"""

import os, json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re

OUTPUT_DIR = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research/0-12-months/"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ncbi_request(endpoint, params):
    url = NCBI_BASE + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                try:
                    return data.decode("utf-8")
                except UnicodeDecodeError:
                    return data.decode("latin-1")
        except Exception as e:
            if attempt == 2: raise
            time.sleep(2)

def search_pmc(query, retmax=3):
    params = {"db": "pmc", "term": query, "retmax": str(retmax), "retmode": "json", "sort": "relevance"}
    data = ncbi_request("esearch.fcgi", params)
    return json.loads(data).get("esearchresult", {}).get("idlist", [])

def get_pmc_fulltext(pmcid):
    params = {"db": "pmc", "id": pmcid, "rettype": "xml", "retmode": "xml"}
    return ncbi_request("efetch.fcgi", params)

def parse_pmc_fulltext(xml_data):
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        xml_data = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]', '', xml_data)
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError:
            return None
    
    # Article metadata
    article_meta = root.find(".//article-meta")
    if article_meta is None:
        return None
    
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
            name = (("".join(given.itertext()).strip() + " ") if given is not None else "") + "".join(surname.itertext()).strip()
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
    abstract_el = article_meta.find(".//abstract")
    if abstract_el is not None:
        for child in abstract_el.iter():
            if child.tag.endswith("title"):
                abstract_parts.append(f"**{''.join(child.itertext()).strip()}:** ")
            elif child.tag.endswith("p"):
                abstract_parts.append("".join(child.itertext()).strip() + "\n\n")
    abstract_text = "".join(abstract_parts) if abstract_parts else "No abstract available."
    
    # Body
    body_parts = []
    body = root.find(".//body")
    if body is not None:
        for sec in body.findall(".//sec"):
            sec_title = sec.find("title")
            if sec_title is not None:
                body_parts.append(f"\n## {''.join(sec_title.itertext()).strip()}\n\n")
            for p in sec.findall(".//p"):
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
        "abstract": abstract_text,
        "body": body_text
    }

def download_pmc_pdf(pmcid, output_path):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "ResearchBot/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            if data and len(data) > 10000:
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
    body = article.get("body", "")
    wc = len(body.split())
    
    md = f"""# {article.get('title', 'Untitled')}

**Authors:** {article.get('authors', 'Unknown')}
**Journal:** {article.get('journal', 'Unknown')}
**Year:** {article.get('year', 'Unknown')}
**PMCID:** {pmcid}
**DOI:** {article.get('doi', 'N/A')}
**Word Count (body):** {wc}

## Abstract

{article.get('abstract', 'No abstract available.')}

## Full Text (Body)

{body}

---
*Source: PubMed Central. Full text at: https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

# ═══════════════════════════════════════════════════════
# FIND SPECIFIC PAPERS
# ═══════════════════════════════════════════════════════

# 1. Find Feldman synchrony paper in PMC
print("="*60)
print("Searching for Feldman parent-infant synchrony paper...")
pmcids = search_pmc('Ruth Feldman[Author] AND synchrony[Title] AND infant[Title] AND "open access"[filter]', 3)
print(f"PMIDs: {pmcids}")

# 2. Search for emotion regulation development in infancy
print("\n" + "="*60)
print("Searching for emotion regulation development in infancy (open access)...")
er_pmcids = search_pmc('(infant[Title] OR infancy[Title]) AND ("emotion regulation"[Title] OR "emotional development"[Title]) AND "open access"[filter]', 3)
print(f"PMIDs: {er_pmcids}")

# 3. Search for secure attachment + infant + full text review
print("\n" + "="*60)
print("Searching for secure attachment infant development review...")
sa_pmcids = search_pmc('(infant[Title] OR infancy[Title]) AND "secure attachment"[Title] AND review AND "open access"[filter]', 3)
print(f"PMIDs: {sa_pmcids}")

all_pmcids = list(set(pmcids + er_pmcids + sa_pmcids))
print(f"\nAll unique PMCIDs: {all_pmcids}")

for pmcid in all_pmcids:
    print(f"\n{'─'*50}")
    print(f"PMC{pmcid}:")
    time.sleep(0.5)
    
    # Try PDF first
    pdf_path = os.path.join(OUTPUT_DIR, f"PMC{pmcid}.pdf")
    if download_pmc_pdf(pmcid, pdf_path):
        # Get metadata
        time.sleep(0.3)
        xml_data = get_pmc_fulltext(pmcid)
        article = parse_pmc_fulltext(xml_data)
        if article and article.get("title"):
            new_name = sanitize(article["title"])
            new_path = os.path.join(OUTPUT_DIR, f"{new_name}.pdf")
            os.rename(pdf_path, new_path)
            print(f"  PDF: {new_name}.pdf ({os.path.getsize(new_path):,} bytes)")
            md_path = os.path.join(OUTPUT_DIR, f"{new_name}_info.md")
            save_fulltext_md(article, pmcid, md_path)
        else:
            print(f"  PDF: PMC{pmcid}.pdf ({os.path.getsize(pdf_path):,} bytes)")
        continue
    
    # Full text
    xml_data = get_pmc_fulltext(pmcid)
    if not xml_data or len(xml_data) < 100:
        print(f"  Skipped (no content)")
        continue
    
    article = parse_pmc_fulltext(xml_data)
    if article is None:
        print(f"  Skipped (parse failed)")
        continue
    
    fname = sanitize(article["title"]) or f"PMC{pmcid}"
    md_path = os.path.join(OUTPUT_DIR, f"{fname}.md")
    
    # Skip if already saved
    if os.path.exists(md_path):
        print(f"  Already exists: {fname}.md")
        continue
    
    save_fulltext_md(article, pmcid, md_path)
    wc = len(article.get("body", "").split())
    print(f"  Saved: {fname}.md ({wc:,} words)")
    print(f"  Title: {article['title'][:80]}")

print(f"\n{'='*60}")
print("FINAL FILE LISTING:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    sz = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    ft = "FULL" if sz > 10000 else ("abs" if sz < 5000 else "mid")
    tp = "PDF" if f.endswith('.pdf') else "MD "
    print(f"  [{tp} {ft}] {f} ({sz:,} bytes)")
