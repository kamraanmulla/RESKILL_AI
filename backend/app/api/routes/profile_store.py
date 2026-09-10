from typing import List, Dict
from ...schemas.profile import StudentProfile, Skill, ResumeFileInfo, ProfileState
from ...schemas.jobs import JobOpportunity
from ...intelligence.career_taxonomy import CAREER_TAXONOMY

# In-memory session store (Modular, replaceable by MongoDB / database layer in the future)
_current_profile = StudentProfile(
    id="std_guest",
    name="New Candidate",
    email="",
    degree="",
    field="",
    institution="",
    graduationYear=2026,
    targetCareerId="career_fullstack",
    profileState="ZERO_KNOWLEDGE",
    skills=[],
    interests=[],
    careerInterest="",
    practicalExperience=""
)

# Canonical Sample / Demo profile (Parvez Ahmed)
DEMO_STUDENT = StudentProfile(
    id="std_parvez",
    name="Parvez Ahmed",
    email="parvez.ahmed@apex.edu.in",
    phone="+91 98450 21980",
    degree="Bachelor of Technology in Computer Science & Engineering",
    field="Computer Science",
    institution="Apex Institute of Technology",
    graduationYear=2026,
    cgpa=8.7,
    bio="Final-year Computer Science undergraduate passionate about full-stack web architectures, distributed systems, and modern developer tooling.",
    targetCareerId="career_fullstack",
    profileState="PERSONALIZED",
    resumeFile=ResumeFileInfo(
        name="Parvez_Ahmed_Resume_2026.pdf",
        size="248 KB",
        uploadedAt="Yesterday at 4:15 PM"
    ),
    skills=[
        Skill(name="JavaScript", category="Frontend", proficiency=85, level="Proficient", verified=True, detectedFrom="Nexus Labs, Projects"),
        Skill(name="React", category="Frontend", proficiency=80, level="Proficient", verified=True, detectedFrom="Nexus Labs, CampusTrade"),
        Skill(name="HTML/CSS", category="Frontend", proficiency=90, level="Expert", verified=True, detectedFrom="Meta Certificate"),
        Skill(name="TypeScript", category="Frontend", proficiency=65, level="Familiar", verified=True, detectedFrom="VisualPath"),
        Skill(name="Node.js", category="Backend", proficiency=60, level="Familiar", verified=True, detectedFrom="CampusTrade"),
        Skill(name="Express", category="Backend", proficiency=60, level="Familiar", verified=True, detectedFrom="CampusTrade"),
        Skill(name="REST APIs", category="Backend", proficiency=65, level="Familiar", verified=True, detectedFrom="Coursework"),
        Skill(name="MongoDB", category="Database", proficiency=65, level="Familiar", verified=True, detectedFrom="CampusTrade"),
        Skill(name="Git", category="Tools", proficiency=75, level="Proficient", verified=True, detectedFrom="GitHub profile"),
        Skill(name="Docker", category="Tools", proficiency=45, level="Familiar", verified=False, detectedFrom="Self-study")
    ],
    interests=["Software Engineering", "Full Stack", "Distributed Systems"],
    careerInterest="Full Stack Developer",
    practicalExperience="Built a peer-to-peer campus marketplace in React and Node.js with MongoDB persistence. Interned at Nexus Labs developing client dashboards."
)

