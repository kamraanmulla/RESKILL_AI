import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.intelligence.adaptive_assessment_engine import (
    adaptive_assessment_engine,
    QUESTION_BANK,
    PRACTICAL_CHALLENGES,
    CANONICAL_DOMAINS
)
from app.intelligence.advanced.combination_engine import CombinationEngine
from app.intelligence.advanced.transferability_engine import TransferabilityEngine
from app.intelligence.skill_gap_engine import SkillGapEngine
from app.intelligence.roadmap_engine import RoadmapEngine
from app.api.routes.profile_store import get_profile, set_profile, reset_to_zero_knowledge
from app.schemas.profile import StudentProfile, Skill

client = TestClient(app)

# ==============================================================================
# 1. Mixed Discovery Question Generation & Distribution
# ==============================================================================
def test_mixed_discovery_questions_distribution():
    discovery_qs = adaptive_assessment_engine.get_discovery_questions()
    assert len(discovery_qs) == 10

    # Ensure questions are NOT all from one domain
    domains_represented = set(q["domain"] for q in discovery_qs)
    assert len(domains_represented) >= 6, f"Expected broad distribution, got {domains_represented}"

    # Verify all 7 canonical domains are supported in the bank
    bank_domains = set(q["domain"] for q in QUESTION_BANK)
    expected_domains = {"cybersecurity", "backend", "frontend", "cloud_devops", "ai_ml", "data_science", "fullstack"}
    assert expected_domains.issubset(bank_domains)

    # Check that no single domain has more than 2 questions in the initial 10
    domain_counts = {}
    for q in discovery_qs:
        domain_counts[q["domain"]] = domain_counts.get(q["domain"], 0) + 1
    for d, count in domain_counts.items():
        assert count <= 2, f"Domain {d} has {count} questions, exceeding discovery limit of 2"


# ==============================================================================
# 2. Deterministic Evaluation of MCQs
# ==============================================================================
def test_deterministic_mcq_evaluation():
    # Pick a question from bank
    q = QUESTION_BANK[0]
    correct_opt = q["correctOptionId"]
    wrong_opt = next(o["id"] for o in q["options"] if o["id"] != correct_opt)

    # Calculate signals with correct answer
    scores_correct, evidence_correct, skills_c, _, _ = adaptive_assessment_engine.calculate_domain_knowledge_signals(
        {q["id"]: correct_opt}, {q["id"]: "very_confident"}
    )
    assert scores_correct[q["domain"]] > 50
    assert q["evidenceSkill"] in skills_c[q["domain"]]

    # Calculate signals with wrong answer
    scores_wrong, evidence_wrong, skills_w, _, _ = adaptive_assessment_engine.calculate_domain_knowledge_signals(
        {q["id"]: wrong_opt}, {q["id"]: "very_confident"}
    )
    assert scores_wrong[q["domain"]] <= 20
    assert q["evidenceSkill"] not in skills_w[q["domain"]]


# ==============================================================================
# 3. Adaptive Question Engine & Information Value
# ==============================================================================
def test_adaptive_selection_focuses_on_promising_domains():
    # Candidate performs strongly in Cybersecurity (high score) and has not tested AI/ML
    demonstrated = {
        "cybersecurity": 85,
        "backend": 40,
        "frontend": 20,
        "cloud_devops": 40,
        "ai_ml": 20,
        "data_science": 20,
        "fullstack": 20
    }
    evidence = {
        "cybersecurity": 2,
        "backend": 1,
        "frontend": 1,
        "cloud_devops": 1,
        "ai_ml": 0,
        "data_science": 1,
        "fullstack": 1
    }
    answered_ids = {"q_sec_01", "q_sec_02"}

    next_q = adaptive_assessment_engine.select_next_adaptive_question(
        answered_ids, demonstrated, evidence, total_answered=10
    )
    assert next_q is not None
    # Must investigate promising or ambiguous domains (e.g. Cybersecurity depth or AI/ML ambiguity)
    assert next_q["domain"] in ["cybersecurity", "ai_ml"]


