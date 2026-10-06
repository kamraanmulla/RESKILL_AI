# ReSkillAI — ML Dataset Schema & Feature Dictionary
**Phase 1: Dataset Preprocessing & Feature Engineering**

This document provides a comprehensive technical schema, feature definitions, transformation lineage, and data hygiene documentation for the machine learning datasets processed in Phase 1.

---

## 1. Pipeline Overview & Data Lineage

The ReSkillAI Machine Learning pipeline ingests raw, unverified data and anchors it against normative, empirical taxonomies from the U.S. Department of Labor:

```
[Raw Kaggle: Resume.csv] ──► [preprocess.py] ──► [feature_engineering.py] ──► resume_features.csv (2,482 rows)
                                    ▲                       ▲
                                    │                       │
[Raw O*NET: 14 CSV files] ──────────┴───────────────────────┴───────────────► occupation_features.csv (1,016 rows)
                                                                            ► skill_occupation_features.csv (63,671 rows)
```

---

## 2. Processed Dataset Schemas

### 2.1 `resume_features.csv`
- **Location:** `backend/ml/data/processed/resume_features.csv`
- **Source:** Kaggle Resume Dataset (`Resume.csv`), cross-referenced with O*NET skills and occupations.
- **Grain:** One row per unique candidate resume.
- **Total Records:** 2,482
- **Deduplication:** 2 duplicate records removed based on normalized text (`2,484 -> 2,482`).

| Column Name | Data Type | Description | Transformations / Derivations | Missing Handling |
|---|---|---|---|---|
| `resume_id` | `int64` | Original unique resume ID from Kaggle dataset. | Retained as-is. | None (0% null) |
| `category` | `string` | Original job category label (24 unique classes). | Case preserved. | None (0% null) |
| `mapped_soc_code` | `string` | Mapped standard O*NET-SOC identifier (e.g., `13-2011.00`) or `'unmapped'`. | Exact mapping dictionary lookup. | Filled `'unmapped'` |
| `mapped_occupation_title` | `string` | Standardized O*NET title or `'unmapped'`. | Canonical title from `occupation_data.csv`. | Filled `'unmapped'` |
| `is_category_mapped` | `int64` | Binary flag (`1` = mapped to specific SOC code, `0` = unmapped/heterogeneous). | Indicator based on mapping confidence. | Defaults to `0` |
| `raw_char_length` | `int64` | Total character length of original `Resume_str`. | String length computation. | `0` if empty |
| `clean_word_count` | `int64` | Word count of cleaned, stripped text. | Split on whitespace after HTML & entity stripping. | `0` if empty |
| `num_extracted_skills` | `int64` | Count of unique skills extracted from candidate resume. | Deterministic matching against O*NET + tech registry. | `0` if none |
| `num_software_skills` | `int64` | Count of extracted software, tools, and tech libraries. | Subset where `skill_type == 'software'`. | `0` if none |
| `num_essential_skills` | `int64` | Count of extracted core foundational skills (e.g. Critical Thinking, Mathematics). | Subset where `skill_type == 'essential'`. | `0` if none |
| `num_transferable_skills` | `int64` | Count of extracted cross-functional competencies (e.g. Negotiation, Troubleshooting). | Subset where `skill_type == 'transferable'`. | `0` if none |
| `num_hot_technologies` | `int64` | Count of tools tagged as "Hot Technology" by O*NET / market standards. | Tagged indicator count. | `0` if none |
| `extracted_skills` | `string` | Semicolon-delimited list of canonical extracted skill names. | Semicolon join of matched skill names. | Empty string if none |
| `skill_category_overlap` | `float64` | Ratio of candidate's extracted skills that belong to the target mapped occupation's skill profile (`0.0` to `1.0`). | Jaccard overlap: $\frac{\|S_{\text{resume}} \cap S_{\text{occupation}}\|}{\|S_{\text{resume}}\|}$. | `0.0` if unmapped |
| `onet_skill_importance_mean` | `float64` | Average normalized O*NET importance rating across candidate's extracted skills (`0.0` to `1.0`). | Average normalized `IM` score from O*NET taxonomy. | `0.0` if no skills |
| `onet_skill_importance_max` | `float64` | Maximum normalized O*NET importance rating among candidate's extracted skills. | Max normalized `IM` score. | `0.0` if no skills |
| `onet_skill_level_mean` | `float64` | Average normalized O*NET required level across candidate's extracted skills (`0.0` to `1.0`). | Average normalized `LV` score from O*NET taxonomy. | `0.0` if no skills |
| `onet_skill_level_max` | `float64` | Maximum normalized O*NET required level among candidate's extracted skills. | Max normalized `LV` score. | `0.0` if no skills |

---

### 2.2 `occupation_features.csv`
- **Location:** `backend/ml/data/processed/occupation_features.csv`
- **Source:** O*NET 31.0 Database (`occupation_data.csv`, `job_zones.csv`, `essential_skills.csv`, `transferable_skills.csv`, `software_skills.csv`, `knowledge.csv`, `abilities.csv`, `work_activities.csv`, `task_statements.csv`, `task_ratings.csv`, `education.csv`, `related_occupations.csv`).
- **Grain:** One row per standard O*NET occupation.
- **Total Records:** 1,016
- **Features:** 43 aggregated and normalized features.

