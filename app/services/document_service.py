from typing import List, Dict, Any
import uuid
from datetime import datetime
from app.services.vector_store import VectorStore
from app.services.embeddings_service import EmbeddingsService
from app.utils.text_splitter import TextSplitter
from app.models.schemas import DocumentInput, DocumentResponse
from app.config import get_settings

settings = get_settings()

class DocumentService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embeddings_service = EmbeddingsService()
        self.text_splitter = TextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    async def index_documents(self, documents: List[DocumentInput]) -> List[DocumentResponse]:
        """Index multiple documents."""
        responses = []
        
        for doc in documents:
            doc_id = str(uuid.uuid4())
            chunks = self.text_splitter.split_by_paragraphs(doc.content)
            
            if not chunks:
                chunks = [doc.content]
            
            embeddings = await self.embeddings_service.get_embeddings_batch(chunks)
            
            metadata_list = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    'doc_id': doc_id,
                    'title': doc.title,
                    'content': chunk,
                    'chunk_index': i,
                    'created_at': datetime.utcnow().isoformat(),
                    'metadata': doc.metadata
                }
                metadata_list.append(metadata)
            
            self.vector_store.add_documents(embeddings, metadata_list)
            
            responses.append(DocumentResponse(
                id=doc_id,
                title=doc.title,
                created_at=datetime.utcnow(),
                chunk_count=len(chunks),
                metadata=doc.metadata
            ))
        
        return responses
    
    def list_documents(self) -> List[DocumentResponse]:
        """List all indexed documents."""
        docs = self.vector_store.get_all_documents()
        responses = []
        
        for doc in docs:
            chunk_count = sum(1 for d in self.vector_store.documents if d.get('doc_id') == doc.get('doc_id'))
            
            responses.append(DocumentResponse(
                id=doc.get('doc_id'),
                title=doc.get('title'),
                created_at=datetime.fromisoformat(doc.get('created_at')),
                chunk_count=chunk_count,
                metadata=doc.get('metadata', {})
            ))
        
        return responses
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        deleted_count = self.vector_store.delete_by_doc_id(doc_id)
        return deleted_count > 0
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get document by ID."""
        return self.vector_store.get_document_by_id(doc_id)
    
    def get_total_documents(self) -> int:
        """Get total number of unique documents."""
        return len(self.vector_store.get_all_documents())