# ==============================================================================
# 4. Question Budget & Non-rigid Stopping (15-20 questions, NEVER 70)
# ==============================================================================
def test_assessment_budget_stops_between_14_and_20():
    # Ensure stopping condition triggers and doesn't force 70 questions
    demonstrated = {d["id"]: 75 for d in CANONICAL_DOMAINS}
    evidence = {d["id"]: 3 for d in CANONICAL_DOMAINS}
    answered_20 = {f"q_{i}": "opt" for i in range(20)}

    next_q = adaptive_assessment_engine.select_next_adaptive_question(
        set(answered_20.keys()), demonstrated, evidence, total_answered=20
    )
    assert next_q is None, "Assessment must stop at or before MAX_QUESTIONS (20)"


# ==============================================================================
# 5. Interest Stored Strictly Separately from Knowledge
# ==============================================================================
def test_interest_stored_separately_from_knowledge():
    # Candidate has low knowledge in AI/ML but Very High interest
    scores = {"ai_ml": 25, "backend": 80}
    evidence = {"ai_ml": 2, "backend": 2}
    skills = {"ai_ml": [], "backend": ["REST APIs", "Node.js"]}
    conf = {"ai_ml": "Medium", "backend": "High"}
    strength = {"ai_ml": "Moderate Evidence", "backend": "Strong Evidence"}
    interests = {"ai_ml": "very_interested", "backend": "not_interested"}
    practicals = {"ai_ml": 30, "backend": 80}

    profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id="test_candidate_archetypes",
        demonstrated_scores=scores,
        domain_evidence_counts=evidence,
        skills_demonstrated=skills,
        confidence_signals=conf,
        evidence_strength=strength,
        interest_ratings=interests,
        scenario_preference="Training ML models",
        practical_scores=practicals,
        total_questions_answered=16
    )

    # Knowledge signal for AI/ML must remain low (25) - NOT artificially boosted to 90
    assert profile.domainSignals["ai_ml"].demonstratedKnowledge == 25
    assert profile.domainSignals["ai_ml"].interestLevel == "Very High"

    # Backend knowledge remains 80, but interest is Low
    assert profile.domainSignals["backend"].demonstratedKnowledge == 80
    assert profile.domainSignals["backend"].interestLevel == "Low"

    # High interest + low knowledge interpretation in observation
    obs = profile.profileObservation.lower()
    assert "high-interest developing pathway" in obs or "ai/ml" in obs
    assert "foundational gaps" in obs


# ==============================================================================
# 6. High Knowledge + Low Interest Handling
# ==============================================================================
def test_high_knowledge_low_interest_observation():
    scores = {"backend": 85, "cybersecurity": 75}
    interests = {"backend": "not_interested", "cybersecurity": "very_interested"}
    evidence = {"backend": 2, "cybersecurity": 2}
    skills = {"backend": ["Node.js", "SQL"], "cybersecurity": ["Incident Response"]}
    conf = {"backend": "High", "cybersecurity": "High"}
    strength = {"backend": "Strong Evidence", "cybersecurity": "Strong Evidence"}
    practicals = {"backend": 80, "cybersecurity": 75}

    profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id="test_high_know_low_int",
        demonstrated_scores=scores,
        domain_evidence_counts=evidence,
        skills_demonstrated=skills,
        confidence_signals=conf,
        evidence_strength=strength,
        interest_ratings=interests,
        scenario_preference=None,
        practical_scores=practicals,
        total_questions_answered=16
    )

    obs = profile.profileObservation.lower()
    assert "transferable" in obs or "adjacent" in obs


