import os
import time
from typing import Dict, List, Optional

# Disable TensorFlow and Flax backends to prevent SIGABRT crashes on macOS
os.environ["USE_TF"] = "0"
os.environ["USE_FLAX"] = "0"

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from session_manager import SessionManager
from intent_detector import get_detector
from wikipedia_fetcher import fetch_article
from qa_pipeline import get_qa_pipeline
from summarizer import get_summarizer

# Initialize FastAPI app
app = FastAPI(title="Wikipedia QA Chatbot API")

# Configure CORS
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
print("\n" + "=" * 60)
print("  Wikipedia QA Chatbot API — Loading Models")
print("=" * 60)

detector = get_detector()
qa = get_qa_pipeline()
summarizer = get_summarizer()

print("\n✅ All models loaded and API is ready.\n")

# In-memory session store
sessions: Dict[str, SessionManager] = {}

def get_session(session_id: str) -> SessionManager:
    if not session_id:
        session_id = "default"
    if session_id not in sessions:
        sessions[session_id] = SessionManager()
    return sessions[session_id]

# Response formatters identical to original app.py
def fmt_greeting() -> str:
    return (
        "👋 **Hello! I'm WikiQA Bot!**\n\n"
        "I can help you explore Wikipedia articles and answer your questions. Here's what I can do:\n\n"
        "- 🔍 **Search a topic** → *\"Tell me about Albert Einstein\"*\n"
        "- ❓ **Answer questions** → *\"When was he born?\"* (after searching a topic)\n"
        "- 📝 **Summarize articles** → *\"Summarize it\"* (after searching a topic)\n"
        "- 👋 **Farewell** → *\"Goodbye\"*\n\n"
        "What topic would you like to explore today?"
    )

def fmt_farewell(session: SessionManager) -> str:
    return (
        f"👋 **Goodbye! Thanks for using WikiQA Bot!**\n\n"
        f"**Session Summary:**\n"
        f"- 📰 Articles fetched: **{session.articles_fetched}**\n"
        f"- ❓ Questions answered: **{session.questions_asked}**\n"
        f"- 📝 Summaries generated: **{session.summaries_done}**\n\n"
        f"Feel free to come back anytime! 🌐"
    )

def fmt_article(article: dict) -> str:
    title = article.get("title", "Unknown")
    url = article.get("url", "")
    wc = article.get("word_count", 0)
    preview = article.get("preview", "")
    url_link = f"[View on Wikipedia]({url})" if url else ""
    wc_badge = f"`{wc:,} words`"
    return (
        f"✅ **Found: {title}** {wc_badge}  {url_link}\n\n"
        f"**Preview:**\n> {preview}\n\n"
        f"---\n"
        f"💡 **You can now:**\n"
        f"- Ask a question → *\"Who invented it?\"*\n"
        f"- Summarize → *\"Summarize it\"*"
    )

def fmt_qa(result: dict, question: str) -> str:
    if not result.get("found"):
        return (
            f"🔍 I couldn't find a confident answer to: *\"{question}\"*\n\n"
            f"Try rephrasing your question, or ask about a different aspect of the article."
        )
    answer = result.get("answer", "")
    score = result.get("score_pct", 0)
    indicator = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    return (
        f"📌 **Answer:**\n> {answer}\n\n"
        f"{indicator} **{score}%** · RoBERTa SQuAD2"
    )

def fmt_summarization(summary_data: dict) -> str:
    bart_sum = summary_data.get("bart_summary", "N/A")
    t5_sum = summary_data.get("t5_summary", "N/A")
    rouge = summary_data.get("rouge_scores", {})
    winner = summary_data.get("winner", "")
    bart_wc = summary_data.get("bart_word_count", 0)
    t5_wc = summary_data.get("t5_word_count", 0)
    bart_r = rouge.get("bart", {})
    t5_r = rouge.get("t5", {})

    winner_line = f"\n\n🏆 **Winner: {winner}** — based on average ROUGE score" if winner else ""

    return (
        f"📝 **Summaries Generated!** Comparing BART vs T5:\n\n"
        f"---\n"
        f"**🔵 BART Summary** `(facebook/bart-large-cnn)` · {bart_wc} words\n\n"
        f"{bart_sum}\n\n"
        f"---\n"
        f"**🟠 T5 Summary** `(t5-small)` · {t5_wc} words\n\n"
        f"{t5_sum}\n\n"
        f"---\n"
        f"**📊 ROUGE Evaluation:**\n\n"
        f"| Metric | BART | T5 |\n"
        f"|--------|------|----|\n"
        f"| ROUGE-1 | `{bart_r.get('rouge1', 0):.3f}` | `{t5_r.get('rouge1', 0):.3f}` |\n"
        f"| ROUGE-2 | `{bart_r.get('rouge2', 0):.3f}` | `{t5_r.get('rouge2', 0):.3f}` |\n"
        f"| ROUGE-L | `{bart_r.get('rougeL', 0):.3f}` | `{t5_r.get('rougeL', 0):.3f}` |"
        f"{winner_line}"
    )

