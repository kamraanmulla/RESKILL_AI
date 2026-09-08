export type SkillCategory = 'Frontend' | 'Backend' | 'Database' | 'Tools' | 'Other';

export type SkillLevel = 'Novice' | 'Familiar' | 'Proficient' | 'Expert';

export interface Skill {
  name: string;
  category: SkillCategory;
  proficiency: number; // 0 - 100
  level: SkillLevel;
  verified?: boolean;
  detectedFrom?: string;
}

export interface StudentExperience {
  title: string;
  company: string;
  period: string;
  description: string;
}

export interface StudentProject {
  title: string;
  tech: string[];
  period: string;
  description: string;
  link?: string;
}

export interface StudentCertification {
  title: string;
  issuer: string;
  year: string;
  credentialId?: string;
}

export interface StudentProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  degree: string;
  institution: string;
  graduationYear: number;
  cgpa: number;
  bio: string;
  targetCareerId: string;
  resumeFile: {
    name: string;
    size: string;
    uploadedAt: string;
  } | null;
  experience: StudentExperience[];
  projects: StudentProject[];
  certifications: StudentCertification[];
  skills: Skill[];
  preferences: {
    weeklyHours: number;
    learningStyle: 'video' | 'reading' | 'interactive';
    notifications: boolean;
  };
}

export interface CareerRole {
  id: string;
  title: string;
  slug: string;
  category: string;
  description: string;
  experienceLevel: 'Entry-Level' | 'Intermediate' | 'Advanced';
  coreSkills: string[];
  secondarySkills: string[];
  currentMatchPercentage: number;
  avgSalary: string;
  demandLevel: 'High' | 'Very High' | 'Moderate';
  marketInsight: string;
}

export interface CareerMatch {
  careerId: string;
  careerTitle: string;
  overallMatch: number;
  strongMatches: Array<{
    skill: string;
    studentLevel: number;
    requiredLevel: number;
    note: string;
  }>;
  needsImprovement: Array<{
    skill: string;
    studentLevel: number;
    requiredLevel: number;
    gap: number;
    priority: 'High' | 'Medium' | 'Low';
  }>;
  benchmarkComparison: Array<{
    skill: string;
    studentLevel: number;
    benchmarkLevel: number;
    category: string;
  }>;
}

export interface SkillGapItem {
  skill: string;
  category: SkillCategory;
  yourLevel: number;
  requiredLevel: number;
  gap: number;
  priority: 'Strong' | 'High' | 'Medium' | 'Low';
  status: 'Mastered' | 'In Progress' | 'Not Started';
  recommendation: string;
}

export interface RoadmapResource {
  title: string;
  type: string;
  duration: string;
  url: string;
  platform: string;
}

export interface RoadmapStep {
  id: string;
  stepNumber: string; // e.g. "01", "02"
  title: string;
  status: 'completed' | 'in_progress' | 'upcoming';
  whyItMatters: string;
  topics: string[];
  recommendedResources: RoadmapResource[];
  practiceProject: {
    title: string;
    description: string;
    deliverable: string;
  };
  estimatedTime: string;
  skillKey: string;
}

export interface LearningResource {
  id: string;
  title: string;
  platform: 'YouTube' | 'Documentation' | 'Interactive' | 'Article';
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  duration: string;
  instructor: string;
  url: string;
  skillTag: string;
  roadmapStepId?: string;
  rating: number;
  isSaved?: boolean;
}

export interface JobOpportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  workMode: 'Remote' | 'Hybrid' | 'On-site';
  type: 'Full-time' | 'Internship' | 'Contract';
  matchPercentage: number;
  matchedSkills: string[];
  missingSkills: string[];
  compensation: string;
  postedAgo: string;
  isSaved?: boolean;
  description: string;
  responsibilities: string[];
  qualifications: string[];
}

export interface ProgressStats {
  careerReadiness: number;
  skillsCompleted: { completed: number; total: number };
  roadmapProgress: number;
  learningHours: number;
  studyStreakDays: number;
  currentFocus: {
    title: string;
    subtitle: string;
    hoursLeft: string;
  };
  nextRecommendedAction: {
    action: string;
    reason: string;
    impact: string;
    stepId: string;
  };
  recentActivity: Array<{
    id: string;
    action: string;
    time: string;
    type: 'completed' | 'uploaded' | 'saved' | 'started';
  }>;
}
