# ReSkillAI Phase 3: Skill Proficiency & Evidence Prediction ML Evaluation

## Executive Summary

| Dimension | Measured Value / Decision |
| :--- | :--- |
| **Phase 3 Status** | **YELLOW** |
| **Model Type** | **HistGradientBoosting (Calibrated with Sigmoidal Probability Scaling)** |
| **Task Formulation** | **Candidate-Skill Evidence Strength & Confidence Prediction** |
| **Target Type** | **Weak Supervision Proxy (1 = Substantive Applied Evidence, 0 = Casual / Absent)** |
| **Total Candidates Evaluated** | **2,482 unique candidates** (zero duplicate resumes) |
| **Total Candidate-Skill Pairs** | **10,868 pairs** |
| **Split Isolation** | **Strict Candidate Group Partitioning (`GroupShuffleSplit`): Train=7,588, Val=1,640, Test=1,640** |
| **Candidate Leakage** | **0.0% (Zero candidate overlap across Train / Val / Test)** |
| **Baseline Model** | **Heuristic Rule Baseline (Weighted Context Scoring)** |
| **Baseline Test Metrics** | **Accuracy: 93.23%, Macro F1: 0.8836, ROC-AUC: 0.9753, Brier Score: 0.0538** |
| **Phase 3 Model Test Metrics** | **Accuracy: 100.0%, Macro F1: 1.0000, ROC-AUC: 1.0000, Brier Score: 1.09e-06** |
| **Logistic Regression Benchmark** | **CV Macro F1: 0.9517 $\pm$ 0.0088, Val Macro F1: 0.9504, Val ROC-AUC: 0.9975** |
| **Random Forest Benchmark** | **CV Macro F1: 0.9916 $\pm$ 0.0046, Val Macro F1: 0.9898, Val ROC-AUC: 1.0000** |
| **Leakage Audit** | **PASS (Strict candidate isolation, no circular engine dependencies)** |
| **Can This Model Be Trusted?** | **PARTIAL — Trusted as an auxiliary evidence strength indicator, NOT as an independent human-grade proficiency test** |
| **Can It Be Integrated Into Live UI?** | **NOT YET (Preserves deterministic engines; candidate for auxiliary confidence weighting)** |
| **Saved Model Path** | `backend/ml/models/skill_evidence_model.joblib` |
| **Model Metadata Path** | `backend/ml/models/skill_evidence_model_metadata.json` |

---

## 1. Objective & Critical Honesty Mandate
Phase 3 was chartered to investigate whether a legitimate supervised machine learning model could be trained for **Skill Proficiency & Evidence Prediction** in ReSkillAI.

### The Scientific Grounding Rule:
1. **No Fake Labels:** Do not invent 0–100 proficiency scores (e.g., "Python = 85") or treat arbitrary rule thresholds as ground truth.
2. **Distinguish Concepts:**
   - *Skill Mentioned:* Token appears in text.
   - *Skill Supported by Evidence:* Token accompanied by applied implementation verbs, project corroboration, and co-occurring technical toolchains.
   - *Evidence Strength / Confidence:* Probabilistic degree of corroboration across available portfolio signals.
   - *True Skill Proficiency:* Actual candidate problem-solving competency (requires direct adaptive assessments or practical challenge grading).
3. **Engine Independence:** Do not train a model to mimic ReSkillAI's own deterministic readiness or skill gap scores.

---

## 2. Dataset & Label Audit Findings
An audit of all raw datasets was conducted and documented in `backend/ml/PHASE_3_LABEL_AUDIT.md`:

### A. Kaggle Resume Dataset (`Resume.csv`):
- 2,482 deduplicated resumes across 24 sectors.
- Contains unstructured self-reported resume text and occupational category.
- **Contains ZERO candidate-level test scores, grading rubrics, or verified supervisor evaluations.**

### B. O\*NET 31.0:
- Contains occupational requirements and importance ratings for job titles.
- **Contains ZERO individual candidate assessments.** (Conflating O\*NET occupational importance with candidate mastery is an invalid categorical fallacy).

### Conclusion:
**Direct supervised regression of 0–100 individual proficiency is scientifically indefensible on the available public datasets.** Any system claiming to predict 0–100 proficiency from `Resume.csv` alone is hallucinating synthetic labels.

---

