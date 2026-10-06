"""
ReSkillAI - Phase 3: Real-Time Skill Evidence Strength Predictor
Provides probabilistic evidence support and confidence estimation for candidate-skill pairs.
Handles ZERO_KNOWLEDGE users with strict 'missing != weak' semantics.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(BASE_DIR)
sys.path.append(ROOT_DIR)

from feature_engineering_skill import (
    SkillEvidenceFeatureExtractor,
    VOCATIONAL_TAXONOMY
)

logger = logging.getLogger("ReSkillAI.ML.SkillEvidencePredictor")

DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "skill_evidence_model.joblib")


class SkillEvidencePredictor:
    """Predicts evidence strength and confidence for candidate-skill pairs."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.extractor = SkillEvidenceFeatureExtractor()
        self.pipeline = None
        self.feature_cols = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.warning(f"Model artifact not found at {self.model_path}. Predictor will run in heuristic fallback mode.")
            return

        try:
            artifact = joblib.load(self.model_path)
            self.pipeline = artifact["pipeline"]
            self.feature_cols = artifact["feature_cols"]
            logger.info("Successfully loaded Phase 3 Skill Evidence Model.")
        except Exception as e:
            logger.error(f"Error loading model artifact: {e}")
            self.pipeline = None

    def predict_skill(
        self,
        profile: Dict[str, Any],
        skill_name: str
    ) -> Dict[str, Any]:
        """
        Evaluates evidence for a single skill given a candidate's profile.
        Handles zero-knowledge users safely without inventing false negatives.
        """
        # 1. Zero-Knowledge / Missing Data Audit
        resume_text = profile.get("resume_text", "").strip() if profile.get("resume_text") else ""
        projects = profile.get("projects") or []
        assess = profile.get("assessmentSignals") or {}
        has_resume = bool(resume_text or profile.get("resumeFile"))
        has_projects = bool(projects)
        has_assess = bool(assess.get("skillsDemonstrated") or assess.get("demonstratedKnowledge"))

        if not has_resume and not has_projects and not has_assess:
            return {
                "skill": skill_name,
                "evidence_strength": 0.0,
                "confidence": 0.0,
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": "No resume, project, assessment, or practical evidence available.",
                "evidence_sources": [],
                "details": {
                    "resume_mentioned": False,
                    "in_projects": False,
                    "in_assessment": False,
                }
            }

        # 2. Extract structured feature dictionary
        features = self.extractor.extract_from_user_profile(profile, skill_name)

        # Identify active evidence sources
        sources = []
        if features.get("resume_mentioned", 0) > 0:
            sources.append("resume")
        if features.get("project_evidence_count", 0) > 0:
            sources.append("project")
        if features.get("assessment_evidence_score", 0.0) > 0.0:
            sources.append("assessment")
        if features.get("practical_evidence_score", 0.0) > 0.0:
            sources.append("practical")

        # 3. Check for complete absence of this specific skill
        if len(sources) == 0:
            return {
                "skill": skill_name,
                "evidence_strength": 0.0,
                "confidence": 0.0,
                "status": "UNSUPPORTED",
                "reason": f"No mention or demonstration of {skill_name} in candidate evidence.",
                "evidence_sources": [],
                "details": {
                    "resume_mentioned": False,
                    "in_projects": False,
                    "in_assessment": False,
                }
            }

        # 4. Predict calibrated evidence strength
        if self.pipeline is not None and self.feature_cols is not None:
            input_df = pd.DataFrame([{col: features.get(col, 0) for col in self.feature_cols}])
            proba = self.pipeline.predict_proba(input_df)[0]
            strength = float(proba[1])
        else:
            # Fallback heuristic if model is not yet trained
            strength = min(1.0, (
                0.30 * features.get("resume_mentioned", 0) +
                0.25 * features.get("in_experience_section", 0) +
                0.20 * features.get("has_action_verb_context", 0) +
                0.25 * min(1.0, features.get("project_evidence_count", 0))
            ))

        # 5. Compute confidence based on multi-source convergence
        # Confidence increases as more independent sources corroborate
        base_confidence = 0.50
        if "resume" in sources and (features.get("in_experience_section", 0) or features.get("has_action_verb_context", 0)):
            base_confidence += 0.15
        if "project" in sources:
            base_confidence += 0.15
        if "assessment" in sources or "practical" in sources:
            base_confidence += 0.15
        confidence = round(min(0.95, base_confidence), 2)
        strength = round(strength, 2)

        # Categorize status
        if strength >= 0.70:
            status = "STRONG_EVIDENCE"
        elif strength >= 0.40:
            status = "MODERATE_EVIDENCE"
        else:
            status = "WEAK_EVIDENCE"

        return {
            "skill": skill_name,
            "evidence_strength": strength,
            "confidence": confidence,
            "status": status,
            "evidence_sources": sources,
            "details": {
                "resume_frequency": features.get("resume_frequency", 0),
                "in_experience": bool(features.get("in_experience_section", 0)),
                "in_projects": bool(features.get("in_project_section", 0) or features.get("project_evidence_count", 0)),
                "has_action_verbs": bool(features.get("has_action_verb_context", 0)),
                "co_occurring_tech_count": features.get("co_occurring_tech_count", 0),
            }
        }

    def predict_multiple_skills(
        self,
        profile: Dict[str, Any],
        skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Batch evaluation for a list of skills."""
        return [self.predict_skill(profile, s) for s in skills]
