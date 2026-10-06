# ReSkillAI — Phase 5A: Evidence-Aware Skill Gap Integration Audit

## 1. Executive Summary

Phase 5A connects the completed Phase 4 Real-User Skill Evidence service (`skill_evidence_service.py`) and Phase 3 ML Evidence Model (`skill_evidence_model.joblib`) to ReSkillAI's deterministic **Skill Gap Engine** (`skill_gap_engine.py`).

**Core Integrity Invariants:**
1. **Preserve Determinism:** The existing deterministic logic for identifying target career skill requirements, calculating student levels, computing point gaps, and assigning primary priorities (`Gap`, `Developing`, `Strong`) and statuses (`Not Started`, `In Progress`, `Mastered`) remains 100% intact.
2. **ML is Evidence Support, NOT Proficiency:** The ML model predicts *evidence strength* (whether user artifacts substantiate a skill claim), NOT true human capability. It does not replace the requirement thresholds or override deterministic gap calculations.
3. **No Fake Data / Real User Isolation:** Real users in zero-knowledge states receive `INSUFFICIENT_EVIDENCE` with `null` evidence strength and `0.0` confidence. Missing sources remain `NOT_AVAILABLE` (never converted to $0$ or failure).
4. **No Premature Scope Expansion:** Career Match, Readiness, Roadmap, and UI redesign are strictly excluded from Phase 5A.

---

## 2. Current Skill Gap Architecture & Scoring Baseline

### 2.1 File Locations & Consumers
- **Implementation File:** `backend/app/intelligence/skill_gap_engine.py`
- **Schema File:** `backend/app/schemas/intelligence.py` (`SkillGapItem`)
- **API Endpoint:** `GET /api/skill-gap` (`backend/app/api/routes/skill_gap.py`)
- **Internal Callers:**
  - `careers.py`: Enriches career match cards with target skill gaps.
  - `roadmap_engine.py`: Uses identified gaps to generate tailored roadmap milestones.
  - `coach.py`: Supplies skill gap context to AI career coaching discussions.
  - `progress.py`: Evaluates overall milestone progression.
  - `learning.py`: Directs learning resource recommendations to active gaps.
- **Frontend Consumer:**
  - `src/services/api.ts`: `api.getSkillGap()`
  - Rendered in: `SkillGapPage.tsx`, `DashboardPage.tsx`

### 2.2 Current Scoring Logic
```python
# 1. Target Career Resolution:
cid = target_career_id or profile.targetCareerId or "career_fullstack"
target_career = get_career_by_id(cid)

# 2. Required Skills & Benchmarks:
# Core skills benchmark: 80%
# Secondary skills benchmark: 65%
all_req_skills = [(s, 80, True) for s in target_career.coreSkills] + \
                 [(s, 65, False) for s in target_career.secondarySkills]

# 3. Student Level Lookup:
found = next((s for s in user_skills if s.name.lower() == skill_name.lower() or ...), None)
student_level = found.proficiency if found else 0
gap = max(0, required_level - student_level)

# 4. Status & Priority Assignment:
if gap == 0 or student_level >= required_level:
    priority = "Strong"
    status = "Mastered"
elif student_level > 0:
    priority = "Developing"
    status = "In Progress"
else:
    priority = "Gap"
    status = "Not Started"

# 5. Sorting:
# Gaps first (largest gap descending), then Developing, then Strong
priority_order = {"Gap": 0, "Developing": 1, "Strong": 2}
items.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.gap))
```

### 2.3 Current Limitations
1. **Unsubstantiated Self-Claims:** A user entering "Python = 85%" manually or from a basic keyword hit on a resume is marked as `Mastered`, even if no projects, experience, or assessment evidence exist.
2. **Missing Evidence Context:** A candidate who has completed a rigorous Python assessment and built a full Python backend project looks identical in the skill gap report to a candidate who merely typed "Python" into their skills list.
3. **Binary Zero State:** A candidate with 0 skills has all skills marked `Not Started` with zero contextual distinction between *skills they have never touched* and *skills where evidence is simply missing/unsubmitted*.

---

## 3. Evidence Integration Point

The evidence layer will integrate directly inside `SkillGapEngine.calculate_skill_gaps`:

```text
Target Career Requirement (e.g. Python, Req: 80%)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
Deterministic Metric             Phase 4 Evidence Service
(yourLevel: 75, gap: 5)          (evaluate_skill_evidence)
status: In Progress                      │
priority: Developing                     ▼
                                 - evidence_strength: 0.84
                                 - evidence_confidence: 0.85
                                 - evidence_status: SUPPORTED
                                 - evidence_sources: [resume, project, assessment]
                                 - evidence_level: STRONG
                                 - evidence_explanation: "..."
       │                                 │
       └────────────────┬────────────────┘
                        ▼
               Enriched SkillGapItem
```

