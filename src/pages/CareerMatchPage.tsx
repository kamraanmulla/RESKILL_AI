import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Briefcase,
  Compass,
  Milestone
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { SkillComparison } from '../components/common/SkillComparison';
import { CareerRole, CareerMatch } from '../types';

interface CareerMatchPageProps {
  career: CareerRole;
  matchData: CareerMatch;
  onNavigateToSkillGap: () => void;
  onNavigateToRoadmap: () => void;
  onNavigateToCareers: () => void;
}

export const CareerMatchPage: React.FC<CareerMatchPageProps> = ({
  career,
  matchData,
  onNavigateToSkillGap,
  onNavigateToRoadmap,
  onNavigateToCareers
}) => {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Career Compatibility Match"
        subtitle={`Detailed alignment of your verified capabilities against ${career.title} market expectations.`}
        badge="Compatibility Audit"
        action={
          <button
            onClick={onNavigateToCareers}
            className="px-3 py-1.5 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-700 text-xs font-medium rounded-sm transition-colors flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5 text-charcoal-500" />
            <span>Switch Target Role</span>
          </button>
        }
      />

      {/* Hero Compatibility Overview Banner */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-6 border-b border-paper-border">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-widest text-charcoal-500 mb-1">
              Evaluated Benchmark
            </div>
            <h2 className="font-serif text-3xl font-medium text-charcoal-900 tracking-tight">
              {career.title.toUpperCase()}
            </h2>
            <p className="text-xs text-charcoal-600 mt-1 max-w-xl leading-relaxed">
              {career.description}
            </p>
          </div>

          {/* Large Match Percentage Card */}
          <div className="flex items-center gap-4 bg-paper p-4 rounded-sm border border-paper-border shrink-0">
            <div>
              <div className="text-[10px] uppercase font-mono tracking-wider text-charcoal-500">
                Overall Match
              </div>
              <div className="font-serif text-4xl font-semibold text-charcoal-900 mt-0.5">
                {matchData.overallMatch}%
              </div>
            </div>
            <div className="w-12 h-12 rounded-sm bg-forest-800 text-white flex items-center justify-center font-serif text-lg font-bold shadow-subtle">
              ✓
            </div>
          </div>
        </div>

        {/* Market Context Insights Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-3 bg-paper rounded-sm border border-paper-border text-xs">
            <span className="text-[10px] font-mono uppercase text-charcoal-500 block">Market Demand</span>
            <span className="font-semibold text-charcoal-900 mt-0.5 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-forest-700" />
              {career.demandLevel} Demand
            </span>
          </div>

          <div className="p-3 bg-paper rounded-sm border border-paper-border text-xs">
            <span className="text-[10px] font-mono uppercase text-charcoal-500 block">Average Entry Salary</span>
            <span className="font-semibold text-charcoal-900 mt-0.5 flex items-center gap-1">
              <Briefcase className="w-3.5 h-3.5 text-forest-700" />
              {career.avgSalary}
            </span>
          </div>

          <div className="p-3 bg-paper rounded-sm border border-paper-border text-xs">
            <span className="text-[10px] font-mono uppercase text-charcoal-500 block">Experience Requirement</span>
            <span className="font-semibold text-charcoal-900 mt-0.5">
              {career.experienceLevel} (0-2 Yrs)
            </span>
          </div>
        </div>
      </div>

      {/* Two-Column Breakdown: Strong Matches vs Needs Improvement */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strong Matches Column */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-paper-border">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Strong Matches
              </h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-forest-100 text-forest-900 rounded border border-forest-200">
              {matchData.strongMatches.length} Verified
            </span>
          </div>

          <div className="space-y-3">
            {matchData.strongMatches.map((item) => (
              <div
                key={item.skill}
                className="p-3.5 bg-paper rounded-sm border border-paper-border text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-charcoal-900 flex items-center gap-1.5">
                    <span className="text-forest-700 font-bold">✓</span>
                    {item.skill}
                  </span>
                  <span className="font-mono text-[11px] text-forest-800 bg-forest-50 px-1.5 py-0.2 rounded border border-forest-200">
                    {item.studentLevel}% vs {item.requiredLevel}% req
                  </span>
                </div>
                <p className="text-[11px] text-charcoal-600 leading-relaxed">
                  {item.note}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Needs Improvement Column */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-paper-border">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-editorial-rust" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Needs Improvement
              </h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-editorial-rustLight text-editorial-rust rounded border border-orange-200">
              {matchData.needsImprovement.length} Gaps
            </span>
          </div>

          <div className="space-y-3">
            {matchData.needsImprovement.map((item) => (
              <div
                key={item.skill}
                className="p-3.5 bg-paper rounded-sm border border-paper-border text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-charcoal-900 flex items-center gap-1.5">
                    <span className="text-editorial-rust font-bold">!</span>
                    {item.skill}
                  </span>
                  <span className="font-mono text-[11px] text-editorial-rust font-medium">
                    -{item.gap}% Gap ({item.priority} Priority)
                  </span>
                </div>
                <div className="text-[10px] text-charcoal-500 font-mono flex justify-between">
                  <span>Current: {item.studentLevel}%</span>
                  <span>Required: {item.requiredLevel}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Horizontal Skill Benchmark Visualization */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-paper-border">
          <div>
            <h3 className="font-serif text-xl font-medium text-charcoal-900">
              Proficiency vs Industry Benchmark
            </h3>
            <p className="text-xs text-charcoal-500">
              Clean horizontal comparison of your verified skills against entry-level industry thresholds.
            </p>
          </div>
          <div className="flex items-center gap-4 text-[10px] font-mono text-charcoal-500">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-charcoal-800 inline-block" /> You
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-charcoal-200 inline-block" /> Benchmark
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {matchData.benchmarkComparison.map((item) => (
            <SkillComparison
              key={item.skill}
              skill={item.skill}
              studentLevel={item.studentLevel}
              benchmarkLevel={item.benchmarkLevel}
              category={item.category}
            />
          ))}
        </div>

        {/* Bottom CTA bar */}
        <div className="pt-4 border-t border-paper-border flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-charcoal-600">
            Ready to systematically address your skill gaps?
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateToSkillGap}
              className="px-4 py-2 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-900 text-xs font-medium rounded-sm transition-colors"
            >
              View Full Gap Table
            </button>
            <button
              onClick={onNavigateToRoadmap}
              className="px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1.5"
            >
              <Milestone className="w-3.5 h-3.5" />
              <span>Open Customized Roadmap</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
