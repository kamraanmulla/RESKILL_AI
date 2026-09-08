import React from 'react';
import { CheckCircle2 } from 'lucide-react';

interface SkillBarProps {
  name: string;
  percentage: number;
  level?: string;
  category?: string;
  verified?: boolean;
  benchmark?: number;
  className?: string;
}

export const SkillBar: React.FC<SkillBarProps> = ({
  name,
  percentage,
  level,
  verified = false,
  benchmark,
  className = ''
}) => {
  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 font-medium text-charcoal-800">
          <span>{name}</span>
          {verified && (
            <span title="Verified by coursework / project artifact">
              <CheckCircle2 className="w-3.5 h-3.5 text-forest-700 inline" />
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {level && (
            <span className="text-[11px] text-charcoal-500 uppercase tracking-wider font-mono">
              {level}
            </span>
          )}
          <span className="font-mono font-medium text-charcoal-900 text-xs">
            {percentage}%
          </span>
        </div>
      </div>

      {/* Progress track */}
      <div className="relative w-full h-2 bg-paper-dark rounded-none overflow-hidden border border-paper-border">
        <div
          className="h-full bg-forest-800 transition-all duration-300 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        />
        {benchmark !== undefined && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-charcoal-900 z-10"
            style={{ left: `${benchmark}%` }}
            title={`Required Benchmark: ${benchmark}%`}
          />
        )}
      </div>

      {benchmark !== undefined && (
        <div className="flex justify-between items-center text-[10px] text-charcoal-500 font-mono">
          <span>Current: {percentage}%</span>
          <span>Target Benchmark: {benchmark}%</span>
        </div>
      )}
    </div>
  );
};
