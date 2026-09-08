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

import {
  mockStudent,
  mockCareers,
  mockCareerMatch,
  mockSkillGaps,
  mockRoadmap,
  mockLearningResources,
  mockJobs,
  mockProgressStats
} from '../data/mockData';

// In-memory editable state store for mock interactions
let currentStudent: StudentProfile = { ...mockStudent };
let currentCareers: CareerRole[] = [...mockCareers];
let currentCareerMatch: CareerMatch = { ...mockCareerMatch };
let currentSkillGaps: SkillGapItem[] = [...mockSkillGaps];
let currentRoadmap: RoadmapStep[] = [...mockRoadmap];
let currentResources: LearningResource[] = [...mockLearningResources];
let currentJobs: JobOpportunity[] = [...mockJobs];
let currentProgress: ProgressStats = { ...mockProgressStats };

/**
 * Service Layer Placeholders for Future Backend REST APIs
 * When the backend service is deployed, these functions can simply swap their implementation
 * to use fetch() or axios against the live REST server without touching the UI components.
 */
export const api = {
  /**
   * POST /api/resume/upload
   * Simulates uploading a resume file (PDF/DOCX) and extracting initial skills
   */
  async uploadResume(file: { name: string; size: number }): Promise<{
    success: boolean;
    detectedSkillsCount: number;
    resumeFile: { name: string; size: string; uploadedAt: string };
  }> {
    await new Promise((resolve) => setTimeout(resolve, 800)); // simulated latency
    const formattedSize = `${(file.size / 1024).toFixed(0)} KB`;
    const resumeInfo = {
      name: file.name,
      size: formattedSize === '0 KB' ? '248 KB' : formattedSize,
      uploadedAt: 'Just now'
    };

    currentStudent = {
      ...currentStudent,
      resumeFile: resumeInfo
    };

    // Add activity record
    currentProgress = {
      ...currentProgress,
      recentActivity: [
        {
          id: `act_${Date.now()}`,
          action: `Uploaded new resume (${file.name})`,
          time: 'Just now',
          type: 'uploaded'
        },
        ...currentProgress.recentActivity
      ]
    };

    return {
      success: true,
      detectedSkillsCount: currentStudent.skills.length,
      resumeFile: resumeInfo
    };
  },

  /**
   * GET /api/profile
   * Retrieves the current student profile
   */
  async getProfile(): Promise<StudentProfile> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return { ...currentStudent };
  },

  /**
   * POST /api/profile
   * Updates student profile details
   */
  async updateProfile(updatedData: Partial<StudentProfile>): Promise<StudentProfile> {
    await new Promise((resolve) => setTimeout(resolve, 200));
    currentStudent = {
      ...currentStudent,
      ...updatedData
    };
    return { ...currentStudent };
  },

  /**
   * GET /api/careers
   * Retrieves the list of available target career trajectories
   */
  async getCareers(): Promise<CareerRole[]> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return [...currentCareers];
  },

  /**
   * POST /api/career/recommend
   * Simulates AI-powered career recommendation based on student skills
   */
  async recommendCareer(): Promise<{
    recommendedCareer: CareerRole;
    rationale: string;
    alternative: CareerRole;
  }> {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const fullstack = currentCareers.find((c) => c.id === 'career_fullstack') || currentCareers[0];
    const frontend = currentCareers.find((c) => c.id === 'career_frontend') || currentCareers[1];

    return {
      recommendedCareer: fullstack,
      rationale: 'Based on your proficient JavaScript (85%) and React (80%) foundations combined with initial Node.js exposure, Full Stack Developer is your highest-velocity trajectory.',
      alternative: frontend
    };
  },

  /**
   * GET /api/career/match/:careerId
   * Retrieves the career match compatibility analysis
   */
  async getCareerMatch(careerId?: string): Promise<CareerMatch> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    const career = currentCareers.find((c) => c.id === (careerId || currentStudent.targetCareerId));
    return {
      ...currentCareerMatch,
      careerId: career?.id || currentCareerMatch.careerId,
      careerTitle: career?.title || currentCareerMatch.careerTitle,
      overallMatch: career?.currentMatchPercentage || currentCareerMatch.overallMatch
    };
  },

  /**
   * GET /api/skill-gap
   * Retrieves skill gap table data against the target career benchmark
   */
  async getSkillGap(): Promise<SkillGapItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return [...currentSkillGaps];
  },

  /**
   * GET /api/roadmap
   * Retrieves the structured curriculum timeline
   */
  async getRoadmap(): Promise<RoadmapStep[]> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return [...currentRoadmap];
  },

  /**
   * POST /api/roadmap/step/:stepId
   * Toggles or updates the completion status of a roadmap step
   */
  async updateRoadmapStep(
    stepId: string,
    status: 'completed' | 'in_progress' | 'upcoming'
  ): Promise<RoadmapStep[]> {
    await new Promise((resolve) => setTimeout(resolve, 100));
    currentRoadmap = currentRoadmap.map((step) =>
      step.id === stepId ? { ...step, status } : step
    );

    // Dynamically recalculate progress stats
    const completedCount = currentRoadmap.filter((s) => s.status === 'completed').length;
    const progressPercent = Math.round((completedCount / currentRoadmap.length) * 100);

    currentProgress = {
      ...currentProgress,
      roadmapProgress: progressPercent,
      careerReadiness: Math.min(96, Math.max(50, Math.round(50 + progressPercent * 0.45)))
    };

    return [...currentRoadmap];
  },

  /**
   * GET /api/learning-resources
   * Retrieves recommended curated video and documentation resources
   */
  async getLearningResources(filterSkill?: string): Promise<LearningResource[]> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    if (!filterSkill || filterSkill === 'All') {
      return [...currentResources];
    }
    return currentResources.filter(
      (res) => res.skillTag.toLowerCase() === filterSkill.toLowerCase()
    );
  },

  /**
   * POST /api/learning-resources/:id/toggle-save
   * Saves or bookmarks a resource
   */
  async toggleSaveResource(resourceId: string): Promise<LearningResource[]> {
    currentResources = currentResources.map((res) =>
      res.id === resourceId ? { ...res, isSaved: !res.isSaved } : res
    );
    return [...currentResources];
  },

  /**
   * GET /api/jobs
   * Retrieves personalized opportunity recommendations
   */
  async getJobs(): Promise<JobOpportunity[]> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return [...currentJobs];
  },

  /**
   * POST /api/jobs/:id/save
   * Toggles saved job bookmark
   */
  async toggleSaveJob(jobId: string): Promise<JobOpportunity[]> {
    currentJobs = currentJobs.map((job) =>
      job.id === jobId ? { ...job, isSaved: !job.isSaved } : job
    );
    return [...currentJobs];
  },

  /**
   * GET /api/progress
   * Retrieves progress tracking analytics
   */
  async getProgress(): Promise<ProgressStats> {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return { ...currentProgress };
  },

  /**
   * Set active target career
   */
  async setTargetCareer(careerId: string): Promise<CareerRole | undefined> {
    const selected = currentCareers.find((c) => c.id === careerId);
    if (selected) {
      currentStudent = { ...currentStudent, targetCareerId: careerId };
      currentCareerMatch = {
        ...currentCareerMatch,
        careerId: selected.id,
        careerTitle: selected.title,
        overallMatch: selected.currentMatchPercentage
      };
    }
    return selected;
  }
};
