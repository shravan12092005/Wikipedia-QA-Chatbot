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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; font-family: 'Inter', sans-serif !important; }

body, .gradio-container {
    background: #0c0e1a !important;
    color: #e2e8f0 !important;
}

footer { display: none !important; }
.gr-examples { display: none !important; }
.gr-button-secondary { display: none !important; }
.message-avatar img { width: 28px !important; height: 28px !important; }

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #10121f;
    border: 1px solid #1c2040;
    border-radius: 14px;
    padding: 14px 22px;
    margin-bottom: 16px;
}
.topbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-icon {
    width: 36px; height: 36px;
    background: #3c3489;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.topbar-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ede9fe;
    margin: 0;
    line-height: 1.2;
}
.topbar-subtitle {
    font-size: 0.72rem;
    color: #6b7280;
    margin: 0;
    line-height: 1.2;
}
.topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.status-pill {
    background: #064e3b;
    color: #34d399;
    border: 1px solid #065f46;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-weight: 600;
}

/* ── Sidebar / Panel cards ── */
.sidebar-card {
    background: #10121f;
    border: 1px solid #1c2040;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.card-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
}

/* ── Topic card ── */
.topic-chip {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #c4b5fd;
    line-height: 1.3;
}
.topic-dot {
    width: 8px; height: 8px;
    background: #534AB7;
    border-radius: 50%;
    flex-shrink: 0;
}
.topic-wc {
    font-size: 0.72rem;
    color: #6b7280;
    margin-top: 5px;
    padding-left: 15px;
}
.topic-link {
    display: block;
    color: #7c6ff7;
    text-decoration: none;
    font-size: 0.72rem;
    margin-top: 6px;
    padding-left: 15px;
}
.topic-link:hover { color: #a5b4fc; }

/* ── Intent card ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-greeting          { background: rgba(99,102,241,0.18);  color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
.badge-topic_request     { background: rgba(83,74,183,0.2);    color: #c4b5fd; border: 1px solid rgba(83,74,183,0.35); }
.badge-question_answering{ background: rgba(83,74,183,0.2);    color: #c4b5fd; border: 1px solid rgba(83,74,183,0.35); }
.badge-summarization     { background: rgba(16,185,129,0.15);  color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.badge-farewell          { background: rgba(107,114,128,0.15); color: #9ca3af; border: 1px solid rgba(107,114,128,0.3); }
.badge-default           { background: rgba(107,114,128,0.1);  color: #6b7280; border: 1px solid rgba(107,114,128,0.2); }

.conf-label-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 4px;
}
.conf-label { font-size: 0.7rem; color: #6b7280; }
.conf-pct   { font-size: 0.7rem; font-weight: 700; color: #a5b4fc; }
.conf-track {
    width: 100%;
    height: 4px;
    background: #0c0e1a;
    border-radius: 4px;
    overflow: hidden;
}
.conf-fill {
    height: 4px;
    background: #534AB7;
    border-radius: 4px;
    transition: width 0.4s ease;
}

/* ── Stats grid ── */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.stat-box {
    background: #0c0e1a;
    border-radius: 8px;
    padding: 10px 10px 8px 10px;
    text-align: center;
}
.stat-num {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #374151;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

/* ── Clear button ── */
.clear-btn {
    width: 100%;
    background: #0c0e1a !important;
    color: #6b7280 !important;
    border: 1px solid #1c2040 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 10px !important;
    cursor: pointer;
    transition: all 0.2s;
}
.clear-btn:hover {
    background: #10121f !important;
    color: #e2e8f0 !important;
    border-color: #3c3489 !important;
}

/* ── Chatbot ── */
#chatbot {
    background: #0f111e !important;
    border: 1px solid #1c2040 !important;
    border-radius: 14px !important;
    min-height: 480px;
}
#chatbot .message.user {
    background: #3c3489 !important;
    color: #ede9fe !important;
    border-radius: 14px 14px 4px 14px !important;
    font-size: 0.88rem;
}
#chatbot .message.bot {
    background: #13172b !important;
    color: #d1d5db !important;
    border: 1px solid #1c2040 !important;
    border-radius: 4px 14px 14px 14px !important;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── Input ── */
