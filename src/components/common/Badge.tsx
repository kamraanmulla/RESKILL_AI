import React from 'react';

export type BadgeVariant =
  | 'default'
  | 'forest'
  | 'amber'
  | 'rust'
  | 'sage'
  | 'slate'
  | 'outline';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = ''
}) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  const variantClasses = {
    default: 'bg-paper-muted text-charcoal-700 border-paper-border',
    forest: 'bg-forest-100 text-forest-900 border-forest-200',
    amber: 'bg-editorial-amberLight text-editorial-amber border-[#FDE68A]',
    rust: 'bg-editorial-rustLight text-editorial-rust border-[#FED7AA]',
    sage: 'bg-editorial-sageLight text-editorial-sage border-[#C6E6D2]',
    slate: 'bg-slate-100 text-slate-800 border-slate-200',
    outline: 'bg-transparent text-charcoal-700 border-paper-border'
  }[variant];

  return (
    <span
      className={`inline-flex items-center font-medium rounded-sm border ${variantClasses} ${sizeClasses} ${className}`}
    >
      {children}
    </span>
  );
};
