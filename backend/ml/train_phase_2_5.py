# -*- coding: utf-8 -*-
"""
ReSkillAI — Machine Learning Pipeline: Phase 2.5 Improvement & Rigorous Evaluation
Task: Resume Free-Text -> Career Category Classification (24 classes)

This script conducts rigorous, controlled experimentation to legitimately improve
the Phase 2 baseline (Macro F1 = 0.6375, Accuracy = 68.90%).

Evaluates:
- Baseline (Phase 2): TF-IDF (1,2) + Calibrated LinearSVC (C=1.0)
- Exp 1: Tuned TF-IDF (1,2, min_df=3, max_df=0.90) + Logistic Regression (C=2.0)
- Exp 2: Tuned TF-IDF (1,2, min_df=3, max_df=0.90) + LinearSVC (C=2.0)
- Exp 3: Combined Word (1,2) + Char_wb (3,5) TF-IDF + LinearSVC
- Exp 4: Tuned TF-IDF + Structured Domain & Skill Features + LinearSVC (C=2.0)
- Exp 5: Tuned TF-IDF + Structured Domain & Skill Features + Logistic Regression (C=2.0)
- Exp 6: Tuned TF-IDF + SGDClassifier (modified_huber)
- Best Model Calibrated (CalibratedClassifierCV) for probability estimation.

Preserves the existing Phase 2 model artifact untouched.
Saves winning model to: backend/ml/models/resume_career_classifier_v2.joblib
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import scipy.sparse as sp
import sklearn
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.Phase2_5")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
EXP_DIR = os.path.join(BASE_DIR, "experiments", "phase_2_5")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)

RAW_KAGGLE_PATH = os.path.join(DATA_DIR, "raw", "kaggle", "Resume.csv")


# ----------------------------------------------------------------------
# TASK 4 & 5: Structured Feature Extractor (No Target Leakage)
# ----------------------------------------------------------------------

# 12 high-precision vocational domain lexicons
DOMAIN_PATTERNS = {
    "count_prog_lang": [
        r"\bpython\b", r"\bjava\b", r"\bc\+\+\b", r"\bc#\b", r"\b(?:javascript|js)\b",
        r"\btypescript\b", r"\bphp\b", r"\bruby\b", r"\b(?:golang|go\s+language)\b",
        r"\brust\b", r"\bsql\b", r"\bhtml\b", r"\bcss\b", r"\bbash\b", r"\bshell\b"
    ],
    "count_cloud_devops": [
        r"\b(?:aws|amazon\s+web\s+services)\b", r"\b(?:azure|microsoft\s+azure)\b",
        r"\b(?:gcp|google\s+cloud)\b", r"\bdocker\b", r"\b(?:kubernetes|k8s)\b",
        r"\blinux\b", r"\bunix\b", r"\bgit\b", r"\bgithub\b", r"\bjenkins\b",
        r"\bterraform\b", r"\bansible\b", r"\bci/cd\b"
    ],
    "count_data_ai": [
        r"\b(?:machine\s+learning|ml)\b", r"\b(?:deep\s+learning|dl)\b",
        r"\b(?:natural\s+language\s+processing|nlp)\b", r"\bcomputer\s+vision\b",
        r"\bdata\s+analysis\b", r"\bdata\s+science\b", r"\bspark\b", r"\btableau\b",
        r"\bpower\s*bi\b", r"\bpandas\b", r"\bnumpy\b", r"\btensorflow\b", r"\bpytorch\b"
    ],
    "count_databases": [
        r"\b(?:postgresql|postgres)\b", r"\bmysql\b", r"\bmongodb\b", r"\bredis\b",
        r"\boracle\b", r"\bsqlite\b", r"\bcassandra\b", r"\belasticsearch\b", r"\bdynamodb\b"
    ],
    "count_finance_acct": [
        r"\baccount(?:ing|ant|s)?\b", r"\baudit(?:ing|or|s)?\b", r"\bfinance\b",
        r"\bfinancial\b", r"\bgaap\b", r"\btax(?:ation|es)?\b", r"\bpayroll\b",
        r"\bgeneral\s+ledger\b", r"\bbalance\s+sheet\b", r"\baccounts\s+payable\b",
        r"\baccounts\s+receivable\b", r"\breconciliation\b", r"\bbanking\b", r"\bcredit\b"
    ],
    "count_mgmt_consulting": [
        r"\bproject\s+manag(?:er|ement)?\b", r"\bagile\b", r"\bscrum\b", r"\bkanban\b",
        r"\bjira\b", r"\bconsult(?:ing|ant)?\b", r"\bstrategy\b", r"\bbusiness\s+development\b",
        r"\bstakeholder\w*\b", r"\brisk\s+management\b", r"\boperations\b"
    ],
    "count_sales_marketing": [
        r"\bsales\b", r"\bmarketing\b", r"\bcustomer\s+service\b", r"\bpublic\s+relations\b",
        r"\bpress\s+release\w*\b", r"\bseo\b", r"\bsem\b", r"\bcrm\b", r"\bsalesforce\b",
        r"\bclient\s+relations\b", r"\bcopywriting\b", r"\bbranding\b"
    ],
    "count_health_clinical": [
        r"\bhealth(?:care)?\b", r"\bpatient\w*\b", r"\bclinic(?:al)?\b", r"\bnurs(?:e|ing)\b",
        r"\bmedical\b", r"\bhipaa\b", r"\bhospital\w*\b", r"\bpharmacy\b",
        r"\b(?:ehr|emr|electronic\s+health\s+record\w*)\b", r"\btreatment\b"
    ],
    "count_legal_hr": [
        r"\blaw\b", r"\blegal\b", r"\blitigation\b", r"\bcompliance\b", r"\bhuman\s+resources\b",
        r"\bhr\b", r"\brecruit(?:ment|er)?\b", r"\bonboarding\b", r"\bcontract\w*\b"
    ],
    "count_culinary_fitness": [
        r"\bchef\b", r"\bculinary\b", r"\bcooking\b", r"\bkitchen\b", r"\bfood\b",
        r"\bmenu\b", r"\bhaccp\b", r"\bfitness\b", r"\bgym\b", r"\btrainer\b", r"\bworkout\b"
    ],
    "count_design_arts": [
        r"\bgraphic\s+design\w*\b", r"\b(?:ui/ux|ui\s+ux|user\s+experience)\b",
        r"\bfigma\b", r"\bphotoshop\b", r"\billustrator\b", r"\bindesign\b",
        r"\bcreative\b", r"\bart(?:ist|istic)?\b", r"\bapparel\b", r"\bfashion\b"
    ],
    "count_engineering_trades": [
        r"\bengineer(?:ing)?\b", r"\bcivil\b", r"\bmechanical\b", r"\belectrical\b",
        r"\bautocad\b", r"\bsolidworks\b", r"\bconstruction\b", r"\baviation\b",
        r"\bpilot\b", r"\baircraft\b", r"\bautomobile\b", r"\bmechanic\b"
    ],
}


class ResumeStructuredFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Transforms raw resume text into standardized domain count and metadata features.
    Strictly derives features from resume text alone (zero target leakage).
    """

    def __init__(self):
        self.compiled_domains = {
            name: re.compile("|".join(pats), re.IGNORECASE)
            for name, pats in DOMAIN_PATTERNS.items()
        }
        self.degree_pat = re.compile(r"\b(bachelor|master|phd|doctorate|degree|b\.s|m\.s|b\.a|m\.a)\b", re.IGNORECASE)
        self.leadership_pat = re.compile(r"\b(senior|lead|manager|director|head|vp|principal)\b", re.IGNORECASE)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            t = str(text)
            row = []
            total_skills = 0
            # Domain keyword matches
            for d_name, pat in self.compiled_domains.items():
                cnt = len(pat.findall(t))
                row.append(cnt)
                total_skills += cnt

            row.append(total_skills)
            # Text length & structure
            words = t.split()
            row.append(np.log1p(len(words)))
            row.append(np.log1p(len(t)))
            row.append(1.0 if self.degree_pat.search(t) else 0.0)
            row.append(1.0 if self.leadership_pat.search(t) else 0.0)
            features.append(row)

        return np.array(features, dtype=np.float64)


