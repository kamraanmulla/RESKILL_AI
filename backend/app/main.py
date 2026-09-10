"""
ReSkillAI - Career Intelligence Platform Backend
Main FastAPI Application Entrypoint
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import (
    health,
    auth,
    resume,
    profile,
    assessment,
    careers,
    skill_gap,
    roadmap,
    learning,
    progress,
    jobs,
    intelligence,
    coach,
)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Deterministic Career Intelligence & Skill Navigation API for ReSkillAI",
)

# Enable CORS for frontend clients
# Note: allow_origins cannot contain '*' when allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router with /api prefix
api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(resume.router)
api_router.include_router(profile.router)
api_router.include_router(assessment.router)
api_router.include_router(careers.router)
api_router.include_router(skill_gap.router)
api_router.include_router(roadmap.router)
api_router.include_router(learning.router)
api_router.include_router(progress.router)
api_router.include_router(jobs.router)
api_router.include_router(intelligence.router)
api_router.include_router(coach.router)

# Mount /api
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "service": "ReSkillAI Backend",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "api_prefix": "/api",
    }
