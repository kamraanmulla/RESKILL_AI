# ReSkillAI — Phase 4: Real User Evidence Integration Specification & Report

## 1. Architecture Overview

Phase 4 integrates ReSkillAI's Phase 3 ML Skill Evidence Model (`skill_evidence_model.joblib`) with live user evidence sources while strictly preserving existing deterministic intelligence engines (`readiness_engine.py`, `skill_gap_engine.py`, `roadmap_engine.py`, career matching).

```text
                                REAL CANDIDATE (Authenticated Session)
                                                  │
                 ┌─────────────────┬──────────────┴───────────────┬─────────────────┐
                 ▼                 ▼                              ▼                 ▼
             Resume Scan      Assessment                     User Projects     Experience & Degree
         (Parsed Entities) (Signals & Session)           (Tech & Repos)     (History & Field)
                 │                 │                              │                 │
                 └─────────────────┼──────────────────────────────┼─────────────────┘
                                   │
                                   ▼
                Evidence Aggregation & Normalization Engine
                  (skill_evidence_service.py)
                    - PRESENT: Source exists and corroborates skill
                    - ABSENT: Source exists but does not corroborate skill
                    - NOT_AVAILABLE: Source has no user data (missing != failed)
                                   │
                                   ▼
                Feature Alignment Layer (15 Feature Vector)
                                   │
                                   ▼
                 Phase 3 ML Evidence Classifier (UNMODIFIED)
                    - HistGradientBoosting + Isotonic Calibration
                    - Predicts: evidence_strength (0.00 – 1.00)
                    - Never predicts: True human skill proficiency
                                   │
                                   ▼
                Multi-Source Evidence Convergence Engine
                    - Conservative Confidence (0.20 – 0.95)
                    - Status: SUPPORTED | MODERATE_EVIDENCE | WEAK_EVIDENCE | UNSUPPORTED | INSUFFICIENT_EVIDENCE
                    - Human-Readable Source Transparency & Explanations
                                   │
                 ┌─────────────────┴──────────────────────────────┐
                 ▼                                                ▼
     Skill Evidence API Routes                    Existing Deterministic Intelligence Engines
  GET /api/intelligence/skill-evidence                  (Readiness, Gap, Roadmap, Matching)
  GET /api/intelligence/skill-evidence/{skill}          *100% Preserved & Unaltered*
```

---

## 2. End-to-End Data Flow

1. **Authentication Identification:**
   Requests authenticate via session state (`usr_xxxx` or active profile). The endpoint resolves the current active user directly from `get_profile()` and `assessment_session_store.get_session(profile.id)`. Client requests cannot specify or spoof arbitrary user IDs.

2. **Evidence Extraction & State Mapping:**
   For each requested skill (or all profile skills), `skill_evidence_service.py` evaluates 6 real sources:
   - `resume`: Scans resume bio, skill entities, and mentions.
   - `assessment`: Checks adaptive session answers, question banks, domain mastery, and preference signals.
   - `project`: Scans user's documented projects for explicit technology tags and textual descriptions.
   - `practical`: Inspects scenario-based coding challenge results (`practicalScores`).
   - `experience`: Matches work titles, companies, and roles against skill synonyms.
   - `education`: Evaluates degree and field of study context.

3. **Inference with Phase 3 ML Model:**
   The service formats the candidate's real evidence into the exact 15-feature schema expected by `SkillEvidencePredictor` and invokes inference. The calibrated probability is mapped to `evidence_strength`.

4. **Conservative Multi-Source Confidence:**
   Confidence is calculated through multi-source convergence rather than raw model certainty, bounding overconfidence.

5. **Explainability Synthesis:**
   The service builds an itemized explanation citing exact sources (e.g., *"Python evidence is supported: documented in profile/resume (4 mention(s)); demonstrated in assessment (70% software_engineering performance); applied in professional experience (Software Engineer at TechCorp)."*).

---

## 3. Evidence Sources & Evaluation Rules

