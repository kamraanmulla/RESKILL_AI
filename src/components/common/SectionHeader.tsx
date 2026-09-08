import React from 'react';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  badge?: string;
  action?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  badge,
  action,
  className = ''
}) => {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-4 border-b border-paper-border mb-6 ${className}`}>
      <div>
        {badge && (
          <span className="inline-block px-2 py-0.5 mb-2 text-xs font-semibold uppercase tracking-wider bg-forest-100 text-forest-900 rounded-sm border border-forest-200">
            {badge}
          </span>
        )}
        <h1 className="font-serif text-2xl sm:text-3xl font-medium text-charcoal-900 tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 text-sm text-charcoal-600 max-w-2xl leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="flex items-center gap-2 shrink-0">{action}</div>}
    </div>
  );
};
