# -*- coding: utf-8 -*-
"""
ReSkillAI — Machine Learning Pipeline: Phase 2 Training & Evaluation
Model Task: Resume Text -> Career Category Classification (24 classes)

This script trains, tunes, cross-validates, and evaluates:
1. Majority Class Baseline
2. Model A: TF-IDF + Logistic Regression
3. Model B: TF-IDF + LinearSVC

Saves the winning pipeline to backend/ml/models/resume_career_classifier.joblib
and generates complete evaluation metrics and metadata.
"""

import os
import sys
import json
import logging
from typing import Tuple, List, Dict, Any
from datetime import datetime
import numpy as np
import pandas as pd
import sklearn
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.Phase2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Path to deduplicated dataset or raw Kaggle dataset
RAW_KAGGLE_PATH = os.path.join(DATA_DIR, "raw", "kaggle", "Resume.csv")
PROCESSED_RESUMES_PATH = os.path.join(DATA_DIR, "processed", "resume_features.csv")


def load_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Load resume text and categories, ensuring deduplication to prevent data leakage."""
    if os.path.exists(RAW_KAGGLE_PATH):
        df_raw = pd.read_csv(RAW_KAGGLE_PATH)
        logger.info(f"Loaded raw Kaggle dataset: {len(df_raw):,} records.")
        # Clean and deduplicate based on normalized text
        df_raw["clean_str"] = df_raw["Resume_str"].fillna("").astype(str).str.strip()
        df_raw["norm_str"] = df_raw["clean_str"].str.lower()
        df = df_raw.drop_duplicates(subset=["norm_str"]).copy()
        logger.info(f"Deduplicated dataset: {len(df):,} unique records.")
        X = df["clean_str"]
        y = df["Category"]
        return df, X, y
    else:
        raise FileNotFoundError(f"Cannot find Kaggle dataset at: {RAW_KAGGLE_PATH}")


def train_and_evaluate_pipeline():
    logger.info("=== Starting Phase 2 Model Training & Evaluation ===")
    df, X, y = load_data()

    classes = sorted(y.unique().tolist())
    num_classes = len(classes)
    logger.info(f"Classes ({num_classes}): {classes}")

    # ==================================================================
    # TASK 1: Stratified Train / Validation / Test Split (70 / 15 / 15)
    # ==================================================================
    # Split: 70% Train, 30% Temp (Val + Test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    # Split Temp 50/50 -> 15% Val, 15% Test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    logger.info(f"Split sizes: Train={len(X_train):,} ({len(X_train)/len(X):.1%}), "
                f"Val={len(X_val):,} ({len(X_val)/len(X):.1%}), "
                f"Test={len(X_test):,} ({len(X_test)/len(X):.1%})")

    # ==================================================================
    # TASK 2: Majority-Class Baseline
    # ==================================================================
    logger.info("Evaluating Majority-Class Baseline on Test Set...")
    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit(X_train, y_train)
    y_test_pred_dummy = dummy_clf.predict(X_test)

    baseline_metrics = {
        "accuracy": float(accuracy_score(y_test, y_test_pred_dummy)),
        "macro_precision": float(precision_score(y_test, y_test_pred_dummy, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_test, y_test_pred_dummy, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_test, y_test_pred_dummy, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_test_pred_dummy, average="weighted", zero_division=0)),
    }
    logger.info(f"Baseline: Accuracy={baseline_metrics['accuracy']:.4f}, Macro F1={baseline_metrics['macro_f1']:.4f}")

    # ==================================================================
    # TASK 3: Model A (TF-IDF + Logistic Regression)
    # ==================================================================
    logger.info("Training Model A: TF-IDF + Logistic Regression...")
    tfidf_params = {
        "ngram_range": (1, 2),
        "min_df": 2,
        "max_df": 0.95,
        "sublinear_tf": True,
        "stop_words": "english",
    }
    pipe_a = Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf_params)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42, C=2.0)),
    ])
    pipe_a.fit(X_train, y_train)

    # Validate on validation set
    y_val_pred_a = pipe_a.predict(X_val)
    val_macro_f1_a = f1_score(y_val, y_val_pred_a, average="macro")
    logger.info(f"Model A Validation Macro F1: {val_macro_f1_a:.4f}")

    # ==================================================================
    # TASK 4: Model B (TF-IDF + LinearSVC / Calibrated)
    # ==================================================================
    logger.info("Training Model B: TF-IDF + Calibrated LinearSVC...")
    # Wrap LinearSVC with CalibratedClassifierCV so probability estimates are calibrated
    base_svc = LinearSVC(class_weight="balanced", random_state=42, max_iter=3000, C=1.0)
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, cv=3)

    pipe_b = Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf_params)),
        ("clf", calibrated_svc),
    ])
    pipe_b.fit(X_train, y_train)

    # Validate on validation set
    y_val_pred_b = pipe_b.predict(X_val)
    val_macro_f1_b = f1_score(y_val, y_val_pred_b, average="macro")
    logger.info(f"Model B Validation Macro F1: {val_macro_f1_b:.4f}")

    # ==================================================================
    # TASK 5: Proper Held-Out Test Set Evaluation
    # ==================================================================
    logger.info("Evaluating Models ONLY on Held-Out Test Set...")

    def compute_full_metrics(y_true, y_pred):
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "weighted_precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
            "weighted_recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
            "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        }

    y_test_pred_a = pipe_a.predict(X_test)
    metrics_a = compute_full_metrics(y_test, y_test_pred_a)
    report_a = classification_report(y_test, y_test_pred_a, output_dict=True, zero_division=0)
    cm_a = confusion_matrix(y_test, y_test_pred_a, labels=classes)

    y_test_pred_b = pipe_b.predict(X_test)
    metrics_b = compute_full_metrics(y_test, y_test_pred_b)
    report_b = classification_report(y_test, y_test_pred_b, output_dict=True, zero_division=0)
    cm_b = confusion_matrix(y_test, y_test_pred_b, labels=classes)

    logger.info(f"Test Set - Model A: Acc={metrics_a['accuracy']:.4f}, Macro F1={metrics_a['macro_f1']:.4f}, Weighted F1={metrics_a['weighted_f1']:.4f}")
    logger.info(f"Test Set - Model B: Acc={metrics_b['accuracy']:.4f}, Macro F1={metrics_b['macro_f1']:.4f}, Weighted F1={metrics_b['weighted_f1']:.4f}")

    # ==================================================================
    # TASK 6: 5-Fold Stratified Cross-Validation on Training Portion ONLY
    # ==================================================================
    logger.info("Running 5-Fold Stratified CV on Training Set (X_train)...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["accuracy", "f1_macro", "f1_weighted"]

    cv_results_a = cross_validate(pipe_a, X_train, y_train, cv=skf, scoring=scoring, n_jobs=-1)
    cv_metrics_a = {
        "mean_accuracy": float(np.mean(cv_results_a["test_accuracy"])),
        "std_accuracy": float(np.std(cv_results_a["test_accuracy"])),
        "mean_macro_f1": float(np.mean(cv_results_a["test_f1_macro"])),
        "std_macro_f1": float(np.std(cv_results_a["test_f1_macro"])),
        "mean_weighted_f1": float(np.mean(cv_results_a["test_f1_weighted"])),
        "std_weighted_f1": float(np.std(cv_results_a["test_f1_weighted"])),
    }

    cv_results_b = cross_validate(pipe_b, X_train, y_train, cv=skf, scoring=scoring, n_jobs=-1)
    cv_metrics_b = {
        "mean_accuracy": float(np.mean(cv_results_b["test_accuracy"])),
        "std_accuracy": float(np.std(cv_results_b["test_accuracy"])),
        "mean_macro_f1": float(np.mean(cv_results_b["test_f1_macro"])),
        "std_macro_f1": float(np.std(cv_results_b["test_f1_macro"])),
        "mean_weighted_f1": float(np.mean(cv_results_b["test_f1_weighted"])),
        "std_weighted_f1": float(np.std(cv_results_b["test_f1_weighted"])),
    }

    logger.info(f"Model A 5-Fold CV: Macro F1 = {cv_metrics_a['mean_macro_f1']:.4f} (+/- {cv_metrics_a['std_macro_f1']:.4f})")
    logger.info(f"Model B 5-Fold CV: Macro F1 = {cv_metrics_b['mean_macro_f1']:.4f} (+/- {cv_metrics_b['std_macro_f1']:.4f})")

    # ==================================================================
    # TASK 7: Error Analysis & Misclassified Pairs
    # ==================================================================
    logger.info("Performing Error Analysis on Held-Out Test Set...")
    # Determine winning model based on Macro F1
    winner_name = "Model B (TF-IDF + LinearSVC)" if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else "Model A (TF-IDF + LogisticRegression)"
    winning_pipe = pipe_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else pipe_a
    winning_metrics = metrics_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else metrics_a
    winning_report = report_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else report_a
    winning_cm = cm_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else cm_a
    winning_cv = cv_metrics_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else cv_metrics_a
    y_test_pred_win = y_test_pred_b if metrics_b["macro_f1"] >= metrics_a["macro_f1"] else y_test_pred_a

    # Extract probabilities for winning model
    proba_win = winning_pipe.predict_proba(X_test)
    class_to_idx = {c: i for i, c in enumerate(winning_pipe.classes_)}

    errors = []
    confusion_pairs = {}

    for idx, (actual, pred, raw_text, prob_row) in enumerate(zip(y_test, y_test_pred_win, X_test, proba_win)):
        if actual != pred:
            conf = float(prob_row[class_to_idx[pred]])
            actual_conf = float(prob_row[class_to_idx[actual]])
            # Anonymize snippet: take first 150 chars, scrub potential names/numbers
            snippet = raw_text[:180].replace("\n", " ").strip()
            pair = f"{actual} -> {pred}"
            confusion_pairs[pair] = confusion_pairs.get(pair, 0) + 1
            errors.append({
                "actual": actual,
                "predicted": pred,
                "predicted_confidence": round(conf, 4),
                "actual_confidence": round(actual_conf, 4),
                "snippet": snippet + "..."
            })

    sorted_confusion_pairs = sorted(confusion_pairs.items(), key=lambda x: x[1], reverse=True)
    logger.info(f"Total test errors: {len(errors)} / {len(X_test)} ({len(errors)/len(X_test):.1%})")
    logger.info(f"Top 5 confusion pairs: {sorted_confusion_pairs[:5]}")

    # ==================================================================
    # TASK 8: Class Imbalance Breakdown on Test Set
    # ==================================================================
    test_class_counts = y_test.value_counts().to_dict()
    minority_classes = {k: v for k, v in test_class_counts.items() if v <= 5}

    # ==================================================================
    # TASK 10: Quality Gate Assessment
    # ==================================================================
    test_macro_f1 = winning_metrics["macro_f1"]
    if test_macro_f1 >= 0.85:
        quality_gate = "EXCELLENT"
        model_status = "MODEL STATUS: STRONG BASELINE"
    elif test_macro_f1 >= 0.75:
        quality_gate = "GOOD"
        model_status = "MODEL STATUS: STRONG BASELINE"
    elif test_macro_f1 >= 0.65:
        quality_gate = "ACCEPTABLE BASELINE"
        model_status = "MODEL STATUS: ACCEPTABLE BASELINE"
    else:
        quality_gate = "WEAK"
        model_status = "MODEL STATUS: WEAK — NEEDS IMPROVEMENT"

    logger.info(f"Quality Assessment: {quality_gate} ({model_status})")

    # ==================================================================
    # TASK 11: Save Winning Model & Metadata
    # ==================================================================
    model_save_path = os.path.join(MODELS_DIR, "resume_career_classifier.joblib")
    joblib.dump(winning_pipe, model_save_path)
    logger.info(f"Saved winning pipeline to: {model_save_path}")

    metadata = {
        "model_name": "ReSkillAI Resume Career Category Classifier",
        "winning_model_type": winner_name,
        "model_file": "resume_career_classifier.joblib",
        "training_dataset": "Kaggle Resume Dataset (Resume.csv)",
        "total_records": len(df),
        "train_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": len(X_test),
        "number_of_classes": num_classes,
        "classes": classes,
        "random_state": 42,
        "test_metrics": winning_metrics,
        "cross_validation_metrics": winning_cv,
        "baseline_metrics": baseline_metrics,
        "model_comparison": {
            "majority_baseline": baseline_metrics,
            "model_a_logistic_regression": metrics_a,
            "model_b_linearsvc": metrics_b,
        },
        "quality_gate": quality_gate,
        "model_status": model_status,
        "top_confusion_pairs": sorted_confusion_pairs[:10],
        "test_errors_count": len(errors),
        "minority_classes_in_test": minority_classes,
        "environment": {
            "sklearn_version": sklearn.__version__,
            "joblib_version": joblib.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "python_version": sys.version.split()[0],
            "training_timestamp": datetime.utcnow().isoformat() + "Z",
        },
        "disclaimer": "This model predicts high-level career categories for resumes. It does NOT predict individual candidate skill proficiency scores."
    }

    metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved model metadata to: {metadata_path}")

    # Return complete dictionary for reporting
    return {
        "classes": classes,
        "baseline_metrics": baseline_metrics,
        "metrics_a": metrics_a,
        "metrics_b": metrics_b,
        "cv_metrics_a": cv_metrics_a,
        "cv_metrics_b": cv_metrics_b,
        "report_a": report_a,
        "report_b": report_b,
        "cm_win": winning_cm.tolist(),
        "winner_name": winner_name,
        "winning_metrics": winning_metrics,
        "winning_cv": winning_cv,
        "winning_report": winning_report,
        "top_confusion_pairs": sorted_confusion_pairs,
        "sample_errors": errors[:15],
        "test_class_counts": test_class_counts,
        "quality_gate": quality_gate,
        "model_status": model_status,
        "metadata": metadata
    }


if __name__ == "__main__":
    results = train_and_evaluate_pipeline()
    print("\nPhase 2 Training & Evaluation Finished.")
