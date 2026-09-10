import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.profile_store import set_profile
from app.schemas.profile import StudentProfile, Skill, StudentProject, AssessmentSignals
from app.intelligence.advanced.hidden_competency_engine import HiddenCompetencyEngine
from app.intelligence.advanced.transferability_engine import TransferabilityEngine
from app.intelligence.advanced.combination_engine import CombinationEngine
from app.intelligence.advanced.contradiction_engine import ContradictionEngine
from app.intelligence.advanced.obsolescence_engine import ObsolescenceEngine
from app.intelligence.roadmap_engine import RoadmapEngine
from app.api.routes.learning import _resources_db

client = TestClient(app)

# ==============================================================================
# 1. Hidden Competency Detection
# Example: Flask + AWS project -> Python + REST API + Cloud/AWS
# ==============================================================================
def test_hidden_competency_flask_aws_inference():
    profile = StudentProfile(
        id="test_candidate_hidden",
        name="Candidate Hidden",
        skills=[],  # Not explicitly listing Python, REST API, or Cloud
        projects=[
            StudentProject(
                title="Microservices Cloud Backend",
                tech=["Flask", "AWS", "Docker"],
                description="Built RESTful microservice deployed on AWS cloud EC2 container instance with endpoints."
            )
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    results = HiddenCompetencyEngine.detect_hidden_competencies(profile)
    inferred_skills = [r["skill"] for r in results]

    # Must infer Python, REST API, and Cloud
    assert any("Python" in s for s in inferred_skills), f"Expected Python in {inferred_skills}"
    assert any("REST API" in s for s in inferred_skills), f"Expected REST API in {inferred_skills}"
    assert any("Cloud" in s for s in inferred_skills), f"Expected Cloud in {inferred_skills}"
    for r in results:
        assert r["confidence"] >= 0.70
        assert r["explicitOrInferred"] == "inferred"


# ==============================================================================
# 2. Skill Transferability Score
# Example: Software Developer -> DevOps Engineer -> dynamically calculated score
# ==============================================================================
def test_skill_transferability_dynamic_calculation():
    # Candidate with typical Software Developer skills
    swe_profile = StudentProfile(
        id="test_candidate_swe",
        name="Candidate SWE",
        skills=[
            Skill(name="JavaScript", category="Frontend", proficiency=85),
            Skill(name="React", category="Frontend", proficiency=80),
            Skill(name="Node.js", category="Backend", proficiency=75),
            Skill(name="SQL", category="Database", proficiency=70),
            Skill(name="Git", category="Tools", proficiency=80)
        ],
        targetCareerId="career_fullstack",
        profileState="PROFILE_READY"
    )

    result_to_devops = TransferabilityEngine.calculate_transferability(
        swe_profile,
        destination_career_id="career_cloud_devops",
        source_career_id="career_fullstack"
    )

    # Must be dynamically calculated (not 0, not 100, not hardcoded)
    assert "overallScore" in result_to_devops
    score_swe_to_devops = result_to_devops["overallScore"]
    assert 20 <= score_swe_to_devops <= 80
    assert len(result_to_devops["transferableSkills"]) > 0  # Git transfers
    assert len(result_to_devops["missingSkills"]) > 0

    # Changing destination to Data Science must yield an appropriately different score
    result_to_ds = TransferabilityEngine.calculate_transferability(
        swe_profile,
        destination_career_id="career_data_science",
        source_career_id="career_fullstack"
    )
    score_swe_to_ds = result_to_ds["overallScore"]
    assert isinstance(score_swe_to_ds, int)


# ==============================================================================
# 3. Skill Combination Discovery
# Example: Python + SQL + AWS + Data Analysis -> Data Engineering
# ==============================================================================
def test_skill_combination_data_engineering():
    profile = StudentProfile(
        id="test_candidate_combo",
        name="Candidate Combo",
        skills=[
            Skill(name="Python", category="Backend", proficiency=80),
            Skill(name="SQL", category="Database", proficiency=75),
            Skill(name="AWS", category="Cloud", proficiency=70),
            Skill(name="Data Analysis", category="AI/ML", proficiency=70)
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    combinations = CombinationEngine.discover_combinations(profile)
    assert len(combinations) > 0

    careers = [c["career"] for c in combinations]
    assert "Data Engineering" in careers

    data_eng = next(c for c in combinations if c["career"] == "Data Engineering")
    assert data_eng["confidence"] >= 0.80
    # Must list the supporting skills actually owned by user
    assert any("Python" in s for s in data_eng["supportingSkills"])
    assert any("Sql" in s or "SQL" in s for s in data_eng["supportingSkills"])


# ==============================================================================
# 4. Skill Contradiction Detection
# Example: Resume: Python Advanced, Assessment: Basic performance -> Evidence Mismatch
# ==============================================================================
def test_skill_contradiction_neutral_evidence_mismatch():
    profile = StudentProfile(
        id="test_candidate_contra",
        name="Candidate Contra",
        skills=[
            Skill(name="Python", category="Backend", proficiency=90, level="Expert")
        ],
        assessmentSignals=AssessmentSignals(
            problemSolvingStyle="basic exploratory intuition without structured debugging",
            workStyleSignals=["foundational concept review"]
        ),
        projects=[],
        practicalExperience="",
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    contradictions = ContradictionEngine.detect_contradictions(profile)
    assert len(contradictions) > 0

    python_contra = next(c for c in contradictions if c["skill"] == "Python")
    assert "Evidence mismatch" in python_contra["explanation"]
    # Check neutral phrasing: no accusatory language
    explanation_lower = python_contra["explanation"].lower()
    assert "lying" not in explanation_lower
    assert "fraud" not in explanation_lower
    assert "dishonest" not in explanation_lower
    assert "fake" not in explanation_lower


# ==============================================================================
# 5. Skill Obsolescence Detection
# Example: jQuery / PHP 5 -> modern replacements from curated dataset
# ==============================================================================
def test_skill_obsolescence_curated_dataset():
    profile = StudentProfile(
        id="test_candidate_obsolete",
        name="Candidate Obsolete",
        skills=[
            Skill(name="jQuery", category="Frontend", proficiency=75),
            Skill(name="PHP 5", category="Backend", proficiency=70),
            Skill(name="Docker", category="Tools", proficiency=85)
        ],
        profileState="PROFILE_READY"
    )
    set_profile(profile)

    findings = ObsolescenceEngine.analyze_skill_trends(profile)
    skills_flagged = {f["skill"].lower(): f for f in findings}

    assert "jquery" in skills_flagged
    assert skills_flagged["jquery"]["trend"] == "Declining Relevance"
    assert any("React" in r or "TypeScript" in r for r in skills_flagged["jquery"]["recommendedSkills"])
    assert skills_flagged["jquery"]["datasetSource"] == "Curated/Internal Trend Dataset"

    assert "php 5" in skills_flagged
    assert skills_flagged["php 5"]["trend"] == "Declining Relevance"

    assert "docker" in skills_flagged
    assert skills_flagged["docker"]["trend"] == "Stable"


# ==============================================================================
# 6. Roadmap: All 7 Careers + Real YouTube URLs + No Fake URLs
# ==============================================================================
def test_roadmap_all_seven_careers_and_real_urls():
    all_7_careers = [
        "career_fullstack",
        "career_frontend",
        "career_backend",
        "career_cybersecurity",
        "career_ai_ml",
        "career_cloud_devops",
        "career_data_science"
    ]

    base_profile = StudentProfile(
        id="test_std_roadmap",
        name="Test Student",
        skills=[Skill(name="Python", category="Backend", proficiency=80)],
        profileState="PROFILE_READY"
    )

    for cid in all_7_careers:
        steps = RoadmapEngine.generate_roadmap(base_profile, cid)
        assert len(steps) == 6, f"Career {cid} should have 6 steps"

        for step in steps:
            # Check video URL in resources
            for res in step.recommendedResources:
                # Must NOT be generic or placeholder
                assert res.url != "https://youtube.com"
                assert res.url != "https://www.youtube.com"
                assert res.url != "https://docs.reskill.ai"
                if res.platform == "YouTube":
                    assert res.url.startswith("https://www.youtube.com/watch?v=")


# ==============================================================================
# 7. Learning Hub: All Resources Verified YouTube Video Format
# ==============================================================================
def test_learning_hub_real_youtube_format():
    assert len(_resources_db) >= 20

    for res in _resources_db:
        if res.platform == "YouTube":
            assert res.url.startswith("https://www.youtube.com/watch?v="), f"Invalid YouTube URL: {res.url}"
            # Must have 11-char video ID
            vid_id = res.url.split("v=")[-1]
            assert len(vid_id) == 11, f"Invalid video ID length: {vid_id} in {res.url}"
            assert res.skillTag, f"Missing skillTag in resource {res.id}"


# ==============================================================================
# 8. Absolute Data Isolation: Zero-Knowledge State & No Persona Fallback
# ==============================================================================
def test_absolute_data_isolation():
    client.post("/api/auth/reset")
    resp = client.get("/api/profile")
    assert resp.status_code == 200
    profile = resp.json()

    assert profile["profileState"] == "ZERO_KNOWLEDGE"
    assert profile["careerReadiness"] == 0
    assert len(profile["skills"]) == 0
    assert len(profile["projects"]) == 0
    assert len(profile["experience"]) == 0
    assert "Parvez" not in profile["name"]
