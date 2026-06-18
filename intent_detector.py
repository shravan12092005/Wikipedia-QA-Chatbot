"""
intent_detector.py
------------------
Loads the fine-tuned DistilBERT model and exposes
detect_intent(text) -> (intent_label: str, confidence: float)

Falls back to zero-shot classification if the model hasn't been trained yet.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "intent_model")

INTENT_LABELS = {
    0: "greeting",
    1: "topic_request",
    2: "question_answering",
    3: "summarization",
    4: "farewell",
}

INTENT_COLORS = {
    "greeting":          "#6366f1",   # indigo
    "topic_request":     "#8b5cf6",   # purple
    "question_answering":"#0ea5e9",   # sky blue
    "summarization":     "#10b981",   # emerald
    "farewell":          "#f59e0b",   # amber
}


class IntentDetector:
    def __init__(self):
        self.model     = None
        self.tokenizer = None
        self.device    = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()

    # ── Loading ─────────────────────────────────────────────────────────────
    def _load_model(self):
        if os.path.isdir(MODEL_DIR) and os.path.exists(
            os.path.join(MODEL_DIR, "config.json")
        ):
            print(f"[IntentDetector] Loading fine-tuned model from {MODEL_DIR}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
                self.model     = AutoModelForSequenceClassification.from_pretrained(
                    MODEL_DIR
                ).to(self.device)
                self.model.eval()
                print("[IntentDetector] ✅ Model loaded successfully.")
            except Exception as e:
                print(f"[IntentDetector] ⚠️  Failed to load model: {e}")
                self._use_fallback()
        else:
            print(
                "[IntentDetector] ⚠️  Fine-tuned model not found. "
                "Run 'python train_intent_model.py' first.\n"
                "Using rule-based fallback for now."
            )
            self._use_fallback()

    def _use_fallback(self):
        """Simple keyword-based fallback when model is unavailable."""
        self.model     = None
        self.tokenizer = None

    # ── Inference ────────────────────────────────────────────────────────────
    def detect_intent(self, text: str):
        """
        Returns (intent_label: str, confidence: float).
        Uses fine-tuned DistilBERT if available, else keyword fallback.
        """
        if self.model is not None and self.tokenizer is not None:
            return self._model_predict(text)
        return self._fallback_predict(text)

    def _model_predict(self, text: str):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=64,
            padding=True,
        ).to(self.device)

        with torch.inference_mode():
            outputs   = self.model(**inputs)
            logits    = outputs.logits
            probs     = torch.softmax(logits, dim=-1)
            pred_id   = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][pred_id].item()

        intent = INTENT_LABELS.get(pred_id, "topic_request")
        return intent, round(confidence * 100, 1)

    def _fallback_predict(self, text: str):
        """Keyword-based rule fallback (used if model not yet trained)."""
        import re
        text_lower = text.lower().strip()

        # ── Topic-request phrases must be checked FIRST ──────────────────────
        # This prevents "tell me about Rohit sharma" being mis-tagged as greeting
        # because "sharma" contains "hi".
        topic_phrases = [
            "tell me about", "search for", "look up", "find info on",
            "find information on", "i want to know about", "i'm curious about",
            "give me information on", "search wikipedia for",
            "what does wikipedia say about", "i want to learn about",
            "can you look up", "who is", "who was", "what is", "what are",
            "learn about", "info on", "information on", "tell me",
        ]
        if any(text_lower.startswith(ph) or ph in text_lower for ph in topic_phrases):
            return "topic_request", 88.0

        # ── Whole-word keyword matching (avoids "sharma" → "hi") ─────────────
        def has_word(kw_list):
            return any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
                       for kw in kw_list)

        greeting_kw  = ["hello", "hi", "hey", "howdy", "greetings",
                        "sup", "hiya", "good morning", "good evening", "what's up"]
        farewell_kw  = ["bye", "goodbye", "see you", "farewell", "thanks",
                        "thank you", "that's all", "cheers", "ciao",
                        "later", "signing off", "good night", "peace"]
        summarize_kw = ["summarize", "summary", "tl;dr", "brief", "condense",
                        "overview", "gist", "shorten", "highlights", "abstract"]
        question_kw  = ["who", "what", "when", "where", "how", "which",
                        "why", "does", "did", "was", "were"]

        if has_word(greeting_kw):
            return "greeting", 90.0
        if has_word(farewell_kw):
            return "farewell", 88.0
        if has_word(summarize_kw):
            return "summarization", 85.0
        if has_word(question_kw):
            return "question_answering", 80.0
        return "topic_request", 75.0

    def get_intent_color(self, intent: str) -> str:
        return INTENT_COLORS.get(intent, "#6366f1")


# Singleton — imported by app.py
_detector_instance = None

def get_detector() -> IntentDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = IntentDetector()
    return _detector_instance
