from typing import List
from ..schemas.intelligence import NextCareerProgression
from ..schemas.profile import StudentProfile

PROGRESSION_MAP = {
    "career_cybersecurity": NextCareerProgression(
        currentCareerTitle="Cybersecurity Analyst",
        nextCareerRole="Threat Hunter / Detection Engineer",
        specializations=["Security Operations Center (SOC)", "Cloud Security Architecture", "Digital Forensics & Incident Response (DFIR)"],
        transferableSkills=["Networking Protocols", "Linux Administration", "SIEM Log Triage", "Python Scripting"],
        skillsToAcquire=["YARA Rule Authoring", "Kernel Internals", "Automated SOAR Playbooks", "Adversary Emulation (MITRE ATT&CK)"],
        rationale="Your foundations in network protocol analysis and Linux telemetry directly unlock threat hunting roles where proactive adversary discovery is paramount."
    ),
    "career_fullstack": NextCareerProgression(
        currentCareerTitle="Full Stack Developer",
        nextCareerRole="Distributed Systems Engineer / Cloud Backend Architect",
        specializations=["Cloud-Native Architecture", "Microservices & Distributed Transactions", "Design Systems & High-Velocity Frontend"],
        transferableSkills=["React State Boundaries", "Node.js Event Loop", "REST Protocol Contracts", "MongoDB Schemas"],
        skillsToAcquire=["gRPC & Protocol Buffers", "Kafka Event Streaming", "Kubernetes Operators", "Cache Invalidation Patterns"],
        rationale="Transitioning from single-app full stack delivery to high-scale distributed backends builds on your established API contracts and database schema knowledge."
    ),
    "career_ai_ml": NextCareerProgression(
        currentCareerTitle="AI / Machine Learning Engineer",
        nextCareerRole="MLOps & LLM Infrastructure Specialist",
        specializations=["Generative AI Fine-Tuning", "Low-Latency Model Inference", "Computer Vision & Edge Deployments"],
        transferableSkills=["Python Vectorization", "PyTorch Modeling", "Pandas Data Wrangling", "FastAPI Serving"],
        skillsToAcquire=["vLLM & TensorRT", "Model Distillation", "Feature Store Infrastructure", "Distributed Training with Ray"],
        rationale="Scaling model inference under sub-100ms latency budgets leverages your mathematical modeling background into high-demand AI platform engineering."
    )
}

class CareerProgressionEngine:
    @staticmethod
    def get_next_progression(profile: StudentProfile) -> NextCareerProgression:
        cid = profile.targetCareerId or "career_fullstack"
        return PROGRESSION_MAP.get(cid, PROGRESSION_MAP["career_fullstack"])
