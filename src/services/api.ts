import {
  StudentProfile,
  CareerRole,
  CareerMatch,
  SkillGapItem,
  RoadmapStep,
  LearningResource,
  JobOpportunity,
  ProgressStats,
  Skill,
  AuthUser,
  CareerRecommendation,
  ReadinessResult,
  AssessmentQuestion,
  MinimalOnboardingRequest,
  ProfileState,
  HiddenCompetency,
  TransferabilityResult,
  SkillCombination,
  SkillContradiction,
  SkillObsolescence,
  AdvancedIntelligenceSummary
} from '../types';

import {
  mockStudent,
  mockCareers,
  mockCareerMatch,
  mockSkillGaps,
  mockRoadmap,
  mockLearningResources,
  mockJobs,
  mockProgressStats,
  createBlankStudentProfile,
  createBlankProgressStats,
  createBlankCareerMatch,
  createBlankSkillGaps
} from '../data/mockData';

const API_BASE = (typeof window !== 'undefined' && window.location.port === '5173')
  ? '/api'
  : (import.meta.env.VITE_API_BASE || 'http://localhost:8000/api');
const AUTH_STORAGE_KEY = 'reskill_auth_user';
const PROFILE_STORAGE_KEY = 'reskill_student_profile';

// Helper to check if a profile has progressed beyond zero knowledge
export const isProfilePersonalized = (student: StudentProfile): boolean => {
  if (!student) return false;
  return (
    student.profileState === 'PERSONALIZED' ||
    student.profileState === 'PROFILE_READY' ||
    Boolean(student.resumeFile) ||
    Boolean(student.skills && student.skills.length > 0)
  );
};

// Internal active state store
let currentUser: AuthUser | null = (() => {
  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
})();

let currentStudent: StudentProfile = (() => {
  try {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch {
    // fallback
  }
  return createBlankStudentProfile(currentUser || undefined);
})();

let currentCareers: CareerRole[] = mockCareers.map(c => ({
  ...c,
  currentMatchPercentage: isProfilePersonalized(currentStudent) ? c.currentMatchPercentage : 0
}));

let currentRoadmap: RoadmapStep[] = isProfilePersonalized(currentStudent)
  ? [...mockRoadmap]
  : mockRoadmap.map(step => ({ ...step, status: 'upcoming' as const }));

let currentResources: LearningResource[] = [...mockLearningResources];
let currentJobs: JobOpportunity[] = mockJobs.map(j => ({
  ...j,
  matchPercentage: isProfilePersonalized(currentStudent) ? j.matchPercentage : 0,
  isDemoSample: !isProfilePersonalized(currentStudent)
}));
let currentSkillGaps: SkillGapItem[] = isProfilePersonalized(currentStudent)
  ? [...mockSkillGaps]
  : createBlankSkillGaps();
let currentProgress: ProgressStats = isProfilePersonalized(currentStudent)
  ? { ...mockProgressStats }
  : createBlankProgressStats();
let currentCareerMatch: CareerMatch = isProfilePersonalized(currentStudent)
  ? { ...mockCareerMatch }
  : createBlankCareerMatch();

// Sync to localStorage
function saveStateLocally() {
  try {
    if (currentUser) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(currentUser));
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(currentStudent));
  } catch (e) {
    console.warn('LocalStorage save failed:', e);
  }
}

