from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.profile_store import set_profile
from app.schemas.profile import StudentProfile, Skill, StudentProject, ProfileState

client = TestClient(app)

def test_hidden_competency_detection():
    # Setup candidate with projects indicating backend & cloud
    profile = StudentProfile(
        id="test_candidate_1",
        name="Elena Rostova",
        skills=[Skill(name="Python", category="Backend", proficiency=75)],
        projects=[
            StudentProject(
                title="Microservices REST Gateway",
                tech=["FastAPI", "Docker", "AWS"],
                description="Engineered containerized REST API endpoints deployed to AWS cloud infrastructure."
            )
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    resp = client.get("/api/intelligence/hidden-competencies")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0

    skills_detected = [item["skill"] for item in data]
    assert "REST API Development" in skills_detected or "Cloud Infrastructure & Deployment" in skills_detected
    assert data[0]["explicitOrInferred"] == "inferred"
    assert data[0]["confidence"] >= 0.70

def test_transferability_score():
    profile = StudentProfile(
        id="test_candidate_2",
        name="Marcus Vance",
        skills=[
            Skill(name="Python", category="Backend", proficiency=80),
            Skill(name="Linux", category="Tools", proficiency=75),
            Skill(name="Git", category="Tools", proficiency=85)
        ],
        targetCareerId="career_fullstack",
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    # Test transferability to Cybersecurity
    resp = client.get("/api/intelligence/transferability?target_career_id=career_cybersecurity")
    assert resp.status_code == 200
    data = resp.json()
    assert "overallScore" in data
    assert 0 <= data["overallScore"] <= 100
    assert "destinationCareer" in data
    assert "transferableSkills" in data
    assert "bridgeSkills" in data
    assert "missingSkills" in data
    assert isinstance(data["explanation"], str)

def test_combination_discovery():
    profile = StudentProfile(
        id="test_candidate_3",
        name="Aisha Patel",
        skills=[
            Skill(name="Python", category="Backend", proficiency=80),
            Skill(name="SQL", category="Database", proficiency=75),
            Skill(name="Linux", category="Tools", proficiency=70)
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    resp = client.get("/api/intelligence/combinations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Python + SQL + Linux triggers Data Engineering
    career_paths = [c["career"] for c in data]
    assert "Data Engineering" in career_paths
    assert "confidence" in data[0]

def test_contradiction_detection():
    # Setup candidate with high-level claim but no projects
    profile = StudentProfile(
        id="test_candidate_4",
        name="David Kim",
        skills=[
            Skill(name="Docker", category="Tools", proficiency=90, level="Proficient")
        ],
        projects=[],
        practicalExperience="",
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    resp = client.get("/api/intelligence/contradictions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["severity"] in ["LOW", "MEDIUM", "HIGH"]
    assert "Evidence mismatch" in data[0]["explanation"]
    assert "recommendation" in data[0]

def test_obsolescence_detection():
    profile = StudentProfile(
        id="test_candidate_5",
        name="Samira Khan",
        skills=[
            Skill(name="jQuery", category="Frontend", proficiency=70),
            Skill(name="Python", category="Backend", proficiency=80)
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    resp = client.get("/api/intelligence/obsolescence")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    jquery_finding = next((item for item in data if item["skill"] == "jQuery"), None)
    assert jquery_finding is not None
    assert jquery_finding["trend"] in ["Declining Relevance", "Watch"]
    assert "React" in jquery_finding["recommendedSkills"]
    assert jquery_finding["datasetSource"] == "Curated/Internal Trend Dataset"

def test_intelligence_summary_endpoint():
    resp = client.get("/api/intelligence/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "hiddenCompetencies" in data
    assert "transferability" in data
    assert "combinations" in data
    assert "contradictions" in data
    assert "obsolescence" in data

def test_ai_career_coach_chat():
    """Test coach endpoint via HTTP — this will attempt real Gemini.
    We test the mock path directly to avoid quota consumption in CI.
    """
    from app.services.gemini_service import gemini_service
    profile = StudentProfile(
        id="test_candidate_6",
        name="Rohan Gupta",
        skills=[Skill(name="Python", category="Backend", proficiency=75)],
        targetCareerId="career_fullstack",
        careerReadiness=45,
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    # Test via force_mock to avoid real API call in automated tests
    result = gemini_service.career_coach_chat(
        message="Why is Full Stack Developer suitable for my skill set?",
        profile=profile,
        intelligence_context={"skillGaps": ["JavaScript", "React"], "hiddenCompetencies": [], "contradictions": []},
        history=[],
        force_mock=True
    )
    assert "response" in result
    assert len(result["response"]) > 20
    assert result["status"] == "success"
    assert result["source"] == "gemini_mock_mode"
    assert "Rohan Gupta" in result["response"]
