import React from 'react';
import {
  TrendingUp,
  Award,
  Milestone,
  Clock,
  CheckCircle2,
  ArrowRight,
  Flame,
  Zap,
  Target
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { StatCard } from '../components/common/StatCard';
import { ProgressRing } from '../components/common/ProgressRing';
import { ProgressStats, CareerRole } from '../types';

interface ProgressDashboardPageProps {
  stats: ProgressStats;
  targetCareer: CareerRole;
  onNavigateToRoadmap: (stepKey?: string) => void;
  onNavigateToLearning: (skill?: string) => void;
}

export const ProgressDashboardPage: React.FC<ProgressDashboardPageProps> = ({
  stats,
  targetCareer,
  onNavigateToRoadmap,
  onNavigateToLearning
}) => {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Progress & Growth Intelligence"
        subtitle="Continuous tracking of your verified engineering competencies and career velocity."
        badge="Analytics Engine"
        action={
          <div className="flex items-center gap-1.5 px-3 py-1 bg-white border border-paper-border rounded-sm text-xs font-mono">
            <Flame className="w-3.5 h-3.5 text-editorial-rust" />
            <span>{stats.studyStreakDays} Day Study Streak</span>
          </div>
        }
      />

      {/* High-Level 4-Stat Metric Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Career Readiness"
          value={`${stats.careerReadiness}%`}
          subtext={`Targeting ${targetCareer.title}`}
          icon={TrendingUp}
          trend={{ value: '4% this week', positive: true }}
        />
        <StatCard
          label="Skills Completed"
          value={`${stats.skillsCompleted.completed} / ${stats.skillsCompleted.total}`}
          subtext="Verified competencies"
          icon={Award}
        />
        <StatCard
          label="Roadmap Progress"
          value={`${stats.roadmapProgress}%`}
          subtext={`${stats.roadmapProgress}% of roadmap completed`}
          icon={Milestone}
        />
        <StatCard
          label="Learning Hours"
          value={`${stats.learningHours}h`}
          subtext="Total platform study time"
          icon={Clock}
        />
      </div>

      {/* Main Focus & Readiness Diagnostic */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2-Cols: Current Focus & Next Recommended Action */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Module Focus Card */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-paper-border">
              <span className="text-[10px] font-mono uppercase tracking-widest text-forest-800 font-semibold">
                Current Focus Module
              </span>
              <span className="text-xs font-mono text-charcoal-500">
                {stats.currentFocus.hoursLeft}
              </span>
            </div>

            <div>
              <h3 className="font-serif text-xl font-medium text-charcoal-900">
                {stats.currentFocus.title}
              </h3>
              <p className="text-xs text-charcoal-600 mt-1">
                {stats.currentFocus.subtitle}
              </p>
            </div>

            <div className="p-3 bg-paper rounded-sm border border-paper-border flex items-center justify-between">
              <div className="text-xs text-charcoal-700">
                Action: <strong>{stats.nextRecommendedAction.action}</strong>
              </div>
              <button
                onClick={() => onNavigateToRoadmap(stats.nextRecommendedAction.stepId || 'Core')}
                className="px-3 py-1 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1"
              >
                <span>Continue</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Next Recommended Skill / Action Banner */}
          <div className="p-5 bg-paper rounded-md border border-paper-border space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase tracking-wider text-editorial-amber font-semibold flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5" />
                <span>Highest Yield Next Action</span>
              </span>
              <span className="text-xs font-mono font-bold text-forest-800 bg-forest-100 px-2 py-0.5 rounded border border-forest-200">
                {stats.nextRecommendedAction.impact}
              </span>
            </div>

            <div>
              <h4 className="font-serif text-lg font-medium text-charcoal-900">
                {stats.nextRecommendedAction.action}
              </h4>
              <p className="text-xs text-charcoal-600 mt-1 leading-relaxed">
                {stats.nextRecommendedAction.reason}
              </p>
            </div>

            <div className="pt-2 flex items-center gap-3">
              <button
                onClick={() => onNavigateToRoadmap(stats.nextRecommendedAction.stepId)}
                className="px-3.5 py-1.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors"
              >
                Open Roadmap Step
              </button>
              <button
                onClick={() => onNavigateToLearning()}
                className="px-3.5 py-1.5 bg-white hover:bg-paper-dark border border-paper-border text-charcoal-900 text-xs font-medium rounded-sm transition-colors"
              >
                View Recommended Tutorials
              </button>
            </div>
          </div>

          {/* Weekly Learning Activity Strip */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-serif font-medium text-charcoal-900">
                Weekly Study Log
              </span>
              <span className="font-mono text-charcoal-500">
                {stats.learningHours > 0 ? `Total: ${stats.learningHours}h active` : 'No study logged yet'}
              </span>
            </div>

            {/* Micro bar distribution derived from user activity */}
            <div className="grid grid-cols-7 gap-2 pt-2 text-center">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, idx) => {
                const hours = stats.learningHours > 0
                  ? (idx === 6 ? Math.min(4, Math.round(stats.learningHours * 0.4)) : Math.min(2, Math.round(stats.learningHours * 0.1)))
                  : 0;
                return (
                  <div key={day} className="space-y-1.5">
                    <div className="h-20 bg-paper-dark rounded-none relative flex flex-col justify-end p-0.5 border border-paper-border">
                      <div
                        className="bg-forest-800 w-full transition-all duration-300"
                        style={{ height: `${(hours / 6.0) * 100}%` }}
                      />
                    </div>
                    <span className="text-[10px] font-mono text-charcoal-500 block">
                      {day}
                    </span>
                    <span className="text-[10px] font-mono text-charcoal-800 font-semibold block">
                      {hours}h
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right 1-Col: Readiness Ring & Recently Completed Log */}
        <div className="space-y-6">
          {/* Target Compatibility Diagnostic Ring */}
          <div className="bg-white border border-paper-border rounded-md p-6 text-center space-y-4">
            <span className="text-[10px] font-mono uppercase tracking-widest text-charcoal-400 block">
              Readiness Diagnostic
            </span>

            <ProgressRing
              progress={stats.careerReadiness}
              size={140}
              strokeWidth={10}
              sublabel="READINESS"
            />

            <div className="text-xs text-charcoal-600 leading-relaxed max-w-xs mx-auto">
              You are currently <strong className="text-charcoal-900">{stats.careerReadiness}% ready</strong> for an entry-level {targetCareer.title} opening.
            </div>
          </div>

          {/* Recently Completed Activity */}
          <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-paper-border">
              <Target className="w-4 h-4 text-forest-800" />
              <h4 className="font-serif text-base font-medium text-charcoal-900">
                Recently Completed
              </h4>
            </div>

            <div className="space-y-3">
              {stats.recentActivity.map((act) => (
                <div
                  key={act.id}
                  className="p-2.5 bg-paper rounded-sm border border-paper-border text-xs space-y-0.5"
                >
                  <div className="font-medium text-charcoal-900 flex items-start gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-forest-700 shrink-0 mt-0.5" />
                    <span>{act.action}</span>
                  </div>
                  <div className="text-[10px] font-mono text-charcoal-400 pl-5">
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
