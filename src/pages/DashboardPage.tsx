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
  FileText
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { SkillBar } from '../components/common/SkillBar';
import { ProgressRing } from '../components/common/ProgressRing';
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
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  student,
  targetCareer,
  stats,
  skillGaps,
  roadmap,
  resources,
  onNavigate,
  onSelectRoadmapStep
}) => {
  const currentStep = roadmap.find((s) => s.status === 'in_progress') || roadmap[3];
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
            Good morning, {student.name.split(' ')[0]}.
          </h1>
          <p className="text-sm text-charcoal-600 mt-1 font-normal">
            Your career direction is taking shape.
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
              {targetCareer.title}
            </span>
          </div>
          <button
            onClick={() => onNavigate('match')}
            className="ml-2 text-xs font-mono text-forest-800 hover:underline"
          >
            {targetCareer.currentMatchPercentage}% Match →
          </button>
        </div>
      </div>

      {/* Compact "Next Best Action" Highlight Card */}
      <div className="p-5 bg-white border border-forest-800/80 rounded-md shadow-card relative overflow-hidden">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-sm bg-forest-800 text-white flex items-center justify-center shrink-0 shadow-subtle">
              <Sparkles className="w-5 h-5 text-forest-100" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-forest-800 font-semibold">
                  Next Best Action
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-forest-100 text-forest-900 rounded border border-forest-200">
                  +9% Readiness
                </span>
              </div>
              <h2 className="font-serif text-xl font-medium text-charcoal-900">
                Learn REST APIs
              </h2>
              <p className="text-xs text-charcoal-600 max-w-xl leading-relaxed">
                REST APIs are currently one of the largest gaps for your selected career. Closing this 35% gap will complete your backend competency baseline.
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

      {/* 4 Core Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Career Readiness"
          value={`${stats.careerReadiness}%`}
          subtext="Targeting Full Stack"
          trend={{ value: '4% this week', positive: true }}
          onClick={() => onNavigate('match')}
        />
        <StatCard
          label="Skills Completed"
          value={`${stats.skillsCompleted.completed} / ${stats.skillsCompleted.total}`}
          subtext="Verified competencies"
          icon={Award}
          onClick={() => onNavigate('profile')}
        />
        <StatCard
          label="Roadmap Progress"
          value={`${stats.roadmapProgress}%`}
          subtext="Step 5 of 9 active"
          icon={Milestone}
          onClick={() => onNavigate('roadmap')}
        />
        <StatCard
          label="Learning Hours"
          value={`${stats.learningHours}h`}
          subtext="Logged platform time"
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
                  Current Roadmap Focus
                </h3>
              </div>
              <button
                onClick={() => onNavigate('roadmap')}
                className="text-xs font-mono text-forest-800 hover:underline flex items-center gap-1"
              >
                <span>View Full Roadmap</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

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
          </div>

          {/* Skill Gap Snapshot */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-paper-border">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-editorial-rust" />
                <h3 className="font-serif text-lg font-medium text-charcoal-900">
                  Critical Skill Gaps
                </h3>
              </div>
              <button
                onClick={() => onNavigate('skill-gap')}
                className="text-xs font-mono text-forest-800 hover:underline flex items-center gap-1"
              >
                <span>Full Gap Table</span>
                <ArrowRight className="w-3 h-3" />
              </button>
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
                      Your Level: {gap.yourLevel}% • Target Benchmark: {gap.requiredLevel}%
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-mono font-semibold text-editorial-rust block">
                      -{gap.gap}% Gap
                    </span>
                    <button
                      onClick={() => onNavigate('roadmap')}
                      className="text-[11px] text-forest-800 hover:underline font-medium"
                    >
                      Add to Study →
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
              Hiring Probability
            </span>
            <ProgressRing
              progress={targetCareer.currentMatchPercentage}
              size={120}
              strokeWidth={8}
              sublabel="MATCH"
            />
            <div className="text-xs text-charcoal-600 leading-relaxed">
              <strong className="text-charcoal-900">{targetCareer.title}</strong> alignment.
            </div>
            <button
              onClick={() => onNavigate('match')}
              className="w-full py-1.5 bg-paper hover:bg-paper-dark border border-paper-border text-xs text-charcoal-800 font-medium rounded-sm transition-colors"
            >
              Analyze Benchmark Details
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
