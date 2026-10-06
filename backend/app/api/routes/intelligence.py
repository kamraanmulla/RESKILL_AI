from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from .profile_store import get_profile
from ...intelligence.advanced.hidden_competency_engine import hidden_competency_engine
from ...intelligence.advanced.transferability_engine import transferability_engine
from ...intelligence.advanced.combination_engine import combination_engine
from ...intelligence.advanced.contradiction_engine import contradiction_engine
from ...intelligence.advanced.obsolescence_engine import obsolescence_engine

router = APIRouter(prefix="/intelligence", tags=["Advanced Intelligence"])

@router.get("/hidden-competencies", response_model=List[Dict[str, Any]])
def get_hidden_competencies():
    """Detect skills the user demonstrates through evidence without explicitly claiming them."""
    profile = get_profile()
    return hidden_competency_engine.detect_hidden_competencies(profile)

@router.get("/transferability", response_model=Dict[str, Any])
def get_transferability(
    target_career_id: Optional[str] = Query(None, description="Destination career ID to compare against"),
    source_career_id: Optional[str] = Query("career_fullstack", description="Source baseline career ID")
):
    """Calculates deterministic skill transferability to another career."""
    profile = get_profile()
    dest_id = target_career_id or profile.targetCareerId or "career_cybersecurity"
    return transferability_engine.calculate_transferability(profile, dest_id, source_career_id)

@router.get("/combinations", response_model=List[Dict[str, Any]])
def get_combinations():
    """Discovers career opportunities unlocked by synergistic skill combinations."""
    profile = get_profile()
    return combination_engine.discover_combinations(profile)

@router.get("/contradictions", response_model=List[Dict[str, Any]])
def get_contradictions():
    """Identifies constructive evidence calibration mismatches across profile claims."""
    profile = get_profile()
    return contradiction_engine.detect_contradictions(profile)

@router.get("/obsolescence", response_model=List[Dict[str, Any]])
def get_obsolescence():
    """Analyzes technology trends and modern skill evolutions from curated industry catalog."""
    profile = get_profile()
    return obsolescence_engine.analyze_skill_trends(profile)

@router.get("/summary", response_model=Dict[str, Any])
def get_advanced_intelligence_summary(target_career_id: Optional[str] = None):
    """Consolidated endpoint providing all five advanced intelligence vectors in a single efficient payload."""
    profile = get_profile()
    dest_id = target_career_id or profile.targetCareerId or "career_cybersecurity"
    
    return {
        "hiddenCompetencies": hidden_competency_engine.detect_hidden_competencies(profile),
        "transferability": transferability_engine.calculate_transferability(profile, dest_id),
        "combinations": combination_engine.discover_combinations(profile),
        "contradictions": contradiction_engine.detect_contradictions(profile),
        "obsolescence": obsolescence_engine.analyze_skill_trends(profile),
        "profileState": profile.profileState
    }


from ...services.skill_evidence_service import (
    skill_evidence_service,
    SkillEvidenceProfileResponse,
    SkillEvidenceItem
)

@router.get("/skill-evidence", response_model=SkillEvidenceProfileResponse)
def get_skill_evidence_profile(skills: Optional[str] = Query(None, description="Comma-separated skill names")):
    """
    Evaluates real user evidence (Resume, Assessment, Projects, Experience)
    via Phase 3 ML evidence model for the authenticated candidate.
    """
    profile = get_profile()
    skills_list = [s.strip() for s in skills.split(",")] if skills else None
    return skill_evidence_service.evaluate_profile_evidence(profile, skills_list)

@router.get("/skill-evidence/{skill_name}", response_model=SkillEvidenceItem)
def get_single_skill_evidence(skill_name: str):
    """
    Evaluates real user evidence for a single targeted skill
    for the authenticated candidate.
    """
    profile = get_profile()
    return skill_evidence_service.evaluate_skill_evidence(profile, skill_name)


from ...schemas.intelligence import ReadinessResult, RoadmapStep
from ...intelligence.readiness_engine import ReadinessEngine
from ...intelligence.roadmap_engine import RoadmapEngine

@router.get("/readiness", response_model=ReadinessResult)
def get_readiness(target_career_id: Optional[str] = Query(None, description="Optional target career ID")):
    """Calculates deterministic career readiness enriched with multi-channel evidence."""
    profile = get_profile()
    return ReadinessEngine.calculate_readiness(profile, target_career_id)

@router.get("/roadmap", response_model=List[RoadmapStep])
def get_roadmap(target_career_id: Optional[str] = Query(None, description="Optional target career ID")):
    """Generates personalized milestone roadmap enriched with multi-channel evidence verification."""
    profile = get_profile()
    cid = target_career_id or profile.targetCareerId or "career_fullstack"
    return RoadmapEngine.generate_roadmap(profile, cid)

