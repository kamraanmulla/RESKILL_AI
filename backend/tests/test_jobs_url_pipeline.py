import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.job_url_validator import validate_job_source_url
from app.api.routes.profile_store import SAMPLE_JOBS, get_profile, load_demo_profile, reset_to_zero_knowledge

client = TestClient(app)

class TestJobUrlValidationUnit:
    def test_missing_source_url(self):
        is_valid, reason = validate_job_source_url(None)
        assert is_valid is False
        assert reason == "missing_source_url"

        is_valid, reason = validate_job_source_url("")
        assert is_valid is False
        assert reason == "missing_source_url"

        is_valid, reason = validate_job_source_url("   ")
        assert is_valid is False
        assert reason == "missing_source_url"

    def test_invalid_source_url_protocols(self):
        is_valid, reason = validate_job_source_url("javascript:alert(1)")
        assert is_valid is False
        assert reason == "invalid_protocol"

        is_valid, reason = validate_job_source_url("ftp://careers.example.com/job/123")
        assert is_valid is False
        assert reason == "invalid_protocol"

    def test_placeholder_workday_urls(self):
        # Specific Workday community invalid URL redirect
        is_valid, reason = validate_job_source_url("https://community.workday.com/invalid-url")
        assert is_valid is False
        assert reason == "placeholder_workday_url"

        # Workday root tenant without specific job ID
        is_valid, reason = validate_job_source_url("https://crowdstrike.wd5.myworkdayjobs.com/crowdstrike_careers")
        assert is_valid is False
        assert reason == "placeholder_workday_url"

    def test_generic_careers_urls(self):
        # Generic company /careers landing page
        is_valid, reason = validate_job_source_url("https://company.com/careers")
        assert is_valid is False
        assert reason == "generic_careers_url"

        # Generic LinkedIn /jobs
        is_valid, reason = validate_job_source_url("https://www.linkedin.com/jobs")
        assert is_valid is False
        assert reason == "generic_careers_url"

    def test_invalid_linkedin_slug_without_numeric_id(self):
        # Non-numeric slug that LinkedIn 404s
        is_valid, reason = validate_job_source_url("https://www.linkedin.com/jobs/view/associate-software-engineer-razorpay")
        assert is_valid is False
        assert reason == "invalid_linkedin_slug"

    def test_valid_https_application_urls(self):
        # Valid LinkedIn job with numeric requisition ID
        is_valid, reason = validate_job_source_url("https://www.linkedin.com/jobs/view/3890214890")
        assert is_valid is True
        assert reason == "valid_application_url"

        # Valid Greenhouse requisition URL
        is_valid, reason = validate_job_source_url("https://boards.greenhouse.io/canonical/jobs/5239923")
        assert is_valid is True
        assert reason == "valid_application_url"

        # Valid Workday specific requisition URL
        is_valid, reason = validate_job_source_url("https://company.wd1.myworkdayjobs.com/en-US/Careers/job/Remote/Senior-Engineer_R10294")
        assert is_valid is True
        assert reason == "valid_application_url"


class TestJobDatasetIntegrity:
    def test_jobs_have_distinct_urls(self):
        """Ensures that distinct real jobs do not share the same application URL."""
        verified_jobs = [j for j in SAMPLE_JOBS if not j.isDemoSample]
        urls = [j.sourceUrl for j in verified_jobs]
        assert len(urls) == len(set(urls)), "Duplicate source URLs detected among active job listings!"

        # Specifically ensure job_01 and job_02 URLs differ
        job_01 = next(j for j in SAMPLE_JOBS if j.id == "job_01")
        job_02 = next(j for j in SAMPLE_JOBS if j.id == "job_02")
        assert job_01.sourceUrl != job_02.sourceUrl

    def test_sample_vs_verified_job_delineation(self):
        """Ensures sample benchmark jobs are marked isDemoSample=True and isVerifiedUrl=False."""
        sample_jobs = [j for j in SAMPLE_JOBS if j.isDemoSample]
        verified_jobs = [j for j in SAMPLE_JOBS if not j.isDemoSample]

        assert len(sample_jobs) >= 1
        assert len(verified_jobs) >= 1

        for sj in sample_jobs:
            assert sj.isDemoSample is True
            assert sj.isVerifiedUrl is False
            assert sj.verificationStatus == "sample_unverified"

        for vj in verified_jobs:
            assert vj.isDemoSample is False
            assert vj.isVerifiedUrl is True
            assert vj.verificationStatus == "verified_active"
            is_valid, _ = validate_job_source_url(vj.sourceUrl)
            assert is_valid is True


class TestJobsApiEndpoints:
    def test_list_jobs_does_not_mutate_is_demo_sample_with_profile_skills(self):
        """Zero knowledge vs filled profile should not flip isDemoSample of benchmark jobs."""
        # Test in zero knowledge
        reset_to_zero_knowledge()
        res_zero = client.get("/api/jobs")
        assert res_zero.status_code == 200
        jobs_zero = res_zero.json()

        # Test with filled profile
        load_demo_profile()
        res_demo = client.get("/api/jobs")
        assert res_demo.status_code == 200
        jobs_demo = res_demo.json()

        # Benchmark job (job_03) should remain isDemoSample=True in both
        job_03_zero = next(j for j in jobs_zero if j["id"] == "job_03")
        job_03_demo = next(j for j in jobs_demo if j["id"] == "job_03")
        assert job_03_zero["isDemoSample"] is True
        assert job_03_demo["isDemoSample"] is True

        # Verified job (job_01) should remain isDemoSample=False in both
        job_01_zero = next(j for j in jobs_zero if j["id"] == "job_01")
        job_01_demo = next(j for j in jobs_demo if j["id"] == "job_01")
        assert job_01_zero["isDemoSample"] is False
        assert job_01_demo["isDemoSample"] is False
        assert job_01_zero["isVerifiedUrl"] is True
        assert job_01_demo["isVerifiedUrl"] is True

    def test_track_apply_click_verified_job(self):
        res = client.post("/api/jobs/job_01/apply-clicked")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "redirect_logged"
        assert data["jobId"] == "job_01"
        assert data["isVerifiedUrl"] is True
        assert "3890214890" in data["sourceUrl"]

    def test_track_apply_click_sample_benchmark_job(self):
        res = client.post("/api/jobs/job_03/apply-clicked")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "sample_benchmark_notice"
        assert data["isDemoSample"] is True
        assert "disabled" in data["message"].lower()

    def test_track_apply_click_not_found(self):
        res = client.post("/api/jobs/nonexistent_job_xyz/apply-clicked")
        assert res.status_code == 404
