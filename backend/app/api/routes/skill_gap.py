from fastapi import APIRouter
from typing import List
from ...schemas.intelligence import SkillGapItem
from ...intelligence.skill_gap_engine import SkillGapEngine
from .profile_store import get_profile

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Analysis"])

@router.get("", response_model=List[SkillGapItem])
def get_skill_gaps():
    profile = get_profile()
    return SkillGapEngine.calculate_skill_gaps(profile)
