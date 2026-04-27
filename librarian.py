"""
librarian.py — core logic for the Knowledge Librarian app.
Handles URL extraction, Claude summarization, and Supabase index management.
"""

import os
import json
import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import anthropic
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from supabase import create_client, Client

# ─── Config ───────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY      = os.environ.get("SUPABASE_KEY", "")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ─── Index management ─────────────────────────────────────────────────────────

def load_index() -> list:
    try:
        sb = get_supabase()
        response = sb.table("knowledge_index").select("*").order("date_saved", desc=True).execute()
        return response.data or []
    except Exception as e:
        print(f"load_index error: {e}")
        return []


def url_already_saved(url: str) -> bool:
    try:
        sb = get_supabase()
        response = sb.table("knowledge_index").select("id").eq("url", url).execute()
        return len(response.data) > 0
    except Exception:
        return False


def delete_entry(entry_id: str) -> bool:
    try:
        sb = get_supabase()
        sb.table("knowledge_index").delete().eq("id", entry_id).execute()
        return True
    except Exception as e:
        print(f"delete_entry error: {e}")
        return False


def update_entry(entry_id: str, **fields) -> bool:
    try:
        sb = get_supabase()
        sb.table("knowledge_index").update(fields).eq("id", entry_id).execute()
        return True
    except Exception as e:
        print(f"update_entry error: {e}")
        return False


# ─── URL detection ────────────────────────────────────────────────────────────

