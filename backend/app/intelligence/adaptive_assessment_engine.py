from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timezone
from ..schemas.assessment import (
    AdaptiveQuestionView,
    AdaptiveOptionView,
    PracticalScenarioView,
    CareerIntelligenceProfile,
    DomainKnowledgeSignal,
    CareerPathwayResult,
    DiscoveredCombinationResult,
    ConfidenceLevel,
    InterestRating
)
from ..schemas.profile import StudentProfile, Skill, AssessmentSignals
from .career_taxonomy import CAREER_TAXONOMY, get_career_by_id
from .advanced.combination_engine import CombinationEngine
from .advanced.transferability_engine import TransferabilityEngine
from .skill_gap_engine import SkillGapEngine

# ==============================================================================
# CANONICAL DOMAIN DEFINITIONS
# ==============================================================================

CANONICAL_DOMAINS = [
    {"id": "cybersecurity", "label": "Cybersecurity", "careerId": "career_cybersecurity"},
    {"id": "backend", "label": "Backend Development", "careerId": "career_backend"},
    {"id": "frontend", "label": "Frontend Development", "careerId": "career_frontend"},
    {"id": "cloud_devops", "label": "Cloud/DevOps", "careerId": "career_cloud_devops"},
    {"id": "ai_ml", "label": "AI/ML", "careerId": "career_ai_ml"},
    {"id": "data_science", "label": "Data Science", "careerId": "career_data_science"},
    {"id": "fullstack", "label": "Full Stack Development", "careerId": "career_fullstack"}
]

DOMAIN_MAP = {d["id"]: d for d in CANONICAL_DOMAINS}

# ==============================================================================
# CANONICAL QUESTION BANK (35+ Detailed Engineering Scenarios)
# ==============================================================================

