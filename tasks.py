import os
from datetime import datetime
from celery_app import celery
from routes.store import session_store


@celery.task(bind=True)
def process_upload(self, session_id, filepath, title, original_filename, is_youtube=False, youtube_url=None):
    try:
        from loaders.loader_manager import LoaderManager
        from loaders.youtube_loader import YoutubeLoader
        from processing.chunker import Chunker
        from processing.embedder import Embedder
        from retrieval.vector_store import VectorStore

        if is_youtube:
            loader = YoutubeLoader(youtube_url)
            documents = loader.load()  # no args — URL already passed to __init__
        else:
            loader = LoaderManager()
            documents = loader.load(filepath)

        chunker = Chunker()
        chunks = chunker.split(documents)

        for chunk in chunks:
            chunk.metadata["session_id"] = session_id

        embedder = Embedder()
        vector_store = VectorStore()
        vector_store.add(embedder.model, chunks)
        vector_store.save()

        full_text = "\n\n".join(doc.page_content for doc in chunks)

        session_store[session_id] = {
            "id": session_id,
            "title": title,
            "original_filename": original_filename,
            "created_at": datetime.now().isoformat(),
            "chunk_count": len(chunks),
            "full_text": full_text,
            "graph": None,
            "notes": None,
            "flashcards": None,
            "quiz": None,
        }

        return {"status": "ready", "session_id": session_id, "chunk_count": len(chunks)}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery.task(bind=True)
def generate_graph_task(self, session_id):
    try:
        from processing.graph_extractor import extract_knowledge_graph
        from processing.chunker import Chunker
        from langchain_core.documents import Document

        session_data = session_store.get(session_id)
        if not session_data:
            raise KeyError(f"Session {session_id} not found")

        full_text = session_data.get("full_text", "")
        if not full_text:
            raise ValueError("No text found for session")

        chunks = Chunker().split([Document(page_content=full_text)])
        graph_data = extract_knowledge_graph(chunks)

        if "edges" in graph_data:
            graph_data["links"] = graph_data.pop("edges")

        session_data["graph"] = graph_data
        session_store[session_id] = session_data

        return graph_data

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery.task(bind=True)
def generate_notes_task(self, session_id):
    try:
        from llm.generator import Generator
        from agents.prompts import NOTES_PROMPT
        from utils.json_helper import extract_json

        session_data = session_store.get(session_id)
        if not session_data:
            raise KeyError(f"Session {session_id} not found")

        full_text = session_data.get("full_text", "")[:6000]
        if not full_text:
            raise ValueError("No text found for session")

        generator = Generator(json_mode=True)
        res = generator.chain.invoke({"context": full_text, "question": NOTES_PROMPT})
        notes = extract_json(res)

        if notes:
            session_data["notes"] = notes
            session_store[session_id] = session_data

        return notes or {"points": []}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery.task(bind=True)
def generate_flashcards_task(self, session_id):
    try:
        from llm.generator import Generator
        from agents.prompts import FLASHCARD_GENERATION_PROMPT
        from utils.json_helper import extract_json
        from db import upsert_card_schedule, upsert_flashcard_progress

        session_data = session_store.get(session_id)
        if not session_data:
            raise KeyError(f"Session {session_id} not found")

        full_text = session_data.get("full_text", "")[:6000]
        if not full_text:
            raise ValueError("No text found for session")

        generator = Generator(json_mode=True)
        res = generator.chain.invoke({"context": full_text, "question": FLASHCARD_GENERATION_PROMPT})
        flashcards = extract_json(res)

        if flashcards:
            for i, c in enumerate(flashcards.get("cards", [])):
                c["id"] = f"card_{i}"
                c["mastery"] = 0
                c["next_review"] = datetime.now().isoformat()
                upsert_card_schedule(session_id, c["id"], c.get("front", ""), c["next_review"])

            session_data["flashcards"] = flashcards
            session_store[session_id] = session_data
            upsert_flashcard_progress(session_id, len(flashcards.get("cards", [])), 0)

        return flashcards or {"cards": []}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
