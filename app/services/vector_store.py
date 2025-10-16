import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Tuple, Optional
from app.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.dimension = 1536
        self.index = None
        self.documents = []
        self.index_path = os.path.join(settings.vector_store_path, "faiss_index.bin")
        self.docs_path = os.path.join(settings.vector_store_path, "documents.pkl")
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self._save_index()

    def _reload_from_disk(self):
        """Reload index and documents from disk if they exist.

        This ensures that long-lived service instances (e.g., QAService)
        see documents that were indexed by other service instances without
        requiring a full process restart.
        """
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
    
    def _save_index(self):
        """Save index and documents to disk."""
        os.makedirs(settings.vector_store_path, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def add_documents(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add documents with embeddings to the index."""
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have the same length")
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        start_idx = len(self.documents)
        self.index.add(embeddings_array)
        
        for i, meta in enumerate(metadata):
            meta['vector_id'] = start_idx + i
            self.documents.append(meta)
        
        self._save_index()
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar documents."""
        # Refresh in-memory state to pick up documents indexed by other instances
        self._reload_from_disk()
        if self.index.ntotal == 0:
            return []
        
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        
        return results
    
    def delete_by_doc_id(self, doc_id: str) -> int:
        """Delete all chunks associated with a document ID."""
        indices_to_remove = [i for i, doc in enumerate(self.documents) if doc.get('doc_id') == doc_id]
        
        if not indices_to_remove:
            return 0
        
        remaining_docs = [doc for i, doc in enumerate(self.documents) if i not in indices_to_remove]
        
        if remaining_docs:
            remaining_indices = [i for i in range(len(self.documents)) if i not in indices_to_remove]
            
            all_vectors = []
            for i in range(self.index.ntotal):
                vector = self.index.reconstruct(int(i))
                all_vectors.append(vector)
            
            remaining_vectors = [all_vectors[i] for i in remaining_indices]
            
            self.index = faiss.IndexFlatL2(self.dimension)
            if remaining_vectors:
                vectors_array = np.array(remaining_vectors, dtype=np.float32)
                self.index.add(vectors_array)
            
            for i, doc in enumerate(remaining_docs):
                doc['vector_id'] = i
            
            self.documents = remaining_docs
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
        
        self._save_index()
        return len(indices_to_remove)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all unique documents."""
        unique_docs = {}
        for doc in self.documents:
            doc_id = doc.get('doc_id')
            if doc_id and doc_id not in unique_docs:
                unique_docs[doc_id] = doc
        return list(unique_docs.values())
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        for doc in self.documents:
            if doc.get('doc_id') == doc_id:
                return doc
        return None
    
    def clear(self):
        """Clear all data."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self._save_index()