from typing import List, Optional
from ..schemas.profile import StudentProfile
from ..schemas.intelligence import SkillGapItem
from .career_taxonomy import get_career_by_id

class SkillGapEngine:
    @staticmethod
    def _categorize_skill(skill_name: str) -> str:
        s = skill_name.lower()
        if any(x in s for x in ["react", "html", "css", "javascript", "typescript", "figma", "ui"]):
            return "Frontend"
        if any(x in s for x in ["node", "express", "python", "rest", "api", "django", "fastapi"]):
            return "Backend"
        if any(x in s for x in ["sql", "mongo", "postgres", "database"]):
            return "Database"
        if any(x in s for x in ["security", "siem", "incident", "wireshark", "threat", "firewall"]):
            return "Security"
        if any(x in s for x in ["docker", "kubernetes", "cloud", "aws", "git", "linux", "ci/cd"]):
            return "Tools"
        if any(x in s for x in ["machine learning", "data analysis", "pandas", "pytorch", "statistics"]):
            return "AI/ML"
        return "Other"

    @classmethod
    def calculate_skill_gaps(cls, profile: StudentProfile, target_career_id: Optional[str] = None) -> List[SkillGapItem]:
        cid = target_career_id or profile.targetCareerId or "career_fullstack"
        target_career = get_career_by_id(cid)
        user_skills = profile.skills

        all_req_skills = [(s, 80, True) for s in target_career.coreSkills] + \
                         [(s, 65, False) for s in target_career.secondarySkills]

        items: List[SkillGapItem] = []

        for skill_name, required_level, is_core in all_req_skills:
            found = next(
                (s for s in user_skills if s.name.lower() == skill_name.lower() or
                 s.name.lower() in skill_name.lower() or skill_name.lower() in s.name.lower()),
                None
            )

            student_level = found.proficiency if found else 0
            gap = max(0, required_level - student_level)

            if gap == 0 or student_level >= required_level:
                priority = "Strong"
                status = "Mastered"
                recommendation = f"Solid competency established ({student_level}%). Maintain by applying in end-to-end architectures."
            elif student_level > 0:
                priority = "Developing"
                status = "In Progress"
                recommendation = f"Active exposure detected ({student_level}%). Deepen practical project exercises to close remaining {gap}% gap."
            else:
                priority = "Gap"
                status = "Not Started"
                recommendation = f"Essential entry-level requirement for {target_career.title}. Prioritize via structured roadmap modules."

            items.append(
                SkillGapItem(
                    skill=skill_name,
                    category=cls._categorize_skill(skill_name),
                    yourLevel=student_level,
                    requiredLevel=required_level,
                    gap=gap,
                    priority=priority,
                    status=status,
                    recommendation=recommendation
                )
            )

        # Sort: Gaps first, then Developing, then Strong
        priority_order = {"Gap": 0, "Developing": 1, "Strong": 2}
        items.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.gap))
        return items
