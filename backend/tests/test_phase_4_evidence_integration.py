"""
ReSkillAI Phase 4: Real User Evidence Integration Test Suite
Verifies:
1. Zero-Knowledge User handling (no fake scores)
2. Resume-only user evidence (assessment marked NOT_AVAILABLE)
3. Resume + Assessment user evidence combination
4. Project evidence corroboration
5. Unknown / unmentioned skill safety
6. Strict Multi-User Isolation (User A vs User B cannot cross-leak)
7. Security: authenticated session enforcement
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_zero_knowledge_user_evidence():
    """Step 20: New user with no evidence receives INSUFFICIENT_EVIDENCE without fake scores."""
    # Register fresh Zero-Knowledge user
    resp_signup = client.post("/api/auth/signup", json={
        "name": "Zero Knowledge Candidate",
        "email": "zk.candidate@testdomain.com",
        "academicLevel": "Undergraduate"
    })
    assert resp_signup.status_code == 200

    # Query evidence profile
    resp_evidence = client.get("/api/intelligence/skill-evidence")
    assert resp_evidence.status_code == 200
    data = resp_evidence.json()

    assert data["userId"].startswith(("std_", "usr_"))
    # All skills evaluated must be INSUFFICIENT_EVIDENCE
    for item in data["skills"]:
        assert item["status"] == "INSUFFICIENT_EVIDENCE"
        assert item["evidence_strength"] is None
        assert item["confidence"] == 0.0
        assert len(item["evidence_sources"]) == 0
        assert item["source_states"]["resume"] == "NOT_AVAILABLE"
        assert item["source_states"]["assessment"] == "NOT_AVAILABLE"


def test_resume_only_user_evidence():
    """Step 21: Real user with resume only has resume=PRESENT, assessment=NOT_AVAILABLE."""
    # Register candidate
    client.post("/api/auth/signup", json={
        "name": "Resume Only Candidate",
        "email": "resume.only@testdomain.com",
        "academicLevel": "Third Year Student"
    })

    # Upload resume mentioning Python, SQL, Docker
    resume_text = """
    Resume Only Candidate
    resume.only@testdomain.com
    B.S. in Computer Science
    
    Technical Skills:
    Python, SQL, Docker, Git
    
    Work Experience:
    Junior Developer at TechCorp
    Developed backend REST services in Python and SQL. Deployed containers using Docker.
    """
    files = {"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")}
    resp_resume = client.post("/api/resume/analyze", files=files)
    assert resp_resume.status_code == 200

    # Query evidence for Python
    resp_py = client.get("/api/intelligence/skill-evidence/Python")
    assert resp_py.status_code == 200
    py_data = resp_py.json()

    assert py_data["skill"] == "Python"
    assert py_data["source_states"]["resume"] == "PRESENT"
    assert py_data["source_states"]["assessment"] == "NOT_AVAILABLE"
    assert "resume" in py_data["evidence_sources"]
    assert "assessment" not in py_data["evidence_sources"]
    assert py_data["evidence_strength"] is not None
    assert py_data["evidence_strength"] >= 0.50
    assert py_data["status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]


def test_user_with_resume_and_assessment():
    """Step 22: User with both resume and assessment combines both evidence signals."""
    # Register candidate
    client.post("/api/auth/signup", json={
        "name": "Full Evidence Candidate",
        "email": "full.evidence@testdomain.com",
        "academicLevel": "Final Year Student"
    })

    # Upload resume with Python and React
    resume_text = """
    Full Evidence Candidate
    full.evidence@testdomain.com
    
    Technical Skills:
    Python, React, Linux
    
    Experience:
    Software Engineering Intern
    Developed web dashboards using Python and React with Linux servers.
    """
    client.post("/api/resume/analyze", files={"file": ("resume.txt", resume_text.encode("utf-8"), "text/plain")})

    # Submit assessment with Software Engineering orientation
    client.post("/api/assessment/submit", json={
        "answers": {
            "q1": "q1_sw",
            "q2": "q2_fix",
            "q3": "q3_prod",
            "q4": "q4_grow"
        }
    })

    # Query evidence for Python
    resp_py = client.get("/api/intelligence/skill-evidence/Python")
    assert resp_py.status_code == 200
    py_data = resp_py.json()

    assert "resume" in py_data["evidence_sources"]
    assert "assessment" in py_data["evidence_sources"]
    assert py_data["source_states"]["resume"] == "PRESENT"
    assert py_data["source_states"]["assessment"] == "PRESENT"
    assert py_data["confidence"] >= 0.50
    assert "assessment" in py_data["explanation"]


def test_project_evidence_corroboration():
    """Step 23: Profile containing projects corroborates skill with project source."""
    client.post("/api/auth/signup", json={
        "name": "Project Candidate",
        "email": "project.cand@testdomain.com"
    })

    # Update profile directly with a project
    profile_resp = client.get("/api/profile")
    profile_data = profile_resp.json()
    profile_data["projects"] = [
        {
            "title": "Cloud Analytics Engine",
            "tech": ["Python", "Docker", "AWS"],
            "description": "Architected distributed streaming pipelines in Python using Docker on AWS.",
            "period": "2025"
        }
    ]
    client.put("/api/profile", json=profile_data)

    # Query evidence for Docker
    resp_docker = client.get("/api/intelligence/skill-evidence/Docker")
    assert resp_docker.status_code == 200
    docker_data = resp_docker.json()

    assert "project" in docker_data["evidence_sources"]
    assert docker_data["source_states"]["project"] == "PRESENT"
    assert docker_data["details"]["project_count"] >= 1
    assert "Cloud Analytics Engine" in docker_data["explanation"]


def test_unknown_unmentioned_skill():
    """Step 24: Querying an absent skill returns UNSUPPORTED without negative proficiency."""
    client.post("/api/auth/signup", json={
        "name": "Specialist Candidate",
        "email": "specialist@testdomain.com"
    })
    # Resume only has Python
    resume_text = "Python developer building APIs."
    client.post("/api/resume/analyze", files={"file": ("res.txt", resume_text.encode("utf-8"), "text/plain")})

    # Query unmentioned skill
    resp_rust = client.get("/api/intelligence/skill-evidence/Rust")
    assert resp_rust.status_code == 200
    rust_data = resp_rust.json()

    assert rust_data["status"] == "UNSUPPORTED"
    assert rust_data["evidence_strength"] is None
    assert rust_data["confidence"] == 0.0
    assert len(rust_data["evidence_sources"]) == 0
    assert "No active evidence supports Rust" in rust_data["explanation"]


def test_multi_user_isolation():
    """Step 19: Strict multi-user isolation. User Alpha evidence cannot leak to User Beta."""
    # 1. Setup User Alpha (Python / FastAPI)
    client.post("/api/auth/signup", json={
        "name": "Alpha Candidate",
        "email": "user.alpha@isolation.com"
    })
    resume_alpha = """
    Alpha Candidate
    user.alpha@isolation.com

    Technical Skills:
    Python, FastAPI, React

    Work Experience:
    Backend Engineer at TechCorp
    Developed microservices with Python and FastAPI.
    """
    client.post("/api/resume/analyze", files={"file": ("alpha.txt", resume_alpha.encode("utf-8"), "text/plain")})

    # Verify Alpha sees Python but NOT Java
    resp_alpha_py = client.get("/api/intelligence/skill-evidence/Python")
    assert resp_alpha_py.json()["status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]
    resp_alpha_java = client.get("/api/intelligence/skill-evidence/Java")
    assert resp_alpha_java.json()["status"] == "UNSUPPORTED"

    # 2. Setup User Beta (Java / Spring Boot)
    client.post("/api/auth/signup", json={
        "name": "Beta Candidate",
        "email": "user.beta@isolation.com"
    })
    resume_beta = """
    Beta Candidate
    user.beta@isolation.com

    Technical Skills:
    Java, Spring Boot, MySQL

    Work Experience:
    Enterprise Software Engineer at BankCorp
    Engineered enterprise banking services with Java and Spring Boot.
    """
    client.post("/api/resume/analyze", files={"file": ("beta.txt", resume_beta.encode("utf-8"), "text/plain")})

    # Verify Beta sees Java but NOT Python
    resp_beta_java = client.get("/api/intelligence/skill-evidence/Java")
    assert resp_beta_java.json()["status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]
    resp_beta_py = client.get("/api/intelligence/skill-evidence/Python")
    assert resp_beta_py.json()["status"] == "UNSUPPORTED"

    # 3. Log back in as Alpha
    client.post("/api/auth/login", json={"email": "user.alpha@isolation.com"})
    resp_alpha_again = client.get("/api/intelligence/skill-evidence/Python")
    assert resp_alpha_again.json()["status"] in ["SUPPORTED", "MODERATE_EVIDENCE"]
    # Still must NOT see Beta's Java
    resp_alpha_java_again = client.get("/api/intelligence/skill-evidence/Java")
    assert resp_alpha_java_again.json()["status"] == "UNSUPPORTED"


def test_security_session_isolation():
    """Step 25: Security tests. User evidence cannot be accessed via arbitrary parameters."""
    client.post("/api/auth/signup", json={
        "name": "Secure Candidate",
        "email": "secure.candidate@security.com"
    })
    # Cannot pass arbitrary user_id parameter to override active session
    resp = client.get("/api/intelligence/skill-evidence?user_id=attacker_override_id")
    assert resp.status_code == 200
    data = resp.json()
    assert data["userId"] != "attacker_override_id"
    assert data["userId"].startswith(("std_", "usr_"))