QUESTION_BANK: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # 1. CYBERSECURITY
    # --------------------------------------------------------------------------
    {
        "id": "q_sec_01",
        "domain": "cybersecurity",
        "skill": "Incident Response",
        "difficulty": "intermediate",
        "questionType": "scenario_analysis",
        "question": "A company's employee account suddenly shows unusual login activity from a foreign IP at 3:00 AM followed by mass file downloads. What is the most critical immediate containment action?",
        "scenario": "Enterprise SOC telemetry detected anomalous concurrent sessions on a privileged Active Directory account.",
        "options": [
            {"id": "opt_a", "text": "Immediately revoke active authentication tokens, force session termination, and isolate the endpoint."},
            {"id": "opt_b", "text": "Send an email to the employee asking if they are currently traveling or accessing files."},
            {"id": "opt_c", "text": "Wait for the file transfer to finish so a complete checksum hash can be computed."},
            {"id": "opt_d", "text": "Reboot the domain controller server to clear temporary memory buffers."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Immediate revocation of tokens, session termination, and endpoint isolation cuts the adversary's lateral access and prevents further exfiltration.",
        "evidenceSkill": "Incident Response",
        "points": 25
    },
    {
        "id": "q_sec_02",
        "domain": "cybersecurity",
        "skill": "Networking",
        "difficulty": "beginner",
        "questionType": "fundamentals",
        "question": "When inspecting network traffic, an analyst observes continuous SYN packets sent to multiple sequential ports on an internal host without completing any three-way handshakes. What is this traffic indicative of?",
        "scenario": "Firewall logs show hundreds of half-open TCP connections originating from a single internal IP.",
        "options": [
            {"id": "opt_a", "text": "A stealth TCP SYN port scan (half-open scan) probing for open service ports."},
            {"id": "opt_b", "text": "Normal DNS name resolution traffic under high load."},
            {"id": "opt_c", "text": "Healthy web browser HTTP keep-alive packet recycling."},
            {"id": "opt_d", "text": "DHCP IP lease renewals across local subnet nodes."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "A sequence of SYN packets without ACK responses is a classic TCP SYN port scan used to map exposed ports without establishing full connections.",
        "evidenceSkill": "Networking",
        "points": 20
    },
    {
        "id": "q_sec_03",
        "domain": "cybersecurity",
        "skill": "Linux",
        "difficulty": "intermediate",
        "questionType": "debugging",
        "question": "On a production Linux server suspected of being compromised, which file contains historical user authentication attempts, sudo elevations, and SSH login failures on Debian/Ubuntu systems?",
        "scenario": "Auditing intrusion forensics after an unauthorized root escalation alert.",
        "options": [
            {"id": "opt_a", "text": "/var/log/auth.log (or secure on RHEL/CentOS)"},
            {"id": "opt_b", "text": "/etc/resolv.conf"},
            {"id": "opt_c", "text": "/proc/cpuinfo"},
            {"id": "opt_d", "text": "/dev/null"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "/var/log/auth.log records system authorization events including sudo execution, PAM authentications, and SSH login history.",
        "evidenceSkill": "Linux",
        "points": 25
    },
    {
        "id": "q_sec_04",
        "domain": "cybersecurity",
        "skill": "SIEM",
        "difficulty": "advanced",
        "questionType": "architecture",
        "question": "When tuning an enterprise SIEM correlation rule for detecting Pass-the-Hash or lateral Kerberos ticket abuse, which telemetry source provides the highest-fidelity evidence?",
        "scenario": "Designing threat detection pipelines to catch lateral movement in internal networks.",
        "options": [
            {"id": "opt_a", "text": "Windows Security Event Logs (Event IDs 4624 Type 9/3, 4672, and 4768/4769) paired with Sysmon network and process telemetry."},
            {"id": "opt_b", "text": "Client web browser cookie caching logs."},
            {"id": "opt_c", "text": "Frontend Nginx access logs recording static image assets."},
            {"id": "opt_d", "text": "Printer spooler service logs on workstation subnets."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Windows Event 4624 (Logon Types 3 and 9) alongside Kerberos Ticket-Granting (4768/4769) and Sysmon process telemetry directly capture credential abuse and lateral movement.",
        "evidenceSkill": "SIEM",
        "points": 30
    },
    {
        "id": "q_sec_05",
        "domain": "cybersecurity",
        "skill": "Cybersecurity",
        "difficulty": "intermediate",
        "questionType": "applied_decision_making",
        "question": "A web application parameter accepts user input directly into an internal SQL query: `SELECT * FROM users WHERE username = '` + input + `'`. How should the development team remediate this vulnerability?",
        "scenario": "Code audit revealing high-severity injection risks in the authentication endpoint.",
        "options": [
            {"id": "opt_a", "text": "Use parameterized queries / prepared statements with placeholder binding."},
            {"id": "opt_b", "text": "Simply encode the input using Base64 before concatenation."},
            {"id": "opt_c", "text": "Increase the database server memory to withstand unexpected query payloads."},
            {"id": "opt_d", "text": "Run the database on a non-standard TCP port."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Parameterized queries separate the query structure from untrusted user data, rendering SQL injection structurally impossible.",
        "evidenceSkill": "Cybersecurity",
        "points": 25
    },

    # --------------------------------------------------------------------------
    # 2. BACKEND DEVELOPMENT
    # --------------------------------------------------------------------------
    {
        "id": "q_be_01",
        "domain": "backend",
        "skill": "REST APIs",
        "difficulty": "intermediate",
        "questionType": "debugging",
        "question": "A production REST API becomes extremely slow whenever concurrent users exceed 1,000. Server CPU is at 15%, but database connection pool wait times are skyrocketing. What should you investigate first?",
        "scenario": "Diagnostic investigation into backend throughput bottlenecks under peak concurrent load.",
        "options": [
            {"id": "opt_a", "text": "Unindexed database queries causing table scans and slow query holds, or unreleased connection pool leaks."},
            {"id": "opt_b", "text": "Re-writing the frontend HTML markup to use simpler CSS class selectors."},
            {"id": "opt_c", "text": "Converting all HTTP GET endpoints to HTTP POST methods."},
            {"id": "opt_d", "text": "Replacing JSON responses with binary XML payloads."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Low CPU with high connection pool wait times strongly indicates blocking I/O caused by slow unindexed table scans or connection leakage.",
        "evidenceSkill": "REST APIs",
        "points": 25
    },
    {
        "id": "q_be_02",
        "domain": "backend",
        "skill": "SQL",
        "difficulty": "intermediate",
        "questionType": "problem_solving",
        "question": "You have an `orders` table with 5 million rows. A dashboard query `SELECT * FROM orders WHERE user_id = 4920 ORDER BY created_at DESC LIMIT 10` is taking 3.8 seconds. Which index strategy will optimize this query?",
        "scenario": "Relational database performance optimization on transactional records.",
        "options": [
            {"id": "opt_a", "text": "A composite index on (user_id, created_at DESC)"},
            {"id": "opt_b", "text": "A single-column index on order_id only"},
            {"id": "opt_c", "text": "Disabling database foreign key constraints"},
            {"id": "opt_d", "text": "Storing all orders as raw CSV text in the file system"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "A composite index on (user_id, created_at DESC) allows the query engine to immediately filter by user_id and read sorted created_at records without sorting in memory.",
        "evidenceSkill": "SQL",
        "points": 25
    },
    {
        "id": "q_be_03",
        "domain": "backend",
        "skill": "Node.js",
        "difficulty": "beginner",
        "questionType": "fundamentals",
        "question": "In a Node.js server, what happens if an asynchronous request handler performs heavy synchronous CPU-bound computing (such as calculating large Fibonacci sequences or synchronous cryptography)?",
        "scenario": "Architectural understanding of the single-threaded Node.js event loop.",
        "options": [
            {"id": "opt_a", "text": "It blocks the single event loop, causing all concurrent requests from other users to freeze until computation finishes."},
            {"id": "opt_b", "text": "Node automatically provisions new background threads to handle each synchronous calculation seamlessly."},
            {"id": "opt_c", "text": "It immediately throws a compilation error at runtime."},
            {"id": "opt_d", "text": "It offloads the calculation to the client browser automatically."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Node.js runs user JavaScript on a single thread event loop. Synchronous compute blocks the event loop, stopping it from servicing any other client requests.",
        "evidenceSkill": "Node.js",
        "points": 20
    },
    {
        "id": "q_be_04",
        "domain": "backend",
        "skill": "Authentication",
        "difficulty": "advanced",
        "questionType": "architecture",
        "question": "When architecting secure JWT authentication for a distributed microservice ecosystem, what is the recommended token expiration and storage strategy?",
        "scenario": "Designing stateless API authorization across multi-region services.",
        "options": [
            {"id": "opt_a", "text": "Short-lived Access Tokens (e.g., 15 mins) transmitted in Authorization headers, paired with HttpOnly Secure Refresh Tokens with rotation."},
            {"id": "opt_b", "text": "Issuing a permanent token with a 10-year expiration stored in plaintext localStorage."},
            {"id": "opt_c", "text": "Passing the database root password in the payload of every request."},
            {"id": "opt_d", "text": "Encrypting the entire token with Base64 without any digital signature."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Short-lived access tokens limit exposure if compromised, while HttpOnly SameSite secure refresh tokens with rotation prevent XSS extraction and permit revocation.",
        "evidenceSkill": "Authentication",
        "points": 30
    },
    {
        "id": "q_be_05",
        "domain": "backend",
        "skill": "MongoDB",
        "difficulty": "intermediate",
        "questionType": "code_reasoning",
        "question": "In an e-commerce document schema, when is embedding order line items directly inside the Order document preferred over referencing separate collection IDs?",
        "scenario": "NoSQL data modeling trade-offs between embedding vs referencing.",
        "options": [
            {"id": "opt_a", "text": "When line items are always read atomically with the order and rarely grow unboundedly beyond document size limits."},
            {"id": "opt_b", "text": "When line items are independently updated 5,000 times per second by different background workers."},
            {"id": "opt_c", "text": "Only when the database does not support collections."},
            {"id": "opt_d", "text": "When you want to execute manual client-side table joins for every single field."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Embedding provides atomic, zero-join reads for bounded child data that belongs strictly to the parent lifecycle (like snapshots of purchased line items).",
        "evidenceSkill": "MongoDB",
        "points": 25
    },

    # --------------------------------------------------------------------------
    # 3. FRONTEND DEVELOPMENT
    # --------------------------------------------------------------------------
    {
        "id": "q_fe_01",
        "domain": "frontend",
        "skill": "React",
        "difficulty": "intermediate",
        "questionType": "debugging",
        "question": "In a React application, a user notices that typing into an input field feels laggy and sluggish. Inspecting the component tree reveals the parent dashboard re-renders all 50 child cards on every single keystroke. What is the root cause and remedy?",
        "scenario": "Client-side rendering performance and state colocation triage.",
        "options": [
            {"id": "opt_a", "text": "The input state is held high up in the parent tree; colocate input state locally or wrap expensive children in React.memo / useMemo."},
            {"id": "opt_b", "text": "The browser is failing to parse JavaScript, so the page must be converted to static PDF."},
            {"id": "opt_c", "text": "React requires reloading the entire browser window whenever state changes."},
            {"id": "opt_d", "text": "Replace all JSX elements with HTML <table> tags."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Keeping high-frequency ephemeral state in an ancestor component causes cascading re-renders across all subtrees. Colocating state or memoizing static children resolves it.",
        "evidenceSkill": "React",
        "points": 25
    },
    {
        "id": "q_fe_02",
        "domain": "frontend",
        "skill": "JavaScript",
        "difficulty": "beginner",
        "questionType": "fundamentals",
        "question": "What is the difference between `==` and `===` in modern JavaScript?",
        "scenario": "Language fundamentals and type coercion safety in web runtimes.",
        "options": [
            {"id": "opt_a", "text": "`===` checks both value and type strictly without implicit type coercion; `==` attempts implicit type conversion."},
            {"id": "opt_b", "text": "`==` is for numbers only, while `===` is for strings only."},
            {"id": "opt_c", "text": "`===` assigns variables, while `==` compares them."},
            {"id": "opt_d", "text": "There is no difference in ES6; they are exact aliases."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Strict equality (===) verifies identical types and values without unexpected type coercions (such as '0' == 0 evaluating to true).",
        "evidenceSkill": "JavaScript",
        "points": 20
    },
    {
        "id": "q_fe_03",
        "domain": "frontend",
        "skill": "TypeScript",
        "difficulty": "intermediate",
        "questionType": "code_reasoning",
        "question": "You want to create a TypeScript type for a function argument that accepts all properties of `User` except for `passwordHash` and `salt`. Which utility type accomplishes this?",
        "scenario": "Type manipulation in modern type-safe application architectures.",
        "options": [
            {"id": "opt_a", "text": "Omit<User, 'passwordHash' | 'salt'>"},
            {"id": "opt_b", "text": "Pick<User, 'passwordHash'>"},
            {"id": "opt_c", "text": "Partial<User>"},
            {"id": "opt_d", "text": "Record<string, User>"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Omit<Type, Keys> constructs a type with all properties from Type except those specified in Keys.",
        "evidenceSkill": "TypeScript",
        "points": 25
    },
    {
        "id": "q_fe_04",
        "domain": "frontend",
        "skill": "Responsive Design",
        "difficulty": "beginner",
        "questionType": "applied_decision_making",
        "question": "When building a responsive UI that displays a 4-column card grid on desktop monitors and a single-column stacked layout on mobile devices, which CSS pattern is most resilient?",
        "scenario": "Responsive layout styling across diverse viewport widths.",
        "options": [
            {"id": "opt_a", "text": "CSS Grid with `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))` or responsive Flexbox with media queries."},
            {"id": "opt_b", "text": "Hardcoded absolute pixel positions: `left: 450px; top: 120px;` for every card."},
            {"id": "opt_c", "text": "Using an HTML `<marquee>` tag to scroll cards horizontally."},
            {"id": "opt_d", "text": "Resizing the user's monitor via client JavaScript window commands."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "CSS Grid with repeat(auto-fit, minmax(...)) gracefully wraps elements dynamically to available width without brittle hardcoded pixel thresholds.",
        "evidenceSkill": "Responsive Design",
        "points": 20
    },
    {
        "id": "q_fe_05",
        "domain": "frontend",
        "skill": "Performance Optimization",
        "difficulty": "advanced",
        "questionType": "architecture",
        "question": "A Single Page Application's bundle size has grown to 8.5 MB, resulting in slow First Contentful Paint (FCP) over mobile networks. Which architectural solution directly tackles this?",
        "scenario": "Optimizing bundle split and web performance metrics for large web apps.",
        "options": [
            {"id": "opt_a", "text": "Route-based dynamic code splitting using dynamic imports (`React.lazy`), tree shaking, and asset compression (Brotli/Gzip)."},
            {"id": "opt_b", "text": "Inlining all images directly into JavaScript bundle files as Base64 strings."},
            {"id": "opt_c", "text": "Disabling client-side caching headers on the CDN."},
            {"id": "opt_d", "text": "Bundling the entire Node.js server inside the client JavaScript file."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Dynamic code splitting loads only the code required for the current route on demand, drastically reducing initial parse, download, and execution time.",
        "evidenceSkill": "Performance Optimization",
        "points": 30
    },

    # --------------------------------------------------------------------------
    # 4. CLOUD & DEVOPS
    # --------------------------------------------------------------------------
    {
        "id": "q_cloud_01",
        "domain": "cloud_devops",
        "skill": "Docker",
        "difficulty": "intermediate",
        "questionType": "debugging",
        "question": "A web application works seamlessly on a developer's macOS machine, but when packaged in a Docker container and deployed to a Linux cloud instance, it crashes on startup with 'standard_init_linux.go: exec user process caused: no such file or directory'. What is the most likely cause?",
        "scenario": "Container runtime troubleshooting across local and cloud environments.",
        "options": [
            {"id": "opt_a", "text": "Windows/DOS line endings (CRLF instead of LF) in entrypoint bash scripts or architecture binary mismatch (ARM64 vs x86_64)."},
            {"id": "opt_b", "text": "The cloud server does not have enough disk space to read the word 'docker'."},
            {"id": "opt_c", "text": "Docker only runs on Windows 98 and cannot execute on modern Linux kernels."},
            {"id": "opt_d", "text": "The developer forgot to buy a commercial SSL domain certificate."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Non-UNIX carriage returns (CRLF) in script shebang lines or deploying an ARM-compiled binary onto an x86 host yields the classic 'no such file or directory' container failure.",
        "evidenceSkill": "Docker",
        "points": 25
    },
    {
        "id": "q_cloud_02",
        "domain": "cloud_devops",
        "skill": "CI/CD",
        "difficulty": "intermediate",
        "questionType": "applied_decision_making",
        "question": "In a continuous delivery pipeline, what is the core purpose of maintaining automated staging environments and automated canary rollouts?",
        "scenario": "Designing safe zero-downtime deployment pipelines for production software.",
        "options": [
            {"id": "opt_a", "text": "To validate migrations and route a small fraction (e.g. 5%) of live traffic to the new release to detect errors before 100% rollout."},
            {"id": "opt_b", "text": "To eliminate the need for writing unit tests altogether."},
            {"id": "opt_c", "text": "To ensure that software is only released once every 3 years."},
            {"id": "opt_d", "text": "To prevent developers from pushing code to Git repositories."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Canary rollouts expose a tiny slice of production traffic to the new build while monitoring error telemetry, allowing instant automated rollback before widespread user impact.",
        "evidenceSkill": "CI/CD",
        "points": 25
    },
    {
        "id": "q_cloud_03",
        "domain": "cloud_devops",
        "skill": "Cloud",
        "difficulty": "advanced",
        "questionType": "architecture",
        "question": "You are architecting high availability for an API on AWS. The application must survive an entire data center failure without human intervention. Which architecture satisfies this requirement?",
        "scenario": "Multi-availability zone cloud infrastructure resilience design.",
        "options": [
            {"id": "opt_a", "text": "Deploying stateless container tasks across multiple Availability Zones (Multi-AZ) behind an Application Load Balancer with Multi-AZ database failover."},
            {"id": "opt_b", "text": "Running everything on a single large EC2 instance in us-east-1a without backups."},
            {"id": "opt_c", "text": "Manually copying files to a USB flash drive every evening."},
            {"id": "opt_d", "text": "Relying on client browsers to host their own database instances locally."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Multi-AZ distribution ensures that if a physical data center experiences power or network failure, load balancers and synchronized replicas seamlessly preserve operations.",
        "evidenceSkill": "Cloud",
        "points": 30
    },
    {
        "id": "q_cloud_04",
        "domain": "cloud_devops",
        "skill": "Linux",
        "difficulty": "beginner",
        "questionType": "fundamentals",
        "question": "On a remote cloud Linux server, you need to check which process is consuming port 8080 and occupying memory. Which command is appropriate?",
        "scenario": "Command-line server diagnostics and process triage.",
        "options": [
            {"id": "opt_a", "text": "`sudo lsof -i :8080` or `sudo ss -tulpn | grep 8080`"},
            {"id": "opt_b", "text": "`rm -rf /`"},
            {"id": "opt_c", "text": "`echo hello world > /dev/null`"},
            {"id": "opt_d", "text": "`cat /etc/passwd | wc -l`"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "lsof -i :port and ss -tulpn reveal the listening sockets and their associated process IDs (PID).",
        "evidenceSkill": "Linux",
        "points": 20
    },
    {
        "id": "q_cloud_05",
        "domain": "cloud_devops",
        "skill": "Git",
        "difficulty": "beginner",
        "questionType": "problem_solving",
        "question": "A developer accidentally committed an AWS secret access key to a public Git repository. What is the immediate correct response?",
        "scenario": "Security incident response regarding source code credential leakage.",
        "options": [
            {"id": "opt_a", "text": "Immediately rotate/revoke the credential in AWS IAM, audit CloudTrail logs for unauthorized usage, and remove the secret from Git history."},
            {"id": "opt_b", "text": "Make a new commit with message 'fixed secret' and leave the credential active."},
            {"id": "opt_c", "text": "Ignore it because Git commits are encrypted and cannot be viewed by others."},
            {"id": "opt_d", "text": "Delete the Git repository on your local laptop only."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Public Git history is scraped within seconds by bots. Immediate revocation and rotation at the provider level is mandatory, followed by history purging and log auditing.",
        "evidenceSkill": "Git",
        "points": 20
    },

    # --------------------------------------------------------------------------
    # 5. AI & MACHINE LEARNING
    # --------------------------------------------------------------------------
    {
        "id": "q_ai_01",
        "domain": "ai_ml",
        "skill": "Machine Learning",
        "difficulty": "intermediate",
        "questionType": "conceptual_reasoning",
        "question": "A classification model achieves 99.4% accuracy on training data, but its accuracy drops to 62.1% on the unseen test set. What is this phenomenon called, and what is a standard mitigation?",
        "scenario": "Model generalization diagnostics and regularization strategies.",
        "options": [
            {"id": "opt_a", "text": "Overfitting (high variance); mitigate using L1/L2 regularization, dropout, data augmentation, or simpler model architecture."},
            {"id": "opt_b", "text": "Underfitting (high bias); mitigate by deleting half the training dataset."},
            {"id": "opt_c", "text": "Vanishing gradient; mitigate by decreasing learning rate to zero."},
            {"id": "opt_d", "text": "Model convergence; the model is ready for immediate unmonitored production deployment."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "A large gap between high training performance and low validation performance is the hallmark of overfitting, where the model memorizes noise instead of generalizable patterns.",
        "evidenceSkill": "Machine Learning",
        "points": 25
    },
    {
        "id": "q_ai_02",
        "domain": "ai_ml",
        "skill": "Pandas",
        "difficulty": "beginner",
        "questionType": "code_reasoning",
        "question": "In Python Pandas, you have a dataframe `df` with a column `salary` containing missing (NaN) values. Which method replaces those missing entries with the column median?",
        "scenario": "Data preprocessing and imputation in exploratory machine learning workflows.",
        "options": [
            {"id": "opt_a", "text": "df['salary'] = df['salary'].fillna(df['salary'].median())"},
            {"id": "opt_b", "text": "df.drop('salary')"},
            {"id": "opt_c", "text": "df['salary'].delete_all_rows()"},
            {"id": "opt_d", "text": "df['salary'] = df['salary'] + 100"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "df.fillna() imputes missing NaN values with the specified scalar, here calculated as the median of the distribution.",
        "evidenceSkill": "Pandas",
        "points": 20
    },
    {
        "id": "q_ai_03",
        "domain": "ai_ml",
        "skill": "Python",
        "difficulty": "intermediate",
        "questionType": "problem_solving",
        "question": "You are preprocessing tabular data for an anomaly detection pipeline. One numeric feature has extreme outliers that skew the mean drastically. Which scaling method is most robust?",
        "scenario": "Feature scaling strategies for sensitive machine learning algorithms.",
        "options": [
            {"id": "opt_a", "text": "RobustScaler (using median and interquartile range IQR) or quantile transformation."},
            {"id": "opt_b", "text": "Multiplying all numbers by 1,000,000 to hide the outliers."},
            {"id": "opt_c", "text": "Replacing all floating point numbers with random strings."},
            {"id": "opt_d", "text": "MinMax scaling between 0 and 1 without filtering extreme outliers."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "StandardScaler and MinMaxScaler are heavily influenced by extreme outliers. RobustScaler uses median and IQR, making feature normalization resilient to extreme values.",
        "evidenceSkill": "Python",
        "points": 25
    },
    {
        "id": "q_ai_04",
        "domain": "ai_ml",
        "skill": "Linear Algebra",
        "difficulty": "advanced",
        "questionType": "fundamentals",
        "question": "In deep learning backpropagation, how is gradient flow through matrix multiplications computed to update layer weights?",
        "scenario": "Mathematical foundations of neural network optimization.",
        "options": [
            {"id": "opt_a", "text": "Applying the multivariable chain rule to compute partial derivatives with respect to weights, propagated via vector-Jacobian products."},
            {"id": "opt_b", "text": "Randomly guessing new weights until the loss drops below 0.1."},
            {"id": "opt_c", "text": "Inverting the entire weight matrix using Gaussian elimination at every forward pass."},
            {"id": "opt_d", "text": "Dividing the target label by the input tensor dimensions."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Backpropagation computes partial derivatives of the scalar loss with respect to all parameter tensors using the multivariate chain rule via efficient backward vector-Jacobian products.",
        "evidenceSkill": "Linear Algebra",
        "points": 30
    },
    {
        "id": "q_ai_05",
        "domain": "ai_ml",
        "skill": "Data Analysis",
        "difficulty": "intermediate",
        "questionType": "scenario_analysis",
        "question": "You are evaluating a credit card fraud detection model where only 0.1% of transactions are fraudulent. The model predicts 'legitimate' for 100% of cases and claims 99.9% accuracy. Why is accuracy a misleading metric here?",
        "scenario": "Class imbalance metrics and evaluation rigor in predictive modeling.",
        "options": [
            {"id": "opt_a", "text": "Due to severe class imbalance, accuracy masks the fact that the model detects zero fraud; Precision, Recall, and PR-AUC must be evaluated instead."},
            {"id": "opt_b", "text": "Because 99.9% is mathematically impossible in binary classification."},
            {"id": "opt_c", "text": "Because credit card transactions cannot be represented as numbers."},
            {"id": "opt_d", "text": "The model is actually optimal and should be deployed immediately."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "In skewed datasets, a naive majority-class classifier scores near 100% accuracy while having zero true positives. Precision, Recall, F1-score, and PR-AUC are required.",
        "evidenceSkill": "Data Analysis",
        "points": 25
    },

    # --------------------------------------------------------------------------
    # 6. DATA SCIENCE
    # --------------------------------------------------------------------------
    {
        "id": "q_ds_01",
        "domain": "data_science",
        "skill": "Statistics",
        "difficulty": "intermediate",
        "questionType": "conceptual_reasoning",
        "question": "In an A/B test for an e-commerce checkout redesign, group A had a conversion rate of 4.1% (n=10,000) and group B had 4.8% (n=10,000). The resulting p-value is 0.012 at an alpha threshold of 0.05. How should a data scientist interpret this result?",
        "scenario": "Hypothesis testing and experimental inference on business metrics.",
        "options": [
            {"id": "opt_a", "text": "Reject the null hypothesis; there is statistically significant evidence that checkout B improves conversion under alpha=0.05."},
            {"id": "opt_b", "text": "The null hypothesis is proven 100% true with certainty."},
            {"id": "opt_c", "text": "p-value of 0.012 means the experiment failed and must be deleted."},
            {"id": "opt_d", "text": "The sample size was too small to make any numerical comparison."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "When p < alpha (0.012 < 0.05), we reject the null hypothesis of no difference, concluding there is statistically significant uplift attributable to variant B.",
        "evidenceSkill": "Statistics",
        "points": 25
    },
    {
        "id": "q_ds_02",
        "domain": "data_science",
        "skill": "SQL",
        "difficulty": "intermediate",
        "questionType": "problem_solving",
        "question": "Which SQL construct allows you to calculate a running cumulative sum of daily sales partitioned by region without collapsing individual row details?",
        "scenario": "Advanced SQL analytical functions for business intelligence.",
        "options": [
            {"id": "opt_a", "text": "Window function: `SUM(sales) OVER (PARTITION BY region ORDER BY sale_date)`"},
            {"id": "opt_b", "text": "A standard `GROUP BY region` clause with no aggregation"},
            {"id": "opt_c", "text": "`DROP TABLE sales CASCADE`"},
            {"id": "opt_d", "text": "An `INNER JOIN` onto the same table without any ON condition"}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Window functions (OVER PARTITION BY ... ORDER BY) compute running calculations across window frames while maintaining individual row records intact.",
        "evidenceSkill": "SQL",
        "points": 25
    },
    {
        "id": "q_ds_03",
        "domain": "data_science",
        "skill": "Data Analysis",
        "difficulty": "beginner",
        "questionType": "fundamentals",
        "question": "A dataset showing user session duration exhibits severe right-skew (a few users stay online for 20 hours while most leave in 3 minutes). Which measure of central tendency provides the most representative snapshot of the typical user?",
        "scenario": "Statistical descriptive summaries under skewed distributions.",
        "options": [
            {"id": "opt_a", "text": "Median (50th percentile), because it is resilient to extreme skew and outliers."},
            {"id": "opt_b", "text": "Arithmetic mean, because it is always pulled higher by the outliers."},
            {"id": "opt_c", "text": "Standard deviation divided by zero."},
            {"id": "opt_d", "text": "The maximum session duration value."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "The median represents the center of a skewed distribution without being distorted by extreme high outliers, unlike the arithmetic mean.",
        "evidenceSkill": "Data Analysis",
        "points": 20
    },
    {
        "id": "q_ds_04",
        "domain": "data_science",
        "skill": "Machine Learning",
        "difficulty": "advanced",
        "questionType": "architecture",
        "question": "When training a gradient boosted tree model (e.g. LightGBM / XGBoost) on tabular customer churn data, what is the best practice for cross-validating time-series transactional features?",
        "scenario": "Temporal validation leak prevention in predictive analytics.",
        "options": [
            {"id": "opt_a", "text": "Time-based rolling window / TimeSeriesSplit cross-validation to ensure models only train on past data and test on future periods."},
            {"id": "opt_b", "text": "Shuffling all data randomly across all years and predicting past records using future transactions."},
            {"id": "opt_c", "text": "Validating on the exact same dataset used for training."},
            {"id": "opt_d", "text": "Deleting all date columns before analysis."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Random k-fold shuffling on time-series data causes future data leakage into past predictions. Time-based rolling validation accurately mimics production inference.",
        "evidenceSkill": "Machine Learning",
        "points": 30
    },
    {
        "id": "q_ds_05",
        "domain": "data_science",
        "skill": "Python",
        "difficulty": "beginner",
        "questionType": "code_reasoning",
        "question": "What is the primary purpose of computing the Pearson correlation matrix across numerical features before building a multi-linear regression model?",
        "scenario": "Exploratory data analysis and multicollinearity checks.",
        "options": [
            {"id": "opt_a", "text": "To identify strong linear associations with the target variable and detect multicollinearity between input predictors."},
            {"id": "opt_b", "text": "To convert tabular numbers into RGB audio signals."},
            {"id": "opt_c", "text": "To automatically eliminate the need for feature engineering."},
            {"id": "opt_d", "text": "To ensure all variables have exactly zero variance."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Correlation matrices surface linear relationships between features and targets while flagging highly correlated predictors that introduce multicollinearity instability.",
        "evidenceSkill": "Python",
        "points": 20
    },

    # --------------------------------------------------------------------------
    # 7. FULL STACK DEVELOPMENT
    # --------------------------------------------------------------------------
    {
        "id": "q_fs_01",
        "domain": "fullstack",
        "skill": "Full Stack Architecture",
        "difficulty": "intermediate",
        "questionType": "architecture",
        "question": "In a Full Stack web application, how should a client-side form submission handle preventing duplicate order submissions caused by impatient users double-clicking the 'Pay Now' button?",
        "scenario": "End-to-end user experience and backend idempotency architecture.",
        "options": [
            {"id": "opt_a", "text": "Disable the UI submit button upon first click and generate an Idempotency-Key header verified server-side before charging."},
            {"id": "opt_b", "text": "Allow all clicks to process and instruct the bank to refund duplicate charges next week."},
            {"id": "opt_c", "text": "Crash the client browser after every transaction."},
            {"id": "opt_d", "text": "Turn off the backend database whenever a payment starts."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Combining client-side button disabling with server-side idempotency keys guarantees that repeated submissions process once and return the cached outcome.",
        "evidenceSkill": "Full Stack Architecture",
        "points": 25
    },
    {
        "id": "q_fs_02",
        "domain": "fullstack",
        "skill": "REST APIs",
        "difficulty": "beginner",
        "questionType": "debugging",
        "question": "A frontend React app running on `http://localhost:5173` tries to fetch data from an Express backend running on `http://localhost:8000/api/users`. The browser console displays: 'Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource'. What is required to resolve this?",
        "scenario": "Cross-Origin Resource Sharing (CORS) protocol fundamentals in full stack systems.",
        "options": [
            {"id": "opt_a", "text": "Configure CORS middleware on the Express server to allow origin `http://localhost:5173` with appropriate HTTP headers."},
            {"id": "opt_b", "text": "Uninstall the web browser and install an operating system that forbids security policies."},
            {"id": "opt_c", "text": "Change all passwords to 'password123'."},
            {"id": "opt_d", "text": "Rewrite the backend in pure CSS."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "CORS is enforced by browsers when protocols, domains, or ports differ. The backend must explicitly whitelist allowed client origins and methods.",
        "evidenceSkill": "REST APIs",
        "points": 20
    },
    {
        "id": "q_fs_03",
        "domain": "fullstack",
        "skill": "Git",
        "difficulty": "intermediate",
        "questionType": "problem_solving",
        "question": "A developer is merging feature branch `feature/auth` into `main`, but Git reports merge conflicts in `schema.prisma`. What is the correct collaborative resolution workflow?",
        "scenario": "Version control conflict resolution in fullstack repositories.",
        "options": [
            {"id": "opt_a", "text": "Open the conflicting files, reconcile both sets of schema additions, run tests to verify data migration integrity, and commit the resolved merge."},
            {"id": "opt_b", "text": "Delete the entire repository and start the project from scratch."},
            {"id": "opt_c", "text": "Force push (`git push -f`) to overwrite everyone else's work silently."},
            {"id": "opt_d", "text": "Ignore the error and deploy the broken conflict markers `<<<<<<< HEAD` to production."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Merge conflicts require manual inspection to synthesize conflicting lines cleanly, followed by automated test verification before finalizing the merge commit.",
        "evidenceSkill": "Git",
        "points": 25
    },
    {
        "id": "q_fs_04",
        "domain": "fullstack",
        "skill": "Node.js",
        "difficulty": "advanced",
        "questionType": "debugging",
        "question": "A fullstack application allows users to upload profile pictures. Under high load, the Node.js server experiences Out-Of-Memory (OOM) crashes. Inspecting the upload handler reveals `fs.readFileSync(req.file.buffer)` holding the entire 20MB files in memory. How should file uploads be re-architected?",
        "scenario": "Memory footprint optimization and streaming architectures in backend services.",
        "options": [
            {"id": "opt_a", "text": "Stream the file directly to object storage (e.g. S3) using Node streams or generate presigned S3 URLs so the client uploads directly to cloud storage."},
            {"id": "opt_b", "text": "Store all 20MB files inside environment variables in `.env`."},
            {"id": "opt_c", "text": "Increase server RAM to 1 terabyte and avoid changing code."},
            {"id": "opt_d", "text": "Convert all images into plain text JSON strings."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "Streaming or issuing presigned direct-to-S3 upload URLs removes large binary buffer overhead from the application server memory entirely.",
        "evidenceSkill": "Node.js",
        "points": 30
    },
    {
        "id": "q_fs_05",
        "domain": "fullstack",
        "skill": "React",
        "difficulty": "intermediate",
        "questionType": "conceptual_reasoning",
        "question": "What is the primary benefit of Server-Side Rendering (SSR) or Static Site Generation (SSG) in frameworks like Next.js compared to a traditional client-only Single Page Application?",
        "scenario": "Architectural rendering trade-offs between CSR and SSR.",
        "options": [
            {"id": "opt_a", "text": "Faster Time-To-First-Byte / initial content rendering and superior Search Engine Optimization (SEO) because search crawlers receive pre-rendered HTML."},
            {"id": "opt_b", "text": "It guarantees that no JavaScript code ever runs in the browser."},
            {"id": "opt_c", "text": "It replaces relational databases with browser cookies."},
            {"id": "opt_d", "text": "It eliminates the need for CSS styling."}
        ],
        "correctOptionId": "opt_a",
        "explanation": "SSR delivers fully formed HTML directly from the server on the initial GET request, accelerating perceived load time and enabling search crawlers to index content without running client JS.",
        "evidenceSkill": "React",
        "points": 25
    }
]

# ==============================================================================
# PRACTICAL REAL-WORLD CHALLENGES
# ==============================================================================

PRACTICAL_CHALLENGES: Dict[str, Dict[str, Any]] = {
    "cybersecurity": {
        "id": "prac_sec",
        "domain": "cybersecurity",
        "domainLabel": "Cybersecurity",
        "title": "Incident Triage: Suspicious High-Privilege Account Anomaly",
        "scenarioText": "At 02:40 AM, security telemetry alerts show an admin account on the corporate Active Directory logging in from an unfamiliar overseas ASN. Within 4 minutes, PowerShell was invoked on an internal domain member server to query 'net group Domain Admins /domain'. What is your sequenced response?",
        "contextSnippet": "Alert Rule: Lateral Reconnaissance via Active Directory Native CLI\nAccount: svc_backup_admin\nHost: CORP-SRV-04\nParent Process: explorer.exe -> powershell.exe -enc JABzACAAPQ... (Base64 Encoded)",
        "options": [
            {"id": "p_sec_opt1", "text": "1. Isolate CORP-SRV-04 from the local VLAN immediately.\n2. Revoke active Kerberos tickets and reset svc_backup_admin credentials.\n3. Decode the Base64 PowerShell payload and triage memory for C2 beaconing.\n4. Audit audit.log/Security Event IDs 4624/4688 to map lateral spread."},
            {"id": "p_sec_opt2", "text": "Send a Slack message to the backup administrator asking if they are doing late maintenance, and check back tomorrow morning."},
            {"id": "p_sec_opt3", "text": "Immediately format all corporate hard drives without collecting any volatile memory or disk forensics."},
            {"id": "p_sec_opt4", "text": "Disable the Windows firewall on the domain controller to see if the connection drops."}
        ],
        "bestOptionId": "p_sec_opt1",
        "bestRubric": "Immediate host containment, credential revocation, forensic decoding of encoded payload, and event correlation for lateral movement.",
        "points": 35
    },
    "backend": {
        "id": "prac_be",
        "domain": "backend",
        "domainLabel": "Backend Development",
        "title": "System Scalability: High-Concurrency API Throughput Degradation",
        "scenarioText": "During a flash sale, checkout throughput drops from 450 req/sec to 18 req/sec. Server CPU utilization is low (22%), but database connections are completely maxed out at 200/200, causing connection timeouts across all payment microservices. How do you resolve this architecture bottleneck?",
        "contextSnippet": "Endpoint: POST /api/v1/orders/checkout\nSlow Log: SELECT * FROM inventory WHERE item_id = ? FOR UPDATE; (locking row for 1.8s while calling external Payment Gateway sync)",
        "options": [
            {"id": "p_be_opt1", "text": "1. Decouple synchronous external payment gateway calls from open database row transactions.\n2. Use optimistic locking or a distributed Redis lock with short TTL.\n3. Implement a background message queue (RabbitMQ/Kafka) for asynchronous settlement processing."},
            {"id": "p_be_opt2", "text": "Double the database pool size to 10,000 connections without changing the transaction locking logic."},
            {"id": "p_be_opt3", "text": "Turn off database transactions entirely and allow concurrent purchases to write freely."},
            {"id": "p_be_opt4", "text": "Switch from PostgreSQL to storing all order states in browser localStorage."}
        ],
        "bestOptionId": "p_be_opt1",
        "bestRubric": "Decoupling slow I/O network calls from DB locks, employing Redis distributed locking/optimistic locks, and processing fulfillment asynchronously.",
        "points": 35
    },
    "cloud_devops": {
        "id": "prac_cloud",
        "domain": "cloud_devops",
        "domainLabel": "Cloud & DevOps",
        "title": "Infrastructure Resilience: Containerized Microservice CrashLoopBackOff",
        "scenarioText": "A newly deployed container in Kubernetes enters CrashLoopBackOff on AWS EKS. Running `kubectl describe pod` reveals Exit Code 137 (OOMKilled) during data initialization, and `kubectl logs --previous` shows the service trying to load an in-memory cache exceeding container memory limits.",
        "contextSnippet": "Container Status: Terminated\nReason: OOMKilled\nExit Code: 137\nLimits: cpu: 500m, memory: 512Mi\nRequests: cpu: 250m, memory: 256Mi",
        "options": [
            {"id": "p_cloud_opt1", "text": "1. Calibrate resource limits with realistic memory headroom (e.g. memory: 1.5Gi).\n2. Reconfigure the application to stream or paginate warm-up cache in chunks or offload cache to an external Redis cluster.\n3. Verify liveness/readiness probes have appropriate initialDelaySeconds."},
            {"id": "p_cloud_opt2", "text": "Delete the entire Kubernetes cluster and redeploy directly onto bare metal without container limits."},
            {"id": "p_cloud_opt3", "text": "Remove all memory limits so single pods can consume all host memory unconstrained until node kernel panic."},
            {"id": "p_cloud_opt4", "text": "Change the service from HTTP to FTP."}
        ],
        "bestOptionId": "p_cloud_opt1",
        "bestRubric": "Calibrating resource requests/limits, offloading local unbounded heap caching to external caching layer, and tuning liveness/readiness probes.",
        "points": 35
    },
    "ai_ml": {
        "id": "prac_ai",
        "domain": "ai_ml",
        "domainLabel": "AI/ML",
        "title": "Model Performance: Addressing Severe Distribution Shift & Overfitting",
        "scenarioText": "You built a deep neural net predicting loan default risk. During training, cross-entropy loss dropped to 0.04 with 98% accuracy. When tested against last quarter's newly originated loans, accuracy collapsed to 56%. What diagnostic and remediation protocol do you implement?",
        "contextSnippet": "Train Dataset: 2018-2022 historical applications (pre-inflation shock)\nTest Dataset: Q1 2026 applications\nObservations: Significant distribution shift in interest_rate and debt_to_income distributions.",
        "options": [
            {"id": "p_ai_opt1", "text": "1. Run population stability index (PSI) and Kolmogorov-Smirnov tests to quantify feature covariate shift.\n2. Retrain model incorporating recent macroeconomic cohorts with sample re-weighting.\n3. Add dropout, weight decay (L2), and early stopping to penalize memorization.\n4. Monitor calibration curves rather than raw uncalibrated accuracy."},
            {"id": "p_ai_opt2", "text": "Double the depth of the neural net by adding 20 more dense layers to memorize the new quarter as well."},
            {"id": "p_ai_opt3", "text": "Delete the 2026 data and assume the model is fine because historical training accuracy was 98%."},
            {"id": "p_ai_opt4", "text": "Convert all numeric inputs into random binary flags."}
        ],
        "bestOptionId": "p_ai_opt1",
        "bestRubric": "Measuring feature covariate drift with PSI/KS-tests, temporal retraining, applying architectural regularization (dropout/L2), and monitoring calibration.",
        "points": 35
    },
    "frontend": {
        "id": "prac_fe",
        "domain": "frontend",
        "domainLabel": "Frontend Development",
        "title": "Client Performance: High-Volume Virtualized List Stutter & Layout Thrashing",
        "scenarioText": "A real-time financial market dashboard displays 5,000 updating ticker rows. Users report the browser tab freezes and Chrome DevTools reveals Severe Layout Thrashing with long tasks lasting 600ms on every web-socket tick. How do you re-architect the rendering pipeline?",
        "contextSnippet": "DevTools Performance Trace:\nTask duration: 642ms\nFunction: updateRowDOM (querying offsetHeight inside loop and mutating style.height)\nVisible Viewport: ~20 rows at any time",
        "options": [
            {"id": "p_fe_opt1", "text": "1. Implement DOM Virtualization (e.g. react-window / TanStack Virtual) so only the ~25 visible rows exist in the DOM.\n2. Eliminate read-then-write layout thrashing (batch style reads and style writes).\n3. Throttle/buffer websocket rendering updates using requestAnimationFrame."},
            {"id": "p_fe_opt2", "text": "Render all 5,000 rows as unvirtualized nested HTML tables with inline styles."},
            {"id": "p_fe_opt3", "text": "Ask users to buy 32-core gaming laptops to view the web dashboard."},
            {"id": "p_fe_opt4", "text": "Stop updating ticker prices in the UI and show static numbers."}
        ],
        "bestOptionId": "p_fe_opt1",
        "bestRubric": "DOM virtualization for huge lists, eliminating forced synchronous layout reads inside write loops, and buffering renders with requestAnimationFrame.",
        "points": 35
    },
    "data_science": {
        "id": "prac_ds",
        "domain": "data_science",
        "domainLabel": "Data Science",
        "title": "Analytical Rigor: Discrepant Experiment Results & Simpson's Paradox",
        "scenarioText": "A product team ran an onboarding test. Globally, overall conversion for Variant B was lower than Variant A (4.2% vs 4.8%). However, when segmented by country, Variant B significantly outperformed Variant A in every individual country (US: 8% vs 6%, IN: 3% vs 2%, EU: 5% vs 4%). What statistical paradox is occurring and how do you resolve it?",
        "contextSnippet": "Total Users Variant A: 100,000 (80% US high-conversion cohort)\nTotal Users Variant B: 100,000 (80% IN lower-baseline cohort)\nResult: Aggregate conversion confounded by country traffic allocation disparity.",
        "options": [
            {"id": "p_ds_opt1", "text": "1. Recognize Simpson's Paradox caused by an unstratified confounding variable (unequal country traffic allocation).\n2. Calculate stratified / standardized average conversion weighted by true country proportions.\n3. Fix future randomizer split to stratify evenly across country segments."},
            {"id": "p_ds_opt2", "text": "Declare Variant A the absolute winner immediately and ignore the country-level data."},
            {"id": "p_ds_opt3", "text": "Assume the database corrupted the numbers and re-run without looking at segments."},
            {"id": "p_ds_opt4", "text": "Delete all data from India and Europe to make the aggregate match the US numbers."}
        ],
        "bestOptionId": "p_ds_opt1",
        "bestRubric": "Identifying Simpson's Paradox from non-stratified traffic allocation, computing weighted stratified conversion, and establishing stratified sampling.",
        "points": 35
    },
    "fullstack": {
        "id": "prac_fs",
        "domain": "fullstack",
        "domainLabel": "Full Stack Development",
        "title": "Architecture: Resilient Token Refresh & Concurrent Request Queueing",
        "scenarioText": "In a fullstack SPA and microservices backend, when an access token expires while a dashboard makes 8 parallel API calls simultaneously, the first call triggers a refresh, but the other 7 calls fail with 401 Unauthorized or cause race conditions generating 8 conflicting refresh requests. How do you design the client-server auth architecture?",
        "contextSnippet": "Client: Axios HTTP Interceptors with parallel dashboard widgets\nServer: Refresh Token rotation with one-time use invalidation policy",
        "options": [
            {"id": "p_fs_opt1", "text": "1. Implement an Axios response interceptor mutex/queue that detects 401, buffers subsequent requests into an array, executes a single refresh token request, and retries all queued requests with the new access token upon resolution.\n2. Server-side allows a grace period (e.g. 10 seconds) during refresh token rotation to absorb network race conditions."},
            {"id": "p_fs_opt2", "text": "Log the user out immediately whenever any single API returns 401."},
            {"id": "p_fs_opt3", "text": "Make all access tokens permanent with no expiration date."},
            {"id": "p_fs_opt4", "text": "Store user passwords in browser cookies and send them in plain text with every request."}
        ],
        "bestOptionId": "p_fs_opt1",
        "bestRubric": "Client-side request queueing/mutex interceptor to prevent duplicate refresh calls, coupled with server-side rotation grace window.",
        "points": 35
    }
}


# ==============================================================================
# ADAPTIVE ASSESSMENT ENGINE CORE
# ==============================================================================

class AdaptiveAssessmentEngine:
    MIN_QUESTIONS = 14
    MAX_QUESTIONS = 20
    DISCOVERY_QUESTIONS = 10

    @classmethod
    def get_discovery_questions(cls) -> List[Dict[str, Any]]:
        """Generates the initial mixed discovery question set (10 questions).
        Guarantees questions are distributed across multiple canonical domains,
        with at least 1 question per domain for all 7 domains, and no more than 2 from any domain.
        """
        selected: List[Dict[str, Any]] = []
        domain_counts: Dict[str, int] = {d["id"]: 0 for d in CANONICAL_DOMAINS}

        # First pass: Pick 1 good question from each of the 7 canonical domains
        for domain in CANONICAL_DOMAINS:
            d_id = domain["id"]
            candidates = [q for q in QUESTION_BANK if q["domain"] == d_id and q["difficulty"] in ["beginner", "intermediate"]]
            if candidates:
                q = candidates[0]
                selected.append(q)
                domain_counts[d_id] += 1

        # Second pass: Pick 3 additional questions from alternating domains to reach exactly 10
        second_pass_domains = ["cybersecurity", "backend", "cloud_devops"]
        for d_id in second_pass_domains:
            candidates = [q for q in QUESTION_BANK if q["domain"] == d_id and q["id"] not in [s["id"] for s in selected]]
            if candidates:
                selected.append(candidates[0])
                domain_counts[d_id] += 1

        return selected[:cls.DISCOVERY_QUESTIONS]

    @classmethod
    def select_next_adaptive_question(
        cls,
        answered_question_ids: Set[str],
        demonstrated_scores: Dict[str, int],
        domain_evidence_counts: Dict[str, int],
        total_answered: int
    ) -> Optional[Dict[str, Any]]:
        """Selects the next question adaptively seeking INFORMATION VALUE:
        - Probes depth/difficulty in promising domains (score >= 65)
        - Clarifies ambiguous domains with low evidence counts
        - Avoids already answered questions
        - Skips domains with conclusive low relevance/low score and sufficient evidence
        """
        if total_answered >= cls.MAX_QUESTIONS:
            return None

        unanswered = [q for q in QUESTION_BANK if q["id"] not in answered_question_ids]
        if not unanswered:
            return None

        promising_domains = [d for d, s in demonstrated_scores.items() if s >= 65]
        ambiguous_domains = [d for d, c in domain_evidence_counts.items() if c < 2]

        # Priority 1: If candidate is strong in a domain, test depth with an advanced or intermediate question
        if promising_domains:
            promising_sorted = sorted(promising_domains, key=lambda d: demonstrated_scores.get(d, 0), reverse=True)
            for d in promising_sorted:
                depth_candidates = [q for q in unanswered if q["domain"] == d and q["difficulty"] in ["intermediate", "advanced"]]
                if depth_candidates:
                    return depth_candidates[0]

        # Priority 2: Clarify ambiguous domains with low evidence count
        if ambiguous_domains:
            for d in ambiguous_domains:
                clarify_candidates = [q for q in unanswered if q["domain"] == d]
                if clarify_candidates:
                    return clarify_candidates[0]

        # Priority 3: Pick highest-weighted remaining question across any domain not over-tested
        unanswered.sort(key=lambda q: (
            q["difficulty"] == "advanced",
            domain_evidence_counts.get(q["domain"], 0) < 3
        ), reverse=True)

        return unanswered[0]

    @classmethod
    def calculate_domain_knowledge_signals(
        cls,
        answers: Dict[str, str], # question_id -> option_id
        confidences: Dict[str, ConfidenceLevel]
    ) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, List[str]], Dict[str, str], Dict[str, str]]:
        """Calculates demonstrated knowledge signals (0-100), evidence counts, demonstrated skills,
        confidence ratings, and evidence strength per domain.
        NOTE: These are assessment signals, not real-world expertise percentages.
        """
        domain_earned: Dict[str, int] = {d["id"]: 0 for d in CANONICAL_DOMAINS}
        domain_possible: Dict[str, int] = {d["id"]: 0 for d in CANONICAL_DOMAINS}
        domain_evidence: Dict[str, int] = {d["id"]: 0 for d in CANONICAL_DOMAINS}
        domain_skills: Dict[str, Set[str]] = {d["id"]: set() for d in CANONICAL_DOMAINS}
        domain_conf_counts: Dict[str, Dict[str, int]] = {d["id"]: {"high": 0, "med": 0, "low": 0} for d in CANONICAL_DOMAINS}

        bank_map = {q["id"]: q for q in QUESTION_BANK}

        for q_id, opt_id in answers.items():
            q = bank_map.get(q_id)
            if not q:
                continue

            domain = q["domain"]
            domain_evidence[domain] += 1
            pts = q.get("points", 25)
            domain_possible[domain] += pts

            conf = confidences.get(q_id, "confident")
            if conf in ["very_confident", "confident"]:
                domain_conf_counts[domain]["high"] += 1
            elif conf == "somewhat_confident":
                domain_conf_counts[domain]["med"] += 1
            else:
                domain_conf_counts[domain]["low"] += 1

            if opt_id == q["correctOptionId"]:
                domain_earned[domain] += pts
                domain_skills[domain].add(q["evidenceSkill"])

        demonstrated_scores: Dict[str, int] = {}
        evidence_strength: Dict[str, str] = {}
        confidence_signals: Dict[str, str] = {}
        uncertainty: Dict[str, str] = {}

        for d in CANONICAL_DOMAINS:
            d_id = d["id"]
            poss = domain_possible[d_id]
            earned = domain_earned[d_id]
            ev_cnt = domain_evidence[d_id]

            if poss > 0:
                raw_score = int(round((earned / poss) * 100.0))
                # Bound between 10 and 95 (never claim 100% expert or 0% complete incompetence from assessment)
                score = max(10, min(95, raw_score))
            else:
                score = 0

            demonstrated_scores[d_id] = score

            # Evidence strength calculation
            if ev_cnt >= 3 and score >= 65:
                strength = "Strong Evidence"
            elif ev_cnt >= 2:
                strength = "Moderate Evidence"
            elif ev_cnt == 1:
                strength = "Emerging Signal"
            else:
                strength = "Limited Evidence"
            evidence_strength[d_id] = strength

            # Uncertainty calculation
            if ev_cnt == 0:
                unc = "High Uncertainty"
            elif ev_cnt == 1:
                unc = "Moderate Uncertainty"
            elif ev_cnt >= 2 and (score >= 75 or score <= 35):
                unc = "Low Uncertainty"
            else:
                unc = "Balanced"
            uncertainty[d_id] = unc

            # Aggregate confidence
            high_c = domain_conf_counts[d_id]["high"]
            low_c = domain_conf_counts[d_id]["low"]
            if high_c > low_c:
                conf_str = "High"
            elif high_c == low_c and ev_cnt > 0:
                conf_str = "Medium"
            elif low_c > high_c:
                conf_str = "Calibrating"
            else:
                conf_str = "Uncalibrated"
            confidence_signals[d_id] = conf_str

        skills_demonstrated_clean = {k: sorted(list(v)) for k, v in domain_skills.items()}

        return demonstrated_scores, domain_evidence, skills_demonstrated_clean, confidence_signals, evidence_strength

    @classmethod
    def evaluate_practical_challenge(
        cls,
        scenario_id: str,
        selected_option_id: str,
        reasoning: Optional[str] = ""
    ) -> Tuple[int, str]:
        """Evaluates applied challenge deterministically.
        Returns (practical_score_0_to_100, applied_feedback_summary).
        """
        scenario = None
        for s in PRACTICAL_CHALLENGES.values():
            if s["id"] == scenario_id:
                scenario = s
                break

        if not scenario:
            return 50, "Practical response received."

        is_best = (selected_option_id == scenario["bestOptionId"])
        if is_best:
            score = 88
            feedback = f"Strong applied reasoning: {scenario['bestRubric']}"
        else:
            score = 45
            feedback = f"Suboptimal mitigation approach. Recommended applied strategy: {scenario['bestRubric']}"

        if reasoning and len(reasoning.strip()) > 30:
            score = min(96, score + 6)

        return score, feedback

    @classmethod
    def build_career_intelligence_profile(
        cls,
        user_id: str,
        demonstrated_scores: Dict[str, int],
        domain_evidence_counts: Dict[str, int],
        skills_demonstrated: Dict[str, List[str]],
        confidence_signals: Dict[str, str],
        evidence_strength: Dict[str, str],
        interest_ratings: Dict[str, InterestRating],
        scenario_preference: Optional[str],
        practical_scores: Dict[str, int],
        total_questions_answered: int
    ) -> CareerIntelligenceProfile:
        """Synthesizes the complete Career Intelligence Profile:
        - Multi-domain detection -> triggers CombinationEngine
        - Specialist detection
        - High interest + low knowledge interpretation
        - High knowledge + low interest interpretation
        - Breadth vs Depth analysis
        - Theory vs Practical analysis
        - Career pathway alignment with transferable skills
        """
        # 1. Multi-domain detection: >= 3 domains with demonstrated knowledge >= 68
        strong_domains = [d for d, s in demonstrated_scores.items() if s >= 68]
        is_multi_domain = len(strong_domains) >= 3

        # 2. Specialist detection: 1-2 domains strong (>= 75), rest <= 45
        is_specialist = False
        if len(strong_domains) in [1, 2]:
            other_scores = [s for d, s in demonstrated_scores.items() if d not in strong_domains]
            if other_scores and max(other_scores) <= 50:
                is_specialist = True

        # 3. Breadth vs Depth analysis
        total_domains_tested = sum(1 for c in domain_evidence_counts.values() if c > 0)
        avg_practical = sum(practical_scores.values()) / max(1, len(practical_scores))
        avg_demonstrated = sum(demonstrated_scores.values()) / max(1, len(demonstrated_scores))

        if total_domains_tested >= 5 and avg_demonstrated >= 60 and avg_practical < 60:
            breadth_vs_depth = "Breadth > Depth"
        elif is_specialist:
            breadth_vs_depth = "Specialist Depth"
        else:
            breadth_vs_depth = "Balanced Technical Exploration"

        # 4. Theory vs Practical analysis
        if avg_demonstrated >= 70 and avg_practical < 60:
            theory_vs_practical = "Strong Conceptual Knowledge with Developing Practical Evidence"
        elif avg_practical >= 70 and avg_demonstrated < 60:
            theory_vs_practical = "Practical Evidence is Stronger than Conceptual Assessment Evidence"
        else:
            theory_vs_practical = "Balanced Theory and Applied Evidence"

        # 5. Formulate Archetype Observation
        observations: List[str] = []

        if is_multi_domain:
            domain_labels = [DOMAIN_MAP[d]["label"] for d in strong_domains]
            observations.append(
                f"You demonstrated strong multi-disciplinary capabilities across {', '.join(domain_labels)}. "
                "Rather than forcing a single silo, ReSkillAI activated the Skill Combination Discovery Engine "
                "to surface synergistic hybrid engineering pathways."
            )
        elif is_specialist:
            spec_labels = [DOMAIN_MAP[d]["label"] for d in strong_domains]
            observations.append(
                f"You demonstrated focused competency depth in {', '.join(spec_labels)}. "
                "The system prioritized specialized development and advanced architectural pathways in these areas."
            )
        else:
            top_domain = max(demonstrated_scores.items(), key=lambda x: x[1])[0]
            observations.append(
                f"You demonstrated emerging technical strengths in {DOMAIN_MAP[top_domain]['label']}."
            )

        # Check for High Interest + Low Knowledge
        for d_id, rating in interest_ratings.items():
            if rating in ["very_interested", "interested"] and demonstrated_scores.get(d_id, 0) < 55:
                d_label = DOMAIN_MAP[d_id]["label"]
                observations.append(
                    f"High-interest developing pathway detected in {d_label}: You exhibited strong curiosity with emerging prior exposure. "
                    "ReSkillAI identified foundational gaps and structured prerequisites rather than discounting this pathway."
                )
                break

        # Check for High Knowledge + Low Interest
        for d_id, rating in interest_ratings.items():
            if rating in ["not_interested", "slightly_interested"] and demonstrated_scores.get(d_id, 0) >= 70:
                d_label = DOMAIN_MAP[d_id]["label"]
                observations.append(
                    f"Demonstrated capability in {d_label} with lower interest: Your solid competence is recognized as a high-value "
                    "transferable foundation for adjacent pathways without forcing role selection."
                )
                break

        profile_observation = " ".join(observations)

        # 6. Build DomainKnowledgeSignal objects
        domain_signals_dict: Dict[str, DomainKnowledgeSignal] = {}
        for d in CANONICAL_DOMAINS:
            d_id = d["id"]
            prac_val = practical_scores.get(d_id, int(demonstrated_scores.get(d_id, 0) * 0.85))
            int_val = interest_ratings.get(d_id, "interested")

            int_map = {
                "not_interested": "Low",
                "slightly_interested": "Moderate",
                "interested": "High",
                "very_interested": "Very High"
            }

            unc = "Low" if domain_evidence_counts.get(d_id, 0) >= 3 else ("Moderate" if domain_evidence_counts.get(d_id, 0) >= 2 else "High")

            domain_signals_dict[d_id] = DomainKnowledgeSignal(
                domain=d_id,
                domainLabel=d["label"],
                demonstratedKnowledge=demonstrated_scores.get(d_id, 0),
                evidenceCount=domain_evidence_counts.get(d_id, 0),
                skillsDemonstrated=skills_demonstrated.get(d_id, []),
                confidenceSignal=confidence_signals.get(d_id, "Medium"),
                practicalScore=prac_val,
                interestLevel=int_map.get(int_val, "Moderate"),
                evidenceStrength=evidence_strength.get(d_id, "Developing"),
                uncertainty=unc
            )

        # 7. Discovered Combinations via CombinationEngine
        all_demonstrated_skills = []
        for s_list in skills_demonstrated.values():
            all_demonstrated_skills.extend(s_list)

        temp_profile = StudentProfile(
            id=user_id,
            skills=[Skill(name=s, proficiency=75) for s in all_demonstrated_skills]
        )

        discovered_raw = CombinationEngine.discover_combinations(temp_profile)
        discovered_combinations: List[DiscoveredCombinationResult] = []
        for dc in discovered_raw:
            discovered_combinations.append(
                DiscoveredCombinationResult(
                    career=dc["career"],
                    combination=dc["combination"],
                    confidence=dc["confidence"],
                    supportingSkills=dc["supportingSkills"],
                    missingSkills=dc["missingSkills"],
                    explanation=dc["explanation"]
                )
            )

        # 8. Career Pathway Analysis (connecting Knowledge + Interest + Practical + Transferable)
        relevant_pathways: List[CareerPathwayResult] = []

        for domain in CANONICAL_DOMAINS:
            d_id = domain["id"]
            career = get_career_by_id(domain["careerId"])
            know_score = demonstrated_scores.get(d_id, 0)
            int_rating = interest_ratings.get(d_id, "interested")
            int_numeric = {"not_interested": 20, "slightly_interested": 45, "interested": 75, "very_interested": 95}.get(int_rating, 60)
            prac_score = practical_scores.get(d_id, int(know_score * 0.85))

            matched_skills = [s for s in career.coreSkills if s in skills_demonstrated.get(d_id, []) or any(s.lower() in ds.lower() for ds in all_demonstrated_skills)]
            missing_skills = [s for s in career.coreSkills if s not in matched_skills]

            transfer_res = TransferabilityEngine.calculate_transferability(temp_profile, career.id)
            transferable = [ts for ts in transfer_res.get("transferableSkills", []) if ts not in matched_skills]

            match_score = int(round(know_score * 0.40 + prac_score * 0.35 + int_numeric * 0.25))
            match_score = max(15, min(96, match_score))

            know_alignment = "Strong" if know_score >= 70 else ("Developing" if know_score >= 45 else "Foundational")
            prac_evidence = "Strong" if prac_score >= 70 else ("Developing" if prac_score >= 45 else "Emerging")

            int_display = {"not_interested": "Low", "slightly_interested": "Moderate", "interested": "High", "very_interested": "Very High"}.get(int_rating, "Moderate")

            explanation = (
                f"Demonstrated {know_alignment.lower()} knowledge ({know_score} signal) with {prac_evidence.lower()} practical evidence. "
                f"Interest is {int_display.lower()}. "
                f"{len(matched_skills)} core competencies demonstrated; key development priority: {missing_skills[0] if missing_skills else 'advanced architecture'}."
            )

            relevant_pathways.append(
                CareerPathwayResult(
                    careerId=career.id,
                    title=career.title,
                    category=career.category,
                    matchScore=match_score,
                    knowledgeAlignment=know_alignment,
                    interestLevel=int_display,
                    practicalEvidence=prac_evidence,
                    existingSkills=matched_skills,
                    transferableSkills=transferable,
                    missingSkills=missing_skills,
                    requiredSkills=career.coreSkills,
                    explanation=explanation
                )
            )

        relevant_pathways.sort(key=lambda p: p.matchScore, reverse=True)

        # 9. Next Development Priorities
        suggested_development: List[str] = []
        if relevant_pathways:
            top_p = relevant_pathways[0]
            if top_p.missingSkills:
                suggested_development.append(f"Close primary gap in {top_p.title}: Master {top_p.missingSkills[0]}.")
            if len(top_p.missingSkills) > 1:
                suggested_development.append(f"Strengthen secondary prerequisite: {top_p.missingSkills[1]}.")

        if breadth_vs_depth == "Breadth > Depth":
            suggested_development.append("Prioritize an end-to-end capstone project to translate broad conceptual exposure into deep applied evidence.")
        elif theory_vs_practical.startswith("Strong Conceptual"):
            suggested_development.append("Focus on production-grade implementation and debugging labs to close the theory-practical gap.")

        return CareerIntelligenceProfile(
            userId=user_id,
            completedAt=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            totalQuestionsAnswered=total_questions_answered,
            isMultiDomain=is_multi_domain,
            profileObservation=profile_observation,
            breadthVsDepth=breadth_vs_depth,
            theoryVsPractical=theory_vs_practical,
            domainSignals=domain_signals_dict,
            discoveredCombinations=discovered_combinations,
            relevantPathways=relevant_pathways,
            suggestedNextDevelopment=suggested_development
        )

    @classmethod
    def apply_assessment_to_student_profile(
        cls,
        profile: StudentProfile,
        intelligence_profile: CareerIntelligenceProfile
    ) -> StudentProfile:
        """Applies assessment discoveries into the canonical StudentProfile store,
        updating verified skills, assessmentSignals, target career pathways, and state.
        """
        existing_skills_map = {s.name.lower().strip(): s for s in profile.skills}

        for domain_id, signal in intelligence_profile.domainSignals.items():
            for skill_name in signal.skillsDemonstrated:
                s_key = skill_name.lower().strip()
                cat = "Security" if domain_id == "cybersecurity" else (
                    "Backend" if domain_id == "backend" else (
                        "Frontend" if domain_id == "frontend" else (
                            "Cloud" if domain_id == "cloud_devops" else (
                                "AI/ML" if domain_id == "ai_ml" else (
                                    "Database" if "sql" in s_key or "mongo" in s_key else "Tools"
                                )
                            )
                        )
                    )
                )

                prof = max(60, signal.demonstratedKnowledge)
                level = "Proficient" if prof >= 75 else "Familiar"

                if s_key in existing_skills_map:
                    existing = existing_skills_map[s_key]
                    existing.proficiency = max(existing.proficiency, prof)
                    existing.verified = True
                    existing.detectedFrom = "Adaptive Cognitive Assessment"
                else:
                    new_skill = Skill(
                        name=skill_name,
                        category=cat,
                        proficiency=prof,
                        level=level,
                        verified=True,
                        detectedFrom="Adaptive Cognitive Assessment"
                    )
                    profile.skills.append(new_skill)
                    existing_skills_map[s_key] = new_skill

        domain_prefs = [p.title for p in intelligence_profile.relevantPathways[:3]]
        domain_know_scores = {d: s.demonstratedKnowledge for d, s in intelligence_profile.domainSignals.items()}

        raw_combinations = [
            {
                "career": c.career,
                "combination": c.combination,
                "confidence": c.confidence,
                "supportingSkills": c.supportingSkills,
                "missingSkills": c.missingSkills,
                "explanation": c.explanation
            }
            for c in intelligence_profile.discoveredCombinations
        ]

        raw_pathways = [
            {
                "careerId": p.careerId,
                "title": p.title,
                "category": p.category,
                "matchScore": p.matchScore,
                "knowledgeAlignment": p.knowledgeAlignment,
                "interestLevel": p.interestLevel,
                "practicalEvidence": p.practicalEvidence,
                "existingSkills": p.existingSkills,
                "transferableSkills": p.transferableSkills,
                "missingSkills": p.missingSkills,
                "requiredSkills": p.requiredSkills,
                "explanation": p.explanation
            }
            for p in intelligence_profile.relevantPathways
        ]

        profile.assessmentSignals = AssessmentSignals(
            domainPreferences=domain_prefs,
            problemSolvingStyle=intelligence_profile.theoryVsPractical,
            workStyleSignals=[intelligence_profile.breadthVsDepth],
            primaryMotivation=f"Focus on {intelligence_profile.relevantPathways[0].title if intelligence_profile.relevantPathways else 'Technical Growth'}",
            careerInterestScores=domain_know_scores,
            demonstratedKnowledge=domain_know_scores,
            interestSignals={d: s.interestLevel for d, s in intelligence_profile.domainSignals.items()},
            confidenceSignal={d: s.confidenceSignal for d, s in intelligence_profile.domainSignals.items()},
            practicalScores={d: s.practicalScore for d, s in intelligence_profile.domainSignals.items()},
            evidenceCounts={d: s.evidenceCount for d, s in intelligence_profile.domainSignals.items()},
            skillsDemonstrated=[s for d in intelligence_profile.domainSignals.values() for s in d.skillsDemonstrated],
            isMultiDomain=intelligence_profile.isMultiDomain,
            discoveredCombinations=raw_combinations,
            profileObservation=intelligence_profile.profileObservation,
            breadthVsDepth=intelligence_profile.breadthVsDepth,
            theoryVsPractical=intelligence_profile.theoryVsPractical,
            relevantPathways=raw_pathways
        )

        if intelligence_profile.relevantPathways:
            top_career = intelligence_profile.relevantPathways[0]
            profile.targetCareerId = top_career.careerId
            profile.careerInterest = top_career.title

        profile.profileState = "PERSONALIZED"
        profile.profileCompleteness = 100

        return profile

adaptive_assessment_engine = AdaptiveAssessmentEngine()
