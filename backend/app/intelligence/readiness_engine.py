from typing import Optional
from ..schemas.profile import StudentProfile
from ..schemas.intelligence import ReadinessResult, ReadinessBreakdown
from .career_taxonomy import get_career_by_id

class ReadinessEngine:
    @staticmethod
    def calculate_readiness(profile: StudentProfile, target_career_id: Optional[str] = None) -> ReadinessResult:
        cid = target_career_id or profile.targetCareerId or "career_fullstack"
        target_career = get_career_by_id(cid)

        # In ZERO_KNOWLEDGE state with no skills and no resume
        if len(profile.skills) == 0 and not profile.resumeFile and not profile.practicalExperience:
            return ReadinessResult(
                readinessScore=0,
                readinessPoints=0,
                readinessLevel="Uncalibrated",
                breakdown=ReadinessBreakdown(
                    skillAlignmentPoints=0,
                    practicalExperiencePoints=0,
                    assessmentPoints=0,
                    educationPoints=0,
                    totalPoints=0
                ),
                statusMessage="Readiness unavailable. Insufficient profile data.",
                recommendationHint="Upload your resume or select your known skills to calibrate your hiring baseline."
            )

        # 1. Skill Alignment Points (Max 450 pts)
        skill_points = 0
        matched_core_count = 0
        user_skills = profile.skills

        for req in target_career.coreSkills:
            found = next((s for s in user_skills if s.name.lower() in req.lower() or req.lower() in s.name.lower()), None)
            if found:
                matched_core_count += 1
                skill_points += int((found.proficiency / 100.0) * (350 / len(target_career.coreSkills)))

        for sec in target_career.secondarySkills:
            found = next((s for s in user_skills if s.name.lower() in sec.lower() or sec.lower() in s.name.lower()), None)
            if found:
                skill_points += int((found.proficiency / 100.0) * (100 / len(target_career.secondarySkills)))

        skill_points = min(450, skill_points)

        # 2. Practical Experience & Projects (Max 250 pts)
        exp_points = 0
        if profile.projects:
            exp_points += min(150, len(profile.projects) * 75)
        if profile.experience:
            exp_points += min(100, len(profile.experience) * 50)
        if profile.practicalExperience and profile.practicalExperience != "I haven't worked on anything yet":
            exp_points = max(exp_points, 120)

        exp_points = min(250, exp_points)

        # 3. Assessment Alignment Points (Max 150 pts)
        assessment_points = 0
        if profile.assessmentSignals:
            assessment_points = 120
            # bonus if domain preference aligns with career category
            for dp in profile.assessmentSignals.domainPreferences:
                if dp.lower() in target_career.category.lower() or target_career.category.lower() in dp.lower():
                    assessment_points = 150
                    break

        # 4. Education & Academic Background Points (Max 150 pts)
        edu_points = 60 # baseline for college student
        if profile.degree:
            deg = profile.degree.lower()
            if "b.tech" in deg or "b.e." in deg or "computer" in deg or "bca" in deg or "mca" in deg:
                edu_points = 120
            else:
                edu_points = 90
        if profile.cgpa > 0:
            if profile.cgpa >= 8.0:
                edu_points = min(150, edu_points + 30)
            elif profile.cgpa >= 7.0:
                edu_points = min(150, edu_points + 15)

        edu_points = min(150, edu_points)

        # Total Points and Final Percentage
        total_points = skill_points + exp_points + assessment_points + edu_points
        final_score = int(round((total_points / 1000.0) * 100.0))
        final_score = max(5, min(96, final_score))

        # Readiness Level Categorization
        if total_points >= 800:
            level = "Industry Ready"
            msg = f"Candidate exhibits top-tier alignment with {target_career.title} market expectations."
        elif total_points >= 650:
            level = "Proficient"
            msg = f"Solid baseline established for {target_career.title}. Near entry-level benchmarks."
        elif total_points >= 400:
            level = "Developing"
            msg = f"Fundamental skills detected. Focus on closing identified core gaps to reach hiring readiness."
        else:
            level = "Early Foundation"
            msg = f"Initial profile created. Follow the personalized roadmap modules to build required competencies."

        hint = f"Focus on mastering {target_career.coreSkills[0]} and {target_career.coreSkills[1]} to gain immediate readiness points."

        return ReadinessResult(
            readinessScore=final_score,
            readinessPoints=total_points,
            readinessLevel=level,
            breakdown=ReadinessBreakdown(
                skillAlignmentPoints=skill_points,
                practicalExperiencePoints=exp_points,
                assessmentPoints=assessment_points,
                educationPoints=edu_points,
                totalPoints=total_points
            ),
            statusMessage=msg,
            recommendationHint=hint
        )
