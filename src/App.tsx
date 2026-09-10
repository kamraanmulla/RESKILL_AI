import React, { useState, useEffect } from 'react';
import { api, isProfilePersonalized } from './services/api';
import {
  StudentProfile,
  CareerRole,
  CareerMatch,
  SkillGapItem,
  RoadmapStep,
  LearningResource,
  JobOpportunity,
  ProgressStats,
  AuthUser
} from './types';
import {
  createBlankStudentProfile,
  createBlankProgressStats,
  createBlankCareerMatch,
  createBlankSkillGaps,
  mockCareers,
  mockRoadmap,
  mockLearningResources,
  mockJobs
} from './data/mockData';

// Layout & Common Components
import { Sidebar, NavItemId } from './components/common/Sidebar';
import { Topbar } from './components/common/Topbar';
import { MobileNav } from './components/common/MobileNav';
import { AuthModal } from './components/auth/AuthModal';
import { OnboardingFlow } from './components/onboarding/OnboardingFlow';
import { CareerAssessmentModal } from './components/assessment/CareerAssessmentModal';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ResumeUploadPage } from './pages/ResumeUploadPage';
import { ProfilePage } from './pages/ProfilePage';
import { CareerSelectionPage } from './pages/CareerSelectionPage';
import { CareerMatchPage } from './pages/CareerMatchPage';
import { SkillGapPage } from './pages/SkillGapPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { LearningPage } from './pages/LearningPage';
import { JobsPage } from './pages/JobsPage';
import { AdvancedIntelligencePage } from './pages/AdvancedIntelligencePage';
import { AICoachPage } from './pages/AICoachPage';

