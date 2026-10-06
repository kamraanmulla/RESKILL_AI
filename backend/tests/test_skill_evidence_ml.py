"""
Unit and Integration Tests for ReSkillAI Phase 3:
Skill Evidence & Proficiency Prediction ML Pipeline.
Verifies zero fake proficiency scores, candidate isolation, and robust missing evidence handling.
"""

import os
import sys
import pytest
from pathlib import Path

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
RESKILL_ROOT = BACKEND_DIR.parent
WORKSPACE_ROOT = RESKILL_ROOT.parent
ML_DIR = WORKSPACE_ROOT / "backend" / "ml"

sys.path.insert(0, str(WORKSPACE_ROOT))
sys.path.insert(0, str(ML_DIR))

# Try imports
try:
    from backend.ml.feature_engineering_skill import (
        ResumeSectionParser,
        SkillEvidenceFeatureExtractor,
        VOCATIONAL_TAXONOMY
    )
    from backend.ml.predict_skill_evidence import SkillEvidencePredictor
except ImportError:
    from feature_engineering_skill import (
        ResumeSectionParser,
        SkillEvidenceFeatureExtractor,
        VOCATIONAL_TAXONOMY
    )
    from predict_skill_evidence import SkillEvidencePredictor


class TestSkillEvidenceFeatureExtractor:
    """Test suite for feature extraction and evidence grounding."""

    def test_1_feature_extraction_schema(self):
        """Verifies all expected evidence feature keys are present."""
        extractor = SkillEvidenceFeatureExtractor()
        sample_sections = {
            "summary": "Experienced Python and AWS software developer.",
            "skills": "Python, Docker, SQL, Git",
            "experience": "Developed microservices in Python using Docker and PostgreSQL. Deployed to AWS.",
            "projects": "Built an analytics platform with Python and React.",
            "education": "B.S. in Computer Science"
        }
        full_text = " ".join(sample_sections.values())
        features = extractor.extract_features_from_sections(
            candidate_id="test_cand_01",
            skill_name="Python",
            sections=sample_sections,
            full_text=full_text
        )

        for expected_col in extractor.FEATURE_NAMES:
            assert expected_col in features, f"Missing expected feature: {expected_col}"

        assert features["candidate_id"] == "test_cand_01"
        assert features["skill"] == "Python"
        assert features["resume_mentioned"] == 1
        assert features["resume_frequency"] >= 3
        assert features["in_experience_section"] == 1
        assert features["has_action_verb_context"] == 1
        assert features["is_evidence_supported"] == 1

    def test_2_missing_evidence_zero_knowledge(self):
        """Verifies zero-knowledge profile returns zero evidence without inventing scores."""
        predictor = SkillEvidencePredictor()
        empty_profile = {
            "id": "zk_student",
            "name": "Zero Knowledge User",
            "email": "zk@example.com",
            "degree": "",
            "skills": [],
            "projects": [],
            "experience": [],
            "assessmentSignals": {}
        }
        result = predictor.predict_skill(empty_profile, "Python")

        assert result["status"] == "INSUFFICIENT_EVIDENCE"
        assert result["evidence_strength"] == 0.0
        assert result["confidence"] == 0.0
        assert "No resume, project, assessment, or practical evidence available." in result["reason"]
        assert len(result["evidence_sources"]) == 0

    def test_3_known_skill_evidence(self):
        """Verifies profile with strong corroboration receives high evidence strength."""
        predictor = SkillEvidencePredictor()
        rich_profile = {
            "id": "rich_student",
            "resume_text": "Senior Developer. Developed high-throughput services with Python, PostgreSQL, and Docker in AWS.",
            "projects": [
                {
                    "title": "Data Pipeline",
                    "tech": ["Python", "Docker"],
                    "description": "Implemented automated ETL workflows."
                }
            ],
            "assessmentSignals": {
                "skillsDemonstrated": ["Python"],
                "demonstratedKnowledge": {"Python": 85}
            }
        }
        result = predictor.predict_skill(rich_profile, "Python")

        assert result["evidence_strength"] >= 0.50
        assert result["confidence"] >= 0.60
        assert "resume" in result["evidence_sources"]
        assert "project" in result["evidence_sources"]
        assert "assessment" in result["evidence_sources"]
        assert result["status"] in ["STRONG_EVIDENCE", "MODERATE_EVIDENCE"]

    def test_4_unknown_unmentioned_skill(self):
        """Verifies profile with resume but absent skill returns UNSUPPORTED with 0.0 strength."""
        predictor = SkillEvidencePredictor()
        profile = {
            "id": "cand_specialist",
            "resume_text": "Experienced accountant specializing in general ledger, GAAP, and corporate audits.",
            "projects": [],
            "assessmentSignals": {}
        }
        result = predictor.predict_skill(profile, "Kubernetes")

        assert result["status"] == "UNSUPPORTED"
        assert result["evidence_strength"] == 0.0
        assert result["confidence"] == 0.0
        assert len(result["evidence_sources"]) == 0

    def test_5_prediction_output_schema(self):
        """Verifies strict adherence to prediction output contract."""
        predictor = SkillEvidencePredictor()
        profile = {
            "id": "schema_test",
            "resume_text": "Software Engineer working with React and TypeScript.",
            "projects": [],
            "assessmentSignals": {}
        }
        result = predictor.predict_skill(profile, "React")

        required_keys = ["skill", "evidence_strength", "confidence", "status", "evidence_sources", "details"]
        for k in required_keys:
            assert k in result, f"Result missing key: {k}"

        assert isinstance(result["evidence_strength"], float)
        assert 0.0 <= result["evidence_strength"] <= 1.0
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["evidence_sources"], list)

    def test_6_model_loading_and_fallback(self):
        """Verifies predictor gracefully falls back to heuristic mode if model missing."""
        predictor = SkillEvidencePredictor(model_path="non_existent_model.joblib")
        assert predictor.pipeline is None

        profile = {
            "id": "test_fallback",
            "resume_text": "Developed Java web applications using Spring Boot.",
            "projects": [],
            "assessmentSignals": {}
        }
        result = predictor.predict_skill(profile, "Java")
        assert result["evidence_strength"] > 0.0
        assert "resume" in result["evidence_sources"]

    def test_7_deterministic_inference(self):
        """Verifies repeated calls with identical input return identical outputs."""
        predictor = SkillEvidencePredictor()
        profile = {
            "id": "determ_test",
            "resume_text": "Architected cloud solutions using AWS and Docker.",
            "projects": [{"title": "Cloud Infra", "tech": ["AWS"], "description": "Cloud setup"}],
            "assessmentSignals": {}
        }
        res1 = predictor.predict_skill(profile, "AWS")
        res2 = predictor.predict_skill(profile, "AWS")

        assert res1["evidence_strength"] == res2["evidence_strength"]
        assert res1["confidence"] == res2["confidence"]
        assert res1["status"] == res2["status"]

    def test_8_no_fake_proficiency_claims(self):
        """Verifies model output never claims to be a 0-100 proficiency score."""
        predictor = SkillEvidencePredictor()
        profile = {
            "id": "no_fake_test",
            "resume_text": "Proficient in Python with 5 years experience.",
            "projects": [],
            "assessmentSignals": {}
        }
        result = predictor.predict_skill(profile, "Python")

        assert "proficiency" not in result
        assert "score_out_of_100" not in result
        assert "evidence_strength" in result

    def test_9_section_parsing_robustness(self):
        """Verifies section parser correctly identifies inline headers."""
        text = "SUMMARY Dedicated engineer. EXPERIENCE Developed backend in Go. SKILLS Go, Docker."
        sections = ResumeSectionParser.parse_sections(text)

        assert len(sections["experience"]) > 0
        assert "developed" in sections["experience"]
        assert len(sections["skills"]) > 0

    def test_10_batch_prediction_consistency(self):
        """Verifies batch prediction interface handles multiple skills."""
        predictor = SkillEvidencePredictor()
        profile = {
            "id": "batch_test",
            "resume_text": "Full stack engineer proficient in Python and React.",
            "projects": [],
            "assessmentSignals": {}
        }
        batch_results = predictor.predict_multiple_skills(profile, ["Python", "React", "Rust"])

        assert len(batch_results) == 3
        skills = [r["skill"] for r in batch_results]
        assert skills == ["Python", "React", "Rust"]
        rust_res = next(r for r in batch_results if r["skill"] == "Rust")
        assert rust_res["status"] == "UNSUPPORTED"
