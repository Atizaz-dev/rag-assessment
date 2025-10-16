from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings, create_directories
from app.api.routes import documents, query, auth
from app.models.schemas import HealthResponse
from app.services.document_service import DocumentService
import os

create_directories()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Document-based Question Answering API with Vector Search and LLM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)

if os.path.exists("./app/static"):
    app.mount("/static", StaticFiles(directory="./app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend UI."""
    html_path = "./app/static/index.html"
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read()
    return """
    <html>
        <head><title>Document QA API</title></head>
        <body>
            <h1>Document QA API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    document_service = DocumentService()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        documents_indexed=document_service.get_total_documents()
    )

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    print(f"📚 Vector store path: {settings.vector_store_path}")
    print(f"📄 Documents path: {settings.documents_path}")
    print(f"🔑 Authentication enabled")
    print(f"🌐 Server running on http://{settings.host}:{settings.port}")
    print(f"📖 API docs available at http://{settings.host}:{settings.port}/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )