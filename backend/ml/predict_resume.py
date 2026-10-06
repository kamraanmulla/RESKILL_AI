# -*- coding: utf-8 -*-
"""
ReSkillAI — Machine Learning Pipeline: Inference Module
Resume Career Category Prediction

This module provides deterministic, standalone inference for predicting
the primary career category from free-text resumes.

DISCLAIMER:
This model predicts high-level career categories (e.g. Information-Technology,
Finance, Healthcare). It does NOT predict individual candidate skill proficiency scores.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
import joblib
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.Inference")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
V2_MODEL_PATH = os.path.join(MODELS_DIR, "resume_career_classifier_v2.joblib")
V2_METADATA_PATH = os.path.join(MODELS_DIR, "model_v2_metadata.json")

MODEL_PATH = V2_MODEL_PATH if os.path.exists(V2_MODEL_PATH) else os.path.join(MODELS_DIR, "resume_career_classifier.joblib")
METADATA_PATH = V2_METADATA_PATH if os.path.exists(V2_METADATA_PATH) else os.path.join(MODELS_DIR, "model_metadata.json")

_MODEL_CACHE = None
_METADATA_CACHE = None



def get_model():
    """Load model pipeline with singleton caching."""
    global _MODEL_CACHE, _METADATA_CACHE
    if _MODEL_CACHE is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}. Run train_career_classifier.py first.")
        logger.info(f"Loading career classifier artifact from: {MODEL_PATH}")
        _MODEL_CACHE = joblib.load(MODEL_PATH)

    if _METADATA_CACHE is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _METADATA_CACHE = json.load(f)

    return _MODEL_CACHE, _METADATA_CACHE


def predict_career_category(resume_text: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Predict high-level career category from free-text resume.

    Parameters:
    - resume_text: String containing raw resume content.
    - top_k: Number of ranked category predictions to return (default: 3).

    Returns:
    Dict containing:
    - predicted_category: Top predicted category name.
    - confidence: Estimated prediction probability score (0.0 to 1.0).
    - top_predictions: List of dicts with category and score for top_k classes.
    - model_version: Version identifier of the classifier.
    - task_type: "career_category_classification"
    - disclaimer: Confirmation that this is NOT a skill proficiency score.
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        return {
            "error": "Empty or invalid resume text provided.",
            "predicted_category": "UNKNOWN",
            "confidence": 0.0,
            "top_predictions": [],
            "model_version": "1.0.0",
        }

    model, metadata = get_model()
    classes = list(model.classes_)

    # Obtain calibrated probabilities
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([resume_text])[0]
    else:
        # Fallback to decision function softmax if probabilities not calibrated
        df_scores = model.decision_function([resume_text])[0]
        exp_scores = np.exp(df_scores - np.max(df_scores))
        probs = exp_scores / np.sum(exp_scores)

    # Rank classes by score
    sorted_indices = np.argsort(probs)[::-1]
    top_indices = sorted_indices[:top_k]

    top_predictions = [
        {
            "rank": rank + 1,
            "category": str(classes[idx]),
            "confidence": round(float(probs[idx]), 4),
        }
        for rank, idx in enumerate(top_indices)
    ]

    best_idx = top_indices[0]
    best_category = str(classes[best_idx])
    best_confidence = round(float(probs[best_idx]), 4)

    return {
        "predicted_category": best_category,
        "confidence": best_confidence,
        "top_predictions": top_predictions,
        "model_type": metadata.get("winning_model_type", "LinearSVC") if metadata else "LinearSVC",
        "model_version": "1.0.0",
        "task_type": "career_category_classification",
        "disclaimer": "Career-category prediction only. Does NOT indicate individual candidate skill proficiency."
    }


def main():
    """Command-line demonstration and smoke test."""
    sample_text = (
        "Senior Software Engineer with 6 years of experience in Python, FastAPI, React, SQL, "
        "Docker, and Kubernetes. Led cloud microservices architecture on AWS and built data pipelines."
    )
    if len(sys.argv) > 1:
        sample_text = " ".join(sys.argv[1:])

    print("\n" + "=" * 65)
    print("ReSkillAI — Resume Career Category Inference Engine")
    print("=" * 65)
    print(f"Input Text Snippet: {sample_text[:120]}...\n")

    result = predict_career_category(sample_text)

    print(f"Predicted Career Category: {result['predicted_category']}")
    print(f"Model Confidence:          {result['confidence']:.2%}")
    print("\nTop 3 Ranked Predictions:")
    for pred in result["top_predictions"]:
        print(f"  {pred['rank']}. {pred['category']:<25} ({pred['confidence']:.2%})")

    print(f"\nModel Version: {result['model_version']}")
    print(f"Notice:        {result['disclaimer']}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
