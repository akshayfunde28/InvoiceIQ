from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
from app.services.ocr_service import ocr_service
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    # Verify DB connectivity
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1")).scalar()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ocr_available": ocr_service.is_available(),
        "ai_model": settings.XAI_MODEL
    }
