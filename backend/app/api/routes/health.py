from fastapi import APIRouter
from ...services.gemini_service import gemini_service

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ReSkillAI Career Intelligence Engine",
        "version": "1.0.0"
    }

@router.get("/health/gemini")
def gemini_health_check():
    return gemini_service.test_gemini_connection()
