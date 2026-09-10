from fastapi import APIRouter
from typing import List, Literal
from pydantic import BaseModel
from ...schemas.intelligence import RoadmapStep
from ...intelligence.roadmap_engine import RoadmapEngine
from .profile_store import get_profile

router = APIRouter(prefix="/roadmap", tags=["Personalized Roadmap"])

class UpdateStepStatusRequest(BaseModel):
    status: Literal["completed", "in_progress", "upcoming"]

_dynamic_roadmap_cache: List[RoadmapStep] = []
_last_career_id: str = ""

@router.get("", response_model=List[RoadmapStep])
def get_roadmap():
    global _dynamic_roadmap_cache, _last_career_id
    profile = get_profile()
    cid = profile.targetCareerId or "career_fullstack"

    # Regenerate if target career changed or cache is empty
    if not _dynamic_roadmap_cache or _last_career_id != cid:
        _dynamic_roadmap_cache = RoadmapEngine.generate_roadmap(profile, cid)
        _last_career_id = cid

    return _dynamic_roadmap_cache

@router.post("/step/{step_id}", response_model=List[RoadmapStep])
def update_step_status(step_id: str, req: UpdateStepStatusRequest):
    global _dynamic_roadmap_cache
    if not _dynamic_roadmap_cache:
        get_roadmap()

    for s in _dynamic_roadmap_cache:
        if s.id == step_id:
            s.status = req.status
            break

    return _dynamic_roadmap_cache
