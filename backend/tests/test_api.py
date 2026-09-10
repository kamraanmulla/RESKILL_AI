import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_auth_reset_zero_knowledge():
    response = client.post("/api/auth/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["profileState"] == "ZERO_KNOWLEDGE"
    assert len(data["skills"]) == 0

def test_5_questions_onboarding():
    client.post("/api/auth/reset")
    payload = {
        "name": "Aarav Sharma",
        "education": "B.E. Computer Science",
        "degree": "B.E. Computer Science",
        "field": "Computer Science",
        "academicLevel": "College Student",
        "skills": ["Python", "SQL", "Linux", "Git"],
        "interests": ["Cybersecurity"],
        "careerDirection": "Cybersecurity",
        "practicalExperienceText": "Built a network packet sniffer in Python and configured iptables"
    }
    response = client.post("/api/profile/onboarding", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["profileState"] in ["PROFILE_READY", "PROFILE_INCOMPLETE", "PERSONALIZED"]
    assert len(data["skills"]) >= 4

def test_assessment_flow():
    # Fetch questions
    q_resp = client.get("/api/assessment/questions")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) == 4

    # Submit answers
    submission = {
        "answers": {
            q["id"]: q["options"][0]["id"] for q in questions
        }
    }
    s_resp = client.post("/api/assessment/submit", json=submission)
    assert s_resp.status_code == 200
    res = s_resp.json()
    assert res["profileState"] in ["PROFILE_INCOMPLETE", "PROFILE_READY", "PERSONALIZED"]

def test_career_recommendations_api():
    response = client.get("/api/careers/recommendations")
    assert response.status_code == 200
    recs = response.json()
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert "matchScore" in recs[0]

def test_career_selection_and_skill_gap():
    # Select career with query param or JSON
    sel_resp = client.post("/api/careers/select?career_id=career_cybersecurity")
    assert sel_resp.status_code == 200
    
    # Check skill gap
    gap_resp = client.get("/api/skill-gap")
    assert gap_resp.status_code == 200
    gaps = gap_resp.json()
    assert len(gaps) > 0

    # Check roadmap
    road_resp = client.get("/api/roadmap")
    assert road_resp.status_code == 200
    roadmap = road_resp.json()
    assert len(roadmap) > 0

def test_jobs_with_source_url():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) > 0
    # Every job MUST have a real sourceUrl and source
    for j in jobs:
        assert j["sourceUrl"].startswith("http")
        assert j["source"] in ["LinkedIn", "Company Website", "Indeed", "Glassdoor"]
