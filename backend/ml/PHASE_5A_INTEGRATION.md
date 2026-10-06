# ReSkillAI — Phase 5A: Evidence-Aware Skill Gap Integration Report

## 1. Objective

Phase 5A delivers the first intelligence integration of Phase 5: connecting the completed Phase 4 Real-User Skill Evidence service (`skill_evidence_service.py`) and Phase 3 ML Evidence Model (`skill_evidence_model.joblib`) into ReSkillAI's deterministic **Skill Gap Engine** (`skill_gap_engine.py`).

**Core Invariants Maintained:**
- **Deterministic Supremacy:** Target career skill requirements, user skill levels, benchmark gaps, primary priorities (`Gap`, `Developing`, `Strong`), and statuses (`Not Started`, `In Progress`, `Mastered`) are 100% preserved.
- **Evidence Support vs. Human Proficiency:** ML predicts evidence strength (artifact support), never ground-truth human skill proficiency.
- **Strict User Isolation & Zero Knowledge:** Zero-knowledge candidates receive `INSUFFICIENT_EVIDENCE` without fake proficiency or synthetic data.
- **Scope Discipline:** Career Match, Readiness, Roadmap, and UI redesign are strictly untouched in Phase 5A.

---

## 2. Existing Skill Gap Architecture (Baseline)

Prior to Phase 5A, the Skill Gap Engine evaluated candidates strictly via self-reported or basic keyword-extracted skills:

1. **Target Career Resolution:** Retrieved the career role from `CAREER_TAXONOMY` (e.g. `career_fullstack`).
2. **Benchmark Standards:** Required 80% competency for core skills, 65% for secondary skills.
3. **Point Gap Calculation:** `gap = max(0, required_level - student_level)`.
4. **Status Assignment:**
   - $student\_level \ge required\_level \implies$ `Strong` / `Mastered`
   - $student\_level > 0 \implies$ `Developing` / `In Progress`
   - $student\_level == 0 \implies$ `Gap` / `Not Started`
5. **Deterministic Sorting:** Gaps first (descending by gap), Developing second, Mastered last.

**Baseline Limitation:** A manual entry of "Python: 80%" or a single resume mention produced identical results to a candidate with documented production experience, completed projects, and verified assessment performance.

---

## 3. Integration Architecture

In Phase 5A, the Skill Gap engine enriches every required career skill with verified evidence context without modifying the deterministic status formula:

```text
                               Authenticated Real Candidate Session
                                                │
                                                ▼
                                    SkillGapEngine.calculate_skill_gaps
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
     Deterministic Gap Evaluator                                Phase 4 Skill Evidence Service
     - Target Career Core & Secondary Skills                     - Profile, Resume, Projects, Assessment
     - yourLevel (0 - 100)                                       - In-memory feature vector construction
     - requiredLevel (80 core / 65 secondary)                    - Phase 3 Calibrated ML Classifier
     - gap: max(0, requiredLevel - yourLevel)                    - Multi-source convergence confidence
     - status: Mastered | In Progress | Not Started              - Transparent source attribution
     - priority: Strong | Developing | Gap                                     │
                 │                                                             ▼
                 │                                               - evidence_strength (0.0 - 1.0)
                 │                                               - evidence_confidence (0.0 - 0.95)
                 │                                               - evidence_status (SUPPORTED, etc.)
                 │                                               - evidence_sources (resume, project, ...)
                 │                                               - evidence_explanation (Rationale)
                 │                                               - evidence_level (STRONG, MODERATE, ...)
                 └──────────────────────────────┬──────────────────────────────┘
                                                ▼
                                  Enriched SkillGapItem (API Output)
                                    GET /api/skill-gap
```

---

## 4. Evidence Sources & Extraction

Every target skill is evaluated across 6 empirical sources through `skill_evidence_service.py`:
1. **Resume:** Parsed skill entities, occurrences in bio, experience, and project sections.
2. **Projects:** Documented project titles, technology lists, and descriptions.
3. **Assessment:** Demonstrated skills, adaptive question domain mastery, and preference scores.
4. **Practical Challenges:** Interactive scenario challenge score submissions.
5. **Professional Experience:** Real work history roles, titles, and company summaries.
6. **Education:** Academic degree context (providing background without asserting standalone skill proficiency).

---

## 5. Evidence Interpretation & Categorical Levels