export const App: React.FC = () => {
  // Global View Mode (Landing Page vs Main Platform Application)
  const [isLandingView, setIsLandingView] = useState(false);
  const [currentTab, setCurrentTab] = useState<NavItemId>('dashboard');
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  // Authentication State
  const [user, setUser] = useState<AuthUser | null>(() => api.getCurrentUser());
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'signin' | 'signup'>('signin');

  // Intelligent Onboarding & Assessment Modals
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [onboardingStage, setOnboardingStage] = useState<'fork' | 'upload' | 'questions'>('fork');
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);

  const handleStartOnboarding = (stage: 'fork' | 'upload' | 'questions' = 'fork') => {
    setOnboardingStage(stage);
    setIsOnboardingOpen(true);
  };

  // Platform Data State (Hydrated from API)
  // Real candidates strictly start with ZERO KNOWLEDGE about their profile
  const [student, setStudent] = useState<StudentProfile>(() => createBlankStudentProfile(user || undefined));
  const [careers, setCareers] = useState<CareerRole[]>(() =>
    mockCareers.map(c => ({ ...c, currentMatchPercentage: 0 }))
  );
  const [careerMatch, setCareerMatch] = useState<CareerMatch>(() => createBlankCareerMatch());
  const [skillGaps, setSkillGaps] = useState<SkillGapItem[]>(() => createBlankSkillGaps());
  const [roadmap, setRoadmap] = useState<RoadmapStep[]>(() =>
    mockRoadmap.map(step => ({ ...step, status: 'upcoming' as const }))
  );
  const [resources, setResources] = useState<LearningResource[]>(mockLearningResources);
  const [jobs, setJobs] = useState<JobOpportunity[]>(() =>
    mockJobs.map(j => ({ ...j, matchPercentage: 0, isDemoSample: true }))
  );
  const [stats, setStats] = useState<ProgressStats>(createBlankProgressStats);

  // Filter state for learning page cross-navigation
  const [learningFilterSkill, setLearningFilterSkill] = useState<string | undefined>(undefined);

  // Synchronize all data from API layer
  const refreshAllData = async () => {
    const [
      loadedProfile,
      loadedCareers,
      loadedMatch,
      loadedGaps,
      loadedRoadmap,
      loadedResources,
      loadedJobs,
      loadedStats
    ] = await Promise.all([
      api.getProfile(),
      api.getCareers(),
      api.getCareerMatch(),
      api.getSkillGap(),
      api.getRoadmap(),
      api.getLearningResources(),
      api.getJobs(),
      api.getProgress()
    ]);

    setStudent(loadedProfile);
    setCareers(loadedCareers);
    setCareerMatch(loadedMatch);
    setSkillGaps(loadedGaps);
    setRoadmap(loadedRoadmap);
    setResources(loadedResources);
    setJobs(loadedJobs);
    setStats(loadedStats);
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  const currentTargetCareer = careers.find((c) => c.id === student.targetCareerId) || careers[0];
  const personalized = isProfilePersonalized(student);

  // Auth Handlers
  const handleLoginSuccess = async (authUser: AuthUser) => {
    setUser(authUser);
    await refreshAllData();
    // For fresh real candidates with no resume or skills, trigger minimal onboarding flow
    if (!authUser.isDemo && (!student.skills || student.skills.length === 0)) {
      setIsOnboardingOpen(true);
    }
  };

  // Onboarding & Assessment Flow Transitions
  const handleOnboardingComplete = async (updatedProfile: StudentProfile) => {
    setIsOnboardingOpen(false);
    await refreshAllData();
    // Flow transitions seamlessly: Onboarding -> Short Assessment
    setIsAssessmentOpen(true);
  };

  const handleAssessmentComplete = async (updatedProfile: StudentProfile) => {
    setIsAssessmentOpen(false);
    await refreshAllData();
    setCurrentTab('dashboard');
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    await refreshAllData();
    setCurrentTab('dashboard');
  };

  const handleResetToZeroKnowledge = async () => {
    await api.resetToZeroKnowledge();
    await refreshAllData();
    setCurrentTab('dashboard');
  };

  const handleLoadDemoProfile = async () => {
    await api.loadDemoProfile();
    await refreshAllData();
    setCurrentTab('dashboard');
  };

  // Actions
  const handleSelectCareer = async (careerId: string) => {
    await api.setTargetCareer(careerId);
    await refreshAllData();
  };

  const handleToggleRoadmapStep = async (
    stepId: string,
    status: 'completed' | 'in_progress' | 'upcoming'
  ) => {
    const updated = await api.updateRoadmapStep(stepId, status);
    setRoadmap(updated);
    const updatedStats = await api.getProgress();
    setStats(updatedStats);
  };

  const handleToggleSaveJob = async (jobId: string) => {
    const updated = await api.toggleSaveJob(jobId);
    setJobs(updated);
  };

  const handleToggleSaveResource = async (resId: string) => {
    const updated = await api.toggleSaveResource(resId);
    setResources(updated);
  };

  const handleUpdateProfile = async (data: Partial<StudentProfile>) => {
    await api.updateProfile(data);
    await refreshAllData();
  };

  const handleResumeUpload = async (fileInfo: { name: string; size: string; uploadedAt: string } | File) => {
    if (fileInfo instanceof File) {
      await api.uploadResume(fileInfo);
    } else {
      await api.uploadResume({ name: fileInfo.name, size: 254000 });
    }
    await refreshAllData();
  };

  // Cross-Page Navigation Handlers
  const navigateToRoadmapWithFilter = (stepKey?: string) => {
    setCurrentTab('roadmap');
  };

  const navigateToLearningWithFilter = (skill?: string) => {
    setLearningFilterSkill(skill);
    setCurrentTab('learning');
  };

  // Get human-readable page title for Topbar breadcrumb
  const pageTitles: Record<NavItemId, string> = {
    dashboard: 'Dashboard',
    resume: 'My Resume',
    profile: 'Student Profile',
    careers: 'Career Selection',
    match: 'Career Match Analysis',
    'skill-gap': 'Skill Gap Analysis',
    roadmap: 'Learning Roadmap',
    learning: 'Recommended Learning',
    jobs: 'Jobs & Opportunities',
    intelligence: 'Career Intelligence',
    coach: 'AI Career Coach'
  };

  // ROUTE PROTECTION: Unauthenticated candidates start directly at Login / Signup
  if (!user && !isLandingView) {
    return (
      <LoginPage
        onLoginSuccess={handleLoginSuccess}
        onExploreLanding={() => setIsLandingView(true)}
      />
    );
  }

  // If in Public Landing Page mode
  if (isLandingView) {
    return (
      <>
        <LandingPage
          targetCareer={currentTargetCareer}
          onStartResume={() => {
            setIsLandingView(false);
            if (user) setCurrentTab('resume');
          }}
          onExploreCareers={() => {
            setIsLandingView(false);
            if (user) setCurrentTab('careers');
          }}
          onEnterDashboard={() => {
            setIsLandingView(false);
            if (user) setCurrentTab('dashboard');
          }}
          onOpenAuth={() => {
            setIsLandingView(false);
            if (!user) {
              setAuthModalMode('signin');
            }
          }}
        />
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          onLoginSuccess={handleLoginSuccess}
          initialMode={authModalMode}
        />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-paper flex flex-col md:flex-row antialiased">
      {/* Desktop Left Sidebar */}
      <div className="hidden md:block shrink-0">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => {
            setCurrentTab(tab);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          targetCareer={currentTargetCareer}
          onViewLanding={() => setIsLandingView(true)}
          isPersonalized={personalized}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-20 md:pb-10">
        <Topbar
          currentPageTitle={pageTitles[currentTab]}
          student={student}
          user={user}
          onOpenMobileNav={() => setIsMobileDrawerOpen(true)}
          onOpenProfile={() => setCurrentTab('profile')}
          onOpenAuth={() => {
            setAuthModalMode('signin');
            setIsAuthModalOpen(true);
          }}
          onLogout={handleLogout}
          onResetToZeroKnowledge={handleResetToZeroKnowledge}
          onLoadDemoProfile={handleLoadDemoProfile}
        />

        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-6xl w-full mx-auto">
          {currentTab === 'dashboard' && (
            <DashboardPage
              student={student}
              targetCareer={currentTargetCareer}
              stats={stats}
              skillGaps={skillGaps}
              roadmap={roadmap}
              resources={resources}
              onNavigate={(tab) => {
                setCurrentTab(tab);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              onSelectRoadmapStep={navigateToRoadmapWithFilter}
              onLoadDemoProfile={handleLoadDemoProfile}
              onUploadSampleResume={() => handleResumeUpload({
                name: 'Sample_Candidate_Resume.pdf',
                size: '248 KB',
                uploadedAt: 'Just now'
              })}
              onStartOnboarding={handleStartOnboarding}
              onStartAssessment={() => setIsAssessmentOpen(true)}
              onSelectCareer={handleSelectCareer}
            />
          )}

          {currentTab === 'resume' && (
            <ResumeUploadPage
              student={student}
              onUploadSuccess={handleResumeUpload}
              onContinueToProfile={() => setCurrentTab('profile')}
              onNavigateToDashboard={() => setCurrentTab('dashboard')}
            />
          )}

          {currentTab === 'profile' && (
            <ProfilePage
              student={student}
              careers={careers}
              onUpdateProfile={handleUpdateProfile}
              onNavigateToCareers={() => setCurrentTab('careers')}
              onNavigateToResume={() => setCurrentTab('resume')}
              onNavigateToDashboard={() => setCurrentTab('dashboard')}
            />
          )}

          {currentTab === 'careers' && (
            <CareerSelectionPage
              careers={careers}
              selectedCareerId={student.targetCareerId}
              onSelectCareer={handleSelectCareer}
              onViewCareerMatch={() => setCurrentTab('match')}
            />
          )}

          {currentTab === 'match' && (
            <CareerMatchPage
              career={currentTargetCareer}
              matchData={careerMatch}
              onNavigateToSkillGap={() => setCurrentTab('skill-gap')}
              onNavigateToRoadmap={() => setCurrentTab('roadmap')}
              onNavigateToCareers={() => setCurrentTab('careers')}
            />
          )}

          {currentTab === 'skill-gap' && (
            <SkillGapPage
              skillGaps={skillGaps}
              onNavigateToRoadmap={navigateToRoadmapWithFilter}
            />
          )}

          {currentTab === 'roadmap' && (
            <RoadmapPage
              roadmap={roadmap}
              targetCareer={currentTargetCareer}
              onToggleStepStatus={handleToggleRoadmapStep}
              onNavigateToLearning={navigateToLearningWithFilter}
            />
          )}

          {currentTab === 'learning' && (
            <LearningPage
              resources={resources}
              initialFilterSkill={learningFilterSkill}
              onToggleSave={handleToggleSaveResource}
            />
          )}

          {currentTab === 'jobs' && (
            <JobsPage
              jobs={jobs}
              onToggleSave={handleToggleSaveJob}
            />
          )}

          {currentTab === 'intelligence' && (
            <AdvancedIntelligencePage
              student={student}
              careers={careers}
              onSelectCareer={handleSelectCareer}
              onNavigateToRoadmap={() => setCurrentTab('roadmap')}
            />
          )}

          {currentTab === 'coach' && (
            <AICoachPage
              student={student}
              targetCareer={currentTargetCareer}
              onNavigateToSkillGap={() => setCurrentTab('skill-gap')}
              onNavigateToRoadmap={() => setCurrentTab('roadmap')}
            />
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation & Drawer */}
      <MobileNav
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setCurrentTab(tab);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        isDrawerOpen={isMobileDrawerOpen}
        onCloseDrawer={() => setIsMobileDrawerOpen(false)}
        onOpenDrawer={() => setIsMobileDrawerOpen(true)}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
        initialMode={authModalMode}
      />

      {/* Smart Minimal Onboarding Flow ("Do you have a resume?" -> YES: Upload / NO: 5 Questions) */}
      <OnboardingFlow
        userName={user?.name || student?.name || 'Candidate'}
        isOpen={isOnboardingOpen}
        initialStage={onboardingStage}
        onClose={() => setIsOnboardingOpen(false)}
        onComplete={handleOnboardingComplete}
      />

      {/* 4-Question Cognitive Career Assessment Modal */}
      <CareerAssessmentModal
        isOpen={isAssessmentOpen}
        onClose={() => setIsAssessmentOpen(false)}
        onComplete={handleAssessmentComplete}
      />
    </div>
  );
};

export default App;