| Evidence Source | Extraction Method | Real Storage Location | Evaluation Rule |
| :--- | :--- | :--- | :--- |
| **Resume** | Structured extraction via `resume_service.analyze_resume` | `profile.skills`, `profile.resumeFile`, `profile.bio` | `PRESENT` if frequency $\ge 1$ or listed in parsed skills; `ABSENT` if resume uploaded but skill not mentioned; `NOT_AVAILABLE` if no resume. |
| **Assessment** | Adaptive assessment session and submitted assessment signals | `profile.assessmentSignals`, `assessment_session_store` | `PRESENT` if question answered correctly, skill demonstrated, domain mastery $\ge 50\%$, or domain score $\ge 40\%$; `ABSENT` if assessment completed without matching; `NOT_AVAILABLE` if no assessment taken. |
| **Projects** | Candidate project entries | `profile.projects` | `PRESENT` if project technology list contains skill or title/description cites it; `ABSENT` if projects exist but lack skill; `NOT_AVAILABLE` if 0 projects. |
| **Practical** | Scenario challenge submissions | `profile.assessmentSignals.practicalScores`, `sess.practicalScores` | `PRESENT` if real scenario score $> 0$ and domain corroborates; `ABSENT` if challenge completed without passing; `NOT_AVAILABLE` if challenge not attempted. |
| **Experience** | Professional work entries | `profile.experience`, `profile.practicalExperience` | `PRESENT` if role description or title cites skill; `ABSENT` if experience exists without skill; `NOT_AVAILABLE` if no experience entries. |
| **Education** | Academic background | `profile.degree`, `profile.field` | `PRESENT` if CS/IT degree aligns with core tech; `NOT_AVAILABLE` if blank. (Provides context, never proves proficiency alone). |

---

## 4. Handling Unavailable Sources (Strict Evidence Invariant)

A cornerstone principle of ReSkillAI Phase 4 is:
$$\text{Missing Evidence} \ne \text{Negative Evidence} \ne \text{Zero Proficiency}$$

- If an evidence source has not been completed by the user (e.g. no assessment attempted yet), its state is set strictly to `NOT_AVAILABLE`.
- It is **never** coerced to a score of $0$ or marked as a failure.
- In zero-knowledge states (brand new user with no resume, assessment, or projects), the system returns `status: "INSUFFICIENT_EVIDENCE"`, `evidence_strength: null`, and `confidence: 0.0`.
- The system never fabricates practical scores, demo projects, or mock answers to fill missing gaps.

---

## 5. API Contracts

### Endpoint 1: Profile Evidence Overview
`GET /api/intelligence/skill-evidence`

**Response (`200 OK`):**
```json
{
  "userId": "usr_91137",
  "evaluatedCount": 3,
  "skills": [
    {
      "skill": "Python",
      "evidence_strength": 0.84,
      "confidence": 0.78,
      "status": "SUPPORTED",
      "evidence_sources": ["resume", "experience", "assessment"],
      "source_states": {
        "resume": "PRESENT",
        "assessment": "PRESENT",
        "project": "NOT_AVAILABLE",
        "practical": "NOT_AVAILABLE",
        "experience": "PRESENT",
        "education": "NOT_AVAILABLE"
      },
      "explanation": "Python evidence is supported: documented in profile/resume (4 mention(s)); demonstrated in assessment (70% software_engineering performance); applied in professional experience (Software Engineer at TechCorp).",
      "details": {
        "resume_frequency": 4,
        "matching_experience": ["Software Engineer at TechCorp"],
        "domain_score": 70
      }
    }
  ],
  "summary": {
    "supported_count": 1,
    "moderate_count": 0,
    "weak_count": 0,
    "unsupported_count": 0,
    "insufficient_evidence_count": 0
  }
}
```

### Endpoint 2: Single Skill Evidence
`GET /api/intelligence/skill-evidence/{skill_name}`

**Response for Supported Skill (`200 OK`):**
```json
{
  "skill": "Python",
  "evidence_strength": 0.84,
  "confidence": 0.78,
  "status": "SUPPORTED",
  "evidence_sources": ["resume", "experience", "assessment"],
  "source_states": { ... },
  "explanation": "Python evidence is supported: ...",
  "details": { ... }
}
```

**Response for Zero-Knowledge User (`200 OK`):**
```json
{
  "skill": "Python",
  "evidence_strength": null,
  "confidence": 0.0,
  "status": "INSUFFICIENT_EVIDENCE",
  "evidence_sources": [],
  "source_states": {
    "resume": "NOT_AVAILABLE",
    "assessment": "NOT_AVAILABLE",
    "project": "NOT_AVAILABLE",
    "practical": "NOT_AVAILABLE",
    "experience": "NOT_AVAILABLE",
    "education": "NOT_AVAILABLE"
  },
  "explanation": "No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence.",
  "details": { "reason": "ZERO_KNOWLEDGE" }
}
```

