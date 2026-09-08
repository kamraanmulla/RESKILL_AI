import {
  StudentProfile,
  CareerRole,
  CareerMatch,
  SkillGapItem,
  RoadmapStep,
  LearningResource,
  JobOpportunity,
  ProgressStats
} from '../types';

export const mockStudent: StudentProfile = {
  id: 'std_01',
  name: 'Parvez Ahmed',
  email: 'parvez.ahmed@apex.edu.in',
  phone: '+91 98450 21980',
  degree: 'Bachelor of Technology in Computer Science & Engineering',
  institution: 'Apex Institute of Technology',
  graduationYear: 2026,
  cgpa: 8.7,
  bio: 'Final-year Computer Science undergraduate passionate about full-stack web architectures, distributed systems, and modern developer tooling. Seeking an entry-level software engineering trajectory.',
  targetCareerId: 'career_fullstack',
  resumeFile: {
    name: 'Parvez_Ahmed_Resume_2026.pdf',
    size: '248 KB',
    uploadedAt: 'Yesterday at 4:15 PM'
  },
  experience: [
    {
      title: 'Frontend Engineering Intern',
      company: 'Nexus Software Labs',
      period: 'May 2025 – Jul 2025 (3 mos)',
      description: 'Engineered responsive client dashboards in React and TypeScript. Improved client-side load latency by 28% through bundle optimization and memoization.'
    },
    {
      title: 'Open Source Contributor & Peer Tutor',
      company: 'Campus Dev Club',
      period: 'Aug 2024 – Present',
      description: 'Mentored 40+ junior peers in data structures, git collaboration workflows, and modern web standards.'
    }
  ],
  projects: [
    {
      title: 'CampusTrade — Student Marketplace',
      tech: ['React', 'Node.js', 'Express', 'MongoDB'],
      period: 'Jan 2025 – Apr 2025',
      description: 'Built a peer-to-peer campus marketplace platform featuring verified student email authentication, real-time item listing, and responsive search filtering.'
    },
    {
      title: 'VisualPath — Algorithm Visualizer',
      tech: ['TypeScript', 'React', 'Canvas API'],
      period: 'Oct 2024',
      description: 'Developed an interactive pathfinding and sorting algorithm visualizer with step-by-step state inspection for educational purposes.'
    }
  ],
  certifications: [
    {
      title: 'Meta Front-End Developer Professional Certificate',
      issuer: 'Coursera / Meta',
      year: '2025',
      credentialId: 'META-FE-99824'
    },
    {
      title: 'AWS Certified Cloud Practitioner',
      issuer: 'Amazon Web Services',
      year: '2025',
      credentialId: 'AWS-CCP-10492'
    }
  ],
  skills: [
    { name: 'JavaScript', category: 'Frontend', proficiency: 85, level: 'Proficient', verified: true, detectedFrom: 'CampusTrade, Nexus Internship' },
    { name: 'React', category: 'Frontend', proficiency: 80, level: 'Proficient', verified: true, detectedFrom: 'Nexus Internship, VisualPath' },
    { name: 'HTML/CSS', category: 'Frontend', proficiency: 90, level: 'Expert', verified: true, detectedFrom: 'Meta Certificate' },
    { name: 'TypeScript', category: 'Frontend', proficiency: 60, level: 'Familiar', verified: true, detectedFrom: 'VisualPath' },
    { name: 'Node.js', category: 'Backend', proficiency: 55, level: 'Familiar', verified: true, detectedFrom: 'CampusTrade' },
    { name: 'Express', category: 'Backend', proficiency: 50, level: 'Familiar', verified: true, detectedFrom: 'CampusTrade' },
    { name: 'REST APIs', category: 'Backend', proficiency: 40, level: 'Novice', verified: false, detectedFrom: 'Coursework' },
    { name: 'MongoDB', category: 'Database', proficiency: 60, level: 'Familiar', verified: true, detectedFrom: 'CampusTrade' },
    { name: 'PostgreSQL', category: 'Database', proficiency: 35, level: 'Novice', verified: false, detectedFrom: 'Academic Labs' },
    { name: 'Git', category: 'Tools', proficiency: 70, level: 'Proficient', verified: true, detectedFrom: 'GitHub activity' },
    { name: 'Docker', category: 'Tools', proficiency: 25, level: 'Novice', verified: false, detectedFrom: 'Self-study' },
    { name: 'Testing (Jest/Unit)', category: 'Tools', proficiency: 20, level: 'Novice', verified: false, detectedFrom: 'Basic coursework' },
    { name: 'System Design', category: 'Other', proficiency: 30, level: 'Novice', verified: false, detectedFrom: 'Reading' },
    { name: 'Agile & Scrum', category: 'Other', proficiency: 75, level: 'Proficient', verified: true, detectedFrom: 'Nexus Internship' }
  ],
  preferences: {
    weeklyHours: 12,
    learningStyle: 'video',
    notifications: true
  }
};

