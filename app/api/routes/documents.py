from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import aiofiles
from app.models.schemas import (
    DocumentCreate, DocumentResponse, DocumentListResponse,
    DeleteResponse, User, DocumentInput
)
from app.services.document_service import DocumentService
from app.api.dependencies import get_current_user
from app.utils.file_processor import FileProcessor
from app.config import get_settings
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()
document_service = DocumentService()
file_processor = FileProcessor()

@router.post("/", response_model=List[DocumentResponse])
async def create_documents(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user)
):
    """Index documents from JSON input."""
    try:
        responses = await document_service.index_documents(document_data.documents)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing documents: {str(e)}")

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and index documents from files (PDF, TXT, DOCX, MD)."""
    try:
        documents = []
        
        for file in files:
            if not file_processor.is_supported_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Supported types: PDF, TXT, DOCX, MD"
                )
            
            file_id = str(uuid.uuid4())
            file_path = os.path.join(settings.documents_path, f"{file_id}_{file.filename}")
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            text_content = file_processor.process_file(file_path, file.filename)
            
            if not text_content:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not extract text from file: {file.filename}"
                )
            
            documents.append(DocumentInput(
                title=file.filename,
                content=text_content,
                metadata={"file_path": file_path, "original_filename": file.filename}
            ))
        
        responses = await document_service.index_documents(documents)
        return responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents(current_user: User = Depends(get_current_user)):
    """List all indexed documents."""
    try:
        documents = document_service.list_documents()
        return DocumentListResponse(documents=documents, total=len(documents))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str, current_user: User = Depends(get_current_user)):
    """Delete a document by ID."""
    try:
        success = document_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DeleteResponse(
            message="Document deleted successfully",
            deleted_doc_id=doc_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")