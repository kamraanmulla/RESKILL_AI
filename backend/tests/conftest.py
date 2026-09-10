import pytest
from app.schemas.profile import StudentProfile, Skill, AssessmentSignals
from app.services.gemini_service import gemini_service
from app.api.routes.profile_store import reset_to_zero_knowledge

@pytest.fixture(autouse=True)
def enforce_mock_mode_and_clean_slate():
    """Ensure Gemini mock mode is active for ALL tests to strictly protect API quota."""
    original_mock = gemini_service.mock_mode
    gemini_service.mock_mode = True
    reset_to_zero_knowledge()
    yield
    gemini_service.mock_mode = original_mock
    reset_to_zero_knowledge()

@pytest.fixture
def zero_knowledge_profile():
    return StudentProfile(
        id="user_zero",
        profileState="ZERO_KNOWLEDGE",
        name="Guest User",
        email="guest@reskillai.dev",
        skills=[],
        interests=[],
        careerInterest="",
        targetCareerId="",
        profileCompleteness=0,
    )

@pytest.fixture
def onboarding_profile():
    return StudentProfile(
        id="user_onboarded",
        profileState="PROFILE_READY",
        name="Aarav Sharma",
        email="aarav@reskillai.dev",
        degree="B.E. Computer Science",
        field="Computer Science",
        skills=[
            Skill(name="Python", category="Backend", proficiency=85, level="Proficient", verified=True),
            Skill(name="SQL", category="Database", proficiency=80, level="Proficient", verified=True),
            Skill(name="Linux", category="Security", proficiency=75, level="Proficient", verified=True),
            Skill(name="Git", category="Tools", proficiency=75, level="Proficient", verified=True)
        ],
        interests=["Cybersecurity", "Networking"],
        careerInterest="Cybersecurity Analyst",
        targetCareerId="cybersecurity_analyst",
        practicalExperience="Built a network packet analyzer and completed Linux security labs",
        profileCompleteness=75,
    )

@pytest.fixture
def assessment_signals():
    return AssessmentSignals(
        domainPreferences=["Cybersecurity"],
        problemSolvingStyle="Investigating why systems fail and threat patterns",
        workStyleSignals=["Hands-on lab investigations and security diagnostics"],
        primaryMotivation="Protecting critical infrastructure",
        careerInterestScores={"cybersecurity_analyst": 92, "cloud_security_engineer": 85, "software_engineer": 40}
    )
