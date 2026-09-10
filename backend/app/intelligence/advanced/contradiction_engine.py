from typing import Dict, Any, List
from ...schemas.profile import StudentProfile

class ContradictionEngine:
    @staticmethod
    def detect_contradictions(profile: StudentProfile) -> List[Dict[str, Any]]:
        """Identifies evidence calibration mismatches between claimed proficiency and project/assessment signals.
        Strictly frames outputs as constructive 'Evidence Mismatches', never accusing the candidate.
        """
        contradictions: List[Dict[str, Any]] = []
        user_skills = profile.skills or []
        
        # Aggregate project tech mentions
        project_tech: List[str] = []
        for p in (profile.projects or []):
            project_tech.extend([t.lower().strip() for t in (p.tech or [])])

        assessment_style = ""
        if profile.assessmentSignals:
            assessment_style = getattr(profile.assessmentSignals, "styleSignal", "").lower()

        for s in user_skills:
            s_lower = s.name.lower().strip()
            claimed_prof = s.proficiency or 60
            level_str = s.level or ("Proficient" if claimed_prof >= 75 else "Familiar")
            
            # Case 1: Claimed high proficiency (>= 80) but zero mentions in any projects or practical experience
            is_advanced_claim = claimed_prof >= 80 or level_str in ["Proficient", "Expert"]
            in_projects = any(s_lower in pt for pt in project_tech)
            in_practical = bool(profile.practicalExperience and s_lower in profile.practicalExperience.lower())
            
            if is_advanced_claim and not in_projects and not in_practical:
                contradictions.append({
                    "skill": s.name,
                    "claimedProficiency": f"{claimed_prof}% ({level_str})",
                    "evidenceProficiency": "Unverified in Projects",
                    "evidenceSources": ["Self-Claimed Skill", "Project Repositories"],
                    "severity": "MEDIUM",
                    "explanation": f"Evidence mismatch: {s.name} is indicated at a high competency level, but no concrete code artifacts or project descriptions currently reference it.",
                    "recommendation": f"Add a portfolio project, repository link, or practical case study demonstrating hands-on implementation of {s.name}."
                })

            # Case 2: Claimed Systems/Architecture depth with purely exploratory/theoretical assessment signals
            if s_lower in ["cloud", "docker", "kubernetes", "networking"] and claimed_prof >= 75:
                if "conceptual" in assessment_style or "exploring" in assessment_style:
                    contradictions.append({
                        "skill": s.name,
                        "claimedProficiency": f"{claimed_prof}% ({level_str})",
                        "evidenceProficiency": "Conceptual Assessment Signal",
                        "evidenceSources": ["Technical Claim", "Diagnostic Assessment"],
                        "severity": "LOW",
                        "explanation": f"Evidence mismatch: Diagnostic responses suggest early theoretical exploration, whereas {s.name} is marked as production-ready.",
                        "recommendation": f"Complete a hands-on lab or guided capstone milestone in {s.name} to reinforce practical troubleshooting intuition."
                    })

            # Case 3: Advanced claimed proficiency vs. basic assessment diagnostic signal
            if is_advanced_claim and profile.assessmentSignals:
                ps_style = (profile.assessmentSignals.problemSolvingStyle or "").lower()
                signals_text = " ".join(profile.assessmentSignals.workStyleSignals or []).lower()
                is_basic_assessment = any(w in ps_style or w in signals_text for w in ["basic", "introductory", "foundational", "beginner", "exploratory"])
                if is_basic_assessment and not any(c["skill"] == s.name and "Diagnostic Assessment" in c["evidenceSources"] for c in contradictions):
                    contradictions.append({
                        "skill": s.name,
                        "claimedProficiency": f"{claimed_prof}% ({level_str})",
                        "evidenceProficiency": "Foundational Assessment Diagnostic",
                        "evidenceSources": ["Claimed Skill", "Diagnostic Assessment"],
                        "severity": "MEDIUM",
                        "explanation": f"Evidence mismatch: {s.name} is marked at an advanced competency level, whereas initial diagnostic assessment responses reflect foundational application patterns.",
                        "recommendation": f"Complete a practical benchmark or guided challenge in {s.name} to calibrate assessment evidence with claimed proficiency."
                    })

        return contradictions

contradiction_engine = ContradictionEngine()
