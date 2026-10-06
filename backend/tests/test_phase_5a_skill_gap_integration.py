import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.intelligence.skill_gap_engine import SkillGapEngine
from app.schemas.profile import StudentProfile, Skill, StudentProject, StudentExperience
from app.services.skill_evidence_service import skill_evidence_service, EvidenceState

client = TestClient(app)


def test_phase_5a_zero_knowledge_skill_gap():
    """Test B & J: Zero-knowledge user has required skills identified but all evidence is INSUFFICIENT."""
    # 1. Register fresh zero-knowledge candidate
    resp_signup = client.post("/api/auth/signup", json={
        "name": "Zero Knowledge User 5A",
        "email": "zk5a@reskill.test",
        "academicLevel": "Undergraduate"
    })
    assert resp_signup.status_code == 200

    # 2. Query Skill Gap endpoint
    resp_gaps = client.get("/api/skill-gap")
    assert resp_gaps.status_code == 200
    gaps = resp_gaps.json()

    assert len(gaps) > 0

    # All required skills must have yourLevel=0, status=Not Started, priority=Gap
    for item in gaps:
        assert item["yourLevel"] == 0
        assert item["gap"] == item["requiredLevel"]
        assert item["status"] == "Not Started"
        assert item["priority"] == "Gap"
        # Phase 5A Evidence Attributes:
        assert item["evidence_strength"] is None
        assert item["evidence_confidence"] == 0.0
        assert item["evidence_status"] == "INSUFFICIENT_EVIDENCE"
        assert item["evidence_sources"] == []
        assert item["evidence_level"] == "INSUFFICIENT"
        assert "No user evidence is currently available" in item["evidence_explanation"]


