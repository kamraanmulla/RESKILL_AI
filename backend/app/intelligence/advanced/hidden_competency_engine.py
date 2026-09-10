from typing import List, Dict, Any, Set
from ...schemas.profile import StudentProfile

# Domain evidence heuristics: mapping combinations of tools, projects, and keywords to inferred competencies
COMPETENCY_RULES = [
    {
        "competency": "Python Programming",
        "triggers": ["flask", "fastapi", "django", "pandas", "numpy", "pytorch", "scikit-learn"],
        "context_keywords": ["python", "script", "backend", "model", "data", "app", "pipeline"],
        "reasoning": "Demonstrated practical implementation using Python framework ecosystems and runtime libraries.",
        "base_confidence": 0.88
    },
    {
        "competency": "REST API Development",
        "triggers": ["flask", "fastapi", "express", "django", "spring boot", "node.js"],
        "context_keywords": ["api", "endpoint", "rest", "backend", "crud", "route"],
        "reasoning": "Demonstrated use of server-side frameworks alongside API implementation patterns.",
        "base_confidence": 0.85
    },
    {
        "competency": "Cloud Infrastructure & Deployment",
        "triggers": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "context_keywords": ["deploy", "cloud", "container", "ec2", "s3", "dockerfile", "cluster"],
        "reasoning": "Practical experience with containerization or hyperscaler cloud services.",
        "base_confidence": 0.85
    },
    {
        "competency": "Database Schema Design & Modeling",
        "triggers": ["sql", "postgresql", "mysql", "mongodb", "sqlite"],
        "context_keywords": ["schema", "query", "database", "table", "collection", "migration", "relational"],
        "reasoning": "Application projects require structured data persistence, normalization, and querying.",
        "base_confidence": 0.80
    },
    {
        "competency": "Full-Stack Application Architecture",
        "triggers": ["react", "vue", "angular", "next.js"],
        "requires_companion": ["python", "node.js", "express", "fastapi", "django", "java"],
        "context_keywords": ["fullstack", "full-stack", "integrated", "dashboard", "portal", "web app"],
        "reasoning": "Connecting modern reactive frontend clients with server-side backend logic.",
        "base_confidence": 0.88
    },
    {
        "competency": "Secure Software Development",
        "triggers": ["jwt", "oauth", "bcrypt", "authentication", "authorization", "csrf", "ssl"],
        "context_keywords": ["auth", "security", "token", "password", "login", "role", "protect"],
        "reasoning": "Implemented identity verification, cryptographic hashing, and access control mechanisms.",
        "base_confidence": 0.84
    },
    {
        "competency": "Network Traffic Analysis",
        "triggers": ["wireshark", "nmap", "tcpdump", "snort"],
        "context_keywords": ["packet", "network", "traffic", "protocol", "port", "ip", "capture"],
        "reasoning": "Hands-on packet inspection, vulnerability scanning, and protocol diagnostics.",
        "base_confidence": 0.86
    },
    {
        "competency": "Version Control & Collaborative Workflow",
        "triggers": ["git", "github", "gitlab"],
        "context_keywords": ["repo", "branch", "pull request", "commit", "merge", "ci/cd"],
        "reasoning": "Standard branch-based development and software lifecycle version tracking.",
        "base_confidence": 0.78
    },
    {
        "competency": "Analytical Problem Decomposition",
        "triggers": ["data analysis", "pandas", "numpy", "matplotlib", "tableau"],
        "context_keywords": ["dataset", "insights", "metrics", "visualiz", "eda", "statistical"],
        "reasoning": "Evidence of transforming unstructured records into statistical distributions and business insights.",
        "base_confidence": 0.81
    }
]

class HiddenCompetencyEngine:
    @staticmethod
    def detect_hidden_competencies(profile: StudentProfile) -> List[Dict[str, Any]]:
        """Detect skills the candidate demonstrates through project/experience evidence
        that are not explicitly claimed in their primary skill chips.
        """
        # Collect explicitly claimed skill names (normalized lower-case)
        explicit_skills: Set[str] = {s.name.lower().strip() for s in (profile.skills or [])}
        
        # Aggregate textual and metadata evidence from projects, experience, and tools
        evidence_corpus: List[Dict[str, str]] = []
        
        for proj in (profile.projects or []):
            combined_text = f"{proj.title} {' '.join(proj.tech or [])} {proj.description or ''}"
            evidence_corpus.append({
                "source": "project",
                "text": combined_text.lower(),
                "display": f"Project: {proj.title}"
            })
            
        for exp in (profile.experience or []):
            combined_text = f"{exp.title} {exp.company} {exp.description or ''}"
            evidence_corpus.append({
                "source": "experience",
                "text": combined_text.lower(),
                "display": f"Experience: {exp.title} at {exp.company}"
            })
            
        if profile.practicalExperience:
            evidence_corpus.append({
                "source": "practical_experience",
                "text": profile.practicalExperience.lower(),
                "display": f"Hands-on work: {profile.practicalExperience[:60]}..."
            })

        results: List[Dict[str, Any]] = []
        already_inferred: Set[str] = set()

        for rule in COMPETENCY_RULES:
            comp_name = rule["competency"]
            # Skip if user already explicitly lists this competency
            if comp_name.lower() in explicit_skills or comp_name in already_inferred:
                continue

            triggers = rule["triggers"]
            context_kw = rule["context_keywords"]
            requires_companion = rule.get("requires_companion", [])

            # Check if user has trigger skills/evidence
            trigger_found = False
            matching_evidence_source = ""
            matching_evidence_snippet = ""
            confidence_boost = 0.0

            # Direct skill match for triggers
            for trig in triggers:
                if trig in explicit_skills:
                    trigger_found = True
                    matching_evidence_source = "explicit_skill_synthesis"
                    matching_evidence_snippet = f"Claimed skill: {trig.title()}"
                    confidence_boost += 0.05
                    break

            # Project / experience corpus check
            for item in evidence_corpus:
                item_text = item["text"]
                has_trigger = any(t in item_text for t in triggers)
                has_context = any(c in item_text for c in context_kw)
                
                if has_trigger and has_context:
                    trigger_found = True
                    matching_evidence_source = item["source"]
                    matching_evidence_snippet = item["display"]
                    confidence_boost += 0.08
                    break
                elif has_trigger and not trigger_found:
                    trigger_found = True
                    matching_evidence_source = item["source"]
                    matching_evidence_snippet = item["display"]

            # Companion requirement check if defined
            if requires_companion and trigger_found:
                companion_found = any(comp in explicit_skills for comp in requires_companion)
                if not companion_found:
                    for item in evidence_corpus:
                        if any(comp in item["text"] for comp in requires_companion):
                            companion_found = True
                            break
                if not companion_found:
                    trigger_found = False

            if trigger_found and matching_evidence_snippet:
                final_confidence = min(0.95, round(rule["base_confidence"] + confidence_boost, 2))
                # Only include if above conservative threshold (>= 0.70)
                if final_confidence >= 0.70:
                    already_inferred.add(comp_name)
                    results.append({
                        "skill": comp_name,
                        "confidence": final_confidence,
                        "source": matching_evidence_source,
                        "evidence": matching_evidence_snippet,
                        "reasoning": rule["reasoning"],
                        "explicitOrInferred": "inferred"
                    })

        return sorted(results, key=lambda x: x["confidence"], reverse=True)

hidden_competency_engine = HiddenCompetencyEngine()
