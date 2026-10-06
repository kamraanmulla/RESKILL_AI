from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .profile_store import (
    get_profile,
    set_profile,
    load_demo_profile,
    reset_to_zero_knowledge,
    login_user,
    signup_user,
    logout_user
)
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

    # Regular login restores user profile from SQLite database if existing
    profile = login_user(email)

    user = {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "academicLevel": profile.academicLevel or "College Student",
        "isDemo": False
    }
    return AuthResponse(
        user=user,
        profile=profile,
        message="Logged in successfully (data loaded from database)"
    )

@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest):
    profile = signup_user(
        name=req.name.strip(),
        email=req.email.strip(),
        academic_level=req.academicLevel or "College Student"
    )

    user = {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "academicLevel": req.academicLevel or "College Student",
        "isDemo": False
    }
    return AuthResponse(
        user=user,
        profile=profile,
        message="Candidate account registered in database. Starting in Zero-Knowledge state."
    )


@router.get("/me")
def get_current_user():
    """Returns the currently authenticated user session or indicates unauthenticated."""
    profile = get_profile()
    if not profile or not profile.email or (profile.profileState == "ZERO_KNOWLEDGE" and profile.id == "std_guest"):
        return {"authenticated": False, "user": None, "profile": None}
    user = {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "academicLevel": profile.academicLevel or "College Student",
        "isDemo": profile.id == "std_parvez"
    }
    return {"authenticated": True, "user": user, "profile": profile}

@router.post("/logout")
def logout():
    """Clears the active session and returns candidate to zero knowledge."""
    logout_user()
    return {"message": "Logged out successfully"}

@router.post("/demo", response_model=StudentProfile)
def activate_demo():
    """Explicit endpoint to load sample student (Parvez Ahmed)."""
    return load_demo_profile()

@router.post("/reset", response_model=StudentProfile)
def reset_profile():
    """Explicit endpoint to return candidate dossier to pristine ZERO_KNOWLEDGE slate."""
    return reset_to_zero_knowledge()