def fmt_no_article() -> str:
    return (
        "⚠️ **No article loaded yet!**\n\n"
        "Please first search for a topic. Try:\n"
        "- *\"Tell me about Python\"*\n"
        "- *\"Search for Albert Einstein\"*\n"
        "- *\"What is machine learning\"*"
    )

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ClearRequest(BaseModel):
    session_id: str

def serialize_session(session: SessionManager) -> dict:
    return {
        "last_topic": session.last_topic,
        "last_article_title": session.last_article_title,
        "last_article_url": session.last_article_url,
        "last_article_word_count": session.last_article_word_count,
        "last_article_summary_preview": session.last_article_summary_preview,
        "last_intent": session.last_intent,
        "last_confidence": session.last_confidence,
        "bart_summary": session.bart_summary,
        "t5_summary": session.t5_summary,
        "rouge_scores": session.rouge_scores,
        "rouge_winner": session.rouge_winner,
        "questions_asked": session.questions_asked,
        "summaries_done": session.summaries_done,
        "articles_fetched": session.articles_fetched,
    }

@app.post("/api/chat")
async def chat(req: ChatRequest):
    start_time = time.time()
    session = get_session(req.session_id)
    message = req.message.strip()

    if not message:
        return {
            "message": {
                "role": "assistant",
                "content": "",
                "meta": {
                    "responseTimeMs": 0,
                    "sourcesUsed": 0,
                    "confidence": 0,
                    "citations": []
                }
            },
            "session_state": serialize_session(session)
        }

    # 1. Intent detection
    intent, confidence = detector.detect_intent(message)
    session.last_intent = intent
    session.last_confidence = confidence

    confidence_score = confidence / 100.0  # Normalize to 0-1
    sources_used = 0
    citations = []

    # 2. Route to handler
    if intent == "greeting":
        response = fmt_greeting()

    elif intent == "farewell":
        response = fmt_farewell(session)

    elif intent == "topic_request":
        # Extract topic (strip common request phrases)
        topic = message
        for phrase in [
            "tell me about", "search for", "look up", "find info on",
            "find information on", "what is", "what are", "i want to know about",
            "i'm curious about", "give me information on", "search wikipedia for",
            "what does wikipedia say about", "i want to learn about", "can you look up",
        ]:
            if topic.lower().startswith(phrase):
                topic = topic[len(phrase):].strip()
                break

        if not topic:
            response = "Please specify a topic to search! Example: *\"Tell me about Python\"*"
        else:
            article = fetch_article(topic)
            if article.get("error"):
                response = f"❌ **Error:** {article['error']}\n\nPlease try a different search term."
            else:
                session.update_article(article)
                # Clear stale summaries
                session.bart_summary = ""
                session.t5_summary = ""
                session.rouge_scores = {}
                session.rouge_winner = ""
                response = fmt_article(article)
                
                # Add Wikipedia citation
                sources_used = 1
                citations.append({
                    "title": article["title"],
                    "description": article["preview"],
                    "url": article["url"]
                })
                confidence_score = 1.0  # High confidence since article fetched successfully

    elif intent == "question_answering":
        if not session.has_article():
            response = fmt_no_article()
        else:
            result = qa.answer_question(message, session.last_article_text)
            session.questions_asked += 1
            response = fmt_qa(result, message)
            
            # Confidence from RoBERTa QA score
            confidence_score = result.get("score", 0.0)
            
            # Citation of original article
            sources_used = 1
            citations.append({
                "title": session.last_article_title,
                "description": session.last_article_summary_preview,
                "url": session.last_article_url
            })

    elif intent == "summarization":
        if not session.has_article():
            response = fmt_no_article()
        else:
            summary_data = summarizer.generate_summaries(session.last_article_text)
            session.update_summaries(summary_data)
            response = fmt_summarization(summary_data)
            
            # Summaries are high confidence processes
            confidence_score = 0.95
            
            # Citation of original article
            sources_used = 1
            citations.append({
                "title": session.last_article_title,
                "description": session.last_article_summary_preview,
                "url": session.last_article_url
            })
    else:
        response = fmt_no_article()

    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)

    # Return message and session states
    return {
        "message": {
            "role": "assistant",
            "content": response,
            "meta": {
                "responseTimeMs": response_time_ms,
                "sourcesUsed": sources_used,
                "confidence": confidence_score,
                "citations": citations
            }
        },
        "session_state": serialize_session(session)
    }

@app.post("/api/clear")
async def clear_session(req: ClearRequest):
    session = get_session(req.session_id)
    session.reset()
    return serialize_session(session)

if __name__ == "__main__":
    import uvicorn
    # Run server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
