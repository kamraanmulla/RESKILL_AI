from typing import Dict, Any, List, Set
from ...schemas.profile import StudentProfile
from ..career_taxonomy import CAREER_TAXONOMY, get_career_by_id

# Curated adjacency matrix mapping skills to adjacent companion disciplines
SKILL_ADJACENCY: Dict[str, Set[str]] = {
    "python": {"scripting", "backend", "data analysis", "automation", "bash", "linux", "cloud", "aws"},
    "javascript": {"typescript", "frontend", "react", "node.js", "ui/ux", "web security", "scripting", "automation"},
    "typescript": {"javascript", "frontend", "backend", "node.js", "type safety", "react"},
    "node.js": {"backend", "express", "apis", "rest apis", "docker", "microservices", "cloud", "ci/cd", "linux"},
    "linux": {"bash", "docker", "cloud", "networking", "security", "devops", "shell scripting", "ci/cd"},
    "git": {"ci/cd", "collaborative devops", "version control", "sdlc", "devops", "collaboration"},
    "docker": {"kubernetes", "cloud", "containerization", "microservices", "devops", "ci/cd", "linux", "infrastructure"},
    "sql": {"database design", "data modeling", "data engineering", "backend", "database", "analytics"},
    "mongodb": {"nosql", "database", "backend", "data storage", "data modeling"},
    "networking": {"wireshark", "cybersecurity", "firewalls", "cloud networking", "tcp/ip", "cloud", "infrastructure"},
    "react": {"next.js", "state management", "frontend architecture", "ui performance", "javascript"},
    "cloud": {"aws", "azure", "gcp", "docker", "kubernetes", "networking", "infrastructure", "devops", "cloud"},
    "aws": {"cloud", "infrastructure", "docker", "devops", "ec2", "s3", "cloud computing"},
    "cybersecurity": {"threat detection", "security", "firewalls", "linux", "networking", "soc operations"}
}

class TransferabilityEngine:
    @staticmethod
    def calculate_transferability(
        profile: StudentProfile,
        destination_career_id: str,
        source_career_id: str = "career_fullstack"
    ) -> Dict[str, Any]:
        """Calculates reproducible, dynamic skill transferability between careers."""
        all_careers = {c.id: c for c in CAREER_TAXONOMY}
        
        dest_career = all_careers.get(destination_career_id) or get_career_by_id("career_cybersecurity") or CAREER_TAXONOMY[0]
        src_career = all_careers.get(source_career_id) or CAREER_TAXONOMY[0]

        dest_core = list(dest_career.coreSkills or [])
        dest_sec = list(dest_career.secondarySkills or [])
        user_skills: Dict[str, int] = {
            s.name.lower().strip(): s.proficiency for s in (profile.skills or [])
        }

        transferable_skills: List[str] = []
        bridge_skills: List[str] = []
        missing_skills: List[str] = []

        total_earned_points = 0.0
        # Core skills weighted at 1.0 (100 max pts each), secondary skills at 0.5 (50 max pts each)
        max_possible_points = max(1.0, (float(len(dest_core)) * 1.0 + float(len(dest_sec)) * 0.5) * 100.0)

        for req in dest_core + dest_sec:
            req_lower = req.lower().strip()
            is_core = req in dest_core
            weight = 1.0 if is_core else 0.5

            # 1. Direct overlap
            matched_user_skill = next((u for u in user_skills if u == req_lower or u in req_lower or req_lower in u), None)
            if matched_user_skill:
                prof = user_skills[matched_user_skill]
                transferable_skills.append(req)
                total_earned_points += prof * weight
            else:
                # 2. Check for adjacent bridge skills
                adjacent_found = False
                for u_skill, u_prof in user_skills.items():
                    adj_set = SKILL_ADJACENCY.get(u_skill, set())
                    if req_lower in adj_set or any(adj in req_lower or req_lower in adj for adj in adj_set):
                        bridge_skills.append(f"{req} (via {u_skill.title()})")
                        total_earned_points += u_prof * 0.70 * weight
                        adjacent_found = True
                        break
                
                if not adjacent_found:
                    missing_skills.append(req)

        # Foundational technical literacy bonus: candidates with existing programming/version-control experience
        foundational_bonus = 0.0
        if len(user_skills) > 0:
            foundational_bonus += min(15.0, float(len(user_skills)) * 3.0)

        # Experience & project weighting factor
        if profile.projects and len(profile.projects) > 0:
            foundational_bonus += min(10.0, float(len(profile.projects)) * 3.0)
        if profile.experience and len(profile.experience) > 0:
            foundational_bonus += 5.0

        raw_score = (total_earned_points / max_possible_points) * 75.0 + foundational_bonus
        overall_score = max(0, min(100, int(round(raw_score))))

        # Deduce structured explanation
        if overall_score >= 65:
            explanation = f"High transferability: Your background provides a strong foundation for {dest_career.title} with solid technical and architectural overlap."
        elif overall_score >= 40:
            explanation = f"Moderate transferability: Foundational engineering competencies transfer effectively; targeted upskilling in {dest_career.title} core gaps will bridge the role."
        else:
            explanation = f"Pivotal transition: Moving into {dest_career.title} requires systematic focus on specialized foundational requirements."

        return {
            "sourceCareer": src_career.title,
            "destinationCareer": dest_career.title,
            "overallScore": overall_score,
            "transferableSkills": transferable_skills,
            "bridgeSkills": bridge_skills,
            "missingSkills": missing_skills,
            "explanation": explanation
        }

transferability_engine = TransferabilityEngine()
