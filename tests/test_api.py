import asyncio
import math
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings
from app.services.document_service import DocumentService
from app.services.vector_store import VectorStore
from app.models.schemas import DocumentInput, DocumentCreate
import app.api.routes.query as query_route
import app.services.embeddings_service as embeddings_module


def get_token(client: TestClient) -> str:
    resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_retrieval_after_indexing(tmp_path):
    # Point vector store to a temporary directory to avoid interference
    settings = get_settings()
    original_vector_path = settings.vector_store_path
    original_docs_path = settings.documents_path
    settings.vector_store_path = str(tmp_path / "vector_store")
    settings.documents_path = str(tmp_path / "documents")

    try:
        client = TestClient(app)
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Ensure the query route's qa_service uses the temp vector store path
        query_route.qa_service.vector_store = VectorStore()

        # Monkeypatch EmbeddingsService to avoid external API and be deterministic
        dimension = 1536

        async def fake_get_embedding(self, text: str):
            v = [0.0] * dimension
            h = sum(ord(c) for c in text) % dimension
            v[h] = 1.0
            return v

        async def fake_get_embeddings_batch(self, texts):
            return [await fake_get_embedding(self, t) for t in texts]

        embeddings_module.EmbeddingsService.get_embedding = fake_get_embedding
        embeddings_module.EmbeddingsService.get_embeddings_batch = fake_get_embeddings_batch

        # Mock LLM chat completion to avoid external API
        class DummyMsg:
            def __init__(self, content):
                self.content = content

        class DummyChoice:
            def __init__(self, content):
                self.message = DummyMsg(content)

        class DummyResponse:
            def __init__(self, content):
                self.choices = [DummyChoice(content)]

        def fake_chat_create(model, messages, max_tokens, temperature):
            return DummyResponse("Paris is the capital of France.")

        query_route.qa_service.client.chat.completions.create = fake_chat_create

        # Then index document via DocumentService (simulating upload route)
        document_service = DocumentService()

        content = "Paris is the capital of France."
        documents = DocumentCreate(
            documents=[DocumentInput(title="facts.txt", content=content)]
        )

        # Index documents
        loop = asyncio.get_event_loop()
        loop.run_until_complete(document_service.index_documents(documents.documents))

        # Query should now find the info
        resp = client.post(
            "/query/",
            headers=headers,
            json={"question": "What is the capital of France?", "top_k": 3, "return_sources": True},
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "France" in data["answer"] or "Paris" in data["answer"]

    finally:
        # restore settings
        settings.vector_store_path = original_vector_path
        settings.documents_path = original_docs_path

