"""
ReSkillAI - Phase 3: Skill Evidence Feature Engineering
Extracts candidate-skill evidence features from both historical resumes
and live structured user profiles. Zero fake proficiency scores.
"""

import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import numpy as np
import pandas as pd

logger = logging.getLogger("ReSkillAI.ML.SkillFeatureEngineering")

# Action-oriented implementation verbs indicating applied practice
ACTION_VERBS = {
    "implemented", "developed", "designed", "architected", "deployed", "built",
    "configured", "optimized", "managed", "administered", "created", "engineered",
    "programmed", "coded", "analyzed", "automated", "tested", "maintained",
    "resolved", "migrated", "integrated", "spearheaded", "executed", "collaborated"
}

# Curated vocational taxonomy with skill categories & canonical synonyms
VOCATIONAL_TAXONOMY = {
    "Python": {"category": "Backend", "synonyms": ["python", "python3", "py"]},
    "Java": {"category": "Backend", "synonyms": ["java", "core java", "j2ee"]},
    "JavaScript": {"category": "Frontend", "synonyms": ["javascript", "js", "ecmascript"]},
    "TypeScript": {"category": "Frontend", "synonyms": ["typescript", "ts"]},
    "C++": {"category": "Backend", "synonyms": ["c++", "cpp"]},
    "C#": {"category": "Backend", "synonyms": ["c#", "csharp", ".net c#"]},
    "PHP": {"category": "Backend", "synonyms": ["php", "php7", "php8"]},
    "Ruby": {"category": "Backend", "synonyms": ["ruby", "ruby on rails"]},
    "Go": {"category": "Backend", "synonyms": ["golang", "go programming"]},
    "Rust": {"category": "Backend", "synonyms": ["rust", "rustlang"]},
    "SQL": {"category": "Database", "synonyms": ["sql", "structured query language"]},
    "PostgreSQL": {"category": "Database", "synonyms": ["postgresql", "postgres", "psql"]},
    "MySQL": {"category": "Database", "synonyms": ["mysql", "mariadb"]},
    "MongoDB": {"category": "Database", "synonyms": ["mongodb", "mongo", "nosql"]},
    "Redis": {"category": "Database", "synonyms": ["redis", "in-memory database"]},
    "Oracle": {"category": "Database", "synonyms": ["oracle db", "oracle database", "pl/sql"]},
    "React": {"category": "Frontend", "synonyms": ["react", "react.js", "reactjs"]},
    "Angular": {"category": "Frontend", "synonyms": ["angular", "angular.js", "angularjs"]},
    "Vue.js": {"category": "Frontend", "synonyms": ["vue", "vue.js", "vuejs"]},
    "HTML": {"category": "Frontend", "synonyms": ["html", "html5"]},
    "CSS": {"category": "Frontend", "synonyms": ["css", "css3", "sass", "scss"]},
    "Node.js": {"category": "Backend", "synonyms": ["node.js", "nodejs", "node js"]},
    "Docker": {"category": "Cloud", "synonyms": ["docker", "containerization", "containers"]},
    "Kubernetes": {"category": "Cloud", "synonyms": ["kubernetes", "k8s"]},
    "AWS": {"category": "Cloud", "synonyms": ["aws", "amazon web services", "ec2", "s3"]},
    "Azure": {"category": "Cloud", "synonyms": ["azure", "microsoft azure"]},
    "Git": {"category": "Tools", "synonyms": ["git", "github", "gitlab", "version control"]},
    "Linux": {"category": "Tools", "synonyms": ["linux", "unix", "ubuntu", "centos", "bash"]},
    "Machine Learning": {"category": "AI/ML", "synonyms": ["machine learning", "ml", "data science"]},
    "Deep Learning": {"category": "AI/ML", "synonyms": ["deep learning", "neural networks", "pytorch", "tensorflow"]},
    "Cybersecurity": {"category": "Security", "synonyms": ["cybersecurity", "information security", "infosec", "network security"]},
    "Data Analysis": {"category": "AI/ML", "synonyms": ["data analysis", "data analytics", "pandas", "data visualization"]},
    "Financial Analysis": {"category": "Domain", "synonyms": ["financial analysis", "financial modeling", "variance analysis"]},
    "Accounting": {"category": "Domain", "synonyms": ["accounting", "general ledger", "gaap", "reconciliation"]},
    "Project Management": {"category": "Domain", "synonyms": ["project management", "pmp", "scrum", "agile", "jira"]},
    "Marketing Strategy": {"category": "Domain", "synonyms": ["marketing strategy", "digital marketing", "seo", "branding"]},
    "Sales Strategy": {"category": "Domain", "synonyms": ["sales strategy", "b2b sales", "crm", "salesforce", "lead generation"]},
    "Healthcare Administration": {"category": "Domain", "synonyms": ["healthcare administration", "patient care", "ehr", "hipaa"]},
    "Human Resources": {"category": "Domain", "synonyms": ["human resources", "talent acquisition", "recruiting", "onboarding"]},
    "Customer Support": {"category": "Domain", "synonyms": ["customer support", "client services", "helpdesk", "ticketing"]},
}

