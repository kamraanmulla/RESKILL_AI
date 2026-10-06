import React, { useState, useEffect } from 'react';
import { Capacitor } from '@capacitor/core';
import { App as CapApp } from '@capacitor/app';
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

// Route to NavItemId mapping
const ROUTE_TAB_MAP: Record<string, NavItemId> = {
  '/dashboard': 'dashboard',
  '/resume': 'resume',
  '/profile': 'profile',
  '/career': 'careers',
  '/careers': 'careers',
  '/match': 'match',
  '/skill-gap': 'skill-gap',
  '/roadmap': 'roadmap',
  '/learning': 'learning',
  '/jobs': 'jobs',
  '/intelligence': 'intelligence',
  '/coach': 'coach'
};

const normalizePath = (raw?: string): string => {
  if (typeof window === 'undefined') return '/';
  const path = (raw || window.location.pathname).toLowerCase().split('?')[0].replace(/\/+$/, '') || '/';
  return path;
};

export const App: React.FC = () => {
  const initialPath = normalizePath();
  const initialUser = api.getCurrentUser();

  // Global View Mode (Landing Page vs Main Platform Application)
  const [isLandingView, setIsLandingView] = useState<boolean>(() => initialPath === '/landing');
  const [currentTab, setCurrentTab] = useState<NavItemId>(() => {
    if (initialUser && initialPath in ROUTE_TAB_MAP) {
      return ROUTE_TAB_MAP[initialPath];
    }
    return 'dashboard';
  });
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>(() => initialPath === '/signup' ? 'signup' : 'signin');
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  // Authentication State
  const [user, setUser] = useState<AuthUser | null>(() => initialUser);
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

  // Validate session on mount
  useEffect(() => {
    const initAuth = async () => {
      const verified = await api.validateSession();
      if (verified) {
        setUser(verified);
        await refreshAllData();
      } else {
        setUser(null);
        const path = normalizePath();
        if (path !== '/landing' && path !== '/signup') {
          window.history.replaceState(null, '', '/login');
        }
      }
    };
    initAuth();
  }, []);

  // Synchronize URL and enforce route guards
  useEffect(() => {
    const syncRoute = () => {
      const path = normalizePath();
      if (!user) {
        if (path === '/landing') {
          setIsLandingView(true);
        } else {
          setIsLandingView(false);
          const targetMode = path === '/signup' ? 'signup' : 'signin';
          setAuthMode(targetMode);
          if (path !== '/login' && path !== '/signup') {
            window.history.replaceState(null, '', '/login');
          }
        }
      } else {
        if (path === '/landing') {
          setIsLandingView(true);
        } else if (path === '/login' || path === '/signup' || path === '/') {
          setIsLandingView(false);
          setCurrentTab('dashboard');
          window.history.replaceState(null, '', '/dashboard');
        } else if (path === '/assessment') {
          setIsLandingView(false);
          setCurrentTab('dashboard');
          setIsAssessmentOpen(true);
          window.history.replaceState(null, '', '/dashboard');
        } else if (path in ROUTE_TAB_MAP) {
          setIsLandingView(false);
          setCurrentTab(ROUTE_TAB_MAP[path]);
        } else {
          setIsLandingView(false);
          setCurrentTab('dashboard');
          window.history.replaceState(null, '', '/dashboard');
        }
      }
    };

    syncRoute();
    window.addEventListener('popstate', syncRoute);
    return () => window.removeEventListener('popstate', syncRoute);
  }, [user]);

  // Navigate to tab and update browser history URL
  const navigateToTab = (tab: NavItemId) => {
    setCurrentTab(tab);
    setIsLandingView(false);
    const path = tab === 'careers' ? '/career' : `/${tab}`;
    if (normalizePath() !== path) {
      window.history.pushState(null, '', path);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Android Native Hardware Back Button Handler
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    let handle: any = null;
    CapApp.addListener('backButton', () => {
      if (isAuthModalOpen) {
        setIsAuthModalOpen(false);
        return;
      }
      if (isAssessmentOpen) {
        setIsAssessmentOpen(false);
        return;
      }
      if (isOnboardingOpen) {
        setIsOnboardingOpen(false);
        return;
      }
      if (isMobileDrawerOpen) {
        setIsMobileDrawerOpen(false);
        return;
      }
      if (isLandingView) {
        setIsLandingView(false);
        return;
      }

      if (currentTab !== 'dashboard') {
        navigateToTab('dashboard');
        return;
      }

      CapApp.minimizeApp().catch(() => CapApp.exitApp());
    }).then((h) => {
      handle = h;
    });

    return () => {
      if (handle) {
        handle.remove();
      }
    };
  }, [isAuthModalOpen, isAssessmentOpen, isOnboardingOpen, isMobileDrawerOpen, isLandingView, currentTab]);

  const currentTargetCareer = careers.find((c) => c.id === student.targetCareerId) || careers[0];
  const personalized = isProfilePersonalized(student);

  // Auth Handlers
  const handleLoginSuccess = async (authUser: AuthUser) => {
    setUser(authUser);
    setIsLandingView(false);
    setCurrentTab('dashboard');
    window.history.replaceState(null, '', '/dashboard');
    await refreshAllData();
    if (!authUser.isDemo && (!student.skills || student.skills.length === 0)) {
      setIsOnboardingOpen(true);
    }
  };

  // Onboarding & Assessment Flow Transitions
  const handleOnboardingComplete = async (updatedProfile: StudentProfile) => {
    setIsOnboardingOpen(false);
    await refreshAllData();
    setIsAssessmentOpen(true);
  };

  const handleAssessmentComplete = async (updatedProfile: StudentProfile) => {
    setIsAssessmentOpen(false);
    await refreshAllData();
    navigateToTab('dashboard');
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    setIsLandingView(false);
    setCurrentTab('dashboard');
    window.history.replaceState(null, '', '/login');
    setStudent(createBlankStudentProfile());
    setCareerMatch(createBlankCareerMatch());
    setSkillGaps(createBlankSkillGaps());
    setRoadmap([]);
    setStats(createBlankProgressStats());
  };

  const handleResetToZeroKnowledge = async () => {
    await api.resetToZeroKnowledge();
    await refreshAllData();
    navigateToTab('dashboard');
  };

  const handleLoadDemoProfile = async () => {
    await api.loadDemoProfile();
    await refreshAllData();
    navigateToTab('dashboard');
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
        initialMode={authMode}
        onLoginSuccess={handleLoginSuccess}
        onExploreLanding={() => {
          setIsLandingView(true);
          window.history.pushState(null, '', '/landing');
        }}
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
            if (user) {
              navigateToTab('resume');
            } else {
              window.history.pushState(null, '', '/login');
            }
          }}
          onExploreCareers={() => {
            setIsLandingView(false);
            if (user) {
              navigateToTab('careers');
            } else {
              window.history.pushState(null, '', '/login');
            }
          }}
          onEnterDashboard={() => {
            setIsLandingView(false);
            if (user) {
              navigateToTab('dashboard');
            } else {
              window.history.pushState(null, '', '/login');
            }
          }}
          onOpenAuth={() => {
            setIsLandingView(false);
            if (!user) {
              window.history.pushState(null, '', '/login');
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
          onSelectTab={navigateToTab}
          targetCareer={currentTargetCareer}
          onViewLanding={() => {
            setIsLandingView(true);
            window.history.pushState(null, '', '/landing');
          }}
          isPersonalized={personalized}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-28 md:pb-10">
        <Topbar
          currentPageTitle={pageTitles[currentTab]}
          student={student}
          user={user}
          onOpenMobileNav={() => setIsMobileDrawerOpen(true)}
          onOpenProfile={() => navigateToTab('profile')}
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
              onNavigate={navigateToTab}
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
              onContinueToProfile={() => navigateToTab('profile')}
              onNavigateToDashboard={() => navigateToTab('dashboard')}
            />
          )}

          {currentTab === 'profile' && (
            <ProfilePage
              student={student}
              careers={careers}
              onUpdateProfile={handleUpdateProfile}
              onNavigateToCareers={() => navigateToTab('careers')}
              onNavigateToResume={() => navigateToTab('resume')}
              onNavigateToDashboard={() => navigateToTab('dashboard')}
            />
          )}

          {currentTab === 'careers' && (
            <CareerSelectionPage
              careers={careers}
              selectedCareerId={student.targetCareerId}
              onSelectCareer={handleSelectCareer}
              onViewCareerMatch={() => navigateToTab('match')}
            />
          )}

          {currentTab === 'match' && (
            <CareerMatchPage
              career={currentTargetCareer}
              matchData={careerMatch}
              onNavigateToSkillGap={() => navigateToTab('skill-gap')}
              onNavigateToRoadmap={() => navigateToTab('roadmap')}
              onNavigateToCareers={() => navigateToTab('careers')}
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
              onNavigateToRoadmap={() => navigateToTab('roadmap')}
            />
          )}

          {currentTab === 'coach' && (
            <AICoachPage
              student={student}
              targetCareer={currentTargetCareer}
              onNavigateToSkillGap={() => navigateToTab('skill-gap')}
              onNavigateToRoadmap={() => navigateToTab('roadmap')}
            />
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation & Drawer */}
      <MobileNav
        currentTab={currentTab}
        onSelectTab={navigateToTab}
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

      {/* Adaptive Career Intelligence Assessment Modal */}
      <CareerAssessmentModal
        isOpen={isAssessmentOpen}
        onClose={() => setIsAssessmentOpen(false)}
        onComplete={handleAssessmentComplete}
        onNavigateToRoadmap={() => setCurrentTab('roadmap')}
      />
    </div>
  );
};

export default App;
