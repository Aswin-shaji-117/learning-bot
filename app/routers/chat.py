from fastapi import APIRouter, HTTPException
from schemas import ChatRequest, ChatResponse
from services.subject_service import subject_service
from services.chatbot_service import get_chatbot_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question to the subject chatbot
    
    Args:
        request: Chat request with subject_id and question
        
    Returns:
        Answer based on subject documents
    """
    # Validate subject exists
    subject = subject_service.get_subject(request.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check if subject has any documents
    if not subject.get("documents") or len(subject["documents"]) == 0:
        return ChatResponse(
            subject_id=request.subject_id,
            question=request.question,
            answer="No information found in the subject documents.",
            sources=[]
        )
    
    try:
        # Get chatbot service and answer question
        chatbot = get_chatbot_service()
        result = chatbot.answer_question(
            subject_id=request.subject_id,
            question=request.question
        )
        
        return ChatResponse(
            subject_id=request.subject_id,
            question=request.question,
            answer=result["answer"],
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )
