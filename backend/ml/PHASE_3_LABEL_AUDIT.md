# ReSkillAI Phase 3: Comprehensive Label & Evidence Audit

## Executive Assessment

> [!CRITICAL]
> **Definitive Finding:** There are **zero explicit candidate-level ground truth skill proficiency scores** in any public or raw dataset available to this project (`Resume.csv` or O\*NET 31.0).
> Any attempt to train a conventional supervised regression model predicting a continuous $0 \text{--} 100$ individual "proficiency score" would require inventing synthetic labels or treating heuristic scores as ground truth. **Both practices are strictly prohibited by ReSkillAI engineering integrity standards.**

---

## 1. Candidate-Level Labels Available
We audited the Kaggle Resume Dataset (`backend/ml/data/raw/kaggle/Resume.csv`), containing 2,482 unique candidate resumes across 24 sectors:

| Column | Data Type | Contains Proficiency Ground Truth? | Description & Limitations |
| :--- | :--- | :---: | :--- |
| `ID` | Integer / String | **NO** | Arbitrary candidate resume identifier. |
| `Resume_str` | Text | **NO** | Unstructured resume text (skills, work experience, summary, education). Contains *unverified self-claims* of skills, not objective performance tests. |
| `Resume_html` | HTML Text | **NO** | HTML formatting of resume text. |
| `Category` | Categorical | **NO** | Broad occupational classification (e.g. `INFORMATION-TECHNOLOGY`, `FINANCE`). Supervised target for Phase 2/2.5 only; does not specify individual skill mastery. |

**Audit Conclusion on Candidate Data:**
- No test scores, assessment answers, code review grades, or verified supervisor evaluations exist in the Kaggle dataset.
- Candidate text reflects self-reported skill mentions with varying degrees of contextual corroboration (e.g., listed in a bullet vs described in an applied project vs accompanied by concrete technical co-occurrences).

---

## 2. Skill-Level Labels Available
We audited O\*NET 31.0 reference tables for skill-specific metrics:

| Table | Relevant Columns | Contains Individual Candidate Proficiency? | Description & Limitations |
| :--- | :--- | :---: | :--- |
| `essential_skills.csv` | `Importance`, `Level`, `Data Value` | **NO** | Represents occupational requirements rated by industrial occupational analysts, **NOT** candidate skill proficiency. |
| `software_skills.csv` | `Hot Technology`, `In Demand` | **NO** | Binary market demand flags for technologies; does not rate any individual's ability. |
| `transferable_skills.csv`| `Element Name`, `Data Value` | **NO** | Occupational cross-functional skill taxonomy. |
| `knowledge.csv` | `Importance`, `Level` | **NO** | Knowledge domain benchmarks for occupations. |

**Audit Conclusion on Skill Data:**
- O\*NET provides normative benchmarks for *occupations* (what a Senior Data Engineer or Accountant is expected to know), not evaluations of *candidates*.
- Treating O\*NET importance (e.g., 4.2 / 5.0) as candidate proficiency is a catastrophic categorical fallacy (conflating job demand with individual competence).

---

## 3. Occupational-Level Labels Available
- `occupation_data.csv`: O\*NET-SOC titles and descriptions.
- `job_zones.csv`: Typical education, experience, and job training thresholds (Job Zone 1 through 5).
- `work_activities.csv`: Generalized work activities associated with occupational roles.

These provide contextual occupational features (e.g., expected technical complexity of a role), but zero individual candidate evaluations.

---

## 4. What Can Legitimately Be Used as a Target
The only scientifically defensible learning formulation is:
### **Candidate-Skill Evidence Support Classification / Ranking**
Instead of hallucinating a 0–100 proficiency grade, we model:
$$\text{Evidence Strength} \in [0.0, 1.0]$$
$$\text{Confidence} \in [0.0, 1.0]$$

