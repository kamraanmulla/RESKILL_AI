import React from 'react';
import {
  ArrowRight,
  Sparkles,
  Award,
  Milestone,
  Clock,
  Briefcase,
  Play,
  CheckCircle2,
  AlertTriangle,
  Compass,
  FileText,
  Lock,
  Target,
  UploadCloud,
  Edit3
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { SkillBar } from '../components/common/SkillBar';
import { ProgressRing } from '../components/common/ProgressRing';
import { ZeroKnowledgeHero } from '../components/dashboard/ZeroKnowledgeHero';
import {
  StudentProfile,
  CareerRole,
  ProgressStats,
  SkillGapItem,
  RoadmapStep,
  LearningResource
} from '../types';

interface DashboardPageProps {
  student: StudentProfile;
  targetCareer: CareerRole;
  stats: ProgressStats;
  skillGaps: SkillGapItem[];
  roadmap: RoadmapStep[];
  resources: LearningResource[];
  onNavigate: (tab: any) => void;
  onSelectRoadmapStep: (stepKey: string) => void;
  onLoadDemoProfile?: () => void;
  onUploadSampleResume?: () => void;
  onStartOnboarding?: (stage?: 'fork' | 'upload' | 'questions') => void;
  onStartAssessment?: () => void;
  onSelectCareer?: (careerId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  student,
  targetCareer,
  stats,
  skillGaps,
  roadmap,
  resources,
  onNavigate,
  onSelectRoadmapStep,
  onLoadDemoProfile,
  onUploadSampleResume,
  onStartOnboarding,
  onStartAssessment,
  onSelectCareer
}) => {
  const isPersonalized = Boolean(
    student.resumeFile !== null || (student.skills && student.skills.length > 0)
  );

  const currentStep = roadmap.find((s) => s.status === 'in_progress') || roadmap[0] || {
    id: 'step_01',
    stepNumber: '01',
    title: 'Baseline Skills Assessment',
    whyItMatters: 'Complete your profile to unlock custom sequenced modules.',
    topics: ['Profile Calibration', 'Skill Indexing'],
    estimatedTime: '15 mins',
    skillKey: 'Core'
  };

  const topGaps = skillGaps.filter((g) => g.gap > 0).slice(0, 3);
  const featuredResources = resources.slice(0, 2);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Top Greeting Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-4 border-b border-paper-border">
        <div>
          <span className="text-[10px] uppercase font-mono tracking-widest text-charcoal-400 block mb-1">
            Academic Engineering Workspace
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-medium text-charcoal-900 tracking-tight">
            Good morning, {student.name.split(' ')[0] || 'Candidate'}.
          </h1>
          <p className="text-sm text-charcoal-600 mt-1 font-normal">
            {isPersonalized
              ? 'Your career direction is actively taking shape.'
              : 'Your workspace has started in zero-knowledge mode. Follow the prompt below to initialize.'}
          </p>
        </div>

        {/* Current Target Role Badge */}
        <div className="flex items-center gap-3 bg-white px-3.5 py-2 rounded-sm border border-paper-border shadow-subtle self-start sm:self-auto">
          <Compass className="w-4 h-4 text-forest-800" />
          <div className="text-xs">
            <span className="text-charcoal-500 text-[10px] block uppercase font-mono">
              Target Trajectory
            </span>
            <span className="font-semibold text-charcoal-900">
              {targetCareer ? targetCareer.title : 'Not Selected'}
            </span>
          </div>
          {isPersonalized ? (
            <button
              onClick={() => onNavigate('match')}
              className="ml-2 text-xs font-mono text-forest-800 hover:underline"
            >
              {targetCareer.currentMatchPercentage}% Match →
            </button>
          ) : (
            <button
              onClick={() => onNavigate('careers')}
              className="ml-2 text-xs font-mono text-forest-800 hover:underline"
            >
              Select Trajectory →
            </button>
          )}
        </div>
      </div>

      {/* ZERO KNOWLEDGE COLD-START ACTIVATION HERO */}
      {!isPersonalized ? (
        <ZeroKnowledgeHero
          onNavigateToResume={() => onNavigate('resume')}
          onNavigateToProfile={() => onNavigate('profile')}
          onNavigateToCareers={() => onNavigate('careers')}
          onLoadDemoProfile={onLoadDemoProfile || (() => { })}
          onUploadSampleResume={onUploadSampleResume || (() => { })}
          onStartOnboarding={onStartOnboarding}
          targetCareer={targetCareer}
        />
      ) : (
        <div className="space-y-4">
          {/* Assessment Calibration Prompt if not completed */}
          {!student.assessmentSignals && onStartAssessment && (
            <div className="p-4 bg-amber-50/80 border border-amber-200 rounded-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-charcoal-700">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-900 flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-semibold text-charcoal-900 block">
                    Complete 4-Question Career Cognitive Assessment (+150 Readiness Points)
                  </span>
                  <span className="text-[11px] text-charcoal-600">
                    Understand how you think, debug, and work to align your hiring readiness points.
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={onStartAssessment}
                className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 text-white font-medium rounded-sm shadow-subtle text-xs transition-colors shrink-0"
              >
                Start Assessment (4 Qs) →
              </button>
            </div>
          )}

          {/* PERSONALIZED NEXT BEST ACTION CARD */}
          <div className="p-5 bg-white border border-forest-800/80 rounded-md shadow-card relative overflow-hidden">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-sm bg-forest-800 text-white flex items-center justify-center shrink-0 shadow-subtle">
                  <Sparkles className="w-5 h-5 text-forest-100" />
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-forest-800 font-semibold">
                      Personalized Next Best Action
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 bg-forest-100 text-forest-900 rounded border border-forest-200">
                      {stats.nextRecommendedAction?.impact || '+8% Readiness'}
                    </span>
                  </div>
                  <h2 className="font-serif text-xl font-medium text-charcoal-900">
                    {stats.nextRecommendedAction?.action || 'Continue Roadmap Module'}
                  </h2>
                  <p className="text-xs text-charcoal-600 max-w-xl leading-relaxed">
                    {stats.nextRecommendedAction?.reason ||
                      'Closing your identified skill gap is the highest-leverage path to improving your hiring readiness.'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2.5 shrink-0 self-end sm:self-center">
                <button
                  onClick={() => onNavigate('roadmap')}
                  className="px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center gap-1.5"
                >
                  <span>Open Roadmap Step</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4 Core Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Career Readiness"
          value={isPersonalized ? `${stats.careerReadiness}%` : '—'}
          subtext={
            isPersonalized
              ? `${Math.round(stats.careerReadiness * 10)} / 1000 Pts • ${targetCareer.title}`
              : 'Requires Profile Setup'
          }
          trend={isPersonalized ? { value: `${Math.round(stats.careerReadiness * 10)} pts`, positive: true } : undefined}
          onClick={() => (isPersonalized ? onNavigate('match') : onNavigate('resume'))}
        />
        <StatCard
          label="Skills Completed"
          value={
            isPersonalized
              ? `${stats.skillsCompleted.completed} / ${stats.skillsCompleted.total}`
              : '0 / 0'
          }
          subtext={isPersonalized ? 'Verified competencies' : 'No skills indexed yet'}
          icon={Award}
          onClick={() => onNavigate('profile')}
        />
        <StatCard
          label="Roadmap Progress"
          value={isPersonalized ? `${stats.roadmapProgress}%` : 'Locked'}
          subtext={isPersonalized ? 'Active curriculum' : 'Awaiting baseline'}
          icon={Milestone}
          onClick={() => (isPersonalized ? onNavigate('roadmap') : onNavigate('resume'))}
        />
        <StatCard
          label="Learning Hours"
          value={isPersonalized ? `${stats.learningHours}h` : '0h'}
          subtext={isPersonalized ? 'Logged platform time' : 'Start your first module'}
          icon={Clock}
          onClick={() => onNavigate('learning')}
        />
      </div>

      {/* Main 2-Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Roadmap Progress & Skill Gaps */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Roadmap Focus */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-paper-border">
              <div className="flex items-center gap-2">
                <Milestone className="w-4 h-4 text-forest-800" />
                <h3 className="font-serif text-lg font-medium text-charcoal-900">
                  {isPersonalized ? 'Current Roadmap Focus' : 'Curriculum Sequencer'}
                </h3>
              </div>
              {isPersonalized && (
                <button
                  onClick={() => onNavigate('roadmap')}
                  className="text-xs font-mono text-forest-800 hover:underline flex items-center gap-1"
                >
                  <span>View Full Roadmap</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </div>

            {isPersonalized ? (
              <div className="p-4 bg-paper rounded-sm border border-paper-border space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-charcoal-400">
                      {currentStep.stepNumber}
                    </span>
                    <h4 className="font-serif text-base font-semibold text-charcoal-900">
                      {currentStep.title}
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-editorial-amberLight text-editorial-amber border border-amber-200">
                    In Progress
                  </span>
                </div>

                <p className="text-xs text-charcoal-600 leading-relaxed">
                  {currentStep.whyItMatters}
                </p>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {currentStep.topics.slice(0, 3).map((topic, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-[10px] font-mono rounded bg-white text-charcoal-700 border border-paper-border"
                    >
                      {topic}
                    </span>
                  ))}
                </div>

                <div className="pt-2 flex items-center justify-between text-xs border-t border-paper-border">
                  <span className="font-mono text-charcoal-500 text-[11px]">
                    Estimated: {currentStep.estimatedTime}
                  </span>
                  <button
                    onClick={() => onSelectRoadmapStep(currentStep.skillKey)}
                    className="text-forest-800 font-medium hover:underline flex items-center gap-1"
                  >
                    <span>Continue Module</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-6 bg-paper rounded-sm border border-dashed border-paper-border text-center space-y-3">
                <div className="w-10 h-10 mx-auto rounded-full bg-paper-muted flex items-center justify-center text-charcoal-500 border border-paper-border">
                  <Lock className="w-5 h-5 text-charcoal-600" />
                </div>
                <div>
                  <h4 className="font-serif text-base font-medium text-charcoal-900">
                    Roadmap Sequencing Paused
                  </h4>
                  <p className="text-xs text-charcoal-600 max-w-md mx-auto mt-1 leading-relaxed">
                    Our adaptive engine generates your sequential learning milestones by mapping where you currently stand against your target role. Provide your resume or manual skills to generate your customized path.
                  </p>
                </div>
                <div className="pt-2 flex items-center justify-center gap-3">
                  <button
                    onClick={() => onNavigate('resume')}
                    className="px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1.5"
                  >
                    <UploadCloud className="w-3.5 h-3.5" />
                    <span>Upload Resume</span>
                  </button>
                  <button
                    onClick={() => onNavigate('profile')}
                    className="px-3.5 py-2 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-800 text-xs font-medium rounded-sm transition-colors flex items-center gap-1.5"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Manual Profile</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Skill Gap Snapshot */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-paper-border">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-editorial-rust" />
                <h3 className="font-serif text-lg font-medium text-charcoal-900">
                  {isPersonalized ? 'Critical Skill Gaps' : `Target Expectations: ${targetCareer.title}`}
                </h3>
              </div>
              {isPersonalized ? (
                <button
                  onClick={() => onNavigate('skill-gap')}
                  className="text-xs font-mono text-forest-800 hover:underline flex items-center gap-1"
                >
                  <span>Full Gap Table</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              ) : (
                <span className="text-[10px] font-mono text-editorial-rust bg-editorial-rustLight/60 px-2 py-0.5 rounded border border-editorial-rust/20">
                  Awaiting Skill Calibration
                </span>
              )}
            </div>

            <div className="space-y-3">
              {topGaps.map((gap) => (
                <div
                  key={gap.skill}
                  className="p-3 bg-paper rounded-sm border border-paper-border text-xs flex items-center justify-between"
                >
                  <div>
                    <div className="font-semibold text-charcoal-900 flex items-center gap-2">
                      <span>{gap.skill}</span>
                      <span className="text-[10px] font-mono text-charcoal-400">({gap.category})</span>
                    </div>
                    <div className="text-[11px] text-charcoal-500 font-mono mt-0.5">
                      {isPersonalized ? (
                        <>Your Level: {gap.yourLevel}% • Target Benchmark: {gap.requiredLevel}%</>
                      ) : (
                        <>Target Expectation: {gap.requiredLevel}% • Current: Not Assessed</>
                      )}
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-mono font-semibold text-editorial-rust block">
                      {isPersonalized ? `-${gap.gap}% Gap` : 'Uncalibrated'}
                    </span>
                    <button
                      onClick={() => (isPersonalized ? onNavigate('roadmap') : onNavigate('profile'))}
                      className="text-[11px] text-forest-800 hover:underline font-medium"
                    >
                      {isPersonalized ? 'Add to Study →' : 'Set Skill →'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 1 Column: Readiness Meter, Recommended Learning & Recent Activity */}
        <div className="space-y-6">
          {/* Readiness Meter Card */}
          <div className="bg-white border border-paper-border rounded-md p-6 text-center space-y-3">
            <span className="text-[10px] font-mono uppercase tracking-widest text-charcoal-400 block">
              {isPersonalized ? 'Hiring Probability' : 'Personalization Status'}
            </span>
            <ProgressRing
              progress={isPersonalized ? targetCareer.currentMatchPercentage : 0}
              size={120}
              strokeWidth={8}
              sublabel={isPersonalized ? 'MATCH' : 'BLANK'}
            />
            <div className="text-xs text-charcoal-600 leading-relaxed">
              {isPersonalized ? (
                <>
                  <strong className="text-charcoal-900">{targetCareer.title}</strong> alignment.
                </>
              ) : (
                'Zero-knowledge profile initialized. Add resume or skills to compute hiring match.'
              )}
            </div>
            <button
              onClick={() => (isPersonalized ? onNavigate('match') : onNavigate('resume'))}
              className="w-full py-1.5 bg-paper hover:bg-paper-dark border border-paper-border text-xs text-charcoal-800 font-medium rounded-sm transition-colors"
            >
              {isPersonalized ? 'Analyze Benchmark Details' : 'Calibrate Profile Now'}
            </button>
          </div>

          {/* Recommended Learning Widget */}
          <div className="bg-white border border-paper-border rounded-md p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-paper-border">
              <span className="font-serif text-base font-medium text-charcoal-900">
                Recommended Learning
              </span>
              <button
                onClick={() => onNavigate('learning')}
                className="text-xs font-mono text-forest-800 hover:underline"
              >
                All →
              </button>
            </div>

            <div className="space-y-2.5">
              {featuredResources.map((res) => (
                <div
                  key={res.id}
                  onClick={() => onNavigate('learning')}
                  className="p-2.5 bg-paper hover:bg-paper-muted rounded-sm border border-paper-border cursor-pointer transition-colors text-xs space-y-1"
                >
                  <div className="font-medium text-charcoal-900 line-clamp-1">
                    {res.title}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-charcoal-500">
                    <span>{res.platform} • {res.duration}</span>
                    <span className="text-forest-800 font-semibold">{res.skillTag}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity Feed */}
          <div className="bg-white border border-paper-border rounded-md p-5 space-y-3">
            <span className="font-serif text-base font-medium text-charcoal-900 block pb-2 border-b border-paper-border">
              Recent Activity
            </span>

            <div className="space-y-2 text-xs">
              {stats.recentActivity.slice(0, 3).map((act) => (
                <div key={act.id} className="text-charcoal-600 space-y-0.5">
                  <div className="text-charcoal-900 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3 h-3 text-forest-700 shrink-0" />
                    <span className="line-clamp-1">{act.action}</span>
                  </div>
                  <div className="text-[10px] font-mono text-charcoal-400 pl-4.5">
                    {act.time}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
