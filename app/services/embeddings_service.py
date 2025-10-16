from typing import List
import openai
from app.config import get_settings
import asyncio

settings = get_settings()
openai.api_key = settings.openai_api_key

class EmbeddingsService:
    def __init__(self):
        self.model = settings.embedding_model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await asyncio.to_thread(
                    self.client.embeddings.create,
                    input=batch,
                    model=self.model
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                raise Exception(f"Error getting embeddings batch: {str(e)}")
        
        return embeddings