---
title: Wikipedia QA API
emoji: 📖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# 📖 Wikipedia AI Research Assistant & QA Chatbot
### NLP Course Project

A unified, transformer-powered Wikipedia QA Chatbot and Research Workspace built with a decoupled modern stack:
- **Frontend**: A premium React, TypeScript, and TailwindCSS app utilizing TanStack Start / Router, authenticated with Supabase Auth.
- **Backend**: A high-performance Python FastAPI NLP engine running on Uvicorn that encapsulates intent classification, extractive QA, comparative summarization, and ROUGE evaluation.

---

## 🏗️ Decoupled Architecture

```mermaid
graph TD
    React[React Frontend: TanStack Start / Router] -->|User Auth| Supabase[Supabase Auth]
    React -->|POST /api/chat| FastAPI[FastAPI NLP Engine: Port 8000]
    React -->|POST /api/clear| FastAPI
    
    FastAPI -->|1. Detect Intent| DistilBERT[DistilBERT Intent Classifier]
    FastAPI -->|2. Fetch & Clean Article| MediaWiki[Wikipedia API]
    FastAPI -->|3. Extractive QA| RoBERTa[RoBERTa SQuAD2 Model]
    FastAPI -->|4. Summarize (BART vs T5)| Summarizers[facebook/bart-large-cnn & t5-small]
    FastAPI -->|5. Evaluate Quality| ROUGE[ROUGE Metric Scorer]
```

---

## 🤖 Models Used

| Model | Task | Size | Reference |
|---|---|---|---|
| `distilbert-base-uncased` | Intent detection (fine-tuned) | ~260MB | Fine-tuned on 150 training samples |
| `deepset/roberta-base-squad2` | Extractive Question Answering | ~480MB | For passage answering |
| `facebook/bart-large-cnn` | Comparative Summarization (Model 1) | ~1.6GB | Optimised cnn weights |
| `t5-small` | Comparative Summarization (Model 2) | ~240MB | Small text-to-text transformer |

---

## 📂 Project Directory Structures

### 1. Root Repository Structure
```text
Wikipedia-QA-Chatbot/
├── main_api.py             # FastAPI REST Server (Port 8000)
├── train_intent_model.py   # DistilBERT training / fine-tuning script
├── intent_detector.py      # Intent classifier pipeline wrapper
├── wikipedia_fetcher.py    # MediaWiki API integrations & text cleaner
├── qa_pipeline.py          # RoBERTa-based SQuAD2 question answering
├── summarizer.py           # BART vs T5 summarizers & ROUGE evaluator
├── session_manager.py      # In-memory FastAPI session states
├── requirements.txt        # Python backend library requirements
├── Dockerfile              # Hugging Face Spaces optimized Docker script
├── download_models.py      # Pre-caches transformer model weights on build
├── data/
│   └── intent_data.json    # 150 labeled training utterances
├── models/
│   └── intent_model/       # Saved fine-tuned DistilBERT weights
└── know-navigator-main/    # React frontend project folder
```

### 2. Frontend Reorganized Structure (`know-navigator-main/src/`)
Refactored into a scalable feature-organized layout:
```text
src/
├── auth/                   # Authentication widgets (AuthPage.tsx)
├── chat/                   # Composer and chat bubbles (ChatInput, MessageBubble, WelcomeHero, CitationCard)
├── account/                # Profile editing (SettingsPage.tsx view)
├── dashboard/              # Metrics visualizer (ResearchPanel.tsx)
├── sidebar/                # Dynamic workspace navigator (Sidebar.tsx)
├── services/               # Remote API & Supabase bridges
│   ├── api/                # FastAPI client middleware (chat.ts /clear & /chat adapter)
│   └── supabase/           # Client re-exports preserving Lovable toolchain integration
├── hooks/                  # Global hooks (useWikiChat.ts, useMobile.ts)
├── types/                  # Shared typings (chat.ts data schemas)
├── lib/                    # Standard utilities (utils.ts, error boundaries)
└── routes/                 # TanStack Router path mapping endpoints (index.tsx, settings.tsx)
```

---

## 🚀 Setup & Local Execution

> [!NOTE]
> Ensure you have Python 3.9+ and Node.js v18+ installed on your system.

### 1. Backend Service Setup
1. Navigate to the root directory and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Fine-tune the intent detector on the local JSON dataset (only needs to be run **once**):
   ```bash
   python train_intent_model.py
   ```
3. Start the FastAPI server on port 8000:
   ```bash
   python main_api.py
   ```
   *(On macOS platforms, imports of Keras/TF are bypassed using `USE_TF=0 USE_FLAX=0` configuration in-code to avoid exit code 134 crashes.)*

### 2. Frontend React Client Setup
1. Navigate to the client directory:
   ```bash
   cd know-navigator-main
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Add a `.env` file explicitly in `know-navigator-main/` mapping to your Supabase and backend URLs:
   ```env
   VITE_SUPABASE_PROJECT_ID="your_project_id"
   VITE_SUPABASE_PUBLISHABLE_KEY="your_anon_key"
   VITE_SUPABASE_URL="https://your_project_id.supabase.co"
   VITE_API_URL="http://localhost:8000/api"
   ```
4. Start the Vite client dev server (running on http://localhost:8080/):
   ```bash
   npm run dev
   ```

---

## 📝 NLP Functionality Overview

### 1. Intent Detection
Before fetching content, the engine classifies user input into 5 distinct intents:
- `greeting` ➜ Returns a conversational intro message.
- `topic_request` ➜ Connects to the Wikipedia API, downloads the page text, cleans annotations/HTML, and stores it in the active session.
- `question_answering` ➜ Runs extractive QA using RoBERTa on the cached Wikipedia page context.
- `summarization` ➜ Performs dual summarization using BART & T5, compiles evaluation metrics, and logs them.
- `farewell` ➜ Ends session and reports total metrics.

### 2. Comparative Summarization & ROUGE Scopes
When a user requests a summary (e.g. *"Summarize it"*):
- Both `facebook/bart-large-cnn` and `t5-small` are executed on the text context.
- ROUGE-1 (unigram overlap), ROUGE-2 (bigram overlap), and ROUGE-L (longest common subsequence) F1 scores are calculated against the Wikipedia article context.
- The summarizer logs a "ROUGE Winner" to the Research Dashboard.

---

## ☁️ Cloud Deployment Guide (100% Free)

### Deploy Backend to Hugging Face Spaces (Free CPU Basic)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Select **Docker** as the SDK, and choose the **Blank** template.
3. Push all backend files (including the fine-tuned `models/`, the `Dockerfile`, and `download_models.py` which pre-caches model weights) to the Space repository.
4. Hugging Face will build the Docker container and start your REST service on port 7860.
5. Copy your Space URL (e.g., `https://<user>-<space>.hf.space/api`).

### Deploy Frontend to Vercel (Free)
1. Push the `know-navigator-main/` directory to a GitHub repository.
2. Link the repository to your [Vercel](https://vercel.com/) dashboard.
3. Configure your Environment Variables (`VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, and `VITE_API_URL` pointing to your Hugging Face Space endpoint).
4. Click **Deploy**. Vercel will build and serve your premium React web interface live.
