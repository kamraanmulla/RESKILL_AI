import React, { useState } from 'react';
import {
  ArrowRight,
  AlertCircle,
  Filter,
  CheckCircle2,
  ExternalLink,
  Milestone
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { Badge } from '../components/common/Badge';
import { SkillGapItem } from '../types';

interface SkillGapPageProps {
  skillGaps: SkillGapItem[];
  onNavigateToRoadmap: (stepKey?: string) => void;
}

export const SkillGapPage: React.FC<SkillGapPageProps> = ({
  skillGaps,
  onNavigateToRoadmap
}) => {
  const [priorityFilter, setPriorityFilter] = useState<'All' | 'High' | 'Medium' | 'Strong'>('All');

  const filteredGaps = priorityFilter === 'All'
    ? skillGaps
    : skillGaps.filter((g) => g.priority === priorityFilter);

  const topPriorities = skillGaps.filter((g) => g.priority === 'High');

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Skill Gap Analysis"
        subtitle="Quantitative evaluation of your current competencies compared with entry-level benchmarks."
        badge="Competency Benchmark"
      />

      {/* Top Priorities Callout Banner */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-paper-border">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-editorial-rust" />
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Top Priority Gaps
            </h3>
          </div>
          <span className="text-[10px] font-mono uppercase tracking-wider text-charcoal-500">
            Immediate Learning Focus
          </span>
        </div>

        <p className="text-xs text-charcoal-600 leading-relaxed">
          Closing these 2 high-priority competencies will yield the largest immediate boost to your hiring readiness score:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topPriorities.map((gap) => (
            <div
              key={gap.skill}
              className="p-4 bg-paper rounded-sm border border-paper-border space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-serif text-base font-semibold text-charcoal-900">
                  {gap.skill}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-editorial-rustLight text-editorial-rust border border-orange-200 font-semibold">
                  -{gap.gap}% Delta
                </span>
              </div>
              <p className="text-[11px] text-charcoal-600 leading-relaxed">
                {gap.recommendation}
              </p>
              <div className="pt-2 flex items-center justify-between">
                <span className="text-[10px] font-mono text-charcoal-500">
                  Current: {gap.yourLevel}% • Target: {gap.requiredLevel}%
                </span>
                <button
                  onClick={() => onNavigateToRoadmap(gap.skill)}
                  className="text-xs text-forest-800 hover:text-forest-900 font-medium flex items-center gap-1 hover:underline"
                >
                  <span>Open Module</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filter and Comparison Table */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-paper-border">
          <div>
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Comprehensive Comparison Matrix
            </h3>
            <p className="text-xs text-charcoal-500 font-mono">
              Calculated across 7 target competencies
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-charcoal-400" />
            {(['All', 'High', 'Medium', 'Strong'] as const).map((pri) => (
              <button
                key={pri}
                onClick={() => setPriorityFilter(pri)}
                className={`px-2.5 py-1 rounded-sm transition-colors ${
                  priorityFilter === pri
                    ? 'bg-charcoal-900 text-white font-medium'
                    : 'text-charcoal-600 hover:bg-paper-muted'
                }`}
              >
                {pri}
              </button>
            ))}
          </div>
        </div>

        {/* Clean Editorial Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-paper-border bg-paper-muted/50 text-[10px] font-mono uppercase text-charcoal-500 tracking-wider">
                <th className="py-2.5 px-3">Skill</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3 font-mono text-center">Your Level</th>
                <th className="py-2.5 px-3 font-mono text-center">Required Level</th>
                <th className="py-2.5 px-3 font-mono text-center">Gap</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3 text-right">Roadmap Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-paper-border font-mono">
              {filteredGaps.map((item) => {
                const isSatisfied = item.gap === 0;
                return (
                  <tr
                    key={item.skill}
                    className="hover:bg-paper-muted/40 transition-colors"
                  >
                    <td className="py-3 px-3 font-sans font-medium text-charcoal-900 flex items-center gap-1.5">
                      {isSatisfied ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-forest-700 inline" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-editorial-rust inline-block" />
                      )}
                      <span>{item.skill}</span>
                    </td>
                    <td className="py-3 px-3 text-charcoal-600 text-[11px] font-sans">
                      {item.category}
                    </td>
                    <td className="py-3 px-3 text-center text-charcoal-900 font-semibold">
                      {item.yourLevel}%
                    </td>
                    <td className="py-3 px-3 text-center text-charcoal-600">
                      {item.requiredLevel}%
                    </td>
                    <td className="py-3 px-3 text-center">
                      {isSatisfied ? (
                        <span className="text-forest-700 font-semibold">0% (Met)</span>
                      ) : (
                        <span className="text-editorial-rust font-semibold">-{item.gap}%</span>
                      )}
                    </td>
                    <td className="py-3 px-3 font-sans">
                      <Badge
                        variant={
                          item.priority === 'High'
                            ? 'rust'
                            : item.priority === 'Medium'
                            ? 'amber'
                            : 'forest'
                        }
                        size="sm"
                      >
                        {item.priority}
                      </Badge>
                    </td>
                    <td className="py-3 px-3 text-right font-sans">
                      <button
                        onClick={() => onNavigateToRoadmap(item.skill)}
                        className="text-xs text-charcoal-600 hover:text-forest-800 font-medium inline-flex items-center gap-1 hover:underline"
                      >
                        <span>{isSatisfied ? 'Review Topics' : 'Start Module'}</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="pt-4 border-t border-paper-border flex justify-end">
          <button
            onClick={() => onNavigateToRoadmap()}
            className="px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle flex items-center gap-2"
          >
            <Milestone className="w-3.5 h-3.5" />
            <span>Open Custom Roadmap</span>
          </button>
        </div>
      </div>
    </div>
  );
};