| Column Name | Data Type | Scale / Range | Description |
|---|---|---|---|
| `soc_code` | `string` | Primary Key | Standard Occupational Classification identifier (e.g., `15-1252.00`). |
| `occupation_title` | `string` | Text | Official occupational title. |
| `job_zone` | `float64` | `1.0` - `5.0` | Preparation tier (Zone 1: Little/No Preparation, Zone 5: Extensive). |
| `job_zone_norm` | `float64` | `0.0` - `1.0` | Normalized Job Zone: $\frac{\text{Zone} - 1}{4.0}$. |
| `num_essential_skills` | `int64` | `0` - `10` | Number of core foundation skills rated. |
| `essential_skills_im_mean` | `float64` | `1.0` - `5.0` | Average raw Importance rating across essential skills. |
| `essential_skills_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized Importance: $\frac{\text{IM} - 1.0}{4.0}$. |
| `essential_skills_lv_mean` | `float64` | `0.0` - `7.0` | Average raw required Level rating across essential skills. |
| `essential_skills_lv_mean_norm` | `float64` | `0.0` - `1.0` | Normalized Level: $\frac{\text{LV}}{7.0}$. |
| `num_transferable_skills` | `int64` | `0` - `25` | Number of cross-functional skills rated. |
| `transferable_skills_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Importance for transferable skills. |
| `transferable_skills_lv_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Level for transferable skills. |
| `num_software_skills` | `int64` | $\ge 0$ | Total number of distinct software tools and technical commodities. |
| `num_hot_technologies` | `int64` | $\ge 0$ | Software tools flagged as in-demand Hot Technologies. |
| `num_in_demand_software` | `int64` | $\ge 0$ | Software tools flagged as high employer demand. |
| `num_knowledge_domains` | `int64` | `0` - `33` | Number of domain knowledge areas rated. |
| `knowledge_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Importance across 33 knowledge domains. |
| `knowledge_lv_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Level across 33 knowledge domains. |
| `num_abilities` | `int64` | `0` - `52` | Number of cognitive and physical human abilities rated. |
| `abilities_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Importance across 52 abilities. |
| `abilities_lv_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Level across 52 abilities. |
| `num_work_activities` | `int64` | `0` - `41` | Number of Generalized Work Activities (GWAs) rated. |
| `work_activities_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Importance across work activities. |
| `work_activities_lv_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average Level across work activities. |
| `num_task_statements` | `int64` | $\ge 0$ | Count of concrete occupational daily duty statements. |
| `task_im_mean_norm` | `float64` | `0.0` - `1.0` | Normalized average importance of daily job tasks. |
| `top_education_category` | `string` | Categorical | Highest percentage educational attainment level reported by incumbents. |
| `top_education_percentage_norm`| `float64` | `0.0` - `1.0` | Percentage of incumbents possessing `top_education_category` ($\div 100$). |
| `num_related_occupations` | `int64` | $\ge 0$ | Count of related occupational transition pathways. |

---

### 2.3 `skill_occupation_features.csv`
- **Location:** `backend/ml/data/processed/skill_occupation_features.csv`
- **Source:** Join of `essential_skills.csv`, `transferable_skills.csv`, `software_skills.csv`, and contextual features from `occupation_features.csv`.
- **Grain:** One row per unique `(O*NET-SOC Code, skill_name)` pair.
- **Total Records:** 63,671
- **Occupations Covered:** 923 distinct occupations.

| Column Name | Data Type | Description |
|---|---|---|
| `soc_code` | `string` | Standard Occupational Classification code. |
| `occupation_title` | `string` | Official occupation title. |
| `skill_name` | `string` | Name of the skill, competency, or software tool. |
| `skill_type` | `string` | Skill classification: `'essential'`, `'transferable'`, or `'software'`. |
| `importance_score` | `float64` | Raw importance score (`1.0` to `5.0`). |
| `importance_norm` | `float64` | Normalized importance score in `[0.0, 1.0]`. |
| `level_score` | `float64` | Raw required level score (`0.0` to `7.0`). |
| `level_norm` | `float64` | Normalized required level score in `[0.0, 1.0]`. |
| `is_software_skill` | `int64` | Binary indicator (`1` if software tool, `0` otherwise). |
| `is_transferable_skill` | `int64` | Binary indicator (`1` if transferable/cross-functional skill). |
| `is_essential_skill` | `int64` | Binary indicator (`1` if core foundation skill). |
| `is_hot_technology` | `int64` | Binary indicator (`1` if tagged as Hot Technology). |
| `is_in_demand` | `int64` | Binary indicator (`1` if tagged as In Demand). |
| `job_zone` | `float64` | Contextual job preparation zone (`1.0` - `5.0`). |
| `job_zone_norm` | `float64` | Contextual normalized job preparation zone (`0.0` - `1.0`). |
| `knowledge_lv_mean_norm` | `float64` | Contextual average required knowledge level of occupation. |
| `top_education_category` | `string` | Contextual typical education requirement for occupation. |

---

## 3. Kaggle Category to O*NET Normalization Table

Out of the 24 Kaggle resume categories, **17 categories** possess unambiguous 1-to-1 mappings to standard O*NET-SOC occupations. **7 categories** represent heterogeneous sectors, multi-role industries, or polysemous terms and are strictly marked as `unmapped` without fabrication:

| Kaggle Category | Status | Mapped SOC Code | Mapped O*NET Title | Mapping Rationale |
|---|---|---|---|---|
| `ACCOUNTANT` | `mapped` | `13-2011.00` | Accountants and Auditors | Direct 1-to-1 occupational correspondence. |
| `CHEF` | `mapped` | `35-1011.00` | Chefs and Head Cooks | Direct 1-to-1 occupational correspondence. |
| `HR` | `mapped` | `13-1071.00` | Human Resources Specialists | Direct 1-to-1 occupational correspondence. |
| `PUBLIC-RELATIONS` | `mapped` | `27-3031.00` | Public Relations Specialists | Direct 1-to-1 occupational correspondence. |
| `INFORMATION-TECHNOLOGY`| `mapped` | `15-1299.09` | Information Technology Project Managers | Canonical technical management occupation. |
| `FITNESS` | `mapped` | `39-9031.00` | Exercise Trainers and Group Fitness Instructors | Direct 1-to-1 correspondence. |
| `CONSTRUCTION` | `mapped` | `11-9021.00` | Construction Managers | Direct occupational leadership match. |
| `CONSULTANT` | `mapped` | `13-1111.00` | Management Analysts | Standard SOC equivalent for business advisory. |
| `DESIGNER` | `mapped` | `27-1024.00` | Graphic Designers | Canonical visual and interface design role. |
| `SALES` | `mapped` | `41-3091.00` | Sales Representatives of Services | Canonical commercial sales role. |
| `FINANCE` | `mapped` | `13-2051.00` | Financial and Investment Analysts | Core financial modeling and valuation. |
| `BANKING` | `mapped` | `13-2072.00` | Loan Officers | Retail and commercial credit underwriting. |
| `TEACHER` | `mapped` | `25-2031.00` | Secondary School Teachers | Representative pedagogy role. |
| `AGRICULTURE` | `mapped` | `11-9013.00` | Farmers, Ranchers, and Other Agricultural Managers | Agricultural operational management. |
| `AVIATION` | `mapped` | `53-2012.00` | Commercial Pilots | Civil and commercial flight operations. |
| `AUTOMOBILE` | `mapped` | `49-3023.00` | Automotive Service Technicians and Mechanics | Vehicular diagnostics and repair. |
| `BUSINESS-DEVELOPMENT` | `mapped` | `11-2022.00` | Sales Managers | Commercial growth and business development. |
| `ADVOCATE` | `unmapped` | `unmapped` | `unmapped` | Polysemous (legal lawyers vs patient advocates). |
| `APPAREL` | `unmapped` | `unmapped` | `unmapped` | Umbrella sector (designers, patternmakers, buyers). |
| `ARTS` | `unmapped` | `unmapped` | `unmapped` | Umbrella sector (painters, actors, sculptors). |
| `BPO` | `unmapped` | `unmapped` | `unmapped` | Business process outsourcing business model, not a SOC occupation. |
| `DIGITAL-MEDIA` | `unmapped` | `unmapped` | `unmapped` | Cross-disciplinary digital sector. |
| `ENGINEERING` | `unmapped` | `unmapped` | `unmapped` | Broad super-family (17-2000) spanning civil, mech, elec, chem. |
| `HEALTHCARE` | `unmapped` | `unmapped` | `unmapped` | Umbrella sector spanning clinicians, nurses, executives. |

---

## 4. Ground Truth Labels: Available vs Unavailable

### Available Ground Truth Labels (Supervised Learning Targets)
1. **`category` (Career Classification):** Discrete multiclass label (24 categories) in `resume_features.csv` for training resume career classification and domain classification models.
2. **`is_hot_technology` & `is_in_demand`:** Binary market demand labels in `skill_occupation_features.csv` for skill prioritization and relevance ranking.
3. **`importance_score` & `level_score`:** Empirical occupational benchmarks from O*NET survey instruments for target skill proficiency benchmarking.

### Non-Existent Labels (Explicitly NOT Available)
> [!CAUTION]
> **No Ground-Truth Candidate Skill Proficiency Scores:**  
> Neither the Kaggle `Resume.csv` dataset nor the O*NET occupational database contains individual candidate skill proficiency scores (e.g., individual competency ratings from 0 to 100). Resumes contain unverified, self-reported text.  
> **Under no circumstances should synthetic proficiency scores be fabricated or claimed as ground truth.** In Phase 2/3, individual proficiency will be estimated via ReSkillAI's multi-evidence synthesis formula (Resume scan depth + assessment answers + project complexity) anchored against O*NET benchmark levels.

---

*Authored by ReSkillAI Machine Learning Operations. Phase 1 Preprocessing and Feature Engineering.*
