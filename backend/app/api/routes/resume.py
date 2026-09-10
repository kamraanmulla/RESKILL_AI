from fastapi import APIRouter, UploadFile, File, HTTPException
from ...services.resume_service import resume_service
from .profile_store import get_profile, set_profile
from ...schemas.profile import StudentProfile, ResumeFileInfo, Skill, StudentProject, StudentExperience

router = APIRouter(prefix="/resume", tags=["Resume Ingestion"])

@router.post("/analyze", response_model=StudentProfile)
async def analyze_resume(file: UploadFile = File(...)):
    filename = file.filename or "resume.pdf"
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Size formatting
    size_kb = len(file_bytes) / 1024.0
    size_str = f"{size_kb:.0f} KB" if size_kb > 0 else "248 KB"

    # Analyze via Gemini or resilient fallback
    extracted = resume_service.analyze_resume(file_bytes, filename)

    profile = get_profile()
    profile.resumeFile = ResumeFileInfo(
        name=filename,
        size=size_str,
        uploadedAt="Just now"
    )

    # Populate extracted values without overwriting valid existing user data
    if extracted.get("name") and (profile.name == "New Candidate" or not profile.name or profile.name == profile.email.split("@")[0].capitalize()):
        profile.name = extracted["name"]
    if extracted.get("degree"):
        profile.degree = extracted["degree"]
    if extracted.get("institution"):
        profile.institution = extracted["institution"]
    if extracted.get("graduationYear"):
        profile.graduationYear = extracted["graduationYear"]

    # Ingest skills
    raw_skills = extracted.get("skills", [])
    ingested_skills = []
    for s in raw_skills:
        ingested_skills.append(
            Skill(
                name=s["name"],
                category=s.get("category", "Other"),
                proficiency=s.get("proficiency", 70),
                level="Proficient" if s.get("proficiency", 70) >= 75 else "Familiar",
                verified=True,
                detectedFrom="Resume Ingestion"
            )
        )
    profile.skills = ingested_skills

    # Ingest projects if any
    raw_projects = extracted.get("projects", [])
    ingested_projects = []
    for p in raw_projects:
        ingested_projects.append(
            StudentProject(
                title=p["title"],
                tech=p.get("tech", []),
                description=p.get("description", "")
            )
        )
    profile.projects = ingested_projects

    # Ingest experience if any
    raw_experience = extracted.get("experience", [])
    ingested_experience = []
    for exp in raw_experience:
        ingested_experience.append(
            StudentExperience(
                title=exp["title"],
                company=exp.get("company", "Organization"),
                period=exp.get("period", "Previous"),
                description=exp.get("description", "")
            )
        )
    profile.experience = ingested_experience

    # Update state machine: if assessment already taken -> PERSONALIZED; otherwise PROFILE_READY
    if profile.assessmentSignals:
        profile.profileState = "PERSONALIZED"
    else:
        profile.profileState = "PROFILE_READY"

    profile.profileCompleteness = 75 if not profile.assessmentSignals else 100
    set_profile(profile)
    return profile