---

## 4. Schema Additions & Backward Compatibility

### 4.1 Additional Fields on `SkillGapItem`
To guarantee 100% backward compatibility for all existing API consumers, existing fields remain untouched and new evidence fields are added with optional/safe defaults:

```python
class SkillGapItem(BaseModel):
    # --- EXISTING PRESERVED FIELDS ---
    skill: str
    category: str
    yourLevel: int # 0 - 100
    requiredLevel: int # 0 - 100
    gap: int # max(0, requiredLevel - yourLevel)
    priority: Literal["Strong", "Developing", "Gap"]
    status: Literal["Mastered", "In Progress", "Not Started"]
    recommendation: str

    # --- NEW PHASE 5A EVIDENCE FIELDS (ADDITIVE) ---
    evidence_strength: Optional[float] = None
    evidence_confidence: float = 0.0
    evidence_status: str = "NOT_AVAILABLE" # SUPPORTED, MODERATE_EVIDENCE, WEAK_EVIDENCE, UNSUPPORTED, INSUFFICIENT_EVIDENCE
    evidence_sources: List[str] = []
    evidence_explanation: Optional[str] = None
    evidence_level: str = "INSUFFICIENT" # STRONG, MODERATE, WEAK, INSUFFICIENT
```

### 4.2 Standardized Categorical Mapping for `evidence_level`
- `SUPPORTED` (strength $\ge 0.70$ and $\ge 2$ converging sources) $\rightarrow$ `STRONG`
- `MODERATE_EVIDENCE` (strength $\ge 0.40$ or strong single source) $\rightarrow$ `MODERATE`
- `WEAK_EVIDENCE` (isolated mention or strength $< 0.40$) $\rightarrow$ `WEAK`
- `INSUFFICIENT_EVIDENCE` / `UNSUPPORTED` $\rightarrow$ `INSUFFICIENT`

### 4.3 Backward Compatibility Plan
- Existing fields (`yourLevel`, `requiredLevel`, `gap`, `priority`, `status`, `recommendation`) remain identical in type, range, and behavior.
- Frontend consumers and internal services reading `item.status` or `item.gap` will continue to function without any modifications.
- API response contract remains `List[SkillGapItem]`.
- Existing tests in `test_engines.py` and other test suites will pass without regression.

---

## 5. Evidence States & Integrity Invariants

1. **`PRESENT`**: Evidence exists in the user's uploaded artifacts (resume, project list, assessment answers, practical score) and corroborates the target skill.
2. **`ABSENT`**: The artifact source was evaluated (e.g. user took the assessment), but did not corroborate this skill.
3. **`NOT_AVAILABLE`**: The source has not been completed by the user.
4. **Invariant 1:** `NOT_AVAILABLE` is never converted to a 0 score or negative proficiency.
5. **Invariant 2:** `ABSENT` does not mean the user has zero ability; it means evidence has not been submitted or demonstrated in that source.
6. **Invariant 3:** Evidence strength never overrides the target career requirements or deterministic gap thresholds.
7. **Invariant 4:** If a user has `status: "In Progress"`, strong evidence confirms the progress (`evidence_level: STRONG`) but does NOT force `status: "Mastered"` if the student's proficiency remains below the requirement.

---

## 6. Zero-Knowledge Guarantees

When a newly registered candidate has no resume, no assessment, no projects, and no skills:
- Every required skill retains deterministic `yourLevel = 0`, `requiredLevel = 80` (or `65`), `gap = 80` (or `65`), `priority = "Gap"`, `status = "Not Started"`.
- Evidence attributes:
  - `evidence_strength`: `None`
  - `evidence_confidence`: `0.0`
  - `evidence_status`: `"INSUFFICIENT_EVIDENCE"`
  - `evidence_sources`: `[]`
  - `evidence_level`: `"INSUFFICIENT"`
  - `evidence_explanation`: `"No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence."`
- Zero fake skills or placeholder scores are injected.

---

## 7. Data Leakage & Security Audit