// Resilient fetch helper with timeout
async function request<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 4000);
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      },
      signal: controller.signal
    });
    clearTimeout(id);
    if (!res.ok) {
      console.warn(`API ${endpoint} responded with status ${res.status}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (err) {
    // Graceful fallback to client-side deterministic store
    return null;
  }
}

export const api = {
  // Authentication
  async login(email: string, password?: string): Promise<AuthUser> {
    const res = await request<{ user: AuthUser; profile: StudentProfile; message: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (res && res.user) {
      currentUser = res.user;
      currentStudent = res.profile;
      saveStateLocally();
      return res.user;
    }

    // Client fallback - strictly isolate demo to exact demo accounts
    const isDemo = email === 'parvez.ahmed@apex.edu.in' || email === 'demo@reskill.ai';
    const user: AuthUser = {
      id: `usr_${Math.random().toString(36).substring(2, 9)}`,
      name: isDemo ? 'Parvez Ahmed' : email.split('@')[0],
      email,
      academicLevel: 'College Student',
      isDemo
    };
    currentUser = user;
    if (isDemo) {
      currentStudent = { ...mockStudent, isDemo: true };
    } else {
      currentStudent = createBlankStudentProfile(user);
    }
    saveStateLocally();
    return user;
  },

  async signup(name: string, email: string, academicLevel?: string, password?: string): Promise<AuthUser> {
    const res = await request<{ user: AuthUser; profile: StudentProfile; message: string }>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, academicLevel, password })
    });

    if (res && res.user) {
      currentUser = res.user;
      currentStudent = res.profile;
      saveStateLocally();
      return res.user;
    }

    // Client fallback
    const user: AuthUser = {
      id: `usr_${Math.random().toString(36).substring(2, 9)}`,
      name,
      email,
      academicLevel: academicLevel || 'College Student',
      isDemo: false
    };
    currentUser = user;
    currentStudent = {
      ...createBlankStudentProfile(user),
      name,
      email
    };
    saveStateLocally();
    return user;
  },

  async loginGuest(): Promise<AuthUser> {
    const guestUser: AuthUser = {
      id: `usr_guest_${Date.now().toString().slice(-4)}`,
      name: 'Guest Candidate',
      email: 'guest.candidate@reskill.ai',
      academicLevel: 'Pre-final Year Undergraduate',
      isGuest: true,
      isDemo: false
    };
    currentUser = guestUser;
    currentStudent = createBlankStudentProfile(guestUser);
    saveStateLocally();
    return guestUser;
  },

  async logout(): Promise<void> {
    currentUser = null;
    currentStudent = createBlankStudentProfile();
    saveStateLocally();
  },

  getCurrentUser(): AuthUser | null {
    return currentUser;
  },

  // Reset & Demo Profiles
  async resetToZeroKnowledge(): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/auth/reset', { method: 'POST' });
    if (res) {
      currentStudent = res;
    } else {
      currentStudent = createBlankStudentProfile(currentUser || undefined);
    }
    saveStateLocally();
    return { ...currentStudent };
  },

  async loadDemoProfile(): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/auth/demo', { method: 'POST' });
    if (res) {
      currentStudent = res;
    } else {
      currentStudent = { ...mockStudent, isDemo: true };
    }
    saveStateLocally();
    return { ...currentStudent };
  },

  // Profile Retrieval and Updates
  async getProfile(): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/profile');
    if (res) {
      currentStudent = res;
      saveStateLocally();
    }
    return { ...currentStudent };
  },

  async updateProfile(updatedData: Partial<StudentProfile>): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(updatedData)
    });
    if (res) {
      currentStudent = res;
    } else {
      currentStudent = { ...currentStudent, ...updatedData };
    }
    saveStateLocally();
    return { ...currentStudent };
  },

  // Smart Minimal Onboarding (5 Core Questions)
  async submitMinimalOnboarding(data: MinimalOnboardingRequest): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/profile/onboarding', {
      method: 'POST',
      body: JSON.stringify(data)
    });

    if (res) {
      currentStudent = res;
      saveStateLocally();
      return res;
    }

    // Client-side fallback computation
    const newSkills: Skill[] = data.skills.map((s) => ({
      name: s,
      category: 'Backend',
      proficiency: 70,
      level: 'Proficient',
      verified: false,
      detectedFrom: 'Self-reported (Onboarding)'
    }));

    currentStudent = {
      ...currentStudent,
      name: data.name || currentStudent.name,
      degree: data.degree || data.education,
      field: data.field || 'Engineering',
      skills: newSkills,
      interests: data.interests,
      careerInterest: data.careerDirection,
      practicalExperience: data.practicalExperienceText || '',
      profileState: 'PROFILE_READY',
      profileCompleteness: 75
    };
    saveStateLocally();
    return { ...currentStudent };
  },

  // Career Assessment (4 Questions)
  async getAssessmentQuestions(): Promise<AssessmentQuestion[]> {
    const res = await request<any[]>('/assessment/questions');
    if (res && res.length > 0) {
      return res.map(q => ({
        id: q.id,
        question: q.question || q.title,
        subtext: q.subtext || q.subtitle,
        options: (q.options || []).map((o: any) => ({
          id: o.id,
          text: o.text,
          domainSignal: o.domainSignal,
          styleSignal: o.styleSignal || o.traitSignal || o.domainSignal
        }))
      }));
    }

    // Default 4 questions
    return [
      {
        id: 'q1',
        question: 'Which type of problem would you enjoy solving most?',
        subtext: 'Choose the challenge that sparks your curiosity the most.',
        options: [
          { id: 'q1_sec', text: 'Finding security threats and investigating incidents', domainSignal: 'Cybersecurity', styleSignal: 'Analytical & Forensic' },
          { id: 'q1_sw', text: 'Building applications and features', domainSignal: 'Full Stack', styleSignal: 'Product-Driven' },
          { id: 'q1_data', text: 'Understanding data and finding patterns', domainSignal: 'Data Science', styleSignal: 'Quantitative' },
          { id: 'q1_ai', text: 'Designing intelligent AI systems', domainSignal: 'AI/ML', styleSignal: 'Algorithmic' },
          { id: 'q1_cloud', text: 'Managing infrastructure and cloud systems', domainSignal: 'Cloud/DevOps', styleSignal: 'Systemic' }
        ]
      },
      {
        id: 'q2',
        question: "When something doesn't work, what sounds most interesting to you?",
        subtext: 'Your natural response to friction reveals your cognitive strengths.',
        options: [
          { id: 'q2_inv', text: 'Investigating why it failed and tracing logs', domainSignal: 'Cybersecurity', styleSignal: 'Investigative' },
          { id: 'q2_fix', text: 'Building a better solution or rewriting the component', domainSignal: 'Software Engineering', styleSignal: 'Iterative Builder' },
          { id: 'q2_ana', text: 'Analyzing the data behind the problem', domainSignal: 'Data Science', styleSignal: 'Empirical' },
          { id: 'q2_exp', text: 'Experimenting with different architectural approaches', domainSignal: 'AI/ML', styleSignal: 'Experimental' },
          { id: 'q2_arch', text: 'Designing resilient system architecture to prevent failure', domainSignal: 'Cloud/DevOps', styleSignal: 'Architectural' }
        ]
      },
      {
        id: 'q3',
        question: 'What kind of work would keep you interested for a long time?',
        subtext: 'Think about sustained engagement over years of practice.',
        options: [
          { id: 'q3_sec', text: 'Protecting systems and finding vulnerabilities', domainSignal: 'Cybersecurity', styleSignal: 'Defensive Strategy' },
          { id: 'q3_prod', text: 'Building customer-facing products', domainSignal: 'Full Stack', styleSignal: 'User Empathy' },
          { id: 'q3_res', text: 'Researching and experimenting with frontier models', domainSignal: 'AI/ML', styleSignal: 'Frontier Research' },
          { id: 'q3_ana', text: 'Analyzing complex information and building predictive models', domainSignal: 'Data Science', styleSignal: 'Insight Driven' },
          { id: 'q3_sys', text: 'Working with distributed systems and cloud infrastructure', domainSignal: 'Cloud/DevOps', styleSignal: 'Scale & Operations' }
        ]
      },
      {
        id: 'q4',
        question: 'What matters most to you in your first career?',
        subtext: 'Your primary north star for your early engineering career.',
        options: [
          { id: 'q4_sec', text: 'Security and high-stakes problem solving', domainSignal: 'Cybersecurity', styleSignal: 'Critical Mission' },
          { id: 'q4_grow', text: 'Building real products used by real people', domainSignal: 'Software Engineering', styleSignal: 'Product Impact' },
          { id: 'q4_inn', text: 'Frontier research, mathematics, and innovation', domainSignal: 'AI/ML', styleSignal: 'Scientific Rigor' },
          { id: 'q4_imp', text: 'High-impact decision making driven by data', domainSignal: 'Data Science', styleSignal: 'Business Value' },
          { id: 'q4_scale', text: 'Deep systems engineering and high availability', domainSignal: 'Cloud/DevOps', styleSignal: 'Engineering Craft' }
        ]
      }
    ];
  },

  async submitAssessment(answers: Record<string, string>): Promise<StudentProfile> {
    const res = await request<StudentProfile>('/assessment/submit', {
      method: 'POST',
      body: JSON.stringify({ answers })
    });

    if (res) {
      currentStudent = res;
      saveStateLocally();
      return res;
    }

    // Client fallback
    currentStudent.profileState = 'PROFILE_READY';
    currentStudent.profileCompleteness = Math.max(85, currentStudent.profileCompleteness);
    saveStateLocally();
    return { ...currentStudent };
  },

  // Career Recommendations & Selection
  async getCareerRecommendations(): Promise<CareerRecommendation[]> {
    const res = await request<CareerRecommendation[]>('/careers/recommendations');
    if (res && res.length > 0) return res;

    const personalized = isProfilePersonalized(currentStudent);
    // Fallback recommendation list
    return currentCareers.map((c, i) => ({
      career: c,
      matchScore: personalized ? (c.currentMatchPercentage || Math.max(15, 85 - i * 8)) : 0,
      confidence: personalized ? 'Moderate' as const : 'Uncalibrated' as const,
      matchedSkills: personalized ? (c.coreSkills || []).slice(0, 3) : [],
      missingSkills: c.coreSkills || [],
      interestAlignment: personalized ? 80 : 0,
      explanation: personalized
        ? `Strong foundation aligned with ${c.title} competencies.`
        : 'Complete minimal onboarding or upload a resume to calculate verified career match.'
    }));
  },

  async setTargetCareer(careerId: string): Promise<CareerRole | undefined> {
    await request<StudentProfile>(`/careers/select?career_id=${careerId}`, { method: 'POST' });
    currentStudent.targetCareerId = careerId;
    if (currentStudent.profileState === 'PROFILE_READY') {
      currentStudent.profileState = 'PERSONALIZED';
    }
    saveStateLocally();
    return currentCareers.find(c => c.id === careerId);
  },

  // Readiness Metrics
  async getReadiness(): Promise<ReadinessResult | null> {
    const res = await request<ProgressStats>('/progress');
    if (res) {
      // Return synthetic readiness result
      return {
        readinessScore: res.careerReadiness,
        readinessPoints: Math.round(res.careerReadiness * 10),
        readinessLevel: res.careerReadiness > 80 ? 'Industry Ready' : res.careerReadiness > 60 ? 'Proficient' : res.careerReadiness > 40 ? 'Developing' : 'Early Foundation',
        breakdown: {
          skillAlignmentPoints: Math.round(res.careerReadiness * 4.5),
          practicalExperiencePoints: Math.round(res.careerReadiness * 2.5),
          assessmentPoints: 120,
          educationPoints: 120,
          totalPoints: Math.round(res.careerReadiness * 10)
        },
        statusMessage: `Calibrated readiness at ${res.careerReadiness}%`,
        recommendationHint: 'Complete pending roadmap modules to increase readiness points.'
      };
    }
    return null;
  },

  // Resume Ingestion
  async uploadResume(fileInput: File | { name: string; size: number }): Promise<{
    success: boolean;
    detectedSkillsCount: number;
    resumeFile: { name: string; size: string; uploadedAt: string };
    student: StudentProfile;
  }> {
    if (fileInput instanceof File) {
      const formData = new FormData();
      formData.append('file', fileInput);
      try {
        const res = await fetch(`${API_BASE}/resume/analyze`, {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          const profile: StudentProfile = await res.json();
          currentStudent = profile;
          saveStateLocally();
          return {
            success: true,
            detectedSkillsCount: currentStudent.skills.length,
            resumeFile: currentStudent.resumeFile || {
              name: fileInput.name,
              size: `${(fileInput.size / 1024).toFixed(0)} KB`,
              uploadedAt: 'Just now'
            },
            student: { ...currentStudent }
          };
        } else {
          const errData = await res.json().catch(() => ({ detail: 'Failed to analyze resume' }));
          throw new Error(errData.detail || 'Resume analysis failed. Please check the uploaded file and try again.');
        }
      } catch (e: any) {
        console.warn('Backend resume upload failed:', e);
        if (e.name === 'TypeError' && (e.message.includes('fetch') || e.message.includes('Failed to fetch') || e.message.includes('NetworkError'))) {
          throw new Error('Unable to connect to the ReSkillAI backend. Please ensure the backend server is running on port 8000.');
        }
        throw e;
      }
    }

    const fileName = fileInput.name;
    const fileSize = typeof fileInput.size === 'number' ? fileInput.size : 254000;
    const formattedSize = `${(fileSize / 1024).toFixed(0)} KB`;
    const resumeInfo = {
      name: fileName,
      size: formattedSize === '0 KB' ? '248 KB' : formattedSize,
      uploadedAt: 'Just now'
    };

    currentStudent = {
      ...currentStudent,
      resumeFile: resumeInfo,
      profileState: currentStudent.skills.length > 0 ? 'PROFILE_READY' : 'PROFILE_INCOMPLETE',
      profileCompleteness: Math.max(60, currentStudent.profileCompleteness)
    };
    saveStateLocally();

    return {
      success: true,
      detectedSkillsCount: currentStudent.skills.length,
      resumeFile: resumeInfo,
      student: { ...currentStudent }
    };
  },

  // Existing methods preserved for backward compatibility
  async getCareers(): Promise<CareerRole[]> {
    const res = await request<CareerRole[]>('/careers');
    if (res && res.length > 0) return res;
    return [...currentCareers];
  },

  async getCareerMatch(careerId?: string): Promise<CareerMatch> {
    const cid = careerId || currentStudent.targetCareerId || 'career_fullstack';
    const res = await request<CareerMatch>(`/careers/${cid}/match`);
    if (res) {
      currentCareerMatch = res;
      return res;
    }
    return { ...currentCareerMatch };
  },

  async getSkillGap(): Promise<SkillGapItem[]> {
    const res = await request<SkillGapItem[]>('/skill-gap');
    if (res && res.length > 0) return res;
    return [...currentSkillGaps];
  },

  async getRoadmap(): Promise<RoadmapStep[]> {
    const res = await request<RoadmapStep[]>('/roadmap');
    if (res && res.length > 0) return res;
    return [...currentRoadmap];
  },

  async updateRoadmapStep(
    stepId: string,
    status: 'completed' | 'in_progress' | 'upcoming'
  ): Promise<RoadmapStep[]> {
    await request<RoadmapStep>(`/roadmap/step/${stepId}`, {
      method: 'POST',
      body: JSON.stringify({ status })
    });
    currentRoadmap = currentRoadmap.map((step) =>
      step.id === stepId ? { ...step, status } : step
    );
    return [...currentRoadmap];
  },

  async getLearningResources(filterSkill?: string): Promise<LearningResource[]> {
    const res = await request<LearningResource[]>('/learning');
    if (res && res.length > 0) {
      if (!filterSkill || filterSkill === 'All') return res;
      return res.filter(r => r.skillTag.toLowerCase() === filterSkill.toLowerCase());
    }
    if (!filterSkill || filterSkill === 'All') return [...currentResources];
    return currentResources.filter(r => r.skillTag.toLowerCase() === filterSkill.toLowerCase());
  },

  async toggleSaveResource(resourceId: string): Promise<LearningResource[]> {
    await request(`/learning/${resourceId}/toggle-save`, { method: 'POST' });
    currentResources = currentResources.map((res) =>
      res.id === resourceId ? { ...res, isSaved: !res.isSaved } : res
    );
    return [...currentResources];
  },

  async getJobs(): Promise<JobOpportunity[]> {
    const res = await request<JobOpportunity[]>('/jobs');
    if (res && res.length > 0) return res;
    return [...currentJobs];
  },

  async toggleSaveJob(jobId: string): Promise<JobOpportunity[]> {
    currentJobs = currentJobs.map((job) =>
      job.id === jobId ? { ...job, isSaved: !job.isSaved } : job
    );
    return [...currentJobs];
  },

  async getProgress(): Promise<ProgressStats> {
    const res = await request<ProgressStats>('/progress');
    if (res) return res;
    return { ...currentProgress };
  },

  async recordJobApplyClick(jobId: string): Promise<void> {
    await request(`/jobs/${jobId}/apply-clicked`, { method: 'POST' });
  },

  // Advanced Intelligence Layer Methods
  async getHiddenCompetencies(): Promise<HiddenCompetency[]> {
    const res = await request<HiddenCompetency[]>('/intelligence/hidden-competencies');
    return res || [];
  },

  async getTransferability(targetCareerId?: string): Promise<TransferabilityResult | null> {
    const query = targetCareerId ? `?target_career_id=${targetCareerId}` : '';
    return await request<TransferabilityResult>(`/intelligence/transferability${query}`);
  },

  async getSkillCombinations(): Promise<SkillCombination[]> {
    const res = await request<SkillCombination[]>('/intelligence/combinations');
    return res || [];
  },

  async getSkillContradictions(): Promise<SkillContradiction[]> {
    const res = await request<SkillContradiction[]>('/intelligence/contradictions');
    return res || [];
  },

  async getSkillObsolescence(): Promise<SkillObsolescence[]> {
    const res = await request<SkillObsolescence[]>('/intelligence/obsolescence');
    return res || [];
  },

  async getAdvancedIntelligenceSummary(targetCareerId?: string): Promise<AdvancedIntelligenceSummary | null> {
    const query = targetCareerId ? `?target_career_id=${targetCareerId}` : '';
    return await request<AdvancedIntelligenceSummary>(`/intelligence/summary${query}`);
  },

  async sendCareerCoachMessage(
    message: string,
    history?: Array<{ role: 'user' | 'assistant'; content: string }>
  ): Promise<{ response: string; source: string; status: string }> {
    try {
      const res = await fetch(`${API_BASE}/coach/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history })
      });
      if (res.ok) {
        return await res.json();
      }
      const err = await res.json().catch(() => ({ detail: 'AI Career Coach is currently unavailable.' }));
      throw new Error(err.detail || 'Could not connect to AI Career Coach.');
    } catch (e: any) {
      if (e.name === 'TypeError' && (e.message.includes('fetch') || e.message.includes('Failed to fetch') || e.message.includes('NetworkError'))) {
        throw new Error('Unable to connect to the ReSkillAI backend. Please ensure the backend server is running on port 8000.');
      }
      throw e;
    }
  }
};
