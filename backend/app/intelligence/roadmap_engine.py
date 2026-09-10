from typing import List, Optional, Dict
from ..schemas.profile import StudentProfile
from ..schemas.intelligence import RoadmapStep, RoadmapResource, PracticeProject
from .career_taxonomy import get_career_by_id
from .skill_gap_engine import SkillGapEngine

# Curated, verified resource mapping for skills
VERIFIED_SKILL_RESOURCES: Dict[str, Dict[str, str]] = {
    "Python": {
        "video_title": "Learn Python – Interactive Course 2026",
        "video_url": "https://www.youtube.com/watch?v=kLZgQWjnUz0",
        "doc_title": "Official Python 3 Documentation & Tutorial",
        "doc_url": "https://docs.python.org/3/tutorial/"
    },
    "JavaScript": {
        "video_title": "JavaScript Crash Course For Beginners",
        "video_url": "https://www.youtube.com/watch?v=hdI2bqOjy3c",
        "doc_title": "MDN Web Docs: JavaScript Reference",
        "doc_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"
    },
    "TypeScript": {
        "video_title": "TypeScript Tutorial for Beginners",
        "video_url": "https://www.youtube.com/watch?v=d56mG7DezGs",
        "doc_title": "Official TypeScript Handbook",
        "doc_url": "https://www.typescriptlang.org/docs/"
    },
    "HTML/CSS": {
        "video_title": "HTML Tutorial for Beginners: HTML Crash Course",
        "video_url": "https://www.youtube.com/watch?v=qz0aGYrrlhU",
        "doc_title": "MDN Web Docs: HTML & CSS Core Guide",
        "doc_url": "https://developer.mozilla.org/en-US/docs/Learn"
    },
    "React": {
        "video_title": "React Crash Course for Modern Web Apps",
        "video_url": "https://www.youtube.com/watch?v=LDB4uaJ87e0",
        "doc_title": "Official React Documentation: Quick Start",
        "doc_url": "https://react.dev/learn"
    },
    "Node.js": {
        "video_title": "Node.js Full Course for Beginners | All-in-One Tutorial",
        "video_url": "https://www.youtube.com/watch?v=f2EqECiTBL8",
        "doc_title": "Official Node.js API Documentation",
        "doc_url": "https://nodejs.org/docs/latest/api/"
    },
    "REST APIs": {
        "video_title": "What Is REST API? Examples And How To Use It",
        "video_url": "https://www.youtube.com/watch?v=-mN3VyJuCjM",
        "doc_title": "Architectural Styles and REST Constraints (Fielding)",
        "doc_url": "https://restfulapi.net/"
    },
    "Express": {
        "video_title": "Learn Express JS In 35 Minutes",
        "video_url": "https://www.youtube.com/watch?v=SccSCuHhOw0",
        "doc_title": "Express.js Official Guide & Routing Reference",
        "doc_url": "https://expressjs.com/en/starter/installing.html"
    },
    "SQL": {
        "video_title": "SQL Tutorial - Full Database Course for Beginners",
        "video_url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "doc_title": "PostgreSQL Documentation & SQL Tutorial",
        "doc_url": "https://www.postgresql.org/docs/current/tutorial-sql.html"
    },
    "MongoDB": {
        "video_title": "MongoDB Crash Course",
        "video_url": "https://www.youtube.com/watch?v=ofme2o29ngU",
        "doc_title": "MongoDB Manual: CRUD Operations & Aggregation",
        "doc_url": "https://www.mongodb.com/docs/manual/"
    },
    "Linux": {
        "video_title": "Linux Crash Course for Beginners with Labs",
        "video_url": "https://www.youtube.com/watch?v=6WatcfENsOU",
        "doc_title": "Linux Journey: Practical Command-Line Foundations",
        "doc_url": "https://linuxjourney.com/"
    },
    "Networking": {
        "video_title": "Computer Networking Full Course - OSI Model Deep Dive",
        "video_url": "https://www.youtube.com/watch?v=IPvYjXCsTg8",
        "doc_title": "Wireshark Official User's Guide",
        "doc_url": "https://www.wireshark.org/docs/wsug_html_chunked/"
    },
    "Cybersecurity": {
        "video_title": "Cyber Security Full Course 2026 | Beginner to Advanced Course",
        "video_url": "https://www.youtube.com/watch?v=IjbSt71piWQ",
        "doc_title": "OWASP Top Ten Web Application Security Risks",
        "doc_url": "https://owasp.org/www-project-top-ten/"
    },
    "SIEM": {
        "video_title": "Wazuh SIEM Complete Beginner's Guide | Concepts, Installation & Setup",
        "video_url": "https://www.youtube.com/watch?v=mKijuwrTeRM",
        "doc_title": "Wazuh Open Source SIEM Documentation",
        "doc_url": "https://documentation.wazuh.com/current/getting-started/index.html"
    },
    "Incident Response": {
        "video_title": "Incident Response Process - SY0-601 CompTIA Security+",
        "video_url": "https://www.youtube.com/watch?v=fU_w8Ou9RVg",
        "doc_title": "NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide",
        "doc_url": "https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final"
    },
    "Docker": {
        "video_title": "Docker Tutorial for Beginners [FULL COURSE in 3 Hours]",
        "video_url": "https://www.youtube.com/watch?v=3c-iBn73dDE",
        "doc_title": "Official Docker Orientation and Setup Guide",
        "doc_url": "https://docs.docker.com/get-started/"
    },
    "Kubernetes": {
        "video_title": "Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours]",
        "video_url": "https://www.youtube.com/watch?v=X48VuDVv0do",
        "doc_title": "Kubernetes Official Documentation: Learn Kubernetes Basics",
        "doc_url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"
    },
    "Git": {
        "video_title": "Git & GitHub Crash Course for Beginners",
        "video_url": "https://www.youtube.com/watch?v=mAFoROnOfHs",
        "doc_title": "Pro Git Book (Chacon & Straub)",
        "doc_url": "https://git-scm.com/book/en/v2"
    },
    "Machine Learning": {
        "video_title": "Machine Learning for Everybody – Full Course",
        "video_url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
        "doc_title": "Scikit-Learn Machine Learning in Python User Guide",
        "doc_url": "https://scikit-learn.org/stable/user_guide.html"
    },
    "Data Analysis": {
        "video_title": "Data Analysis with Python: Complete Live Course",
        "video_url": "https://www.youtube.com/watch?v=EsDFiZPljYo",
        "doc_title": "Pandas Official Documentation & API Reference",
        "doc_url": "https://pandas.pydata.org/docs/user_guide/index.html"
    },
    "Cloud": {
        "video_title": "AWS Tutorial For Beginners | AWS Full Course in 10 Hours",
        "video_url": "https://www.youtube.com/watch?v=k1RI5locZE4",
        "doc_title": "AWS Getting Started Documentation Center",
        "doc_url": "https://aws.amazon.com/getting-started/"
    },
    "Statistics": {
        "video_title": "Statistics - A Full University Course on Data Science Basics",
        "video_url": "https://www.youtube.com/watch?v=xxpc-HPKN28",
        "doc_title": "StatQuest: Statistics & Machine Learning Visual Guides",
        "doc_url": "https://statquest.org/"
    }
}

