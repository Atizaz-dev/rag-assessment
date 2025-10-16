from typing import List, AsyncGenerator
import openai
from app.services.vector_store import VectorStore
from app.services.embeddings_service import EmbeddingsService
from app.models.schemas import SourceDocument, QueryResponse
from app.config import get_settings
import time
import asyncio

settings = get_settings()

class QAService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embeddings_service = EmbeddingsService()
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def answer_question(self, question: str, top_k: int = 5, return_sources: bool = True) -> QueryResponse:
        """Answer a question using vector search and LLM."""
        start_time = time.time()
        
        query_embedding = await self.embeddings_service.get_embedding(question)
        
        results = self.vector_store.search(query_embedding, top_k)
        
        if not results:
            return QueryResponse(
                answer="I don't have enough information to answer this question. Please add relevant documents first.",
                sources=[],
                processing_time=time.time() - start_time
            )
        
        context_parts = []
        sources = []
        
        for doc, score in results:
            context_parts.append(doc.get('content', ''))
            if return_sources:
                sources.append(SourceDocument(
                    doc_id=doc.get('doc_id'),
                    title=doc.get('title'),
                    content=doc.get('content')[:500],
                    score=1 / (1 + score)
                ))
        
        context = "\n\n".join(context_parts)
        
        prompt = self._create_prompt(context, question)
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Always base your answers on the context provided."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
        
        answer = response.choices[0].message.content
        
        return QueryResponse(
            answer=answer,
            sources=sources if return_sources else [],
            processing_time=time.time() - start_time
        )
    
    async def answer_question_stream(self, question: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Answer a question with streaming response."""
        query_embedding = await self.embeddings_service.get_embedding(question)
        results = self.vector_store.search(query_embedding, top_k)
        
        if not results:
            yield "I don't have enough information to answer this question."
            return
        
        context_parts = [doc.get('content', '') for doc, _ in results]
        context = "\n\n".join(context_parts)
        prompt = self._create_prompt(context, question)
        
        stream = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    def _create_prompt(self, context: str, question: str) -> str:
        """Create prompt for the LLM."""
        return f"""Context information is below:
---------------------
{context}
---------------------

Given the context information and not prior knowledge, answer the following question. If the answer is not in the context, say "I cannot find this information in the provided documents."

Question: {question}
Answer:"""