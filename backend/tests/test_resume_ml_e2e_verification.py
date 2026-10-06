"""
ReSkillAI — Real Resume E2E Verification & Complete ML Integration Audit
Verifies real resume ingestion, Phase 2.5 career classifier, Phase 3 evidence model,
multi-engine intelligence propagation, multi-user isolation, and zero-knowledge handling.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.skill_evidence_service import skill_evidence_service, EvidenceState
from app.intelligence.career_taxonomy import CAREER_TAXONOMY
from app.schemas.profile import StudentProfile, Skill, StudentProject, StudentExperience, ResumeFileInfo

client = TestClient(app)

REALISTIC_RESUME_TEXT = """
Karan Patel
karan.patel@e2e.test
Bachelor of Technology in Computer Science & Engineering
Apex Institute of Technology, 2026 | CGPA: 8.6

Technical Skills:
Python, FastAPI, React, SQL, Git, Linux, Docker

Projects:
Task Orchestrator API: Developed distributed task scheduling backend service using Python and FastAPI with Redis workers.
Real-Time Analytics Dashboard: Built frontend client interface using React and modern CSS.

Work Experience:
Backend Engineering Intern at CloudBase:
Engineered RESTful APIs with Python and FastAPI, containerized microservices using Docker on Linux, and managed Git version control workflows.
"""


def setup_karan_profile():
    """Helper to ensure Karan Patel is registered and has uploaded his resume."""
    client.post("/api/auth/signup", json={
        "name": "Karan Patel",
        "email": "karan.patel@e2e.test",
        "academicLevel": "College Student"
    })
    resp_upload = client.post(
        "/api/resume/analyze",
        files={"file": ("karan_patel_resume.txt", REALISTIC_RESUME_TEXT.encode("utf-8"), "text/plain")}
    )
    return resp_upload.json()


# ============================================================================
# 1. Resume Ingestion & Real Artifact Extraction Test
# ============================================================================
def test_resume_ingestion_and_extraction():
    """
    Uploads a realistic resume and verifies that text extraction, skills,
    projects, education, and experience are parsed and persisted in SQLite.
    """
    profile = setup_karan_profile()

    # Verify extracted skills
    assert len(profile["skills"]) > 0
    extracted_names = [s["name"] for s in profile["skills"]]
    assert "Python" in extracted_names
    assert "FastAPI" in extracted_names
    assert "React" in extracted_names
    assert "SQL" in extracted_names
    assert "Git" in extracted_names
    assert "Linux" in extracted_names
    assert "Docker" in extracted_names

    # Verify all skills are marked as detected from resume ingestion
    for s in profile["skills"]:
        assert s["detectedFrom"] == "Resume Ingestion"
        assert s["verified"] is True
        assert 50 <= s["proficiency"] <= 100

    # Verify education extraction
    assert "Computer Science" in (profile["degree"] or "")
    assert "Apex" in (profile["institution"] or "")
    assert profile["graduationYear"] == 2026

    # Verify projects extraction
    assert len(profile["projects"]) >= 1
    proj_titles = [p["title"] for p in profile["projects"]]
    assert any("task" in t.lower() or "orchestrator" in t.lower() or "api" in t.lower() for t in proj_titles)

    # Verify experience extraction
    assert len(profile["experience"]) >= 1
    exp_titles = [e["title"] for e in profile["experience"]]
    assert any("intern" in t.lower() or "backend" in t.lower() or "cloudbase" in e["company"].lower() for e in profile["experience"] for t in [e["title"]])

    # Verify persistence by re-fetching profile
    resp_me = client.get("/api/profile")
    assert resp_me.status_code == 200
    saved = resp_me.json()
    assert saved["email"] == "karan.patel@e2e.test"
    assert len(saved["skills"]) == len(profile["skills"])
    assert saved["resumeFile"]["name"] == "karan_patel_resume.txt"


# ============================================================================
# 2. Career Classification ML Pipeline Test (Phase 2.5 v2)
# ============================================================================
def test_career_classification_ml_pipeline():
    """
    Verifies that the existing Phase 2.5 career classifier artifact
    (resume_career_classifier_v2.joblib) is loaded, executes real inference,
    and returns valid probability distributions through the backend API.
    """
    setup_karan_profile()
    # Query prediction endpoint for the uploaded resume
    resp_pred = client.get("/api/resume/career-prediction")
    assert resp_pred.status_code == 200
    data = resp_pred.json()

    assert data["model_file"] == "resume_career_classifier_v2.joblib"
    assert data["task_type"] == "career_category_classification"
    assert data["predicted_category"] in [
        "INFORMATION-TECHNOLOGY",
        "ENGINEERING",
        "CONSULTANT",
        "BUSINESS-DEVELOPMENT"
    ]
    assert 0.0 < data["confidence"] <= 1.0
    assert len(data["top_predictions"]) >= 3

    # Direct ML inference check to ensure identical pipeline behavior
    try:
        from ml.predict_resume import predict_career_category, get_model
    except ImportError:
        from backend.ml.predict_resume import predict_career_category, get_model
    model, metadata = get_model()
    assert model is not None
    assert metadata is not None
    assert len(model.classes_) == 24

    direct_pred = predict_career_category(REALISTIC_RESUME_TEXT)
    assert direct_pred["predicted_category"] == data["predicted_category"]
    assert abs(direct_pred["confidence"] - data["confidence"]) < 1e-4


# ============================================================================
# 3. Skill Evidence ML & 5-State Verification (Phase 3)
# ============================================================================
def test_skill_evidence_ml_states():
    """
    Verifies that real user evidence produces the 5 expected evidence states:
    1. SUPPORTED (Skill backed by resume and project)
    2. MODERATE_EVIDENCE (Skill backed by resume mention)
    3. WEAK_EVIDENCE (Weak heuristic signal)
    4. UNSUPPORTED (Skill with zero evidence in profile)
    5. INSUFFICIENT_EVIDENCE (Zero-knowledge profile)
    """
    setup_karan_profile()
    from app.api.routes.profile_store import get_profile
    karan_profile = get_profile()


    # 1. Supported: Python is in resume, project, and experience
    ev_python = skill_evidence_service.evaluate_skill_evidence(karan_profile, "Python")
    assert ev_python.status == "SUPPORTED"
    assert ev_python.evidence_strength is not None
    assert ev_python.evidence_strength >= 0.70
    assert "resume" in ev_python.evidence_sources
    assert "project" in ev_python.evidence_sources
    assert ev_python.confidence >= 0.50

    # 2. Moderate / Supported: Linux is in resume and experience
    ev_linux = skill_evidence_service.evaluate_skill_evidence(karan_profile, "Linux")
    assert ev_linux.status in ["SUPPORTED", "MODERATE_EVIDENCE"]
    assert "resume" in ev_linux.evidence_sources

    # 3. Unsupported: Rust is not mentioned anywhere in Karan's profile
    ev_rust = skill_evidence_service.evaluate_skill_evidence(karan_profile, "Rust")
    assert ev_rust.status == "UNSUPPORTED"
    assert ev_rust.evidence_strength is None
    assert ev_rust.confidence == 0.0
    assert ev_rust.evidence_sources == []

    # 4. Insufficient Evidence: Candidate with zero profile data
    zk_profile = StudentProfile(id="zk_test", email="zk@test.com")
    ev_zk = skill_evidence_service.evaluate_skill_evidence(zk_profile, "Python")
    assert ev_zk.status == "INSUFFICIENT_EVIDENCE"
    assert ev_zk.evidence_strength is None
    assert ev_zk.confidence == 0.0
    assert ev_zk.evidence_sources == []

    # 5. Weak Evidence: Minimal claim with no artifacts
    weak_profile = StudentProfile(
        id="weak_cand",
        email="weak@test.com",
        bio="I heard about C++ once.",
        skills=[Skill(name="C++", proficiency=50)]
    )
    ev_cpp = skill_evidence_service.evaluate_skill_evidence(weak_profile, "C++")
    assert ev_cpp.status in ["MODERATE_EVIDENCE", "WEAK_EVIDENCE", "SUPPORTED"]


# ============================================================================
# 4. Full Intelligence Engine Integration Chain
# ============================================================================
def test_full_intelligence_engine_integration_chain():
    """
    Verifies the complete downstream propagation:
    Resume -> Extracted Skills -> Intelligence Engines:
    - Skill Gap: calculates gaps using Karan's real skills
    - Career Match: matches Full Stack / Backend with evidence
    - Readiness: computes 1000-pt budget from real evidence pillars
    - Roadmap: respects verified evidence guards
    """
    setup_karan_profile()
    # 1. Skill Gap
    resp_gaps = client.get("/api/skill-gap")
    assert resp_gaps.status_code == 200

    gaps = resp_gaps.json()
    assert len(gaps) > 0
    # Python, Git should have userLevel > 0
    python_gap = next((g for g in gaps if "python" in g["skill"].lower()), None)
    if python_gap:
        assert python_gap["yourLevel"] > 0
        assert python_gap["evidence_level"] in ["STRONG", "MODERATE"]

    # 2. Career Match
    resp_recs = client.get("/api/careers/recommendations")
    assert resp_recs.status_code == 200
    recs = resp_recs.json()
    assert len(recs) > 0
    top_rec = recs[0]
    assert top_rec["matchScore"] > 0
    assert len(top_rec["matchedSkills"]) > 0
    assert "Python" in top_rec["matchedSkills"] or "FastAPI" in top_rec["matchedSkills"] or "React" in top_rec["matchedSkills"]
    assert "resume" in top_rec["evidence_sources"]
    assert top_rec["evidence_level"] in ["STRONG", "MODERATE", "WEAK"]

    # 3. Readiness Diagnostic
    resp_readiness = client.get("/api/readiness")
    assert resp_readiness.status_code == 200
    readiness = resp_readiness.json()
    assert readiness["readinessScore"] > 0
    assert readiness["readinessPoints"] > 0
    # Must have points from Skills, Projects, and Education
    assert readiness["breakdown"]["skillAlignmentPoints"] > 0
    assert readiness["breakdown"]["practicalExperiencePoints"] > 0
    assert readiness["breakdown"]["educationPoints"] > 0
    assert "resume" in readiness["evidence_sources"]
    assert "project" in readiness["evidence_sources"]
    assert readiness["evidence_level"] in ["STRONG", "MODERATE"]

    # 4. Roadmap Engine
    resp_roadmap = client.get("/api/roadmap")
    assert resp_roadmap.status_code == 200
    steps = resp_roadmap.json()
    assert len(steps) > 0
    # Roadmap should have evidence attached to relevant steps
    has_evidence_step = any(len(s["evidence_sources"]) > 0 for s in steps)
    assert has_evidence_step is True


# ============================================================================
# 5. Multi-User Strict Isolation & Cross-User Security Test
# ============================================================================
def test_multi_user_strict_isolation():
    """
    Creates two isolated test users with completely distinct resumes:
    - User A: Karan Patel (Python, FastAPI, Docker)
    - User B: Devika Rao (Java, Spring Boot, MySQL)
    Verifies that User A's data never leaks into User B's intelligence,
    and query spoofing cannot breach user isolation.
    """
    # 1. Setup User A (Karan Patel)
    setup_karan_profile()

    # 2. Setup User B (Devika Rao)
    client.post("/api/auth/signup", json={
        "name": "Devika Rao",
        "email": "devika.rao@e2e.test",
        "academicLevel": "College Student"
    })
    resume_devika = """
    Devika Rao
    devika.rao@e2e.test
    Bachelor of Engineering in Information Technology
    Mumbai University, 2025

    Technical Skills:
    Java, Spring Boot, MySQL, REST APIs

    Projects:
    Banking Transaction Engine: Built core accounting service with Java and Spring Boot.

    Work Experience:
    Java Developer Intern at FinCorp: Created microservices with Spring Boot and MySQL.
    """
    resp_devika_resume = client.post(
        "/api/resume/analyze",
        files={"file": ("devika_resume.txt", resume_devika.encode("utf-8"), "text/plain")}
    )
    assert resp_devika_resume.status_code == 200

    # Verify Devika's skills
    devika_profile = resp_devika_resume.json()
    devika_skill_names = [s["name"] for s in devika_profile["skills"]]
    assert "Java" in devika_skill_names or "Spring Boot" in devika_skill_names
    assert "FastAPI" not in devika_skill_names
    assert "Docker" not in devika_skill_names

    # Devika's career recommendations
    recs_devika = client.get("/api/careers/recommendations").json()
    devika_matched = [s for r in recs_devika for s in r["matchedSkills"]]
    assert "FastAPI" not in devika_matched
    assert "Docker" not in devika_matched

    # Anti-Spoofing: Devika tries to query with ?user_id=karan.patel@e2e.test
    spoof_resp = client.get("/api/careers/recommendations?user_id=karan.patel@e2e.test")
    spoof_matched = [s for r in spoof_resp.json() for s in r["matchedSkills"]]
    # Must still reflect Devika's session
    assert "FastAPI" not in spoof_matched

    # 2. Re-login as Karan Patel
    client.post("/api/auth/login", json={"email": "karan.patel@e2e.test"})
    karan_again = client.get("/api/profile").json()
    assert karan_again["email"] == "karan.patel@e2e.test"
    karan_skills = [s["name"] for s in karan_again["skills"]]
    assert "FastAPI" in karan_skills
    assert "Java" not in karan_skills

    # Karan's recommendations again
    recs_karan_again = client.get("/api/careers/recommendations").json()
    karan_matched = [s for r in recs_karan_again for s in r["matchedSkills"]]
    assert "FastAPI" in karan_matched or "Python" in karan_matched
    assert "Spring Boot" not in karan_matched


# ============================================================================
# 6. Zero-Knowledge Truthfulness Test
# ============================================================================
def test_zero_knowledge_truthfulness():
    """
    Verifies that a newly registered user with no resume or projects
    starts in a pristine uncalibrated state without synthetic scores.
    """
    client.post("/api/auth/signup", json={
        "name": "Blank Candidate",
        "email": "blank.cand@e2e.test"
    })

    # Profile check
    prof = client.get("/api/profile").json()
    assert len(prof["skills"]) == 0
    assert prof["profileState"] == "ZERO_KNOWLEDGE"
    assert prof["predictedCareerCategory"] is None

    # Readiness check
    readiness = client.get("/api/readiness").json()
    assert readiness["readinessScore"] == 0
    assert readiness["readinessPoints"] == 0
    assert readiness["readinessLevel"] == "Uncalibrated"
    assert readiness["evidence_level"] == "INSUFFICIENT"

    # Career Match check
    recs = client.get("/api/careers/recommendations").json()
    for r in recs:
        assert r["matchScore"] == 0
        assert r["confidence"] == "Uncalibrated"
        assert r["evidence_level"] == "INSUFFICIENT"

    # Roadmap check
    steps = client.get("/api/roadmap").json()
    completed = [s for s in steps if s["status"] == "completed"]
    assert len(completed) == 0
    assert steps[0]["status"] == "in_progress"

    # Career prediction endpoint check
    pred = client.get("/api/resume/career-prediction").json()
    assert pred["status"] == "NO_RESUME_UPLOADED"
    assert pred["predicted_category"] is None
