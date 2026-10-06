import json
import logging
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple
from ..config import settings
from ..schemas.profile import StudentProfile, Skill, StudentExperience, StudentProject, AssessmentSignals

logger = logging.getLogger(__name__)

# Server-side in-memory prompt cache to prevent redundant Gemini calls and save API quota
_PROMPT_CACHE: Dict[str, Any] = {}

class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.mock_mode = settings.gemini_mock_mode
        self.last_error: Optional[str] = None
        self.last_call_status: str = "untested"
        self._model = None
        self._init_client()

    def _init_client(self):
        if self.mock_mode:
            logger.info("GeminiService initialized in MOCK_MODE (Zero API quota consumed).")
            return

        if self.api_key:
            try:
                import google.generativeai as genai
                # Configure with REST transport for fast and reliable connectivity on all platforms
                genai.configure(api_key=self.api_key, transport="rest")
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                self.last_error = f"Initialization error: {type(e).__name__}: {str(e)}"
                logger.error(f"Could not initialize Google Generative AI client: {self.last_error}")

    def test_gemini_connection(self) -> Dict[str, Any]:
        """Performs a test request to Gemini or returns mock status in mock mode."""
        if self.mock_mode:
            return {
                "configured": bool(self.api_key),
                "model": self.model_name,
                "status": "mock_mode_active",
                "message": "Gemini Mock Mode active for quota protection. Zero live API quota consumed.",
                "response": {"status": "connected", "model": self.model_name}
            }

        if not self.api_key:
            return {
                "configured": False,
                "model": self.model_name,
                "status": "missing_api_key",
                "error": "GEMINI_API_KEY is not set in backend/.env"
            }

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key, transport="rest")
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                'Respond with valid JSON: {"status": "connected", "model": "' + self.model_name + '"}',
                request_options={"timeout": 15}
            )
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            parsed = json.loads(clean_text.strip())
            self.last_call_status = "success"
            self.last_error = None
            return {
                "configured": True,
                "model": self.model_name,
                "status": "success",
                "response": parsed,
                "raw_text": response.text.strip()
            }
        except Exception as e:
            # Capture exact error without exposing API key
            err_msg = f"{type(e).__name__}: {str(e)}"
            if self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "[REDACTED_API_KEY]")
            self.last_error = err_msg
            self.last_call_status = "error"
            logger.error(f"Gemini test request failed: {err_msg}")
            return {
                "configured": True,
                "model": self.model_name,
                "status": "error",
                "error": err_msg
            }

    def parse_resume_text(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured profile data from raw resume text using Gemini.
        Protects quota with MD5 prompt caching and never falls back to demo student data.
        """
        if not resume_text or not resume_text.strip():
            return self._extract_from_text_strictly("")

        cache_key = "resume_" + hashlib.md5(resume_text.strip().encode('utf-8')).hexdigest()
        if cache_key in _PROMPT_CACHE:
            logger.info("Serving resume extraction from local prompt cache (0 API quota).")
            return _PROMPT_CACHE[cache_key]

        if self.mock_mode:
            extracted = self._extract_from_text_strictly(resume_text)
            _PROMPT_CACHE[cache_key] = extracted
            return extracted

        if not self._model and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key, transport="rest")
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini client lazily initialized for resume parser: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to lazy-init Gemini client for resume: {e}")

        if self._model:
            prompt = f"""
You are the resume analysis engine for ReSkillAI.
Extract structured profile details from the following resume text.
Return ONLY valid JSON matching this exact structure:
{{
  "name": "Candidate Full Name or null",
  "email": "Email address or null",
  "degree": "Degree and major (e.g. B.Tech in Computer Science) or null",
  "institution": "University or college name or null",
  "graduationYear": 2026,
  "skills": [
    {{"name": "SkillName", "category": "Frontend|Backend|Database|Tools|Security|AI/ML|Other", "proficiency": 75}}
  ],
  "projects": [
    {{"title": "Project Title", "tech": ["Tech1", "Tech2"], "description": "Short description"}}
  ],
  "experience": [
    {{"title": "Role Title", "company": "Company Name", "period": "Duration", "description": "Short description"}}
  ]
}}

RESUME TEXT:
{resume_text[:4000]}
"""
            try:
                response = self._model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
                    request_options={"timeout": 20}
                )
                if response and response.text:
                    parsed = json.loads(response.text)
                    self.last_error = None
                    self.last_call_status = "success"
                    _PROMPT_CACHE[cache_key] = parsed
                    return parsed
            except Exception as err:
                err_str = f"{type(err).__name__}: {str(err)}"
                if self.api_key and self.api_key in err_str:
                    err_str = err_str.replace(self.api_key, "[REDACTED_API_KEY]")
                self.last_error = err_str
                self.last_call_status = "error"
                logger.error(f"Gemini resume analysis failed: {err_str}")

        # Extract strictly from user's actual text without any demo/mock student data fallback
        fallback_res = self._extract_from_text_strictly(resume_text)
        _PROMPT_CACHE[cache_key] = fallback_res
        return fallback_res

    def interpret_experience_text(self, text: str) -> Tuple[List[Skill], Optional[str]]:
        """Interprets free-text answer to Question 5 of onboarding.
        Protects quota with MD5 prompt caching and never falls back to demo student data.
        """
        if not text or text.strip() == "I haven't worked on anything yet":
            return [], None

        cache_key = "exp_" + hashlib.md5(text.strip().encode('utf-8')).hexdigest()
        if cache_key in _PROMPT_CACHE:
            logger.info("Serving experience interpretation from local prompt cache (0 API quota).")
            return _PROMPT_CACHE[cache_key], None

        if self.mock_mode:
            skills, err = self._extract_skills_from_text_locally(text)
            _PROMPT_CACHE[cache_key] = skills
            return skills, err

        if self._model:
            prompt = f"""
You are the skill extraction intelligence of ReSkillAI.
A student wrote this response about what they have built or learned:
"{text}"

Identify the technical skills, tools, or concepts explicitly demonstrated in their text.
Return ONLY valid JSON:
[
  {{"name": "SkillName", "category": "Frontend|Backend|Database|Tools|Security|AI/ML|Other", "proficiency": 65}}
]
"""
            try:
                response = self._model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
                    request_options={"timeout": 15}
                )
                if response and response.text:
                    clean = response.text.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    if clean.startswith("```"):
                        clean = clean[3:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    parsed = json.loads(clean.strip())
                    if isinstance(parsed, list):
                        self.last_error = None
                        self.last_call_status = "success"
                        skills = [Skill(**s) for s in parsed]
                        _PROMPT_CACHE[cache_key] = skills
                        return skills, None
            except Exception as e:
                err_str = f"{type(e).__name__}: {str(e)}"
                if self.api_key and self.api_key in err_str:
                    err_str = err_str.replace(self.api_key, "[REDACTED_API_KEY]")
                self.last_error = err_str
                self.last_call_status = "error"
                logger.error(f"Gemini experience interpretation error: {err_str}")

        skills, err = self._extract_skills_from_text_locally(text)
        _PROMPT_CACHE[cache_key] = skills
        return skills, self.last_error

    def _extract_skills_from_text_locally(self, text: str) -> Tuple[List[Skill], Optional[str]]:
        """Extracts skills derived strictly from words appearing in the candidate's own text."""
        keywords = {
            "python": ("Python", "Backend", 75),
            "fastapi": ("FastAPI", "Backend", 75),
            "django": ("Django", "Backend", 70),
            "flask": ("Flask", "Backend", 70),
            "java": ("Java", "Backend", 75),
            "spring boot": ("Spring Boot", "Backend", 75),
            "spring": ("Spring Boot", "Backend", 70),
            "c++": ("C++", "Backend", 75),
            "c#": ("C#", "Backend", 70),
            ".net": ("ASP.NET", "Backend", 70),
            "javascript": ("JavaScript", "Frontend", 75),
            "typescript": ("TypeScript", "Frontend", 70),
            "react": ("React", "Frontend", 75),
            "node": ("Node.js", "Backend", 70),
            "express": ("Express", "Backend", 65),
            "html": ("HTML/CSS", "Frontend", 80),
            "css": ("HTML/CSS", "Frontend", 80),
            "tailwind": ("Tailwind CSS", "Frontend", 70),
            "sql": ("SQL", "Database", 70),
            "mysql": ("MySQL", "Database", 70),
            "postgres": ("PostgreSQL", "Database", 70),
            "postgresql": ("PostgreSQL", "Database", 70),
            "mongo": ("MongoDB", "Database", 65),
            "mongodb": ("MongoDB", "Database", 65),
            "redis": ("Redis", "Database", 65),
            "linux": ("Linux", "Tools", 70),
            "git": ("Git", "Tools", 75),
            "docker": ("Docker", "Tools", 65),
            "kubernetes": ("Kubernetes", "Tools", 60),
            "aws": ("Cloud / AWS", "Cloud", 65),
            "azure": ("Azure", "Cloud", 65),
            "gcp": ("Google Cloud", "Cloud", 65),
            "cyber": ("Cybersecurity", "Security", 70),
            "cybersecurity": ("Cybersecurity", "Security", 70),
            "networking": ("Networking", "Security", 65),
            "wireshark": ("Wireshark", "Security", 65),
            "siem": ("SIEM", "Security", 65),
            "machine learning": ("Machine Learning", "AI/ML", 70),
            "ai": ("AI / ML", "AI/ML", 70),
            "pytorch": ("PyTorch", "AI/ML", 65),
            "tensorflow": ("TensorFlow", "AI/ML", 65),
            "pandas": ("Pandas", "AI/ML", 70),
            "rest": ("REST APIs", "Backend", 70),
            "graphql": ("GraphQL", "Backend", 65)
        }
        lower = text.lower()
        found_skills: List[Skill] = []
        seen = set()

        for kw, (name, cat, prof) in keywords.items():
            # Check pattern with word boundary to prevent partial substring false positives
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, lower) and name not in seen:
                seen.add(name)
                found_skills.append(
                    Skill(
                        name=name,
                        category=cat, # type: ignore
                        proficiency=prof,
                        level="Proficient" if prof >= 70 else "Familiar",
                        verified=True,
                        detectedFrom="User-entered practical experience"
                    )
                )

        return found_skills, self.last_error

    def _extract_from_text_strictly(self, text: str) -> Dict[str, Any]:
        """Extracts strictly from user's resume text without any hardcoded demo profile or demo student data."""
        if not text:
            return {
                "name": None,
                "email": None,
                "degree": None,
                "institution": None,
                "graduationYear": 2026,
                "skills": [],
                "projects": [],
                "experience": []
            }

        lower = text.lower()
        skills: List[Dict[str, Any]] = []
        seen_skills = set()

        # Comprehensive technical taxonomy
        catalog = [
            ("Python", "Backend", 80, r'\bpython\b'),
            ("FastAPI", "Backend", 75, r'\bfastapi\b'),
            ("Django", "Backend", 75, r'\bdjango\b'),
            ("Flask", "Backend", 70, r'\bflask\b'),
            ("Java", "Backend", 80, r'\bjava\b(?!\s*script)'),
            ("Spring Boot", "Backend", 75, r'\bspring\s*boot\b|\bspring\s*framework\b'),
            ("C++", "Backend", 75, r'\bc\+\+\b'),
            ("C#", "Backend", 70, r'\bc#\b|\bc\s*sharp\b'),
            ("Go", "Backend", 70, r'\bgolang\b|\bgo\s+language\b'),
            ("Rust", "Backend", 70, r'\brust\b'),
            ("JavaScript", "Frontend", 80, r'\bjavascript\b|\bjs\b'),
            ("TypeScript", "Frontend", 75, r'\btypescript\b|\bts\b'),
            ("React", "Frontend", 80, r'\breact(?:\.js)?\b'),
            ("Next.js", "Frontend", 70, r'\bnext(?:\.js)?\b'),
            ("Node.js", "Backend", 75, r'\bnode(?:\.js)?\b'),
            ("Express", "Backend", 70, r'\bexpress(?:\.js)?\b'),
            ("REST APIs", "Backend", 75, r'\brest\s*api[s]?\b|\brestful\b'),
            ("GraphQL", "Backend", 65, r'\bgraphql\b'),
            ("HTML/CSS", "Frontend", 85, r'\bhtml\b|\bcss\b'),
            ("Tailwind CSS", "Frontend", 75, r'\btailwind\b'),
            ("SQL", "Database", 75, r'\bsql\b'),
            ("MySQL", "Database", 75, r'\bmysql\b'),
            ("PostgreSQL", "Database", 75, r'\bpostgres(?:ql)?\b'),
            ("MongoDB", "Database", 70, r'\bmongo(?:db)?\b'),
            ("Redis", "Database", 65, r'\bredis\b'),
            ("Git", "Tools", 80, r'\bgit\b|\bgithub\b|\bgitlab\b'),
            ("Docker", "Tools", 70, r'\bdocker\b'),
            ("Kubernetes", "Tools", 65, r'\bkubernetes\b|\bk8s\b'),
            ("Linux", "Tools", 75, r'\blinux\b|\bunix\b|\bubuntu\b'),
            ("AWS", "Cloud", 70, r'\baws\b|\bamazon\s*web\s*services\b'),
            ("Azure", "Cloud", 65, r'\bazure\b'),
            ("Google Cloud", "Cloud", 65, r'\bgcp\b|\bgoogle\s*cloud\b'),
            ("Cybersecurity", "Security", 75, r'\bcybersecurity\b|\binformation\s*security\b'),
            ("Networking", "Security", 70, r'\bnetworking\b|\btcp/ip\b|\bdns\b'),
            ("SIEM", "Security", 70, r'\bsiem\b|\bsplunk\b'),
            ("Wireshark", "Security", 65, r'\bwireshark\b'),
            ("Incident Response", "Security", 65, r'\bincident\s*response\b'),
            ("Machine Learning", "AI/ML", 75, r'\bmachine\s*learning\b|\bml\b'),
            ("Deep Learning", "AI/ML", 70, r'\bdeep\s*learning\b'),
            ("PyTorch", "AI/ML", 70, r'\bpytorch\b'),
            ("TensorFlow", "AI/ML", 70, r'\btensorflow\b'),
            ("Pandas", "AI/ML", 75, r'\bpandas\b'),
            ("NumPy", "AI/ML", 75, r'\bnumpy\b'),
            ("Data Analysis", "AI/ML", 75, r'\bdata\s*analysis\b|\bdata\s*analytics\b')
        ]

        for name, cat, prof, pat in catalog:
            if re.search(pat, lower) and name not in seen_skills:
                seen_skills.add(name)
                skills.append({"name": name, "category": cat, "proficiency": prof})

        # Name extraction strictly from first non-empty header line
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        detected_name = None
        for line in lines[:5]:
            clean_l = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            words = clean_l.split()
            if 2 <= len(words) <= 4 and "@" not in line and "http" not in line.lower() and "resume" not in line.lower():
                detected_name = clean_l
                break

        # Email extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        detected_email = email_match.group(0) if email_match else None

        # Degree extraction
        deg_match = re.search(
            r'(B\.?Tech|B\.?E\.?|Bachelor(?:\'s)?(?:\s+of\s+[A-Za-z\s]+)?|M\.?Tech|Master(?:\'s)?(?:\s+of\s+[A-Za-z\s]+)?|BCA|MCA|B\.?Sc|M\.?Sc)(?:(?:\s+in|\s+of|\s*-)?\s*([A-Za-z\s&]{3,40}))?',
            text,
            re.IGNORECASE
        )
        detected_degree = None
        if deg_match:
            base_deg = deg_match.group(1).strip()
            field_spec = deg_match.group(2).strip() if deg_match.group(2) else ""
            detected_degree = f"{base_deg} in {field_spec}".strip() if field_spec else base_deg

        # Institution extraction
        inst_match = re.search(
            r'([A-Za-z0-9\s&,.\'-]+(?:Institute of Technology|University|National Institute|Engineering College|Campus|Academy|College))',
            text,
            re.IGNORECASE
        )
        detected_institution = inst_match.group(1).strip() if inst_match else None

        # Graduation year extraction
        grad_match = re.search(r'\b(20[2-3][0-9])\b', text)
        detected_grad_year = int(grad_match.group(1)) if grad_match else 2026

        # Projects extraction
        projects: List[Dict[str, Any]] = []
        proj_section = re.search(r'(?:projects?|academic projects?|personal projects?)[\s:]*\n([\s\S]*?)(?:\n\s*(?:experience|education|skills|certifications|awards)|\Z)', text, re.IGNORECASE)
        if proj_section:
            p_text = proj_section.group(1).strip()
            p_blocks = [b.strip() for b in re.split(r'\n(?=[A-Z0-9•\-\*])', p_text) if b.strip()]
            for blk in p_blocks[:3]:
                blk_lines = [l.strip().lstrip('•-*0123456789. ') for l in blk.split('\n') if l.strip()]
                if blk_lines:
                    title = blk_lines[0]
                    desc = " ".join(blk_lines[1:]) if len(blk_lines) > 1 else title
                    # Detect tech mentioned in this project
                    p_tech = [s["name"] for s in skills if s["name"].lower() in blk.lower()]
                    projects.append({
                        "title": title[:60],
                        "tech": p_tech[:4],
                        "description": desc[:200]
                    })
        elif "project" in lower:
            # Fallback inline project detection
            proj_lines = [l.strip() for l in lines if "project" in l.lower() or "built" in l.lower() or "developed" in l.lower()]
            for pl in proj_lines[:2]:
                projects.append({
                    "title": pl.lstrip('•-*0123456789. ')[:60],
                    "tech": [s["name"] for s in skills if s["name"].lower() in pl.lower()][:3],
                    "description": pl[:180]
                })

        # Experience extraction
        experience: List[Dict[str, Any]] = []
        exp_section = re.search(r'(?:experience|work experience|employment|internships?)[\s:]*\n([\s\S]*?)(?:\n\s*(?:projects?|education|skills|certifications|awards)|\Z)', text, re.IGNORECASE)
        if exp_section:
            e_text = exp_section.group(1).strip()
            e_blocks = [b.strip() for b in re.split(r'\n(?=[A-Z0-9•\-\*])', e_text) if b.strip()]
            for blk in e_blocks[:2]:
                blk_lines = [l.strip().lstrip('•-*0123456789. ') for l in blk.split('\n') if l.strip()]
                if blk_lines:
                    title = blk_lines[0]
                    desc = " ".join(blk_lines[1:]) if len(blk_lines) > 1 else title
                    experience.append({
                        "title": title[:50],
                        "company": "Organization",
                        "period": "Previous",
                        "description": desc[:200]
                    })
        elif "intern" in lower or "engineer" in lower:
            exp_lines = [l.strip() for l in lines if "intern" in l.lower() or "engineer" in l.lower() or "developer" in l.lower()]
            for el in exp_lines[:2]:
                experience.append({
                    "title": el.lstrip('•-*0123456789. ')[:50],
                    "company": "Organization",
                    "period": "Previous",
                    "description": el[:180]
                })

        return {
            "name": detected_name,
            "email": detected_email,
            "degree": detected_degree,
            "institution": detected_institution,
            "graduationYear": detected_grad_year,
            "skills": skills,
            "projects": projects,
            "experience": experience
        }


    def career_coach_chat(
        self,
        message: str,
        profile: StudentProfile,
        intelligence_context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        force_mock: bool = False
    ) -> Dict[str, Any]:
        """Real Gemini-powered conversational AI Career Coach.

        IMPORTANT: This method ALWAYS calls the real Gemini API for live user
        interactions. The global mock_mode setting is intentionally bypassed here
        so that the AI Career Coach remains genuinely AI-powered.

        The `force_mock` parameter exists ONLY for automated tests that need
        deterministic responses without consuming API quota.

        Error handling covers:
        - Missing API key
        - Gemini API failure / timeout / quota exhaustion
        - Invalid/empty API response
        """
        user_skills = [s.name for s in (profile.skills or [])]
        skill_details = [
            f"{s.name} ({s.category}, {s.proficiency}%, {s.level}, source: {s.detectedFrom or 'unknown'})"
            for s in (profile.skills or [])
        ]
        target_career = profile.targetCareerId or "career_fullstack"
        target_career_readable = target_career.replace("career_", "").replace("_", " ").title()
        readiness = getattr(profile, "careerReadiness", 0) or 0
        ctx = intelligence_context or {}

        # --- MOCK MODE: Only for automated tests ---
        if force_mock:
            skills_str = ", ".join(user_skills) if user_skills else "exploratory stage"
            gaps_str = ", ".join(ctx.get("skillGaps", [])[:3]) if ctx.get("skillGaps") else "core domain requirements"
            hidden_str = ", ".join([h.get("skill", "") for h in ctx.get("hiddenCompetencies", [])[:2]])

            response_text = (
                f"Hello {profile.name or 'Candidate'}! Looking at your current profile, you are positioning for "
                f"{target_career_readable} with current readiness at {readiness}%.\n\n"
                f"Your demonstrated skills include: {skills_str}. "
            )
            if hidden_str:
                response_text += f"Interestingly, your practical evidence also suggests hidden competencies in {hidden_str}.\n\n"
            if gaps_str:
                response_text += f"To accelerate your hiring trajectory, I recommend prioritizing your primary gaps in {gaps_str}. "
            response_text += f"\n\nRegarding your question: \"{message}\" — focus on building project artifacts that validate these skills in real repositories."

            return {
                "response": response_text,
                "source": "gemini_mock_mode",
                "status": "success"
            }

        # --- REAL GEMINI API: Always used for live coach interactions ---

        # Guard: missing API key
        if not self.api_key:
            return {
                "response": "",
                "source": "error",
                "status": "error",
                "error": "GEMINI_API_KEY is not configured. Please set it in backend/.env to enable the AI Career Coach."
            }

        # Ensure Gemini client is initialized (may have been skipped if mock_mode was true at startup)
        if not self._model:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key, transport="rest")
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini client lazily initialized for coach: {self.model_name}")
            except Exception as e:
                err_str = f"{type(e).__name__}: {str(e)}"
                if self.api_key and self.api_key in err_str:
                    err_str = err_str.replace(self.api_key, "[REDACTED_API_KEY]")
                logger.error(f"Failed to initialize Gemini client: {err_str}")
                return {
                    "response": "",
                    "source": "error",
                    "status": "error",
                    "error": f"Failed to initialize Gemini AI: {err_str}"
                }

        # Build conversation history
        history_text = ""
        if history:
            for h in history[-6:]:
                role = h.get("role", "user")
                content = h.get("content", "")
                history_text += f"{role.capitalize()}: {content}\n"

        # Build rich skill gap details
        gaps_list = ctx.get("skillGaps", [])
        gaps_str = ", ".join(gaps_list[:5]) if gaps_list else "No significant gaps identified"

        # Build hidden competency details
        hidden_comps = ctx.get("hiddenCompetencies", [])
        hidden_str = ", ".join([h.get("skill", "") for h in hidden_comps[:3]]) if hidden_comps else "None detected yet"

        # Build contradiction details
        contradictions = ctx.get("contradictions", [])
        contradiction_str = ", ".join([c.get("skill", "") for c in contradictions[:3]]) if contradictions else "None"

        # Build transferability details
        transferability = ctx.get("transferability", {})
        transfer_str = json.dumps(transferability, default=str)[:500] if transferability else "Not yet analyzed"

        # Build project summaries
        projects_str = ""
        if profile.projects:
            for p in profile.projects[:3]:
                projects_str += f"- {p.title}: {p.description} (Tech: {', '.join(p.tech)})\n"
        else:
            projects_str = "No projects listed yet."

        # Build experience summaries
        experience_str = ""
        if profile.experience:
            for exp in profile.experience[:3]:
                experience_str += f"- {exp.title} at {exp.company} ({exp.period}): {exp.description}\n"
        elif profile.practicalExperience:
            experience_str = f"Self-described: {profile.practicalExperience}"
        else:
            experience_str = "No experience listed yet."

        # Build assessment signals
        assessment_str = "Not yet completed."
        if profile.assessmentSignals:
            signals = profile.assessmentSignals
            assessment_str = (
                f"Domain Preferences: {', '.join(signals.domainPreferences)}\n"
                f"Problem Solving Style: {signals.problemSolvingStyle or 'Not assessed'}\n"
                f"Work Style: {', '.join(signals.workStyleSignals)}\n"
                f"Primary Motivation: {signals.primaryMotivation or 'Not assessed'}"
            )

        prompt = f"""You are the personal AI Career Coach for ReSkillAI, an advanced career intelligence platform.
You provide encouraging, technically rigorous, actionable, and honest career navigation advice.
You must reference the candidate's ACTUAL verified data below — never fabricate or assume skills they don't have.
You must directly answer their specific question. Do not give generic advice unrelated to their question.

═══════════════════════════════════════
CANDIDATE CANONICAL DOSSIER
═══════════════════════════════════════

Name: {profile.name or 'Candidate'}
Education: {profile.degree or 'In Progress'} — {profile.field or 'Not specified'} at {profile.institution or 'Institution not specified'}
Graduation Year: {profile.graduationYear}
CGPA: {profile.cgpa if profile.cgpa > 0 else 'Not provided'}

Target Career: {target_career_readable}
Career Readiness Score: {readiness}%
Profile State: {profile.profileState}
Profile Completeness: {profile.profileCompleteness}%

Skills (with proficiency):
{chr(10).join(skill_details) if skill_details else 'No skills registered yet.'}

Projects:
{projects_str}

Experience:
{experience_str}

Career Assessment Signals:
{assessment_str}

═══════════════════════════════════════
INTELLIGENCE ANALYSIS
═══════════════════════════════════════

Top Skill Gaps: {gaps_str}
Hidden Competencies Detected: {hidden_str}
Skills with Evidence Contradictions: {contradiction_str}
Transferability Analysis: {transfer_str}

═══════════════════════════════════════
CONVERSATION HISTORY
═══════════════════════════════════════
{history_text if history_text else 'No prior messages in this session.'}

═══════════════════════════════════════
USER'S CURRENT QUESTION
═══════════════════════════════════════
{message}

═══════════════════════════════════════
RESPONSE INSTRUCTIONS
═══════════════════════════════════════
1. Directly answer the user's specific question using their actual profile data.
2. Reference their real skills, gaps, projects, and target career where relevant.
3. Be encouraging but honest — do not fabricate achievements or skills they lack.
4. Provide concrete, actionable next steps tailored to their situation.
5. If this is a follow-up question, understand the context from the conversation history.
6. Keep responses focused and well-structured (2-4 paragraphs or structured bullet points).
7. Use specific numbers (readiness %, skill proficiency %) from their dossier when relevant.
"""

        try:
            gemini_resp = self._model.generate_content(
                prompt,
                generation_config={"temperature": 0.5, "max_output_tokens": 1000},
                request_options={"timeout": 25}
            )
            if gemini_resp and gemini_resp.text and gemini_resp.text.strip():
                self.last_error = None
                self.last_call_status = "success"
                return {
                    "response": gemini_resp.text.strip(),
                    "source": self.model_name,
                    "status": "success"
                }
            else:
                self.last_error = "Gemini returned an empty response."
                self.last_call_status = "error"
                return {
                    "response": "",
                    "source": "error",
                    "status": "error",
                    "error": "Gemini AI returned an empty response. Please try again."
                }
        except Exception as e:
            err_str = f"{type(e).__name__}: {str(e)}"
            if self.api_key and self.api_key in err_str:
                err_str = err_str.replace(self.api_key, "[REDACTED_API_KEY]")
            self.last_error = err_str
            self.last_call_status = "error"
            logger.error(f"AI Career Coach Gemini request failed: {err_str}")

            # Identify specific error types for user-friendly messages
            err_lower = err_str.lower()
            if "quota" in err_lower or "rate" in err_lower or "429" in err_lower or "resource_exhausted" in err_lower:
                user_error = "Gemini API quota has been reached. Please try again later or check your API plan."
            elif "timeout" in err_lower or "deadline" in err_lower:
                user_error = "Gemini API request timed out. Please try again."
            elif "invalid" in err_lower and "key" in err_lower:
                user_error = "Gemini API key is invalid. Please check your backend/.env configuration."
            elif "permission" in err_lower or "403" in err_lower:
                user_error = "Gemini API access denied. Please verify your API key permissions."
            else:
                user_error = f"Gemini AI service error: {err_str}"

            return {
                "response": "",
                "source": "error",
                "status": "error",
                "error": user_error
            }

gemini_service = GeminiService()

