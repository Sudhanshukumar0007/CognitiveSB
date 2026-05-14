# Contributing to CognitiveSB / ShadowByte

Thanks for your interest in contributing. This guide will get you set up and making your first PR in under 15 minutes.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Local Setup](#local-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Good First Issues](#good-first-issues)
- [PR Guidelines](#pr-guidelines)
- [Coding Conventions](#coding-conventions)
- [Communication](#communication)

---

## Project Overview

ShadowByte is an AI study companion that turns PDFs, DOCX files, TXT files, and YouTube transcripts into an interactive tutor. It uses a LangGraph RAG pipeline with FAISS vector search, streams responses via SSE, and persists all data in SQLite.

**Stack:** Python, Flask, LangChain, LangGraph, FAISS, Groq, React, TypeScript, SQLite

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 20.19+ or 22.12+
- A free [Groq API key](https://console.groq.com)

### Backend

```bash
git clone https://github.com/Sudhanshukumar0007/CognitiveSB.git
cd CognitiveSB

python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Windows
copy .env.sample .env

# Mac/Linux
cp .env.sample .env
# Edit .env and add your GROQ_API_KEY

python app.py
```

Backend runs on `http://localhost:5000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## Project Structure

```
CognitiveSB/
├── app.py                  # Flask entry point
├── db.py                   # SQLite persistence (sessions, SM-2, history)
├── agents/
│   ├── prompts.py          # LLM prompt templates per mode
│   └── rag_workflow.py     # LangGraph RAG pipeline
├── loaders/                # PDF, DOCX, TXT, YouTube loaders
├── processing/             # Chunker, embedder, graph extractor
├── retrieval/              # FAISS vector store wrapper
├── routes/                 # Flask API blueprints
├── llm/                    # Groq LLM wrapper
├── utils/                  # JSON helpers
└── frontend/
    └── src/
        ├── pages/          # Dashboard, StudyChat pages
        ├── components/ui/  # Chat, flashcards, quiz, notes, graph
        ├── hooks/          # useChat SSE hook
        ├── lib/            # API client
        └── styles/         # CSS design tokens
```

---

## How to Contribute

1. **Find an issue** — look for issues labeled `good-first-issue`
2. **Comment on the issue** — say you'd like to work on it so it gets assigned to you
3. **Fork the repo** and create a branch:
   ```bash
   git checkout -b fix/your-issue-name
   ```
4. **Make your changes** — keep commits small and focused
5. **Test your changes** — make sure the backend runs and the frontend builds
6. **Submit a PR** — fill out the PR template completely

---

## Good First Issues

If you're new to the project, start here:

| Label | Area | Example Tasks |
|---|---|---|
| `good-first-issue` + `frontend` | React/TypeScript | Add theme toggle, improve loading skeletons |
| `good-first-issue` + `backend` | Flask/Python | Add PPTX loader, improve error messages |
| `good-first-issue` + `documentation` | Docs | Add docstrings, improve API docs |
| `good-first-issue` + `ai-ml` | RAG/LLM | Improve chunking strategy, add reranking |

---

## PR Guidelines

- **One PR per issue** — don't bundle multiple unrelated changes
- **Fill out the PR template** — incomplete PRs will be asked to resubmit
- **Keep PRs small** — under 300 lines of change is ideal
- **No breaking changes** without discussion in the issue first

- **Backend changes** — make sure `python app.py` still runs without errors
- **Frontend changes** — make sure `npm run build` passes without errors
- **Don't commit** `.env`, `vector_store/`, `uploads/`, `*.db` files — these are gitignored for a reason

---

## Coding Conventions

### Python
- Use Python 3.10+ syntax
- Use the existing Python 3.10 typing style (`dict[str, Any]`, `X | None`, etc.)
- Add docstrings to any new function you write
- Keep route handlers thin — business logic goes in the relevant module
- Follow existing patterns in `routes/` for new endpoints

### TypeScript / React
- Use functional components with hooks only
- Prefer CSS variables from `frontend/src/styles/tokens.css` for reusable colors; keep one-off hardcoded values scoped and consistent with the current design system
- Avoid adding new blur-heavy or glassmorphism effects unless the surrounding component already uses that visual style
- Keep components under 200 lines — split if larger
- Use `frontend/src/lib/api.ts` for backend calls shared by multiple components

### Git
- Branch naming: `fix/issue-name`, `feat/feature-name`, `docs/what-you-documented`
- Commit messages: `fix: correct flashcard SM-2 interval calculation` not `fixed stuff`

---

## Communication

- **GitHub Issues** — for bug reports, feature requests, and task discussion
- **GitHub Discussions** — for questions about the codebase or architecture
- **Discord** — `sudhanshu_007_87493` for quick questions

PR reviews will happen within **24-48 hours**. If you haven't heard back in 48 hours, ping in the issue thread.

---

## First time contributing to open source?

That's completely fine. Read [How to make your first open source contribution](https://opensource.guide/how-to-contribute/) and feel free to ask questions in GitHub Discussions. Everyone starts somewhere.