---

## 6. Authentication & User Isolation

- **Session Context:** The service consumes the authenticated user session via `profile_store.get_profile()`.
- **Query Parameter Shielding:** Client requests cannot override the user identity via query parameters (e.g. `?user_id=attacker_id` is completely ignored).
- **Multi-Tenant State Isolation:**
  - Tested between candidate **Alpha** (`Python / FastAPI / React`) and candidate **Beta** (`Java / Spring Boot / MySQL`).
  - Candidate Alpha can only see Alpha's evidence. Java evaluates to `UNSUPPORTED`.
  - Candidate Beta can only see Beta's evidence. Python evaluates to `UNSUPPORTED`.
  - Switching sessions strictly restores the authenticated user's isolated profile.

---

## 7. Machine Learning Inference Details

- **Model Artifact:** `backend/ml/models/skill_evidence_model.joblib` (Phase 3 model).
- **Model Architecture:** Scikit-Learn `HistGradientBoostingClassifier` wrapped with `CalibratedClassifierCV(method='isotonic')`.
- **Model Invariant:** The model artifact was **not retrained** and remains completely untouched.
- **Role of Model:** Operates solely as an **evidence support signal**. It predicts the likelihood that the candidate's documentation substantiates the skill, not true human capability.

---

## 8. Confidence Calculation Formula

To prevent artificial certainty ($0.99+$) derived from a single isolated source, ReSkillAI computes confidence through multi-source convergence:

$$\text{Raw Confidence} = \sum_{s \in \text{Active Sources}} w_s$$

Where weights are distributed across independent empirical sources:
- Resume mention/section: $w_{\text{resume}} = 0.30$
- Documented projects: $w_{\text{project}} = 0.30$
- Assessment questions & domain mastery: $w_{\text{assessment}} = 0.25$
- Practical scenario challenge: $w_{\text{practical}} = 0.15$

**Bounds:**
$$\text{Final Confidence} = \text{round}\Big(\min(0.95, \max(0.20, \text{Raw Confidence})), 2\Big)$$

- Single source maximum confidence: $\le 0.30$.
- Two converging sources: $\approx 0.55 - 0.60$.
- Three converging sources: $\approx 0.85$.
- Four converging sources: $\le 0.95$ (strictly preventing misleading $1.00$ or $0.99$).

---

## 9. Known Limitations

1. **Weak Supervision Baseline:** The Phase 3 model was trained using weak supervision rules derived from resume text. While effective as an evidence classifier, it does not have human proficiency gold-standard labels.
2. **Contextual Skill Parsing:** In resumes lacking section headers (e.g., plain inline bullets without "Work Experience" or "Projects"), skill identification defaults to entity presence rather than deep sectional attribution.
3. **Language Scope:** Currently optimized for technical roles and standard English technical resumes and assessments.

---

## 10. Regression & Integration Test Suite Verification

### Backend Pytest Suite:
- `tests/test_phase_4_evidence_integration.py`: **7 passed**
  - `test_zero_knowledge_user_evidence`: PASSED
  - `test_resume_only_user_evidence`: PASSED
  - `test_user_with_resume_and_assessment`: PASSED
  - `test_project_evidence_corroboration`: PASSED
  - `test_unknown_unsupported_skill`: PASSED
  - `test_multi_user_isolation`: PASSED
  - `test_security_session_isolation`: PASSED
- `tests/test_skill_evidence_ml.py`: **10 passed**
- `tests/test_dual_real_users.py`: **1 passed**
- `tests/test_engines.py`: **5 passed**
- `tests/test_real_user_flow_isolated.py`: **8 passed**
- **Full Backend Suite:** **76 passed, 0 failed** (100% clean).

### Frontend Production Build:
- Command: `npm run build` (`tsc -b && vite build`)
- Output: 1883 modules transformed, 0 TypeScript errors, bundle generated in 1.29s.

### Deterministic Engine Integrity:
- `readiness_engine.py`: **UNCHANGED**
- `skill_gap_engine.py`: **UNCHANGED**
- `roadmap_engine.py`: **UNCHANGED**
- Career Matching: **UNCHANGED**