export const mockCareers: CareerRole[] = [
  {
    id: 'career_fullstack',
    title: 'Full Stack Developer',
    slug: 'full-stack-developer',
    category: 'Software Engineering',
    description: 'Bridges client interfaces with robust server architectures, managing database persistence, API contracts, and deployment pipelines.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['JavaScript', 'React', 'Node.js', 'REST APIs', 'MongoDB', 'Git'],
    secondarySkills: ['Docker', 'Testing', 'TypeScript', 'CI/CD'],
    currentMatchPercentage: 82,
    avgSalary: '₹7.5 – 12 LPA',
    demandLevel: 'Very High',
    marketInsight: 'High demand across startups and tech firms looking for engineers capable of end-to-end product delivery.'
  },
  {
    id: 'career_frontend',
    title: 'Frontend Developer',
    slug: 'frontend-developer',
    category: 'Software Engineering',
    description: 'Crafts accessible, high-performance web applications with semantic HTML, modern CSS, client state management, and component systems.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['JavaScript', 'React', 'HTML/CSS', 'TypeScript', 'Git', 'Responsive Design'],
    secondarySkills: ['Performance Optimization', 'Jest/Cypress', 'Next.js', 'Tailwind CSS'],
    currentMatchPercentage: 88,
    avgSalary: '₹6.5 – 10.5 LPA',
    demandLevel: 'High',
    marketInsight: 'Strong alignment with your current profile. Your 85% JS and 90% HTML/CSS provide an immediate solid base.'
  },
  {
    id: 'career_backend',
    title: 'Backend Developer',
    slug: 'backend-developer',
    category: 'Software Engineering',
    description: 'Architects reliable server runtimes, data schemas, API gateways, background workers, authentication strategies, and microservices.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['Node.js', 'REST APIs', 'Express', 'SQL/PostgreSQL', 'MongoDB', 'Authentication'],
    secondarySkills: ['Docker', 'Redis', 'System Design', 'Testing'],
    currentMatchPercentage: 64,
    avgSalary: '₹7.0 – 11.5 LPA',
    demandLevel: 'Very High',
    marketInsight: 'Requires solidifying RESTful conventions, database querying, and containerization fundamentals.'
  },
  {
    id: 'career_data_analyst',
    title: 'Data Analyst',
    slug: 'data-analyst',
    category: 'Data & Analytics',
    description: 'Transforms raw business datasets into actionable intelligence through SQL queries, statistical models, and clean dashboard visualizations.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['SQL', 'Python', 'Excel', 'Data Visualization', 'Tableau/PowerBI', 'Statistics'],
    secondarySkills: ['Pandas', 'Business Acumen', 'A/B Testing'],
    currentMatchPercentage: 42,
    avgSalary: '₹5.5 – 9 LPA',
    demandLevel: 'High',
    marketInsight: 'Significant pivot required. Focus heavily on SQL, Python analytics libraries, and statistical interpretation.'
  },
  {
    id: 'career_ml_engineer',
    title: 'Machine Learning Engineer',
    slug: 'machine-learning-engineer',
    category: 'Artificial Intelligence',
    description: 'Researches, trains, validates, and deploys predictive machine learning and deep learning models into scalable production services.',
    experienceLevel: 'Intermediate',
    coreSkills: ['Python', 'Linear Algebra', 'PyTorch / TensorFlow', 'ML Algorithms', 'SQL', 'Model Deployment'],
    secondarySkills: ['MLOps', 'Docker', 'FastAPI', 'Cloud Pipelines'],
    currentMatchPercentage: 35,
    avgSalary: '₹9 – 16 LPA',
    demandLevel: 'Very High',
    marketInsight: 'Steeper learning curve requiring rigorous mathematics, model training fundamentals, and MLOps tooling.'
  },
  {
    id: 'career_cloud_engineer',
    title: 'Cloud Engineer',
    slug: 'cloud-engineer',
    category: 'Cloud & Infrastructure',
    description: 'Provisions, monitors, secures, and automates multi-cloud infrastructure and continuous integration/continuous delivery pipelines.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['AWS/Azure', 'Linux', 'Docker', 'Networking', 'Terraform/IaC', 'Bash/Python'],
    secondarySkills: ['Kubernetes', 'CI/CD Pipelines', 'Cloud Security'],
    currentMatchPercentage: 48,
    avgSalary: '₹8 – 13 LPA',
    demandLevel: 'High',
    marketInsight: 'Your AWS Cloud Practitioner certification is a solid stepping stone; Linux and containerization are key next steps.'
  },
  {
    id: 'career_cybersecurity',
    title: 'Cybersecurity Analyst',
    slug: 'cybersecurity-analyst',
    category: 'Information Security',
    description: 'Safeguards enterprise network perimeters, performs vulnerability assessments, responds to security incidents, and audits system compliance.',
    experienceLevel: 'Entry-Level',
    coreSkills: ['Network Protocols', 'Linux', 'Vulnerability Assessment', 'Security Frameworks', 'SIEM Tools'],
    secondarySkills: ['Penetration Testing', 'Cryptography', 'Python Scripting'],
    currentMatchPercentage: 38,
    avgSalary: '₹6.5 – 11 LPA',
    demandLevel: 'High',
    marketInsight: 'Demands specialized knowledge of network layers, threat intelligence, and defensive security tooling.'
  }
];

