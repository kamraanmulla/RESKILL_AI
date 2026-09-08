import React from 'react';

interface SkillComparisonProps {
  skill: string;
  studentLevel: number;
  benchmarkLevel: number;
  category?: string;
  priority?: 'High' | 'Medium' | 'Low' | 'Strong';
}

export const SkillComparison: React.FC<SkillComparisonProps> = ({
  skill,
  studentLevel,
  benchmarkLevel,
  category,
  priority
}) => {
  const gap = benchmarkLevel - studentLevel;
  const isSurplus = gap <= 0;

  return (
    <div className="p-3 bg-white border border-paper-border rounded-md hover:border-charcoal-400 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div>
          <span className="text-xs font-semibold text-charcoal-900">{skill}</span>
          {category && (
            <span className="ml-2 text-[10px] text-charcoal-500 uppercase tracking-wider font-mono">
              {category}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {priority && (
            <span
              className={`text-[10px] font-mono px-1.5 py-0.5 rounded-sm border ${
                priority === 'High'
                  ? 'bg-editorial-rustLight text-editorial-rust border-orange-200'
                  : priority === 'Medium'
                  ? 'bg-editorial-amberLight text-editorial-amber border-amber-200'
                  : priority === 'Strong'
                  ? 'bg-forest-100 text-forest-800 border-forest-200'
                  : 'bg-paper-muted text-charcoal-600 border-paper-border'
              }`}
            >
              {priority}
            </span>
          )}
          <span
            className={`text-xs font-mono font-medium ${
              isSurplus ? 'text-forest-700' : 'text-editorial-rust'
            }`}
          >
            {isSurplus ? '✓ Match' : `-${gap}% Gap`}
          </span>
        </div>
      </div>

      {/* Stacked comparison bar */}
      <div className="space-y-1">
        <div className="flex items-center text-[10px] text-charcoal-500 justify-between">
          <span>You: {studentLevel}%</span>
          <span>Target: {benchmarkLevel}%</span>
        </div>
        <div className="relative h-2.5 w-full bg-paper-dark rounded-none overflow-hidden border border-paper-border">
          {/* Target marker background */}
          <div
            className="absolute top-0 bottom-0 bg-charcoal-200"
            style={{ width: `${benchmarkLevel}%` }}
          />
          {/* Student fill */}
          <div
            className={`absolute top-0 bottom-0 transition-all duration-300 ${
              isSurplus ? 'bg-forest-800' : 'bg-charcoal-800'
            }`}
            style={{ width: `${studentLevel}%` }}
          />
          {/* Target line */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-charcoal-900 z-10"
            style={{ left: `${benchmarkLevel}%` }}
          />
        </div>
      </div>
    </div>
  );
};
