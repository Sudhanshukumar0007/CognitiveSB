# CognitiveSB / ShadowByte

ShadowByte is an AI study companion that turns uploaded study material or YouTube transcripts into a chat tutor, notes, quizzes, flashcards, and a knowledge graph.

The project has two main parts:

- A Flask backend that ingests documents, chunks and embeds them, stores them in FAISS, and calls Groq-hosted LLMs through LangChain.
- A Vite + React frontend that provides the dashboard, study chat, notes, quiz, flashcards, and graph views.

## Features

- Upload study files: PDF, TXT, DOCX, and PPTX.
- Import YouTube transcripts from normal YouTube or `youtu.be` URLs.
- Create study sessions from uploaded content.
- Chat with the material through a RAG workflow.
- Switch chat modes: Socratic, Feynman, simple explanation, and exam prep.
- Generate structured notes, flashcards, quizzes, short-answer grading, and knowledge graphs.
- Store embeddings in a local FAISS vector index.

## Tech Stack

Backend:

- Python
- Flask
- Flask-CORS
- LangChain
- LangGraph
- Groq chat models
- HuggingFace sentence-transformer embeddings
- FAISS
- YouTube Transcript API

Frontend:

- React
- TypeScript
- Vite
- React Router
- Tailwind CSS
- lucide-react
- react-force-graph-2d
- react-markdown
- sonner

## Project Structure

```text
.
|-- app.py                  # Flask app entry point and legacy server-rendered routes
|-- agents/                 # Prompts and streaming RAG workflow
|-- frontend/               # Vite React application
|-- llm/                    # Groq LLM wrapper
|-- loaders/                # File and YouTube transcript loaders
|-- processing/             # Chunking, embeddings, LangGraph RAG, graph extraction
|-- retrieval/              # FAISS vector store wrapper
|-- routes/                 # Flask API blueprints
|-- templates/              # Legacy Flask templates
|-- uploads/                # Runtime upload directory
|-- utils/                  # JSON parsing helpers
|-- vector_store/           # Runtime FAISS index files
|-- requirements.txt        # Python dependencies
```

## Backend Flow

1. `routes/upload.py` accepts a file upload or YouTube URL.
2. `loaders/loader_manager.py` chooses either `FileLoader` or `YoutubeLoader`.
3. `processing/chunker.py` splits loaded documents into overlapping chunks.
4. `processing/embedder.py` creates a HuggingFace embedding model.
5. `retrieval/vector_store.py` writes chunks into the local FAISS index.
6. Session metadata and full extracted text are stored in `routes/store.py`.
7. Chat uses `agents/rag_workflow.py` to retrieve relevant chunks and stream an answer from Groq.
8. Notes, flashcards, quizzes, grading, and graph generation reuse `llm/generator.py` with specialized prompts from `agents/prompts.py`.

## API Overview

All modern API routes are mounted under `/api`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Backend health check |
| `POST` | `/api/upload` | Upload a file or submit a YouTube URL |
| `GET` | `/api/chat` | Stream chat response as server-sent events |
| `GET` | `/api/sessions` | List in-memory sessions |
| `DELETE` | `/api/sessions/<session_id>` | Delete a session |
| `GET` | `/api/notes/<session_id>` | Fetch generated notes |
| `POST` | `/api/notes/generate/<session_id>` | Generate notes |
| `GET` | `/api/flashcards/<session_id>` | Fetch flashcards |
| `POST` | `/api/flashcards/generate/<session_id>` | Generate flashcards |
| `POST` | `/api/flashcards/rate` | Rate flashcard mastery |
| `GET` | `/api/quiz/<session_id>` | Fetch quiz data |
| `POST` | `/api/quiz/generate/<session_id>` | Generate quiz questions |
| `POST` | `/api/quiz/grade` | Grade a short answer |
| `GET` | `/api/graph/<session_id>` | Fetch a knowledge graph |
| `POST` | `/api/graph/generate/<session_id>` | Generate a knowledge graph |
| `GET` | `/api/fact/<session_id>` | Generate a short study fact |

`app.py` also contains older form-based routes such as `/`, `/query`, `/youtube`, and a POST-based `/api/chat`. The React frontend uses the blueprint routes above through `frontend/src/lib/api.ts`.

## Setup

### 1. Backend Environment

Create and activate a Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the sample:

```bash
copy .env.sample .env
```

Set at least:

```env
GROQ_API_KEY="your_groq_api_key"
```

LangSmith variables are optional unless you want tracing.

### 2. Frontend Environment

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Running the App

Start the Flask backend from the repository root:

```bash
python app.py
```

The backend runs on:

```text
http://localhost:5000
```

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

The frontend usually runs on:

```text
http://localhost:5173
```

The Flask CORS config allows Vite dev origins on ports `5173` and `5174`.

## Testing and Smoke Checks

Manual backend checks:

```bash
python test_generate.py
python test_retrieval.py
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

`test_generate.py` calls the Groq API, so it requires a valid `GROQ_API_KEY`. `test_retrieval.py` expects a populated `vector_store/` directory.

## Runtime Data

- `uploads/` stores uploaded files.
- `vector_store/` stores the FAISS index.
- `knowledge_graph.json` stores merged graph extraction output.
- `routes/store.py` currently uses an in-memory dictionary for sessions, so sessions are lost when the Flask process restarts.

## Notes for Development

- The active frontend API base URL is hard-coded in `frontend/src/lib/api.ts` as `http://localhost:5000/api`.
- Uploaded chunks receive a `session_id` in metadata, but the current FAISS search path does not strictly isolate retrieval by session.
- `VectorStore.load()` uses `allow_dangerous_deserialization=True`, which is acceptable only when loading a trusted local FAISS index.
- Groq model usage is centralized in `llm/generator.py` and `agents/rag_workflow.py`.
- Knowledge graph extraction samples up to three chunks to keep generation small and fast.
