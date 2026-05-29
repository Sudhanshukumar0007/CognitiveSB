import os
from langchain_community.vectorstores import FAISS

class VectorStore:

    def __init__(self, index_path="vector_store"):
        self.index_path = index_path
        self.vector_store = None
        self._embeddings_model = None

    def add(self, embeddings_model, documents):
        self._embeddings_model = embeddings_model
         # Create directory if missing
        os.makedirs(self.index_path, exist_ok=True)
        index_file = os.path.join(self.index_path, "index.faiss")
        if not os.path.exists(index_file):
            # First addition, create new vector store
            self.vector_store = FAISS.from_documents(documents, embeddings_model)
        else:
            # Load existing and format new documents
            self.load(embeddings_model)
            self.vector_store.add_documents(documents)

    def save(self):
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)

    def load(self, embeddings_model):
        self._embeddings_model = embeddings_model
        index_file = os.path.join(self.index_path, "index.faiss")
        if os.path.exists(index_file):
            self.vector_store = FAISS.load_local(
                self.index_path, embeddings_model, allow_dangerous_deserialization=True
            )
        else:
            self.vector_store = None

    def _ensure_loaded(self):
        if self.vector_store is None and self._embeddings_model is not None:
            self.load(self._embeddings_model)

    def search(self, query, k=3, session_id=None):
        if self.vector_store is None:
            return []
        # Return LangChain Document objects
        if session_id:
            try:
                return self.vector_store.max_marginal_relevance_search(
                    query,
                    k=k,
                    fetch_k=max(10, k * 4),
                    filter={"session_id": session_id}
                )
            except TypeError:
                docs = self.vector_store.max_marginal_relevance_search(query, k=max(k * 4, 10), fetch_k=max(k * 8, 20))
                return [doc for doc in docs if doc.metadata.get("session_id") == session_id][:k]
        return self.vector_store.max_marginal_relevance_search(query, k=k, fetch_k=10)
