# 📖 Wikipedia QA Chatbot
### NLP Course Project 

A unified, transformer-powered Wikipedia QA Chatbot that combines:
- **1** — Chatbot / QA System with BERT-based intent detection
- **2** — Text Summarization using HuggingFace (BART + T5) with ROUGE evaluation

---

## 🏗️ Architecture

```
User Message
     ↓
Intent Detection (DistilBERT — 5 intent classes)
     ↓
┌────────────────────────────────────────────────────┐
│ greeting        → Friendly welcome response        │
│ topic_request   → Wikipedia API fetch + clean      │
│ question_ans.   → RoBERTa-SQuAD2 QA pipeline       │
│ summarization   → BART-Large + T5-Small + ROUGE    │
│ farewell        → Goodbye + session stats          │
└────────────────────────────────────────────────────┘
     ↓
Gradio Web Interface (dark-themed, sidebar + chat)
```

---

## 🤖 Models Used

| Model | Task | Size |
|---|---|---|
| `distilbert-base-uncased` | Intent detection (fine-tuned) | 260MB |
| `deepset/roberta-base-squad2` | Question Answering | 480MB |
| `facebook/bart-large-cnn` | Summarization (Model 1) | 1.6GB |
| `t5-small` | Summarization (Model 2) | 240MB |

---

## 📦 Setup

### 1. Install Dependencies
```bash
cd "Wikipedia QA Chatbot"
pip install -r requirements.txt
```

### 2. Train the Intent Classifier (run ONCE)
```bash
python train_intent_model.py
```
- Fine-tunes `distilbert-base-uncased` on 150 labeled utterances
- Trains for up to 12 epochs with early stopping
- Saves model to `models/intent_model/`
- Takes ~2–5 minutes on CPU

### 3. Launch the App
```bash
python app.py
```
Open your browser at: **http://localhost:7860**

---

## 💬 Supported Intents (P08)

| Intent | Example Utterances |
|---|---|
| `greeting` | "Hello!", "Hi there", "Good morning" |
| `topic_request` | "Tell me about Einstein", "Search for Python" |
| `question_answering` | "Who invented it?", "When was he born?" |
| `summarization` | "Summarize it", "TL;DR please", "Give me a summary" |
| `farewell` | "Goodbye", "Thanks", "Bye!" |

---

## 📝 Summarization & ROUGE (P09)

The summarization pipeline:
1. **Fetches** Wikipedia article and **cleans** text (strip HTML, citations, whitespace)
2. **BART** (`facebook/bart-large-cnn`) generates summary up to 250 words
3. **T5** (`t5-small`) generates summary with `"summarize: "` prefix
4. **ROUGE-1, ROUGE-2, ROUGE-L** F1 scores computed for both
5. **Winner** declared based on average ROUGE score

### Fine-tuning Strategy (P09-d)
Inference-time fine-tuning via generation hyperparameters:
- `num_beams=4` — beam search for quality
- `length_penalty=2.0` (BART) / `1.5` (T5) — encourages longer summaries
- `no_repeat_ngram_size=3` — reduces repetition
- `min_length=80` — ensures meaningful summaries

---

## 🗂️ Project Structure

```
Wikipedia QA Chatbot/
├── app.py                  # Main Gradio web application
├── train_intent_model.py   # DistilBERT fine-tuning script
├── intent_detector.py      # Intent inference wrapper
├── wikipedia_fetcher.py    # Wikipedia API + text cleaning
├── qa_pipeline.py          # RoBERTa QA pipeline
├── summarizer.py           # BART + T5 + ROUGE evaluation
├── session_manager.py      # Session state management
├── data/
│   └── intent_data.json    # 150 labeled training utterances
├── models/
│   └── intent_model/       # Saved fine-tuned DistilBERT
└── requirements.txt
```

---

## 🖥️ UI Features

- **Dark-themed** Gradio interface with glassmorphism cards
- **Left Sidebar**: Current topic, intent badge, confidence meter, session stats, ROUGE scores
- **Chat Area**: Conversation history, BART vs T5 comparison cards, QA answers with confidence
- **Example prompts** for quick testing
- **Clear Chat** button to reset session

---

## 📊 Sample ROUGE Output

```
| Metric  | BART  | T5    |
|---------|-------|-------|
| ROUGE-1 | 0.421 | 0.312 |
| ROUGE-2 | 0.213 | 0.141 |
| ROUGE-L | 0.384 | 0.281 |
| Winner  | 🏆 BART       |
```

---

## ⚙️ Requirements

- Python 3.9+
- ~3GB free disk space (for model downloads)
- Internet connection (first run only, for model downloads)
- 8GB RAM recommended

---

*NLP Course Project · Built with HuggingFace Transformers, Gradio, Wikipedia API*
