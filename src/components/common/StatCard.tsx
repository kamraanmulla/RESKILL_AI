import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    positive: boolean;
  };
  className?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  trend,
  className = '',
  onClick
}) => {
  return (
    <div
      onClick={onClick}
      className={`bg-white border border-paper-border p-5 rounded-md transition-all duration-150 ${
        onClick ? 'cursor-pointer hover:border-charcoal-400 hover:shadow-subtle' : ''
      } ${className}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-500">
          {label}
        </span>
        {Icon && (
          <div className="w-8 h-8 rounded-sm bg-paper-muted flex items-center justify-center text-charcoal-700">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="font-serif text-3xl font-semibold text-charcoal-900 tracking-tight">
          {value}
        </span>
        {trend && (
          <span
            className={`text-xs font-medium ${
              trend.positive ? 'text-forest-700' : 'text-editorial-rust'
            }`}
          >
            {trend.positive ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-2 text-xs text-charcoal-600 leading-relaxed">
          {subtext}
        </p>
      )}
    </div>
  );
};