The evidence signal is categorized into standardized tiers:
- **`STRONG`** (`evidence_status: "SUPPORTED"`): Evidence strength $\ge 0.70$ with $\ge 2$ converging empirical sources.
- **`MODERATE`** (`evidence_status: "MODERATE_EVIDENCE"`): Evidence strength $\ge 0.40$ or supported by a solid independent source.
- **`WEAK`** (`evidence_status: "WEAK_EVIDENCE"`): Low evidence strength $< 0.40$ or isolated mention without depth.
- **`INSUFFICIENT`** (`evidence_status: "INSUFFICIENT_EVIDENCE"` or `"UNSUPPORTED"`): Zero user artifacts submitted or skill absent across all sources.

---

## 6. Exact Fields Added

The following additive fields were integrated into `SkillGapItem` (`backend/app/schemas/intelligence.py` and `src/types/index.ts`):

```python
class SkillGapItem(BaseModel):
    # Preserved deterministic fields
    skill: str
    category: str
    yourLevel: int
    requiredLevel: int
    gap: int
    priority: Literal["Strong", "Developing", "Gap"]
    status: Literal["Mastered", "In Progress", "Not Started"]
    recommendation: str

    # Additive Phase 5A Evidence fields
    evidence_strength: Optional[float] = None
    evidence_confidence: float = 0.0
    evidence_status: str = "NOT_AVAILABLE"
    evidence_sources: List[str] = []
    evidence_explanation: Optional[str] = None
    evidence_level: str = "INSUFFICIENT"
```

---

## 7. Scoring & Decision Logic

- **Deterministic Primacy:** Deterministic `yourLevel`, `gap`, `priority`, and `status` are calculated using the exact same formulas as before.
- **Supporting Context Rule:** If a candidate is `In Progress` with a 5% gap, strong evidence produces `evidence_level: "STRONG"` and `evidence_status: "SUPPORTED"`, but does **not** force `status = "Mastered"` until the candidate genuinely satisfies the requirement benchmark.
- **Sorting Rule:** Items remain sorted by `priority_order` (`Gap` $\rightarrow$ `Developing` $\rightarrow$ `Strong`), secondary sorted by descending `gap`.

---

## 8. Zero-Knowledge Behavior

When an unpopulated candidate profile is evaluated:
- All required skills report deterministic `yourLevel = 0`, `status = "Not Started"`, `priority = "Gap"`.
- Evidence fields strictly return:
  - `evidence_strength = null`
  - `evidence_confidence = 0.0`
  - `evidence_status = "INSUFFICIENT_EVIDENCE"`
  - `evidence_sources = []`
  - `evidence_level = "INSUFFICIENT"`
  - `evidence_explanation = "No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence."`
- **Zero fake skills, zero synthetic scores, and zero demo student data.**

---

## 9. Data Leakage & Security Audit

- **Career Match Leakage:** PASS. Skill Gap does not consume career match percentages or recommendation objects.
- **Readiness Leakage:** PASS. Readiness engine is downstream and isolated; Skill Gap does not read readiness scores.
- **Roadmap Leakage:** PASS. Roadmap is generated downstream from Skill Gap; Skill Gap does not read roadmap steps.
- **Target Feedback Leakage:** PASS. Phase 3 ML model input features are derived strictly from raw candidate artifacts, never circular Skill Gap status.
- **Multi-Tenant State Isolation:** PASS. Candidate data is extracted strictly from the active session profile. Query parameter overrides (`?user_id=attacker`) are completely ignored.

---

## 10. User Isolation Verification

Verified with isolated test fixtures:
- **User Alpha** (Python / FastAPI / React):
  - React Skill Gap: `yourLevel > 0`, `evidence_status: "SUPPORTED"` / `"MODERATE_EVIDENCE"`, `evidence_sources: ["resume", "experience"]`.
  - Java Skill Gap: `evidence_status: "UNSUPPORTED"`, `evidence_level: "INSUFFICIENT"`.
- **User Beta** (Java / Spring Boot / MySQL):
  - React Skill Gap: `yourLevel = 0`, `evidence_status: "UNSUPPORTED"`, `evidence_level: "INSUFFICIENT"`.
  - Java Skill Gap: `evidence_status: "SUPPORTED"` / `"MODERATE_EVIDENCE"`.
- **Cross-User Leakage:** Exactly $0.0\%$.

---

## 11. Before & After Integration Examples

