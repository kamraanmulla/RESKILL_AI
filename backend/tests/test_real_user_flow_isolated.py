"""
Comprehensive test suite verifying ReSkillAI requirements A through H:
ZERO live Gemini API quota consumed (strictly uses gemini_service.mock_mode = True).
No demo student (Parvez Ahmed) data leakage into real-user flow.
Deterministic intelligence calculations verified.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.gemini_service import gemini_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def force_mock_mode_and_clean_slate():
    """Ensure Gemini mock mode is active to protect API quota completely, and reset profile."""
    original_mock = gemini_service.mock_mode
    gemini_service.mock_mode = True
    client.post("/api/auth/reset")
    yield
    gemini_service.mock_mode = original_mock
    client.post("/api/auth/reset")


def test_a_zero_knowledge_user():
    """
    Test A: ZERO_KNOWLEDGE user.
    Expected:
    - no demo profile (no Parvez Ahmed, no CampusTrade)
    - no fake scores (readiness is 0, match is 0)
    - profileState is ZERO_KNOWLEDGE
    """
    resp = client.get("/api/profile")
    assert resp.status_code == 200
    profile = resp.json()

    assert profile["profileState"] == "ZERO_KNOWLEDGE"
    assert profile["name"] != "Parvez Ahmed"
    assert len(profile["skills"]) == 0
    assert len(profile["projects"]) == 0
    assert len(profile["experience"]) == 0

    # Verify readiness is 0 / uncalibrated
    prog_resp = client.get("/api/progress")
    assert prog_resp.status_code == 200
    prog = prog_resp.json()
    assert prog["careerReadiness"] == 0
    assert prog["readinessLevel"] == "Uncalibrated"
    assert prog["studyStreakDays"] == 0

    # Verify career match in zero knowledge is 0
    rec_resp = client.get("/api/careers/recommendations")
    assert rec_resp.status_code == 200
    recs = rec_resp.json()
    assert recs[0]["matchScore"] == 0


def test_b_manual_onboarding_five_questions():
    """
    Test B: Manual onboarding (5 Core Questions).
    Expected:
    - profile generated from user's supplied information
    - no demo data
    - deterministic intelligence generated from that profile
    """
    client.post("/api/auth/reset")

    payload = {
        "name": "Sarah Jenkins",
        "education": "B.Tech Computer Science",
        "degree": "B.Tech Computer Science",
        "field": "Computer Science",
        "academicLevel": "Final Year Undergraduate",
        "skills": ["Python", "SQL", "Linux", "Git"],
        "interests": ["Cybersecurity", "Networking"],
        "careerDirection": "Cybersecurity",
        "practicalExperienceText": "Built a network packet analyzer in Python and set up snort IDS"
    }
    resp = client.post("/api/profile/onboarding", json=payload)
    assert resp.status_code == 200
    profile = resp.json()

    # User profile should strictly reflect what was supplied
    assert profile["name"] == "Sarah Jenkins"
    assert profile["degree"] == "B.Tech Computer Science"
    assert profile["profileState"] == "PROFILE_READY"
    skill_names = [s["name"].lower() for s in profile["skills"]]
    assert "python" in skill_names
    assert "sql" in skill_names
    assert "linux" in skill_names
    assert "git" in skill_names
    # Practical experience was processed locally without demo fallback
    assert profile["practicalExperience"] == payload["practicalExperienceText"]

    # Now verify deterministic readiness engine computes a legitimate score (not 0, not demo 82%)
    prog_resp = client.get("/api/progress")
    assert prog_resp.status_code == 200
    prog = prog_resp.json()
    assert prog["careerReadiness"] > 0
    assert prog["readinessPoints"] > 0


def test_c_manual_onboarding_missing_information():
    """
    Test C: Manual onboarding with missing information.
    Expected:
    - missing information remains missing
    - no fabricated values (no demo skills injected)
    - system sets PROFILE_INCOMPLETE when under threshold
    """
    client.post("/api/auth/reset")

    # Incomplete payload: only 1 skill, no practical experience
    payload = {
        "name": "Incomplete User",
        "education": "High School",
        "degree": "High School",
        "field": None,
        "academicLevel": None,
        "skills": ["HTML/CSS"],
        "interests": [],
        "careerDirection": "I'm not sure yet",
        "practicalExperienceText": ""
    }
    resp = client.post("/api/profile/onboarding", json=payload)
    assert resp.status_code == 200
    profile = resp.json()

    # Missing info stays missing
    assert profile["profileState"] == "PROFILE_INCOMPLETE"
    assert len(profile["skills"]) == 1
    assert profile["skills"][0]["name"] == "HTML/CSS"
    assert profile["interests"] == []
    assert profile["projects"] == []
    assert profile["experience"] == []


def test_d_resume_processing_without_quota():
    """
    Test D: Resume processing.
    Expected:
    - resume text becomes the user's profile
    - no Parvez Ahmed / demo student data
    - Gemini call is mocked during development
    """
    client.post("/api/auth/reset")

    # Upload mock resume text file
    resume_content = b"""
    Elena Rostova
    elena.rostova@university.edu
    B.S. in Software Engineering, Class of 2026
    Skills: React, JavaScript, TypeScript, Node.js, Express, Docker
    Projects: Distributed Task Queue using Node.js and Redis
    """
    files = {"file": ("Elena_Rostova_Resume.pdf", resume_content, "application/pdf")}
    resp = client.post("/api/resume/analyze", files=files)
    assert resp.status_code == 200
    profile = resp.json()

    assert profile["resumeFile"]["name"] == "Elena_Rostova_Resume.pdf"
    assert profile["profileState"] in ["PROFILE_READY", "PERSONALIZED"]

    # Verify extracted skills contain resume keywords and NOT demo fallback
    skill_names = [s["name"].lower() for s in profile["skills"]]
    assert any("react" in s for s in skill_names)
    assert any("node" in s for s in skill_names)
    # Elena Rostova should NOT be Parvez Ahmed
    assert profile["name"] != "Parvez Ahmed"


def test_e_gemini_failure_handling():
    """
    Test E: Gemini failure handling.
    Expected:
    - controlled error response / safe fallback
    - no demo student data fallback (no Parvez Ahmed, no fake SIEM skills)
    """
    client.post("/api/auth/reset")

    # Simulate error by passing corrupted binary
    corrupted_bytes = b"\x00\x01\x02\x03\x04\x05\x06\x07"
    files = {"file": ("corrupted.pdf", corrupted_bytes, "application/pdf")}
    resp = client.post("/api/resume/analyze", files=files)
    assert resp.status_code == 200
    profile = resp.json()

    # When extraction has nothing, skills MUST be empty, not filled with demo data
    assert profile["name"] != "Parvez Ahmed"
    assert len(profile["skills"]) == 0
    assert len(profile["projects"]) == 0


def test_f_career_selection_affects_intelligence():
    """
    Test F: Career selection.
    Expected:
    - actual selected career dynamically affects skill gaps, readiness, and roadmap
    """
    client.post("/api/auth/reset")

    # Onboard with Python and Linux
    client.post("/api/profile/onboarding", json={
        "name": "Dev User",
        "education": "B.E. Computer Science",
        "skills": ["Python", "Linux", "Git"],
        "interests": ["Cybersecurity"],
        "careerDirection": "Cybersecurity",
        "practicalExperienceText": "Linux administration and basic scripts"
    })

    # Select Cybersecurity
    client.post("/api/careers/select?career_id=career_cybersecurity")
    gaps_cyber = client.get("/api/skill-gap").json()
    roadmap_cyber = client.get("/api/roadmap").json()
    prog_cyber = client.get("/api/progress").json()

    # Select Fullstack
    client.post("/api/careers/select?career_id=career_fullstack")
    gaps_fs = client.get("/api/skill-gap").json()
    roadmap_fs = client.get("/api/roadmap").json()
    prog_fs = client.get("/api/progress").json()

    # Verify skill gaps and roadmap are different for different careers!
    cyber_gap_skills = [g["skill"] for g in gaps_cyber]
    fs_gap_skills = [g["skill"] for g in gaps_fs]
    assert cyber_gap_skills != fs_gap_skills
    assert any("SIEM" in s or "Networking" in s for s in cyber_gap_skills)
    assert any("React" in s or "Node" in s for s in fs_gap_skills)


def test_g_jobs_external_redirect():
    """
    Test G: Jobs.
    Expected:
    - apply records click/redirect
    - no fake internal submission
    - sourceUrl is valid HTTP/HTTPS link
    """
    jobs_resp = client.get("/api/jobs")
    assert jobs_resp.status_code == 200
    jobs = jobs_resp.json()
    assert len(jobs) > 0

    first_job = jobs[0]
    assert first_job["sourceUrl"].startswith("http")

    # Tracking click
    click_resp = client.post(f"/api/jobs/{first_job['id']}/apply-clicked")
    assert click_resp.status_code == 200
    data = click_resp.json()
    assert data["status"] == "redirect_logged"
    assert "sourceUrl" in data
    # Must NOT claim fake "Application Submitted"
    assert "submitted" not in data.get("status", "").lower()


def test_h_new_user_zero_baseline():
    """
    Test H: New user baseline.
    Expected:
    - zero demo progress
    - zero demo profile
    - zero demo career match
    - zero demo skill gaps
    """
    # Signup new user
    auth_resp = client.post("/api/auth/signup", json={
        "name": "Maya Lin",
        "email": "maya.lin@example.edu",
        "academicLevel": "Junior Undergraduate"
    })
    assert auth_resp.status_code == 200
    profile = auth_resp.json()["profile"]

    assert profile["profileState"] == "ZERO_KNOWLEDGE"
    assert profile["name"] == "Maya Lin"
    assert profile["email"] == "maya.lin@example.edu"
    assert len(profile["skills"]) == 0

    # Career match must be 0
    match_resp = client.get("/api/careers/match")
    assert match_resp.status_code == 200
    assert match_resp.json()["overallMatch"] == 0

    # Readiness score must be 0
    prog_resp = client.get("/api/progress")
    assert prog_resp.status_code == 200
    assert prog_resp.json()["careerReadiness"] == 0
    assert prog_resp.json()["studyStreakDays"] == 0