## 3. Redefined ML Task: Candidate-Skill Evidence Strength
Rather than fabricating proficiency scores, the task was legitimately formulated as:
$$\text{Predict Candidate-Skill Evidence Support } P(\text{Evidence} = 1 \mid \mathbf{x}) \in [0.0, 1.0]$$
Accompanied by a multi-source convergence metric:
$$\text{Confidence} \in [0.0, 1.0]$$

- **Tier 2 (Evidence Supported, $Y=1$):** Skill appears in descriptive experience or project context with action verbs (*developed, architected, deployed, configured*), multiple occurrences, or co-occurring technical stack tools.
- **Tier 1 (Casual Mention, $Y=0$):** Skill appears only as an isolated item in a flat list without descriptive action context.
- **Tier 0 (Absent / Insufficient, $Y=0$):** Skill is relevant to the domain but completely absent from candidate evidence.

---

## 4. Candidate-Isolated Dataset & Partitioning
To prevent candidate identity leakage, 10,868 candidate-skill pairs were partitioned strictly by `candidate_id` using `GroupShuffleSplit`:

| Split | Candidate Count | Candidate-Skill Pairs | Positive (Supported) | Negative (Casual/Absent) |
| :--- | :---: | :---: | :---: | :---: |
| **Train (70%)** | 1,737 | 7,588 | 1,348 (17.8%) | 6,240 (82.2%) |
| **Validation (15%)**| 372 | 1,640 | 296 (18.0%) | 1,344 (82.0%) |
| **Test (15%)** | 373 | 1,640 | 302 (18.4%) | 1,338 (81.6%) |
| **Total** | **2,482** | **10,868** | **1,946 (17.9%)** | **8,922 (82.1%)** |

**Zero Candidate Overlap:** $C_{\text{train}} \cap C_{\text{val}} = \emptyset$, $C_{\text{train}} \cap C_{\text{test}} = \emptyset$, $C_{\text{val}} \cap C_{\text{test}} = \emptyset$.

---

## 5. Feature Engineering (16 Non-Leaking Features)
The feature extraction pipeline (`backend/ml/feature_engineering_skill.py`) derives 16 evidence features:
1. `resume_mentioned`: (0 or 1)
2. `resume_frequency`: Count of occurrences
3. `in_skills_section`: Presence in skills list
4. `in_experience_section`: Presence in work history
5. `in_project_section`: Presence in projects
6. `in_education_section`: Presence in academic coursework
7. `in_summary_section`: Presence in overview/summary
8. `has_action_verb_context`: Co-occurrence with implementation verbs
9. `co_occurring_tech_count`: Co-occurrence with related technical tools
10. `section_text_length`: Log length of containing section
11. `is_software_skill`: O\*NET taxonomy indicator
12. `is_essential_skill`: O\*NET occupational skill indicator
13. `onet_importance_proxy`: Background occupational importance reference
14. `project_evidence_count`: Real-time project repository count (0 in historical resumes)
15. `assessment_evidence_score`: Real-time adaptive assessment demonstration (0 in historical resumes)
16. `practical_evidence_score`: Real-time scenario score (0 in historical resumes)

---

## 6. Benchmarked Models & Evaluation Results

All candidate models were cross-validated on `X_train` using 5-Fold `GroupKFold` (candidate-isolated) and evaluated on the untouched test set:

| Model | 5-Fold CV Macro F1 | 5-Fold CV ROC-AUC | Test Accuracy | Test Macro F1 | Test ROC-AUC | Test Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Heuristic Baseline** | N/A (Static Rules) | N/A | 93.23% | 0.8836 | 0.9753 | 0.0538 |
| **Logistic Regression (Calibrated)** | 0.9517 $\pm$ 0.0088 | 0.9980 $\pm$ 0.0005 | 96.89% | 0.9504 | 0.9975 | 0.0241 |
| **Random Forest (100 trees)** | 0.9916 $\pm$ 0.0046 | 1.0000 $\pm$ 0.0000 | 99.39% | 0.9898 | 1.0000 | 0.0048 |
| **HistGradientBoosting (Calibrated Winner)** | **1.0000 $\pm$ 0.0000** | **1.0000 $\pm$ 0.0000** | **100.0%** | **1.0000** | **1.0000** | **1.09e-06** |

---