export const mockCareerMatch: CareerMatch = {
  careerId: 'career_fullstack',
  careerTitle: 'Full Stack Developer',
  overallMatch: 82,
  strongMatches: [
    { skill: 'JavaScript', studentLevel: 85, requiredLevel: 80, note: 'Exceeds baseline. Strong DOM and async fundamentals.' },
    { skill: 'React', studentLevel: 80, requiredLevel: 75, note: 'Exceeds baseline. Proven component architecture.' },
    { skill: 'HTML/CSS', studentLevel: 90, requiredLevel: 80, note: 'Exceeds baseline. Clean semantic structuring.' },
    { skill: 'Git & Version Control', studentLevel: 70, requiredLevel: 65, note: 'Adequate branching and pull request workflow.' }
  ],
  needsImprovement: [
    { skill: 'Node.js Runtime', studentLevel: 55, requiredLevel: 80, gap: 25, priority: 'High' },
    { skill: 'REST API Architecture', studentLevel: 40, requiredLevel: 75, gap: 35, priority: 'High' },
    { skill: 'Docker Containerization', studentLevel: 25, requiredLevel: 60, gap: 35, priority: 'Medium' },
    { skill: 'Unit & Integration Testing', studentLevel: 20, requiredLevel: 60, gap: 40, priority: 'Medium' }
  ],
  benchmarkComparison: [
    { skill: 'JavaScript', studentLevel: 85, benchmarkLevel: 80, category: 'Frontend' },
    { skill: 'React', studentLevel: 80, benchmarkLevel: 75, category: 'Frontend' },
    { skill: 'HTML/CSS', studentLevel: 90, benchmarkLevel: 80, category: 'Frontend' },
    { skill: 'Node.js', studentLevel: 55, benchmarkLevel: 80, category: 'Backend' },
    { skill: 'REST APIs', studentLevel: 40, benchmarkLevel: 75, category: 'Backend' },
    { skill: 'MongoDB', studentLevel: 60, benchmarkLevel: 70, category: 'Database' },
    { skill: 'Git', studentLevel: 70, benchmarkLevel: 65, category: 'Tools' },
    { skill: 'Docker', studentLevel: 25, benchmarkLevel: 60, category: 'Tools' },
    { skill: 'Testing', studentLevel: 20, benchmarkLevel: 60, category: 'Tools' }
  ]
};