# 6-step curriculum templates for all 7 careers in the taxonomy
CURRICULUM_TEMPLATES = {
    "career_fullstack": [
        ("Modern Client Architecture & JavaScript Core", "JavaScript", "Deep command of asynchronous runtimes, promises, and DOM mechanics.",
         ["Event Loop Execution", "Closures & Scopes", "Async/Await Pipelines", "ES6+ Modules"],
         "Build reactive state management store from scratch without libraries.", "12 hours"),
        ("Declarative UI Systems & React Component Lifecycle", "React", "Industry standard for web application interfaces.",
         ["Custom Hooks", "Context Boundaries", "Rendering Optimization", "TypeScript with React"],
         "Create accessible design system with modal, tabs, and datatable.", "16 hours"),
        ("Node.js Runtime & Express Server Pipelines", "Node.js", "Server execution runtime handling concurrent network I/O.",
         ["Event-Driven Architecture", "Express Middleware", "Error Handling Boundaries", "Security Headers"],
         "Build streaming file ingestion server with zero memory leaks.", "14 hours"),
        ("REST API Design, Validation & Contracts", "REST APIs", "Clean protocol contracts between frontend clients and server endpoints.",
         ["HTTP Idempotency", "Zod/Joi Validation", "Standardized Error Objects", "Pagination & Filtering"],
         "Design full-featured multi-tenant Course API with comprehensive validation.", "15 hours"),
        ("Database Schemas & Persistence Mechanics", "MongoDB", "Structured document and relational storage strategies.",
         ["Schema Normalization", "Compound Indexes", "Aggregation Pipelines", "Transaction Locks"],
         "Design optimized persistence layer handling concurrent writes with index analysis.", "14 hours"),
        ("Containerization & Production Deployment Pipelines", "Docker", "Ensuring consistent runtime across development and production clouds.",
         ["Multi-stage Dockerfiles", "Docker Compose Orchestration", "GitHub Actions CI", "Environment Segregation"],
         "Containerize full-stack application and deploy with automated CI pipeline.", "12 hours"),
    ],
    "career_frontend": [
        ("HTML5 Semantic Architecture & Responsive CSS Systems", "HTML/CSS", "Foundations of accessible, high-performance web structure and layout.",
         ["Semantic HTML5 Elements", "CSS Flexbox & Grid", "Fluid Responsive Typography", "ARIA Accessibility Standards"],
         "Build mobile-responsive marketing landing page passing 100% Lighthouse accessibility score.", "10 hours"),
        ("Modern JavaScript Deep Dive & Asynchronous Mechanics", "JavaScript", "Mastering DOM events, modern ES6+ idioms, and reactive paradigms.",
         ["Closures & Higher Order Functions", "Fetch & Async/Await", "Event Delegation", "Module Bundling"],
         "Develop client-side task board application with offline persistence in localStorage.", "14 hours"),
        ("Declarative UI Systems & React Component Architecture", "React", "Industry-standard library for component-based reactive interfaces.",
         ["Functional Components & Hooks", "Component Composition", "State Colocation", "Forms & Controlled Inputs"],
         "Construct responsive e-commerce product catalog with dynamic filter and sort controls.", "16 hours"),
        ("Type-Safe Frontend Development with TypeScript", "TypeScript", "Eliminate runtime errors through static type contracts.",
         ["Interfaces & Type Aliases", "Generic Component Props", "Union & Discriminated Types", "Strict Null Checks"],
         "Migrate React application to strict TypeScript with zero any types.", "14 hours"),
        ("Version Control & Collaborative Git Workflows", "Git", "Standard branching strategies and team pull request lifecycles.",
         ["Feature Branch Workflows", "Rebasing & Resolving Merge Conflicts", "Pull Request Reviews", "Git Tagging"],
         "Initialize monorepo with multiple packages, branch protections, and PR templates.", "10 hours"),
        ("Container Packaging & Frontend Deployment", "Docker", "Building optimized static bundles and lightweight container images.",
         ["Multi-Stage Nginx Builds", "Cache Invalidation", "Environment Variable Injection", "Vercel/Cloudflare Deployment"],
         "Build and deploy production-ready containerized frontend application on a cloud provider.", "12 hours")
    ],
    "career_backend": [
        ("Server-Side JavaScript Runtimes & Node.js Core", "Node.js", "Mastering asynchronous I/O, event emitters, and process management.",
         ["Non-Blocking Event Loop", "Buffers & Streams", "Process Environment Config", "Native Child Processes"],
         "Implement streaming HTTP server capable of handling multipart file uploads.", "14 hours"),
        ("Express Framework & Middleware Architecture", "Express", "Standard web server framework for handling routes and requests.",
         ["Custom Middleware Chains", "Route Controllers", "Global Error Handling", "CORS & Rate Limiting"],
         "Build secure REST service with rate limiting, input validation, and structured error responses.", "14 hours"),
        ("RESTful API Contracts & Specification Standards", "REST APIs", "Robust protocol design following standardized OpenAPI specifications.",
         ["HTTP Status Semantics", "OpenAPI/Swagger Generation", "JSON Schema Validation", "Pagination & Filtering"],
         "Publish verified OpenAPI 3.0 specification with interactive Swagger documentation.", "12 hours"),
        ("Relational Data Modeling & SQL Query Optimization", "SQL", "Designing normalized relational schemas and efficient queries.",
         ["Third Normal Form Schemas", "Foreign Key Cascades", "Inner & Outer Joins", "B-Tree Indexing Plans"],
         "Design relational inventory database and optimize slow join queries using EXPLAIN ANALYZE.", "16 hours"),
        ("NoSQL Document Modeling & Aggregations", "MongoDB", "High-throughput unstructured and document persistence strategies.",
         ["Document Embedding vs Referencing", "Aggregation Pipelines", "Secondary Indexes", "Sharding Basics"],
         "Build analytics aggregation pipeline summarizing multi-metric timeseries records.", "14 hours"),
        ("Containerization & Microservice Packaging", "Docker", "Packaging backend services for isolated container execution.",
         ["Production Dockerfiles", "Docker Compose Multi-Container Stacks", "Healthchecks & Restarts", "Secret Management"],
         "Package backend API, database, and Redis cache into a orchestrated Docker Compose cluster.", "15 hours")
    ],
    "career_cybersecurity": [
        ("Networking Fundamentals & Packet Inspection", "Networking", "Essential foundation for packet analysis and firewall rules.",
         ["OSI 7 Layers", "TCP/IP Handshake", "Subnetting", "DNS/DHCP Protocols"],
         "Analyze pcap trace in Wireshark and extract unencrypted credentials.", "12 hours"),
        ("Linux System Administration & Shell Scripting", "Linux", "SOC analysts operate primarily within POSIX terminal environments.",
         ["File Permissions", "Systemd Services", "Bash Automation", "Cron & Process Auditing"],
         "Author bash script that alerts on unauthorized sudo attempts in /var/log/auth.log.", "14 hours"),
        ("Defensive Security Principles & Vulnerability Assessment", "Cybersecurity", "Core concepts of attack surfaces, CVE metrics, and threat vectors.",
         ["CIA Triad", "OWASP Top 10", "CVSS Scoring", "Port Scanning with Nmap"],
         "Execute controlled scan on vulnerable laboratory VM and produce remediation briefing.", "16 hours"),
        ("SIEM Log Ingestion & Threat Detection Architecture", "SIEM", "The central nerve center of enterprise security operations.",
         ["Wazuh & ELK Stack", "Syslog & Windows Event IDs", "Correlation Rules", "Alert Tuning"],
         "Deploy local Wazuh/Elastic instance and author rule detecting brute-force SSH.", "18 hours"),
        ("Incident Response Lifecycles & Forensics", "Incident Response", "Protocol for containing, eradicating, and reporting breach events.",
         ["NIST SP 800-61", "Memory Dumping", "Root Cause Analysis", "Chain of Custody"],
         "Conduct tabletop containment exercise for simulated credential compromise.", "15 hours"),
        ("Security Automation with Python", "Python", "Automating triage scripts and threat feed enrichment.",
         ["Requests & APIs", "Regex Log Parsing", "Threat Feed Automation", "Scripted Alert Triaging"],
         "Build automated IP reputation lookup tool querying public threat databases.", "12 hours"),
    ],
    "career_ai_ml": [
        ("Python Scientific Computing & Numerical Foundations", "Python", "Vectorized math and matrix manipulations driving all tensor runtimes.",
         ["NumPy Broadcasting", "Matrix Factorization", "Vector Calculus", "Memory Layouts"],
         "Implement linear regression and neural forward pass purely in NumPy.", "14 hours"),
        ("Data Wrangling & Statistical Exploratory Analysis", "Data Analysis", "Real-world ML fails on noisy data pipelines.",
         ["Pandas Aggregations", "Missing Value Imputation", "Feature Distributions", "Outlier Capping"],
         "Clean and normalize 1M+ transaction dataset with zero data leakage.", "16 hours"),
        ("Relational Data Extraction & SQL Feature Stores", "SQL", "Extracting point-in-time features from transactional stores.",
         ["Window Functions", "Common Table Expressions", "Indexing Execution Plans", "Aggregations"],
         "Author analytical queries computing 30-day user rolling engagement features.", "12 hours"),
        ("Supervised & Unsupervised Machine Learning Algorithms", "Machine Learning", "Core classical modeling techniques before neural networks.",
         ["Decision Trees & Ensembles", "Gradient Boosting (XGBoost)", "Cross-Validation", "Precision/Recall Tuning"],
         "Train customer churn predictor achieving >0.88 ROC-AUC score.", "18 hours"),
        ("Probability & Inferential Statistics for Modeling", "Statistics", "Formulating rigorous statistical hypotheses and validation.",
         ["Probability Distributions", "Hypothesis Testing & p-values", "Confidence Intervals", "A/B Testing"],
         "Conduct statistical significance test analyzing model inference uplift over baseline.", "14 hours"),
        ("Containerization & Model Service Deployment", "Docker", "Serving model predictions behind low-latency REST interfaces.",
         ["FastAPI Inference Wrappers", "Docker Containerization", "Model Serialization", "Latency Benchmarks"],
         "Deploy trained ML model behind Docker container with automated health endpoints.", "15 hours")
    ],
    "career_cloud_devops": [
        ("Linux Administration & POSIX Automation", "Linux", "The universal foundation of cloud virtual machines and container runtimes.",
         ["Bash Shell Scripting", "Systemd Daemon Management", "Kernel Parameters & Tuning", "SSH Key Infrastructure"],
         "Author modular bash script automating hardened server provisioning with firewall rules.", "14 hours"),
        ("Distributed Version Control & Collaborative Git", "Git", "Core underpinning of declarative GitOps and team collaboration.",
         ["Trunk-Based Development", "Interactive Rebasing", "Git Hooks & Linters", "Semantic Versioning"],
         "Setup complete repository with branch protection rules, linting hooks, and changelog automation.", "10 hours"),
        ("Cloud Infrastructure Fundamentals & Cloud Architecture", "Cloud", "Hyperscaler compute, virtual networks, and storage primitives.",
         ["VPC Peering & Subnets", "IAM Security Roles", "Object Storage (S3)", "Elastic Cloud Compute (EC2)"],
         "Provision secure multi-tier cloud network with public load balancer and private instances.", "16 hours"),
        ("Container Packaging & Docker Image Optimization", "Docker", "Creating immutable, lightweight application artifacts for cloud runtime.",
         ["Multi-stage Build Layers", "Non-Root Security Containers", "Volume Mounting & Networking", "Docker Registries"],
         "Package multi-service application with Docker Compose and publish to container registry.", "14 hours"),
        ("Container Orchestration & Cluster Management", "Kubernetes", "Managing high availability, automated scaling, and rollout strategies.",
         ["Pods, Deployments & Services", "Ingress Controllers", "ConfigMaps & Secrets", "Horizontal Pod Autoscalers"],
         "Deploy scalable Kubernetes cluster with rolling deployments and zero downtime.", "18 hours"),
        ("Enterprise Networking & Cloud Traffic Routing", "Networking", "Configuring secure ingress, TLS certificates, and domain routing.",
         ["DNS Record Types", "Reverse Proxies & Nginx", "TLS/SSL Certificate Lifecycle", "Load Balancer Routing"],
         "Configure reverse proxy routing encrypted traffic to containerized backend microservices.", "12 hours")
    ],
    "career_data_science": [
        ("Python Analytics & Vectorized Computing", "Python", "Core programming runtime for data extraction and algorithmic workflows.",
         ["NumPy Arrays & Vectors", "List Comprehensions & Lambdas", "File I/O & CSV Parsing", "Script Optimization"],
         "Implement algorithm calculating statistical moving averages across time-series data.", "12 hours"),
        ("Data Transformation & Tabular Wrangling with Pandas", "Data Analysis", "Cleaning, pivoting, and preparing raw datasets for statistical analysis.",
         ["DataFrame Operations", "Groupby Aggregations", "Handling Nulls & Duplicates", "Merging & Joining Data"],
         "Transform messy multi-source survey dataset into clean, normalized analysis table.", "16 hours"),
        ("Relational Database Extraction & Advanced SQL", "SQL", "Pulling strategic insights directly from relational data stores.",
         ["Window Functions & Partitioning", "CTEs (Common Table Expressions)", "Complex Subqueries", "Aggregations"],
         "Write analytical SQL queries calculating monthly cohort retention metrics.", "14 hours"),
        ("Statistical Foundations & Probability Theory", "Statistics", "Rigorous reasoning about experimental certainty and distributions.",
         ["Normal & Binomial Distributions", "Central Limit Theorem", "Hypothesis Testing (t-tests, chi-square)", "p-value Interpretation"],
         "Run A/B test analysis evaluating conversion uplift with 95% confidence intervals.", "15 hours"),
        ("Predictive Machine Learning Algorithms", "Machine Learning", "Building predictive regression and classification pipelines.",
         ["Feature Engineering & Scaling", "Supervised Classifiers", "Model Evaluation Metrics (F1, AUC)", "Hyperparameter Tuning"],
         "Build end-to-end regression pipeline predicting real estate valuations with cross-validation.", "18 hours"),
        ("Version Control & Collaborative Data Science", "Git", "Managing reproducible analytical notebooks and shared codebases.",
         ["Notebook Versioning", "Branching & Git Workflows", "Open Source Collaboration", "Reproducible Pipelines"],
         "Structure reproducible data science repository with dataset tracking and environment lockfiles.", "10 hours")
    ]
}

