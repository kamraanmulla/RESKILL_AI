"""
ReSkillAI - Phase 3: Train & Rigorously Evaluate Skill Evidence Model
Trains an interpretable, calibrated ML model to predict candidate-skill evidence strength.
Zero fake proficiency numbers. Strict candidate isolation.
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Tuple

import numpy as np
import pandas as pd
import joblib
import sklearn

from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix
)

# Import feature extractor from Phase 3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(BASE_DIR)
sys.path.append(ROOT_DIR)

from feature_engineering_skill import (
    SkillEvidenceFeatureExtractor,
    VOCATIONAL_TAXONOMY,
    CATEGORY_EXPECTED_SKILLS
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.Phase3_Training")

DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
EXP_DIR = os.path.join(BASE_DIR, "experiments", "phase_3")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)

RAW_KAGGLE_PATH = os.path.join(DATA_DIR, "raw", "kaggle", "Resume.csv")
PROCESSED_CSV_PATH = os.path.join(PROCESSED_DIR, "candidate_skill_features.csv")


def build_candidate_skill_dataset(force_rebuild: bool = False) -> pd.DataFrame:
    """Builds or loads the candidate-skill pair dataset."""
    if os.path.exists(PROCESSED_CSV_PATH) and not force_rebuild:
        logger.info(f"Loading existing candidate-skill features from: {PROCESSED_CSV_PATH}")
        return pd.read_csv(PROCESSED_CSV_PATH)

    logger.info("Extracting candidate-skill pair features from Resume.csv...")
    df_raw = pd.read_csv(RAW_KAGGLE_PATH)
    df_raw["clean_str"] = df_raw["Resume_str"].fillna("").astype(str).str.strip()
    df_raw["norm_str"] = df_raw["clean_str"].str.lower()
    df_dedup = df_raw.drop_duplicates(subset=["norm_str"]).copy()

    extractor = SkillEvidenceFeatureExtractor()
    records = []

    for idx, row in df_dedup.iterrows():
        cand_id = str(row["ID"])
        resume_text = str(row["clean_str"])
        category = str(row.get("Category", ""))
        cand_records = extractor.extract_from_raw_resume(cand_id, resume_text, category)
        records.extend(cand_records)

    df_features = pd.DataFrame(records)
    df_features.to_csv(PROCESSED_CSV_PATH, index=False)
    logger.info(f"Extracted and saved {len(df_features):,} candidate-skill pairs to: {PROCESSED_CSV_PATH}")
    return df_features


def run_phase_3_training():
    logger.info("=== Starting ReSkillAI Phase 3 Skill Evidence Model Training & Benchmark ===")

    # 1. Load dataset
    df = build_candidate_skill_dataset(force_rebuild=True)
    logger.info(f"Total candidate-skill pairs: {len(df):,} across {df['candidate_id'].nunique():,} unique candidates.")

    # Feature columns
    feature_cols = [
        "resume_mentioned",
        "resume_frequency",
        "in_skills_section",
        "in_experience_section",
        "in_project_section",
        "in_education_section",
        "in_summary_section",
        "has_action_verb_context",
        "co_occurring_tech_count",
        "section_text_length",
        "is_software_skill",
        "is_essential_skill",
        "onet_importance_proxy",
        "project_evidence_count",
        "assessment_evidence_score",
        "practical_evidence_score",
    ]

    target_col = "is_evidence_supported"
    group_col = "candidate_id"

    X = df[feature_cols].copy()
    y = df[target_col].copy()
    groups = df[group_col].copy()

    # 2. Strict Candidate-Isolated Split (70% Train, 15% Val, 15% Test)
    gss1 = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
    train_idx, temp_idx = next(gss1.split(X, y, groups=groups))

    X_train, y_train, groups_train = X.iloc[train_idx], y.iloc[train_idx], groups.iloc[train_idx]
    X_temp, y_temp, groups_temp = X.iloc[temp_idx], y.iloc[temp_idx], groups.iloc[temp_idx]

    gss2 = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=42)
    val_rel_idx, test_rel_idx = next(gss2.split(X_temp, y_temp, groups=groups_temp))

    X_val, y_val, groups_val = X_temp.iloc[val_rel_idx], y_temp.iloc[val_rel_idx], groups_temp.iloc[val_rel_idx]
    X_test, y_test, groups_test = X_temp.iloc[test_rel_idx], y_temp.iloc[test_rel_idx], groups_temp.iloc[test_rel_idx]

    # Verify zero candidate overlap
    train_cands = set(groups_train.unique())
    val_cands = set(groups_val.unique())
    test_cands = set(groups_test.unique())
    assert len(train_cands.intersection(val_cands)) == 0, "Leakage: Train and Val share candidates!"
    assert len(train_cands.intersection(test_cands)) == 0, "Leakage: Train and Test share candidates!"
    assert len(val_cands.intersection(test_cands)) == 0, "Leakage: Val and Test share candidates!"

    logger.info(f"Split sizes: Train={len(X_train):,} pairs ({len(train_cands):,} cands), "
                f"Val={len(X_val):,} pairs ({len(val_cands):,} cands), "
                f"Test={len(X_test):,} pairs ({len(test_cands):,} cands)")
    logger.info(f"Target distribution in Train: Positive={y_train.sum():,} ({y_train.mean():.1%}), Negative={(y_train == 0).sum():,}")

    # 3. Deterministic Heuristic Baseline
    logger.info("Evaluating Heuristic Rule-Based Baseline...")
    def heuristic_predict_proba(X_df):
        # Heuristic scoring formula based on rule weights
        scores = (
            0.20 * X_df["resume_mentioned"] +
            0.35 * X_df["in_experience_section"] +
            0.20 * X_df["in_project_section"] +
            0.25 * X_df["has_action_verb_context"]
        )
        return np.clip(scores, 0.0, 1.0)

    y_test_heuristic_prob = heuristic_predict_proba(X_test)
    y_test_heuristic_pred = (y_test_heuristic_prob >= 0.50).astype(int)

    baseline_metrics = {
        "name": "Heuristic Rule Baseline",
        "accuracy": float(accuracy_score(y_test, y_test_heuristic_pred)),
        "precision": float(precision_score(y_test, y_test_heuristic_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_test_heuristic_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_test, y_test_heuristic_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_test_heuristic_pred, average="weighted", zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_test_heuristic_prob)),
        "pr_auc": float(average_precision_score(y_test, y_test_heuristic_prob)),
        "brier_score": float(brier_score_loss(y_test, y_test_heuristic_prob)),
    }
    logger.info(f"Baseline Test: Macro F1={baseline_metrics['macro_f1']:.4f}, ROC-AUC={baseline_metrics['roc_auc']:.4f}, Accuracy={baseline_metrics['accuracy']:.4f}")

    # 4. Controlled Model Candidates
    gkf = GroupKFold(n_splits=5)

    candidates = [
        (
            "Logistic Regression (Calibrated)",
            Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(class_weight="balanced", random_state=42, max_iter=2000, C=1.0))
            ])
        ),
        (
            "Random Forest",
            Pipeline([
                ("clf", RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42, n_jobs=-1))
            ])
        ),
        (
            "HistGradientBoosting",
            Pipeline([
                ("clf", HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42))
            ])
        )
    ]

    benchmark_results = []
    trained_models = {}

    for name, pipe in candidates:
        logger.info(f"Cross-validating: {name}...")
        cv_scores = []
        cv_rocs = []

        for fold_idx, (tr_idx, cv_idx) in enumerate(gkf.split(X_train, y_train, groups=groups_train)):
            X_tr_f, y_tr_f = X_train.iloc[tr_idx], y_train.iloc[tr_idx]
            X_cv_f, y_cv_f = X_train.iloc[cv_idx], y_train.iloc[cv_idx]

            pipe.fit(X_tr_f, y_tr_f)
            y_cv_pred = pipe.predict(X_cv_f)
            y_cv_prob = pipe.predict_proba(X_cv_f)[:, 1]

            cv_scores.append(f1_score(y_cv_f, y_cv_pred, average="macro", zero_division=0))
            cv_rocs.append(roc_auc_score(y_cv_f, y_cv_prob))

        mean_cv_f1 = float(np.mean(cv_scores))
        std_cv_f1 = float(np.std(cv_scores))
        mean_cv_roc = float(np.mean(cv_rocs))
        std_cv_roc = float(np.std(cv_rocs))

        # Fit on full training set and evaluate on validation set
        pipe.fit(X_train, y_train)
        y_val_pred = pipe.predict(X_val)
        y_val_prob = pipe.predict_proba(X_val)[:, 1]

        val_macro_f1 = float(f1_score(y_val, y_val_pred, average="macro", zero_division=0))
        val_roc = float(roc_auc_score(y_val, y_val_prob))
        val_acc = float(accuracy_score(y_val, y_val_pred))

        logger.info(f"  -> CV Macro F1: {mean_cv_f1:.4f} (+/- {std_cv_f1:.4f}), CV ROC-AUC: {mean_cv_roc:.4f}, Val Macro F1: {val_macro_f1:.4f}, Val ROC: {val_roc:.4f}")

        benchmark_results.append({
            "name": name,
            "cv_macro_f1_mean": mean_cv_f1,
            "cv_macro_f1_std": std_cv_f1,
            "cv_roc_auc_mean": mean_cv_roc,
            "cv_roc_auc_std": std_cv_roc,
            "val_macro_f1": val_macro_f1,
            "val_roc_auc": val_roc,
            "val_accuracy": val_acc,
        })
        trained_models[name] = pipe

    # Pick top candidate on validation ROC-AUC & Macro F1
    best_candidate_meta = max(benchmark_results, key=lambda x: x["val_roc_auc"] + x["val_macro_f1"])
    best_pipe = trained_models[best_candidate_meta["name"]]
    logger.info(f"Top Candidate Model: {best_candidate_meta['name']}")

    # 5. Calibrate the best model with CalibratedClassifierCV
    logger.info("Calibrating top candidate using 3-fold sigmoid calibration...")
    calibrated_clf = CalibratedClassifierCV(estimator=best_pipe, cv=3)
    calibrated_clf.fit(X_train, y_train)

    # 6. Final Test Set Evaluation (Evaluated strictly once)
    logger.info("Evaluating Final Model on Untouched Test Set (Candidate-Isolated)...")
    y_test_pred = calibrated_clf.predict(X_test)
    y_test_prob = calibrated_clf.predict_proba(X_test)[:, 1]

    test_metrics = {
        "model_name": best_candidate_meta["name"],
        "accuracy": float(accuracy_score(y_test, y_test_pred)),
        "precision": float(precision_score(y_test, y_test_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_test_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_test, y_test_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_test_prob)),
        "pr_auc": float(average_precision_score(y_test, y_test_prob)),
        "brier_score": float(brier_score_loss(y_test, y_test_prob)),
        "cv_macro_f1": best_candidate_meta["cv_macro_f1_mean"],
        "cv_macro_f1_std": best_candidate_meta["cv_macro_f1_std"],
        "cv_roc_auc": best_candidate_meta["cv_roc_auc_mean"],
    }

    test_rep = classification_report(y_test, y_test_pred, output_dict=True, zero_division=0)
    test_cm = confusion_matrix(y_test, y_test_pred).tolist()

    logger.info(f"Final Test Accuracy: {test_metrics['accuracy']:.4f} (Baseline: {baseline_metrics['accuracy']:.4f})")
    logger.info(f"Final Test Macro F1: {test_metrics['macro_f1']:.4f} (Baseline: {baseline_metrics['macro_f1']:.4f})")
    logger.info(f"Final Test ROC-AUC: {test_metrics['roc_auc']:.4f} (Baseline: {baseline_metrics['roc_auc']:.4f})")
    logger.info(f"Final Test Brier Score: {test_metrics['brier_score']:.4f} (Baseline: {baseline_metrics['brier_score']:.4f})")

    # Improvements over baseline
    delta_macro_f1 = test_metrics["macro_f1"] - baseline_metrics["macro_f1"]
    delta_roc_auc = test_metrics["roc_auc"] - baseline_metrics["roc_auc"]
    delta_accuracy = test_metrics["accuracy"] - baseline_metrics["accuracy"]

    # Quality Gate Assessment
    # GREEN: Clearly beats baseline, stable CV, calibrated probabilities, zero leakage
    # YELLOW: Useful signal, weak/moderate improvement
    # RED: Indefensible / does not beat baseline
    if delta_macro_f1 > 0.05 and delta_roc_auc > 0.05 and test_metrics["roc_auc"] >= 0.85:
        quality_gate = "GREEN"
        status_str = "MODEL STATUS: GREEN — STRONG EVIDENCE PREDICTION BASELINE"
        trust_status = "YES — Defensible probabilistic evidence strength model"
        integratable = "YES"
    elif delta_macro_f1 > 0.0 and delta_roc_auc > 0.0:
        quality_gate = "YELLOW"
        status_str = "MODEL STATUS: YELLOW — MODERATE SIGNAL"
        trust_status = "PARTIAL — Useful auxiliary signal under weak supervision"
        integratable = "NOT YET"
    else:
        quality_gate = "RED"
        status_str = "MODEL STATUS: RED — DOES NOT BEAT BASELINE"
        trust_status = "NO — Not defensible"
        integratable = "NO"

    # 7. Save Artifacts
    model_artifact_path = os.path.join(MODELS_DIR, "skill_evidence_model.joblib")
    joblib.dump({
        "pipeline": calibrated_clf,
        "feature_cols": feature_cols,
        "taxonomy": VOCATIONAL_TAXONOMY,
    }, model_artifact_path)
    logger.info(f"Saved model artifact to: {model_artifact_path}")

    metadata = {
        "model_name": "ReSkillAI Skill Evidence Strength Model (Phase 3)",
        "model_type": best_candidate_meta["name"],
        "model_file": "skill_evidence_model.joblib",
        "training_strategy": "Weak Supervision with Calibrated Probabilistic Inference",
        "target_type": "Binary Evidence Support (1 = Substantive Applied Evidence, 0 = Casual / Absent)",
        "dataset": "Kaggle Resume Dataset (2,482 deduplicated resumes) -> candidate_skill_features.csv",
        "total_candidate_skill_pairs": len(df),
        "total_unique_candidates": df["candidate_id"].nunique(),
        "train_pairs": len(X_train),
        "val_pairs": len(X_val),
        "test_pairs": len(X_test),
        "feature_names": feature_cols,
        "test_metrics": test_metrics,
        "baseline_metrics": baseline_metrics,
        "improvement_over_baseline": {
            "delta_macro_f1": round(delta_macro_f1, 4),
            "delta_roc_auc": round(delta_roc_auc, 4),
            "delta_accuracy": round(delta_accuracy, 4),
        },
        "quality_gate": quality_gate,
        "status_string": status_str,
        "can_model_be_trusted": trust_status,
        "can_integrate_into_reskillai": integratable,
        "all_candidates_benchmarked": benchmark_results,
        "classification_report": test_rep,
        "confusion_matrix": test_cm,
        "environment": {
            "sklearn_version": sklearn.__version__,
            "joblib_version": joblib.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "python_version": sys.version.split()[0],
            "timestamp": datetime.now().isoformat() + "Z",
        },
        "disclaimer": (
            "Estimates evidence support and confidence from multi-source portfolio signals. "
            "Does NOT represent an unverified 0-100 personal skill proficiency test."
        )
    }

    meta_path = os.path.join(MODELS_DIR, "skill_evidence_model_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved model metadata to: {meta_path}")

    summary_path = os.path.join(EXP_DIR, "experiment_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Mirror artifacts to RESKILL_AI/backend/ml/ if exists
    reskill_models_dir = os.path.join(ROOT_DIR, "RESKILL_AI", "backend", "ml", "models")
    reskill_exp_dir = os.path.join(ROOT_DIR, "RESKILL_AI", "backend", "ml", "experiments", "phase_3")
    if os.path.exists(os.path.dirname(reskill_models_dir)):
        os.makedirs(reskill_models_dir, exist_ok=True)
        os.makedirs(reskill_exp_dir, exist_ok=True)
        shutil.copy2(model_artifact_path, os.path.join(reskill_models_dir, "skill_evidence_model.joblib"))
        shutil.copy2(meta_path, os.path.join(reskill_models_dir, "skill_evidence_model_metadata.json"))
        shutil.copy2(summary_path, os.path.join(reskill_exp_dir, "experiment_summary.json"))
        logger.info("Mirrored Phase 3 artifacts to RESKILL_AI/backend/ml/")

    logger.info("=== Phase 3 Training Pipeline Completed Successfully ===")
    return metadata


if __name__ == "__main__":
    meta = run_phase_3_training()
    print("\nPhase 3 Training Complete. Quality Gate:", meta["quality_gate"])
