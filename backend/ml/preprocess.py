# -*- coding: utf-8 -*-
"""
ReSkillAI — Machine Learning Pipeline: Preprocessing Module
Phase 1: Dataset Preprocessing & Skill Extraction

This module is completely separate and modular from the production application.
It loads raw Kaggle and O*NET datasets, performs text cleaning, deduplication,
deterministic skill extraction, and occupation category normalization.
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReSkillAI.ML.Preprocess")

# Base directory resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
ONET_RAW_DIR = os.path.join(RAW_DIR, "onet")
KAGGLE_RAW_DIR = os.path.join(RAW_DIR, "kaggle")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# Fallback paths if raw datasets are located in parent directory
ROOT_FALLBACK_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# ----------------------------------------------------------------------
# TASK 1: Safe Dataset Loading
# ----------------------------------------------------------------------

def resolve_file_path(filename: str, subfolder: str = "onet") -> str:
    """Resolve file path across standard raw dir and root fallback."""
    candidate1 = os.path.join(RAW_DIR, subfolder, filename)
    if os.path.exists(candidate1):
        return candidate1
    candidate2 = os.path.join(BASE_DIR, "data", "raw", subfolder, filename)
    if os.path.exists(candidate2):
        return candidate2
    candidate3 = os.path.join(ROOT_FALLBACK_DIR, filename)
    if os.path.exists(candidate3):
        return candidate3
    raise FileNotFoundError(f"Could not locate dataset '{filename}' in raw or fallback paths.")


def load_csv_safe(file_path: str) -> pd.DataFrame:
    """Load a CSV file with robust multi-encoding fallback."""
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    last_err = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, low_memory=False)
            return df
        except UnicodeDecodeError as e:
            last_err = e
            continue
        except Exception as e:
            raise e
    raise ValueError(f"Failed to decode '{file_path}' across encodings: {last_err}")


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Load all required O*NET and Kaggle datasets safely without modifying raw files."""
    datasets = {}
    
    # 1. Kaggle Resume Dataset
    resume_path = resolve_file_path("Resume.csv", subfolder="kaggle")
    df_resume = load_csv_safe(resume_path)
    datasets["Resume.csv"] = df_resume
    logger.info(f"Loaded 'Resume.csv': {len(df_resume):,} rows, {len(df_resume.columns)} cols. Columns: {list(df_resume.columns)}")

    # 2. O*NET Datasets
    onet_filenames = [
        "occupation_data.csv",
        "job_titles.csv",
        "related_occupations.csv",
        "essential_skills.csv",
        "software_skills.csv",
        "transferable_skills.csv",
        "knowledge.csv",
        "abilities.csv",
        "education.csv",
        "job_zones.csv",
        "training_and_experience.csv",
        "task_statements.csv",
        "task_ratings.csv",
        "work_activities.csv",
    ]

    for fname in onet_filenames:
        fpath = resolve_file_path(fname, subfolder="onet")
        df = load_csv_safe(fpath)
        datasets[fname] = df
        logger.info(f"Loaded '{fname}': {len(df):,} rows, {len(df.columns)} cols.")

    return datasets


# ----------------------------------------------------------------------
# TASK 2: Resume Preprocessing & Deduplication
# ----------------------------------------------------------------------

def clean_resume_text(text: Any) -> Tuple[str, str]:
    """
    Clean and normalize resume text:
    - Uses Resume_str as primary text
    - Strips HTML tags and entities
    - Normalizes whitespace
    - Generates lowercase normalized text for matching
    - Preserves case-preserved cleaned text separately
    - Retains technical terms (Python, SQL, AWS, React, etc.)
    """
    if not isinstance(text, str):
        return "", ""
    
    # Remove HTML tags if present in Resume_str
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Remove common HTML entities
    cleaned = re.sub(r"&(?:nbsp|amp|quot|lt|gt|#39|#x27);", " ", cleaned)
    cleaned = re.sub(r"&[a-zA-Z0-9#]+;", " ", cleaned)
    # Collapse multiple spaces and horizontal tabs
    cleaned = re.sub(r"[ \t\r\f\v]+", " ", cleaned)
    # Collapse multiple consecutive newlines
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)
    cleaned = cleaned.strip()

    # Normalized text for matching and deduplication
    normalized = cleaned.lower()
    return cleaned, normalized


