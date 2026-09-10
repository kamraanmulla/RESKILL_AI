import React from 'react';
import {
  LayoutDashboard,
  FileText,
  Compass,
  Target,
  BarChart3,
  Milestone,
  BookOpen,
  Briefcase,
  User,
  ArrowUpRight,
  Sparkles,
  Bot
} from 'lucide-react';
import { CareerRole } from '../../types';

export type NavItemId =
  | 'dashboard'
  | 'resume'
  | 'profile'
  | 'careers'
  | 'match'
  | 'skill-gap'
  | 'roadmap'
  | 'learning'
  | 'jobs'
  | 'intelligence'
  | 'coach';

interface SidebarProps {
  currentTab: NavItemId;
  onSelectTab: (tab: NavItemId) => void;
  targetCareer: CareerRole;
  onViewLanding: () => void;
  isPersonalized?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  targetCareer,
  onViewLanding,
  isPersonalized = true
}) => {
  const navItems = [
    { id: 'dashboard' as NavItemId, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'resume' as NavItemId, label: 'My Resume', icon: FileText, badge: isPersonalized ? 'PDF' : 'Required' },
    { id: 'profile' as NavItemId, label: 'Student Profile', icon: User },
    { id: 'careers' as NavItemId, label: 'Career Selection', icon: Compass },
    {
      id: 'match' as NavItemId,
      label: 'Career Match',
      icon: Target,
      indicator: isPersonalized ? `${targetCareer.currentMatchPercentage}%` : '0%'
    },
    { id: 'skill-gap' as NavItemId, label: 'Skill Gap', icon: BarChart3 },
    { id: 'roadmap' as NavItemId, label: 'Roadmap', icon: Milestone, badge: isPersonalized ? 'Active' : 'Locked' },
    { id: 'learning' as NavItemId, label: 'Learning', icon: BookOpen },
    { id: 'jobs' as NavItemId, label: 'Jobs & Internships', icon: Briefcase },
    { id: 'intelligence' as NavItemId, label: 'Career Intelligence', icon: Sparkles, badge: 'Multi-Vector' },
    { id: 'coach' as NavItemId, label: 'AI Career Coach', icon: Bot, badge: 'AI' }
  ];


  return (
    <aside className="w-64 bg-paper-card border-r border-paper-border h-screen sticky top-0 flex flex-col justify-between select-none z-30">
      {/* Top Brand Header */}
      <div>
        <div className="p-5 border-b border-paper-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-sm bg-forest-800 flex items-center justify-center text-white font-serif font-bold text-base shadow-subtle">
              R
            </div>
            <div>
              <span className="font-serif font-semibold text-lg text-charcoal-900 tracking-tight leading-none block">
                ReSkill<span className="text-forest-700 font-sans font-normal text-xs ml-0.5">.AI</span>
              </span>
              <span className="text-[10px] text-charcoal-500 uppercase tracking-widest font-mono block mt-0.5">
                Career Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-0.5">
          <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-charcoal-400">
            Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs rounded-sm transition-all text-left ${
                  isActive
                    ? 'bg-forest-100 text-forest-900 font-medium border-l-2 border-forest-800 pl-2.5 shadow-subtle'
                    : 'text-charcoal-700 hover:bg-paper-muted hover:text-charcoal-900'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? 'text-forest-800' : 'text-charcoal-500'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span className="px-1.5 py-0.2 text-[9px] font-mono rounded bg-paper-dark text-charcoal-600 border border-paper-border">
                    {item.badge}
                  </span>
                )}
                {item.indicator && (
                  <span className="px-1.5 py-0.2 text-[10px] font-mono font-medium rounded bg-forest-200 text-forest-900">
                    {item.indicator}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Target Role Banner & Public View Link */}
      <div className="p-3 border-t border-paper-border space-y-2 bg-paper/60">
        <div className="p-3 rounded-sm border border-paper-border bg-white shadow-subtle">
          <div className="flex items-center justify-between text-[10px] uppercase font-mono tracking-wider text-charcoal-500 mb-1">
            <span>Target Role</span>
            <span className="text-forest-700 font-semibold">{targetCareer.currentMatchPercentage}% Match</span>
          </div>
          <div className="text-xs font-semibold text-charcoal-900 truncate">
            {targetCareer.title}
          </div>
          <button
            onClick={() => onSelectTab('careers')}
            className="mt-2 w-full py-1 text-[11px] text-center text-charcoal-600 hover:text-forest-800 bg-paper-muted hover:bg-paper-dark border border-paper-border rounded-sm transition-colors flex items-center justify-center gap-1"
          >
            <span>Change Target</span>
            <ArrowUpRight className="w-3 h-3" />
          </button>
        </div>

        <button
          onClick={onViewLanding}
          className="w-full py-1.5 text-xs text-charcoal-600 hover:text-charcoal-900 flex items-center justify-center gap-1.5 hover:bg-paper-muted rounded-sm transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5 text-charcoal-500" />
          <span>View Landing Overview</span>
        </button>
      </div>
    </aside>
  );
};
