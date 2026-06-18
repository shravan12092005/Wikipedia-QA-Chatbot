"""
wikipedia_fetcher.py
---------------------
Fetches Wikipedia articles and cleans the raw text.

Functions:
    fetch_article(topic: str) -> dict
    clean_text(raw: str)       -> str
"""

import re
import html
import requests
import nltk

# ── Optional: try the wikipedia library, but we don't depend on it ───────────
try:
    import wikipedia as _wikipedia_lib
    _HAS_WIKIPEDIA_LIB = True
except ImportError:
    _HAS_WIKIPEDIA_LIB = False

# Download NLTK data if needed (silent)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

# ── Shared HTTP session with proper User-Agent ───────────────────────────────
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "WikiQA-Chatbot/1.0 (NLP Course Project; Python/requests)"
})

_API_URL = "https://en.wikipedia.org/w/api.php"


# ── Text Cleaning ────────────────────────────────────────────────────────────
def clean_text(raw: str) -> str:
    """
    Full text cleaning pipeline:
    1. Unescape HTML entities
    2. Strip HTML tags
    3. Remove Wikipedia citation markers like [1], [2], [note 3]
    4. Remove parenthetical pronunciation ( /.../ )
    5. Collapse excessive whitespace / newlines
    6. Strip leading/trailing whitespace
    """
    if not raw:
        return ""
    # 1. HTML unescape
    text = html.unescape(raw)
    # 2. Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # 3. Remove citation brackets [1], [citation needed], etc.
    text = re.sub(r"\[[^\]]{0,20}\]", "", text)
    # 4. Remove pronunciation hints in parentheses with slashes
    text = re.sub(r"\(/[^)]+/\)", "", text)
    # 5. Collapse newlines and extra spaces
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    # 6. Strip
    text = text.strip()
    return text


# ── Direct MediaWiki API helpers ─────────────────────────────────────────────
def _api_search(topic: str, limit: int = 5) -> list[str]:
    """Search Wikipedia via the MediaWiki API and return a list of page titles."""
    resp = _SESSION.get(_API_URL, params={
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "srlimit": limit,
        "format": "json",
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [item["title"] for item in data.get("query", {}).get("search", [])]


def _api_get_page(title: str) -> dict | None:
    """Fetch full page content via the MediaWiki API. Returns dict or None."""
    resp = _SESSION.get(_API_URL, params={
        "action": "query",
        "titles": title,
        "prop": "extracts|info",
        "explaintext": True,        # plain text, no HTML
        "inprop": "url",
        "format": "json",
    }, timeout=30)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    for pid, page_data in pages.items():
        if pid == "-1":
            return None
        return page_data
    return None


# ── Wikipedia Fetch ───────────────────────────────────────────────────────────
def fetch_article(topic: str) -> dict:
    """
    Search Wikipedia and fetch the best matching article.

    Returns a dict with:
        {
          "topic":        str,   # original query
          "title":        str,   # Wikipedia page title
          "url":          str,   # Wikipedia URL
          "raw_text":     str,   # raw page content
          "cleaned_text": str,   # cleaned version
          "word_count":   int,
          "sentences":    list,  # NLTK sentence tokens
          "preview":      str,   # first 300 chars
          "error":        str or None
        }
    """
    result = {
        "topic":        topic,
        "title":        "",
        "url":          "",
        "raw_text":     "",
        "cleaned_text": "",
        "word_count":   0,
        "sentences":    [],
        "preview":      "",
        "error":        None,
    }

    # Sanitize and limit topic length
    topic = topic.strip()[:200]
    if not topic:
        result["error"] = "Topic cannot be empty."
        return result

    try:
        # ── Step 1: Search ────────────────────────────────────────────────
        search_results = _api_search(topic)
        if not search_results:
            result["error"] = f"No Wikipedia articles found for: '{topic}'"
            return result

        # ── Step 2: Fetch the first valid page ────────────────────────────
        page_data = None
        for candidate in search_results:
            page_data = _api_get_page(candidate)
            if page_data and page_data.get("extract"):
                break
            page_data = None

        if page_data is None:
            result["error"] = f"Could not load a Wikipedia page for: '{topic}'"
            return result

        raw_text   = page_data.get("extract", "")
        page_title = page_data.get("title", topic)
        page_url   = page_data.get("fullurl",
                                   f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}")

        cleaned    = clean_text(raw_text)
        sentences  = nltk.sent_tokenize(cleaned)
        word_count = len(cleaned.split())
        preview    = cleaned[:400].rsplit(" ", 1)[0] + "…" if len(cleaned) > 400 else cleaned

        result.update({
            "title":        page_title,
            "url":          page_url,
            "raw_text":     raw_text,
            "cleaned_text": cleaned,
            "word_count":   word_count,
            "sentences":    sentences,
            "preview":      preview,
        })

    except requests.RequestException as e:
        result["error"] = f"Network error fetching Wikipedia: {str(e)}"
    except Exception as e:
        result["error"] = f"Wikipedia fetch error: {str(e)}"

    return result


# ── Singleton / Module-level helper ──────────────────────────────────────────
def get_article_preview(article: dict, max_chars: int = 300) -> str:
    """Return a short preview of the article for the chat response."""
    text = article.get("cleaned_text", "")
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"
