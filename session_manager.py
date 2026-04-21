"""
session_manager.py
------------------
Manages per-session state for the Wikipedia QA Chatbot.
Stores the last fetched article, intent, summaries, and usage stats.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class SessionManager:
    # Article state
    last_topic: str = ""
    last_article_title: str = ""
    last_article_text: str = ""
    last_article_url: str = ""
    last_article_word_count: int = 0
    last_article_summary_preview: str = ""

    # Intent state
    last_intent: str = "—"
    last_confidence: float = 0.0

    # Summaries
    bart_summary: str = ""
    t5_summary: str = ""
    rouge_scores: Dict = field(default_factory=dict)
    rouge_winner: str = ""

    # Usage stats
    questions_asked: int = 0
    summaries_done: int = 0
    articles_fetched: int = 0

    def reset(self):
        """Reset all session state."""
        self.__init__()

    def has_article(self) -> bool:
        """Check if an article has been loaded into session."""
        return bool(self.last_article_text.strip())

    def has_summaries(self) -> bool:
        """Check if summaries have been generated."""
        return bool(self.bart_summary or self.t5_summary)

    def update_article(self, article_data: dict):
        """Update session with fetched article data."""
        self.last_topic = article_data.get("topic", "")
        self.last_article_title = article_data.get("title", "")
        self.last_article_text = article_data.get("cleaned_text", "")
        self.last_article_url = article_data.get("url", "")
        self.last_article_word_count = article_data.get("word_count", 0)
        self.last_article_summary_preview = article_data.get("preview", "")
        self.articles_fetched += 1

    def update_summaries(self, summary_data: dict):
        """Update session with generated summary data."""
        self.bart_summary = summary_data.get("bart_summary", "")
        self.t5_summary = summary_data.get("t5_summary", "")
        self.rouge_scores = summary_data.get("rouge_scores", {})
        self.rouge_winner = summary_data.get("winner", "")
        self.summaries_done += 1
