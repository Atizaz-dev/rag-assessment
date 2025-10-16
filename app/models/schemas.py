from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentInput(BaseModel):
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class DocumentCreate(BaseModel):
    documents: List[DocumentInput] = Field(..., description="List of documents to index")

class DocumentResponse(BaseModel):
    id: str = Field(..., description="Document unique identifier")
    title: str = Field(..., description="Document title")
    created_at: datetime = Field(..., description="Creation timestamp")
    chunk_count: int = Field(..., description="Number of chunks")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

class SourceDocument(BaseModel):
    doc_id: str
    title: str
    content: str
    score: float

class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask")
    top_k: Optional[int] = Field(default=5, description="Number of relevant chunks to retrieve")
    return_sources: Optional[bool] = Field(default=True, description="Include source documents in response")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: Optional[List[SourceDocument]] = Field(default=[], description="Source documents used")
    processing_time: float = Field(..., description="Query processing time in seconds")

class DeleteResponse(BaseModel):
    message: str
    deleted_doc_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class HealthResponse(BaseModel):
    status: str
    version: str
    documents_indexed: int