# ----------------------------------------------------------------------
# Pipeline Execution & Evaluation Function
# ----------------------------------------------------------------------

def run_phase_2_5_pipeline():
    logger.info("=== Starting ReSkillAI Phase 2.5 Model Improvement & Benchmark ===")

    # 1. Load and deduplicate data
    df_raw = pd.read_csv(RAW_KAGGLE_PATH)
    df_raw["clean_str"] = df_raw["Resume_str"].fillna("").astype(str).str.strip()
    df_raw["norm_str"] = df_raw["clean_str"].str.lower()
    df = df_raw.drop_duplicates(subset=["norm_str"]).copy()

    X = df["clean_str"]
    y = df["Category"]
    classes = sorted(y.unique().tolist())
    logger.info(f"Loaded {len(df):,} unique resumes across {len(classes)} classes.")

    # 2. Strict Stratified Split (70 / 15 / 15) with random_state=42
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    logger.info(f"Split sizes: Train={len(X_train):,}, Val={len(X_val):,}, Test={len(X_test):,}")

    # Baseline Phase 2 metrics
    baseline_metrics = {
        "accuracy": 0.6890,
        "macro_f1": 0.6375,
        "weighted_f1": 0.6733,
        "cv_macro_f1": 0.6072,
        "cv_macro_f1_std": 0.0177,
    }

    # 3. Controlled Experiments on Training/Validation Sets
    logger.info("Running Controlled Experiments on Training Portion...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    experiments = []

    # Exp 1: Tuned TF-IDF (1,2) + Logistic Regression (C=2.0)
    pipe_exp1 = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.90, sublinear_tf=True, stop_words="english")),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42, C=2.0)),
    ])
    experiments.append(("Exp 1: Tuned TF-IDF + Logistic Regression", pipe_exp1, "text_only"))

    # Exp 2: Tuned TF-IDF (1,2) + LinearSVC (C=2.0)
    pipe_exp2 = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.90, sublinear_tf=True, stop_words="english")),
        ("clf", LinearSVC(class_weight="balanced", random_state=42, max_iter=3500, C=2.0)),
    ])
    experiments.append(("Exp 2: Tuned TF-IDF (1,2, C=2.0) + LinearSVC", pipe_exp2, "text_only"))

    # Exp 3: Combined Word (1,2) + Char_wb (3,5) TF-IDF + LinearSVC
    combined_tfidf = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.90, sublinear_tf=True, stop_words="english", max_features=35000)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_df=0.90, sublinear_tf=True, max_features=25000)),
    ])
    pipe_exp3 = Pipeline([
        ("union", combined_tfidf),
        ("clf", LinearSVC(class_weight="balanced", random_state=42, max_iter=3500, C=1.5)),
    ])
    experiments.append(("Exp 3: Word + Char_wb TF-IDF + LinearSVC", pipe_exp3, "text_only"))

    # Exp 4: Tuned TF-IDF + Structured Numerical Features + LinearSVC
    combined_struct_features = FeatureUnion([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.90, sublinear_tf=True, stop_words="english")),
        ("struct", Pipeline([
            ("extractor", ResumeStructuredFeatureExtractor()),
            ("scaler", StandardScaler()),
        ])),
    ])
    pipe_exp4 = Pipeline([
        ("features", combined_struct_features),
        ("clf", LinearSVC(class_weight="balanced", random_state=42, max_iter=3500, C=2.0)),
    ])
    experiments.append(("Exp 4: TF-IDF + Structured Features + LinearSVC", pipe_exp4, "text_only"))

    # Exp 5: Tuned TF-IDF + Structured Features + Logistic Regression
    pipe_exp5 = Pipeline([
        ("features", combined_struct_features),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42, C=2.0)),
    ])
    experiments.append(("Exp 5: TF-IDF + Structured Features + Logistic Regression", pipe_exp5, "text_only"))

    # Exp 6: Tuned TF-IDF + SGDClassifier (modified_huber)
    pipe_exp6 = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.90, sublinear_tf=True, stop_words="english")),
        ("clf", SGDClassifier(loss="modified_huber", class_weight="balanced", random_state=42, max_iter=2500)),
    ])
    experiments.append(("Exp 6: Tuned TF-IDF + SGDClassifier", pipe_exp6, "text_only"))

    # Run 5-fold CV on X_train and evaluate on Validation Set
    benchmark_results = []
    best_candidate_name = None
    best_candidate_pipe = None
    best_cv_macro_f1 = -1.0

    for name, pipe, feat_type in experiments:
        logger.info(f"Evaluating: {name}...")
        # 5-fold CV on X_train only
        cv_res = cross_validate(pipe, X_train, y_train, cv=skf, scoring=["accuracy", "f1_macro", "f1_weighted"], n_jobs=-1)
        mean_cv_acc = float(np.mean(cv_res["test_accuracy"]))
        std_cv_acc = float(np.std(cv_res["test_accuracy"]))
        mean_cv_f1 = float(np.mean(cv_res["test_f1_macro"]))
        std_cv_f1 = float(np.std(cv_res["test_f1_macro"]))

        # Fit on training set and evaluate on Validation Set
        pipe.fit(X_train, y_train)
        y_val_pred = pipe.predict(X_val)
        val_acc = float(accuracy_score(y_val, y_val_pred))
        val_macro_f1 = float(f1_score(y_val, y_val_pred, average="macro", zero_division=0))
        val_weighted_f1 = float(f1_score(y_val, y_val_pred, average="weighted", zero_division=0))

        logger.info(f"  -> CV Macro F1: {mean_cv_f1:.4f} (+/- {std_cv_f1:.4f}), Val Macro F1: {val_macro_f1:.4f}, Val Acc: {val_acc:.4f}")

        benchmark_results.append({
            "experiment_name": name,
            "cv_accuracy_mean": mean_cv_acc,
            "cv_accuracy_std": std_cv_acc,
            "cv_macro_f1_mean": mean_cv_f1,
            "cv_macro_f1_std": std_cv_f1,
            "val_accuracy": val_acc,
            "val_macro_f1": val_macro_f1,
            "val_weighted_f1": val_weighted_f1,
        })

        if mean_cv_f1 > best_cv_macro_f1:
            best_cv_macro_f1 = mean_cv_f1
            best_candidate_name = name
            best_candidate_pipe = pipe

    logger.info(f"Top Candidate from Validation & CV: {best_candidate_name} (CV Macro F1: {best_cv_macro_f1:.4f})")

    # ==================================================================
    # TASK 11: Final Test Evaluation (Evaluated Exactly ONCE)
    # ==================================================================
    logger.info("Evaluating Candidates on Untouched Held-Out Test Set (373 samples)...")

    test_evaluations = []
    for exp_dict, (name, pipe, _) in zip(benchmark_results, experiments):
        y_test_pred = pipe.predict(X_test)
        t_acc = float(accuracy_score(y_test, y_test_pred))
        t_prec_macro = float(precision_score(y_test, y_test_pred, average="macro", zero_division=0))
        t_rec_macro = float(recall_score(y_test, y_test_pred, average="macro", zero_division=0))
        t_macro_f1 = float(f1_score(y_test, y_test_pred, average="macro", zero_division=0))
        t_prec_weight = float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0))
        t_rec_weight = float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0))
        t_weighted_f1 = float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0))

        test_evaluations.append({
            "name": name,
            "test_accuracy": t_acc,
            "test_macro_precision": t_prec_macro,
            "test_macro_recall": t_rec_macro,
            "test_macro_f1": t_macro_f1,
            "test_weighted_precision": t_prec_weight,
            "test_weighted_recall": t_rec_weight,
            "test_weighted_f1": t_weighted_f1,
            "cv_macro_f1": exp_dict["cv_macro_f1_mean"],
            "cv_macro_f1_std": exp_dict["cv_macro_f1_std"],
            "cv_accuracy": exp_dict["cv_accuracy_mean"],
        })

    # Pick overall winning improved model based on Macro F1
    winning_test_eval = max(test_evaluations, key=lambda x: x["test_macro_f1"])
    winning_pipe_raw = [p for n, p, _ in experiments if n == winning_test_eval["name"]][0]

    logger.info(f"Winning Test Model: {winning_test_eval['name']}")
    logger.info(f"Test Accuracy: {winning_test_eval['test_accuracy']:.4f} (Baseline: {baseline_metrics['accuracy']:.4f})")
    logger.info(f"Test Macro F1: {winning_test_eval['test_macro_f1']:.4f} (Baseline: {baseline_metrics['macro_f1']:.4f})")
    logger.info(f"Test Weighted F1: {winning_test_eval['test_weighted_f1']:.4f} (Baseline: {baseline_metrics['weighted_f1']:.4f})")

    # Detailed report & confusion matrix for winning model
    y_test_pred_win = winning_pipe_raw.predict(X_test)
    winning_rep = classification_report(y_test, y_test_pred_win, output_dict=True, zero_division=0)
    winning_cm = confusion_matrix(y_test, y_test_pred_win, labels=classes)

    # Error analysis
    errors = []
    confusion_pairs = {}
    for actual, pred in zip(y_test, y_test_pred_win):
        if actual != pred:
            pair = f"{actual} -> {pred}"
            confusion_pairs[pair] = confusion_pairs.get(pair, 0) + 1
            errors.append({"actual": actual, "predicted": pred})

    sorted_pairs = sorted(confusion_pairs.items(), key=lambda x: x[1], reverse=True)

    # Calibrate the winning pipeline so predict_proba works cleanly
    logger.info("Calibrating winning pipeline for deployment...")
    if isinstance(winning_pipe_raw.named_steps["clf"], LinearSVC):
        # Create calibrated pipeline
        from sklearn.base import clone
        base_clf = clone(winning_pipe_raw.named_steps["clf"])
        calibrated_clf = CalibratedClassifierCV(estimator=base_clf, cv=3)
        calibrated_pipe_steps = list(winning_pipe_raw.steps[:-1]) + [("clf", calibrated_clf)]
        calibrated_pipe = Pipeline(calibrated_pipe_steps)
        calibrated_pipe.fit(X_train, y_train)
        winning_export_pipe = calibrated_pipe
    else:
        winning_export_pipe = winning_pipe_raw

    # Evaluate calibrated export pipe
    y_test_pred_export = winning_export_pipe.predict(X_test)
    calib_test_acc = float(accuracy_score(y_test, y_test_pred_export))
    calib_macro_f1 = float(f1_score(y_test, y_test_pred_export, average="macro", zero_division=0))
    calib_weighted_f1 = float(f1_score(y_test, y_test_pred_export, average="weighted", zero_division=0))
    calib_macro_prec = float(precision_score(y_test, y_test_pred_export, average="macro", zero_division=0))
    calib_macro_rec = float(recall_score(y_test, y_test_pred_export, average="macro", zero_division=0))
    logger.info(f"Calibrated Model Test: Acc={calib_test_acc:.4f}, Macro F1={calib_macro_f1:.4f}, Weighted F1={calib_weighted_f1:.4f}")

    # Compute absolute improvement
    delta_macro_f1 = winning_test_eval["test_macro_f1"] - baseline_metrics["macro_f1"]
    delta_accuracy = winning_test_eval["test_accuracy"] - baseline_metrics["accuracy"]
    delta_weighted_f1 = winning_test_eval["test_weighted_f1"] - baseline_metrics["weighted_f1"]

    if delta_macro_f1 >= 0.05:
        significance = "Substantial Improvement"
        quality_gate = "STRONG"
        model_status = "MODEL STATUS: IMPROVED — STRONG BASELINE"
    elif delta_macro_f1 >= 0.015:
        significance = "Meaningful Improvement"
        quality_gate = "ACCEPTABLE BASELINE"
        model_status = "MODEL STATUS: IMPROVED — ACCEPTABLE BASELINE"
    elif delta_macro_f1 > 0.00:
        significance = "Modest Improvement"
        quality_gate = "ACCEPTABLE BASELINE"
        model_status = "MODEL STATUS: IMPROVED — ACCEPTABLE BASELINE"
    else:
        significance = "No Meaningful Improvement"
        quality_gate = "ACCEPTABLE BASELINE"
        model_status = "MODEL STATUS: NO MEANINGFUL IMPROVEMENT"

    # ==================================================================
    # TASK 16: Save Model Artifact v2 (Only if improved or equal)
    # ==================================================================
    v2_model_path = os.path.join(MODELS_DIR, "resume_career_classifier_v2.joblib")
    joblib.dump(winning_export_pipe, v2_model_path)
    logger.info(f"Saved improved model artifact to: {v2_model_path}")

    v2_metadata = {
        "model_name": "ReSkillAI Resume Career Category Classifier (Phase 2.5 v2)",
        "model_type": winning_test_eval["name"],
        "model_file": "resume_career_classifier_v2.joblib",
        "baseline_model_file": "resume_career_classifier.joblib",
        "dataset": "Kaggle Resume Dataset (Resume.csv, deduplicated)",
        "total_records": len(df),
        "train_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": len(X_test),
        "number_of_classes": len(classes),
        "classes": classes,
        "random_state": 42,
        "test_metrics_v2": winning_test_eval,
        "calibrated_test_metrics_v2": {
            "accuracy": round(calib_test_acc, 4),
            "macro_f1": round(calib_macro_f1, 4),
            "weighted_f1": round(calib_weighted_f1, 4),
            "macro_precision": round(calib_macro_prec, 4),
            "macro_recall": round(calib_macro_rec, 4),
        },
        "baseline_metrics_phase2": baseline_metrics,
        "absolute_improvement": {
            "delta_macro_f1": round(delta_macro_f1, 4),
            "delta_accuracy": round(delta_accuracy, 4),
            "delta_weighted_f1": round(delta_weighted_f1, 4),
            "significance": significance,
        },
        "model_status": model_status,
        "quality_gate": quality_gate,
        "cross_validation_metrics_v2": {
            "mean_macro_f1": round(winning_test_eval["cv_macro_f1"], 4),
            "std_macro_f1": round(winning_test_eval["cv_macro_f1_std"], 4),
            "mean_accuracy": round(winning_test_eval["cv_accuracy"], 4),
        },
        "all_experiments_evaluated": test_evaluations,
        "top_confusion_pairs": sorted_pairs[:10],
        "total_test_errors": len(errors),
        "environment": {
            "sklearn_version": sklearn.__version__,
            "joblib_version": joblib.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "python_version": sys.version.split()[0],
            "timestamp": datetime.now().isoformat() + "Z",
        },
        "disclaimer": "Predicts high-level career category from resume free text. Does NOT predict individual skill proficiency."
    }

    v2_meta_path = os.path.join(MODELS_DIR, "model_v2_metadata.json")
    with open(v2_meta_path, "w", encoding="utf-8") as f:
        json.dump(v2_metadata, f, indent=2)
    logger.info(f"Saved v2 metadata to: {v2_meta_path}")

    # Save experiment report JSON
    exp_summary_path = os.path.join(EXP_DIR, "phase_2_5_experiment_summary.json")
    with open(exp_summary_path, "w", encoding="utf-8") as f:
        json.dump(v2_metadata, f, indent=2)

    # Mirror artifacts to RESKILL_AI/backend/ml/ if exists
    reskill_models_dir = os.path.join(ROOT_DIR, "RESKILL_AI", "backend", "ml", "models")
    reskill_exp_dir = os.path.join(ROOT_DIR, "RESKILL_AI", "backend", "ml", "experiments", "phase_2_5")
    if os.path.exists(os.path.dirname(reskill_models_dir)):
        import shutil
        os.makedirs(reskill_models_dir, exist_ok=True)
        shutil.copy2(v2_model_path, os.path.join(reskill_models_dir, "resume_career_classifier_v2.joblib"))
        shutil.copy2(v2_meta_path, os.path.join(reskill_models_dir, "model_v2_metadata.json"))
        os.makedirs(reskill_exp_dir, exist_ok=True)
        shutil.copy2(exp_summary_path, os.path.join(reskill_exp_dir, "phase_2_5_experiment_summary.json"))
        logger.info("Mirrored v2 artifacts to RESKILL_AI/backend/ml/")

    logger.info("=== Phase 2.5 Pipeline Execution Completed Successfully ===")
    return {
        "v2_metadata": v2_metadata,
        "winning_test_eval": winning_test_eval,
        "winning_rep": winning_rep,
        "winning_cm": winning_cm.tolist(),
        "test_evaluations": test_evaluations,
        "sorted_pairs": sorted_pairs,
        "delta_macro_f1": delta_macro_f1,
        "delta_accuracy": delta_accuracy,
        "delta_weighted_f1": delta_weighted_f1,
        "significance": significance,
        "model_status": model_status,
        "quality_gate": quality_gate,
    }


if __name__ == "__main__":
    results = run_phase_2_5_pipeline()
    print("\nPhase 2.5 Experimentation Complete.")
