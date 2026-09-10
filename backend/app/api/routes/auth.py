from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .profile_store import get_profile, set_profile, load_demo_profile, reset_to_zero_knowledge
from ...schemas.profile import StudentProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

class SignupRequest(BaseModel):
    name: str
    email: str
    academicLevel: Optional[str] = "College Student"
    password: Optional[str] = None

class AuthResponse(BaseModel):
    user: dict
    profile: StudentProfile
    message: str

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    email = req.email.strip().lower()
    # Demo profile only loaded for explicit demo accounts or /api/auth/demo
    if email in ["parvez.ahmed@apex.edu.in", "demo@reskill.ai"]:
        profile = load_demo_profile()
        user = {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "isDemo": True
        }
        return AuthResponse(
            user=user,
            profile=profile,
            message="Logged in as Demo Student (Parvez Ahmed)"
        )

    # Regular login starts in clean ZERO_KNOWLEDGE state
    reset_to_zero_knowledge()
    profile = get_profile()
    profile.email = req.email
    profile.name = req.email.split("@")[0].capitalize()
    set_profile(profile)

    user = {
        "id": f"usr_{abs(hash(req.email)) % 100000}",
        "name": profile.name,
        "email": profile.email,
        "isDemo": False
    }
    return AuthResponse(
        user=user,
        profile=profile,
        message="Logged in with fresh Zero-Knowledge candidate profile"
    )

@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest):
    reset_to_zero_knowledge()
    profile = get_profile()
    profile.name = req.name.strip()
    profile.email = req.email.strip()
    profile.profileState = "ZERO_KNOWLEDGE"
    set_profile(profile)

    user = {
        "id": f"usr_{abs(hash(req.email)) % 100000}",
        "name": profile.name,
        "email": profile.email,
        "academicLevel": req.academicLevel,
        "isDemo": False
    }
    return AuthResponse(
        user=user,
        profile=profile,
        message="Candidate account registered. Starting in Zero-Knowledge state."
    )

@router.post("/demo", response_model=StudentProfile)
def activate_demo():
    """Explicit endpoint to load sample student (Parvez Ahmed)."""
    return load_demo_profile()

@router.post("/reset", response_model=StudentProfile)
def reset_profile():
    """Explicit endpoint to return candidate dossier to pristine ZERO_KNOWLEDGE slate."""
    return reset_to_zero_knowledge()