def test_phase_5a_real_user_resume_enrichment():
    """Test A: Real user resume enriches Skill Gap items with valid evidence signals."""
    client.post("/api/auth/signup", json={
        "name": "Resume User 5A",
        "email": "resume5a@reskill.test",
        "academicLevel": "Final Year Student"
    })

    resume_text = """
    Resume User 5A
    resume5a@reskill.test

    Technical Skills:
    React, JavaScript, Git

    Work Experience:
    Frontend Developer at WebLab
    Built responsive client applications using React and JavaScript. Managed version control with Git.
    """
    resp_res = client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})
    assert resp_res.status_code == 200

    resp_gaps = client.get("/api/skill-gap")
    assert resp_gaps.status_code == 200
    gaps = resp_gaps.json()

    react_gap = next((g for g in gaps if g["skill"].lower() == "react"), None)
    assert react_gap is not None
    assert react_gap["yourLevel"] > 0
    assert react_gap["status"] in ["In Progress", "Mastered"]
    assert react_gap["evidence_sources"] == ["resume", "experience"]
    assert react_gap["evidence_status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]
    assert react_gap["evidence_level"] in ["STRONG", "MODERATE"]
    assert react_gap["evidence_confidence"] >= 0.30
    assert "profile/resume" in react_gap["evidence_explanation"]


def test_phase_5a_multiple_sources_convergence():
    """Test C: User with Resume + Project + Assessment shows multiple converging sources and elevated confidence."""
    client.post("/api/auth/signup", json={
        "name": "Multi Source User 5A",
        "email": "multisource5a@reskill.test",
        "academicLevel": "College Senior"
    })

    resume_text = """
    Multi Source User 5A
    multisource5a@reskill.test

    Technical Skills:
    Python, SQL, Linux

    Work Experience:
    Backend Intern at CloudCorp
    Engineered backend services with Python, SQL, and Linux servers.
    """
    client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})

    # Add project directly to profile and set target to career_backend so SQL is a core requirement
    resp_prof = client.get("/api/profile")
    prof_data = resp_prof.json()
    prof_data["targetCareerId"] = "career_backend"
    prof_data["projects"] = [{
        "title": "Data Pipeline Service",
        "tech": ["Python", "SQL", "PostgreSQL"],
        "period": "2025",
        "description": "Constructed high-throughput ingestion pipeline using Python and SQL."
    }]
    client.put("/api/profile", json=prof_data)

    # Submit assessment
    client.post("/api/assessment/submit", json={
        "answers": {
            "q1": "q1_sw",
            "q2": "q2_fix",
            "q3": "q3_prod",
            "q4": "q4_grow"
        }
    })

    # Query skill gap
    resp_gaps = client.get("/api/skill-gap")
    assert resp_gaps.status_code == 200
    gaps = resp_gaps.json()

    # Find SQL (core skill for backend developer)
    sql_gap = next((g for g in gaps if g["skill"].lower() == "sql"), None)
    assert sql_gap is not None
    assert "resume" in sql_gap["evidence_sources"]
    assert "project" in sql_gap["evidence_sources"]
    assert sql_gap["evidence_confidence"] >= 0.50
    assert sql_gap["evidence_level"] in ["STRONG", "MODERATE"]
    assert sql_gap["evidence_status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]


def test_phase_5a_not_available_preservation():
    """Test D: Unavailable sources remain NOT_AVAILABLE and are not treated as 0 or failure."""
    profile = StudentProfile(
        id="test_user_na",
        name="NA Candidate",
        email="na@test.com",
        skills=[Skill(name="React", proficiency=75)],
        projects=[],
        experience=[]
    )
    # No assessment, no projects, no practical challenges
    ev_item = skill_evidence_service.evaluate_skill_evidence(profile, "React")
    assert ev_item.source_states["assessment"] == EvidenceState.NOT_AVAILABLE
    assert ev_item.source_states["project"] == EvidenceState.NOT_AVAILABLE
    assert ev_item.source_states["practical"] == EvidenceState.NOT_AVAILABLE

    gaps = SkillGapEngine.calculate_skill_gaps(profile)
    react_gap = next((g for g in gaps if g.skill.lower() == "react"), None)
    if react_gap:
        assert "assessment" not in react_gap.evidence_sources
        assert "project" not in react_gap.evidence_sources
        # In progress status must be maintained by deterministic logic, not dropped to 0
        assert react_gap.yourLevel == 75
        assert react_gap.status == "In Progress"


def test_phase_5a_absent_source_handling():
    """Test E: Evaluated but missing skill in uploaded resume results in ABSENT, not negative proficiency."""
    profile = StudentProfile(
        id="test_user_absent",
        name="Absent Candidate",
        email="absent@test.com",
        skills=[Skill(name="React", proficiency=75)],
        bio="React frontend developer",
        projects=[],
        experience=[]
    )
    # Docker is in target career requirements, but absent in profile
    ev_item = skill_evidence_service.evaluate_skill_evidence(profile, "Docker")
    assert ev_item.source_states["resume"] == EvidenceState.ABSENT
    assert ev_item.status == "UNSUPPORTED"

    gaps = SkillGapEngine.calculate_skill_gaps(profile)
    docker_gap = next((g for g in gaps if g.skill.lower() == "docker"), None)
    if docker_gap:
        assert docker_gap.yourLevel == 0
        assert docker_gap.status == "Not Started"
        assert docker_gap.evidence_status == "UNSUPPORTED"
        assert docker_gap.evidence_level == "INSUFFICIENT"


def test_phase_5a_multi_user_isolation():
    """Test F & G: Two users have strictly isolated evidence in Skill Gap analysis."""
    # 1. Setup User Alpha (Python / FastAPI / React)
    client.post("/api/auth/signup", json={
        "name": "Alpha 5A",
        "email": "alpha5a@isolation.test"
    })
    resume_alpha = """
    Alpha 5A
    alpha5a@isolation.test

    Technical Skills:
    Python, FastAPI, React

    Work Experience:
    Frontend & Backend Engineer at AlphaCorp
    Built responsive web applications with React and microservices with Python and FastAPI.
    """
    client.post("/api/resume/analyze", files={"file": ("alpha.txt", resume_alpha.encode("utf-8"), "text/plain")})

    resp_alpha_gaps = client.get("/api/skill-gap")
    alpha_gaps = resp_alpha_gaps.json()
    alpha_react = next((g for g in alpha_gaps if g["skill"].lower() == "react"), None)
    assert alpha_react is not None
    assert alpha_react["evidence_status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]
    assert "resume" in alpha_react["evidence_sources"]

    # 2. Setup User Beta (Java / Spring Boot / MySQL)
    client.post("/api/auth/signup", json={
        "name": "Beta 5A",
        "email": "beta5a@isolation.test"
    })
    resume_beta = """
    Beta 5A
    beta5a@isolation.test

    Technical Skills:
    Java, Spring Boot, MySQL

    Work Experience:
    Enterprise Engineer at BetaCorp
    Engineered enterprise systems with Java and Spring Boot.
    """
    client.post("/api/resume/analyze", files={"file": ("beta.txt", resume_beta.encode("utf-8"), "text/plain")})

    resp_beta_gaps = client.get("/api/skill-gap")
    beta_gaps = resp_beta_gaps.json()
    beta_react = next((g for g in beta_gaps if g["skill"].lower() == "react"), None)
    assert beta_react is not None
    assert beta_react["evidence_status"] in ["UNSUPPORTED", "INSUFFICIENT_EVIDENCE", "NOT_AVAILABLE"]
    assert beta_react["evidence_level"] == "INSUFFICIENT"

    # 3. Log back in as Alpha
    client.post("/api/auth/login", json={"email": "alpha5a@isolation.test"})
    resp_alpha_again = client.get("/api/skill-gap")
    alpha_again_gaps = resp_alpha_again.json()
    alpha_again_react = next((g for g in alpha_again_gaps if g["skill"].lower() == "react"), None)
    assert alpha_again_react is not None
    assert alpha_again_react["evidence_status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]


def test_phase_5a_target_career_differentiation():
    """Test H: Different target careers produce corresponding required skill sets and benchmarks."""
    profile = StudentProfile(
        id="test_career_diff",
        name="Career Diff User",
        email="diff@test.com",
        skills=[Skill(name="Python", proficiency=80), Skill(name="Linux", proficiency=70)],
        targetCareerId="career_fullstack"
    )

    gaps_fullstack = SkillGapEngine.calculate_skill_gaps(profile, "career_fullstack")
    skills_fs = {g.skill for g in gaps_fullstack}
    assert "React" in skills_fs or "HTML/CSS" in skills_fs

    gaps_cyber = SkillGapEngine.calculate_skill_gaps(profile, "career_cybersecurity")
    skills_cyber = {g.skill for g in gaps_cyber}
    assert "Network Security" in skills_cyber or "Linux" in skills_cyber or "Ethical Hacking" in skills_cyber
    assert skills_fs != skills_cyber


def test_phase_5a_deterministic_regression():
    """Test I: Deterministic priority order, gap calculations, and benchmarks remain identical."""
    profile = StudentProfile(
        id="test_reg",
        name="Regression Candidate",
        email="reg@test.com",
        skills=[
            Skill(name="React", proficiency=85),        # Exceeds 80 -> Mastered
            Skill(name="JavaScript", proficiency=50),   # Below 80 -> In Progress
            # Missing other skills -> Not Started
        ]
    )
    gaps = SkillGapEngine.calculate_skill_gaps(profile, "career_fullstack")
    react_item = next(g for g in gaps if g.skill == "React")
    assert react_item.status == "Mastered"
    assert react_item.priority == "Strong"
    assert react_item.gap == 0

    js_item = next(g for g in gaps if g.skill == "JavaScript")
    assert js_item.status == "In Progress"
    assert js_item.priority == "Developing"
    assert js_item.gap == 30 # 80 - 50

    # Priorities must be sorted: Gap (0) -> Developing (1) -> Strong (2)
    priority_order = {"Gap": 0, "Developing": 1, "Strong": 2}
    ranks = [priority_order[g.priority] for g in gaps]
    assert ranks == sorted(ranks)

    # Priorities must be sorted: Gap (0) -> Developing (1) -> Strong (2)
    priority_order = {"Gap": 0, "Developing": 1, "Strong": 2}
    ranks = [priority_order[g.priority] for g in gaps]
    assert ranks == sorted(ranks)
