import os
from dotenv import load_dotenv
load_dotenv()  # must be first — before any module that reads env vars

from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from loaders.loader_manager import LoaderManager
from loaders.youtube_loader import YoutubeLoader
from processing.chunker import Chunker
from processing.embedder import Embedder
from retrieval.vector_store import VectorStore

from db import init_db
from flask_cors import CORS
from routes.upload import upload_bp
from routes.chat import chat_bp
from routes.graph import graph_bp
from routes.flashcards import flashcards_bp
from routes.quiz import quiz_bp
from routes.notes import notes_bp
from routes.sessions import sessions_bp
from routes.fact import fact_bp

from celery_app import celery

init_db()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"])

app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(graph_bp, url_prefix='/api')
app.register_blueprint(flashcards_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')
app.register_blueprint(notes_bp, url_prefix='/api')
app.register_blueprint(sessions_bp, url_prefix='/api')
app.register_blueprint(fact_bp, url_prefix='/api')

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "server_error", "message": str(e)}), 500


@app.route("/api/task/<task_id>", methods=["GET"])
def task_status(task_id):
    result = celery.AsyncResult(task_id)
    if result.state == "PENDING":
        return jsonify({"state": "pending"})
    if result.state == "FAILURE":
        return jsonify({"state": "failure", "error": str(result.info)}), 500
    if result.state == "SUCCESS":
        return jsonify({"state": "success", "result": result.result})
    return jsonify({"state": result.state.lower()})


app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf','txt','docx','pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":

        if "file" not in request.files:
            message = "No file part"
            return render_template("index.html", message=message)

        file = request.files["file"]

        if file.filename == "":
            message = "No selected file"
            return render_template("index.html", message=message)

        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            loader = LoaderManager()
            documents = loader.load(filepath)

            # Chunking
            chunker = Chunker()
            chunks = chunker.split(documents)

            # Extract text from chunks
            texts = [doc.page_content for doc in chunks]

            # Embedding (LangChain)
            embedder = Embedder()
            
            # Vector Store (LangChain native handles embedding execution internally)
            vector_store = VectorStore()
            vector_store.add(embedder.model, chunks)
            vector_store.save()
            
            # Extract Knowledge Graph
            from processing.graph_extractor import extract_knowledge_graph
            extract_knowledge_graph(chunks)

            message = f"File uploaded and loaded successfully! Pages loaded: {len(documents)}"
            return render_template("index.html", message=message)

        else:
            message = "Only PDF files allowed."
            return render_template("index.html", message=message)

    return render_template("index.html", message=message)
@app.route("/query", methods=["POST"])
def query():
    from processing.graph import rag_graph

    user_query = request.form["query"]

    # Run LangGraph workflow
    inputs = {"query": user_query}
    result = rag_graph.invoke(inputs)
    answer = result["answer"]

    return render_template("index.html", answer=answer)
@app.route("/youtube", methods=["GET", "POST"])
def youtube():

    message = ""

    if request.method == "POST":
        url = request.form["url"]

        try:
            loader = YoutubeLoader(url)
            documents = loader.load()

            # Chunking
            chunker = Chunker()
            chunks = chunker.split(documents)

            # Extract text
            texts = [doc.page_content for doc in chunks]

            # Embedding
            embedder = Embedder()
            
            # Vector Store
            vector_store = VectorStore()
            vector_store.add(embedder.model, chunks)
            vector_store.save()
            
            # Extract Knowledge Graph
            from processing.graph_extractor import extract_knowledge_graph
            extract_knowledge_graph(chunks)

            message = "YouTube transcript loaded successfully!"

        except Exception as e:
            message = f"Error loading YouTube transcript: {str(e)}"

    # 🔴 ALWAYS return something
    return render_template("index.html", message=message)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    mode = data.get("mode", "normal")
    history = data.get("history", [])
    file_data = data.get("file", None)

    # Build mode-aware system prefix
    mode_prefixes = {
        "socratic_quiz": "You are a Socratic tutor. Never give direct answers. Only ask probing questions that guide the student to the answer.",
        "explain_simple": "Explain everything as simply as possible, like the student is 12 years old. Use analogies and short sentences.",
        "feynman": "You are a curious student. The user will explain a concept to you. Ask follow-up questions whenever something is unclear.",
        "exam_prep": "You are an exam coach. Focus only on likely exam questions, key definitions, and common mistakes students make.",
        "normal": "You are ShadowByte, a helpful AI study companion. Be clear, concise, and accurate."
    }
    system_hint = mode_prefixes.get(mode, mode_prefixes["normal"])
    full_query = f"{system_hint}\n\nStudent: {message}"

    def generate():
        try:
            from processing.graph import rag_graph
            result = rag_graph.invoke({"query": full_query})
            
            # Extract answer
            answer = result.get("answer", str(result)) if isinstance(result, dict) else str(result)
            
            # Stream word by word
            import time
            words = answer.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {chunk}\n\n"
                time.sleep(0.02)
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
