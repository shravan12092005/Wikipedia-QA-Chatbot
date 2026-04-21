"""
qa_pipeline.py
--------------
Question-Answering using deepset/roberta-base-squad2.
Handles long contexts by chunking into overlapping 512-token windows
and returning the highest-confidence answer.

P08 Requirement: Implement QA using a pretrained transformer model.
"""

import os
from transformers import pipeline

QA_MODEL = "deepset/roberta-base-squad2"
MAX_CONTEXT_CHARS = 3000   # characters per chunk (safe for 512 tokens)
OVERLAP_CHARS     = 200    # overlap between chunks to avoid boundary issues


class QAPipeline:
    def __init__(self):
        self.qa = None
        self._load()

    def _load(self):
        print(f"[QAPipeline] Loading model: {QA_MODEL} ...")
        try:
            self.qa = pipeline(
                "question-answering",
                model=QA_MODEL,
                tokenizer=QA_MODEL,
            )
            print("[QAPipeline] ✅ Model loaded.")
        except Exception as e:
            print(f"[QAPipeline] ❌ Failed to load model: {e}")
            self.qa = None

    # ── Public API ────────────────────────────────────────────────────────────
    def answer_question(self, question: str, context: str) -> dict:
        """
        Answer a question given a context (Wikipedia article text).

        Returns:
            {
                "answer":     str,
                "score":      float,   # confidence 0–1
                "score_pct":  float,   # confidence as %
                "start":      int,
                "end":        int,
                "found":      bool,
            }
        """
        if self.qa is None:
            return {
                "answer":    "QA model is not loaded. Please check your installation.",
                "score":     0.0,
                "score_pct": 0.0,
                "start":     0,
                "end":       0,
                "found":     False,
            }

        if not context.strip():
            return {
                "answer":    "No article context available. Please search for a topic first.",
                "score":     0.0,
                "score_pct": 0.0,
                "start":     0,
                "end":       0,
                "found":     False,
            }

        # Chunk long contexts
        chunks = self._chunk_context(context)
        best   = None

        for chunk in chunks:
            try:
                result = self.qa(question=question, context=chunk)
                if best is None or result["score"] > best["score"]:
                    best = result
            except Exception as e:
                print(f"[QAPipeline] Warning: chunk failed: {e}")
                continue

        if best is None:
            return {
                "answer":    "Could not find an answer in the article.",
                "score":     0.0,
                "score_pct": 0.0,
                "start":     0,
                "end":       0,
                "found":     False,
            }

        return {
            "answer":    best["answer"].strip(),
            "score":     best["score"],
            "score_pct": round(best["score"] * 100, 1),
            "start":     best.get("start", 0),
            "end":       best.get("end", 0),
            "found":     best["score"] > 0.05,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _chunk_context(self, context: str) -> list:
        """Split long context into overlapping character chunks."""
        if len(context) <= MAX_CONTEXT_CHARS:
            return [context]

        chunks = []
        start  = 0
        while start < len(context):
            end = start + MAX_CONTEXT_CHARS
            chunks.append(context[start:end])
            if end >= len(context):
                break
            start = end - OVERLAP_CHARS
        return chunks


# ── Singleton ─────────────────────────────────────────────────────────────────
_qa_instance = None

def get_qa_pipeline() -> QAPipeline:
    global _qa_instance
    if _qa_instance is None:
        _qa_instance = QAPipeline()
    return _qa_instance
