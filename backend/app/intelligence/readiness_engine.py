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
                recommendationHint="Upload your resume or select your known skills to calibrate your hiring baseline.",
                evidence_summary="No profile evidence has been submitted. Readiness is uncalibrated.",
                evidence_confidence=0.0,
                evidence_sources=[],
                evidence_strength=None,
                evidence_level="INSUFFICIENT"
            )

        # 1. Skill Alignment Points (Max 400 pts — 40%)
        skill_points = 0
        matched_core_count = 0
        user_skills = profile.skills

        if target_career.coreSkills:
            core_unit = 300.0 / len(target_career.coreSkills)
            for req in target_career.coreSkills:
                found = next((s for s in user_skills if s.name.lower() in req.lower() or req.lower() in s.name.lower()), None)
                if found:
                    matched_core_count += 1
                    skill_points += int((found.proficiency / 100.0) * core_unit)

        if target_career.secondarySkills:
            sec_unit = 100.0 / len(target_career.secondarySkills)
            for sec in target_career.secondarySkills:
                found = next((s for s in user_skills if s.name.lower() in sec.lower() or sec.lower() in s.name.lower()), None)
                if found:
                    skill_points += int((found.proficiency / 100.0) * sec_unit)

        skill_points = min(400, skill_points)

        # 2. Practical Experience & Projects (Max 300 pts — 30%)
        exp_points = 0
        if profile.projects:
            exp_points += min(160, len(profile.projects) * 80)
        if profile.experience:
            exp_points += min(140, len(profile.experience) * 70)
        if not profile.projects and not profile.experience and profile.practicalExperience and profile.practicalExperience != "I haven't worked on anything yet":
            # Points for free-text practical description
            txt_len = len(profile.practicalExperience.strip())
            exp_points = min(150, max(60, txt_len // 2))

        exp_points = min(300, exp_points)

        # 3. Assessment Alignment Points (Max 150 pts — 15%)
        # Strictly computed from actual candidate answers, practical challenge, and confidence
        assessment_points = 0
        if profile.assessmentSignals:
            signals = profile.assessmentSignals
            # A. Demonstrated knowledge score (0..80 pts)
            know_dict = signals.demonstratedKnowledge or {}
            domain_score = 0
            if know_dict:
                # Target category match or average
                matched_domain_scores = [v for k, v in know_dict.items() if k.lower() in target_career.category.lower() or target_career.category.lower() in k.lower()]
                if matched_domain_scores:
                    domain_score = max(matched_domain_scores)
                else:
                    domain_score = sum(know_dict.values()) // max(1, len(know_dict))
            elif signals.careerInterestScores:
                matched_interest_scores = [v for k, v in signals.careerInterestScores.items() if k.lower() in target_career.category.lower() or target_career.category.lower() in k.lower() or target_career.id.lower() in k.lower() or k.lower() in target_career.id.lower()]
                if matched_interest_scores:
                    domain_score = max(matched_interest_scores)
                else:
                    domain_score = sum(signals.careerInterestScores.values()) // max(1, len(signals.careerInterestScores))
            else:
                domain_score = 50

            knowledge_pts = int((domain_score / 100.0) * 80)

            # B. Practical challenge score (0..45 pts)
            prac_dict = signals.practicalScores or {}
            prac_score = max(prac_dict.values()) if prac_dict else (domain_score if domain_score > 0 else 50)
            practical_pts = int((prac_score / 100.0) * 45)


            # C. Confidence and domain preference alignment (0..25 pts)
            conf_pts = 0
            if signals.confidenceSignal:
                high_conf_count = sum(1 for v in signals.confidenceSignal.values() if "high" in str(v).lower())
                conf_pts += min(15, high_conf_count * 5)
            for dp in (signals.domainPreferences or []):
                if dp.lower() in target_career.category.lower() or target_career.category.lower() in dp.lower():
                    conf_pts += 10
                    break
            conf_pts = min(25, conf_pts)

            assessment_points = min(150, knowledge_pts + practical_pts + conf_pts)

        # 4. Education & Academic Background Points (Max 150 pts — 15%)
        edu_points = 50  # Baseline
        if profile.degree:
            deg = profile.degree.lower()
            if any(k in deg for k in ["b.tech", "b.e.", "computer", "bca", "mca", "m.tech", "software", "information"]):
                edu_points = 100
            else:
                edu_points = 75
        elif profile.academicLevel:
            edu_points = 70

        if profile.cgpa > 0:
            if profile.cgpa >= 8.5:
                edu_points += 50
            elif profile.cgpa >= 7.5:
                edu_points += 35
            elif profile.cgpa >= 6.5:
                edu_points += 20
        else:
            edu_points += 20  # Default academic progress baseline

        edu_points = min(150, edu_points)

        # Total Points and Final Percentage
        total_points = skill_points + exp_points + assessment_points + edu_points
        final_score = int(round((total_points / 1000.0) * 100.0))
        final_score = max(5, min(98, final_score))

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

        # Phase 5: Evidence Summary & Multi-Source Corroboration
        try:
            from ..services.skill_evidence_service import skill_evidence_service
        except Exception:
            skill_evidence_service = None

        ev_summary = None
        ev_confidence = 0.0
        ev_sources_set = set()
        ev_strengths = []
        ev_level = "INSUFFICIENT"

        if skill_evidence_service:
            check_skills = [s.name for s in user_skills]
            if not check_skills and target_career.coreSkills:
                check_skills = target_career.coreSkills[:3]
            for s_name in check_skills:
                try:
                    ev = skill_evidence_service.evaluate_skill_evidence(profile, s_name)
                    if ev.evidence_strength is not None:
                        ev_strengths.append(ev.evidence_strength)
                    if ev.confidence > 0:
                        ev_confidence = max(ev_confidence, ev.confidence)
                    for src in ev.evidence_sources:
                        ev_sources_set.add(src)
                except Exception:
                    pass

        active_ev_sources = sorted(list(ev_sources_set))
        avg_strength = round(sum(ev_strengths) / len(ev_strengths), 2) if ev_strengths else None

        if active_ev_sources:
            if len(active_ev_sources) >= 3 and (avg_strength or 0) >= 0.70:
                ev_level = "STRONG"
            elif len(active_ev_sources) >= 2 or (avg_strength or 0) >= 0.40:
                ev_level = "MODERATE"
            else:
                ev_level = "WEAK"
            ev_summary = (
                f"Readiness score is corroborated by {len(active_ev_sources)} empirical channel(s): "
                f"{', '.join(active_ev_sources)} across documented candidate profile artifacts."
            )
        else:
            ev_summary = "Readiness score is uncorroborated by empirical external artifacts."

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
            recommendationHint=hint,
            evidence_summary=ev_summary,
            evidence_confidence=ev_confidence,
            evidence_sources=active_ev_sources,
            evidence_strength=avg_strength,
            evidence_level=ev_level
        )