def preprocess_resumes(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Preprocess Resume.csv:
    - Clean text
    - Drop duplicates based on normalized text
    - Preserve original ID and Category
    """
    df = df_raw.copy()
    initial_count = len(df)

    # Clean text
    results = [clean_resume_text(t) for t in df["Resume_str"]]
    df["cleaned_text"] = [r[0] for r in results]
    df["normalized_text"] = [r[1] for r in results]

    # Deduplicate based on normalized text while preserving first occurrence
    df_dedup = df.drop_duplicates(subset=["normalized_text"]).copy()
    duplicates_removed = initial_count - len(df_dedup)

    logger.info(f"Resume Preprocessing: {initial_count:,} raw resumes -> {len(df_dedup):,} unique resumes ({duplicates_removed} duplicates removed).")
    return df_dedup, duplicates_removed


# ----------------------------------------------------------------------
# TASK 4: Occupation & Category Normalization
# ----------------------------------------------------------------------

# Kaggle Category to O*NET Occupation mapping dictionary
# Explicitly distinguishing mapped vs unmapped categories
CATEGORY_TO_ONET_MAPPING: Dict[str, Dict[str, Any]] = {
    "ACCOUNTANT": {
        "status": "mapped",
        "soc_code": "13-2011.00",
        "occupation_title": "Accountants and Auditors",
        "rationale": "Direct 1-to-1 match with standard financial auditing and accounting occupation.",
    },
    "CHEF": {
        "status": "mapped",
        "soc_code": "35-1011.00",
        "occupation_title": "Chefs and Head Cooks",
        "rationale": "Direct 1-to-1 match with culinary leadership and head cook occupation.",
    },
    "HR": {
        "status": "mapped",
        "soc_code": "13-1071.00",
        "occupation_title": "Human Resources Specialists",
        "rationale": "Direct 1-to-1 match with human resources recruitment, onboarding, and employee relations.",
    },
    "PUBLIC-RELATIONS": {
        "status": "mapped",
        "soc_code": "27-3031.00",
        "occupation_title": "Public Relations Specialists",
        "rationale": "Direct 1-to-1 match with public communications and media relations specialists.",
    },
    "INFORMATION-TECHNOLOGY": {
        "status": "mapped",
        "soc_code": "15-1299.09",
        "occupation_title": "Information Technology Project Managers",
        "rationale": "Representative IT technical leadership and systems administration occupation.",
    },
    "FITNESS": {
        "status": "mapped",
        "soc_code": "39-9031.00",
        "occupation_title": "Exercise Trainers and Group Fitness Instructors",
        "rationale": "Direct 1-to-1 match with personal fitness training and instruction.",
    },
    "CONSTRUCTION": {
        "status": "mapped",
        "soc_code": "11-9021.00",
        "occupation_title": "Construction Managers",
        "rationale": "Direct match with construction project management and site oversight.",
    },
    "CONSULTANT": {
        "status": "mapped",
        "soc_code": "13-1111.00",
        "occupation_title": "Management Analysts",
        "rationale": "Standard O*NET-SOC equivalent for business and management consultants.",
    },
    "DESIGNER": {
        "status": "mapped",
        "soc_code": "27-1024.00",
        "occupation_title": "Graphic Designers",
        "rationale": "Canonical design occupation covering visual design, UI layout, and media design.",
    },
    "SALES": {
        "status": "mapped",
        "soc_code": "41-3091.00",
        "occupation_title": "Sales Representatives of Services, Except Advertising, Insurance, Financial Services, and Travel",
        "rationale": "General commercial sales and business client management.",
    },
    "FINANCE": {
        "status": "mapped",
        "soc_code": "13-2051.00",
        "occupation_title": "Financial and Investment Analysts",
        "rationale": "Core financial modeling, investment research, and economic analysis.",
    },
    "BANKING": {
        "status": "mapped",
        "soc_code": "13-2072.00",
        "occupation_title": "Loan Officers",
        "rationale": "Commercial and retail banking lending and credit evaluation.",
    },
    "TEACHER": {
        "status": "mapped",
        "soc_code": "25-2031.00",
        "occupation_title": "Secondary School Teachers, Except Special and Career/Technical Education",
        "rationale": "Representative pedagogy and classroom instructional occupation.",
    },
    "AGRICULTURE": {
        "status": "mapped",
        "soc_code": "11-9013.00",
        "occupation_title": "Farmers, Ranchers, and Other Agricultural Managers",
        "rationale": "Agricultural operational management and production oversight.",
    },
    "AVIATION": {
        "status": "mapped",
        "soc_code": "53-2012.00",
        "occupation_title": "Commercial Pilots",
        "rationale": "Civil and commercial aviation flight operations.",
    },
    "AUTOMOBILE": {
        "status": "mapped",
        "soc_code": "49-3023.00",
        "occupation_title": "Automotive Service Technicians and Mechanics",
        "rationale": "Automotive technical maintenance and vehicular diagnostics.",
    },
    "BUSINESS-DEVELOPMENT": {
        "status": "mapped",
        "soc_code": "11-2022.00",
        "occupation_title": "Sales Managers",
        "rationale": "Corporate commercial growth, account expansion, and client partnership leadership.",
    },
    # Unmapped categories (heterogeneous industries / ambiguous sectors / no 1-to-1 SOC)
    "ADVOCATE": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Polysemous term: in India/Commonwealth indicates trial lawyers (23-1011.00), in US covers patient advocates or legal assistants. Cannot assume without fabrication.",
    },
    "APPAREL": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Broad manufacturing and retail sector spanning fashion design (27-1022.00), sewing operators, and retail buyers.",
    },
    "ARTS": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Disparate umbrella category combining fine artists (27-1013.00), actors, musicians, and gallery directors.",
    },
    "BPO": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Business Process Outsourcing is a business operations outsourcing model, not a standard O*NET occupational code.",
    },
    "DIGITAL-MEDIA": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Cross-disciplinary digital domain covering content creation, SEO, video production, and social media.",
    },
    "ENGINEERING": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Broad super-family (Major SOC 17-2000) containing mechanical, electrical, civil, biomedical, and chemical disciplines.",
    },
    "HEALTHCARE": {
        "status": "unmapped",
        "soc_code": "unmapped",
        "occupation_title": "unmapped",
        "rationale": "Broad healthcare industry sector containing physicians, registered nurses, radiologists, and administrative executives.",
    },
}


def normalize_category(category: str) -> Dict[str, Any]:
    """Normalize Kaggle category to O*NET occupation mapping."""
    cat_upper = str(category).strip().upper()
    mapping = CATEGORY_TO_ONET_MAPPING.get(cat_upper)
    if mapping is None:
        return {
            "status": "unmapped",
            "soc_code": "unmapped",
            "occupation_title": "unmapped",
            "rationale": f"Unknown category '{category}'.",
        }
    return mapping


# ----------------------------------------------------------------------
# TASK 3: Deterministic Skill Extraction Engine
# ----------------------------------------------------------------------

class SkillExtractor:
    """
    Deterministic skill extraction layer utilizing O*NET skill taxonomy,
    software skills, and standardized industry technology vocabulary.
    Avoids naive substring false-positives via boundary checks and strict regex rules.
    """

    def __init__(self, onet_datasets: Dict[str, pd.DataFrame]):
        self.onet_datasets = onet_datasets
        self.skill_registry: Dict[str, Dict[str, Any]] = {}
        self._compiled_patterns: List[Tuple[str, re.Pattern, Dict[str, Any]]] = []
        self._build_skill_registry()

    def _build_skill_registry(self):
        """Construct unified skill vocabulary and compiled regexes."""
        
        # 1. O*NET Essential Skills (10 core foundation skills)
        df_ess = self.onet_datasets["essential_skills.csv"]
        for s in df_ess["Element Name"].dropna().unique():
            canonical = str(s).strip()
            self.skill_registry[canonical] = {
                "type": "essential",
                "canonical_name": canonical,
                "is_hot_tech": False,
                "is_in_demand": False,
                "regex": r"\b" + re.escape(canonical.lower()) + r"\b"
            }

        # 2. O*NET Transferable Skills (25 cross-functional skills)
        df_trans = self.onet_datasets["transferable_skills.csv"]
        for s in df_trans["Element Name"].dropna().unique():
            canonical = str(s).strip()
            self.skill_registry[canonical] = {
                "type": "transferable",
                "canonical_name": canonical,
                "is_hot_tech": False,
                "is_in_demand": False,
                "regex": r"\b" + re.escape(canonical.lower()) + r"\b"
            }

        # 3. O*NET Software Skills (High-frequency, In-Demand, Hot Technologies)
        df_soft = self.onet_datasets["software_skills.csv"]
        # Group software tools to aggregate Hot Tech and In Demand flags
        soft_agg = df_soft.groupby("Workplace Example").agg({
            "Hot Technology": lambda x: "Y" in x.values,
            "In Demand": lambda x: "Y" in x.values,
            "O*NET-SOC Code": "count"
        }).reset_index()

        # Disambiguate single-word common English nouns to prevent false positives
        generic_words_to_contextualize = {
            "chef": r"\b(?:chef\s+(?:devops|automate|software|tool|infra)|devops\s+chef)\b",
            "base": r"\b(?:openoffice\s+base|libreoffice\s+base)\b",
            "access": r"\b(?:microsoft\s+access|ms\s+access)\b",
            "word": r"\b(?:microsoft\s+word|ms\s+word)\b",
            "excel": r"\b(?:microsoft\s+excel|ms\s+excel|excel)\b",
            "project": r"\b(?:microsoft\s+project|ms\s+project)\b",
            "visio": r"\b(?:microsoft\s+visio|ms\s+visio)\b",
            "outlook": r"\b(?:microsoft\s+outlook|ms\s+outlook)\b",
            "teams": r"\b(?:microsoft\s+teams|ms\s+teams)\b",
            "spark": r"\b(?:apache\s+spark|spark)\b",
            "hive": r"\b(?:apache\s+hive|hive)\b",
            "storm": r"\b(?:apache\s+storm|storm)\b",
            "pig": r"\b(?:apache\s+pig|pig)\b",
            "hadoop": r"\b(?:apache\s+hadoop|hadoop)\b",
            "kafka": r"\b(?:apache\s+kafka|kafka)\b",
            "cassandra": r"\b(?:apache\s+cassandra|cassandra)\b",
        }

        # Specific programming languages with strict token boundaries
        special_language_patterns = {
            "C++": r"(?:\bc\+\+|\bc\s*plus\s*plus\b)",
            "C#": r"(?:\bc#|\bc\s*sharp\b)",
            "C": r"\b(?:c\s+programming|c\s+language)\b",
            "R": r"\b(?:r\s+programming|r\s+language|r\s+statistical|r\s+studio)\b",
            "Go": r"\b(?:golang|go\s+programming|go\s+language)\b",
            ".NET": r"(?:\b\.net\b|\bdotnet\b|\basp\.net\b)",
            "Node.js": r"\b(?:node\.js|nodejs|node\s+js)\b",
            "React": r"\b(?:react\.js|reactjs|react\s+native|react)\b",
            "Vue.js": r"\b(?:vue\.js|vuejs|vue)\b",
            "Angular": r"\b(?:angular\.js|angularjs|angular)\b",
            "AWS": r"\b(?:aws|amazon\s+web\s+services)\b",
            "GCP": r"\b(?:gcp|google\s+cloud\s+platform|google\s+cloud)\b",
            "Azure": r"\b(?:microsoft\s+azure|azure)\b",
            "FastAPI": r"\bfastapi\b",
            "SQL": r"\bsql\b",
            "NoSQL": r"\bnosql\b",
            "Git": r"\bgit\b",
            "GitHub": r"\bgithub\b",
            "GitLab": r"\bgitlab\b",
            "Docker": r"\bdocker\b",
            "Kubernetes": r"\b(?:kubernetes|k8s)\b",
            "Linux": r"\blinux\b",
            "Unix": r"\bunix\b",
            "Machine Learning": r"\b(?:machine\s+learning|ml)\b",
            "Deep Learning": r"\bdeep\s+learning\b",
            "Artificial Intelligence": r"\b(?:artificial\s+intelligence|ai)\b",
            "Natural Language Processing": r"\b(?:natural\s+language\s+processing|nlp)\b",
            "Computer Vision": r"\bcomputer\s+vision\b",
            "TensorFlow": r"\btensorflow\b",
            "PyTorch": r"\bpytorch\b",
            "Scikit-learn": r"\b(?:scikit-learn|sklearn)\b",
            "Pandas": r"\bpandas\b",
            "NumPy": r"\bnumpy\b",
            "Tableau": r"\btableau\b",
            "Power BI": r"\bpower\s*bi\b",
        }

        # Add explicit special patterns
        for name, pat in special_language_patterns.items():
            self.skill_registry[name] = {
                "type": "software",
                "canonical_name": name,
                "is_hot_tech": True,
                "is_in_demand": True,
                "regex": pat
            }

        # Add prominent software skills from O*NET (frequency >= 3 or Hot Tech / In Demand)
        for _, row in soft_agg.iterrows():
            tool_name = str(row["Workplace Example"]).strip()
            tool_lower = tool_name.lower()
            
            # Skip if already registered
            if tool_name in self.skill_registry or tool_lower in [k.lower() for k in self.skill_registry]:
                continue
            
            # Skip extremely long descriptive strings (> 35 chars) or single chars
            if len(tool_name) < 2 or len(tool_name) > 35:
                continue

            # Check contextualized generic words
            if tool_lower in generic_words_to_contextualize:
                pat = generic_words_to_contextualize[tool_lower]
            elif len(tool_name) <= 3:
                # Require explicit word boundary for short tools (e.g. PHP, AWK, SAS)
                pat = r"\b" + re.escape(tool_lower) + r"\b"
            else:
                pat = r"\b" + re.escape(tool_lower) + r"\b"

            # Filter out software tools that appear in very few occupations and aren't in demand
            if row["Hot Technology"] or row["In Demand"] or row["O*NET-SOC Code"] >= 3:
                self.skill_registry[tool_name] = {
                    "type": "software",
                    "canonical_name": tool_name,
                    "is_hot_tech": bool(row["Hot Technology"]),
                    "is_in_demand": bool(row["In Demand"]),
                    "regex": pat
                }

        # Compile all patterns for high-speed deterministic matching
        for skill_name, info in self.skill_registry.items():
            try:
                compiled = re.compile(info["regex"], re.IGNORECASE)
                self._compiled_patterns.append((skill_name, compiled, info))
            except re.error as e:
                logger.warning(f"Regex compilation failed for skill '{skill_name}': {e}")

        logger.info(f"Skill Registry compiled with {len(self._compiled_patterns):,} deterministic skill patterns.")

    def extract_skills(self, normalized_text: str) -> List[Dict[str, Any]]:
        """
        Extract matching skills from normalized resume text.
        Returns list of matched skill metadata dicts.
        """
        if not normalized_text:
            return []
        
        extracted = []
        for skill_name, pattern, info in self._compiled_patterns:
            if pattern.search(normalized_text):
                extracted.append({
                    "skill_name": info["canonical_name"],
                    "skill_type": info["type"],
                    "is_hot_tech": info["is_hot_tech"],
                    "is_in_demand": info["is_in_demand"],
                })
        return extracted


# ----------------------------------------------------------------------
# Pipeline Execution Entrypoint for Preprocessing
# ----------------------------------------------------------------------

def run_preprocessing_pipeline() -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], SkillExtractor]:
    """Execute complete Phase 1 preprocessing workflow."""
    logger.info("=== Starting ReSkillAI Dataset Preprocessing Pipeline ===")
    
    # 1. Load datasets
    datasets = load_all_datasets()
    
    # 2. Preprocess and deduplicate resumes
    df_resumes, dupes_removed = preprocess_resumes(datasets["Resume.csv"])
    
    # 3. Initialize deterministic skill extractor
    extractor = SkillExtractor(datasets)
    
    # 4. Extract skills for each resume
    logger.info("Extracting deterministic skills across all resumes...")
    extracted_results = []
    for idx, row in df_resumes.iterrows():
        skills = extractor.extract_skills(row["normalized_text"])
        extracted_results.append(skills)
    
    df_resumes["extracted_skills_list"] = extracted_results
    df_resumes["num_extracted_skills"] = [len(s) for s in extracted_results]
    df_resumes["extracted_skills_str"] = ["; ".join([item["skill_name"] for item in s]) for s in extracted_results]

    logger.info(f"Extraction complete. Total resumes: {len(df_resumes):,}. Average skills per resume: {df_resumes['num_extracted_skills'].mean():.2f}")
    
    return df_resumes, datasets, extractor


if __name__ == "__main__":
    df_clean_resumes, all_data, skill_ext = run_preprocessing_pipeline()
    print("Preprocessing completed successfully.")
