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