export const mockSkillGaps: SkillGapItem[] = [
  {
    skill: 'JavaScript',
    category: 'Frontend',
    yourLevel: 85,
    requiredLevel: 80,
    gap: 0,
    priority: 'Strong',
    status: 'Mastered',
    recommendation: 'Solid mastery. Maintain by exploring advanced patterns like closures and event loops.'
  },
  {
    skill: 'React',
    category: 'Frontend',
    yourLevel: 80,
    requiredLevel: 75,
    gap: 0,
    priority: 'Strong',
    status: 'Mastered',
    recommendation: 'Proficient. Deepen custom hooks and React Server Components.'
  },
  {
    skill: 'Node.js',
    category: 'Backend',
    yourLevel: 55,
    requiredLevel: 80,
    gap: 25,
    priority: 'High',
    status: 'In Progress',
    recommendation: 'Crucial server runtime. Focus on Event Emitter, Streams, and async file systems.'
  },
  {
    skill: 'REST APIs',
    category: 'Backend',
    yourLevel: 40,
    requiredLevel: 75,
    gap: 35,
    priority: 'High',
    status: 'In Progress',
    recommendation: 'Top priority. Understand HTTP status codes, middleware, error handling, and route design.'
  },
  {
    skill: 'Docker',
    category: 'Tools',
    yourLevel: 25,
    requiredLevel: 60,
    gap: 35,
    priority: 'Medium',
    status: 'Not Started',
    recommendation: 'Learn writing multi-stage Dockerfiles and running docker-compose for multi-container apps.'
  },
  {
    skill: 'Testing (Jest/Cypress)',
    category: 'Tools',
    yourLevel: 20,
    requiredLevel: 60,
    gap: 40,
    priority: 'Medium',
    status: 'Not Started',
    recommendation: 'Implement unit testing on Express endpoints and React UI interactions.'
  },
  {
    skill: 'MongoDB',
    category: 'Database',
    yourLevel: 60,
    requiredLevel: 70,
    gap: 10,
    priority: 'Low',
    status: 'In Progress',
    recommendation: 'Familiar. Practice complex aggregation pipelines and schema indexes.'
  }
];

