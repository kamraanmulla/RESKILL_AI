from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from .profile_store import get_profile
from ...services.gemini_service import gemini_service
from ...intelligence.advanced.hidden_competency_engine import hidden_competency_engine
from ...intelligence.advanced.transferability_engine import transferability_engine
from ...intelligence.advanced.contradiction_engine import contradiction_engine
from ...intelligence.skill_gap_engine import SkillGapEngine

router = APIRouter(prefix="/coach", tags=["AI Career Coach"])

class CoachChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

class CoachChatResponse(BaseModel):
    response: str
    source: str
    status: str
    error: Optional[str] = None

@router.post("/chat", response_model=CoachChatResponse)
async def chat_with_coach(req: CoachChatRequest):
    """Conversational endpoint for the ReSkillAI Career Coach powered by Gemini.
    Always calls the real Gemini API. Mock mode is only available for automated tests.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Inquiry message cannot be empty.")

    profile = get_profile()
    target_career_id = profile.targetCareerId or "career_fullstack"

    # Assemble contextual intelligence dossier for Gemini
    gaps_data = SkillGapEngine.calculate_skill_gaps(profile, target_career_id)
    top_gaps = [g.skill for g in gaps_data if g.status != "Mastered"]

    context = {
        "skillGaps": top_gaps,
        "hiddenCompetencies": hidden_competency_engine.detect_hidden_competencies(profile),
        "transferability": transferability_engine.calculate_transferability(profile, target_career_id),
        "contradictions": contradiction_engine.detect_contradictions(profile)
    }

    result = gemini_service.career_coach_chat(
        message=req.message.strip(),
        profile=profile,
        intelligence_context=context,
        history=req.history
    )

    # If Gemini returned an error, propagate it clearly
    if result.get("status") == "error":
        error_msg = result.get("error", "AI Career Coach encountered an error.")
        return CoachChatResponse(
            response=result.get("response", ""),
            source=result.get("source", "error"),
            status="error",
            error=error_msg
        )

    return CoachChatResponse(
        response=result.get("response", "Could not generate response at this time."),
        source=result.get("source", "unknown"),
        status=result.get("status", "success"),
        error=result.get("error")
    )