def detect_source_type(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "kaggle.com" in domain:
        return "kaggle"
    return "web"


# ─── Extractors ───────────────────────────────────────────────────────────────

def extract_youtube(url: str) -> dict:
    """Extract video description from a YouTube URL."""
    try:
        import requests
        from bs4 import BeautifulSoup

        video_id = None
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]

        if not video_id:
            return {"success": False, "error": "Could not extract video ID from URL"}

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        title_tag = soup.find("meta", property="og:title")
        if title_tag:
            title = title_tag.get("content", "")
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.replace(" - YouTube", "").strip()

        description = ""
        desc_tag = soup.find("meta", property="og:description")
        if desc_tag:
            description = desc_tag.get("content", "")

        match = re.search(r'"shortDescription":"(.*?)"(?:,"isCrawlable")', response.text)
        if match:
            description = match.group(1).replace("\\n", "\n").replace('\\"', '"')

        if not description:
            description = "No description available."

        return {
            "success": True,
            "title": title or f"YouTube Video ({video_id})",
            "content": description,
            "source_type": "youtube",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_kaggle(url: str) -> dict:
    """Extract content from a Kaggle notebook, competition, or discussion."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        title_tag = soup.find("meta", property="og:title")
        if title_tag:
            title = title_tag.get("content", "")
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.strip()

        content = ""
        desc_tag = soup.find("meta", property="og:description")
        if desc_tag:
            content = desc_tag.get("content", "")

        for tag in soup.find_all(["p", "h1", "h2", "h3"], limit=20):
            text = tag.get_text(strip=True)
            if len(text) > 50:
                content += "\n" + text

        content = content.strip()
        if not content:
            content = "Kaggle resource — no extractable description."

        return {
            "success": True,
            "title": title or "Kaggle Resource",
            "content": content[:3000],
            "source_type": "kaggle",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_generic(url: str) -> dict:
    """Extract main content from any webpage using trafilatura."""
    try:
        import trafilatura
        import requests
        from bs4 import BeautifulSoup

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.text, "html.parser")
        title = ""
        title_tag = soup.find("meta", property="og:title")
        if title_tag:
            title = title_tag.get("content", "")
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.strip()

        content = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=True,
            no_fallback=False
        )

        if not content:
            paragraphs = soup.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

        if not content:
            content = "Could not extract readable content from this page."

        return {
            "success": True,
            "title": title or urlparse(url).netloc,
            "content": content[:5000],
            "source_type": "web",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_content(url: str) -> dict:
    """Route to the correct extractor based on URL."""
    source_type = detect_source_type(url)
    if source_type == "youtube":
        return extract_youtube(url)
    elif source_type == "kaggle":
        return extract_kaggle(url)
    else:
        return extract_generic(url)


# ─── Claude summarization ─────────────────────────────────────────────────────

def summarize_with_claude(title: str, content: str, url: str, source_type: str, user_note: str = None) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    note_section = f"\nUser's note: {user_note}" if user_note else ""

    prompt = f"""You are a knowledge librarian. A data scientist with expertise in Power BI, Microsoft Fabric, Machine Learning, Causal Inference, Time Series Analysis, Survival Analysis, and Deep Learning has saved this resource.

URL: {url}
Source type: {source_type}
Title: {title}
{note_section}

Content:
{content[:4000]}

Your job is to create a concise summary card for this resource. Return ONLY a JSON object with this exact structure:
{{
  "title": "clean, readable title (use the original title if good, improve it if needed)",
  "summary": "2-4 sentence summary of what this resource covers and why it is useful. Be specific about methods, techniques, or concepts covered.",
  "tags": ["tag1", "tag2", "tag3"],
  "category": "broad discipline, e.g. Business Intelligence, Machine Learning & AI, Statistics, Programming, Data Engineering",
  "subcategory": "mid-level grouping within the category, e.g. Power BI, Deep Learning, Survival Analysis, Causal Inference, Time Series",
  "topic": "specific subject within the subcategory, e.g. DAX measures, SMOTE oversampling, Cox PH model, SHAP values",
  "key_concepts": ["concept1", "concept2", "concept3"]
}}

Rules:
- tags should be specific technical terms (e.g. "SMOTE", "DAX", "Cox PH", "LightGBM")
- category / subcategory / topic form a hierarchy from broad to narrow — be consistent across entries
- summary should be informative enough that the user can decide whether to revisit the source
- Return only valid JSON, no other text"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)

        parsed = json.loads(raw)
        return {"success": True, "data": parsed}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Main entry point ─────────────────────────────────────────────────────────

def process_url(url: str, user_note: str = None, collection: str = None,
                category: str = None, subcategory: str = None, topic: str = None) -> dict:
    if url_already_saved(url):
        return {"success": False, "error": "This URL is already in your library."}

    extraction = extract_content(url)
    if not extraction["success"]:
        return {"success": False, "error": f"Extraction failed: {extraction['error']}"}

    summary_result = summarize_with_claude(
        title=extraction["title"],
        content=extraction["content"],
        url=url,
        source_type=extraction["source_type"],
        user_note=user_note
    )

    if not summary_result["success"]:
        return {"success": False, "error": f"Summarization failed: {summary_result['error']}"}

    card = summary_result["data"]

    entry = {
        "id":           hashlib.md5(url.encode()).hexdigest()[:10],
        "url":          url,
        "title":        card.get("title", extraction["title"]),
        "summary":      card.get("summary", ""),
        "tags":         card.get("tags", []),
        "key_concepts": card.get("key_concepts", []),
        "category":     category    or card.get("category", "General"),
        "subcategory":  subcategory or card.get("subcategory", ""),
        "topic":        topic       or card.get("topic", ""),
        "collection":   collection  or "",
        "source_type":  extraction["source_type"],
        "user_note":    user_note   or "",
        "date_saved":   datetime.now().isoformat(),
    }

    try:
        sb = get_supabase()
        sb.table("knowledge_index").insert(entry).execute()
    except Exception as e:
        return {"success": False, "error": f"Database save failed: {e}"}

    return {"success": True, "entry": entry}


# ─── Search ───────────────────────────────────────────────────────────────────

def entry_category(entry: dict) -> str:
    return entry.get("category") or entry.get("domain", "General")


def search_index(query: str, category: str = None, source_type: str = None) -> list:
    index = load_index()
    query_terms = query.lower().split()

    scored = []
    for entry in index:
        if category and entry_category(entry) != category:
            continue
        if source_type and entry.get("source_type") != source_type:
            continue

        score = 0
        searchable = " ".join([
            entry.get("title", ""),
            entry.get("summary", ""),
            " ".join(entry.get("tags", []) if isinstance(entry.get("tags"), list) else []),
            " ".join(entry.get("key_concepts", []) if isinstance(entry.get("key_concepts"), list) else []),
            entry.get("user_note", ""),
            entry.get("category", ""),
            entry.get("subcategory", ""),
            entry.get("topic", ""),
            entry.get("collection", ""),
            entry.get("domain", ""),
        ]).lower()

        for term in query_terms:
            tags = entry.get("tags", []) if isinstance(entry.get("tags"), list) else []
            concepts = entry.get("key_concepts", []) if isinstance(entry.get("key_concepts"), list) else []
            if any(term in t.lower() for t in tags + concepts):
                score += 3
            if term in entry.get("title", "").lower():
                score += 2
            if term in searchable:
                score += 1

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored]