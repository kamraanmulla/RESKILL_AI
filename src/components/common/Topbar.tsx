import React, { useState, useRef, useEffect } from 'react';
import {
  Bell,
  Search,
  Menu,
  Check,
  GraduationCap,
  LogOut,
  Sparkles,
  RotateCcw,
  User,
  ShieldCheck,
  LogIn,
  ChevronDown
} from 'lucide-react';
import { StudentProfile, AuthUser } from '../../types';

interface TopbarProps {
  currentPageTitle: string;
  student: StudentProfile;
  user: AuthUser | null;
  onOpenMobileNav: () => void;
  onOpenProfile: () => void;
  onOpenAuth: () => void;
  onLogout: () => void;
  onResetToZeroKnowledge: () => void;
  onLoadDemoProfile: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentPageTitle,
  student,
  user,
  onOpenMobileNav,
  onOpenProfile,
  onOpenAuth,
  onLogout,
  onResetToZeroKnowledge,
  onLoadDemoProfile
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isPersonalized = Boolean(student.resumeFile !== null || (student.skills && student.skills.length > 0));

  const notifications = [
    {
      id: 1,
      title: isPersonalized ? 'Roadmap Milestone Active' : 'System Initialized',
      text: isPersonalized
        ? 'Module 05: REST API Design is prioritized for your target role.'
        : 'Zero-knowledge candidate environment active.',
      time: 'Just now'
    },
    {
      id: 2,
      title: isPersonalized ? 'Market Benchmark Synchronized' : 'Profile Required',
      text: isPersonalized
        ? `${student.skills.length} skills indexed against target career benchmarks.`
        : 'Provide your resume or enter skills to unlock personalized hiring match.',
      time: '5m ago'
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
        {/* Testing Switcher Shortcut Pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2 py-1 bg-paper border border-paper-border rounded text-[11px] font-mono text-charcoal-600">
          <span className={`w-2 h-2 rounded-full ${isPersonalized ? 'bg-forest-600' : 'bg-editorial-amber'}`} />
          <span>{isPersonalized ? 'Personalized' : 'Zero-Knowledge'}</span>
        </div>

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

        {/* User Account Capsule / Dropdown */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2.5 pl-2 pr-1.5 py-1 rounded-sm hover:bg-paper-muted transition-colors border border-transparent hover:border-paper-border text-left"
          >
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-charcoal-900 leading-tight">
                {student.name || 'Candidate'}
              </div>
              <div className="text-[10px] font-mono text-charcoal-500 flex items-center justify-end gap-1">
                <GraduationCap className="w-2.5 h-2.5" />
                <span>{isPersonalized ? 'Calibrated' : 'Zero-Knowledge'}</span>
              </div>
            </div>
            <div className="w-7 h-7 rounded-sm bg-forest-800 text-white font-serif text-xs font-semibold flex items-center justify-center">
              {student.name ? student.name.charAt(0) : 'C'}
            </div>
            <ChevronDown className="w-3 h-3 text-charcoal-400 hidden sm:block" />
          </button>

          {/* User Account Menu Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-72 bg-white border border-paper-border rounded-md shadow-modal p-2 z-40 animate-in fade-in text-xs space-y-1">
              <div className="p-2.5 border-b border-paper-border">
                <div className="font-semibold text-charcoal-900 truncate">
                  {student.name}
                </div>
                <div className="text-[11px] text-charcoal-500 font-mono truncate">
                  {student.email || 'guest@reskill.ai'}
                </div>
                <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono bg-paper border border-paper-border">
                  <span className={`w-1.5 h-1.5 rounded-full ${isPersonalized ? 'bg-forest-600' : 'bg-editorial-amber'}`} />
                  <span>{isPersonalized ? `${student.skills.length} Skills Calibrated` : 'Zero-Knowledge Slate'}</span>
                </div>
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onOpenProfile();
                  }}
                  className="w-full px-2.5 py-1.5 text-left rounded hover:bg-paper-muted flex items-center gap-2 text-charcoal-700 hover:text-charcoal-900"
                >
                  <User className="w-3.5 h-3.5 text-charcoal-500" />
                  <span>Student Profile & Skills</span>
                </button>

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onResetToZeroKnowledge();
                  }}
                  className="w-full px-2.5 py-1.5 text-left rounded hover:bg-paper-muted flex items-center gap-2 text-editorial-amber hover:text-editorial-amber"
                  title="Reset profile to 0 skills to test cold start"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-editorial-amber" />
                  <span>Reset to Zero-Knowledge Slate</span>
                </button>

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onLoadDemoProfile();
                  }}
                  className="w-full px-2.5 py-1.5 text-left rounded hover:bg-paper-muted flex items-center gap-2 text-forest-800 hover:text-forest-900 font-medium"
                  title="Loads Parvez Ahmed's profile"
                >
                  <Sparkles className="w-3.5 h-3.5 text-forest-700" />
                  <span>Load Demo Student (Parvez Ahmed)</span>
                </button>
              </div>

              <div className="pt-1 border-t border-paper-border space-y-0.5">
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onOpenAuth();
                  }}
                  className="w-full px-2.5 py-1.5 text-left rounded hover:bg-paper-muted flex items-center gap-2 text-charcoal-700"
                >
                  <LogIn className="w-3.5 h-3.5 text-charcoal-500" />
                  <span>Switch Account / Sign In</span>
                </button>

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onLogout();
                  }}
                  className="w-full px-2.5 py-1.5 text-left rounded hover:bg-editorial-rustLight/50 flex items-center gap-2 text-editorial-rust"
                >
                  <LogOut className="w-3.5 h-3.5 text-editorial-rust" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
