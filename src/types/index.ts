export type SkillCategory = 'Frontend' | 'Backend' | 'Database' | 'Tools' | 'Security' | 'AI/ML' | 'Cloud' | 'Other';

export type SkillLevel = 'Novice' | 'Familiar' | 'Proficient' | 'Expert';

export type ProfileState = 'ZERO_KNOWLEDGE' | 'PROFILE_INCOMPLETE' | 'PROFILE_READY' | 'PERSONALIZED';

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

export interface AssessmentOption {
  id: string;
  text: string;
  domainSignal: string;
  styleSignal?: string;
  traitSignal?: string;
}

export interface AssessmentQuestion {
  id: string;
  question?: string;
  subtext?: string;
  title?: string;
  subtitle?: string;
  options: AssessmentOption[];
}

export interface AssessmentSignals {
  domainPreferences: string[];
  problemSolvingStyle?: string;
  workStyleSignals: string[];
  primaryMotivation?: string;
  careerInterestScores: Record<string, number>;
}

export interface StudentProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  degree: string;
  field?: string;
  institution: string;
  graduationYear: number;
  cgpa: number;
  bio: string;
  targetCareerId: string;
  profileState: ProfileState;
  resumeFile: {
    name: string;
    size: string;
    uploadedAt: string;
  } | null;
  skills: Skill[];
  interests: string[];
  careerInterest?: string;
  practicalExperience?: string;
  experience: StudentExperience[];
  projects: StudentProject[];
  certifications: StudentCertification[];
  preferences: {
    weeklyHours: number;
    learningStyle: 'video' | 'reading' | 'interactive';
    notifications: boolean;
  };
  assessmentSignals?: AssessmentSignals | null;
  profileCompleteness: number; // 0 - 100
  careerReadiness?: number;
  readinessTier?: string;
  isDemo?: boolean;
}

export interface MinimalOnboardingRequest {
  name?: string;
  education: string;
  degree?: string;
  field?: string;
  academicLevel?: string;
  skills: string[];
  interests: string[];
  careerDirection: string;
  practicalExperienceText?: string;
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

export interface CareerRecommendation {
  career: CareerRole;
  matchScore: number;
  confidence: 'High' | 'Moderate' | 'Emerging' | 'Uncalibrated' | number;
  matchedSkills: string[];
  missingSkills: string[];
  interestAlignment: number;
  explanation: string;
}

export interface ReadinessBreakdown {
  skillAlignmentPoints: number; // Max 450
  practicalExperiencePoints: number; // Max 250
  assessmentPoints: number; // Max 150
  educationPoints: number; // Max 150
  totalPoints: number; // Max 1000
}

export interface ReadinessResult {
  readinessScore: number; // 0 - 100%
  readinessPoints: number; // 0 - 1000
  readinessLevel: 'Uncalibrated' | 'Early Foundation' | 'Developing' | 'Proficient' | 'Industry Ready';
  breakdown: ReadinessBreakdown;
  statusMessage: string;
  recommendationHint: string;
}

export interface SkillGapItem {
  skill: string;
  category: SkillCategory | string;
  yourLevel: number;
  requiredLevel: number;
  gap: number;
  priority: 'Strong' | 'Developing' | 'Gap' | 'High' | 'Medium' | 'Low';
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
  skillsCovered?: string[];
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
  applyClicked?: boolean;
  isDemoSample?: boolean;
  source: 'LinkedIn' | 'Company Website' | 'Campus Placement Portal' | 'Indeed' | 'Glassdoor';
  sourceUrl: string;
  description: string;
  responsibilities: string[];
  qualifications: string[];
}

export interface NextCareerProgression {
  currentCareerTitle: string;
  nextCareerRole: string;
  specializations: string[];
  transferableSkills: string[];
  skillsToAcquire: string[];
  rationale: string;
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

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  academicLevel?: string;
  isGuest?: boolean;
  isDemo?: boolean;
}

export interface HiddenCompetency {
  skill: string;
  confidence: number;
  source: string;
  evidence: string;
  reasoning: string;
  explicitOrInferred: 'inferred' | 'explicit';
}

export interface TransferabilityResult {
  sourceCareer: string;
  destinationCareer: string;
  overallScore: number;
  transferableSkills: string[];
  bridgeSkills: string[];
  missingSkills: string[];
  explanation: string;
}

export interface SkillCombination {
  combination: string[];
  career: string;
  confidence: number;
  supportingSkills: string[];
  missingSkills: string[];
  explanation: string;
}

export interface SkillContradiction {
  skill: string;
  claimedProficiency: string;
  evidenceProficiency: string;
  evidenceSources: string[];
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  explanation: string;
  recommendation: string;
}

export interface SkillObsolescence {
  skill: string;
  trend: 'Stable' | 'Watch' | 'Declining Relevance' | 'Emerging Replacement';
  reason: string;
  confidence: number;
  recommendedSkills: string[];
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  datasetSource: string;
}

export interface AdvancedIntelligenceSummary {
  hiddenCompetencies: HiddenCompetency[];
  transferability: TransferabilityResult;
  combinations: SkillCombination[];
  contradictions: SkillContradiction[];
  obsolescence: SkillObsolescence[];
  profileState: ProfileState;
}

export interface CoachChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  source?: string;
  timestamp: string;
}

