from fastapi import APIRouter
from typing import Dict, Any
from ...intelligence.readiness_engine import ReadinessEngine
from ...intelligence.progression_engine import CareerProgressionEngine
from ...intelligence.skill_gap_engine import SkillGapEngine
from .profile_store import get_profile
from .roadmap import get_roadmap

router = APIRouter(tags=["Progress & Readiness"])

@router.get("/progress")
def get_progress_data():
    profile = get_profile()
    readiness = ReadinessEngine.calculate_readiness(profile)
    roadmap_steps = get_roadmap()

    completed_steps = sum(1 for s in roadmap_steps if s.status == "completed")
    roadmap_pct = int(round((completed_steps / len(roadmap_steps)) * 100.0)) if roadmap_steps else 0

    verified_skills_count = sum(1 for s in profile.skills if s.proficiency >= 65)

    return {
        "careerReadiness": readiness.readinessScore,
        "readinessPoints": readiness.readinessPoints,
        "readinessLevel": readiness.readinessLevel,
        "readinessBreakdown": readiness.breakdown,
        "skillsCompleted": {
            "completed": verified_skills_count,
            "total": max(len(profile.skills), 8)
        },
        "roadmapProgress": roadmap_pct,
        "learningHours": max(0, completed_steps * 6),
        "studyStreakDays": 0 if len(profile.skills) == 0 else (4 if len(profile.skills) >= 4 else 1),
        "currentFocus": {
            "title": profile.targetCareerId.replace("career_", "").replace("_", " ").title() if profile.targetCareerId else "No Trajectory Selected",
            "subtitle": "Targeting entry-level benchmark alignment" if profile.targetCareerId else "Complete onboarding to select career trajectory",
            "hoursLeft": "12 hours in active module" if len(profile.skills) > 0 else "0 hours"
        },
        "nextRecommendedAction": {
            "action": readiness.recommendationHint,
            "reason": readiness.statusMessage,
            "impact": "+8% Career Readiness",
            "stepId": "step_01"
        },
        "recentActivity": [
            {
                "id": "act_01",
                "action": "Profile calibrated against industry taxonomy",
                "time": "Just now",
                "type": "completed"
            }
        ] if len(profile.skills) > 0 else [
            {
                "id": "act_zero",
                "action": "Initialized zero-knowledge candidate workspace",
                "time": "Just now",
                "type": "started"
            }
        ]
    }

@router.get("/next-action")
def get_next_action():
    profile = get_profile()
    readiness = ReadinessEngine.calculate_readiness(profile)
    gaps = SkillGapEngine.calculate_skill_gaps(profile)
    top_gap = next((g for g in gaps if g.priority in ["Gap", "Developing"]), None)

    return {
        "action": f"Master {top_gap.skill}" if top_gap else "Review Roadmap Modules",
        "reason": f"Closing this {top_gap.category.lower()} competency yields immediate hiring alignment." if top_gap else "Target role expectations met.",
        "impact": "+8% Career Readiness",
        "targetSkill": top_gap.skill if top_gap else "Core"
    }

@router.get("/next-career")
def get_next_career_progression():
    profile = get_profile()
    return CareerProgressionEngine.get_next_progression(profile)
