# ShadowByte

> Most study tools let you read passively. ShadowByte forces active recall — upload your material and get a Socratic tutor, structured notes, auto-generated quizzes, spaced repetition flashcards, and an interactive knowledge graph, all powered by a RAG pipeline that actually understands your content.

![ShadowByte Demo](assets/demo.gif)

---

## Screenshots

| Dashboard | Study Chat |
|---|---|
| ![Dashboard](assets/dashboard.png) | ![Chat](assets/chat.png) |

| MCQ Quiz | Short Answer |
|---|---|
| ![Quiz](assets/quiz.png) | ![Short Answer](assets/short_answer.png) |

| Flashcards | Mind Map |
|---|---|
| ![Flashcards](assets/flashcards.png) | ![Mind Map](assets/mindmap.png) |

---

## What it does

Upload a PDF, DOCX, TXT, or YouTube URL. ShadowByte ingests it through a RAG pipeline and gives you:

- **4 chat modes** — Socratic (guides with questions), Feynman (you explain it to the AI), Simple (explain like I'm 12), Exam Prep (high-yield definitions and likely questions)
- **Structured notes** — key topics extracted with difficulty ratings, click any topic to go deeper
- **MCQ quiz** — auto-generated multiple choice with hints and difficulty tags
- **Short answer practice** — LLM-graded answers with specific feedback
- **Flashcards** — spaced repetition with SM-2 algorithm, tracks mastery across cards
- **Interactive mind map** — click any node to ask the AI about that specific concept

---

## Tech Stack

**Backend**
- Python, Flask, Flask-CORS
- LangChain, LangGraph
- Groq (LLM inference)
- HuggingFace sentence-transformers (embeddings)
- FAISS (vector store)
- YouTube Transcript API
- Celery + Redis (async task queue)

**Frontend**
- React 19, TypeScript, Vite
- Tailwind CSS, Framer Motion
- React Force Graph 2D (mind map)
- React Router, Lucide Icons, Sonner

---

## Architecture

```
Upload (PDF / DOCX / TXT / YouTube URL)
        ↓
  Loader Manager
        ↓
  Chunker → Embedder → FAISS Vector Store
        ↓
  Session Store (in-memory)
        ↓
  ┌─────────────────────────────────────┐
  │         LangGraph RAG Pipeline      │
  │  Retrieve → Rerank → Stream (Groq)  │
  └─────────────────────────────────────┘
        ↓
  Mode Prompts: Socratic / Feynman / Simple / Exam
        ↓
  SSE Streaming → React Frontend
```

```
.
├── app.py                  # Flask entry point
├── db.py                   # SQLite persistence layer (sessions, history, SM-2, progress)
├── agents/
│   ├── prompts.py          # All mode prompt templates
│   └── rag_workflow.py     # LangGraph RAG pipeline
├── loaders/                # PDF, DOCX, TXT, YouTube loaders
├── processing/             # Chunker, embedder, graph extractor
├── retrieval/              # FAISS vector store wrapper
├── routes/                 # Flask API blueprints
├── llm/                    # Groq LLM wrapper
├── utils/                  # JSON helpers
├── frontend/               # Vite + React app
│   └── src/
│       ├── pages/          # Dashboard, StudyChat
│       ├── components/ui/  # Chat, flashcards, quiz, notes, graph
│       ├── hooks/          # useChat (SSE streaming)
│       ├── lib/            # API client, utils
│       └── styles/         # Design tokens (flat dark)
├── celery_app.py           # Celery app factory
├── tasks.py                # Async task definitions (upload, graph, notes, flashcards)
├── uploads/                # Runtime — gitignored
└── vector_store/           # Runtime FAISS index — gitignored
```

---

## API

All routes under `/api`:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload file or YouTube URL |
| `GET` | `/api/chat` | Stream chat via SSE |
| `GET` | `/api/sessions` | List sessions |
| `DELETE` | `/api/sessions/<id>` | Delete session |
| `GET` | `/api/notes/<id>` | Get notes |
| `POST` | `/api/notes/generate/<id>` | Generate notes |
| `GET` | `/api/flashcards/<id>` | Get flashcards |
| `POST` | `/api/flashcards/generate/<id>` | Generate flashcards |
| `POST` | `/api/flashcards/rate` | Rate flashcard mastery |
| `GET` | `/api/quiz/<id>` | Get quiz |
| `POST` | `/api/quiz/generate/<id>` | Generate quiz |
| `POST` | `/api/quiz/grade` | LLM-grade short answer |
| `GET` | `/api/graph/<id>` | Get knowledge graph |
| `POST` | `/api/graph/generate/<id>` | Generate knowledge graph |
| `GET` | `/api/fact/<id>` | Get a study fact |
| `GET` | `/api/task/<task_id>` | Poll async task status |

---

## Setup

**1. Clone and set up backend**

```bash
git clone https://github.com/Sudhanshukumar0007/CognitiveSB.git
cd CognitiveSB

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

**2. Configure environment**

```bash
copy .env.sample .env         # Windows
cp .env.sample .env           # Mac/Linux
```

Edit `.env` and set:

```env
GROQ_API_KEY="your_groq_api_key"
REDIS_URL="redis://localhost:6379/0"
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

**3. Start Redis**

Using Docker (recommended):

```bash
docker run -d -p 6379:6379 --name redis-sb redis
```

Or install Redis natively on Windows from [github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)

**4. Set up frontend**

```bash
cd frontend
npm install
```

**5. Run**

```bash
# Terminal 1 — backend
python app.py

# Terminal 2 — Celery worker
celery -A celery_app.celery worker --loglevel=info --pool=solo

# Terminal 3 — frontend
cd frontend
npm run dev
```

Open your browser and go to `http://localhost:5173`

---

## Persistence & Data Layer

All session data is persisted to a local SQLite database (`shadowbyte.db`) via `db.py`:

- **Sessions** — stored with full extracted text and metadata, survive Flask restarts
- **Message history** — every chat message saved per session, last 6 loaded as context on each request
- **Spaced repetition** — SM-2 algorithm fully implemented in `card_schedule` table, tracking easiness factor, interval, repetitions, and next review date per card
- **Progress tracking** — quiz scores and flashcard mastery percentages tracked per session in a `progress` table
- **Cascade deletes** — deleting a session cleans up all related messages, progress, and card schedules

`vector_store/` and `uploads/` are created at runtime and gitignored.

---

## Built by

[Sudhanshu Kumar](https://github.com/Sudhanshukumar0007) — 2nd year CS student building AI systems.
Part of the larger **Aira** project — a modular AI OS connecting multiple specialized agents.

## ✨ README Improvement Notes

### 📌 Formatting Enhancements Needed
- Improve heading hierarchy for better readability
- Ensure consistent spacing between sections
- Use proper Markdown formatting for code blocks and lists
- Align all installation and usage steps properly

### 🚀 Suggested Structure Upgrade
- Introduction
- Features
- Tech Stack
- Installation
- Usage
- Project Structure
- Contribution Guidelines
- License

### 🛠️ Documentation Improvements
- Add badges (optional): build, license, contributors
- Add screenshots for better UI understanding
- Standardize code blocks for commands

### 🎯 Goal
Improve onboarding experience for new contributors and users by making README more structured, readable, and professional.

