import React, { useState } from 'react';
import {
  Bell,
  Search,
  Menu,
  Check,
  GraduationCap
} from 'lucide-react';
import { StudentProfile } from '../../types';

interface TopbarProps {
  currentPageTitle: string;
  student: StudentProfile;
  onOpenMobileNav: () => void;
  onOpenProfile: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentPageTitle,
  student,
  onOpenMobileNav,
  onOpenProfile
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const notifications = [
    {
      id: 1,
      title: 'Roadmap Milestone Unlocked',
      text: 'Module 05: REST API Design is ready for study.',
      time: '2h ago'
    },
    {
      id: 2,
      title: 'New Job Opportunity Match',
      text: 'Junior Full Stack Developer at Linear (87% match).',
      time: '1d ago'
    },
    {
      id: 3,
      title: 'Resume Skills Extracted',
      text: '14 skills successfully indexed from uploaded PDF.',
      time: 'Yesterday'
    }
  ];

  return (
    <header className="h-14 bg-paper-card border-b border-paper-border px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Mobile hamburger & breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileNav}
          className="md:hidden p-1.5 rounded-sm text-charcoal-600 hover:text-charcoal-900 hover:bg-paper-muted"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs text-charcoal-500 font-mono">
          <span>ReSkill</span>
          <span>/</span>
          <span className="font-sans font-medium text-charcoal-900 text-sm">
            {currentPageTitle}
          </span>
        </div>
      </div>

      {/* Center: Search box */}
      <div className="hidden lg:flex items-center w-80 relative">
        <Search className="w-3.5 h-3.5 absolute left-3 text-charcoal-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search skills, roadmaps, jobs..."
          className="w-full pl-8 pr-12 py-1.5 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
        />
        <span className="absolute right-2.5 text-[10px] font-mono text-charcoal-400 px-1 py-0.2 bg-paper-muted border border-paper-border rounded">
          ⌘K
        </span>
      </div>

      {/* Right: Notifications & User snippet */}
      <div className="flex items-center gap-3">
        {/* Notifications toggle */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-charcoal-600 hover:text-charcoal-900 hover:bg-paper-muted rounded-sm relative transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-editorial-rust rounded-full" />
          </button>

          {/* Notifications dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-paper-border rounded-md shadow-modal p-3 z-30 animate-in fade-in">
              <div className="flex items-center justify-between pb-2 border-b border-paper-border mb-2">
                <span className="font-serif text-sm font-medium text-charcoal-900">
                  Notifications
                </span>
                <span className="text-[10px] font-mono text-forest-700 cursor-pointer hover:underline flex items-center gap-1">
                  <Check className="w-3 h-3" /> Mark all read
                </span>
              </div>
              <div className="space-y-2">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className="p-2 rounded bg-paper-muted/60 hover:bg-paper-muted text-xs transition-colors"
                  >
                    <div className="font-medium text-charcoal-900 flex justify-between">
                      <span>{n.title}</span>
                      <span className="text-[10px] text-charcoal-400 font-mono">{n.time}</span>
                    </div>
                    <p className="text-[11px] text-charcoal-600 mt-0.5">{n.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User profile capsule */}
        <button
          onClick={onOpenProfile}
          className="flex items-center gap-2.5 pl-2 pr-1 py-1 rounded-sm hover:bg-paper-muted transition-colors border border-transparent hover:border-paper-border"
        >
          <div className="text-right hidden sm:block">
            <div className="text-xs font-semibold text-charcoal-900 leading-tight">
              {student.name}
            </div>
            <div className="text-[10px] font-mono text-charcoal-500 flex items-center justify-end gap-1">
              <GraduationCap className="w-2.5 h-2.5" />
              <span>B.Tech '26</span>
            </div>
          </div>
          <div className="w-7 h-7 rounded-sm bg-forest-800 text-white font-serif text-xs font-semibold flex items-center justify-center">
            {student.name.charAt(0)}
          </div>
        </button>
      </div>
    </header>
  );
};
