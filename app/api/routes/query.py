from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import QueryRequest, QueryResponse, User
from app.services.qa_service import QAService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/query", tags=["query"])
qa_service = QAService()

@router.post("/", response_model=QueryResponse)
async def query_documents(
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Ask a question and get an answer based on indexed documents."""
    try:
        response = await qa_service.answer_question(
            question=query_data.question,
            top_k=query_data.top_k,
            return_sources=query_data.return_sources
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/stream")
async def query_documents_stream(
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Ask a question and get a streaming answer."""
    try:
        async def generate():
            async for chunk in qa_service.answer_question_stream(
                question=query_data.question,
                top_k=query_data.top_k
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")