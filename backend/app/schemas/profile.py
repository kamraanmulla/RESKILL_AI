from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

ProfileState = Literal["ZERO_KNOWLEDGE", "PROFILE_INCOMPLETE", "PROFILE_READY", "PERSONALIZED"]
SkillCategory = Literal["Frontend", "Backend", "Database", "Tools", "Security", "AI/ML", "Cloud", "Other"]
SkillLevel = Literal["Novice", "Familiar", "Proficient", "Expert"]

class Skill(BaseModel):
    name: str
    category: SkillCategory = "Other"
    proficiency: int = Field(default=60, ge=0, le=100)
    level: SkillLevel = "Familiar"
    verified: bool = False
    detectedFrom: Optional[str] = "Manual entry"

class StudentExperience(BaseModel):
    title: str
    company: str
    period: str
    description: str

class StudentProject(BaseModel):
    title: str
    tech: List[str] = []
    period: Optional[str] = ""
    description: str
    link: Optional[str] = None

class StudentCertification(BaseModel):
    title: str
    issuer: str
    year: str
    credentialId: Optional[str] = None

class ResumeFileInfo(BaseModel):
    name: str
    size: str
    uploadedAt: str

class AssessmentSignals(BaseModel):
    domainPreferences: List[str] = []
    problemSolvingStyle: Optional[str] = None
    workStyleSignals: List[str] = []
    primaryMotivation: Optional[str] = None
    careerInterestScores: Dict[str, int] = {}

class StudentPreferences(BaseModel):
    weeklyHours: int = 12
    learningStyle: Literal["video", "reading", "interactive"] = "video"
    notifications: bool = True

class StudentProfile(BaseModel):
    id: str = "std_guest"
    name: str = "New Candidate"
    email: str = ""
    phone: str = ""
    degree: str = ""
    field: str = ""
    institution: str = ""
    graduationYear: int = 2026
    cgpa: float = 0.0
    bio: str = ""
    targetCareerId: str = ""
    profileState: ProfileState = "ZERO_KNOWLEDGE"
    resumeFile: Optional[ResumeFileInfo] = None
    skills: List[Skill] = []
    interests: List[str] = []
    careerInterest: str = ""
    practicalExperience: str = ""
    experience: List[StudentExperience] = []
    projects: List[StudentProject] = []
    certifications: List[StudentCertification] = []
    preferences: StudentPreferences = Field(default_factory=StudentPreferences)
    assessmentSignals: Optional[AssessmentSignals] = None
    profileCompleteness: int = 0
    careerReadiness: int = 0
    academicLevel: str = ""

class MinimalOnboardingRequest(BaseModel):
    name: Optional[str] = None
    education: str
    degree: Optional[str] = None
    field: Optional[str] = None
    academicLevel: Optional[str] = None
    skills: List[str] = []
    interests: List[str] = []
    careerDirection: str = "I'm not sure yet"
    practicalExperienceText: Optional[str] = "I haven't worked on anything yet"
