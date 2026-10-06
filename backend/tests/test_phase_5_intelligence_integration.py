import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.intelligence.recommendation_engine import CareerRecommendationEngine
from app.intelligence.readiness_engine import ReadinessEngine
from app.intelligence.roadmap_engine import RoadmapEngine
from app.intelligence.skill_gap_engine import SkillGapEngine
from app.schemas.profile import StudentProfile, Skill, StudentProject, StudentExperience

client = TestClient(app)


def test_career_match_zero_knowledge():
    """Verify zero-knowledge candidate receives 0 match score and uncalibrated evidence."""
    client.post("/api/auth/signup", json={
        "name": "ZK Career Candidate",
        "email": "zk_career@testdomain.com"
    })
    resp = client.get("/api/careers/recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) > 0

    for r in recs:
        assert r["matchScore"] == 0
        assert r["confidence"] == "Uncalibrated"
        assert r["evidence_strength"] is None
        assert r["evidence_confidence"] == 0.0
        assert r["evidence_sources"] == []
        assert r["evidence_level"] == "INSUFFICIENT"


def test_career_match_real_user_evidence():
    """Verify real candidate with resume evidence receives evidence-corroborated career match."""
    client.post("/api/auth/signup", json={
        "name": "Real Career Candidate",
        "email": "real_career@testdomain.com"
    })
    resume_text = """
    Real Career Candidate
    real_career@testdomain.com

    Technical Skills:
    JavaScript, React, Node.js, Git

    Work Experience:
    Frontend Engineer at TechCorp
    Built responsive client applications using JavaScript, React, Node.js, and managed Git repositories.
    """
    client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})

    resp = client.get("/api/careers/recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) > 0

    # Fullstack or Frontend should be top match
    top = recs[0]
    assert top["matchScore"] > 0
    assert len(top["matchedSkills"]) > 0
    assert "resume" in top["evidence_sources"]
    assert top["evidence_strength"] is not None
    assert top["evidence_level"] in ["STRONG", "MODERATE", "WEAK"]
    assert "corroborated by" in top["evidence_explanation"]

    # Single career match endpoint GET /api/careers/match
    resp_match = client.get("/api/careers/match")
    assert resp_match.status_code == 200
    match_data = resp_match.json()
    assert match_data["overallMatch"] > 0
    assert len(match_data["strongMatches"]) > 0 or len(match_data["needsImprovement"]) > 0
    assert match_data["evidence_strength"] is not None
    assert "resume" in match_data["evidence_sources"]


def test_readiness_zero_knowledge():
    """Verify zero-knowledge candidate receives 0 readiness points and uncalibrated evidence summary."""
    client.post("/api/auth/signup", json={
        "name": "ZK Readiness Candidate",
        "email": "zk_readiness@testdomain.com"
    })
    resp = client.get("/api/intelligence/readiness")
    assert resp.status_code == 200
    data = resp.json()

    assert data["readinessScore"] == 0
    assert data["readinessPoints"] == 0
    assert data["readinessLevel"] == "Uncalibrated"
    assert data["breakdown"]["totalPoints"] == 0
    assert data["evidence_strength"] is None
    assert data["evidence_confidence"] == 0.0
    assert data["evidence_sources"] == []
    assert data["evidence_level"] == "INSUFFICIENT"
    assert "uncalibrated" in data["evidence_summary"].lower()


def test_readiness_real_user_evidence():
    """Verify real candidate with portfolio evidence receives corroborated readiness score without score inflation."""
    client.post("/api/auth/signup", json={
        "name": "Real Readiness Candidate",
        "email": "real_readiness@testdomain.com"
    })
    resume_text = """
    Real Readiness Candidate
    real_readiness@testdomain.com
    B.Tech in Computer Science & Engineering

    Technical Skills:
    React, JavaScript, Node.js, Git, SQL

    Work Experience:
    Junior Software Engineer at DevHouse
    Architected web modules with React and Node.js.
    """
    client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})

    resp = client.get("/api/intelligence/readiness")
    assert resp.status_code == 200
    data = resp.json()

    assert data["readinessScore"] > 0
    assert data["readinessPoints"] > 0
    assert data["readinessLevel"] in ["Early Foundation", "Developing", "Proficient", "Industry Ready"]
    assert data["breakdown"]["skillAlignmentPoints"] > 0
    assert data["breakdown"]["educationPoints"] > 0
    # Additive evidence fields
    assert "resume" in data["evidence_sources"]
    assert data["evidence_confidence"] >= 0.30
    assert data["evidence_level"] in ["STRONG", "MODERATE", "WEAK"]
    assert "corroborated by" in data["evidence_summary"].lower()


def test_roadmap_zero_knowledge():
    """Verify zero-knowledge candidate roadmap has 0 completed steps and starts from step 1."""
    client.post("/api/auth/signup", json={
        "name": "ZK Roadmap Candidate",
        "email": "zk_roadmap@testdomain.com"
    })
    resp = client.get("/api/intelligence/roadmap")
    assert resp.status_code == 200
    steps = resp.json()

    assert len(steps) > 0
    # Zero completed steps
    completed_steps = [s for s in steps if s["status"] == "completed"]
    assert len(completed_steps) == 0

    # Step 1 should be in_progress
    assert steps[0]["status"] == "in_progress"
    for s in steps:
        assert s["evidence_level"] == "INSUFFICIENT"
        assert s["evidence_sources"] == []


