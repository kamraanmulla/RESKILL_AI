from typing import List
from ..schemas.intelligence import CareerRole

CAREER_TAXONOMY: List[CareerRole] = [
    CareerRole(
        id="career_fullstack",
        title="Full Stack Developer",
        slug="full-stack-developer",
        category="Software Engineering",
        description="Bridges client interfaces with robust server architectures, managing database persistence, API contracts, and deployment pipelines.",
        experienceLevel="Entry-Level",
        coreSkills=["JavaScript", "React", "Node.js", "REST APIs", "MongoDB", "Git"],
        secondarySkills=["Docker", "Testing", "TypeScript", "CI/CD"],
        currentMatchPercentage=0,
        avgSalary="₹7.5 – 12 LPA",
        demandLevel="Very High",
        marketInsight="High demand across startups and tech firms looking for engineers capable of end-to-end feature delivery."
    ),
    CareerRole(
        id="career_frontend",
        title="Frontend Developer",
        slug="frontend-developer",
        category="Software Engineering",
        description="Crafts accessible, high-performance web applications with semantic HTML, modern CSS, client state management, and component systems.",
        experienceLevel="Entry-Level",
        coreSkills=["JavaScript", "React", "HTML/CSS", "TypeScript", "Git", "Responsive Design"],
        secondarySkills=["Performance Optimization", "Next.js", "Tailwind CSS"],
        currentMatchPercentage=0,
        avgSalary="₹6.5 – 10.5 LPA",
        demandLevel="High",
        marketInsight="Strong demand for engineers focused on UI latency, design system architecture, and modern JavaScript frameworks."
    ),
    CareerRole(
        id="career_backend",
        title="Backend Developer",
        slug="backend-developer",
        category="Software Engineering",
        description="Architects reliable server runtimes, data schemas, API gateways, background workers, authentication strategies, and microservices.",
        experienceLevel="Entry-Level",
        coreSkills=["Node.js", "REST APIs", "Express", "SQL", "MongoDB", "Authentication"],
        secondarySkills=["Docker", "Redis", "System Design", "Testing"],
        currentMatchPercentage=0,
        avgSalary="₹7.0 – 11.5 LPA",
        demandLevel="Very High",
        marketInsight="Requires solidifying RESTful conventions, relational and document database indexing, and containerization fundamentals."
    ),
    CareerRole(
        id="career_cybersecurity",
        title="Cybersecurity Analyst",
        slug="cybersecurity-analyst",
        category="Information Security",
        description="Monitors enterprise network telemetry, triages security alerts, detects intrusion vectors, and enforces defensive posture across systems.",
        experienceLevel="Entry-Level",
        coreSkills=["Networking", "Linux", "Cybersecurity", "SIEM", "Incident Response", "Python"],
        secondarySkills=["Threat Detection", "Wireshark", "Firewalls", "SOC Operations"],
        currentMatchPercentage=0,
        avgSalary="₹7.0 – 12.5 LPA",
        demandLevel="Very High",
        marketInsight="High urgency worldwide. Security operations centers seek talent with solid Linux command-line, networking, and log triage capabilities."
    ),
    CareerRole(
        id="career_ai_ml",
        title="AI / Machine Learning Engineer",
        slug="ai-ml-engineer",
        category="Artificial Intelligence",
        description="Researches, trains, validates, and deploys predictive machine learning, deep learning, and transformer architectures into production pipelines.",
        experienceLevel="Entry-Level",
        coreSkills=["Python", "Machine Learning", "Data Analysis", "SQL", "Pandas", "Linear Algebra"],
        secondarySkills=["PyTorch", "TensorFlow", "FastAPI", "MLOps", "Docker"],
        currentMatchPercentage=0,
        avgSalary="₹8.5 – 15.0 LPA",
        demandLevel="Very High",
        marketInsight="Explosive growth in generative AI, data preparation pipelines, and embedded model inference services."
    ),
    CareerRole(
        id="career_cloud_devops",
        title="Cloud / DevOps Engineer",
        slug="cloud-devops-engineer",
        category="Cloud & Infrastructure",
        description="Builds automated continuous integration pipelines, provisions cloud infrastructure-as-code, and ensures 99.99% system availability.",
        experienceLevel="Entry-Level",
        coreSkills=["Linux", "Cloud", "Git", "Docker", "Networking", "CI/CD"],
        secondarySkills=["Kubernetes", "AWS", "Terraform", "Shell Scripting"],
        currentMatchPercentage=0,
        avgSalary="₹7.5 – 13.0 LPA",
        demandLevel="Very High",
        marketInsight="Every software group requires automated deployment and container orchestration. High entry-level leverage."
    ),
    CareerRole(
        id="career_data_science",
        title="Data Scientist",
        slug="data-scientist",
        category="Data & Analytics",
        description="Applies statistical rigor, machine learning models, and data mining algorithms to extract strategic business forecasts from raw data.",
        experienceLevel="Entry-Level",
        coreSkills=["Python", "SQL", "Data Analysis", "Statistics", "Machine Learning", "Excel"],
        secondarySkills=["Data Visualization", "Pandas", "Scikit-Learn", "A/B Testing"],
        currentMatchPercentage=0,
        avgSalary="₹7.0 – 12.0 LPA",
        demandLevel="High",
        marketInsight="Steady demand across fintech, retail, and healthcare for data-driven modeling and experiment analysis."
    )
]

def get_career_by_id(career_id: str) -> CareerRole:
    for c in CAREER_TAXONOMY:
        if c.id == career_id:
            return c
    return CAREER_TAXONOMY[0]