# ==============================================================================
# 7. Multi-Domain Profile Triggers Combination Discovery Engine
# ==============================================================================
def test_multi_domain_student_triggers_combination_discovery():
    # Candidate strong across 4 domains
    multi_scores = {
        "cybersecurity": 88,
        "cloud_devops": 85,
        "backend": 82,
        "fullstack": 80,
        "frontend": 60,
        "ai_ml": 40,
        "data_science": 50
    }
    multi_evidence = {d: 3 for d in multi_scores}
    multi_skills = {
        "cybersecurity": ["Linux", "Cybersecurity", "Networking"],
        "cloud_devops": ["Docker", "Linux", "Git"],
        "backend": ["Python", "SQL", "REST APIs"],
        "fullstack": ["JavaScript", "React"],
        "frontend": [],
        "ai_ml": [],
        "data_science": []
    }
    conf = {d: "High" for d in multi_scores}
    strength = {d: "Strong Evidence" for d in multi_scores}
    interests = {d: "very_interested" for d in multi_scores}
    practicals = {d: 80 for d in multi_scores}

    profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id="test_multi_domain_student",
        demonstrated_scores=multi_scores,
        domain_evidence_counts=multi_evidence,
        skills_demonstrated=multi_skills,
        confidence_signals=conf,
        evidence_strength=strength,
        interest_ratings=interests,
        scenario_preference="Security and Systems Architecture",
        practical_scores=practicals,
        total_questions_answered=18
    )

    assert profile.isMultiDomain is True
    assert len(profile.discoveredCombinations) > 0

    combo_careers = [c.career for c in profile.discoveredCombinations]
    # Linux + Git + Cyber + Docker triggers DevSecOps in existing CombinationEngine
    assert any("DevSecOps" in c or "Backend Cloud" in c for c in combo_careers)


# ==============================================================================
# 8. Theory vs. Practical Ability Distinction
# ==============================================================================
def test_theory_vs_practical_distinction():
    scores = {"backend": 85, "cybersecurity": 80}
    # Low practical scores
    practicals = {"backend": 45, "cybersecurity": 40}

    profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id="test_theory_heavy",
        demonstrated_scores=scores,
        domain_evidence_counts={"backend": 2, "cybersecurity": 2},
        skills_demonstrated={"backend": ["SQL"], "cybersecurity": ["Networking"]},
        confidence_signals={"backend": "High", "cybersecurity": "High"},
        evidence_strength={"backend": "Strong Evidence", "cybersecurity": "Strong Evidence"},
        interest_ratings={"backend": "interested", "cybersecurity": "interested"},
        scenario_preference=None,
        practical_scores=practicals,
        total_questions_answered=16
    )

    assert "Strong Conceptual Knowledge" in profile.theoryVsPractical
    assert any("implementation" in dev.lower() or "project" in dev.lower() for dev in profile.suggestedNextDevelopment)


# ==============================================================================
# 9. Breadth > Depth Distinction
# ==============================================================================
def test_breadth_greater_than_depth_detection():
    # Tested in 6 domains, scores ~65, but low practical
    scores = {d["id"]: 65 for d in CANONICAL_DOMAINS}
    evidence = {d["id"]: 2 for d in CANONICAL_DOMAINS}
    practicals = {d["id"]: 40 for d in CANONICAL_DOMAINS}

    profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id="test_breadth_candidate",
        demonstrated_scores=scores,
        domain_evidence_counts=evidence,
        skills_demonstrated={d["id"]: ["Foundation"] for d in CANONICAL_DOMAINS},
        confidence_signals={d["id"]: "Medium" for d in CANONICAL_DOMAINS},
        evidence_strength={d["id"]: "Moderate Evidence" for d in CANONICAL_DOMAINS},
        interest_ratings={d["id"]: "interested" for d in CANONICAL_DOMAINS},
        scenario_preference=None,
        practical_scores=practicals,
        total_questions_answered=16
    )

    assert profile.breadthVsDepth == "Breadth > Depth"
    assert any("capstone" in dev.lower() or "deep" in dev.lower() for dev in profile.suggestedNextDevelopment)


