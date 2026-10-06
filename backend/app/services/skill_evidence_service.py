"""
ReSkillAI - Phase 4: Real User Evidence Integration Service
Connects real candidate evidence (Resume, Assessment, Projects, Experience, Education)
to the Phase 3 ML Skill Evidence model without altering existing deterministic intelligence engines.
"""

import os
import sys
import logging
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

# Ensure ML package is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
WORKSPACE_ROOT = os.path.dirname(BACKEND_DIR)
ML_DIR = os.path.join(WORKSPACE_ROOT, "backend", "ml")

for p in [WORKSPACE_ROOT, BACKEND_DIR, ML_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.ml.predict_skill_evidence import SkillEvidencePredictor
    from backend.ml.feature_engineering_skill import VOCATIONAL_TAXONOMY
except ImportError:
    try:
        from predict_skill_evidence import SkillEvidencePredictor
        from feature_engineering_skill import VOCATIONAL_TAXONOMY
    except ImportError:
        SkillEvidencePredictor = None
        VOCATIONAL_TAXONOMY = {}

from ..schemas.profile import StudentProfile, Skill, StudentProject, StudentExperience, AssessmentSignals
from .assessment_session_store import assessment_session_store

logger = logging.getLogger("ReSkillAI.Services.SkillEvidenceService")


class EvidenceState(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class SkillEvidenceItem(BaseModel):
    skill: str
    evidence_strength: Optional[float] = None
    confidence: float = 0.0
    status: str  # "SUPPORTED", "MODERATE_EVIDENCE", "WEAK_EVIDENCE", "INSUFFICIENT_EVIDENCE", "UNSUPPORTED"
    evidence_sources: List[str] = []
    source_states: Dict[str, EvidenceState]
    explanation: str
    details: Dict[str, Any] = {}


class SkillEvidenceProfileResponse(BaseModel):
    userId: str
    targetCareerId: str
    totalSkillsEvaluated: int
    supportedSkillsCount: int
    skills: List[SkillEvidenceItem]
    disclaimer: str = (
        "Evidence strength represents multi-source portfolio corroboration. "
        "It does NOT represent an unverified 0-100 personal skill proficiency test."
    )


class SkillEvidenceService:
    """Aggregates real user evidence and invokes the Phase 3 ML evidence model."""

    def __init__(self):
        self.predictor = SkillEvidencePredictor() if SkillEvidencePredictor else None

    def _normalize_skill_name(self, raw_name: str) -> str:
        clean = raw_name.strip()
        for canonical, info in VOCATIONAL_TAXONOMY.items():
            if clean.lower() == canonical.lower() or any(clean.lower() == s for s in info.get("synonyms", [])):
                return canonical
        return clean

    def evaluate_skill_evidence(
        self,
        profile: StudentProfile,
        skill_name: str
    ) -> SkillEvidenceItem:
        """
        Evaluates real multi-source evidence for a single skill.
        Strictly enforces 'missing != weak' and distinguishes PRESENT vs ABSENT vs NOT_AVAILABLE.
        """
        canonical_skill = self._normalize_skill_name(skill_name)
        synonyms = VOCATIONAL_TAXONOMY.get(canonical_skill, {}).get("synonyms", [canonical_skill.lower()])

        # -------------------------------------------------------------
        # 1. Zero-Knowledge / Completely Unpopulated Profile Check
        # -------------------------------------------------------------
        has_any_resume = bool(profile.resumeFile or profile.bio)
        has_any_skills = len(profile.skills) > 0
        has_any_projects = len(profile.projects) > 0
        has_any_experience = len(profile.experience) > 0 or bool(profile.practicalExperience and profile.practicalExperience != "I haven't worked on anything yet")
        has_any_assessment = bool(
            (profile.assessmentSignals and (
                profile.assessmentSignals.demonstratedKnowledge or
                profile.assessmentSignals.skillsDemonstrated or
                profile.assessmentSignals.careerInterestScores or
                profile.assessmentSignals.domainPreferences
            )) or
            (assessment_session_store.get_session(profile.id) and assessment_session_store.get_session(profile.id).total_answered_count() > 0)
        )

        if not has_any_resume and not has_any_skills and not has_any_projects and not has_any_experience and not has_any_assessment:
            return SkillEvidenceItem(
                skill=canonical_skill,
                evidence_strength=None,
                confidence=0.0,
                status="INSUFFICIENT_EVIDENCE",
                evidence_sources=[],
                source_states={
                    "resume": EvidenceState.NOT_AVAILABLE,
                    "assessment": EvidenceState.NOT_AVAILABLE,
                    "project": EvidenceState.NOT_AVAILABLE,
                    "practical": EvidenceState.NOT_AVAILABLE,
                    "experience": EvidenceState.NOT_AVAILABLE,
                    "education": EvidenceState.NOT_AVAILABLE,
                },
                explanation="No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence.",
                details={"reason": "ZERO_KNOWLEDGE"}
            )

        # -------------------------------------------------------------
        # 2. Inspect Real User Evidence Sources
        # -------------------------------------------------------------
        source_states: Dict[str, EvidenceState] = {}
        active_sources: List[str] = []
        source_explanations: List[str] = []
        details: Dict[str, Any] = {}

        # --- A. RESUME EVIDENCE ---
        # Reconstruct resume text from parsed entities and bio if raw text isn't directly retained
        resume_corpus = f"{profile.bio} {profile.practicalExperience} "
        for s in profile.skills:
            resume_corpus += f" {s.name}"
        for exp in profile.experience:
            resume_corpus += f" {exp.title} {exp.company} {exp.description}"
        for proj in profile.projects:
            resume_corpus += f" {proj.title} {' '.join(proj.tech)} {proj.description}"

        lower_corpus = resume_corpus.lower()
        resume_match_count = sum(lower_corpus.count(syn) for syn in synonyms)
        is_in_skills_list = any(any(syn == s.name.lower() or syn in s.name.lower() for syn in synonyms) for s in profile.skills)

        if has_any_resume or is_in_skills_list:
            if resume_match_count > 0 or is_in_skills_list:
                source_states["resume"] = EvidenceState.PRESENT
                active_sources.append("resume")
                details["resume_frequency"] = max(resume_match_count, 1 if is_in_skills_list else 0)
                source_explanations.append(f"documented in profile/resume ({details['resume_frequency']} mention(s))")
            else:
                source_states["resume"] = EvidenceState.ABSENT
        else:
            source_states["resume"] = EvidenceState.NOT_AVAILABLE

        # --- B. PROJECT EVIDENCE ---
        if has_any_projects:
            matching_projects = []
            for p in profile.projects:
                tech_lower = [t.lower() for t in p.tech]
                desc_lower = p.description.lower()
                title_lower = p.title.lower()
                if any(syn in tech_lower for syn in synonyms) or any(syn in desc_lower for syn in synonyms) or any(syn in title_lower for syn in synonyms):
                    matching_projects.append(p.title)

            if matching_projects:
                source_states["project"] = EvidenceState.PRESENT
                active_sources.append("project")
                details["matching_projects"] = matching_projects
                details["project_count"] = len(matching_projects)
                source_explanations.append(f"applied in {len(matching_projects)} project(s): {', '.join(matching_projects[:2])}")
            else:
                source_states["project"] = EvidenceState.ABSENT
        else:
            source_states["project"] = EvidenceState.NOT_AVAILABLE

        # --- C. ASSESSMENT EVIDENCE ---
        assess_signals = profile.assessmentSignals
        sess = assessment_session_store.get_session(profile.id)
        has_assessment_data = bool(
            (assess_signals and (
                assess_signals.demonstratedKnowledge or
                assess_signals.skillsDemonstrated or
                assess_signals.careerInterestScores or
                assess_signals.domainPreferences
            )) or
            (sess and sess.total_answered_count() > 0)
        )

        if has_assessment_data:
            demo_knowledge = (assess_signals.demonstratedKnowledge if assess_signals else {}) or {}
            skills_demo = [s.lower() for s in ((assess_signals.skillsDemonstrated if assess_signals else []) or [])]
            career_scores = (assess_signals.careerInterestScores if assess_signals else {}) or {}
            domain_prefs = [d.lower() for d in ((assess_signals.domainPreferences if assess_signals else []) or [])]

            # Check domain knowledge matching skill's category
            skill_cat = VOCATIONAL_TAXONOMY.get(canonical_skill, {}).get("category", "Other").lower()
            category_domain_map = {
                "backend": "software_engineering",
                "frontend": "software_engineering",
                "database": "software_engineering",
                "security": "cybersecurity",
                "ai/ml": "ai_ml",
                "cloud": "cloud_devops",
                "tools": "software_engineering",
                "data science": "data_science",
            }
            mapped_domain = category_domain_map.get(skill_cat, "")

            is_skill_directly_demo = any(syn in skills_demo for syn in synonyms)
            demo_score = demo_knowledge.get(mapped_domain, 0)
            career_score = career_scores.get(mapped_domain, 0)
            is_domain_preferred = bool(mapped_domain and mapped_domain in domain_prefs)

            # Check session answers if available
            answered_for_skill = False
            if sess and sess.answers:
                from ..intelligence.adaptive_assessment_engine import QUESTION_BANK
                for q_id in sess.answers:
                    q_data = next((q for q in QUESTION_BANK if q["id"] == q_id), None)
                    if q_data and (any(syn in q_data.get("skill", "").lower() for syn in synonyms) or q_data.get("domain") == mapped_domain):
                        answered_for_skill = True
                        break

            if is_skill_directly_demo or demo_score >= 50 or career_score >= 40 or answered_for_skill or is_domain_preferred:
                source_states["assessment"] = EvidenceState.PRESENT
                active_sources.append("assessment")
                details["assessment_demonstrated"] = is_skill_directly_demo
                active_score = demo_score or career_score
                details["domain_score"] = active_score
                source_explanations.append(
                    f"demonstrated in assessment ({'direct question confirmation' if is_skill_directly_demo else f'{active_score}% {mapped_domain} performance'})"
                )
            else:
                source_states["assessment"] = EvidenceState.ABSENT
        else:
            source_states["assessment"] = EvidenceState.NOT_AVAILABLE

        # --- D. PRACTICAL EVIDENCE ---
        practical_scores = assess_signals.practicalScores if assess_signals else {}
        if not practical_scores and sess:
            practical_scores = sess.practicalScores

        if practical_scores:
            top_prac_score = max(practical_scores.values()) if practical_scores else 0
            if top_prac_score > 0 and source_states.get("assessment") == EvidenceState.PRESENT:
                source_states["practical"] = EvidenceState.PRESENT
                active_sources.append("practical")
                details["practical_score"] = top_prac_score
                source_explanations.append(f"evaluated in practical scenario challenge ({top_prac_score}% score)")
            else:
                source_states["practical"] = EvidenceState.ABSENT
        else:
            source_states["practical"] = EvidenceState.NOT_AVAILABLE

        # --- E. EXPERIENCE EVIDENCE ---
        if has_any_experience:
            matching_exp = []
            for exp in profile.experience:
                exp_text = f"{exp.title} {exp.company} {exp.description}".lower()
                if any(syn in exp_text for syn in synonyms):
                    matching_exp.append(f"{exp.title} at {exp.company}")

            if matching_exp:
                source_states["experience"] = EvidenceState.PRESENT
                active_sources.append("experience")
                details["matching_experience"] = matching_exp
                source_explanations.append(f"applied in professional experience ({matching_exp[0]})")
            else:
                source_states["experience"] = EvidenceState.ABSENT
        else:
            source_states["experience"] = EvidenceState.NOT_AVAILABLE

        # --- F. EDUCATION EVIDENCE ---
        if profile.degree or profile.field:
            edu_text = f"{profile.degree} {profile.field}".lower()
            is_edu_related = any(syn in edu_text for syn in synonyms) or ("computer" in edu_text and VOCATIONAL_TAXONOMY.get(canonical_skill, {}).get("category") in ["Backend", "Frontend", "Database", "Tools"])
            source_states["education"] = EvidenceState.PRESENT if is_edu_related else EvidenceState.ABSENT
            if is_edu_related:
                details["education_context"] = f"{profile.degree} in {profile.field}".strip()
        else:
            source_states["education"] = EvidenceState.NOT_AVAILABLE

        # -------------------------------------------------------------
        # 3. Check for Complete Absence Across All Active Sources
        # -------------------------------------------------------------
        if len(active_sources) == 0:
            return SkillEvidenceItem(
                skill=canonical_skill,
                evidence_strength=None,
                confidence=0.0,
                status="UNSUPPORTED",
                evidence_sources=[],
                source_states=source_states,
                explanation=f"No active evidence supports {canonical_skill} in the candidate profile.",
                details={"reason": "NO_MATCHING_EVIDENCE_IN_ACTIVE_SOURCES"}
            )

        # -------------------------------------------------------------
        # 4. Invoke Phase 3 ML Model for Probabilistic Evidence Support
        # -------------------------------------------------------------
        profile_dict = profile.model_dump()
        profile_dict["resume_text"] = resume_corpus

        ml_result = {}
        if self.predictor:
            ml_result = self.predictor.predict_skill(profile_dict, canonical_skill)

        # Model predicted probability
        raw_strength = ml_result.get("evidence_strength", 0.50) if ml_result else 0.50

        # -------------------------------------------------------------
        # 5. Conservative Multi-Source Evidence Confidence Formula
        # (Task 16: Never output artificial confidence = 0.99 from single source)
        # -------------------------------------------------------------
        # Weights for distinct evidence sources:
        # Resume presence: 0.30
        # Projects: 0.30
        # Assessment: 0.25
        # Practical Scenario: 0.15
        calculated_conf = 0.0
        if "resume" in active_sources:
            calculated_conf += 0.30
        if "project" in active_sources:
            calculated_conf += 0.30
        if "assessment" in active_sources:
            calculated_conf += 0.25
        if "practical" in active_sources:
            calculated_conf += 0.15

        # Cap confidence based on source convergence
        final_confidence = round(min(0.95, max(0.20, calculated_conf)), 2)
        final_strength = round(float(raw_strength), 2)

        # Status categorization
        if final_strength >= 0.70 and len(active_sources) >= 2:
            status = "SUPPORTED"
        elif final_strength >= 0.40:
            status = "MODERATE_EVIDENCE"
        else:
            status = "WEAK_EVIDENCE"

        # Construct clear, transparent explanation
        explanation_body = "; ".join(source_explanations)
        explanation = f"{canonical_skill} evidence is {status.lower().replace('_', ' ')}: {explanation_body}."

        return SkillEvidenceItem(
            skill=canonical_skill,
            evidence_strength=final_strength,
            confidence=final_confidence,
            status=status,
            evidence_sources=active_sources,
            source_states=source_states,
            explanation=explanation,
            details=details
        )

    def evaluate_profile_evidence(
        self,
        profile: StudentProfile,
        skills_filter: Optional[List[str]] = None
    ) -> SkillEvidenceProfileResponse:
        """Evaluates evidence across all target career skills or user skills."""
        # Determine skills to evaluate:
        skills_to_eval: List[str] = []
        if skills_filter:
            skills_to_eval = [self._normalize_skill_name(s) for s in skills_filter]
        else:
            # Union of user profile skills and target career skills
            user_skill_names = [s.name for s in profile.skills]
            skills_to_eval = list(dict.fromkeys(user_skill_names))

        # Default fallback to top vocational skills if user has no skills
        if not skills_to_eval and profile.targetCareerId:
            from ..intelligence.career_taxonomy import get_career_by_id
            target_career = get_career_by_id(profile.targetCareerId)
            skills_to_eval = (target_career.coreSkills or [])[:6]

        if not skills_to_eval:
            skills_to_eval = ["Python", "JavaScript", "SQL", "Git"]

        items: List[SkillEvidenceItem] = []
        supported_count = 0

        for skill in skills_to_eval:
            item = self.evaluate_skill_evidence(profile, skill)
            items.append(item)
            if item.status in ["SUPPORTED", "MODERATE_EVIDENCE"]:
                supported_count += 1

        return SkillEvidenceProfileResponse(
            userId=profile.id,
            targetCareerId=profile.targetCareerId or "career_fullstack",
            totalSkillsEvaluated=len(items),
            supportedSkillsCount=supported_count,
            skills=items
        )


skill_evidence_service = SkillEvidenceService()