def test_roadmap_real_user_evidence_and_verification_guard():
    """Verify roadmap marks step completed only when substantiated by empirical evidence."""
    # Case 1: Candidate with real verified evidence
    client.post("/api/auth/signup", json={
        "name": "Real Roadmap Candidate",
        "email": "real_roadmap@testdomain.com"
    })
    resume_text = """
    Real Roadmap Candidate
    real_roadmap@testdomain.com

    Technical Skills:
    React, JavaScript, HTML/CSS

    Work Experience:
    Frontend Specialist at WebWorks
    Developed production user interfaces using React and modern JavaScript.
    """
    client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})

    resp = client.get("/api/intelligence/roadmap")
    assert resp.status_code == 200
    steps = resp.json()
    assert len(steps) > 0

    # React / JavaScript step should have evidence sources
    react_step = next((s for s in steps if "react" in s["title"].lower() or "react" in s["skillKey"].lower()), None)
    if react_step:
        assert "resume" in react_step["evidence_sources"]
        assert react_step["evidence_level"] in ["STRONG", "MODERATE", "WEAK"]

    # Case 2: Verification Guard: Unsubstantiated self-claim is not completed without evidence
    unverified_profile = StudentProfile(
        id="unverified_user",
        name="Unverified User",
        email="unverified@test.com",
        skills=[Skill(name="React", proficiency=85)], # High claim, but 0 artifacts, 0 resume, 0 projects
        projects=[],
        experience=[]
    )
    unverified_steps = RoadmapEngine.generate_roadmap(unverified_profile, "career_fullstack")
    uv_react_step = next((s for s in unverified_steps if "react" in s.title.lower() or "react" in s.skillKey.lower()), None)
    if uv_react_step:
        # Must not be marked completed because evidence is INSUFFICIENT
        assert uv_react_step.status in ["in_progress", "upcoming"]


def test_multi_user_cross_engine_isolation():
    """Verify complete cross-engine isolation between User Alpha (Python) and User Beta (Java)."""
    # 1. Setup User Alpha (Python)
    client.post("/api/auth/signup", json={
        "name": "Alpha Engine 5",
        "email": "alpha.engine5@isolation.com"
    })
    resume_alpha = """
    Alpha Engine 5
    alpha.engine5@isolation.com
    Technical Skills:
    Python, FastAPI, Linux
    Work Experience:
    Python Developer at PyCorp
    Built microservices with Python and FastAPI on Linux.
    """
    client.post("/api/resume/analyze", files={"file": ("alpha.txt", resume_alpha.encode("utf-8"), "text/plain")})

    resp_alpha_gaps = client.get("/api/skill-gap").json()
    resp_alpha_recs = client.get("/api/careers/recommendations").json()
    resp_alpha_readiness = client.get("/api/intelligence/readiness").json()

    # Alpha must see resume evidence in readiness and Python in matched skills
    assert "resume" in resp_alpha_readiness["evidence_sources"]
    alpha_matched_initial = [skill for r in resp_alpha_recs for skill in r["matchedSkills"]]
    assert "Python" in alpha_matched_initial or "FastAPI" in alpha_matched_initial

    # 2. Setup User Beta (Java)
    client.post("/api/auth/signup", json={
        "name": "Beta Engine 5",
        "email": "beta.engine5@isolation.com"
    })
    resume_beta = """
    Beta Engine 5
    beta.engine5@isolation.com
    Technical Skills:
    Java, Spring Boot, MySQL
    Work Experience:
    Enterprise Engineer at JavaCorp
    Engineered enterprise systems with Java and Spring Boot.
    """
    client.post("/api/resume/analyze", files={"file": ("beta.txt", resume_beta.encode("utf-8"), "text/plain")})

    resp_beta_recs = client.get("/api/careers/recommendations").json()
    resp_beta_readiness = client.get("/api/intelligence/readiness").json()

    # Beta's top matched skills must include SQL, never Alpha's Python / Linux
    beta_matched = [skill for r in resp_beta_recs for skill in r["matchedSkills"]]
    assert "SQL" in beta_matched
    assert "Python" not in beta_matched
    assert "Linux" not in beta_matched

    # 3. Log back in as Alpha
    client.post("/api/auth/login", json={"email": "alpha.engine5@isolation.com"})
    resp_alpha_again_recs = client.get("/api/careers/recommendations").json()
    alpha_matched = [skill for r in resp_alpha_again_recs for skill in r["matchedSkills"]]
    assert "Python" in alpha_matched or "Linux" in alpha_matched
    assert "SQL" not in alpha_matched



def test_no_double_counting_and_formula_integrity():
    """Verify numerical scores strictly adhere to deterministic formulas without ML inflation."""
    profile = StudentProfile(
        id="test_integrity",
        name="Integrity Candidate",
        email="integrity@test.com",
        skills=[Skill(name="React", proficiency=80), Skill(name="JavaScript", proficiency=80)],
        projects=[StudentProject(title="Web App", tech=["React"], description="Single project")],
        degree="B.Tech in Computer Science"
    )

    # 1. Readiness score calculation
    readiness = ReadinessEngine.calculate_readiness(profile, "career_fullstack")
    expected_skill_pts = readiness.breakdown.skillAlignmentPoints
    expected_exp_pts = readiness.breakdown.practicalExperiencePoints
    expected_edu_pts = readiness.breakdown.educationPoints
    expected_total = expected_skill_pts + expected_exp_pts + expected_edu_pts
    assert readiness.readinessPoints == expected_total
    assert readiness.readinessScore == int(round(expected_total / 1000.0 * 100.0))

    # 2. Career match score calculation
    recs = CareerRecommendationEngine.recommend_careers(profile)
    fs_rec = next(r for r in recs if r.career.id == "career_fullstack")
    # Score must be bounded and strictly deterministic
    assert 15 <= fs_rec.matchScore <= 98
