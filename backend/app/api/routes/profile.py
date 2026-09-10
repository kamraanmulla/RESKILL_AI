from fastapi import APIRouter
from .profile_store import get_profile, set_profile
from ...schemas.profile import StudentProfile, MinimalOnboardingRequest, Skill
from ...services.gemini_service import gemini_service

router = APIRouter(prefix="/profile", tags=["Profile Dossier"])

@router.get("", response_model=StudentProfile)
def read_profile():
    return get_profile()

@router.put("", response_model=StudentProfile)
def update_profile(updated: StudentProfile):
    set_profile(updated)
    return updated

@router.post("/onboarding", response_model=StudentProfile)
def submit_minimal_onboarding(data: MinimalOnboardingRequest):
    """
    Submits the 5 Core Questions for users without a resume:
    1. Education
    2. Skills (chips)
    3. Interests
    4. Career Direction
    5. Practical Experience (free text interpreted by Gemini)
    """
    profile = get_profile()

    if data.name and data.name.strip():
        profile.name = data.name.strip()

    profile.degree = data.education
    if data.field:
        profile.field = data.field

    # Core Question 2: Ingest Selected Skills
    skills_list = []
    for skill_name in data.skills:
        # Default category heuristics
        cat = "Other"
        sn = skill_name.lower()
        if any(k in sn for k in ["react", "html", "css", "javascript", "typescript", "figma"]):
            cat = "Frontend"
        elif any(k in sn for k in ["python", "node", "express", "sql", "api", "backend"]):
            cat = "Backend"
        elif any(k in sn for k in ["security", "networking", "linux", "threat", "siem"]):
            cat = "Security"
        elif any(k in sn for k in ["machine learning", "data", "pandas", "ai"]):
            cat = "AI/ML"
        elif any(k in sn for k in ["cloud", "docker", "git", "devops"]):
            cat = "Tools"

        skills_list.append(
            Skill(
                name=skill_name,
                category=cat, # type: ignore
                proficiency=70,
                level="Proficient",
                verified=True,
                detectedFrom="Smart Onboarding"
            )
        )

    # Core Question 3: Interests
    profile.interests = data.interests

    # Core Question 4: Career Direction
    if data.careerDirection and data.careerDirection != "I'm not sure yet":
        profile.careerInterest = data.careerDirection
        # Match against taxonomy if exact match found
        cd = data.careerDirection.lower()
        if "cyber" in cd:
            profile.targetCareerId = "career_cybersecurity"
        elif "machine learning" in cd or "ai" in cd:
            profile.targetCareerId = "career_ai_ml"
        elif "frontend" in cd:
            profile.targetCareerId = "career_frontend"
        elif "backend" in cd:
            profile.targetCareerId = "career_backend"
        elif "cloud" in cd or "devops" in cd:
            profile.targetCareerId = "career_cloud_devops"
        elif "data" in cd:
            profile.targetCareerId = "career_data_science"
        elif "software" in cd or "full" in cd:
            profile.targetCareerId = "career_fullstack"
    else:
        profile.careerInterest = "I'm not sure yet"

    # Core Question 5: Practical Experience free-text interpreted by Gemini
    if data.practicalExperienceText:
        profile.practicalExperience = data.practicalExperienceText
        interpreted_skills, err = gemini_service.interpret_experience_text(data.practicalExperienceText)
        for isk in interpreted_skills:
            if not any(s.name.lower() == isk.name.lower() for s in skills_list):
                skills_list.append(isk)

    profile.skills = skills_list

    # Update Profile State Machine
    if len(profile.skills) >= 2:
        profile.profileState = "PROFILE_READY" if not profile.assessmentSignals else "PERSONALIZED"
        profile.profileCompleteness = 70 if not profile.assessmentSignals else 100
    else:
        profile.profileState = "PROFILE_INCOMPLETE"
        profile.profileCompleteness = 35

    set_profile(profile)
    return profile
