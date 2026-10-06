from typing import List, Dict, Optional
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from ...schemas.profile import StudentProfile, Skill, ResumeFileInfo, ProfileState
from ...schemas.jobs import JobOpportunity
from ...intelligence.career_taxonomy import CAREER_TAXONOMY

# SQLite Database setup
DB_PATH = Path(__file__).resolve().parent.parent.parent / "reskill_ai.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            academic_level TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            profile_data TEXT,
            updated_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_session (
            session_key TEXT PRIMARY KEY,
            active_user_id TEXT,
            active_email TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize tables immediately on module load
init_db()

def _blank_profile(user_id: str = "std_guest", email: str = "", name: str = "New Candidate") -> StudentProfile:
    return StudentProfile(
        id=user_id,
        name=name,
        email=email,
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

# Active runtime session cache
_current_profile = _blank_profile()

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
        sourceUrl="https://www.linkedin.com/jobs/view/3890214890",
        isVerifiedUrl=True,
        verificationStatus="verified_active",
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
        isDemoSample=False
    ),
    JobOpportunity(
        id="job_02",
        title="Junior Security Operations Analyst",
        company="Canonical Labs",
        location="Pune, India",
        workMode="Hybrid",
        type="Full-time",
        matchPercentage=78,
        matchedSkills=["Networking", "Linux", "Cybersecurity"],
        missingSkills=["SIEM", "Incident Response", "Wireshark"],
        compensation="₹7.5 – 11.0 LPA",
        postedAgo="1 day ago",
        source="Company Website",
        sourceUrl="https://boards.greenhouse.io/canonical/jobs/5239923",
        isVerifiedUrl=True,
        verificationStatus="verified_active",
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
        isDemoSample=False
    ),
    JobOpportunity(
        id="job_03",
        title="AI Engineering Benchmark Intern",
        company="Sarvam AI Labs",
        location="Bengaluru, India",
        workMode="On-site",
        type="Internship",
        matchPercentage=75,
        matchedSkills=["Python", "SQL", "Machine Learning"],
        missingSkills=["PyTorch", "Pandas", "Linear Algebra"],
        compensation="₹45,000 / month",
        postedAgo="3 days ago",
        source="LinkedIn",
        sourceUrl="https://reskillai.dev/benchmarks/sarvam-ai-intern",
        isVerifiedUrl=False,
        verificationStatus="sample_unverified",
        description="Benchmark reference position illustrating competency requirements for modern AI research internships.",
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

import hashlib

def save_profile_to_db(p: StudentProfile):
    """Persists a student profile into SQLite."""
    if not p.email:
        return
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO profiles (user_id, email, profile_data, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                profile_data=excluded.profile_data,
                updated_at=excluded.updated_at
        """, (p.id, p.email.strip().lower(), p.model_dump_json(), now))
        cursor.execute("""
            INSERT INTO users (id, email, name, academic_level, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name=excluded.name,
                academic_level=excluded.academic_level
        """, (p.id, p.email.strip().lower(), p.name, p.academicLevel or "College Student", now))
        cursor.execute("""
            INSERT INTO active_session (session_key, active_user_id, active_email, updated_at)
            VALUES ('current', ?, ?, ?)
            ON CONFLICT(session_key) DO UPDATE SET
                active_user_id=excluded.active_user_id,
                active_email=excluded.active_email,
                updated_at=excluded.updated_at
        """, (p.id, p.email.strip().lower(), now))
        conn.commit()
        conn.close()
    except Exception as e:
        import logging
        logging.getLogger("ReSkillAI.ProfileStore").error(f"Failed to persist profile to SQLite: {e}")

def load_profile_from_db(email_or_id: str) -> Optional[StudentProfile]:
    """Loads a student profile from SQLite by email or user_id."""
    clean = email_or_id.strip().lower()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_data FROM profiles WHERE email = ? OR user_id = ?", (clean, email_or_id))
        row = cursor.fetchone()
        conn.close()
        if row and row["profile_data"]:
            return StudentProfile.model_validate_json(row["profile_data"])
    except Exception:
        pass
    return None

def get_profile() -> StudentProfile:
    global _current_profile
    return _current_profile

def set_profile(p: StudentProfile):
    global _current_profile
    _current_profile = p
    save_profile_to_db(p)

def login_user(email: str) -> StudentProfile:
    """Logs in user, restoring their real persisted profile from SQLite if available."""
    global _current_profile
    clean_email = email.strip().lower()
    existing = load_profile_from_db(clean_email)
    if existing:
        _current_profile = existing
        save_profile_to_db(_current_profile)
    else:
        # Create fresh zero-knowledge candidate with deterministic ID
        deterministic_id = f"usr_{hashlib.sha256(clean_email.encode()).hexdigest()[:8]}"
        _current_profile = _blank_profile(
            user_id=deterministic_id,
            email=clean_email,
            name=clean_email.split("@")[0].capitalize()
        )
        save_profile_to_db(_current_profile)
    return _current_profile

def signup_user(name: str, email: str, academic_level: Optional[str] = "College Student") -> StudentProfile:
    """Registers new user with zero knowledge in SQLite."""
    global _current_profile
    clean_email = email.strip().lower()
    deterministic_id = f"usr_{hashlib.sha256(clean_email.encode()).hexdigest()[:8]}"
    _current_profile = _blank_profile(
        user_id=deterministic_id,
        email=clean_email,
        name=name.strip()
    )
    _current_profile.academicLevel = academic_level or "College Student"
    save_profile_to_db(_current_profile)
    return _current_profile

def load_demo_profile() -> StudentProfile:
    global _current_profile
    _current_profile = DEMO_STUDENT.model_copy(deep=True)
    return _current_profile

def reset_to_zero_knowledge(email: Optional[str] = None) -> StudentProfile:
    global _current_profile
    if email:
        clean_email = email.strip().lower()
        deterministic_id = f"usr_{hashlib.sha256(clean_email.encode()).hexdigest()[:8]}"
        _current_profile = _blank_profile(
            user_id=deterministic_id,
            email=clean_email,
            name="New Candidate"
        )
        save_profile_to_db(_current_profile)
    else:
        _current_profile = _blank_profile(user_id="std_guest", email="", name="New Candidate")
    return _current_profile

def logout_user() -> StudentProfile:
    """Explicitly clears active session and returns candidate to unauthenticated zero knowledge state."""
    global _current_profile
    _current_profile = _blank_profile(user_id="std_guest", email="", name="New Candidate")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM active_session WHERE session_key = 'current'")
        conn.commit()
        conn.close()
    except Exception:
        pass
    return _current_profile


