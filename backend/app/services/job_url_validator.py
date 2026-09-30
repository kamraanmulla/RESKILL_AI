import re
from typing import Tuple, Optional
from urllib.parse import urlparse

def validate_job_source_url(url: Optional[str]) -> Tuple[bool, str]:
    """Validates whether a job application URL is a specific, valid, verifiable external link.
    Rejects:
    - Missing or empty URLs
    - Non-HTTP/HTTPS URLs
    - Placeholder Workday URLs (e.g. community.workday.com/invalid-url or tenant roots without job ID)
    - Generic careers homepages (e.g. /careers, /jobs without specific requisition)
    - Search engine URLs
    - Fake/broken LinkedIn slugs without numeric ID
    """
    if not url or not url.strip():
        return False, "missing_source_url"

    clean_url = url.strip()

    try:
        parsed = urlparse(clean_url)
    except Exception:
        return False, "malformed_url"

    if parsed.scheme not in ["http", "https"]:
        return False, "invalid_protocol"

    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()

    # 1. Reject Workday invalid-url / placeholder redirects
    if "community.workday.com" in hostname or "invalid-url" in path:
        return False, "placeholder_workday_url"

    # 2. Reject Workday tenant root / generic portal without specific job requisition
    if "myworkdayjobs.com" in hostname:
        # A valid workday job posting must have a specific job route, e.g. /job/... or /en-us/job/...
        if "/job/" not in path and not re.search(r"/(r\d+|jr\d+|\d+)", path):
            return False, "placeholder_workday_url"

    # 3. Reject generic search engine URLs
    if any(engine in hostname for engine in ["google.", "bing.", "yahoo.", "duckduckgo."]):
        if "/search" in path or "q=" in (parsed.query or ""):
            return False, "generic_search_url"

    # 4. Reject LinkedIn generic homepages or broken textual slugs
    if "linkedin.com" in hostname:
        # Bare linkedin homepage or bare /jobs
        if path in ["", "/", "/jobs", "/jobs/"]:
            return False, "generic_careers_url"
        # /jobs/view/ must be followed by a numeric ID
        if "/jobs/view/" in path:
            slug = path.split("/jobs/view/")[-1].strip("/")
            # If slug doesn't start with digits, it's a broken non-existent slug
            if not re.match(r"^\d+", slug):
                return False, "invalid_linkedin_slug"

    # 5. Reject generic company careers landing pages without specific job IDs
    generic_career_paths = ["/careers", "/careers/", "/jobs", "/jobs/"]
    if path in generic_career_paths and not parsed.query and not parsed.fragment:
        return False, "generic_careers_url"

    return True, "valid_application_url"