SAMPLE_JOBS: List[JobOpportunity] = [
    JobOpportunity(
        id="job_01",
        title="Associate Full Stack Software Engineer",
        company="Razorpay NeoBank",
        location="Bengaluru, India",
        workMode="Hybrid",
        type="Full-time",
        matchPercentage=84,
        matchedSkills=["JavaScript", "React", "Node.js", "REST APIs", "Git"],
        missingSkills=["Docker", "Redis"],
        compensation="₹8.5 – 12.0 LPA",
        postedAgo="2 days ago",
        source="LinkedIn",
        sourceUrl="https://www.linkedin.com/jobs/view/associate-software-engineer-razorpay",
        description="Build and scale consumer-facing fintech payment dashboards and real-time ledger settlement web interfaces.",
        responsibilities=[
            "Author modular, type-safe client interfaces in React and TypeScript.",
            "Collaborate with backend engineers to integrate high-volume REST and GraphQL contracts.",
            "Write comprehensive unit test suites using Jest and React Testing Library."
        ],
        qualifications=[
            "B.E. / B.Tech in Computer Science, Information Technology, or equivalent.",
            "Demonstrable fluency in JavaScript, React, and REST API conventions.",
            "Strong grasp of version control (Git) and responsive DOM styling."
        ],
        isDemoSample=True
    ),
    JobOpportunity(
        id="job_02",
        title="Junior Security Operations Analyst",
        company="CrowdStrike India",
        location="Pune, India",
        workMode="Hybrid",
        type="Full-time",
        matchPercentage=78,
        matchedSkills=["Networking", "Linux", "Cybersecurity"],
        missingSkills=["SIEM", "Incident Response", "Wireshark"],
        compensation="₹7.5 – 11.0 LPA",
        postedAgo="1 day ago",
        source="Company Website",
        sourceUrl="https://crowdstrike.wd5.myworkdayjobs.com/crowdstrike_careers",
        description="Monitor enterprise security telemetry, analyze endpoint alert anomalies, and assist in triage of defensive security events.",
        responsibilities=[
            "Monitor tier-1 security operations queues across SIEM and EDR platforms.",
            "Triage suspicious network connections and identify credential abuse patterns.",
            "Document shift incident notes and follow standard containment runbooks."
        ],
        qualifications=[
            "Degree in Computer Science, Cybersecurity, or relevant certifications (Security+, CEH).",
            "Familiarity with TCP/IP network layers and Linux command-line utilities.",
            "Analytical mindset with high attention to diagnostic detail."
        ],
        isDemoSample=True
    ),
    JobOpportunity(
        id="job_03",
        title="AI Engineering Intern",
        company="Sarvam AI",
        location="Bengaluru, India",
        workMode="On-site",
        type="Internship",
        matchPercentage=75,
        matchedSkills=["Python", "SQL", "Machine Learning"],
        missingSkills=["PyTorch", "Pandas", "Linear Algebra"],
        compensation="₹45,000 / month",
        postedAgo="3 days ago",
        source="LinkedIn",
        sourceUrl="https://www.linkedin.com/jobs/view/ai-engineering-intern-sarvam",
        description="Assist research scientists in curating training datasets and benchmarking transformer inference latency.",
        responsibilities=[
            "Prepare clean evaluation benchmarks for multi-modal language models.",
            "Build data preprocessing and tokenization scripts in Python.",
            "Monitor validation loss curves and benchmark inferencing speeds."
        ],
        qualifications=[
            "Graduating in 2026 with coursework in Linear Algebra, Probability, and Machine Learning.",
            "Comfortable with Python scripting and basic tensor operations.",
            "Eager to learn modern transformer architectures and fine-tuning pipelines."
        ],
        isDemoSample=True
    )
]

def get_profile() -> StudentProfile:
    global _current_profile
    return _current_profile

def set_profile(p: StudentProfile):
    global _current_profile
    _current_profile = p

def load_demo_profile() -> StudentProfile:
    global _current_profile
    _current_profile = DEMO_STUDENT.model_copy(deep=True)
    return _current_profile

def reset_to_zero_knowledge() -> StudentProfile:
    global _current_profile
    _current_profile = StudentProfile(
        id="std_guest",
        name="New Candidate",
        email="",
        degree="",
        field="",
        institution="",
        graduationYear=2026,
        targetCareerId="career_fullstack",
        profileState="ZERO_KNOWLEDGE",
        skills=[],
        interests=[],
        careerInterest="",
        practicalExperience=""
    )
    return _current_profile