#user-input textarea {
    background: #13172b !important;
    border: 1px solid #1c2040 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
    resize: none;
}
#user-input textarea:focus {
    border-color: #534AB7 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(83,74,183,0.2) !important;
}
#send-btn {
    background: #3c3489 !important;
    color: #ede9fe !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    height: 44px !important;
    padding: 0 22px !important;
    transition: all 0.2s !important;
}
#send-btn:hover {
    background: #534AB7 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(83,74,183,0.35) !important;
}

/* ── Quick pick chips ── */
.chips-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 10px;
}
.chip {
    background: #13172b;
    border: 1px solid #1c2040;
    color: #6b7280;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.18s;
    user-select: none;
}
.chip:hover {
    background: #1c2040;
    color: #a5b4fc;
    border-color: #3730a3;
}

/* ── ROUGE right panel ── */
.rouge-panel {
    background: #0a1a12;
    border: 1px solid #064e3b;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.rouge-panel .card-label { color: #065f46; }
.rouge-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
    margin-top: 4px;
}
.rouge-table th {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 4px 0;
    border-bottom: 1px solid #064e3b;
}
.rouge-table th:first-child { text-align: left; color: #6b7280; }
.rouge-table th.col-bart { text-align: right; color: #60a5fa; }
.rouge-table th.col-t5   { text-align: right; color: #fb923c; }
.rouge-table td { padding: 5px 0; border-bottom: 1px solid #0d2a1c; }
.rouge-table td:first-child { color: #9ca3af; }
.rouge-table td.val-bart { text-align: right; color: #60a5fa; font-weight: 700; }
.rouge-table td.val-t5   { text-align: right; color: #fb923c; font-weight: 700; }
.rouge-table tr:last-child td { border-bottom: none; }
.rouge-avg-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}
.rouge-avg-label { font-size: 0.72rem; color: #6b7280; }
.winner-pill {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    color: #34d399;
    border: 1px solid #065f46;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-weight: 700;
}

/* ── Model info card ── */
.model-row {
    padding: 7px 0;
    border-bottom: 1px solid #1c2040;
}
.model-row:last-child { border-bottom: none; }
.model-name {
    font-family: 'Courier New', monospace !important;
    font-size: 0.75rem;
    color: #c4b5fd;
    font-weight: 600;
}
.model-role {
    font-size: 0.68rem;
    color: #4b5563;
    margin-top: 2px;
}

/* ── How to use card ── */
.how-step {
    display: flex;
    gap: 8px;
    padding: 4px 0;
    font-size: 0.75rem;
    color: #6b7280;
}
.how-step-num {
    font-weight: 700;
    color: #534AB7;
    flex-shrink: 0;
    width: 14px;
}

/* ── Summary cards ── */
.summary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 12px;
}
.sum-card-bart {
    background: rgba(14,165,233,0.06);
    border: 1px solid #0ea5e9;
    border-radius: 12px;
    padding: 12px;
}
.sum-card-t5 {
    background: rgba(251,146,60,0.06);
    border: 1px solid #fb923c;
    border-radius: 12px;
    padding: 12px;
}
.sum-card-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.sum-card-bart .sum-card-title { color: #7dd3fc; }
.sum-card-t5   .sum-card-title { color: #fdba74; }
.sum-card-body {
    font-size: 0.8rem;
    color: #cbd5e1;
    line-height: 1.55;
}
"""

# ── HTML Render Helpers ───────────────────────────────────────────────────────

TOP_BAR_HTML = """
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-icon">📖</div>
    <div>
      <p class="topbar-title">WikiQA Bot</p>
      <p class="topbar-subtitle">NLP Course Project — Practical 08 + 09</p>
    </div>
  </div>
  <div class="topbar-pills">
    <span class="status-pill">● BERT Ready</span>
    <span class="status-pill">● BART Ready</span>
    <span class="status-pill">● T5 Ready</span>
  </div>
</div>
"""

CHIPS_HTML = """
<div class="chips-row">
  <span class="chip" onclick="(function(){var t=document.querySelector('#user-input textarea');if(t){t.value='Hello!';t.dispatchEvent(new Event('input',{bubbles:true}));}})()">Hello!</span>
  <span class="chip" onclick="(function(){var t=document.querySelector('#user-input textarea');if(t){t.value='Tell me about Einstein';t.dispatchEvent(new Event('input',{bubbles:true}));}})()">Tell me about Einstein</span>
  <span class="chip" onclick="(function(){var t=document.querySelector('#user-input textarea');if(t){t.value='When was he born?';t.dispatchEvent(new Event('input',{bubbles:true}));}})()">When was he born?</span>
  <span class="chip" onclick="(function(){var t=document.querySelector('#user-input textarea');if(t){t.value='Summarize it';t.dispatchEvent(new Event('input',{bubbles:true}));}})()">Summarize it</span>
  <span class="chip" onclick="(function(){var t=document.querySelector('#user-input textarea');if(t){t.value='Goodbye!';t.dispatchEvent(new Event('input',{bubbles:true}));}})()">Goodbye!</span>
</div>
"""

MODEL_INFO_HTML = """
<div class="sidebar-card">
  <div class="card-label">Models Used</div>
  <div class="model-row">
    <div class="model-name">bert-base-uncased</div>
    <div class="model-role">Intent Detection</div>
  </div>
  <div class="model-row">
    <div class="model-name">roberta-base-squad2</div>
    <div class="model-role">Question Answering</div>
  </div>
  <div class="model-row">
    <div class="model-name">bart-large-cnn &amp; t5-small</div>
    <div class="model-role">Summarization</div>
  </div>
</div>
"""

HOW_TO_USE_HTML = """
<div class="sidebar-card">
  <div class="card-label">How to Use</div>
  <div class="how-step"><span class="how-step-num">1</span><span>Search: <em>"Tell me about Einstein"</em></span></div>
  <div class="how-step"><span class="how-step-num">2</span><span>Ask: <em>"When was he born?"</em></span></div>
  <div class="how-step"><span class="how-step-num">3</span><span>Summarize: <em>"Summarize it"</em></span></div>
  <div class="how-step"><span class="how-step-num">4</span><span>Bye: <em>"Goodbye"</em></span></div>
</div>
"""


def render_topic_card(title: str, url: str = "", word_count: int = 0) -> str:
    title_display = title if title else "—"
    dot = '<span class="topic-dot"></span>' if title else '<span class="topic-dot" style="background:#374151"></span>'
    wc_html = f'<div class="topic-wc">{word_count:,} words</div>' if word_count > 0 else ""
    link_html = f'<a class="topic-link" href="{url}" target="_blank">View on Wikipedia →</a>' if url else ""
    return f"""
<div class="sidebar-card">
  <div class="card-label">Current Topic</div>
  <div class="topic-chip">{dot}<span>{title_display}</span></div>
  {wc_html}
  {link_html}
</div>
"""


def render_intent_card(intent: str, confidence: float) -> str:
    badge_class = f"badge-{intent}" if intent not in ("—", "") else "badge-default"
    intent_display = intent.replace("_", " ").title() if intent not in ("—", "") else "—"
    conf_pct = confidence if confidence else 0
    fill_width = int(conf_pct)
    conf_display = f"{conf_pct:.0f}%" if conf_pct else "—"
    return f"""
<div class="sidebar-card">
  <div class="card-label">Intent Detected</div>
  <span class="badge {badge_class}">{intent_display}</span>
  <div class="conf-label-row">
    <span class="conf-label">Confidence</span>
    <span class="conf-pct">{conf_display}</span>
  </div>
  <div class="conf-track">
    <div class="conf-fill" style="width:{fill_width}%"></div>
  </div>
</div>
"""


def render_stats_card(questions: int, summaries: int, articles: int, avg_conf: float = 0.0) -> str:
    avg_display = f"{avg_conf:.0f}%" if avg_conf else "—"
    return f"""
<div class="sidebar-card">
  <div class="card-label">Session Stats</div>
  <div class="stats-grid">
    <div class="stat-box">
      <div class="stat-num">{articles}</div>
      <div class="stat-lbl">Articles Fetched</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">{questions}</div>
      <div class="stat-lbl">Questions Asked</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">{summaries}</div>
      <div class="stat-lbl">Summaries Done</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">{avg_display}</div>
      <div class="stat-lbl">Avg Confidence</div>
    </div>
  </div>
</div>
"""


def render_rouge_card(rouge_scores: dict, winner: str = "") -> str:
    if not rouge_scores:
        return """
<div class="rouge-panel">
  <div class="card-label">Rouge Scores</div>
  <div style="color:#4b5563;font-size:0.8rem;text-align:center;padding:16px 0">
    Summarize an article to see scores
  </div>
</div>
"""
    bart = rouge_scores.get("bart", {})
    t5   = rouge_scores.get("t5",   {})
    r1b  = bart.get("rouge1", 0); r2b = bart.get("rouge2", 0); rlb = bart.get("rougeL", 0)
    r1t  = t5.get("rouge1",   0); r2t = t5.get("rouge2",   0); rlt = t5.get("rougeL",  0)

    # Winner chip
    if winner == "Tie" or not winner:
        winner_chip = '<span class="winner-pill">Tie</span>'
    else:
        winner_chip = f'<span class="winner-pill">{winner} wins</span>'

    return f"""
<div class="rouge-panel">
  <div class="card-label">Rouge Scores</div>
  <table class="rouge-table">
    <thead>
      <tr>
        <th>Metric</th>
        <th class="col-bart">BART</th>
        <th class="col-t5">T5</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>ROUGE-1</td>
        <td class="val-bart">{r1b:.3f}</td>
        <td class="val-t5">{r1t:.3f}</td>
      </tr>
      <tr>
        <td>ROUGE-2</td>
        <td class="val-bart">{r2b:.3f}</td>
        <td class="val-t5">{r2t:.3f}</td>
      </tr>
      <tr>
        <td>ROUGE-L</td>
        <td class="val-bart">{rlb:.3f}</td>
        <td class="val-t5">{rlt:.3f}</td>
      </tr>
    </tbody>
  </table>
  <div class="rouge-avg-row">
    <span class="rouge-avg-label">Average score</span>
    {winner_chip}
  </div>
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
    score  = result.get("score_pct", 0)
    indicator = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    return (
        f"📌 **Answer:**\n> {answer}\n\n"
        f"{indicator} **{score}%** · RoBERTa SQuAD2"
    )

def fmt_summarization(summary_data: dict) -> str:
    bart_sum = summary_data.get("bart_summary", "N/A")
    t5_sum   = summary_data.get("t5_summary",   "N/A")
    rouge    = summary_data.get("rouge_scores", {})
    winner   = summary_data.get("winner", "")
    bart_wc  = summary_data.get("bart_word_count", 0)
    t5_wc    = summary_data.get("t5_word_count",   0)
    bart_r   = rouge.get("bart", {})
    t5_r     = rouge.get("t5",   {})

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
        f"|--------|------|----||\n"
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

        # ── Top bar (full width) ───────────────────────────────────────────
        gr.HTML(TOP_BAR_HTML)

        # ── 3-column layout ────────────────────────────────────────────────
        with gr.Row(equal_height=False):

            # ===== LEFT SIDEBAR =====
            with gr.Column(scale=1, min_width=230, elem_id="sidebar"):
                topic_display  = gr.HTML(render_topic_card(""))
                intent_display = gr.HTML(render_intent_card("—", 0))
                stats_display  = gr.HTML(render_stats_card(0, 0, 0))
                clear_btn = gr.Button("🗑️  Clear Chat", elem_classes=["clear-btn"])

            # ===== MAIN CHAT AREA =====
            with gr.Column(scale=3, elem_id="main-area"):
                chatbot = gr.Chatbot(
                    value=[],
                    elem_id="chatbot",
                    height=480,
                    show_label=False,
                    avatar_images=(
                        None,
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/103px-Wikipedia-logo-v2.svg.png",
                    ),
                )
                # Quick-pick chips
                gr.HTML(CHIPS_HTML)
                # Input row
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder='Try: "Tell me about Albert Einstein" or "Summarize it"',
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        elem_id="user-input",
                        scale=5,
                    )
                    send_btn = gr.Button("Send ➤", elem_id="send-btn", scale=1, min_width=90)

            # ===== RIGHT PANEL =====
            with gr.Column(scale=1, min_width=220, elem_id="right-panel"):
                rouge_display = gr.HTML(render_rouge_card({}))
                gr.HTML(MODEL_INFO_HTML)
                gr.HTML(HOW_TO_USE_HTML)

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
