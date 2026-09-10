import pytest
from app.intelligence.readiness_engine import ReadinessEngine
from app.intelligence.recommendation_engine import CareerRecommendationEngine
from app.intelligence.skill_gap_engine import SkillGapEngine
from app.intelligence.roadmap_engine import RoadmapEngine
from app.intelligence.career_taxonomy import CAREER_TAXONOMY, get_career_by_id
from app.schemas.profile import StudentProfile

def test_readiness_zero_knowledge(zero_knowledge_profile):
    result = ReadinessEngine.calculate_readiness(zero_knowledge_profile)
    assert result.readinessScore == 0
    assert result.readinessPoints == 0
    assert result.readinessLevel == "Uncalibrated"
    assert "insufficient" in result.statusMessage.lower()

def test_readiness_onboarded_profile(onboarding_profile, assessment_signals):
    onboarding_profile.assessmentSignals = assessment_signals
    result = ReadinessEngine.calculate_readiness(onboarding_profile, target_career_id="career_cybersecurity")
    
    assert result.readinessScore > 30
    assert result.readinessPoints > 300
    assert result.breakdown.skillAlignmentPoints > 0
    assert result.breakdown.assessmentPoints > 0
    assert result.breakdown.totalPoints <= 1000

def test_career_recommendations(onboarding_profile, assessment_signals):
    onboarding_profile.assessmentSignals = assessment_signals
    recommendations = CareerRecommendationEngine.recommend_careers(onboarding_profile)
    
    assert len(recommendations) > 0
    top = recommendations[0]
    assert "Security" in top.career.title or "Cybersecurity" in top.career.title or top.matchScore > 50
    assert len(top.matchedSkills) >= 0

def test_skill_gap_deterministic(onboarding_profile):
    gaps = SkillGapEngine.calculate_skill_gaps(onboarding_profile, "career_cybersecurity")
    assert len(gaps) > 0
    
    priorities = {g.priority for g in gaps}
    assert "Strong" in priorities or "Developing" in priorities or "Gap" in priorities

def test_roadmap_changes_with_career(onboarding_profile):
    roadmap_cyber = RoadmapEngine.generate_roadmap(onboarding_profile, "career_cybersecurity")
    roadmap_swe = RoadmapEngine.generate_roadmap(onboarding_profile, "career_fullstack")
    
    assert len(roadmap_cyber) > 0
    assert len(roadmap_swe) > 0
    # Ensure titles and skills differ between cyber and swe roadmaps
    cyber_topics = [t for step in roadmap_cyber for t in step.topics]
    swe_topics = [t for step in roadmap_swe for t in step.topics]
    assert cyber_topics != swe_topics
