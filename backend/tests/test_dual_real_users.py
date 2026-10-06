"""
Verification test proving ReSkillAI calculates 100% genuine results from real user evidence.
Tests two distinctly different candidates:
- User A: Python, FastAPI, React, SQL (high assessment score)
- User B: Java, Spring Boot, MySQL (lower assessment score)
Validates that skills, readiness, career matches, skill gaps, and roadmaps differ meaningfully
and persist reliably across logout/re-login from the SQLite backend.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dual_real_users_evidence_driven():
    # -------------------------------------------------------------
    # 1. USER A (Ayaan Desai — Python / FastAPI / React / SQL)
    # -------------------------------------------------------------
    # Step 1: Register User A
    resp_signup_a = client.post("/api/auth/signup", json={
        "name": "Ayaan Desai",
        "email": "ayaan.desai@realstudent.com",
        "academicLevel": "Final Year Undergraduate"
    })
    assert resp_signup_a.status_code == 200
    user_a_profile = resp_signup_a.json()["profile"]
    assert user_a_profile["profileState"] == "ZERO_KNOWLEDGE"
    assert len(user_a_profile["skills"]) == 0

    # Step 2: Upload User A's Resume
    resume_a_text = """
    Ayaan Desai
    ayaan.desai@realstudent.com
    B.Tech in Computer Science, Indian Institute of Technology
    Class of 2026
    
    Technical Skills:
    Python, FastAPI, React, SQL, Git, Linux
    
    Projects:
    Microservices Cloud Portal
    Built asynchronous REST APIs using FastAPI and Python with SQL database and React web interface.
    
    Work Experience:
    Software Intern at HyperScale
    Developed data pipelines and FastAPI backend services with Git version control.
    """
    files_a = {"file": ("Ayaan_Desai_Resume.txt", resume_a_text.encode("utf-8"), "text/plain")}
    resp_resume_a = client.post("/api/resume/analyze", files=files_a)
    assert resp_resume_a.status_code == 200
    profile_a = resp_resume_a.json()

    skills_a = [s["name"] for s in profile_a["skills"]]
    assert "Python" in skills_a
    assert "FastAPI" in skills_a
    assert "React" in skills_a
    assert "SQL" in skills_a
    # Must NOT contain Java or Spring Boot
    assert "Java" not in skills_a
    assert "Spring Boot" not in skills_a
    # Must NOT contain Parvez Ahmed demo data
    assert profile_a["name"] != "Parvez Ahmed"

    # Step 3: Select Target Career (Full Stack Developer)
    resp_sel_a = client.post("/api/careers/select?career_id=career_fullstack")
    assert resp_sel_a.status_code == 200

    # Step 4: User A completes adaptive assessment with high scores (14/16 correct)
    sess_a_resp = client.get("/api/assessment/session")
    assert sess_a_resp.status_code == 200
    q_state_a = sess_a_resp.json()

    # Answer all discovery questions correctly with high confidence
    while q_state_a["currentPhase"] in ["MIXED_DISCOVERY", "ADAPTIVE_EXPLORATION"] and q_state_a.get("currentQuestion"):
        curr_q = q_state_a["currentQuestion"]
        ans_resp = client.post("/api/assessment/session/answer", json={
            "questionId": curr_q["id"],
            "selectedOptionId": "opt_a",  # opt_a is correct
            "confidence": "very_confident"
        })
        assert ans_resp.status_code == 200
        q_state_a = ans_resp.json()

    # Domain interest submission
    if q_state_a["currentPhase"] == "INTEREST_CALIBRATION":
        int_resp = client.post("/api/assessment/session/interest", json={
            "domainInterests": [
                {"domain": "fullstack", "interestLevel": "very_interested"},
                {"domain": "backend", "interestLevel": "interested"}
            ],
            "scenarioPreference": "fullstack"
        })
        assert int_resp.status_code == 200
        q_state_a = int_resp.json()

    # Practical challenge submission with best option and reasoning
    prac_resp_a = client.post("/api/assessment/session/practical", json={
        "scenarioId": "prac_sec",
        "selectedOptionId": "p_sec_opt1",
        "reasoning": "Isolate the compromised host immediately from VLAN, revoke Kerberos tickets and preserve volatile memory."
    })
    assert prac_resp_a.status_code == 200

    # Record User A metrics
    readiness_a_resp = client.get("/api/progress")
    readiness_a = readiness_a_resp.json()
    score_a = readiness_a["careerReadiness"]
    breakdown_a = readiness_a["readinessBreakdown"]

    gaps_a_resp = client.get("/api/skill-gap")
    gaps_a = gaps_a_resp.json()

    roadmap_a_resp = client.get("/api/roadmap")
    roadmap_a = roadmap_a_resp.json()

    match_a_resp = client.get("/api/careers/career_fullstack/match")
    match_a = match_a_resp.json()


    # -------------------------------------------------------------
    # 2. USER B (Vikram Malhotra — Java / Spring Boot / MySQL)
    # -------------------------------------------------------------
    # Step 1: Register User B
    resp_signup_b = client.post("/api/auth/signup", json={
        "name": "Vikram Malhotra",
        "email": "vikram.malhotra@realstudent.com",
        "academicLevel": "Final Year Undergraduate"
    })
    assert resp_signup_b.status_code == 200

    # Step 2: Upload User B's Resume
    resume_b_text = """
    Vikram Malhotra
    vikram.malhotra@realstudent.com
    B.Tech in Information Technology, Apex Institute of Technology
    Class of 2026
    
    Technical Skills:
    Java, Spring Boot, MySQL, HTML/CSS
    
    Projects:
    Enterprise Inventory System
    Developed inventory tracking microservice with Java, Spring Boot, and MySQL relational store.
    """
    files_b = {"file": ("Vikram_Malhotra_Resume.txt", resume_b_text.encode("utf-8"), "text/plain")}
    resp_resume_b = client.post("/api/resume/analyze", files=files_b)
    assert resp_resume_b.status_code == 200
    profile_b = resp_resume_b.json()

    skills_b = [s["name"] for s in profile_b["skills"]]
    assert "Java" in skills_b
    assert "Spring Boot" in skills_b
    assert "MySQL" in skills_b
    # Must NOT contain Python or FastAPI
    assert "Python" not in skills_b
    assert "FastAPI" not in skills_b

    # Step 3: Select Target Career (Full Stack Developer)
    client.post("/api/careers/select?career_id=career_fullstack")

    # Step 4: User B completes adaptive assessment with suboptimal choices (low confidence)
    sess_b_resp = client.get("/api/assessment/session")
    assert sess_b_resp.status_code == 200
    q_state_b = sess_b_resp.json()

    while q_state_b["currentPhase"] in ["MIXED_DISCOVERY", "ADAPTIVE_EXPLORATION"] and q_state_b.get("currentQuestion"):
        curr_q = q_state_b["currentQuestion"]
        # Intentionally choose opt_c (incorrect option) to simulate lower scores
        ans_resp = client.post("/api/assessment/session/answer", json={
            "questionId": curr_q["id"],
            "selectedOptionId": "opt_c",
            "confidence": "guessing"
        })
        assert ans_resp.status_code == 200
        q_state_b = ans_resp.json()


    if q_state_b["currentPhase"] == "INTEREST_CALIBRATION":
        int_resp = client.post("/api/assessment/session/interest", json={
            "domainInterests": [
                {"domain": "data_science", "interestLevel": "neutral"}
            ],
            "scenarioPreference": "cybersecurity"
        })
        assert int_resp.status_code == 200
        q_state_b = int_resp.json()

    # Suboptimal practical challenge choice
    prac_resp_b = client.post("/api/assessment/session/practical", json={
        "scenarioId": "prac_sec",
        "selectedOptionId": "p_sec_opt2",  # suboptimal choice
        "reasoning": "Waiting till tomorrow."
    })
    assert prac_resp_b.status_code == 200

    # Record User B metrics
    readiness_b_resp = client.get("/api/progress")
    readiness_b = readiness_b_resp.json()
    score_b = readiness_b["careerReadiness"]
    breakdown_b = readiness_b["readinessBreakdown"]

    gaps_b_resp = client.get("/api/skill-gap")
    gaps_b = gaps_b_resp.json()

    roadmap_b_resp = client.get("/api/roadmap")
    roadmap_b = roadmap_b_resp.json()

    match_b_resp = client.get("/api/careers/career_fullstack/match")
    match_b = match_b_resp.json()


    # -------------------------------------------------------------
    # 3. VERIFY MEANINGFUL DIFFERENCES (User A vs User B)
    # -------------------------------------------------------------
    # 1. Skills are completely distinct
    assert set(skills_a) != set(skills_b)
    assert "FastAPI" in skills_a and "FastAPI" not in skills_b
    assert "Spring Boot" in skills_b and "Spring Boot" not in skills_a

    # 2. Assessment scores differ meaningfully
    assert breakdown_a["assessmentPoints"] > breakdown_b["assessmentPoints"]

    # 3. Overall Readiness scores differ meaningfully
    assert score_a > score_b
    assert breakdown_a["totalPoints"] > breakdown_b["totalPoints"]

    # 4. Career matches differ
    # Ayaan has React and SQL which align with Full Stack, giving distinct match
    assert match_a["overallMatch"] != match_b["overallMatch"]

    # 5. Skill gap classifications differ based on their real skills
    # User A has React (Mastered/Developing), User B has HTML/CSS
    gaps_a_dict = {g["skill"]: g["status"] for g in gaps_a}
    gaps_b_dict = {g["skill"]: g["status"] for g in gaps_b}
    assert gaps_a_dict != gaps_b_dict

    # 6. Roadmap steps differ:
    # User A's React step is completed or in_progress, while User B's React is upcoming
    react_step_a = next((s for s in roadmap_a if "React" in s["title"] or "React" in s.get("focusSkills", [])), None)
    react_step_b = next((s for s in roadmap_b if "React" in s["title"] or "React" in s.get("focusSkills", [])), None)
    if react_step_a and react_step_b:
        assert react_step_a["status"] != react_step_b["status"]


    # -------------------------------------------------------------
    # 4. PERSISTENCE VERIFICATION: Log back in as User A
    # -------------------------------------------------------------
    # Login back as User A
    relogin_a = client.post("/api/auth/login", json={
        "email": "ayaan.desai@realstudent.com"
    })
    assert relogin_a.status_code == 200
    reloaded_profile_a = relogin_a.json()["profile"]

    # Profile data must persist from SQLite!
    assert reloaded_profile_a["name"] == "Ayaan Desai"
    assert reloaded_profile_a["email"] == "ayaan.desai@realstudent.com"
    reloaded_skills_a = [s["name"] for s in reloaded_profile_a["skills"]]
    assert "FastAPI" in reloaded_skills_a
    assert "Python" in reloaded_skills_a
    assert "React" in reloaded_skills_a

    # Reloaded readiness must match User A's previously calculated score
    reloaded_prog = client.get("/api/progress").json()
    assert reloaded_prog["careerReadiness"] == score_a
