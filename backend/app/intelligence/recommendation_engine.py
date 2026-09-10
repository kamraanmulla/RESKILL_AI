from typing import List
from ..schemas.profile import StudentProfile
from ..schemas.intelligence import CareerRecommendation, CareerRole
from .career_taxonomy import CAREER_TAXONOMY

class CareerRecommendationEngine:
    @staticmethod
    def _skill_matches(user_skill: str, target_skill: str) -> bool:
        u = user_skill.lower().strip()
        t = target_skill.lower().strip()
        return u == t or u in t or t in u

    @classmethod
    def recommend_careers(cls, profile: StudentProfile) -> List[CareerRecommendation]:
        recommendations: List[CareerRecommendation] = []
        user_skills = profile.skills
        has_skills = len(user_skills) > 0
        signals = profile.assessmentSignals

        for career in CAREER_TAXONOMY:
            matched_skills: List[str] = []
            missing_skills: List[str] = []

            core_score = 0.0
            for req in career.coreSkills:
                found = next((s for s in user_skills if cls._skill_matches(s.name, req)), None)
                if found:
                    matched_skills.append(req)
                    core_score += (found.proficiency / 100.0)
                else:
                    missing_skills.append(req)

            sec_score = 0.0
            for sec in career.secondarySkills:
                found = next((s for s in user_skills if cls._skill_matches(s.name, sec)), None)
                if found:
                    matched_skills.append(sec)
                    sec_score += (found.proficiency / 100.0)

            # Raw skill match calculation
            core_weight = len(career.coreSkills) * 1.0
            sec_weight = len(career.secondarySkills) * 0.4
            max_weight = core_weight + sec_weight

            skill_pct = 0.0
            if has_skills and max_weight > 0:
                skill_pct = ((core_score * 1.0 + sec_score * 0.4) / max_weight) * 100.0

            # Interest alignment
            interest_alignment = 50
            if signals and signals.careerInterestScores:
                # Map signals to career domains
                domain_key = career.category.lower()
                for k, v in signals.careerInterestScores.items():
                    if k.lower() in domain_key or domain_key in k.lower():
                        interest_alignment = max(interest_alignment, v)

            # Career direction bonus
            if profile.careerInterest:
                ci = profile.careerInterest.lower()
                ct = career.title.lower()
                cc = career.category.lower()
                if ci in ct or ct in ci or ci in cc:
                    interest_alignment = min(100, interest_alignment + 30)

            # Combined weighted score
            if not has_skills and not signals and not profile.careerInterest:
                final_score = 0
                confidence = "Uncalibrated"
                explanation = "Complete onboarding or upload a resume to calculate verified career match."
            elif not has_skills:
                # In initial profile without skills, driven purely by stated interest
                final_score = int(round(interest_alignment * 0.3))
                confidence = "Emerging"
                explanation = f"Initial interest alignment ({interest_alignment}%). Add technical skills or upload resume to compute verified match."
            else:
                final_score = int(round(skill_pct * 0.75 + interest_alignment * 0.25))
                final_score = min(98, max(15, final_score))
                if final_score >= 75:
                    confidence = "High"
                elif final_score >= 50:
                    confidence = "Moderate"
                else:
                    confidence = "Emerging"

                explanation = (
                    f"Strong alignment across {len(matched_skills)} verified competencies "
                    f"({', '.join(matched_skills[:3]) if matched_skills else 'foundational'}). "
                    f"Key development gap: {', '.join(missing_skills[:2]) if missing_skills else 'advanced architecture'}."
                )

            updated_career = career.model_copy(update={"currentMatchPercentage": final_score})

            recommendations.append(
                CareerRecommendation(
                    career=updated_career,
                    matchScore=final_score,
                    confidence=confidence,
                    matchedSkills=matched_skills,
                    missingSkills=missing_skills,
                    interestAlignment=interest_alignment,
                    explanation=explanation
                )
            )

        # Sort deterministically by matchScore descending, then by title
        recommendations.sort(key=lambda r: (r.matchScore, r.career.title), reverse=True)
        return recommendations
