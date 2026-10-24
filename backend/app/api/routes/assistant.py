from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.assistant_service import assistant_service

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str

@router.post("/chat", response_model=ChatResponse)
def ask_assistant(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not data.question or not data.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    answer = assistant_service.answer_query(db, current_user, data.question.strip())
    return {
        "question": data.question,
        "answer": answer
    }
