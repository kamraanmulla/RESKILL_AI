from fastapi import APIRouter, HTTPException
from typing import List
from ...schemas.jobs import JobOpportunity
from ...services.job_url_validator import validate_job_source_url
from .profile_store import SAMPLE_JOBS, get_profile

router = APIRouter(prefix="/jobs", tags=["Jobs & Opportunities"])

@router.get("", response_model=List[JobOpportunity])
def list_jobs():
    profile = get_profile()
    user_skill_names = [s.name.lower() for s in profile.skills]

    # Calculate dynamic match per job based on user's real skills
    updated_jobs = []
    for j in SAMPLE_JOBS:
        matched = []
        missing = []
        for req in (j.matchedSkills + j.missingSkills):
            if any(us in req.lower() or req.lower() in us for us in user_skill_names):
                matched.append(req)
            else:
                missing.append(req)

        # In zero knowledge, match is 0
        if len(user_skill_names) == 0:
            match_pct = 0
        else:
            total_reqs = len(matched) + len(missing)
            match_pct = int(round((len(matched) / total_reqs) * 100.0)) if total_reqs > 0 else 50

        # Validate URL dynamically to ensure integrity
        is_valid_url, reason = validate_job_source_url(j.sourceUrl)
        verified_flag = j.isVerifiedUrl and is_valid_url
        status = "verified_active" if verified_flag else ("sample_unverified" if j.isDemoSample else "invalid_url")

        updated_jobs.append(
            j.model_copy(
                update={
                    "matchedSkills": matched if len(user_skill_names) > 0 else [],
                    "missingSkills": missing if len(user_skill_names) > 0 else (j.matchedSkills + j.missingSkills),
                    "matchPercentage": match_pct,
                    "isDemoSample": j.isDemoSample,
                    "isVerifiedUrl": verified_flag,
                    "verificationStatus": status
                }
            )
        )

    return updated_jobs

@router.get("/{job_id}", response_model=JobOpportunity)
def get_job_detail(job_id: str):
    job = next((j for j in SAMPLE_JOBS if j.id == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job opportunity not found.")
    return job

@router.post("/{job_id}/apply-clicked")
def track_apply_click(job_id: str):
    """Logs external application redirect without fake internal submission."""
    job = next((j for j in SAMPLE_JOBS if j.id == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    is_valid, reason = validate_job_source_url(job.sourceUrl)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Job application URL is invalid ({reason}). Redirect blocked."
        )

    if job.isDemoSample or not job.isVerifiedUrl:
        return {
            "status": "sample_benchmark_notice",
            "jobId": job_id,
            "isDemoSample": True,
            "message": "This is an illustrative benchmark position. External application is disabled."
        }

    job.applyClicked = True
    return {
        "status": "redirect_logged",
        "jobId": job_id,
        "source": job.source,
        "sourceUrl": job.sourceUrl,
        "isVerifiedUrl": True,
        "message": f"Redirecting candidate to verified external job posting on {job.source} ({job.sourceUrl})"
    }

