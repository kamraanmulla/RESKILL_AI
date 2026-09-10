import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  Edit3,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  GraduationCap,
  Target,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { CareerRole } from '../../types';

interface ZeroKnowledgeHeroProps {
  onNavigateToResume: () => void;
  onNavigateToProfile: () => void;
  onNavigateToCareers: () => void;
  onLoadDemoProfile: () => void;
  onUploadSampleResume: () => void;
  onStartOnboarding?: (stage?: 'fork' | 'upload' | 'questions') => void;
  targetCareer?: CareerRole;
}

export const ZeroKnowledgeHero: React.FC<ZeroKnowledgeHeroProps> = ({
  onNavigateToResume,
  onNavigateToProfile,
  onNavigateToCareers,
  onLoadDemoProfile,
  onUploadSampleResume,
  onStartOnboarding,
  targetCareer
}) => {
  const [isProcessingSample, setIsProcessingSample] = useState(false);

  const handleSampleClick = () => {
    setIsProcessingSample(true);
    setTimeout(() => {
      onUploadSampleResume();
      setIsProcessingSample(false);
    }, 600);
  };

  return (
    <div className="bg-white border-2 border-forest-800/20 rounded-lg p-6 sm:p-8 shadow-card space-y-6 relative overflow-hidden">
      {/* Subtle background accent */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-forest-50/60 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />

      {/* Header status bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-paper-border relative">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-editorial-amber opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-editorial-amber" />
          </span>
          <span className="text-[11px] font-mono uppercase tracking-widest font-semibold text-charcoal-700">
            System State: Zero-Knowledge Initial Baseline
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-charcoal-500 self-start sm:self-auto">
          <ShieldAlert className="w-3.5 h-3.5 text-editorial-amber" />
          <span>No skills or credentials indexed yet</span>
        </div>
      </div>

      {/* Main explanation */}
      <div className="max-w-2xl space-y-2 relative">
        <h2 className="font-serif text-2xl sm:text-3xl font-medium text-charcoal-900 tracking-tight leading-tight">
          Calibrate your career intelligence dashboard.
        </h2>
        <p className="text-xs sm:text-sm text-charcoal-600 leading-relaxed font-normal">
          We start with <strong>zero assumptions</strong> about your background. To calculate your real-time{' '}
          <strong>Career Readiness Score</strong>, audit your <strong>Skill Gaps</strong> against industry benchmarks,
          and construct your step-by-step <strong>Roadmap</strong>, initialize your profile using either pathway below:
        </p>
      </div>

      {/* Two Primary Pathway Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
        {/* Pathway 1: Upload Resume */}
        <div className="p-5 bg-paper rounded-md border border-paper-border hover:border-forest-800/60 transition-all flex flex-col justify-between space-y-4 group">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-sm bg-forest-800 text-white flex items-center justify-center shadow-subtle group-hover:scale-105 transition-transform">
                <FileText className="w-5 h-5 text-forest-100" />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-forest-100 text-forest-900 border border-forest-200 font-semibold uppercase">
                I Have a Resume
              </span>
            </div>

            <div>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Option 1: Upload Your Resume
              </h3>
              <p className="text-xs text-charcoal-600 mt-1 leading-relaxed">
                Provide a PDF or DOCX file. Our Gemini intelligence layer extracts your academic degree,
                skills, and projects in one shot without manual forms.
              </p>
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <button
              onClick={() => onStartOnboarding ? onStartOnboarding('upload') : onNavigateToResume()}
              className="flex-1 py-2 px-3.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center justify-center gap-2"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Resume</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              onClick={handleSampleClick}
              disabled={isProcessingSample}
              className="py-2 px-3 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-800 text-xs font-medium rounded-sm transition-colors flex items-center justify-center gap-1.5"
              title="Loads verified sample candidate resume"
            >
              {isProcessingSample ? (
                <Loader2 className="w-3.5 h-3.5 text-forest-800 animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-forest-700" />
              )}
              <span>Sample Resume</span>
            </button>
          </div>
        </div>

        {/* Pathway 2: Smart Minimal Onboarding (5 Core Questions) */}
        <div className="p-5 bg-paper rounded-md border border-paper-border hover:border-forest-800/60 transition-all flex flex-col justify-between space-y-4 group">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-sm bg-white border border-paper-border text-charcoal-800 flex items-center justify-center shadow-subtle group-hover:scale-105 transition-transform">
                <Sparkles className="w-5 h-5 text-forest-800" />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-semibold uppercase">
                No Resume Needed
              </span>
            </div>

            <div>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Option 2: Smart Minimal Onboarding
              </h3>
              <p className="text-xs text-charcoal-600 mt-1 leading-relaxed">
                No resume? Answer <strong>5 quick questions</strong> in under 2 minutes (Education, Skills chips, Interests, Direction, Projects). Ask less, understand more.
              </p>
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <button
              onClick={() => onStartOnboarding ? onStartOnboarding('questions') : onNavigateToProfile()}
              className="flex-1 py-2 px-3.5 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-900 text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center justify-center gap-2"
            >
              <Edit3 className="w-4 h-4 text-forest-800" />
              <span>Answer 5 Questions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={onNavigateToCareers}
              className="py-2 px-3 bg-paper hover:bg-paper-dark border border-paper-border text-charcoal-700 text-xs font-medium rounded-sm transition-colors flex items-center justify-center gap-1.5"
            >
              <Target className="w-3.5 h-3.5 text-charcoal-500" />
              <span>Browse Roles</span>
            </button>
          </div>
        </div>
      </div>

      {/* Evaluator Quick Demo Bar */}
      <div className="p-3 bg-paper-muted/80 rounded-sm border border-paper-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-charcoal-600">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-forest-800 shrink-0" />
          <span>
            <strong>Testing & Evaluation:</strong> Want to instantly see how a fully calibrated profile looks with live roadmaps and skill gap benchmarks?
          </span>
        </div>

        <button
          type="button"
          onClick={onLoadDemoProfile}
          className="shrink-0 px-3 py-1 bg-white hover:bg-forest-50 border border-forest-800/30 text-forest-900 font-medium rounded-sm text-xs transition-colors self-end sm:self-auto"
        >
          Load Demo Student (Parvez Ahmed) →
        </button>
      </div>
    </div>
  );
};
