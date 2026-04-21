"""
summarizer.py
-------------
Generates summaries using two HuggingFace models and compares them
using ROUGE scores.

Models used:
    1. facebook/bart-large-cnn  (406M params, specialized for summarization)
    2. t5-small                  (60M params,  general text-to-text)

P09 Requirements:
    a. Clean input text (done in wikipedia_fetcher.py)
    b. Generate summary using BART
    c. Generate summary using T5, compare both
    d. Evaluate using ROUGE-1, ROUGE-2, ROUGE-L
"""

from transformers import pipeline, AutoTokenizer
from rouge_score import rouge_scorer

BART_MODEL = "facebook/bart-large-cnn"
T5_MODEL   = "t5-small"

BART_MAX_INPUT  = 1024   # BART token limit
T5_MAX_INPUT    = 512    # T5 token limit
SUMMARY_MIN_LEN = 80
SUMMARY_MAX_LEN = 250
MAX_INPUT_CHARS = 10000  # hard cap on input to prevent unbounded consumption


class Summarizer:
    def __init__(self):
        self.bart_pipe  = None
        self.t5_pipe    = None
        self.bart_tok   = None
        self.t5_tok     = None
        self.scorer     = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )
        self._load_models()

    # ── Loading ──────────────────────────────────────────────────────────────
    def _load_models(self):
        print(f"[Summarizer] Loading {BART_MODEL} ...")
        try:
            self.bart_pipe = pipeline(
                "summarization",
                model=BART_MODEL,
                tokenizer=BART_MODEL,
            )
            self.bart_tok = AutoTokenizer.from_pretrained(BART_MODEL)
            print("[Summarizer] ✅ BART loaded.")
        except Exception as e:
            print(f"[Summarizer] ❌ BART failed: {e}")

        print(f"[Summarizer] Loading {T5_MODEL} ...")
        try:
            self.t5_pipe = pipeline(
                "summarization",
                model=T5_MODEL,
                tokenizer=T5_MODEL,
            )
            self.t5_tok = AutoTokenizer.from_pretrained(T5_MODEL)
            print("[Summarizer] ✅ T5 loaded.")
        except Exception as e:
            print(f"[Summarizer] ❌ T5 failed: {e}")

    # ── Public API ────────────────────────────────────────────────────────────
    def generate_summaries(self, text: str) -> dict:
        """
        Generate summaries from both BART and T5, then compute ROUGE scores.

        Returns:
            {
                "bart_summary":  str,
                "t5_summary":    str,
                "rouge_scores":  {
                    "bart": {"rouge1": float, "rouge2": float, "rougeL": float},
                    "t5":   {"rouge1": float, "rouge2": float, "rougeL": float},
                },
                "bart_word_count": int,
                "t5_word_count":   int,
                "winner":          "BART" | "T5" | "Tie",
                "error":           str or None,
            }
        """
        result = {
            "bart_summary":    "",
            "t5_summary":      "",
            "rouge_scores":    {},
            "bart_word_count": 0,
            "t5_word_count":   0,
            "winner":          "",
            "error":           None,
        }

        if not text.strip():
            result["error"] = "No article text to summarize."
            return result

        # Hard cap on input length to prevent unbounded resource consumption
        text = text[:MAX_INPUT_CHARS]

        # ── BART ─────────────────────────────────────────────────────────────
        bart_text = self._truncate_to_tokens(text, self.bart_tok, BART_MAX_INPUT)
        if self.bart_pipe:
            try:
                bart_out = self.bart_pipe(
                    bart_text,
                    max_length=SUMMARY_MAX_LEN,
                    min_length=SUMMARY_MIN_LEN,
                    num_beams=4,
                    length_penalty=2.0,
                    no_repeat_ngram_size=3,
                    do_sample=False,
                )
                result["bart_summary"]    = bart_out[0]["summary_text"].strip()
                result["bart_word_count"] = len(result["bart_summary"].split())
            except Exception as e:
                result["bart_summary"] = f"BART error: {e}"
        else:
            result["bart_summary"] = "BART model not loaded."

        # ── T5 ───────────────────────────────────────────────────────────────
        t5_text = self._truncate_to_tokens(text, self.t5_tok, T5_MAX_INPUT)
        # T5 needs "summarize: " prefix
        t5_input = "summarize: " + t5_text
        if self.t5_pipe:
            try:
                t5_out = self.t5_pipe(
                    t5_input,
                    max_length=SUMMARY_MAX_LEN,
                    min_length=SUMMARY_MIN_LEN,
                    num_beams=4,
                    length_penalty=1.5,
                    no_repeat_ngram_size=3,
                    do_sample=False,
                )
                result["t5_summary"]    = t5_out[0]["summary_text"].strip()
                result["t5_word_count"] = len(result["t5_summary"].split())
            except Exception as e:
                result["t5_summary"] = f"T5 error: {e}"
        else:
            result["t5_summary"] = "T5 model not loaded."

        # ── ROUGE Evaluation ─────────────────────────────────────────────────
        reference = text[:2000]   # Use first 2000 chars as pseudo-reference
        bart_scores = self._compute_rouge(reference, result["bart_summary"])
        t5_scores   = self._compute_rouge(reference, result["t5_summary"])

        result["rouge_scores"] = {
            "bart": bart_scores,
            "t5":   t5_scores,
        }

        # ── Winner ────────────────────────────────────────────────────────────
        bart_avg = (bart_scores["rouge1"] + bart_scores["rouge2"] + bart_scores["rougeL"]) / 3
        t5_avg   = (t5_scores["rouge1"]   + t5_scores["rouge2"]   + t5_scores["rougeL"]) / 3

        if abs(bart_avg - t5_avg) < 0.01:
            result["winner"] = "Tie"
        elif bart_avg > t5_avg:
            result["winner"] = "BART"
        else:
            result["winner"] = "T5"

        return result

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _truncate_to_tokens(self, text: str, tokenizer, max_tokens: int) -> str:
        """Truncate text to fit within the model's token limit."""
        if tokenizer is None:
            # Rough approximation: 1 token ≈ 4 chars
            return text[: max_tokens * 4]
        tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
        return tokenizer.decode(tokens, skip_special_tokens=True)

    def _compute_rouge(self, reference: str, hypothesis: str) -> dict:
        """Compute ROUGE-1, ROUGE-2, ROUGE-L F1 scores."""
        if not reference or not hypothesis:
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        try:
            scores = self.scorer.score(reference, hypothesis)
            return {
                "rouge1": round(scores["rouge1"].fmeasure, 4),
                "rouge2": round(scores["rouge2"].fmeasure, 4),
                "rougeL": round(scores["rougeL"].fmeasure, 4),
            }
        except Exception:
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}


# ── Singleton ─────────────────────────────────────────────────────────────────
_summarizer_instance = None

def get_summarizer() -> Summarizer:
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = Summarizer()
    return _summarizer_instance