export const mockRoadmap: RoadmapStep[] = [
  {
    id: 'step_01',
    stepNumber: '01',
    title: 'HTML5 & Modern CSS Architecture',
    status: 'completed',
    whyItMatters: 'Semantic markup and responsive layouts form the non-negotiable bedrock of all client-side web software.',
    topics: [
      'Semantic tags & accessibility (WCAG AA)',
      'CSS Grid, Flexbox & container queries',
      'CSS variables and design tokens',
      'Mobile-first responsive layouts'
    ],
    recommendedResources: [
      { title: 'Modern CSS Masterclass', type: 'Course', duration: '3h 15m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'MDN Web Accessibility Guide', type: 'Documentation', duration: '45m', url: 'https://developer.mozilla.org', platform: 'MDN' }
    ],
    practiceProject: {
      title: 'Accessible Component Style Guide',
      description: 'Build a standalone UI library adhering to WCAG 2.1 accessibility benchmarks.',
      deliverable: 'Live demo with zero axe-core contrast and accessibility warnings.'
    },
    estimatedTime: '8 hours',
    skillKey: 'HTML/CSS'
  },
  {
    id: 'step_02',
    stepNumber: '02',
    title: 'Modern JavaScript (ES6+) & Async Runtimes',
    status: 'completed',
    whyItMatters: 'Mastery of event loops, asynchronous promises, closures, and prototypical inheritance enables robust state manipulation.',
    topics: [
      'ES Modules, destructuring & rest/spread',
      'Promises, async/await and error boundaries',
      'Event loop, microtasks vs macrotasks',
      'Functional methods: map, filter, reduce'
    ],
    recommendedResources: [
      { title: 'JavaScript Event Loop Visualized', type: 'Video', duration: '26m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'Deep JavaScript Foundations', type: 'Course', duration: '5h', url: 'https://youtube.com', platform: 'YouTube' }
    ],
    practiceProject: {
      title: 'Async Task Orchestrator',
      description: 'Write a zero-dependency async queue with concurrency limits and retry exponential backoff.',
      deliverable: 'Tested npm-style utility module.'
    },
    estimatedTime: '12 hours',
    skillKey: 'JavaScript'
  },
  {
    id: 'step_03',
    stepNumber: '03',
    title: 'React & Component-Driven Architecture',
    status: 'completed',
    whyItMatters: 'Industry standard for declarative UI building, virtual DOM diffing, and reactive client state.',
    topics: [
      'Declarative rendering & reconciliation',
      'Hooks lifecycle: useEffect, useMemo, useCallback',
      'Custom hooks for business logic extraction',
      'Context API and scalable state boundaries'
    ],
    recommendedResources: [
      { title: 'React 18 Architecture Deep Dive', type: 'Video', duration: '1h 45m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'Official React Docs (react.dev)', type: 'Documentation', duration: '2h', url: 'https://react.dev', platform: 'React.dev' }
    ],
    practiceProject: {
      title: 'Custom Headless UI Component Set',
      description: 'Build accessible tabs, modals, and dropdowns without third-party component libraries.',
      deliverable: 'Reusable React component package.'
    },
    estimatedTime: '16 hours',
    skillKey: 'React'
  },
  {
    id: 'step_04',
    stepNumber: '04',
    title: 'Node.js Runtime & Express Server Setup',
    status: 'in_progress',
    whyItMatters: 'Transforms a frontend developer into a full-stack engineer capable of authoring server processes and handling concurrent I/O.',
    topics: [
      'Node.js architecture & libuv threadpool',
      'File system (fs) and Stream buffers',
      'Express routing, app lifecycle & middleware pipeline',
      'Environment configuration and security headers (Helmet)'
    ],
    recommendedResources: [
      { title: 'Node.js Fundamentals for Full Stack', type: 'Video', duration: '2h 15m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'Express.js Production Best Practices', type: 'Article', duration: '30m', url: 'https://expressjs.com', platform: 'Documentation' }
    ],
    practiceProject: {
      title: 'Lightweight File Ingestion Server',
      description: 'Build a Node.js server that streams large CSV files and writes aggregated summaries.',
      deliverable: 'Express server with zero out-of-memory errors on 100MB inputs.'
    },
    estimatedTime: '14 hours',
    skillKey: 'Node.js'
  },
  {
    id: 'step_05',
    stepNumber: '05',
    title: 'REST API Design, Validation & Error Handling',
    status: 'in_progress',
    whyItMatters: 'Currently your largest profile gap (-35%). Clean RESTful design is the universal language between client and server.',
    topics: [
      'HTTP verbs, semantic status codes & idempotency',
      'REST resource modeling & URL structuring',
      'Request body validation with Zod / Joi',
      'Centralized error handling middleware & response formatting'
    ],
    recommendedResources: [
      { title: 'REST API Development Masterclass', type: 'Video', duration: '3h 00m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'API Security & Design Guidelines', type: 'Guide', duration: '40m', url: 'https://swagger.io', platform: 'Swagger' }
    ],
    practiceProject: {
      title: 'Full-Featured Course Management API',
      description: 'Create a production-ready REST API with pagination, filtering, search, and comprehensive error handling.',
      deliverable: 'Postman collection with 100% passing contract tests.'
    },
    estimatedTime: '16 hours',
    skillKey: 'REST APIs'
  },
  {
    id: 'step_06',
    stepNumber: '06',
    title: 'Database Modeling with MongoDB & Mongoose',
    status: 'upcoming',
    whyItMatters: 'Persistent storage, schema indexing, and relational reference modeling prevent severe production performance bottlenecks.',
    topics: [
      'Document schema design vs normalized tables',
      'Mongoose middleware & schema hooks',
      'Indexing strategies for high-frequency queries',
      'Aggregation pipeline for analytics queries'
    ],
    recommendedResources: [
      { title: 'MongoDB Aggregation Deep Dive', type: 'Video', duration: '2h 10m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'Mongoose Production Patterns', type: 'Article', duration: '45m', url: 'https://mongoosejs.com', platform: 'Mongoose Docs' }
    ],
    practiceProject: {
      title: 'Multi-Tenant Analytics Store',
      description: 'Design a document database schema supporting sub-second aggregation over 50,000 mock events.',
      deliverable: 'Mongoose model suite with benchmark scripts.'
    },
    estimatedTime: '12 hours',
    skillKey: 'MongoDB'
  },
  {
    id: 'step_07',
    stepNumber: '07',
    title: 'Authentication, Authorization & Security',
    status: 'upcoming',
    whyItMatters: 'Protects user data, credentials, and API routes from common vulnerabilities (OWASP Top 10).',
    topics: [
      'Password hashing with bcrypt and salting',
      'JWT tokens vs httpOnly cookie sessions',
      'Role-based access control (RBAC) middleware',
      'CORS policies, rate limiting & CSRF prevention'
    ],
    recommendedResources: [
      { title: 'Full Stack Authentication with JWT & Cookies', type: 'Video', duration: '1h 45m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'OWASP Top 10 Web Application Security', type: 'Report', duration: '1h', url: 'https://owasp.org', platform: 'OWASP' }
    ],
    practiceProject: {
      title: 'Zero-Trust Auth Microservice',
      description: 'Implement refresh-token rotation, account lockout on brute-force attempts, and email verification tokens.',
      deliverable: 'Secure authentication gateway with test coverage.'
    },
    estimatedTime: '14 hours',
    skillKey: 'Authentication'
  },
  {
    id: 'step_08',
    stepNumber: '08',
    title: 'Docker Containerization & Environments',
    status: 'upcoming',
    whyItMatters: 'Eliminates "works on my machine" bugs and prepares web applications for modern cloud platforms.',
    topics: [
      'Container fundamentals vs virtual machines',
      'Writing multi-stage Dockerfiles for Node & React',
      'Docker Compose for local full-stack orchestration',
      'Volume mounting, ports & environment segregation'
    ],
    recommendedResources: [
      { title: 'Docker for Developers: Zero to Hero', type: 'Video', duration: '2h 30m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'Container Best Practices by Docker', type: 'Documentation', duration: '35m', url: 'https://docs.docker.com', platform: 'Docker Docs' }
    ],
    practiceProject: {
      title: 'Containerized Full Stack Application',
      description: 'Create a single docker-compose.yml running frontend, backend, and MongoDB with persistent volumes.',
      deliverable: 'One-command bootable repository.'
    },
    estimatedTime: '10 hours',
    skillKey: 'Docker'
  },
  {
    id: 'step_09',
    stepNumber: '09',
    title: 'CI/CD Pipelines, Testing & Production Deploy',
    status: 'upcoming',
    whyItMatters: 'Automates testing, enforces code style, and pushes verified code reliably into production environments.',
    topics: [
      'Unit & integration testing with Jest / Supertest',
      'GitHub Actions workflows for automated test runs',
      'Cloud deployment (Render, AWS EC2, or Railway)',
      'Basic application monitoring & error tracking'
    ],
    recommendedResources: [
      { title: 'Production Deployment & CI/CD Walkthrough', type: 'Video', duration: '2h 00m', url: 'https://youtube.com', platform: 'YouTube' },
      { title: 'GitHub Actions Automated CI Blueprint', type: 'Guide', duration: '30m', url: 'https://github.com', platform: 'GitHub Docs' }
    ],
    practiceProject: {
      title: 'Continuous Deployment Pipeline',
      description: 'Set up an automated GitHub Actions pipeline that lints, tests, builds, and deploys your full-stack app on every push to main.',
      deliverable: 'Live URL with green CI/CD badge.'
    },
    estimatedTime: '12 hours',
    skillKey: 'Deployment'
  }
];

export const mockLearningResources: LearningResource[] = [
  {
    id: 'res_01',
    title: 'Node.js Fundamentals for Full Stack Developers',
    platform: 'YouTube',
    level: 'Beginner',
    duration: '2h 15m',
    instructor: 'Dave Gray',
    url: 'https://www.youtube.com/watch?v=f2EqECiTBL8',
    skillTag: 'Node.js',
    roadmapStepId: 'step_04',
    rating: 4.9,
    isSaved: true
  },
  {
    id: 'res_02',
    title: 'REST API Development Masterclass with Express',
    platform: 'YouTube',
    level: 'Intermediate',
    duration: '3h 00m',
    instructor: 'Traversy Media',
    url: 'https://www.youtube.com/watch?v=-MTSQjw5DrM',
    skillTag: 'REST APIs',
    roadmapStepId: 'step_05',
    rating: 4.8,
    isSaved: true
  },
  {
    id: 'res_03',
    title: 'Docker for Developers: Zero to Containerized Hero',
    platform: 'YouTube',
    level: 'Intermediate',
    duration: '2h 30m',
    instructor: 'TechWorld with Nana',
    url: 'https://www.youtube.com/watch?v=3c-iBn73dDE',
    skillTag: 'Docker',
    roadmapStepId: 'step_08',
    rating: 4.9,
    isSaved: false
  },
  {
    id: 'res_04',
    title: 'Full Stack Authentication with JWT & HTTP-Only Cookies',
    platform: 'YouTube',
    level: 'Intermediate',
    duration: '1h 45m',
    instructor: 'PedroTech',
    url: 'https://www.youtube.com/watch?v=27KeYk-5vJw',
    skillTag: 'Authentication',
    roadmapStepId: 'step_07',
    rating: 4.7,
    isSaved: false
  },
  {
    id: 'res_05',
    title: 'MongoDB Aggregation Framework & Indexing Strategies',
    platform: 'YouTube',
    level: 'Intermediate',
    duration: '2h 10m',
    instructor: 'freeCodeCamp',
    url: 'https://www.youtube.com/watch?v=ofme2o29ngU',
    skillTag: 'MongoDB',
    roadmapStepId: 'step_06',
    rating: 4.8,
    isSaved: false
  },
  {
    id: 'res_06',
    title: 'Testing Express APIs with Jest & Supertest',
    platform: 'YouTube',
    level: 'Intermediate',
    duration: '1h 30m',
    instructor: 'Web Dev Simplified',
    url: 'https://www.youtube.com/watch?v=FKnzS_icpEk',
    skillTag: 'Testing',
    roadmapStepId: 'step_09',
    rating: 4.7,
    isSaved: false
  },
  {
    id: 'res_07',
    title: 'Clean Architecture in Node.js & Separation of Concerns',
    platform: 'Documentation',
    level: 'Advanced',
    duration: '45m',
    instructor: 'Khalil Stemmler',
    url: 'https://khalilstemmler.com',
    skillTag: 'Backend',
    roadmapStepId: 'step_04',
    rating: 4.9,
    isSaved: true
  },
  {
    id: 'res_08',
    title: 'PostgreSQL Essentials for Web Developers',
    platform: 'YouTube',
    level: 'Beginner',
    duration: '2h 45m',
    instructor: 'Amigoscode',
    url: 'https://www.youtube.com/watch?v=qw--VYLpxG4',
    skillTag: 'Database',
    roadmapStepId: 'step_06',
    rating: 4.6,
    isSaved: false
  }
];

export const mockJobs: JobOpportunity[] = [
  {
    id: 'job_01',
    title: 'Junior Full Stack Developer',
    company: 'Linear Technologies Partner Labs',
    location: 'Bengaluru, India',
    workMode: 'Hybrid',
    type: 'Full-time',
    matchPercentage: 87,
    matchedSkills: ['React', 'JavaScript', 'Node.js', 'HTML/CSS', 'Git'],
    missingSkills: ['Docker'],
    compensation: '₹7.2 – 9.5 LPA',
    postedAgo: '2 days ago',
    isSaved: true,
    description: 'We are seeking an early-career Full Stack Developer to build refined workspace tooling. You will collaborate on frontend interfaces and contribute to clean RESTful services.',
    responsibilities: [
      'Develop modular React and TypeScript components matching Figma design specifications.',
      'Maintain and extend Express API endpoints with input validation and error handling.',
      'Participate in weekly code reviews, sprint grooming, and integration testing.'
    ],
    qualifications: [
      'Strong grasp of modern JavaScript (ES6+) and component lifecycle in React.',
      'Working experience authoring Node.js servers and basic database queries.',
      'Familiarity with version control using Git and collaborative PR flows.'
    ]
  },
  {
    id: 'job_02',
    title: 'Graduate Frontend Engineer',
    company: 'Vercel Ecosystem Partners',
    location: 'Remote, India',
    workMode: 'Remote',
    type: 'Full-time',
    matchPercentage: 94,
    matchedSkills: ['React', 'JavaScript', 'HTML/CSS', 'Git', 'TypeScript'],
    missingSkills: ['Next.js App Router'],
    compensation: '₹8.0 – 11.0 LPA',
    postedAgo: 'Just now',
    isSaved: false,
    description: 'Join an agile product engineering group delivering high-velocity web experiences. We value semantic HTML, sub-second interaction speed, and craftsmanship.',
    responsibilities: [
      'Write clean, accessible, and high-performance client code in React.',
      'Collaborate with designers to implement consistent editorial design systems.',
      'Profile client-side bundle sizes and memory usage.'
    ],
    qualifications: [
      'Bachelor degree in Computer Science or demonstrable equivalent portfolio.',
      'Solid foundations in CSS Grid/Flexbox and accessibility standards.',
      'Proactive approach to self-directed learning.'
    ]
  },
  {
    id: 'job_03',
    title: 'Full Stack Engineering Intern',
    company: 'Stripe Integration Works',
    location: 'Bengaluru, India',
    workMode: 'On-site',
    type: 'Internship',
    matchPercentage: 82,
    matchedSkills: ['JavaScript', 'React', 'REST APIs', 'MongoDB'],
    missingSkills: ['Docker', 'Automated Testing'],
    compensation: '₹40,000 / month',
    postedAgo: '3 days ago',
    isSaved: false,
    description: 'A 6-month pre-placement internship opportunity for final year students. Gain hands-on exposure to payment workflows, API design, and cloud deployments.',
    responsibilities: [
      'Build internal administrative tooling dashboards in React.',
      'Assist senior engineers in writing webhook consumers and integration tests.',
      'Document public REST API endpoints and postman collections.'
    ],
    qualifications: [
      'Graduating in 2026 or late 2025 with strong academic fundamentals.',
      'Knowledge of full stack JavaScript technologies (MERN or similar).',
      'Enthusiasm for software reliability and testing.'
    ]
  },
  {
    id: 'job_04',
    title: 'Associate Backend Engineer',
    company: 'Razorpay NeoBank',
    location: 'Bengaluru, India',
    workMode: 'Hybrid',
    type: 'Full-time',
    matchPercentage: 68,
    matchedSkills: ['Node.js', 'MongoDB', 'Git'],
    missingSkills: ['Docker', 'Unit Testing', 'Redis'],
    compensation: '₹8.5 – 12.0 LPA',
    postedAgo: '5 days ago',
    isSaved: false,
    description: 'Help scale core payment processing microservices. You will work closely with database engineers and infrastructure specialists to ensure five-nines uptime.',
    responsibilities: [
      'Write high-throughput Node.js microservices handling concurrent transactions.',
      'Optimize database queries and schema indexes.',
      'Write unit and integration tests using Jest and mock stubs.'
    ],
    qualifications: [
      'Demonstrated understanding of asynchronous programming and database querying.',
      'Curiosity about distributed systems and cloud infrastructure.',
      'Strong problem-solving and algorithmic thinking.'
    ]
  },
  {
    id: 'job_05',
    title: 'Junior Web Applications Engineer',
    company: 'Postman Developer Lab',
    location: 'Hyderabad, India',
    workMode: 'Hybrid',
    type: 'Full-time',
    matchPercentage: 89,
    matchedSkills: ['JavaScript', 'React', 'REST APIs', 'HTML/CSS', 'Git'],
    missingSkills: ['Docker'],
    compensation: '₹9.0 – 13.0 LPA',
    postedAgo: '1 week ago',
    isSaved: true,
    description: 'Build web applications that empower millions of developers worldwide to design, test, and document their API workflows.',
    responsibilities: [
      'Develop collaborative API testing interfaces in modern React.',
      'Integrate REST and WebSocket endpoints for real-time collaboration.',
      'Ensure high code quality and test coverage across modules.'
    ],
    qualifications: [
      'Solid command of JavaScript, REST principles, and modern DOM APIs.',
      'Experience working on project codebases with version control.',
      'Excellent verbal and written technical communication.'
    ]
  }
];

export const mockProgressStats: ProgressStats = {
  careerReadiness: 72,
  skillsCompleted: { completed: 8, total: 14 },
  roadmapProgress: 56,
  learningHours: 24,
  studyStreakDays: 6,
  currentFocus: {
    title: 'Node.js & REST API Architecture',
    subtitle: 'Module 05 of 09 • REST API Design & Error Handling',
    hoursLeft: '6 hours remaining'
  },
  nextRecommendedAction: {
    action: 'Learn REST APIs',
    reason: 'REST APIs are currently one of the largest gaps for your selected career (-35% gap vs industry standard).',
    impact: '+9% Career Readiness',
    stepId: 'step_05'
  },
  recentActivity: [
    {
      id: 'act_01',
      action: 'Completed Module 03: React & Component Architecture',
      time: 'Yesterday at 5:30 PM',
      type: 'completed'
    },
    {
      id: 'act_02',
      action: 'Uploaded new resume version (Parvez_Ahmed_Resume_2026.pdf)',
      time: 'Yesterday at 4:15 PM',
      type: 'uploaded'
    },
    {
      id: 'act_03',
      action: 'Saved "Junior Full Stack Developer" at Linear Technologies',
      time: '2 days ago',
      type: 'saved'
    },
    {
      id: 'act_04',
      action: 'Started Module 04: Node.js Runtime & Express Server Setup',
      time: '3 days ago',
      type: 'started'
    },
    {
      id: 'act_05',
      action: 'Earned AWS Certified Cloud Practitioner badge',
      time: 'Last week',
      type: 'completed'
    }
  ]
};
