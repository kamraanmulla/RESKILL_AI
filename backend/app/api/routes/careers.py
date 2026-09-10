from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from ...schemas.intelligence import CareerRecommendation, CareerRole
from ...schemas.profile import StudentProfile
from ...intelligence.recommendation_engine import CareerRecommendationEngine
from ...intelligence.career_taxonomy import CAREER_TAXONOMY, get_career_by_id
from .profile_store import get_profile, set_profile

router = APIRouter(prefix="/careers", tags=["Career Recommendations"])

class SelectCareerRequest(BaseModel):
    careerId: str

@router.get("", response_model=List[CareerRole])
def list_careers():
    profile = get_profile()
    recs = CareerRecommendationEngine.recommend_careers(profile)
    return [r.career for r in recs]

@router.get("/recommendations", response_model=List[CareerRecommendation])
def get_career_recommendations():
    profile = get_profile()
    return CareerRecommendationEngine.recommend_careers(profile)

from ...schemas.intelligence import CareerRecommendation, CareerRole, CareerMatch, StrongMatchItem, NeedsImprovementItem, BenchmarkComparisonItem
from ...intelligence.skill_gap_engine import SkillGapEngine

@router.get("/match", response_model=CareerMatch)
@router.get("/{career_id}/match", response_model=CareerMatch)
def get_career_match(career_id: Optional[str] = None):
    profile = get_profile()
    cid = career_id or profile.targetCareerId or "career_fullstack"
    career = get_career_by_id(cid)
    recs = CareerRecommendationEngine.recommend_careers(profile)
    rec = next((r for r in recs if r.career.id == cid), None)
    
    overall_match = rec.matchScore if rec else 0
    if len(profile.skills) == 0 and not profile.resumeFile and not profile.practicalExperience:
        overall_match = 0

    gaps = SkillGapEngine.calculate_skill_gaps(profile, cid)

    strong_matches = []
    needs_improvement = []
    benchmark_comparison = []

    for g in gaps:
        benchmark_comparison.append(
            BenchmarkComparisonItem(
                skill=g.skill,
                studentLevel=g.yourLevel,
                benchmarkLevel=g.requiredLevel,
                category=g.category
            )
        )
        if g.status == "Mastered" or g.gap == 0:
            strong_matches.append(
                StrongMatchItem(
                    skill=g.skill,
                    studentLevel=g.yourLevel,
                    requiredLevel=g.requiredLevel,
                    note=g.recommendation
                )
            )
        else:
            priority_str = "High" if g.gap >= 50 else ("Medium" if g.gap >= 25 else "Low")
            needs_improvement.append(
                NeedsImprovementItem(
                    skill=g.skill,
                    studentLevel=g.yourLevel,
                    requiredLevel=g.requiredLevel,
                    gap=g.gap,
                    priority=priority_str
                )
            )

    return CareerMatch(
        careerId=career.id,
        careerTitle=career.title,
        overallMatch=overall_match,
        strongMatches=strong_matches,
        needsImprovement=needs_improvement,
        benchmarkComparison=benchmark_comparison
    )

@router.post("/select", response_model=StudentProfile)
def select_career(req: Optional[SelectCareerRequest] = None, career_id: Optional[str] = None, careerId: Optional[str] = None):
    profile = get_profile()
    target_id = ""
    if req and req.careerId:
        target_id = req.careerId
    elif career_id:
        target_id = career_id
    elif careerId:
        target_id = careerId
    else:
        target_id = "career_fullstack"

    career = get_career_by_id(target_id)
    profile.targetCareerId = career.id

    # If in PROFILE_READY, transition to PERSONALIZED
    if profile.profileState in ["PROFILE_READY", "ZERO_KNOWLEDGE"] and len(profile.skills) > 0:
        profile.profileState = "PERSONALIZED"

    set_profile(profile)
    return profile

