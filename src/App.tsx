import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import {
  StudentProfile,
  CareerRole,
  CareerMatch,
  SkillGapItem,
  RoadmapStep,
  LearningResource,
  JobOpportunity,
  ProgressStats
} from './types';
import {
  mockStudent,
  mockCareers,
  mockCareerMatch,
  mockSkillGaps,
  mockRoadmap,
  mockLearningResources,
  mockJobs,
  mockProgressStats
} from './data/mockData';

// Layout & Components
import { Sidebar, NavItemId } from './components/common/Sidebar';
import { Topbar } from './components/common/Topbar';
import { MobileNav } from './components/common/MobileNav';

// Pages
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ResumeUploadPage } from './pages/ResumeUploadPage';
import { ProfilePage } from './pages/ProfilePage';
import { CareerSelectionPage } from './pages/CareerSelectionPage';
import { CareerMatchPage } from './pages/CareerMatchPage';
import { SkillGapPage } from './pages/SkillGapPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { LearningPage } from './pages/LearningPage';
import { JobsPage } from './pages/JobsPage';

export const App: React.FC = () => {
  // Global View Mode (Landing Page vs Main Platform Application)
  const [isLandingView, setIsLandingView] = useState(false);
  const [currentTab, setCurrentTab] = useState<NavItemId>('dashboard');
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  // Platform Data State (Hydrated from service-layer placeholders)
  const [student, setStudent] = useState<StudentProfile>(mockStudent);
  const [careers, setCareers] = useState<CareerRole[]>(mockCareers);
  const [careerMatch, setCareerMatch] = useState<CareerMatch>(mockCareerMatch);
  const [skillGaps, setSkillGaps] = useState<SkillGapItem[]>(mockSkillGaps);
  const [roadmap, setRoadmap] = useState<RoadmapStep[]>(mockRoadmap);
  const [resources, setResources] = useState<LearningResource[]>(mockLearningResources);
  const [jobs, setJobs] = useState<JobOpportunity[]>(mockJobs);
  const [stats, setStats] = useState<ProgressStats>(mockProgressStats);

  // Filter state for learning page cross-navigation
  const [learningFilterSkill, setLearningFilterSkill] = useState<string | undefined>(undefined);

  // Load initial data through API layer
  useEffect(() => {
    const initData = async () => {
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

    initData();
  }, []);

  const currentTargetCareer = careers.find((c) => c.id === student.targetCareerId) || careers[0];

  // Actions
  const handleSelectCareer = async (careerId: string) => {
    await api.setTargetCareer(careerId);
    const updatedCareer = careers.find((c) => c.id === careerId);
    if (updatedCareer) {
      setStudent((prev) => ({ ...prev, targetCareerId: careerId }));
      setCareerMatch((prev) => ({
        ...prev,
        careerId: updatedCareer.id,
        careerTitle: updatedCareer.title,
        overallMatch: updatedCareer.currentMatchPercentage
      }));
    }
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
    const updated = await api.updateProfile(data);
    setStudent(updated);
    if (data.targetCareerId) {
      await handleSelectCareer(data.targetCareerId);
    }
  };

  const handleResumeUpload = async (fileInfo: { name: string; size: string; uploadedAt: string }) => {
    setStudent((prev) => ({
      ...prev,
      resumeFile: fileInfo
    }));
    const updatedStats = await api.getProgress();
    setStats(updatedStats);
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
    jobs: 'Jobs & Opportunities'
  };

  // If in Public Landing Page mode
  if (isLandingView) {
    return (
      <LandingPage
        targetCareer={currentTargetCareer}
        onStartResume={() => {
          setIsLandingView(false);
          setCurrentTab('resume');
        }}
        onExploreCareers={() => {
          setIsLandingView(false);
          setCurrentTab('careers');
        }}
        onEnterDashboard={() => {
          setIsLandingView(false);
          setCurrentTab('dashboard');
        }}
      />
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
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-20 md:pb-10">
        <Topbar
          currentPageTitle={pageTitles[currentTab]}
          student={student}
          onOpenMobileNav={() => setIsMobileDrawerOpen(true)}
          onOpenProfile={() => setCurrentTab('profile')}
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
            />
          )}

          {currentTab === 'resume' && (
            <ResumeUploadPage
              student={student}
              onUploadSuccess={handleResumeUpload}
              onContinueToProfile={() => setCurrentTab('profile')}
            />
          )}

          {currentTab === 'profile' && (
            <ProfilePage
              student={student}
              careers={careers}
              onUpdateProfile={handleUpdateProfile}
              onNavigateToCareers={() => setCurrentTab('careers')}
              onNavigateToResume={() => setCurrentTab('resume')}
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
    </div>
  );
};

export default App;