class RoadmapEngine:
    @classmethod
    def generate_roadmap(cls, profile: StudentProfile, target_career_id: Optional[str] = None) -> List[RoadmapStep]:
        cid = target_career_id or profile.targetCareerId or "career_fullstack"
        target_career = get_career_by_id(cid)
        gaps = SkillGapEngine.calculate_skill_gaps(profile, cid)

        # Select template matching career or fallback to fullstack
        template = CURRICULUM_TEMPLATES.get(cid, CURRICULUM_TEMPLATES["career_fullstack"])

        # Assessment signals influence prioritization
        assessment_style = ""
        assessment_weak_signals = []
        if profile.assessmentSignals:
            assessment_style = (profile.assessmentSignals.problemSolvingStyle or "").lower()
            assessment_weak_signals = [s.lower() for s in (profile.assessmentSignals.workStyleSignals or [])]

        steps: List[RoadmapStep] = []

        for idx, (title, skill_key, why, topics, proj_desc, est_time) in enumerate(template):
            step_num = f"{idx + 1:02d}"

            # Check if student already mastered or has in-progress status from SkillGapEngine
            gap_item = next(
                (g for g in gaps if g.skill.lower() in skill_key.lower() or skill_key.lower() in g.skill.lower()),
                None
            )

            # Check candidate's direct skill proficiency in profile
            user_skill = next(
                (s for s in (profile.skills or []) if s.name.lower().strip() == skill_key.lower().strip()),
                None
            )

            if gap_item:
                if gap_item.status == "Mastered" or (user_skill and user_skill.proficiency >= 75):
                    status = "completed"
                elif gap_item.status == "In Progress" or (user_skill and user_skill.proficiency >= 50):
                    status = "in_progress"
                else:
                    status = "upcoming"
            elif user_skill and user_skill.proficiency >= 75:
                status = "completed"
            elif user_skill and user_skill.proficiency >= 50:
                status = "in_progress"
            else:
                status = "upcoming"

            # Retrieve verified real video and documentation resources for this skill
            res_info = VERIFIED_SKILL_RESOURCES.get(skill_key, {
                "video_title": f"{skill_key} Masterclass & Engineering Patterns",
                "video_url": "https://www.youtube.com/watch?v=kLZgQWjnUz0",
                "doc_title": f"Official {skill_key} Documentation",
                "doc_url": "https://developer.mozilla.org/"
            })

            recommended_resources = [
                RoadmapResource(
                    title=res_info["video_title"],
                    type="Video",
                    duration="2h 30m",
                    url=res_info["video_url"],
                    platform="YouTube"
                ),
                RoadmapResource(
                    title=res_info["doc_title"],
                    type="Documentation",
                    duration="1h 15m",
                    url=res_info["doc_url"],
                    platform="Documentation"
                )
            ]

            steps.append(
                RoadmapStep(
                    id=f"step_{step_num}_{cid}",
                    stepNumber=step_num,
                    title=title,
                    status=status,
                    whyItMatters=why,
                    topics=topics,
                    skillsCovered=topics,
                    recommendedResources=recommended_resources,
                    practiceProject=PracticeProject(
                        title=f"{skill_key} Milestone Project",
                        description=proj_desc,
                        deliverable="Production-ready GitHub repository with README and tests."
                    ),
                    estimatedTime=est_time,
                    skillKey=skill_key
                )
            )

        # Dynamic Prioritization:
        # If student has completed steps, they remain marked completed.
        # Ensure at least one step is in_progress if none is.
        has_in_progress = any(s.status == "in_progress" for s in steps)
        if not has_in_progress:
            for s in steps:
                if s.status != "completed":
                    s.status = "in_progress"
                    break

        return steps
