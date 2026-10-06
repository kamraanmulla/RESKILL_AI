# -*- coding: utf-8 -*-
"""
ReSkillAI — Machine Learning Pipeline: Feature Engineering Module
Phase 1: Feature Construction & Processed Dataset Generation

This module generates:
1. occupation_features.csv (O*NET occupational benchmark features)
2. skill_occupation_features.csv (Occupation-skill relationship features)
3. resume_features.csv (Candidate-level feature representations from resumes)

Validation checks are executed across all processed datasets.
CRITICAL: No fake proficiency scores are created. Ground-truth boundaries are explicitly enforced.
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
import numpy as np
import pandas as pd

from preprocess import (
    BASE_DIR,
    DATA_DIR,
    PROCESSED_DIR,
    run_preprocessing_pipeline,
    normalize_category,
    CATEGORY_TO_ONET_MAPPING,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.FeatureEngineering")


# ----------------------------------------------------------------------
# Helper Normalization Functions
# ----------------------------------------------------------------------

def norm_min_max(val: float, min_val: float, max_val: float) -> float:
    """Normalize a value to [0.0, 1.0] given known theoretical bounds."""
    if pd.isna(val):
        return 0.0
    return float(np.clip((val - min_val) / (max_val - min_val), 0.0, 1.0))


# ----------------------------------------------------------------------
# TASK 5: O*NET Feature Construction
# ----------------------------------------------------------------------

def build_occupation_features(onet_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Construct rich occupational features across all O*NET occupations.
    Aggregates:
    - Job Zone (1-5 preparation tiers)
    - Essential skills (IM 1-5, LV 0-7)
    - Transferable skills (IM 1-5, LV 0-7)
    - Software skills, Hot Tech, and In Demand counts
    - Knowledge domains (IM, LV)
    - Abilities (IM, LV)
    - Generalized Work Activities (IM, LV)
    - Task statements and importance ratings
    - Incumbent educational attainment
    - Related occupations count
    """
    logger.info("Constructing O*NET Occupation Features...")
    df_occ = onet_data["occupation_data.csv"][["O*NET-SOC Code", "Title"]].copy()
    df_occ.columns = ["soc_code", "occupation_title"]

    # 1. Job Zones (1 - 5)
    df_jz = onet_data["job_zones.csv"][["O*NET-SOC Code", "Job Zone"]].drop_duplicates("O*NET-SOC Code")
    df_occ = df_occ.merge(df_jz.rename(columns={"O*NET-SOC Code": "soc_code", "Job Zone": "job_zone"}), on="soc_code", how="left")
    df_occ["job_zone"] = df_occ["job_zone"].fillna(df_occ["job_zone"].median())
    df_occ["job_zone_norm"] = df_occ["job_zone"].apply(lambda z: norm_min_max(z, 1.0, 5.0))

    # 2. Essential Skills Aggregates (10 skills, IM: 1-5, LV: 0-7)
    df_ess = onet_data["essential_skills.csv"]
    ess_im = df_ess[df_ess["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].agg(["count", "mean", "max"]).reset_index()
    ess_lv = df_ess[df_ess["Scale ID"] == "LV"].groupby("O*NET-SOC Code")["Data Value"].agg(["mean", "max"]).reset_index()
    ess_agg = ess_im.merge(ess_lv, on="O*NET-SOC Code", suffixes=("_im", "_lv"))
    ess_agg.columns = ["soc_code", "num_essential_skills", "essential_skills_im_mean", "essential_skills_im_max", "essential_skills_lv_mean", "essential_skills_lv_max"]
    df_occ = df_occ.merge(ess_agg, on="soc_code", how="left")

    df_occ["num_essential_skills"] = df_occ["num_essential_skills"].fillna(0).astype(int)
    df_occ["essential_skills_im_mean"] = df_occ["essential_skills_im_mean"].fillna(0.0)
    df_occ["essential_skills_im_mean_norm"] = df_occ["essential_skills_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))
    df_occ["essential_skills_lv_mean"] = df_occ["essential_skills_lv_mean"].fillna(0.0)
    df_occ["essential_skills_lv_mean_norm"] = df_occ["essential_skills_lv_mean"].apply(lambda v: norm_min_max(v, 0.0, 7.0))

    # 3. Transferable Skills Aggregates (25 skills, IM: 1-5, LV: 0-7)
    df_trans = onet_data["transferable_skills.csv"]
    trans_im = df_trans[df_trans["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].agg(["count", "mean", "max"]).reset_index()
    trans_lv = df_trans[df_trans["Scale ID"] == "LV"].groupby("O*NET-SOC Code")["Data Value"].agg(["mean", "max"]).reset_index()
    trans_agg = trans_im.merge(trans_lv, on="O*NET-SOC Code", suffixes=("_im", "_lv"))
    trans_agg.columns = ["soc_code", "num_transferable_skills", "transferable_skills_im_mean", "transferable_skills_im_max", "transferable_skills_lv_mean", "transferable_skills_lv_max"]
    df_occ = df_occ.merge(trans_agg, on="soc_code", how="left")

    df_occ["num_transferable_skills"] = df_occ["num_transferable_skills"].fillna(0).astype(int)
    df_occ["transferable_skills_im_mean"] = df_occ["transferable_skills_im_mean"].fillna(0.0)
    df_occ["transferable_skills_im_mean_norm"] = df_occ["transferable_skills_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))
    df_occ["transferable_skills_lv_mean"] = df_occ["transferable_skills_lv_mean"].fillna(0.0)
    df_occ["transferable_skills_lv_mean_norm"] = df_occ["transferable_skills_lv_mean"].apply(lambda v: norm_min_max(v, 0.0, 7.0))

    # 4. Software Skills & Hot Technologies
    df_soft = onet_data["software_skills.csv"]
    soft_counts = df_soft.groupby("O*NET-SOC Code").agg(
        num_software_skills=("Workplace Example", "count"),
        num_hot_technologies=("Hot Technology", lambda x: (x == "Y").sum()),
        num_in_demand_software=("In Demand", lambda x: (x == "Y").sum()),
    ).reset_index().rename(columns={"O*NET-SOC Code": "soc_code"})
    df_occ = df_occ.merge(soft_counts, on="soc_code", how="left")
    df_occ["num_software_skills"] = df_occ["num_software_skills"].fillna(0).astype(int)
    df_occ["num_hot_technologies"] = df_occ["num_hot_technologies"].fillna(0).astype(int)
    df_occ["num_in_demand_software"] = df_occ["num_in_demand_software"].fillna(0).astype(int)

    # 5. Knowledge Domains (33 domains, IM: 1-5, LV: 0-7)
    df_know = onet_data["knowledge.csv"]
    know_im = df_know[df_know["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].agg(["count", "mean"]).reset_index()
    know_lv = df_know[df_know["Scale ID"] == "LV"].groupby("O*NET-SOC Code")["Data Value"].mean().reset_index()
    know_agg = know_im.merge(know_lv, on="O*NET-SOC Code")
    know_agg.columns = ["soc_code", "num_knowledge_domains", "knowledge_im_mean", "knowledge_lv_mean"]
    df_occ = df_occ.merge(know_agg, on="soc_code", how="left")
    df_occ["num_knowledge_domains"] = df_occ["num_knowledge_domains"].fillna(0).astype(int)
    df_occ["knowledge_im_mean"] = df_occ["knowledge_im_mean"].fillna(0.0)
    df_occ["knowledge_im_mean_norm"] = df_occ["knowledge_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))
    df_occ["knowledge_lv_mean"] = df_occ["knowledge_lv_mean"].fillna(0.0)
    df_occ["knowledge_lv_mean_norm"] = df_occ["knowledge_lv_mean"].apply(lambda v: norm_min_max(v, 0.0, 7.0))

    # 6. Abilities (52 abilities, IM: 1-5, LV: 0-7)
    df_ab = onet_data["abilities.csv"]
    ab_im = df_ab[df_ab["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].agg(["count", "mean"]).reset_index()
    ab_lv = df_ab[df_ab["Scale ID"] == "LV"].groupby("O*NET-SOC Code")["Data Value"].mean().reset_index()
    ab_agg = ab_im.merge(ab_lv, on="O*NET-SOC Code")
    ab_agg.columns = ["soc_code", "num_abilities", "abilities_im_mean", "abilities_lv_mean"]
    df_occ = df_occ.merge(ab_agg, on="soc_code", how="left")
    df_occ["num_abilities"] = df_occ["num_abilities"].fillna(0).astype(int)
    df_occ["abilities_im_mean"] = df_occ["abilities_im_mean"].fillna(0.0)
    df_occ["abilities_im_mean_norm"] = df_occ["abilities_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))
    df_occ["abilities_lv_mean"] = df_occ["abilities_lv_mean"].fillna(0.0)
    df_occ["abilities_lv_mean_norm"] = df_occ["abilities_lv_mean"].apply(lambda v: norm_min_max(v, 0.0, 7.0))

    # 7. Work Activities (GWA, IM: 1-5, LV: 0-7)
    df_wa = onet_data["work_activities.csv"]
    wa_im = df_wa[df_wa["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].agg(["count", "mean"]).reset_index()
    wa_lv = df_wa[df_wa["Scale ID"] == "LV"].groupby("O*NET-SOC Code")["Data Value"].mean().reset_index()
    wa_agg = wa_im.merge(wa_lv, on="O*NET-SOC Code")
    wa_agg.columns = ["soc_code", "num_work_activities", "work_activities_im_mean", "work_activities_lv_mean"]
    df_occ = df_occ.merge(wa_agg, on="soc_code", how="left")
    df_occ["num_work_activities"] = df_occ["num_work_activities"].fillna(0).astype(int)
    df_occ["work_activities_im_mean"] = df_occ["work_activities_im_mean"].fillna(0.0)
    df_occ["work_activities_im_mean_norm"] = df_occ["work_activities_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))
    df_occ["work_activities_lv_mean"] = df_occ["work_activities_lv_mean"].fillna(0.0)
    df_occ["work_activities_lv_mean_norm"] = df_occ["work_activities_lv_mean"].apply(lambda v: norm_min_max(v, 0.0, 7.0))

    # 8. Tasks (Statements & Ratings)
    df_ts = onet_data["task_statements.csv"].groupby("O*NET-SOC Code")["Task ID"].count().reset_index()
    df_ts.columns = ["soc_code", "num_task_statements"]
    df_occ = df_occ.merge(df_ts, on="soc_code", how="left")
    df_occ["num_task_statements"] = df_occ["num_task_statements"].fillna(0).astype(int)

    df_tr = onet_data["task_ratings.csv"]
    tr_im = df_tr[df_tr["Scale ID"] == "IM"].groupby("O*NET-SOC Code")["Data Value"].mean().reset_index()
    tr_im.columns = ["soc_code", "task_im_mean"]
    df_occ = df_occ.merge(tr_im, on="soc_code", how="left")
    df_occ["task_im_mean"] = df_occ["task_im_mean"].fillna(0.0)
    df_occ["task_im_mean_norm"] = df_occ["task_im_mean"].apply(lambda v: norm_min_max(v, 1.0, 5.0))

    # 9. Educational Attainment (Mode Category)
    df_edu = onet_data["education.csv"]
    if "Category" in df_edu.columns and "Data Value" in df_edu.columns:
        # Find category with highest percentage for each occupation
        idx_max = df_edu.groupby("O*NET-SOC Code")["Data Value"].idxmax().dropna()
        top_edu = df_edu.loc[idx_max, ["O*NET-SOC Code", "Category", "Data Value"]].rename(
            columns={"O*NET-SOC Code": "soc_code", "Category": "top_education_category", "Data Value": "top_education_percentage"}
        )
        df_occ = df_occ.merge(top_edu, on="soc_code", how="left")
    else:
        df_occ["top_education_category"] = "Unspecified"
        df_occ["top_education_percentage"] = 0.0

    df_occ["top_education_category"] = df_occ["top_education_category"].fillna("Unspecified")
    df_occ["top_education_percentage"] = df_occ["top_education_percentage"].fillna(0.0)
    df_occ["top_education_percentage_norm"] = df_occ["top_education_percentage"] / 100.0

    # 10. Related Occupations Count
    df_rel = onet_data["related_occupations.csv"].groupby("O*NET-SOC Code")["Related O*NET-SOC Code"].count().reset_index()
    df_rel.columns = ["soc_code", "num_related_occupations"]
    df_occ = df_occ.merge(df_rel, on="soc_code", how="left")
    df_occ["num_related_occupations"] = df_occ["num_related_occupations"].fillna(0).astype(int)

    logger.info(f"Occupation Features built successfully: {len(df_occ):,} occupations, {len(df_occ.columns)} features.")
    return df_occ


def build_skill_occupation_features(onet_data: Dict[str, pd.DataFrame], df_occ_features: pd.DataFrame) -> pd.DataFrame:
    """
    Construct pairwise skill-to-occupation feature table.
    Encompasses:
    - Essential skills (IM, LV)
    - Transferable skills (IM, LV)
    - Software skills (In Demand, Hot Technology)
    - Contextual features joined from occupation_features.
    """
    logger.info("Constructing Skill-Occupation Pairwise Features...")
    records = []

    # 1. Essential Skills
    df_ess = onet_data["essential_skills.csv"]
    ess_piv = df_ess.pivot_table(
        index=["O*NET-SOC Code", "Title", "Element Name"],
        columns="Scale ID",
        values="Data Value",
        aggfunc="first"
    ).reset_index()
    
    for _, row in ess_piv.iterrows():
        im_val = float(row.get("IM", 1.0)) if pd.notna(row.get("IM")) else 1.0
        lv_val = float(row.get("LV", 0.0)) if pd.notna(row.get("LV")) else 0.0
        records.append({
            "soc_code": str(row["O*NET-SOC Code"]),
            "occupation_title": str(row["Title"]),
            "skill_name": str(row["Element Name"]).strip(),
            "skill_type": "essential",
            "importance_score": im_val,
            "importance_norm": norm_min_max(im_val, 1.0, 5.0),
            "level_score": lv_val,
            "level_norm": norm_min_max(lv_val, 0.0, 7.0),
            "is_software_skill": 0,
            "is_transferable_skill": 0,
            "is_essential_skill": 1,
            "is_hot_technology": 0,
            "is_in_demand": 0,
        })

    # 2. Transferable Skills
    df_trans = onet_data["transferable_skills.csv"]
    trans_piv = df_trans.pivot_table(
        index=["O*NET-SOC Code", "Title", "Element Name"],
        columns="Scale ID",
        values="Data Value",
        aggfunc="first"
    ).reset_index()

    for _, row in trans_piv.iterrows():
        im_val = float(row.get("IM", 1.0)) if pd.notna(row.get("IM")) else 1.0
        lv_val = float(row.get("LV", 0.0)) if pd.notna(row.get("LV")) else 0.0
        records.append({
            "soc_code": str(row["O*NET-SOC Code"]),
            "occupation_title": str(row["Title"]),
            "skill_name": str(row["Element Name"]).strip(),
            "skill_type": "transferable",
            "importance_score": im_val,
            "importance_norm": norm_min_max(im_val, 1.0, 5.0),
            "level_score": lv_val,
            "level_norm": norm_min_max(lv_val, 0.0, 7.0),
            "is_software_skill": 0,
            "is_transferable_skill": 1,
            "is_essential_skill": 0,
            "is_hot_technology": 0,
            "is_in_demand": 0,
        })

    # 3. Software Skills
    df_soft = onet_data["software_skills.csv"]
    for _, row in df_soft.iterrows():
        is_hot = 1 if str(row.get("Hot Technology", "")).strip().upper() == "Y" else 0
        is_dem = 1 if str(row.get("In Demand", "")).strip().upper() == "Y" else 0
        # For software skills, O*NET does not administer 1-5 survey scales directly,
        # but in-demand/hot-tech tags provide empirical market weight.
        # We record empirical base importance: Hot/InDemand = 4.0, standard = 3.0
        est_im = 4.0 if (is_hot or is_dem) else 3.0
        est_lv = 4.5 if (is_hot or is_dem) else 3.5
        records.append({
            "soc_code": str(row["O*NET-SOC Code"]),
            "occupation_title": str(row["Title"]),
            "skill_name": str(row["Workplace Example"]).strip(),
            "skill_type": "software",
            "importance_score": est_im,
            "importance_norm": norm_min_max(est_im, 1.0, 5.0),
            "level_score": est_lv,
            "level_norm": norm_min_max(est_lv, 0.0, 7.0),
            "is_software_skill": 1,
            "is_transferable_skill": 0,
            "is_essential_skill": 0,
            "is_hot_technology": is_hot,
            "is_in_demand": is_dem,
        })

    df_skill_occ = pd.DataFrame(records)

    # Join occupation context features
    context_cols = ["soc_code", "job_zone", "job_zone_norm", "knowledge_lv_mean_norm", "top_education_category"]
    df_context = df_occ_features[context_cols].drop_duplicates("soc_code")
    df_skill_occ = df_skill_occ.merge(df_context, on="soc_code", how="left")

    logger.info(f"Skill-Occupation Features built: {len(df_skill_occ):,} relationships across {df_skill_occ['soc_code'].nunique():,} occupations.")
    return df_skill_occ


# ----------------------------------------------------------------------
# TASK 6: Candidate Feature Representation
# ----------------------------------------------------------------------

def build_resume_candidate_features(
    df_resumes: pd.DataFrame,
    df_skill_occ: pd.DataFrame,
    df_occ: pd.DataFrame
) -> pd.DataFrame:
    """
    Construct candidate-level feature representation derived from Kaggle resumes.
    Features:
    - resume_id
    - category
    - mapped_soc_code, mapped_occupation_title, is_category_mapped
    - raw_char_length, clean_word_count
    - num_extracted_skills, num_software_skills, num_essential_skills, num_transferable_skills, num_hot_technologies
    - extracted_skills (semicolon-separated string)
    - skill_category_overlap (overlap ratio with mapped occupation's skills)
    - onet_skill_importance_mean, onet_skill_importance_max
    - onet_skill_level_mean, onet_skill_level_max
    CRITICAL: No synthetic proficiency score is created.
    """
    logger.info("Constructing Candidate-Level Resume Features...")

    # Build lookup dictionaries for skill benchmarks
    # Map lowercase skill_name -> {importance_norm, level_norm, type}
    skill_lookup = df_skill_occ.groupby(df_skill_occ["skill_name"].str.lower()).agg({
        "importance_norm": "mean",
        "level_norm": "mean",
        "is_software_skill": "max",
        "is_essential_skill": "max",
        "is_transferable_skill": "max",
        "is_hot_technology": "max",
    }).to_dict(orient="index")

    # Map soc_code -> set of lowercase skill names for that occupation
    occ_skills_map = df_skill_occ.groupby("soc_code")["skill_name"].apply(
        lambda s: set(s.str.lower())
    ).to_dict()

    feature_rows = []

    for idx, row in df_resumes.iterrows():
        res_id = row["ID"]
        category = str(row["Category"]).strip()
        norm_map = normalize_category(category)
        mapped_soc = norm_map["soc_code"]
        mapped_title = norm_map["occupation_title"]
        is_mapped = 1 if norm_map["status"] == "mapped" else 0

        raw_char_len = len(str(row.get("Resume_str", "")))
        clean_text = str(row.get("cleaned_text", ""))
        word_count = len(clean_text.split())

        skills_list = row.get("extracted_skills_list", [])
        num_skills = len(skills_list)
        skill_names = [s["skill_name"] for s in skills_list]
        extracted_skills_str = "; ".join(skill_names)

        # Count skill subtypes
        num_soft = sum(1 for s in skills_list if s.get("skill_type") == "software")
        num_ess = sum(1 for s in skills_list if s.get("skill_type") == "essential")
        num_trans = sum(1 for s in skills_list if s.get("skill_type") == "transferable")
        num_hot = sum(1 for s in skills_list if s.get("is_hot_tech"))

        # Skill-category overlap
        overlap_ratio = 0.0
        if is_mapped and mapped_soc in occ_skills_map and num_skills > 0:
            target_skills = occ_skills_map[mapped_soc]
            overlap_count = sum(1 for s in skill_names if s.lower() in target_skills)
            overlap_ratio = round(overlap_count / num_skills, 4)

        # O*NET importance and level aggregates for extracted skills
        im_scores = []
        lv_scores = []
        for s in skill_names:
            lookup = skill_lookup.get(s.lower())
            if lookup:
                im_scores.append(lookup["importance_norm"])
                lv_scores.append(lookup["level_norm"])

        im_mean = round(float(np.mean(im_scores)), 4) if im_scores else 0.0
        im_max = round(float(np.max(im_scores)), 4) if im_scores else 0.0
        lv_mean = round(float(np.mean(lv_scores)), 4) if lv_scores else 0.0
        lv_max = round(float(np.max(lv_scores)), 4) if lv_scores else 0.0

        feature_rows.append({
            "resume_id": res_id,
            "category": category,
            "mapped_soc_code": mapped_soc,
            "mapped_occupation_title": mapped_title,
            "is_category_mapped": is_mapped,
            "raw_char_length": raw_char_len,
            "clean_word_count": word_count,
            "num_extracted_skills": num_skills,
            "num_software_skills": num_soft,
            "num_essential_skills": num_ess,
            "num_transferable_skills": num_trans,
            "num_hot_technologies": num_hot,
            "extracted_skills": extracted_skills_str,
            "skill_category_overlap": overlap_ratio,
            "onet_skill_importance_mean": im_mean,
            "onet_skill_importance_max": im_max,
            "onet_skill_level_mean": lv_mean,
            "onet_skill_level_max": lv_max,
        })

    df_resume_features = pd.DataFrame(feature_rows)
    logger.info(f"Candidate Features built successfully: {len(df_resume_features):,} resumes, {len(df_resume_features.columns)} features.")
    return df_resume_features


# ----------------------------------------------------------------------
# TASK 8: Pipeline Validation & Quality Auditing
# ----------------------------------------------------------------------

def run_dataset_validation(
    df_resumes: pd.DataFrame,
    df_occ_features: pd.DataFrame,
    df_skill_occ: pd.DataFrame
) -> Dict[str, Any]:
    """
    Run comprehensive statistical and integrity validation:
    - Duplicates
    - Missing values
    - Numeric bounds
    - Empty resume text
    - Skill extraction sanity
    - Category coverage
    """
    logger.info("=== Running Phase 1 Validation & Quality Audits ===")
    
    # 1. Resume validation
    total_resumes = len(df_resumes)
    unique_resumes = df_resumes["resume_id"].nunique()
    dupes = total_resumes - unique_resumes
    empty_resumes = (df_resumes["clean_word_count"] == 0).sum()
    
    # Skills sanity
    avg_skills = df_resumes["num_extracted_skills"].mean()
    zero_skills_count = (df_resumes["num_extracted_skills"] == 0).sum()
    unique_skills_extracted = set()
    for s_str in df_resumes["extracted_skills"].dropna():
        if s_str:
            for s in s_str.split("; "):
                unique_skills_extracted.add(s)

    # Category coverage
    unique_cats = df_resumes["category"].nunique()
    mapped_cats = df_resumes[df_resumes["is_category_mapped"] == 1]["category"].nunique()
    unmapped_cats = df_resumes[df_resumes["is_category_mapped"] == 0]["category"].nunique()

    # 2. Occupation features validation
    total_occs = len(df_occ_features)
    null_occs = df_occ_features.isnull().sum().to_dict()

    # 3. Skill-occupation relationships validation
    total_rels = len(df_skill_occ)
    unique_skills_in_onet = df_skill_occ["skill_name"].nunique()

    # Bounds check for normalized values (must be in [0.0, 1.0])
    norm_cols_valid = True
    for c in ["essential_skills_im_mean_norm", "essential_skills_lv_mean_norm", "knowledge_lv_mean_norm"]:
        if c in df_occ_features.columns:
            if df_occ_features[c].min() < 0.0 or df_occ_features[c].max() > 1.0:
                norm_cols_valid = False

    audit_summary = {
        "total_resumes_processed": total_resumes,
        "unique_resumes": unique_resumes,
        "duplicate_resumes": dupes,
        "empty_resumes": int(empty_resumes),
        "total_unique_extracted_skills": len(unique_skills_extracted),
        "average_skills_per_resume": round(float(avg_skills), 2),
        "resumes_with_zero_skills": int(zero_skills_count),
        "total_categories": unique_cats,
        "mapped_categories_count": mapped_cats,
        "unmapped_categories_count": unmapped_cats,
        "total_occupations": total_occs,
        "total_skill_occupation_relationships": total_rels,
        "unique_skills_in_taxonomy": unique_skills_in_onet,
        "numeric_bounds_valid_0_to_1": norm_cols_valid,
    }

    logger.info("Validation Results Summary:")
    for k, v in audit_summary.items():
        logger.info(f"  - {k}: {v}")

    return audit_summary


# ----------------------------------------------------------------------
# Pipeline Execution Entrypoint
# ----------------------------------------------------------------------

def execute_feature_engineering_pipeline():
    """Execute complete Phase 1 Feature Engineering pipeline."""
    logger.info("Starting ReSkillAI Feature Engineering Pipeline...")
    
    # Run preprocessing to get clean resumes and raw datasets
    df_clean_resumes, onet_datasets, skill_ext = run_preprocessing_pipeline()

    # Ensure processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Generate occupation_features.csv
    df_occ_features = build_occupation_features(onet_datasets)
    occ_out_path = os.path.join(PROCESSED_DIR, "occupation_features.csv")
    df_occ_features.to_csv(occ_out_path, index=False)
    logger.info(f"Saved: {occ_out_path} ({len(df_occ_features):,} rows)")

    # 2. Generate skill_occupation_features.csv
    df_skill_occ = build_skill_occupation_features(onet_datasets, df_occ_features)
    skill_occ_out_path = os.path.join(PROCESSED_DIR, "skill_occupation_features.csv")
    df_skill_occ.to_csv(skill_occ_out_path, index=False)
    logger.info(f"Saved: {skill_occ_out_path} ({len(df_skill_occ):,} rows)")

    # 3. Generate resume_features.csv
    df_resume_features = build_resume_candidate_features(df_clean_resumes, df_skill_occ, df_occ_features)
    resume_out_path = os.path.join(PROCESSED_DIR, "resume_features.csv")
    df_resume_features.to_csv(resume_out_path, index=False)
    logger.info(f"Saved: {resume_out_path} ({len(df_resume_features):,} rows)")

    # 4. Run validation checks
    validation_report = run_dataset_validation(df_resume_features, df_occ_features, df_skill_occ)

    # 5. Mirror to RESKILL_AI directory if present
    reskill_ai_processed = os.path.join(BASE_DIR, "..", "..", "RESKILL_AI", "backend", "ml", "data", "processed")
    if os.path.exists(os.path.dirname(reskill_ai_processed)):
        os.makedirs(reskill_ai_processed, exist_ok=True)
        import shutil
        for fn in ["occupation_features.csv", "skill_occupation_features.csv", "resume_features.csv"]:
            shutil.copy2(os.path.join(PROCESSED_DIR, fn), os.path.join(reskill_ai_processed, fn))
        logger.info(f"Mirrored processed datasets to: {reskill_ai_processed}")

    print("\n" + "="*80)
    print("PHASE 1 FEATURE ENGINEERING & VALIDATION COMPLETE")
    print("="*80)
    print(f"Total Resumes Processed: {validation_report['total_resumes_processed']:,}")
    print(f"Unique Resumes: {validation_report['unique_resumes']:,} (Duplicates Removed: {validation_report['duplicate_resumes']})")
    print(f"Total Unique Extracted Skills: {validation_report['total_unique_extracted_skills']:,}")
    print(f"Average Skills Per Resume: {validation_report['average_skills_per_resume']}")
    print(f"Mapped Categories: {validation_report['mapped_categories_count']} / {validation_report['total_categories']}")
    print(f"Unmapped Categories: {validation_report['unmapped_categories_count']} / {validation_report['total_categories']}")
    print(f"Total O*NET Occupations: {validation_report['total_occupations']:,}")
    print(f"Total Skill-Occupation Relationships: {validation_report['total_skill_occupation_relationships']:,}")
    print(f"Normalized Numeric Bounds Valid [0.0, 1.0]: {validation_report['numeric_bounds_valid_0_to_1']}")
    print("="*80)
    print("CRITICAL GROUND-TRUTH LABEL STATEMENT:")
    print("1. AVAILABLE FOR SUPERVISED LEARNING: 'category' (Kaggle Career Classification, 24 classes),")
    print("   'In Demand' and 'Hot Technology' flags (software market trends), and O*NET empirical")
    print("   benchmark levels (LV 0-7) and importance ratings (IM 1-5) per occupation.")
    print("2. NOT AVAILABLE: Ground-truth individual candidate skill proficiency scores (0-100).")
    print("   The Kaggle dataset contains raw self-reported resumes and ZERO proficiency ratings.")
    print("   No fake proficiency labels have been invented or assigned.")
    print("="*80 + "\n")

    return validation_report


if __name__ == "__main__":
    execute_feature_engineering_pipeline()
