# ReSkillAI Phase 3: Skill Evidence & Proficiency ML Experiment

## Overview
Phase 3 builds the first machine learning component for ReSkillAI's skill intelligence layer:
**Skill Evidence Strength & Confidence Prediction**

### Fundamental Integrity Principle
ReSkillAI does **NOT** invent fake 0–100 candidate skill proficiency labels.
Neither the Kaggle Resume dataset nor O\*NET 31.0 contains individual candidate test scores or graded competencies.
Instead of training a deceptive regression model on synthetic numbers, Phase 3 implements an interpretable, calibrated machine learning model that determines:
1. **Evidence Strength ($[0.0, 1.0]$):** How strongly available multi-source portfolio evidence (action-oriented experience descriptions, verified projects, assessment confirmations, co-occurring toolchains) corroborates a candidate's skill.
2. **Confidence ($[0.0, 1.0]$):** The degree of certainty based on multi-source convergence.

---

## Dataset & Candidate-Skill Pairs
- **Source:** 2,482 unique, deduplicated candidate resumes from `backend/ml/data/raw/kaggle/Resume.csv`.
- **Processed Pairs:** `backend/ml/data/processed/candidate_skill_features.csv`.
- **Candidate Isolation:** Data partitioning is strictly grouped by `candidate_id` (`GroupShuffleSplit` / `GroupKFold`). All skill pairs for any candidate remain strictly inside a single partition (70% Train, 15% Val, 15% Test). Zero candidate leakage.

---

## Extracted Evidence Features
Each (candidate, skill) pair contains 16 evidence features:
1. `resume_mentioned`: Binary indicator of skill presence.
2. `resume_frequency`: Count of skill occurrences across the resume.
3. `in_skills_section`: Presence in flat skills/competencies block.
4. `in_experience_section`: Presence in professional work history blocks.
5. `in_project_section`: Presence in portfolio/academic project blocks.
6. `in_education_section`: Presence in academic coursework blocks.
7. `in_summary_section`: Presence in objective/profile overview.
8. `has_action_verb_context`: Co-occurrence with applied implementation verbs (*developed, architected, deployed, engineered, configured*).
9. `co_occurring_tech_count`: Co-occurrence with related technical tools in the same context block.
10. `section_text_length`: Log length of the containing text context.
11. `is_software_skill`: O\*NET technology classification.
12. `is_essential_skill`: O\*NET occupational skill classification.
13. `onet_importance_proxy`: Background occupational importance reference.
14. `project_evidence_count`: Real-time project repository count (0 in historical resumes).
15. `assessment_evidence_score`: Real-time adaptive assessment demonstration (0 in historical resumes).
16. `practical_evidence_score`: Real-time scenario score (0 in historical resumes).

---

## Model Candidates Evaluated
1. **Heuristic Rule Baseline:** Static weighted rule formula combining mention, experience, and action verbs.
2. **Logistic Regression (L2 Regularized, Calibrated):** Linear evidence weight model.
3. **Random Forest Classifier:** Non-linear decision tree ensemble with balanced class weights.
4. **HistGradientBoostingClassifier:** Fast gradient boosted decision trees.

---

## How to Reproduce
Run the dedicated Phase 3 pipeline:
```powershell
python backend/ml/train_skill_evidence_model.py
```

---

## Real-Time Inference
Use the inference predictor:
```python
from backend.ml.predict_skill_evidence import SkillEvidencePredictor

predictor = SkillEvidencePredictor()
result = predictor.predict_skill(student_profile, "Python")
# Returns:
# {
#   "skill": "Python",
#   "evidence_strength": 0.86,
#   "confidence": 0.80,
#   "status": "STRONG_EVIDENCE",
#   "evidence_sources": ["resume", "project"]
# }
```

### Zero-Knowledge Handling
For candidates without resumes, projects, or assessments:
`missing != weak` and `missing != failed`.
The system safely returns:
```json
{
  "skill": "Python",
  "evidence_strength": 0.0,
  "confidence": 0.0,
  "status": "INSUFFICIENT_EVIDENCE",
  "reason": "No resume, project, assessment, or practical evidence available."
}
```