This predicts:
> *"Does the candidate's portfolio of evidence (resume contextual depth, action-oriented implementation phrasing, co-occurring toolchains, verified project applications, and domain assessment outcomes) substantively corroborate this skill, or is it an isolated superficial mention / entirely unevidenced?"*

### Defensible Evidence Support Tiers:
- **Tier 2: Strong / Substantive Evidence ($Y=2$ or Positive Binary)**
  - Skill appears in applied project or work experience descriptions with active implementation verbs ("architected", "deployed", "implemented", "optimized").
  - Skill co-occurs with related technical stack tools (e.g. Python co-occurring with pandas/Docker/PostgreSQL).
  - High contextual frequency and descriptive depth.
- **Tier 1: Superficial / Casual Mention ($Y=1$ or Weak)**
  - Skill appears only as an isolated bullet point in a generic "Skills" list without descriptive elaboration or project validation.
- **Tier 0: Absent / Insufficient Evidence ($Y=0$)**
  - Skill is expected or queried for an occupational pathway, but zero evidence exists anywhere in the candidate's portfolio.

---

## 5. What Cannot Legitimately Be Used as a Target
1. **Arbitrary numerical formulas:** Converting word counts into pseudo-percentages (e.g., $\text{count} \times 15 = \text{Proficiency}$) and calling it ground truth.
2. **Current ReSkillAI Readiness Scores:** Training an ML model to predict ReSkillAI's own deterministic readiness engine output is circular and provides zero independent validation.
3. **Deterministic Skill Gap Engine Outputs:** Replicating existing rule-based gap outputs produces a redundant copycat model rather than an independent evidence discriminator.
4. **O\*NET Occupational Importance as Candidate Grade:** Conflating occupational necessity with candidate mastery.

---

## 6. Is Supervised Learning Defensible?
- **Direct Supervised Regression ($0 \text{--} 100$ Proficiency):** **NO.** Categorically indefensible due to complete absence of ground-truth candidate grading data.
- **Evidence-Support Classification with Programmatic Weak Supervision:** **YES.** Highly defensible. We can train an interpretable model to classify whether evidence for a skill is substantively corroborated vs superficial vs absent, using multimodal evidence signals.

---

## 7. Weak Supervision & Proxy-Labeling Strategy
To avoid arbitrary labeling:
1. Candidate resumes are parsed into semantic sections: *Summary*, *Core Skills*, *Professional Experience*, *Projects*, and *Education*.
2. For each candidate-skill pair:
   - Positive evidence requires contextual convergence across independent text signals: occurrence in an experience/project block, active verb accompaniment, and domain tool co-occurrence.
   - Negative evidence is drawn from career-relevant skills that are completely unmentioned in the candidate's resume (true negatives).
3. The model outputs a calibrated probability:
   - `evidence_strength`: Probability that the candidate's evidence substantively corroborates the skill.
   - `confidence`: Certainty metric reflecting depth and convergence of available signals.

---

## 8. Risks of Label Leakage & Mitigation
| Leakage Vector | Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Candidate Identity Leakage** | Resumes with multiple candidate-skill pairs appearing in both train and test splits would cause severe data leakage. | **Strict Group / Candidate-Isolated Split:** Train/Val/Test partitioning is performed strictly at the candidate level (`candidate_id`). All skill pairs for candidate $X$ remain strictly in one split. |
| **Target Derived Features** | Using the label definition criteria directly as a sole feature. | Model learns from a multi-dimensional feature representation (frequencies, section ratios, token distance, co-occurrence graph, O\*NET background context), ensuring generalization across unseen skills and phrasings. |
| **Engine Output Leakage** | Incorporating ReSkillAI live engine scores into feature sets. | Features are extracted strictly from raw textual and structural evidence. No deterministic engine outputs are used. |

---

## Summary Decision
We proceed with **Candidate-Skill Evidence Strength Prediction** powered by candidate-isolated weak supervision and calibrated probabilistic inference. The system will explicitly disclaim pseudo-proficiency and instead output reliable, interpretable evidence strength and confidence metrics.