# ==============================================================================
# 10. Canonical Profile Update & Roadmap Alignment
# ==============================================================================
def test_assessment_updates_student_profile_and_roadmap():
    reset_to_zero_knowledge()
    base_profile = get_profile()
    assert base_profile.profileState == "ZERO_KNOWLEDGE"

    intel_profile = adaptive_assessment_engine.build_career_intelligence_profile(
        user_id=base_profile.id,
        demonstrated_scores={"cybersecurity": 88, "backend": 70},
        domain_evidence_counts={"cybersecurity": 3, "backend": 2},
        skills_demonstrated={
            "cybersecurity": ["Linux", "Networking", "Incident Response"],
            "backend": ["REST APIs"]
        },
        confidence_signals={"cybersecurity": "High", "backend": "Medium"},
        evidence_strength={"cybersecurity": "Strong Evidence", "backend": "Moderate Evidence"},
        interest_ratings={"cybersecurity": "very_interested", "backend": "interested"},
        scenario_preference="Defending systems",
        practical_scores={"cybersecurity": 85, "backend": 65},
        total_questions_answered=16
    )

    updated_student = adaptive_assessment_engine.apply_assessment_to_student_profile(base_profile, intel_profile)
    set_profile(updated_student)

    # Must be transitioned to PERSONALIZED
    assert updated_student.profileState == "PERSONALIZED"
    assert updated_student.profileCompleteness == 100
    assert len(updated_student.skills) >= 3

    # Roadmap must reflect updated demonstrated skills
    steps = RoadmapEngine.generate_roadmap(updated_student, updated_student.targetCareerId)
    assert len(steps) == 6
    # Mastered or demonstrated skills should reflect completed or in-progress
    completed_or_in_prog = [s for s in steps if s.status in ["completed", "in_progress"]]
    assert len(completed_or_in_prog) > 0


# ==============================================================================
# 11. End-to-End API Session Lifecycle & Isolation
# ==============================================================================
def test_api_session_lifecycle():
    client.post("/api/auth/reset")

    # 1. Start session
    resp = client.post("/api/assessment/session/start?force_new=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentPhase"] == "MIXED_DISCOVERY"
    assert data["questionNumber"] == 1
    assert data["currentQuestion"] is not None

    q1_id = data["currentQuestion"]["id"]
    opt_id = data["currentQuestion"]["options"][0]["id"]

    # 2. Answer question
    resp = client.post("/api/assessment/session/answer", json={
        "questionId": q1_id,
        "selectedOptionId": opt_id,
        "confidence": "very_confident"
    })
    assert resp.status_code == 200
    ans_data = resp.json()
    assert ans_data["questionsAnsweredCount"] == 1

    # 3. Submit interest
    resp = client.post("/api/assessment/session/interest", json={
        "domainInterests": [
            {"domain": "cybersecurity", "interestLevel": "very_interested"},
            {"domain": "backend", "interestLevel": "interested"}
        ],
        "scenarioPreference": "Investigating threats"
    })
    assert resp.status_code == 200
    interest_data = resp.json()
    assert interest_data["currentPhase"] == "PRACTICAL_CHALLENGE"
    assert interest_data["currentPracticalScenario"] is not None

    # 4. Submit practical challenge
    prac_scenario_id = interest_data["currentPracticalScenario"]["id"]
    prac_opt_id = interest_data["currentPracticalScenario"]["options"][0]["id"]

    resp = client.post("/api/assessment/session/practical", json={
        "scenarioId": prac_scenario_id,
        "selectedOptionId": prac_opt_id,
        "reasoning": "Immediately isolating compromised endpoints prevents adversary lateral spread."
    })
    assert resp.status_code == 200
    profile_data = resp.json()
    assert "domainSignals" in profile_data
    assert "relevantPathways" in profile_data
    assert profile_data["totalQuestionsAnswered"] >= 1

    # 5. Check GET /api/assessment/profile
    resp = client.get("/api/assessment/profile")
    assert resp.status_code == 200
    assert resp.json() is not None
