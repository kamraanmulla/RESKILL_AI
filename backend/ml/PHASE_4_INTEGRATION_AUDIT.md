# ReSkillAI Phase 4: Real User Evidence Integration Audit

## Executive Summary
This audit inspects all active data structures, persistence layers, and intelligence components across ReSkillAI to establish a verified mapping of **Real User Evidence Sources** to the Phase 3 ML evidence pipeline.

---

## 1. Where Resume Evidence Comes From
- **Ingestion Path:** `POST /api/resume/analyze` (`RESKILL_AI/backend/app/api/routes/resume.py`).
- **Processing Layer:** `ResumeService.extract_text_from_bytes()` extracts raw text from PDF/DOCX/TXT bytes using `fitz` (PyMuPDF), `pdfplumber`, or zipfile XML. `GeminiService.parse_resume_text()` performs deterministic semantic parsing.
- **Persistence Location:** 
  - `profile.resumeFile`: Stores `ResumeFileInfo` (`name`, `size`, `uploadedAt`).
  - `profile.skills`: Ingested skills with `detectedFrom="Resume Ingestion"`.
  - `profile.experience`: Extracted professional employment blocks.
  - `profile.projects`: Extracted portfolio projects.
  - Persisted in SQLite (`profiles` table in `reskill_ai.db`).
- **Evidence Characteristics:**
  - `resume_mentioned`: 1 if skill name or canonical synonyms match extracted resume content or skills list.
  - `resume_frequency`: Count of occurrences.
  - `in_experience_section`: Presence in parsed employment descriptions.
  - `in_project_section`: Presence in parsed project descriptions.
  - `has_action_verb_context`: Co-occurrence with implementation verbs.

---

## 2. Where Assessment Evidence Comes From
- **Storage Layer:** `AssessmentSessionStore` (`RESKILL_AI/backend/app/services/assessment_session_store.py`) and `profile.assessmentSignals` (`RESKILL_AI/backend/app/schemas/profile.py`).
- **Session Telemetry:**
  - `sess.answers`: Dict of `question_id -> option_id`.
  - `sess.confidences`: Dict of `question_id -> ConfidenceLevel` (`confident`, `somewhat_confident`, `guessing`).
  - `sess.isComplete`: Completion state.
  - `demonstratedKnowledge`: Domain knowledge percentage scores (0–100) per domain (e.g. `{"cybersecurity": 85, "software_engineering": 75}`).
  - `skillsDemonstrated`: Specific skills validated during question selection (e.g. `["Threat Modeling", "SQL Injection Prevention", "React State Management"]`).
  - `confidenceSignal`: Aggregate confidence rating per domain.
- **Evidence Characteristics:**
  - `assessment_attempted`: Boolean flag.
  - `assessment_score`: Specific domain score corresponding to the skill's taxonomy.
  - `assessment_confidence`: Student's explicit confidence rating on related items.

---

## 3. Where Project Evidence Comes From
- **Storage Layer:** `profile.projects` (List of `StudentProject` in SQLite `profiles` table).
- **Structure:**
  - `title`: Name of project (e.g., "E-Commerce Microservices", "CampusTrade").
  - `tech`: List of technology tags (e.g., `["React", "Node.js", "MongoDB"]`).
  - `description`: Text describing implementation and outcomes.
  - `link`: Optional GitHub/live URL.
- **Evidence Characteristics:**
  - `project_evidence_count`: Number of projects explicitly utilizing or mentioning the skill.
  - `project_match`: Boolean flag if skill exists in `project.tech` or `project.description`.

---

## 4. Where Practical Evidence Comes From
- **Storage Layer:** `sess.practicalScores` and `profile.assessmentSignals.practicalScores`.
- **Structure:**
  - The adaptive assessment system includes real-world scenario challenges (`PRACTICAL_CHALLENGES` evaluated via `evaluate_practical_challenge`).
  - For students who have completed the practical phase, scores are stored under `practicalScores` (e.g. `{"cybersecurity": 85}`).
- **Status When Absent:**
  - If a student has not completed the practical challenge phase, practical evidence is marked **`NOT_AVAILABLE`** (or `ABSENT`).
  - **Zero fake practical scores are invented.**

---