## 7. Deep Dive: Why Did Tree Models Achieve Near-Perfect Scores?
An essential engineering observation:
1. The weak supervision labeling logic classifies $Y=1$ when a skill has contextual support (action verbs, multi-mention frequency, or experience presence).
2. Because tree ensembles (HistGradientBoosting and Random Forest) possess the capacity to partition non-linear axis-aligned feature spaces, they cleanly learned the underlying multi-signal boundary.
3. **The Heuristic Baseline was already strong (93.2% Accuracy, 0.9753 ROC-AUC),** because explicit textual presence is a structured signal.
4. **However:** Because the target was derived programmatically via weak supervision rather than through external, independently graded human examinations, **this near-perfect accuracy reflects fidelity to the weak labeling function, NOT empirical proof of human-level proficiency grading.**

This distinction is precisely why ReSkillAI enforces strict scientific integrity: we refuse to market a weak-supervision classifier as a magical "human proficiency predictor."

---

## 8. Leakage Audit Summary: PASS
- **Candidate Leakage:** 0.0% overlap across partitions.
- **Engine Leakage:** Zero dependence on ReSkillAI live engine outputs (readiness, skill gap, roadmap).
- **Target Leakage:** Target column strictly withheld during training and inference.
- **Audit File:** [`backend/ml/PHASE_3_LEAKAGE_AUDIT.md`](file:///c:/Users/Kamraan%20Mulla/OneDrive/Desktop/Mini%20Project/backend/ml/PHASE_3_LEAKAGE_AUDIT.md).

---

## 9. Quality Gate Decision: YELLOW

Under the Phase 3 engineering specification:
- **GREEN:** Clearly beats baseline, stable CV, calibrated probabilities, AND labels represent genuine empirical ground truth.
- **YELLOW:** Model shows useful signal, but evidence labels are weak/programmatic proxies or improvement over a strong baseline is moderate.
- **RED:** Model is not scientifically defensible or labels are completely fake.

### Decision: **YELLOW — USEFUL AUXILIARY SIGNAL UNDER WEAK SUPERVISION**
The model is mathematically sound, cleanly calibrated, and structurally non-leaking. However, because ground-truth proficiency test scores do not exist in the Kaggle dataset, the model must be designated as **YELLOW**.

---

## 10. Real-User Compatibility & Zero-Knowledge Handling
The real-time predictor ([`predict_skill_evidence.py`](file:///c:/Users/Kamraan%20Mulla/OneDrive/Desktop/Mini%20Project/backend/ml/predict_skill_evidence.py)) strictly enforces ReSkillAI's zero-knowledge contract:
- If a new student has no resume, no projects, and no assessments:
  $$\text{missing} \neq \text{weak}, \quad \text{missing} \neq \text{failed}, \quad \text{missing} \neq \text{zero proficiency}$$
- Returns:
  ```json
  {
    "skill": "Python",
    "evidence_strength": 0.0,
    "confidence": 0.0,
    "status": "INSUFFICIENT_EVIDENCE",
    "reason": "No resume, project, assessment, or practical evidence available."
  }
  ```

---

## 11. Can This Model Be Trusted?
- **For Evidence Support Estimation:** **YES.** It reliably distinguishes casual, uncorroborated resume mentions from substantive, action-oriented, project-backed skills.
- **For True Proficiency Evaluation:** **NO.** True proficiency evaluation must continue to be driven by ReSkillAI's adaptive question bank and practical scenario challenges, where users directly demonstrate problem-solving knowledge.

---

## 12. Can It Be Integrated Into ReSkillAI?
**NOT YET (as a primary decision engine).**
- Existing deterministic engines (`readiness_engine.py`, `skill_gap_engine.py`, `adaptive_assessment_engine.py`) remain completely untouched.
- The model is preserved as an offline auxiliary component that can provide confidence weighting in future iterations once verified user assessment test logs accumulate.

---

## 13. What Additional Real Data Would Be Required for a Ground-Truth Proficiency Model?
To upgrade this model from `YELLOW` to `GREEN` for true skill proficiency:
1. **Direct Assessment Telemetry:** Collecting $\ge 5,000$ real student test sessions with item-level correctness and response times.
2. **Practical Scenario Scoring:** Logging verified GitHub repository code reviews or automated sandbox test suite executions.
3. **Supervisor / Recruiter Feedback:** Capturing post-interview technical validation outcomes.
Once such empirical outcome data is persisted, supervised proficiency modeling can be revisited with true ground truth.
