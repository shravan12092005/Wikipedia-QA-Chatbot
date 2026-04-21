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
import wikipedia
import nltk

# Download NLTK data if needed (silent)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


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

    try:
        wikipedia.set_lang("en")

        # Sanitize and limit topic length
        topic = topic.strip()[:200]
        if not topic:
            result["error"] = "Topic cannot be empty."
            return result

        # Search for the topic
        search_results = wikipedia.search(topic, results=5)
        if not search_results:
            result["error"] = f"No Wikipedia articles found for: '{topic}'"
            return result

        # Try each result until one loads without a disambiguation error
        page = None
        for candidate in search_results:
            try:
                page = wikipedia.page(candidate, auto_suggest=False)
                break
            except wikipedia.exceptions.DisambiguationError as e:
                # Take the first option from disambiguation
                try:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    break
                except Exception as ex:
                    print(f"[WikipediaFetcher] Warning: disambiguation fallback failed: {ex}")
                    continue
            except wikipedia.exceptions.PageError:
                continue

        if page is None:
            result["error"] = f"Could not load a Wikipedia page for: '{topic}'"
            return result

        raw_text     = page.content
        cleaned      = clean_text(raw_text)
        sentences    = nltk.sent_tokenize(cleaned)
        word_count   = len(cleaned.split())
        preview      = cleaned[:400].rsplit(" ", 1)[0] + "…"

        result.update({
            "title":        page.title,
            "url":          page.url,
            "raw_text":     raw_text,
            "cleaned_text": cleaned,
            "word_count":   word_count,
            "sentences":    sentences,
            "preview":      preview,
        })

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