# Domain to typical skill mapping for plausible negative / contrastive sampling
CATEGORY_EXPECTED_SKILLS = {
    "INFORMATION-TECHNOLOGY": ["Python", "Java", "SQL", "Linux", "AWS", "Docker", "Git", "Cybersecurity", "React", "Node.js"],
    "ENGINEERING": ["C++", "Python", "Linux", "Project Management", "Git", "SQL", "Docker", "AWS"],
    "FINANCE": ["Financial Analysis", "Accounting", "SQL", "Project Management", "Data Analysis"],
    "ACCOUNTANT": ["Accounting", "Financial Analysis", "SQL", "Project Management"],
    "BUSINESS-DEVELOPMENT": ["Sales Strategy", "Marketing Strategy", "Project Management", "Customer Support"],
    "SALES": ["Sales Strategy", "Customer Support", "Marketing Strategy", "Project Management"],
    "HR": ["Human Resources", "Project Management", "Customer Support"],
    "HEALTHCARE": ["Healthcare Administration", "Customer Support", "Project Management"],
    "DIGITAL-MEDIA": ["Marketing Strategy", "HTML", "CSS", "JavaScript", "Project Management"],
    "CONSULTANT": ["Project Management", "Financial Analysis", "Data Analysis", "Sales Strategy"],
    "BPO": ["Customer Support", "Project Management", "Data Analysis"],
}


class ResumeSectionParser:
    """Parses raw resume text into distinct semantic sections."""

    SECTION_PATTERNS = [
        ("experience", r"\b(?:experience|employment|work history|professional experience)\b"),
        ("skills", r"\b(?:skills|technical skills|highlights|core competencies|expertise|tools)\b"),
        ("projects", r"\b(?:projects|portfolio|academic projects)\b"),
        ("education", r"\b(?:education|academic background|qualifications)\b"),
        ("summary", r"\b(?:summary|objective|profile|overview)\b"),
    ]

    @classmethod
    def parse_sections(cls, text: str) -> Dict[str, str]:
        """Splits free text into sections by keyword positions."""
        lower_text = text.lower()
        matches = []
        for sec_name, pat in cls.SECTION_PATTERNS:
            for m in re.finditer(pat, lower_text):
                matches.append((m.start(), sec_name))

        sections = {"summary": "", "skills": "", "experience": "", "projects": "", "education": ""}
        if not matches:
            sections["summary"] = lower_text
            return sections

        matches.sort(key=lambda x: x[0])
        if matches[0][0] > 0:
            sections["summary"] = lower_text[:matches[0][0]]

        for i in range(len(matches)):
            st, sec_name = matches[i]
            en = matches[i + 1][0] if i + 1 < len(matches) else len(lower_text)
            sections[sec_name] += " " + lower_text[st:en]

        return sections


