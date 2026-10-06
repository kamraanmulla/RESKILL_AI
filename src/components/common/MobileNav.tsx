import React from 'react';
import {
  LayoutDashboard,
  Target,
  Milestone,
  Briefcase,
  Layers,
  X,
  FileText,
  User,
  Compass,
  BarChart3,
  BookOpen,
  Sparkles,
  Bot
} from 'lucide-react';
import { NavItemId } from './Sidebar';

interface MobileNavProps {
  currentTab: NavItemId;
  onSelectTab: (tab: NavItemId) => void;
  isDrawerOpen: boolean;
  onCloseDrawer: () => void;
  onOpenDrawer: () => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({
  currentTab,
  onSelectTab,
  isDrawerOpen,
  onCloseDrawer,
  onOpenDrawer
}) => {
  const bottomItems = [
    { id: 'dashboard' as NavItemId, label: 'Home', icon: LayoutDashboard },
    { id: 'match' as NavItemId, label: 'Assess', icon: Target },
    { id: 'roadmap' as NavItemId, label: 'Roadmap', icon: Milestone },
    { id: 'learning' as NavItemId, label: 'Learn', icon: BookOpen },
    { id: 'jobs' as NavItemId, label: 'Jobs', icon: Briefcase },
    { id: 'profile' as NavItemId, label: 'Profile', icon: User }
  ];

  const drawerItems = [
    { id: 'dashboard' as NavItemId, label: 'Main Dashboard', icon: LayoutDashboard },
    { id: 'resume' as NavItemId, label: 'My Resume', icon: FileText },
    { id: 'profile' as NavItemId, label: 'Student Profile', icon: User },
    { id: 'careers' as NavItemId, label: 'Career Selection', icon: Compass },
    { id: 'match' as NavItemId, label: 'Career Match & Assess', icon: Target },
    { id: 'skill-gap' as NavItemId, label: 'Skill Gap Breakdown', icon: BarChart3 },
    { id: 'roadmap' as NavItemId, label: 'Learning Roadmap', icon: Milestone },
    { id: 'learning' as NavItemId, label: 'Curated Learning', icon: BookOpen },
    { id: 'jobs' as NavItemId, label: 'Jobs & Opportunities', icon: Briefcase },
    { id: 'intelligence' as NavItemId, label: 'Career Intelligence', icon: Sparkles },
    { id: 'coach' as NavItemId, label: 'AI Career Coach', icon: Bot }
  ];

  return (
    <>
      {/* Bottom bar for mobile screens */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-paper-border z-40 flex items-center justify-around px-1 shadow-card pb-safe pt-1">
        {bottomItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex flex-col items-center justify-center flex-1 py-1 px-0.5 transition-colors touch-manipulation ${
                isActive ? 'text-forest-800 font-semibold' : 'text-charcoal-500 hover:text-charcoal-900'
              }`}
            >
              <Icon className={`w-4 h-4 mb-1 ${isActive ? 'text-forest-800 stroke-[2.2]' : 'text-charcoal-500'}`} />
              <span className="text-[10px] font-sans leading-none tracking-tight">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Mobile Menu Drawer Overlay */}
      {isDrawerOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex flex-col justify-end">
          <div
            className="fixed inset-0 bg-charcoal-900/40 backdrop-blur-xs transition-opacity"
            onClick={onCloseDrawer}
          />
          <div className="relative bg-white border-t border-paper-border rounded-t-lg p-5 z-10 max-h-[80vh] overflow-y-auto space-y-3 animate-in slide-in-from-bottom">
            <div className="flex items-center justify-between pb-3 border-b border-paper-border">
              <span className="font-serif font-medium text-lg text-charcoal-900">
                Navigation Menu
              </span>
              <button
                onClick={onCloseDrawer}
                className="p-1 rounded text-charcoal-500 hover:text-charcoal-900"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 gap-1">
              {drawerItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectTab(item.id);
                      onCloseDrawer();
                    }}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-xs text-left transition-colors ${
                      isActive
                        ? 'bg-forest-100 text-forest-900 font-semibold'
                        : 'text-charcoal-700 hover:bg-paper-muted'
                    }`}
                  >
                    <Icon className="w-4 h-4 text-forest-800" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