## 5. Where Education Evidence Comes From
- **Storage Layer:** `profile.degree`, `profile.field`, `profile.institution`, `profile.graduationYear`.
- **Evidence Characteristics:**
  - Degree field context (e.g., Computer Science, Information Technology, Accounting).
  - Provides institutional background context without falsely treating a degree as 100% individual skill proof.

---

## 6. Where Experience Evidence Comes From
- **Storage Layer:** `profile.experience` (List of `StudentExperience` in SQLite `profiles` table) and `profile.practicalExperience` (free-text summary).
- **Structure:**
  - `title`: Role title (e.g., "Frontend Developer Intern").
  - `company`: Organization name.
  - `period`: Duration of tenure.
  - `description`: Responsibilities and technical duties.
- **Evidence Characteristics:**
  - Matches skill mentions within professional role descriptions.

---

## 7. How the Authenticated User is Identified
- **Session Identification:**
  - `GET /api/auth/me`: Returns active session user (`id`, `name`, `email`, `academicLevel`).
  - `active_session` table in SQLite (`session_key = 'current'`) tracks active authenticated user.
  - `get_profile()` resolves the active candidate profile.
- **Security Rule:**
  - All intelligence requests MUST resolve the user from the authenticated session context.
  - Direct query parameters (e.g. `?user_id=attacker`) must NEVER allow bypassing session boundaries.

---

## 8. Which Data is Persistent
| Data Entity | Persistence Mechanism | Persistence State |
| :--- | :--- | :---: |
| User Account & Credentials | SQLite `users` table | **PERSISTENT** |
| Profile Dossier (Skills, Bio, Target Career) | SQLite `profiles` table (`profile_data` JSON) | **PERSISTENT** |
| Projects & Work History | SQLite `profiles` table (`profile.projects`, `profile.experience`) | **PERSISTENT** |
| Assessment Signals | SQLite `profiles` table (`profile.assessmentSignals`) | **PERSISTENT** |
| Active Assessment Session Queue | In-memory `AssessmentSessionStore` (ephemeral across restarts) | **SEMI-PERSISTENT** (Signals persisted to profile upon phase completion) |

---

## 9. Which Data is Currently Unavailable
1. **Live Code Sandbox AST Analysis:** ReSkillAI does not currently run a live sandbox compiler inside the backend.
2. **Third-Party External LMS Integration:** External platform certifications (Coursera, Udemy) are currently ingested as self-reported text, not live OAuth API verified.
3. **Supervisor Post-Hiring Evaluations:** Industrial supervisor feedback does not exist in the platform.

These sources are designated as **`NOT_AVAILABLE`** and are strictly excluded from evidence calculations rather than penalizing the user with zero scores.

---

## 10. Existing APIs That Can Be Reused
- `get_profile()` / `load_profile_from_db()`: Retrieves persistent student portfolio.
- `assessment_session_store.get_session(user_id)`: Retrieves active assessment telemetry.
- `predict_skill_evidence.py`: Phase 3 ML inference interface.

---

## 11. New API / Service Required
- **New Service:** `SkillEvidenceService` (`backend/app/services/skill_evidence_service.py`).
  - Aggregates real user evidence across profile, resume, assessment, and projects.
  - Normalizes evidence states: `PRESENT`, `ABSENT`, `NOT_AVAILABLE`.
  - Invokes Phase 3 ML model for probabilistic evidence support estimation.
  - Computes conservative multi-source confidence and provides human-readable explanations.
- **New Authenticated API Route:**
  - `GET /api/intelligence/skill-evidence`: Returns complete skill evidence profile for authenticated user.
  - `GET /api/intelligence/skill-evidence/{skill_name}`: Returns targeted evidence for a single skill.

---

## 12. Data-Model Limitations
- Free-text resume strings are parsed into structured items (`skills`, `projects`, `experience`); storing raw text on `profile.bio` or dynamically reconstructing the text context ensures Phase 3 ML feature extractors receive full context.
- Zero-knowledge profiles have empty skill lists and empty assessment signals. The service must cleanly return `INSUFFICIENT_EVIDENCE` with zero hallucinations.

---

## Audit Verdict: PROCEED TO IMPLEMENTATION
The existing system has robust, cleanly isolated storage for resume, assessment, project, and experience evidence. The integration layer will bridge these real evidence sources to Phase 3 ML inference without touching the deterministic intelligence engines.
