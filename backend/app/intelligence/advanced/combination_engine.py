from typing import Dict, Any, List, Set
from ...schemas.profile import StudentProfile

COMBINATION_PATTERNS = [
    {
        "career": "Data Engineering",
        "pattern": ["python", "sql", "aws", "data analysis"],
        "min_match": 2,
        "explanation": "Combining automated Python pipelines with structured SQL queries, cloud infrastructure (AWS), and analytical modeling enables scalable data engineering architectures.",
        "base_confidence": 0.88
    },
    {
        "career": "DevSecOps Engineer",
        "pattern": ["linux", "git", "cybersecurity", "docker"],
        "min_match": 2,
        "explanation": "Integrating operational Linux systems with version-controlled CI/CD workflows and security scanning creates a strong bridge to DevSecOps.",
        "base_confidence": 0.88
    },
    {
        "career": "Backend Cloud Architect",
        "pattern": ["python", "rest apis", "docker", "sql"],
        "min_match": 2,
        "explanation": "Designing microservices with robust relational persistence and container packaging unlocks scalable backend systems architecture.",
        "base_confidence": 0.84
    },
    {
        "career": "Security Operations Analyst (SOC)",
        "pattern": ["networking", "linux", "cybersecurity", "wireshark"],
        "min_match": 2,
        "explanation": "Pairing deep network protocol understanding with Linux administration and traffic analysis provides high operational fidelity for incident triage.",
        "base_confidence": 0.90
    },
    {
        "career": "AI Application Developer",
        "pattern": ["python", "react", "fastapi", "machine learning"],
        "min_match": 2,
        "explanation": "Connecting responsive reactive client interfaces with Python machine learning inference services unlocks modern AI product development.",
        "base_confidence": 0.85
    }
]

class CombinationEngine:
    @staticmethod
    def discover_combinations(profile: StudentProfile) -> List[Dict[str, Any]]:
        """Identifies synergistic combinations of 2-5 user skills that unlock specific career pathways."""
        user_skills: Set[str] = {s.name.lower().strip() for s in (profile.skills or [])}
        
        # Also include companion skills derived from practical experience or projects
        for proj in (profile.projects or []):
            for t in (proj.tech or []):
                user_skills.add(t.lower().strip())

        discovered: List[Dict[str, Any]] = []

        for item in COMBINATION_PATTERNS:
            career_title = item["career"]
            pattern = item["pattern"]
            min_match = item["min_match"]

            matching_skills = [p for p in pattern if any(p in u or u in p for u in user_skills)]
            missing_skills = [p for p in pattern if p not in matching_skills]

            if len(matching_skills) >= min_match:
                match_ratio = float(len(matching_skills)) / float(len(pattern))
                confidence = round(min(0.95, item["base_confidence"] * (0.6 + 0.4 * match_ratio)), 2)

                discovered.append({
                    "combination": [m.title() for m in matching_skills],
                    "career": career_title,
                    "confidence": confidence,
                    "supportingSkills": [m.title() for m in matching_skills],
                    "missingSkills": [m.title() for m in missing_skills],
                    "explanation": item["explanation"]
                })

        return sorted(discovered, key=lambda x: x["confidence"], reverse=True)

combination_engine = CombinationEngine()