| Potential Leakage Vector | Risk Analysis | Prevention Invariant |
| :--- | :--- | :--- |
| **Career Match Output** | Could Skill Gap borrow match scores? | **Prohibited:** Skill Gap does NOT read career match percentages or recommendation objects. |
| **Readiness Engine** | Could Skill Gap use readiness points as evidence? | **Prohibited:** Readiness calculations are downstream of skills and are NOT read by `SkillGapEngine`. |
| **Roadmap Engine** | Could Skill Gap read completed roadmap steps? | **Prohibited:** Roadmap is downstream of Skill Gap. |
| **Target Feedback** | Could Skill Gap output be fed back into the evidence model? | **Prohibited:** ML model input features are strictly extracted from raw profile artifacts, never from `SkillGapItem`. |
| **Multi-Tenant Leakage** | Could User Alpha's evidence be visible to User Beta? | **Prohibited:** Profile and session are strictly scoped to the active session user; test fixtures are isolated. |
| **Frontend Spoofing** | Could client pass arbitrary `user_id` to override profile? | **Prohibited:** Session user is extracted server-side from `get_profile()`; client query overrides are rejected. |

---

## 8. Before & After Integration Examples

### Scenario A: Zero-Knowledge User (Target: Full-Stack Developer)
- **Skill:** React (Core Skill, Required: 80%)
- **Before Phase 5A:**
  ```json
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
  ```
- **After Phase 5A:**
  ```json
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
    "evidence_level": "INSUFFICIENT",
    "evidence_explanation": "No user evidence is currently available. Upload a resume, add projects, or complete an assessment to establish evidence."
  }
  ```
  *Verdict:* Completely backward-compatible. Truthful zero-evidence transparency added without mutating deterministic gap logic.

### Scenario B: Real Candidate with Multi-Source Evidence (Target: Full-Stack Developer)
- **Skill:** Python (Core Skill, Required: 80%)
- **User Evidence:** Resume with Python experience + Python web project + Software engineering assessment.
- **Before Phase 5A:**
  ```json
  {
    "skill": "Python",
    "category": "Backend",
    "yourLevel": 75,
    "requiredLevel": 80,
    "gap": 5,
    "priority": "Developing",
    "status": "In Progress",
    "recommendation": "Active exposure detected (75%). Deepen practical project exercises to close remaining 5% gap."
  }
  ```
- **After Phase 5A:**
  ```json
  {
    "skill": "Python",
    "category": "Backend",
    "yourLevel": 75,
    "requiredLevel": 80,
    "gap": 5,
    "priority": "Developing",
    "status": "In Progress",
    "recommendation": "Active exposure detected (75%). Deepen practical project exercises to close remaining 5% gap.",
    "evidence_strength": 0.84,
    "evidence_confidence": 0.85,
    "evidence_status": "SUPPORTED",
    "evidence_sources": ["resume", "experience", "project", "assessment"],
    "evidence_level": "STRONG",
    "evidence_explanation": "Python evidence is supported: documented in profile/resume (4 mention(s)); applied in 1 project(s): Task Manager API; demonstrated in assessment (70% software_engineering performance); applied in professional experience (Backend Intern at Organization)."
  }
  ```
  *Verdict:* The candidate's `In Progress` status is transparently supported by multi-source evidence, giving clear proof of real exposure while respecting that the 5% requirement gap still needs to be formally closed.

---

## 9. Comprehensive Test Plan

We will create `backend/tests/test_phase_5a_skill_gap_integration.py` covering:
1. **Test A (Real User Evidence Enrichment):** Verify real evidence enriches Skill Gap items with evidence strength, confidence, and source citations.
2. **Test B (Zero Knowledge User):** Verify unpopulated profile receives `INSUFFICIENT_EVIDENCE`, `null` strength, `0.0` confidence for all target career skills.
3. **Test C (Multi-Source Convergence):** Verify candidate with Resume + Project + Assessment shows multiple converging sources and elevated confidence.
4. **Test D (NOT_AVAILABLE Preservation):** Verify unsubmitted sources remain `NOT_AVAILABLE` without dragging down scores.
5. **Test E (ABSENT Source Handling):** Verify evaluated sources that lack the skill report `ABSENT` without asserting zero ability.
6. **Test F (User Isolation):** User Alpha (Python) and User Beta (Java) see strictly distinct skill gap evidence with zero cross-talk.
7. **Test G (Security & Session Scoping):** Verify client cannot pass query parameters to inspect another user's evidence.
8. **Test H (Target Career Variations):** Verify changing target careers (e.g. `career_cybersecurity` vs `career_fullstack`) dynamically updates required skills while preserving evidence mappings.
9. **Test I (Deterministic Regression):** Verify existing deterministic assertions (priority order, gap formulas, status values) remain 100% identical.
10. **Test J (No Fake Data Leakage):** Verify no sample student (Parvez) data leaks into freshly created candidate accounts.
