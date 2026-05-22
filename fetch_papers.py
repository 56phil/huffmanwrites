#!/usr/bin/env python3
"""
Refined search for high-quality infant development research articles.
Targeted queries for: attachment theory, emotional regulation, early socialization.
"""

import os
import json
import time
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

OUTPUT_DIR = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research/0-12-months/"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ncbi_request(endpoint, params, max_retries=3):
    url = NCBI_BASE + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    return None

def search_pubmed(query, retmax=5):
    params = {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json", "sort": "relevance"}
    data = ncbi_request("esearch.fcgi", params)
    result = json.loads(data)
    return result.get("esearchresult", {}).get("idlist", [])

def get_pubmed_details(pmids):
    if not pmids:
        return None
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"}
    return ncbi_request("efetch.fcgi", params)

def parse_articles(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        info = {"pmid": "", "pmcid": "", "title": "", "authors": "", "journal": "", 
                "year": "", "abstract": "", "doi": ""}
        pmid_el = article.find(".//PMID")
        if pmid_el is not None:
            info["pmid"] = pmid_el.text or ""
        art = article.find(".//Article")
        if art is not None:
            title_el = art.find(".//ArticleTitle")
            if title_el is not None:
                info["title"] = title_el.text or ""
            abs_parts = []
            for abs_el in art.findall(".//AbstractText"):
                label = abs_el.get("Label", "")
                text = abs_el.text or ""
                if label:
                    abs_parts.append(f"{label}: {text}")
                else:
                    abs_parts.append(text)
            info["abstract"] = " ".join(abs_parts)
            journal_el = art.find(".//Journal")
            if journal_el is not None:
                jtitle = journal_el.find(".//Title")
                if jtitle is not None:
                    info["journal"] = jtitle.text or ""
                year_el = journal_el.find(".//PubDate/Year")
                if year_el is None:
                    year_el = journal_el.find(".//PubDate/MedlineDate")
                if year_el is not None:
                    info["year"] = year_el.text[:4] if year_el.text else ""
            authors = []
            for author in art.findall(".//Author"):
                last = author.find("LastName")
                fore = author.find("ForeName")
                if last is not None:
                    name = last.text or ""
                    if fore is not None:
                        name = (fore.text or "") + " " + name
                    authors.append(name)
            info["authors"] = ", ".join(authors[:5])
            if len(authors) > 5:
                info["authors"] += " et al."
        for eid in article.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi":
                info["doi"] = eid.text or ""
        for art_id in article.findall(".//ArticleIdList/ArticleId"):
            if art_id.get("IdType") == "pmc":
                info["pmcid"] = art_id.text or ""
        articles.append(info)
    return articles

def download_pmc_pdf(pmcid, output_path):
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "ResearchBot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
            if data and len(data) > 5000:  # Real PDFs are larger
                with open(output_path, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"    PDF download failed: {e}")
    return False

def save_as_markdown(article, output_path):
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
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    return True

def sanitize_filename(name):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    while "__" in safe:
        safe = safe.replace("__", "_")
    if len(safe) > 80:
        safe = safe[:80]
    safe = safe.strip("_ ")
    return safe

def process_query(query_name, query_string, max_results=3):
    print(f"\n{'='*70}")
    print(f"QUERY: {query_name}")
    print(f"Search: {query_string}")
    print(f"{'='*70}")
    
    pmids = search_pubmed(query_string, retmax=max_results)
    print(f"Found {len(pmids)} results: {pmids}")
    
    if not pmids:
        print("No results found.")
        return
    
    time.sleep(0.5)
    xml_data = get_pubmed_details(pmids)
    if not xml_data:
        print("Failed to fetch article details.")
        return
    
    articles = parse_articles(xml_data)
    print(f"Parsed {len(articles)} articles.")
    
    for i, article in enumerate(articles):
        print(f"\n--- [{i+1}] {article['title'][:90]}")
        print(f"    Journal: {article['journal']} ({article['year']})")
        print(f"    Authors: {article['authors'][:80]}")
        
        fname = sanitize_filename(article["title"])
        if not fname:
            fname = f"article_{article['pmid']}"
        
        pmcid = article.get("pmcid", "")
        pdf_path = os.path.join(OUTPUT_DIR, f"{fname}.pdf")
        md_path = os.path.join(OUTPUT_DIR, f"{fname}.md")
        
        downloaded = False
        if pmcid:
            print(f"    PMCID: {pmcid} - attempting PDF download...")
            time.sleep(0.5)
            downloaded = download_pmc_pdf(pmcid, pdf_path)
            if downloaded:
                print(f"    -> PDF saved: {os.path.basename(pdf_path)}")
        
        if not downloaded:
            save_as_markdown(article, md_path)
            print(f"    -> Markdown saved: {os.path.basename(md_path)}")

# ══════════════════════════════════════════════════════
# REFINED QUERIES - targeted for infant 0-12 months
# ══════════════════════════════════════════════════════

queries = [
    # (1) Attachment Theory - specific infant-focused
    ("Attachment Theory - Infant-Mother Attachment",
     '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND ("attachment theory"[Title/Abstract] OR "secure attachment"[Title/Abstract] OR "strange situation"[Title/Abstract] OR "maternal sensitivity"[Title/Abstract]) AND hasabstract',
     4),
    
    # (2) Emotional Regulation - infant-specific
    ("Emotional Regulation in Infancy 0-12 months",
     '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND ("emotion regulation"[Title/Abstract] OR "emotional regulation"[Title/Abstract] OR "self-regulation"[Title/Abstract] OR "co-regulation"[Title/Abstract]) AND hasabstract AND (review[Publication Type] OR journal article[Publication Type])',
     4),
    
    # (3) Early Socialization and Bonding
    ("Infant Bonding and Early Social Development",
     '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND ("mother-infant bonding"[Title/Abstract] OR "parent-infant bonding"[Title/Abstract] OR "social development"[Title/Abstract] OR "early social"[Title/Abstract]) AND hasabstract',
     4),
    
    # (4) Infant Mental Health / Co-regulation
    ("Infant Mental Health Co-Regulation",
     '(infant[Title/Abstract] OR infancy[Title/Abstract]) AND ("infant mental health"[Title/Abstract] OR "co-regulation"[Title/Abstract] OR "parent-infant interaction"[Title/Abstract]) AND hasabstract',
     3),
]

total_attempted = 0
for name, query, max_r in queries:
    process_query(name, query, max_r)
    total_attempted += max_r
    time.sleep(1)

print(f"\n{'='*70}")
print(f"DONE. Searched for up to {total_attempted} articles.")
print(f"Output directory: {OUTPUT_DIR}")

# List all files with size
print("\nAll saved files:")
files = [f for f in os.listdir(OUTPUT_DIR) if not f.startswith('.')]
files.sort()
for f in files:
    fpath = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(fpath)
    suffix = "PDF" if f.endswith('.pdf') else "MD"
    print(f"  [{suffix}] {f} ({size:,} bytes)")

print(f"\nTotal files: {len(files)}")
