# ReSkillAI — Machine Learning Pipeline: Phase 1
## Dataset Preprocessing & Feature Engineering

This directory contains the independent, modular machine learning pipeline for **ReSkillAI Phase 1**.

> **Note on Application Isolation:**  
> This ML pipeline operates independently from the ReSkillAI production application. It does not modify existing frontend components, backend FastAPI endpoints, database schemas, authentication, or intelligence engines.

---

## 1. Directory Structure

```
backend/ml/
├── data/
│   ├── raw/
│   │   ├── onet/                   # 14 raw O*NET 31.0 CSV files (read-only)
│   │   └── kaggle/                 # Resume.csv (2,484 resumes, read-only)
│   └── processed/
│       ├── occupation_features.csv          # 1,016 occupations with 43 features
│       ├── skill_occupation_features.csv    # 63,671 pairwise relationship records
│       └── resume_features.csv              # 2,482 candidate feature records
├── preprocess.py                   # Loading, cleaning, deduplication, skill extraction
├── feature_engineering.py          # O*NET & candidate feature tables, validation audits
├── dataset_schema.md               # Complete feature dictionary & lineage documentation
├── DATASET_AUDIT.md                # Comprehensive data audit report
└── README.md                       # This documentation file
```

---

## 2. Pipeline Execution Instructions

### Prerequisites
The pipeline runs on Python 3.10+ and requires `pandas` and `numpy`:
```powershell
pip install pandas numpy
```

### Running Preprocessing Only
To test data loading, text cleaning, deduplication, and deterministic skill extraction:
```powershell
python backend/ml/preprocess.py
```

### Running Full Feature Engineering & Validation Pipeline
To construct all three processed datasets and execute validation audits:
```powershell
python backend/ml/feature_engineering.py
```

---

## 3. Phase 1 Validation & Quality Metrics

The automated validation suite (`feature_engineering.py`) enforces strict integrity checks:

| Metric | Measured Value | Quality Evaluation |
|---|---|---|
| **Total Resumes Processed** | `2,484` raw resumes | Complete ingest |
| **Unique Resumes Retained** | `2,482` | `2` duplicates identified & purged |
| **Duplicate Records Remaining** | `0` | Zero duplicate resumes |
| **Total Unique Extracted Skills** | `301` | High vocational diversity |
| **Average Skills per Resume** | `3.03` skills | Non-trivial extraction |
| **Resumes with Extracted Skills** | `2,176` (87.7%) | Strong signal retention |
| **Mapped Categories** | `17 / 24` | 1-to-1 exact SOC mapping |
| **Unmapped Categories** | `7 / 24` | Safely marked without fabrication |
| **Total O*NET Occupations** | `1,016` | Complete 2026 SOC coverage |
| **Skill-Occupation Relationships** | `63,671` | High-density competency graph |
| **Numeric Normalization Bounds** | All $\in [0.0, 1.0]$ | Bounds verified mathematically |

---

## 4. Critical Statement on Supervised Learning Labels

### What Labels ARE Available for Supervised ML:
1. **`category` (Career Classification):** Discrete multiclass label spanning 24 industry sectors in `resume_features.csv`.
2. **`is_hot_technology` & `is_in_demand`:** Market relevance flags in `skill_occupation_features.csv`.
3. **`importance_score` & `level_score`:** Empirical occupational benchmarks from O*NET survey instruments.

### What Labels ARE NOT Available:
> [!IMPORTANT]
> **No Ground-Truth Candidate Skill Proficiency Scores:**  
> Neither the Kaggle `Resume.csv` dataset nor the O*NET database provides ground-truth individual skill proficiency scores (e.g. 0–100 or 1–5 measured scores for individual applicants).  
> Resumes represent self-reported claims rather than verified skill competencies.  
> **Under no circumstances should synthetic proficiency scores be fabricated or claimed as ground truth.** Individual skill proficiency in ReSkillAI is computed through multi-evidence synthesis (resume scan depth + assessment answers + project complexity) anchored against O*NET benchmark levels.

---

*Phase 1 Pipeline complete. No models trained; raw datasets unmodified.*
