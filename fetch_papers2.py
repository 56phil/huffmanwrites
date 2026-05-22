#!/usr/bin/env python3
"""
Fetch additional high-quality papers and attempt full-text downloads.
Focus on: Bowlby, still-face paradigm, social-emotional development reviews.
"""

import os, json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET

OUTPUT_DIR = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research/0-12-months/"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ncbi_request(endpoint, params):
    url = NCBI_BASE + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt == 2: raise
            time.sleep(1)

def search_pubmed(query, retmax=3):
    params = {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json", "sort": "relevance"}
    data = ncbi_request("esearch.fcgi", params)
    result = json.loads(data)
    return result.get("esearchresult", {}).get("idlist", [])

def get_details(pmids):
    if not pmids: return None
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"}
    return ncbi_request("efetch.fcgi", params)

def parse_articles(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        info = {"pmid": "", "pmcid": "", "title": "", "authors": "", "journal": "", "year": "", "abstract": "", "doi": ""}
        pmid_el = article.find(".//PMID")
        if pmid_el is not None: info["pmid"] = pmid_el.text or ""
        art = article.find(".//Article")
        if art is not None:
            title_el = art.find(".//ArticleTitle")
            if title_el is not None: info["title"] = title_el.text or ""
            abs_parts = []
            for abs_el in art.findall(".//AbstractText"):
                label = abs_el.get("Label", "")
                text = abs_el.text or ""
                abs_parts.append(f"{label}: {text}" if label else text)
            info["abstract"] = " ".join(abs_parts)
            journal_el = art.find(".//Journal")
            if journal_el is not None:
                jtitle = journal_el.find(".//Title")
                if jtitle is not None: info["journal"] = jtitle.text or ""
                year_el = journal_el.find(".//PubDate/Year")
                if year_el is None: year_el = journal_el.find(".//PubDate/MedlineDate")
                if year_el is not None: info["year"] = year_el.text[:4] if year_el.text else ""
            authors = []
            for author in art.findall(".//Author"):
                last = author.find("LastName")
                fore = author.find("ForeName")
                if last is not None:
                    name = (fore.text or "") + " " + (last.text or "") if fore is not None else last.text or ""
                    authors.append(name.strip())
            info["authors"] = ", ".join(authors[:5])
            if len(authors) > 5: info["authors"] += " et al."
        for eid in article.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi": info["doi"] = eid.text or ""
        for art_id in article.findall(".//ArticleIdList/ArticleId"):
            if art_id.get("IdType") == "pmc": info["pmcid"] = art_id.text or ""
        articles.append(info)
    return articles

def download_pmc_pdf(pmcid, output_path):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "ResearchBot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if data and len(data) > 5000:
                with open(output_path, "wb") as f: f.write(data)
                return True
    except: pass
    return False

def save_md(article, output_path):
    abstract = article.get("abstract", "No abstract available.")
    abstract = abstract.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    md = f"""# {article.get('title', 'Untitled')}

**Authors:** {article.get('authors', 'Unknown')}
**Journal:** {article.get('journal', 'Unknown')}
**Year:** {article.get('year', 'Unknown')}
**PMID:** {article.get('pmid', 'N/A')}
**PMCID:** {article.get('pmcid', 'N/A')}
**DOI:** {article.get('doi', 'N/A')}

## Abstract

{abstract}

---
*Source: PubMed. Full text: https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid', '')}/*
"""
    with open(output_path, "w", encoding="utf-8") as f: f.write(md)

def sanitize(name):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    while "__" in safe: safe = safe.replace("__", "_")
    if len(safe) > 80: safe = safe[:80]
    return safe.strip("_ ")

def process_query(name, query, max_r=3):
    print(f"\n{'='*60}")
    print(f"QUERY: {name}")
    print(f"Search: {query}")
    pmids = search_pubmed(query, max_r)
    print(f"Found: {pmids}")
    if not pmids: return
    time.sleep(0.5)
    xml_data = get_details(pmids)
    if not xml_data: return
    articles = parse_articles(xml_data)
    for i, a in enumerate(articles):
        print(f"\n  [{i+1}] {a['title'][:85]}")
        print(f"      {a['journal']} ({a['year']}) - PMID:{a['pmid']}")
        fname = sanitize(a["title"]) or f"article_{a['pmid']}"
        pmcid = a.get("pmcid", "")
        pdf_path = os.path.join(OUTPUT_DIR, f"{fname}.pdf")
        md_path = os.path.join(OUTPUT_DIR, f"{fname}.md")
        downloaded = False
        if pmcid:
            print(f"      PMCID: {pmcid} - trying PDF...")
            time.sleep(0.5)
            downloaded = download_pmc_pdf(pmcid, pdf_path)
            if downloaded: print(f"      -> PDF: {os.path.basename(pdf_path)}")
        if not downloaded:
            save_md(a, md_path)
            print(f"      -> MD: {os.path.basename(md_path)}")

# ═══════════════════════════════════════════════════════
# TARGETED QUERIES
# ═══════════════════════════════════════════════════════

# 1. Still-face paradigm / Tronick
process_query("Still-Face Paradigm",
    '(infant[Title/Abstract]) AND ("still face"[Title/Abstract] OR Tronick[Author]) AND hasabstract',
    2)

# 2. Early social-emotional development review
process_query("Social-Emotional Development Review",
    '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND ("social-emotional development"[Title/Abstract] OR "socioemotional development"[Title/Abstract]) AND hasabstract AND (review[Publication Type])',
    2)

# 3. Oxytocin and infant bonding 
process_query("Oxytocin Infant Bonding",
    '(infant[Title/Abstract]) AND (oxytocin[Title/Abstract]) AND (bonding[Title/Abstract] OR attachment[Title/Abstract]) AND hasabstract',
    2)

# 4. Temperament and emotional development infancy 
process_query("Infant Temperament Emotional Development",
    '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND (temperament[Title/Abstract]) AND ("emotional"[Title/Abstract] OR "emotion"[Title/Abstract]) AND hasabstract AND (review[Publication Type])',
    2)

print(f"\n{'='*60}")
print("DONE. Listing all files:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    sz = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    tp = "PDF" if f.endswith('.pdf') else "MD "
    print(f"  [{tp}] {f} ({sz:,} bytes)")