### Example 1: Zero-Knowledge User (Skill: React)
```json
// BEFORE Phase 5A:
{
  "skill": "React",
  "category": "Frontend",
  "yourLevel": 0,
  "requiredLevel": 80,
  "gap": 80,
  "priority": "Gap",
  "status": "Not Started",
  "recommendation": "Essential entry-level requirement for Full Stack Developer. Prioritize via structured roadmap modules."
}

// AFTER Phase 5A:
{
  "skill": "React",
  "category": "Frontend",
  "yourLevel": 0,
  "requiredLevel": 80,
  "gap": 80,
  "priority": "Gap",
  "status": "Not Started",
  "recommendation": "Essential entry-level requirement for Full Stack Developer. Prioritize via structured roadmap modules.",
  "evidence_strength": null,
  "evidence_confidence": 0.0,
  "evidence_status": "INSUFFICIENT_EVIDENCE",
  "evidence_sources": [],
  "evidence_explanation": "No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence.",
  "evidence_level": "INSUFFICIENT"
}
```

### Example 2: Candidate with Multi-Source Portfolio (Skill: SQL, Target: Backend Developer)
```json
// BEFORE Phase 5A:
{
  "skill": "SQL",
  "category": "Database",
  "yourLevel": 75,
  "requiredLevel": 80,
  "gap": 5,
  "priority": "Developing",
  "status": "In Progress",
  "recommendation": "Active exposure detected (75%). Deepen practical project exercises to close remaining 5% gap."
}

// AFTER Phase 5A:
{
  "skill": "SQL",
  "category": "Database",
  "yourLevel": 75,
  "requiredLevel": 80,
  "gap": 5,
  "priority": "Developing",
  "status": "In Progress",
  "recommendation": "Active exposure detected (75%). Deepen practical project exercises to close remaining 5% gap.",
  "evidence_strength": 0.82,
  "evidence_confidence": 0.85,
  "evidence_status": "SUPPORTED",
  "evidence_sources": ["resume", "experience", "project", "assessment"],
  "evidence_explanation": "SQL evidence is supported: documented in profile/resume (3 mention(s)); applied in 1 project(s): Data Pipeline Service; demonstrated in assessment (70% software_engineering performance); applied in professional experience (Backend Intern at CloudCorp).",
  "evidence_level": "STRONG"
}
```

---

## 12. Verification & Test Results

### Dedicated Phase 5A Test Suite (`test_phase_5a_skill_gap_integration.py`):
- `test_phase_5a_zero_knowledge_skill_gap`: **PASS**
- `test_phase_5a_real_user_resume_enrichment`: **PASS**
- `test_phase_5a_multiple_sources_convergence`: **PASS**
- `test_phase_5a_not_available_preservation`: **PASS**
- `test_phase_5a_absent_source_handling`: **PASS**
- `test_phase_5a_multi_user_isolation`: **PASS**
- `test_phase_5a_target_career_differentiation`: **PASS**
- `test_phase_5a_deterministic_regression`: **PASS**
- **Result:** **8 passed, 0 failed**

### Full Backend Pytest Suite:
- `test_adaptive_assessment.py`: 11 passed
- `test_advanced_intelligence.py`: 7 passed
- `test_api.py`: 7 passed
- `test_dual_real_users.py`: 1 passed
- `test_engines.py`: 5 passed
- `test_final_specification.py`: 8 passed
- `test_jobs_url_pipeline.py`: 12 passed
- `test_phase_4_evidence_integration.py`: 7 passed
- `test_phase_5a_skill_gap_integration.py`: 8 passed
- `test_real_user_flow_isolated.py`: 8 passed
- `test_skill_evidence_ml.py`: 10 passed
- **Total Backend Pytest:** **84 passed, 0 failed** (100% pass)

### Frontend Production TypeScript & Bundle Build:
- Command: `npm run build` (`tsc -b && vite build`)
- Output: 1883 modules transformed, 0 errors, bundle generated in 1.56s.

---

## 13. Known Limitations

1. **Weak Supervision Baseline:** The underlying Phase 3 model was trained using weak supervision rules on Kaggle resume pairs and estimates evidence support strength rather than verified human proficiency.
2. **Career Requirement Thresholds:** Benchmarks are fixed at 80% for core skills and 65% for secondary skills per career taxonomy definitions.
3. **Assessment Scope:** Domain mastery reflects answers submitted in the adaptive discovery/assessment questions; skills not covered in the assessment bank rely on resume and project artifacts.

---

## 14. Recommendation for Phase 5B (Career Match Integration)

1. **Keep Deterministic Matching Intact:** Career matching should continue to use required core/secondary skill alignments and user preferences as its primary score.
2. **Use Evidence Strength as Corroboration Signal:** Phase 4 evidence should enrich matching cards with an *Evidence Corroboration Index* rather than overwriting core match formulas.
3. **Preserve User Isolation:** Continue enforcing strict authenticated session profile scoping.