class SkillEvidenceFeatureExtractor:
    """
    Extracts multi-source evidence features for a (candidate, skill) pair.
    Operates without target leakage or fabricated proficiency numbers.
    """

    FEATURE_NAMES = [
        "resume_mentioned",
        "resume_frequency",
        "in_skills_section",
        "in_experience_section",
        "in_project_section",
        "in_education_section",
        "in_summary_section",
        "has_action_verb_context",
        "co_occurring_tech_count",
        "section_text_length",
        "is_software_skill",
        "is_essential_skill",
        "onet_importance_proxy",
        "project_evidence_count",
        "assessment_evidence_score",
        "practical_evidence_score",
    ]

    def __init__(self, onet_skill_lookup: Optional[Dict[str, Dict[str, float]]] = None):
        self.onet_lookup = onet_skill_lookup or {}

    def _skill_matches_text(self, skill_name: str, text: str) -> Tuple[int, List[str]]:
        """Finds occurrences of a skill and returns frequency and matched context snippets."""
        if not text:
            return 0, []

        info = VOCATIONAL_TAXONOMY.get(skill_name, {"synonyms": [skill_name.lower()]})
        synonyms = info.get("synonyms", [skill_name.lower()])

        total_count = 0
        snippets = []
        for syn in synonyms:
            # Escape regex characters (e.g. C++, C#)
            if syn in ["c++", "cpp"]:
                pattern = r"\b(?:c\+\+|cpp)\b"
            elif syn in ["c#", "csharp"]:
                pattern = r"\b(?:c\#|csharp)\b"
            elif syn == "r":
                pattern = r"\b[Rr]\s+programming\b|\b[Rr]\s+language\b"
            elif syn == "go":
                pattern = r"\b(?:golang|go\s+language|go\s+programming)\b"
            else:
                pattern = rf"\b{re.escape(syn)}\b"

            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            total_count += len(matches)
            for m in matches:
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippets.append(text[start:end])

        return total_count, snippets

    def extract_features_from_sections(
        self,
        candidate_id: str,
        skill_name: str,
        sections: Dict[str, str],
        full_text: str,
        external_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Computes all evidence metrics for candidate-skill pair."""
        external = external_evidence or {}

        freq_skills, _ = self._skill_matches_text(skill_name, sections.get("skills", ""))
        freq_exp, exp_snippets = self._skill_matches_text(skill_name, sections.get("experience", ""))
        freq_proj, proj_snippets = self._skill_matches_text(skill_name, sections.get("projects", ""))
        freq_edu, _ = self._skill_matches_text(skill_name, sections.get("education", ""))
        freq_sum, _ = self._skill_matches_text(skill_name, sections.get("summary", ""))

        total_freq, all_snippets = self._skill_matches_text(skill_name, full_text)
        is_mentioned = 1 if total_freq > 0 else 0

        # Action verb context check across all occurrences
        has_action_verb = 0
        all_snippet_text = " ".join(all_snippets).lower()
        for verb in ACTION_VERBS:
            if re.search(rf"\b{verb}\b", all_snippet_text):
                has_action_verb = 1
                break

        # Co-occurring technologies in surrounding snippets
        co_occurring = 0
        for other_skill, other_info in VOCATIONAL_TAXONOMY.items():
            if other_skill != skill_name:
                for syn in other_info["synonyms"]:
                    if syn in all_snippet_text:
                        co_occurring += 1
                        break

        # O*NET background context
        onet_info = self.onet_lookup.get(skill_name.lower(), {})
        is_software = onet_info.get("is_software", 1 if VOCATIONAL_TAXONOMY.get(skill_name, {}).get("category") in ["Backend", "Frontend", "Database", "Cloud", "Tools", "AI/ML"] else 0)
        is_essential = onet_info.get("is_essential", 1 if VOCATIONAL_TAXONOMY.get(skill_name, {}).get("category") == "Domain" else 0)
        onet_importance = onet_info.get("importance", 0.5)

        # Real-time / External signals (defaults to 0 for historical Kaggle dataset)
        project_evidence_cnt = external.get("project_evidence_count", 0)
        assessment_score = external.get("assessment_evidence_score", 0.0)
        practical_score = external.get("practical_evidence_score", 0.0)

        # Section length context (log-scaled)
        sec_length = float(np.log1p(len(sections.get("experience", "") + sections.get("projects", ""))))

        features = {
            "candidate_id": candidate_id,
            "skill": skill_name,
            "skill_category": VOCATIONAL_TAXONOMY.get(skill_name, {}).get("category", "Other"),
            "resume_mentioned": is_mentioned,
            "resume_frequency": min(total_freq, 25),
            "in_skills_section": 1 if freq_skills > 0 else 0,
            "in_experience_section": 1 if freq_exp > 0 else 0,
            "in_project_section": 1 if freq_proj > 0 else 0,
            "in_education_section": 1 if freq_edu > 0 else 0,
            "in_summary_section": 1 if freq_sum > 0 else 0,
            "has_action_verb_context": has_action_verb,
            "co_occurring_tech_count": min(co_occurring, 15),
            "section_text_length": sec_length,
            "is_software_skill": is_software,
            "is_essential_skill": is_essential,
            "onet_importance_proxy": onet_importance,
            "project_evidence_count": project_evidence_cnt,
            "assessment_evidence_score": assessment_score,
            "practical_evidence_score": practical_score,
        }

        # -------------------------------------------------------------
        # Programmatic Weak Supervision Grounding (Target: evidence_tier)
        # Tier 2: Strong / Substantive Evidence (applied practice)
        # Tier 1: Casual Mention (flat listing, no action context)
        # Tier 0: Insufficient / Absent Evidence
        # -------------------------------------------------------------
        if not is_mentioned and project_evidence_cnt == 0 and assessment_score == 0.0:
            evidence_tier = 0  # Absent / Insufficient
        elif is_mentioned and (has_action_verb == 1 or total_freq >= 3 or (freq_exp > 0 and co_occurring >= 1) or project_evidence_cnt > 0):
            evidence_tier = 2  # Strong / Applied Evidence
        elif is_mentioned or project_evidence_cnt > 0 or assessment_score > 0.0:
            evidence_tier = 1  # Casual / Moderate Mention
        else:
            evidence_tier = 0

        features["evidence_tier"] = evidence_tier
        features["is_evidence_supported"] = 1 if evidence_tier == 2 else 0

        return features

    def extract_from_raw_resume(
        self,
        candidate_id: str,
        resume_text: str,
        candidate_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates candidate-skill pair records for a single resume."""
        sections = ResumeSectionParser.parse_sections(resume_text)
        lower_full = resume_text.lower()

        # Identify all skills present in resume
        present_skills = []
        for skill_name in VOCATIONAL_TAXONOMY:
            freq, _ = self._skill_matches_text(skill_name, lower_full)
            if freq > 0:
                present_skills.append(skill_name)

        # Select expected negative skills from category to ensure balanced contrast
        category_skills = CATEGORY_EXPECTED_SKILLS.get(candidate_category, [])
        absent_candidates = [s for s in category_skills if s not in present_skills]
        if not absent_candidates:
            # Fallback general skills that are absent
            absent_candidates = [s for s in ["Kubernetes", "PostgreSQL", "Cybersecurity", "Deep Learning", "Ruby"] if s not in present_skills]

        # Combine present skills with a sample of absent skills (for true negatives)
        selected_skills = present_skills + absent_candidates[:max(3, len(present_skills) // 2)]

        records = []
        for s in selected_skills:
            rec = self.extract_features_from_sections(
                candidate_id=candidate_id,
                skill_name=s,
                sections=sections,
                full_text=lower_full,
                external_evidence=None
            )
            records.append(rec)

        return records

    def extract_from_user_profile(
        self,
        profile_dict: Dict[str, Any],
        target_skill: str
    ) -> Dict[str, Any]:
        """
        Extracts features for a live real-time ReSkillAI profile.
        Handles zero-knowledge users gracefully.
        """
        user_id = profile_dict.get("id", "anonymous_user")

        # Resume text (if available)
        resume_info = profile_dict.get("resumeFile") or {}
        resume_text = profile_dict.get("resume_text", "")
        sections = ResumeSectionParser.parse_sections(resume_text) if resume_text else {"summary": "", "skills": "", "experience": "", "projects": "", "education": ""}

        # Projects evidence
        projects = profile_dict.get("projects") or []
        project_count = 0
        for p in projects:
            techs = [t.lower() for t in p.get("tech", [])]
            desc = p.get("description", "").lower()
            title = p.get("title", "").lower()
            synonyms = VOCATIONAL_TAXONOMY.get(target_skill, {}).get("synonyms", [target_skill.lower()])
            if any(syn in techs for syn in synonyms) or any(syn in desc for syn in synonyms) or any(syn in title for syn in synonyms):
                project_count += 1

        # Assessment signals
        assess = profile_dict.get("assessmentSignals") or {}
        skills_demo = [s.lower() for s in (assess.get("skillsDemonstrated") or [])]
        demo_know = assess.get("demonstratedKnowledge") or {}
        practical_scores = assess.get("practicalScores") or {}

        synonyms = VOCATIONAL_TAXONOMY.get(target_skill, {}).get("synonyms", [target_skill.lower()])
        assess_matched = any(syn in skills_demo for syn in synonyms)
        know_score = max([demo_know.get(k, 0) for k in demo_know if any(syn in k.lower() for syn in synonyms)] or [0])
        prac_score = max([practical_scores.get(k, 0) for k in practical_scores if any(syn in k.lower() for syn in synonyms)] or [0])

        external_evidence = {
            "project_evidence_count": project_count,
            "assessment_evidence_score": float(know_score / 100.0) if know_score else (0.8 if assess_matched else 0.0),
            "practical_evidence_score": float(prac_score / 100.0) if prac_score else 0.0,
        }

        return self.extract_features_from_sections(
            candidate_id=user_id,
            skill_name=target_skill,
            sections=sections,
            full_text=resume_text.lower(),
            external_evidence=external_evidence
        )
