"""
app.py
------
Wikipedia QA Chatbot — Main Gradio Application
NLP Course Project: Practical 08 (Chatbot + Intent Detection) + Practical 09 (Summarization + ROUGE)

Run:
    python app.py
"""

import gradio as gr
from session_manager import SessionManager
from intent_detector import get_detector
from wikipedia_fetcher import fetch_article
from qa_pipeline import get_qa_pipeline
from summarizer import get_summarizer

# ── Load models at startup ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Wikipedia QA Chatbot — Model Loading")
print("=" * 60)

detector   = get_detector()
qa         = get_qa_pipeline()
summarizer = get_summarizer()

print("\n✅ All models ready. Launching Gradio...\n")

# ── Custom CSS ────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { box-sizing: border-box; font-family: 'Inter', sans-serif !important; }

body, .gradio-container {
    background: #0b0d17 !important;
    color: #e2e8f0 !important;
}

/* ── Header ── */
.wikiqa-header {
    background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 50%, #0ea5e9 100%);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 16px;
    text-align: center;
}
.wikiqa-header h1 {
    font-size: 1.9rem;
    font-weight: 800;
    color: #fff;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}
.wikiqa-header p {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.8);
    margin: 0;
    font-weight: 400;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Sidebar cards ── */
.sidebar-card {
    background: #141625;
    border: 1px solid #1e2235;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.sidebar-logo {
    text-align: center;
    padding: 18px 0 14px 0;
}
.sidebar-logo .wiki-icon {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #6d28d9, #4f46e5);
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    margin-bottom: 8px;
}
.sidebar-logo h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
}
.sidebar-logo p {
    font-size: 0.72rem;
    color: #6b7280;
    margin: 2px 0 0 0;
    letter-spacing: 0.5px;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.topic-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #c4b5fd;
}
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-greeting        { background: rgba(99,102,241,0.2);  color: #a5b4fc; }
.badge-topic_request   { background: rgba(139,92,246,0.2);  color: #c4b5fd; }
.badge-question_answering { background: rgba(14,165,233,0.2); color: #7dd3fc; }
.badge-summarization   { background: rgba(16,185,129,0.2);  color: #6ee7b7; }
.badge-farewell        { background: rgba(245,158,11,0.2);  color: #fcd34d; }
.badge-default         { background: rgba(107,114,128,0.2); color: #9ca3af; }

.confidence-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
}
.confidence-bar-track {
    flex: 1;
    background: #1e2235;
    border-radius: 4px;
    height: 6px;
    margin: 0 10px;
    overflow: hidden;
}
.confidence-bar-fill {
    height: 6px;
    border-radius: 4px;
    background: linear-gradient(90deg, #6d28d9, #0ea5e9);
    transition: width 0.4s ease;
}
.confidence-pct {
    font-size: 0.78rem;
    font-weight: 700;
    color: #a5b4fc;
    min-width: 38px;
    text-align: right;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    font-size: 0.8rem;
    color: #9ca3af;
    border-bottom: 1px solid #1e2235;
}
.stat-row:last-child { border-bottom: none; }
.stat-row span:last-child {
    font-weight: 700;
    color: #e2e8f0;
}

.rouge-card {
    background: #141625;
    border: 1px solid #065f46;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.rouge-card .card-label { color: #34d399; }
.rouge-metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    font-size: 0.78rem;
    border-bottom: 1px solid #1e2235;
}
.rouge-metric-row:last-child { border-bottom: none; }
.rouge-label { color: #9ca3af; font-weight: 500; }
.rouge-val-bart { color: #60a5fa; font-weight: 700; }
.rouge-val-t5   { color: #fb923c; font-weight: 700; }
.winner-badge {
    display: inline-block;
    background: rgba(16,185,129,0.2);
    color: #34d399;
    border: 1px solid #065f46;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 10px;
}

.clear-btn {
    width: 100%;
    background: #1e2235 !important;
    color: #9ca3af !important;
    border: 1px solid #2d3148 !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 10px !important;
    cursor: pointer;
    transition: all 0.2s;
}
.clear-btn:hover {
    background: #272a40 !important;
    color: #e2e8f0 !important;
    border-color: #3d4265 !important;
}

/* ── Chatbot ── */
#chatbot {
    background: #0f111e !important;
    border: 1px solid #1e2235 !important;
    border-radius: 16px !important;
    min-height: 460px;
}
#chatbot .message.bot {
    background: #141625 !important;
    border: 1px solid #1e2235 !important;
    border-radius: 14px 14px 14px 4px !important;
    color: #e2e8f0 !important;
    font-size: 0.88rem;
    line-height: 1.6;
}
#chatbot .message.user {
    background: linear-gradient(135deg, #6d28d9, #4f46e5) !important;
    border-radius: 14px 14px 4px 14px !important;
    color: #fff !important;
    font-size: 0.88rem;
}
#chatbot .message.bot .summary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 12px;
}
.sum-card-bart {
    background: rgba(14,165,233,0.07);
    border: 1px solid #0ea5e9;
    border-radius: 12px;
    padding: 12px;
}
.sum-card-t5 {
    background: rgba(251,146,60,0.07);
    border: 1px solid #fb923c;
    border-radius: 12px;
    padding: 12px;
}
.sum-card-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.sum-card-bart .sum-card-title { color: #7dd3fc; }
.sum-card-t5   .sum-card-title { color: #fdba74; }
.sum-card-body {
    font-size: 0.82rem;
    color: #cbd5e1;
    line-height: 1.55;
}

/* ── Input ── */
#user-input textarea {
    background: #141625 !important;
    border: 1px solid #2d3148 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
    resize: none;
}
#user-input textarea:focus {
    border-color: #6d28d9 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(109,40,217,0.2) !important;
}
#send-btn {
    background: linear-gradient(135deg, #6d28d9, #4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    height: 44px !important;
    padding: 0 24px !important;
    transition: all 0.2s !important;
}
#send-btn:hover {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(109,40,217,0.4) !important;
}

.divider { border: none; border-top: 1px solid #1e2235; margin: 10px 0; }
"""

# ── HTML Render Helpers ───────────────────────────────────────────────────────
LOGO_HTML = """
<div class="sidebar-logo">
  <div class="wiki-icon">📖</div>
  <h2>WikiQA Bot</h2>
  <p>NLP Course Project</p>
</div>
"""

def render_topic_card(title: str, url: str = "", word_count: int = 0) -> str:
    title_display = title if title else "—"
    wc_text = f"<span style='font-size:0.72rem;color:#6b7280;display:block;margin-top:4px'>{word_count:,} words</span>" if word_count > 0 else ""
    link = f"<a href='{url}' target='_blank' style='color:#6366f1;text-decoration:none;font-size:0.7rem'>🔗 View on Wikipedia</a>" if url else ""
    return f"""
<div class="sidebar-card">
  <div class="card-label">📄 Current Topic</div>
  <div class="topic-chip">🌐 {title_display}</div>
  {wc_text}
  {link}
</div>
"""

def render_intent_card(intent: str, confidence: float) -> str:
    badge_class = f"badge-{intent}" if intent != "—" else "badge-default"
    intent_display = intent.replace("_", " ").title() if intent != "—" else "—"
    conf_pct = confidence if confidence else 0
    fill_width = int(conf_pct)
    conf_display = f"{conf_pct}%" if conf_pct else "—"
    return f"""
<div class="sidebar-card">
  <div class="card-label">🧠 Intent Detected</div>
  <span class="badge {badge_class}">{intent_display}</span>
  <div class="confidence-row" style="margin-top:10px">
    <span style="font-size:0.72rem;color:#6b7280">Confidence</span>
    <div class="confidence-bar-track">
      <div class="confidence-bar-fill" style="width:{fill_width}%"></div>
    </div>
    <span class="confidence-pct">{conf_display}</span>
  </div>
</div>
"""

def render_stats_card(questions: int, summaries: int, articles: int) -> str:
    return f"""
<div class="sidebar-card">
  <div class="card-label">📊 Session Stats</div>
  <div class="stat-row"><span>📰 Articles Fetched</span><span>{articles}</span></div>
  <div class="stat-row"><span>❓ Questions Asked</span><span>{questions}</span></div>
  <div class="stat-row"><span>📝 Summaries Done</span><span>{summaries}</span></div>
</div>
"""

def render_rouge_card(rouge_scores: dict, winner: str = "") -> str:
    if not rouge_scores:
        return """
<div class="rouge-card">
  <div class="card-label">📈 ROUGE Scores</div>
  <div style="color:#6b7280;font-size:0.8rem;text-align:center;padding:12px 0">
    Summarize an article to see scores
  </div>
</div>
"""
    bart = rouge_scores.get("bart", {})
    t5   = rouge_scores.get("t5",   {})
    r1b  = bart.get("rouge1", 0)
    r2b  = bart.get("rouge2", 0)
    rlb  = bart.get("rougeL", 0)
    r1t  = t5.get("rouge1", 0)
    r2t  = t5.get("rouge2", 0)
    rlt  = t5.get("rougeL", 0)
    winner_html = f'<div class="winner-badge">🏆 {winner} Wins</div>' if winner and winner != "Tie" else '<div class="winner-badge">🤝 Tie</div>'
    return f"""
<div class="rouge-card">
  <div class="card-label">📈 ROUGE Scores</div>
  <div style="display:flex;justify-content:flex-end;gap:16px;margin-bottom:6px">
    <span style="font-size:0.7rem;font-weight:700;color:#60a5fa">BART</span>
    <span style="font-size:0.7rem;font-weight:700;color:#fb923c">T5</span>
  </div>
  <div class="rouge-metric-row">
    <span class="rouge-label">ROUGE-1</span>
    <span>
      <span class="rouge-val-bart">{r1b:.3f}</span>
      <span style="color:#4b5563;margin:0 4px">|</span>
      <span class="rouge-val-t5">{r1t:.3f}</span>
    </span>
  </div>
  <div class="rouge-metric-row">
    <span class="rouge-label">ROUGE-2</span>
    <span>
      <span class="rouge-val-bart">{r2b:.3f}</span>
      <span style="color:#4b5563;margin:0 4px">|</span>
      <span class="rouge-val-t5">{r2t:.3f}</span>
    </span>
  </div>
  <div class="rouge-metric-row">
    <span class="rouge-label">ROUGE-L</span>
    <span>
      <span class="rouge-val-bart">{rlb:.3f}</span>
      <span style="color:#4b5563;margin:0 4px">|</span>
      <span class="rouge-val-t5">{rlt:.3f}</span>
    </span>
  </div>
  {winner_html}
</div>
"""

# ── Response Formatters ────────────────────────────────────────────────────────
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
    title    = article.get("title", "Unknown")
    url      = article.get("url", "")
    wc       = article.get("word_count", 0)
    preview  = article.get("preview", "")
    url_link = f"[View on Wikipedia]({url})" if url else ""
    return (
        f"✅ **Found: {title}** {url_link}\n\n"
        f"📊 *Article has {wc:,} words*\n\n"
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
    answer   = result.get("answer", "")
    score    = result.get("score_pct", 0)
    bar_fill = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    return (
        f"📌 **Answer:** {answer}\n\n"
        f"{bar_fill} **Confidence:** {score}%\n\n"
        f"*Source: {answer} — extracted from the loaded Wikipedia article*"
    )

def fmt_summarization(summary_data: dict) -> str:
    bart_sum = summary_data.get("bart_summary", "N/A")
    t5_sum   = summary_data.get("t5_summary", "N/A")
    rouge    = summary_data.get("rouge_scores", {})
    winner   = summary_data.get("winner", "")
    bart_wc  = summary_data.get("bart_word_count", 0)
    t5_wc    = summary_data.get("t5_word_count", 0)
    bart_r   = rouge.get("bart", {})
    t5_r     = rouge.get("t5", {})

    winner_line = f"\n\n🏆 **Winner: {winner}** — based on average ROUGE scores" if winner else ""

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
        f"| ROUGE-L | `{bart_r.get('rougeL', 0):.3f}` | `{t5_r.get('rougeL', 0):.3f}` |\n"
        f"| Words   | {bart_wc} | {t5_wc} |"
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

# ── Core Chat Handler ─────────────────────────────────────────────────────────
def chat_handler(message: str, history: list, session: SessionManager):
    """
    Main chat function. Detects intent and routes to the correct handler.
    Returns updated (history, topic_html, intent_html, stats_html, rouge_html, session, "")
    """
    if not message.strip():
        return history, \
               render_topic_card(session.last_article_title, session.last_article_url, session.last_article_word_count), \
               render_intent_card(session.last_intent, session.last_confidence), \
               render_stats_card(session.questions_asked, session.summaries_done, session.articles_fetched), \
               render_rouge_card(session.rouge_scores, session.rouge_winner), \
               session, ""

    # 1. Intent detection
    intent, confidence = detector.detect_intent(message)
    session.last_intent     = intent
    session.last_confidence = confidence

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
                session.t5_summary   = ""
                session.rouge_scores = {}
                session.rouge_winner = ""
                response = fmt_article(article)

    elif intent == "question_answering":
        if not session.has_article():
            response = fmt_no_article()
        else:
            result = qa.answer_question(message, session.last_article_text)
            session.questions_asked += 1
            response = fmt_qa(result, message)

    elif intent == "summarization":
        if not session.has_article():
            response = fmt_no_article()
        else:
            response = "⏳ **Generating summaries...** This may take 20–60 seconds for the first summarization.\n\n*Using BART (bart-large-cnn) and T5 (t5-small)...*"
            history.append((message, response))
            # Generate summaries
            summary_data = summarizer.generate_summaries(session.last_article_text)
            session.update_summaries(summary_data)
            # Replace the "generating" message with the real result
            history[-1] = (message, fmt_summarization(summary_data))
            # Update sidebar
            return (
                history,
                render_topic_card(session.last_article_title, session.last_article_url, session.last_article_word_count),
                render_intent_card(intent, confidence),
                render_stats_card(session.questions_asked, session.summaries_done, session.articles_fetched),
                render_rouge_card(session.rouge_scores, session.rouge_winner),
                session,
                "",
            )
    else:
        response = fmt_no_article()

    history.append((message, response))

    return (
        history,
        render_topic_card(session.last_article_title, session.last_article_url, session.last_article_word_count),
        render_intent_card(intent, confidence),
        render_stats_card(session.questions_asked, session.summaries_done, session.articles_fetched),
        render_rouge_card(session.rouge_scores, session.rouge_winner),
        session,
        "",
    )


def clear_chat(session: SessionManager):
    """Reset the chat and session state."""
    session.reset()
    empty_history = []
    return (
        empty_history,
        render_topic_card(""),
        render_intent_card("—", 0),
        render_stats_card(0, 0, 0),
        render_rouge_card({}),
        session,
        "",
    )


# ── Gradio UI ─────────────────────────────────────────────────────────────────
def build_ui():
    with gr.Blocks(title="WikiQA Bot — NLP Course Project", css=CUSTOM_CSS) as demo:
        # ── State ──────────────────────────────────────────────────────────
        session_state = gr.State(SessionManager())

        # ── Layout ─────────────────────────────────────────────────────────
        with gr.Row(equal_height=False):

            # ===== SIDEBAR =====
            with gr.Column(scale=1, min_width=270, elem_id="sidebar"):
                gr.HTML(LOGO_HTML)
                topic_display  = gr.HTML(render_topic_card(""))
                intent_display = gr.HTML(render_intent_card("—", 0))
                gr.HTML('<hr class="divider">')
                stats_display  = gr.HTML(render_stats_card(0, 0, 0))
                rouge_display  = gr.HTML(render_rouge_card({}))
                clear_btn = gr.Button("🗑️ Clear Chat", elem_classes=["clear-btn"])

            # ===== MAIN CHAT AREA =====
            with gr.Column(scale=3, elem_id="main-area"):
                gr.HTML("""
<div class="wikiqa-header">
  <h1>📖 Wikipedia QA Chatbot</h1>
  <p>NLP Course Project</p>
</div>
""")
                chatbot = gr.Chatbot(
                    value=[],
                    elem_id="chatbot",
                    height=480,
                    show_label=False,
                    avatar_images=(None, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/103px-Wikipedia-logo-v2.svg.png"),
                )
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder='Try: "Tell me about Albert Einstein" or "Summarize it" or "When was he born?"',
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        elem_id="user-input",
                        scale=5,
                    )
                    send_btn = gr.Button("Send ➤", elem_id="send-btn", scale=1, min_width=90)

                # Example prompts
                gr.Examples(
                    examples=[
                        ["Hello!"],
                        ["Tell me about Albert Einstein"],
                        ["When was Einstein born?"],
                        ["Where was he born?"],
                        ["Summarize it"],
                        ["Tell me about Machine Learning"],
                        ["What is deep learning?"],
                        ["Summarize it"],
                        ["Goodbye, thanks!"],
                    ],
                    inputs=user_input,
                    label="💡 Try these examples",
                )

        # ── Events ─────────────────────────────────────────────────────────
        outputs = [
            chatbot, topic_display, intent_display,
            stats_display, rouge_display,
            session_state, user_input,
        ]

        send_btn.click(
            fn=chat_handler,
            inputs=[user_input, chatbot, session_state],
            outputs=outputs,
            api_name=False,
        )
        user_input.submit(
            fn=chat_handler,
            inputs=[user_input, chatbot, session_state],
            outputs=outputs,
            api_name=False,
        )
        clear_btn.click(
            fn=clear_chat,
            inputs=[session_state],
            outputs=outputs,
            api_name=False,
        )

    return demo


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        inbrowser=False,
        show_error=True,
    )
    print("\n🌐 App running at: http://localhost:7861")
