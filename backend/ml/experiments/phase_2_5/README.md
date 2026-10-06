# ReSkillAI Phase 2.5 — ML Model Improvement & Benchmark

## Overview
Phase 2.5 builds upon the initial Phase 2 baseline for the **Resume Text → Career Category Classifier** in ReSkillAI.
The primary goal is to legitimately improve **Macro F1** across all 24 professional categories without sacrificing generalization or introducing data leakage.

---

## Datasets Required
1. **Kaggle Resume Dataset**:
   - Location: `backend/ml/data/raw/Resume.csv`
   - Total rows: 2,484 (2,482 after deduplication of normalized text)
   - Categories: 24 occupational classes
2. **O\*NET 31.0 Reference Taxonomies**:
   - Location: `backend/ml/data/raw/onet_csv/`
   - Used exclusively as a structured occupational knowledge and vocabulary reference (technology skills, tools, activities).
   - Zero circular features (no category leakage).

---

## Controlled Split & Leakage Verification
- **Split Ratio**: 70% Train (1,737), 15% Validation (372), 15% Test (373).
- **Random Seed**: `random_state=42` with stratified distribution across 24 categories.
- **Leakage Guards**:
  - TF-IDF vectorizers fitted strictly on training data (`X_train`).
  - Structured feature extractors and scalers fitted strictly on training data (`X_train`).
  - Held-out test set (373 samples) preserved untouched until final benchmark evaluation.
  - Zero duplicate resumes across splits.

---

## Models Tested in Phase 2.5
1. **Baseline (Phase 2)**: TF-IDF (`ngram_range=(1,2)`) + Calibrated LinearSVC (`C=1.0`)
2. **Experiment 1**: Tuned TF-IDF (`ngram_range=(1,2)`, `min_df=3`, `max_df=0.90`, `sublinear_tf=True`) + Logistic Regression (`C=2.0`, `class_weight='balanced'`)
3. **Experiment 2**: Tuned TF-IDF (`ngram_range=(1,2)`, `min_df=3`, `max_df=0.90`, `sublinear_tf=True`) + LinearSVC (`C=2.0`, `class_weight='balanced'`)
4. **Experiment 3**: Combined Word (`ngram_range=(1,2)`) + Subword Char (`analyzer='char_wb'`, `ngram_range=(3,5)`) TF-IDF + LinearSVC (`C=1.5`)
5. **Experiment 4**: Tuned TF-IDF + 15 Structured Resume Feature Counts (technologies, education, leadership) + LinearSVC
6. **Experiment 5**: Tuned TF-IDF + 15 Structured Resume Feature Counts + Logistic Regression
7. **Experiment 6**: Tuned TF-IDF + SGDClassifier (`loss='modified_huber'`, `class_weight='balanced'`)

---

## How to Reproduce
Run the dedicated Phase 2.5 training pipeline script:
```powershell
python backend/ml/train_phase_2_5.py
```

The script will:
1. Verify dataset integrity and splits.
2. Execute 5-fold cross-validation on `X_train`.
3. Evaluate candidates on the validation set.
4. Select top candidates and evaluate on the held-out test set.
5. Calibrate the winning pipeline with `CalibratedClassifierCV` for well-calibrated probabilities.
6. Export the new model artifact to `backend/ml/models/resume_career_classifier_v2.joblib` and metadata to `backend/ml/models/model_v2_metadata.json`.

---

## Artifact Locations
- Preserved Phase 2 Baseline: `backend/ml/models/resume_career_classifier.joblib`
- Baseline Metrics: `backend/ml/experiments/phase_2_5/baseline_results.json`
- Phase 2.5 Improved Model v2: `backend/ml/models/resume_career_classifier_v2.joblib`
- Model v2 Metadata: `backend/ml/models/model_v2_metadata.json`
- Experiment Summary: `backend/ml/experiments/phase_2_5/phase_2_5_experiment_summary.json`
- Detailed Evaluation Report: `backend/ml/PHASE_2_5_EVALUATION.md`

---

## Model Scope & Limitations
- **Scope**: Classifies candidate resume text into one of 24 broad occupational sectors (e.g. Information-Technology, Engineering, Finance, Healthcare).
- **Safety Boundary**: This model **DOES NOT** predict candidate skill proficiency scores, grades, or personal competency levels. Proficiency and readiness evaluation in ReSkillAI is derived exclusively from real user assessment evidence, verified projects, and deterministic skill coverage.
