import React from 'react';
import {
  ArrowRight,
  CheckCircle2,
  Compass,
  FileText,
  Milestone,
  Target,
  GraduationCap
} from 'lucide-react';
import { CareerRole } from '../types';

interface LandingPageProps {
  onStartResume: () => void;
  onExploreCareers: () => void;
  onEnterDashboard: () => void;
  targetCareer: CareerRole;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartResume,
  onExploreCareers,
  onEnterDashboard,
  targetCareer
}) => {
  return (
    <div className="min-h-screen bg-paper text-charcoal-900 selection:bg-forest-100">
      {/* Editorial Navigation Header */}
      <header className="border-b border-paper-border bg-paper/95 backdrop-blur-sm sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-sm bg-forest-800 text-white font-serif font-bold text-base flex items-center justify-center shadow-subtle">
              R
            </div>
            <div>
              <span className="font-serif font-semibold text-lg text-charcoal-900 tracking-tight leading-none block">
                ReSkill<span className="text-forest-700 font-sans font-normal text-xs ml-0.5">.AI</span>
              </span>
              <span className="text-[10px] text-charcoal-500 font-mono tracking-wider uppercase block">
                University Career Framework
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onEnterDashboard}
              className="text-xs text-charcoal-700 hover:text-charcoal-900 font-medium px-3 py-1.5 rounded-sm hover:bg-paper-muted transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={onStartResume}
              className="text-xs bg-forest-800 hover:bg-forest-900 text-white font-medium px-4 py-2 rounded-sm shadow-subtle transition-all flex items-center gap-1.5"
            >
              <span>Launch Platform</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-14 pb-16 px-4 sm:px-6 border-b border-paper-border">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-forest-50 border border-forest-200 text-forest-800 text-xs font-mono">
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Built for College Students & Early-Career Engineers</span>
          </div>

          <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl font-medium tracking-tight text-charcoal-900 leading-[1.15] max-w-3xl mx-auto">
            Build a career path that fits you.
          </h1>

          <p className="text-base sm:text-lg text-charcoal-600 max-w-2xl mx-auto leading-relaxed font-normal">
            Understand your skills, discover suitable career paths, and turn your skill gaps into a practical learning roadmap.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={onStartResume}
              className="w-full sm:w-auto px-6 py-3 bg-forest-800 hover:bg-forest-900 text-white text-sm font-medium rounded-sm shadow-subtle transition-all flex items-center justify-center gap-2"
            >
              <span>Analyze My Resume</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onExploreCareers}
              className="w-full sm:w-auto px-6 py-3 bg-white hover:bg-paper-muted text-charcoal-900 border border-paper-border text-sm font-medium rounded-sm transition-all flex items-center justify-center gap-2"
            >
              <Compass className="w-4 h-4 text-charcoal-500" />
              <span>Explore Careers</span>
            </button>
          </div>

          <div className="pt-4 flex items-center justify-center gap-6 text-xs text-charcoal-500 font-mono">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" /> No generic AI buzzwords
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" /> Evidence-based skill gap
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" /> Curated curriculum
            </span>
          </div>
        </div>

        {/* Dashboard Visual Preview Card */}
        <div className="max-w-5xl mx-auto mt-12 bg-white border border-paper-border rounded-md shadow-card overflow-hidden">
          {/* Mock Window Bar */}
          <div className="bg-paper-muted px-4 py-2.5 border-b border-paper-border flex items-center justify-between text-xs text-charcoal-500 font-mono">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-paper-border inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-paper-border inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-paper-border inline-block" />
              <span className="ml-2 text-charcoal-700">reskill.ai/dashboard/student-profile</span>
            </div>
            <span className="text-[11px] text-forest-800 font-medium">● System Benchmark Ready</span>
          </div>

          {/* Inner Dashboard Preview */}
          <div className="p-6 sm:p-8 space-y-6 bg-paper/30">
            {/* Header snippet */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-paper-border">
              <div>
                <span className="text-[10px] uppercase font-mono tracking-widest text-charcoal-400">
                  Live Editorial Preview
                </span>
                <h3 className="font-serif text-2xl font-medium text-charcoal-900 mt-0.5">
                  Parvez Ahmed — Career Readiness Overview
                </h3>
                <p className="text-xs text-charcoal-600">
                  Target Trajectory: <strong className="text-charcoal-900">{targetCareer.title}</strong>
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-charcoal-500 font-mono">Compatibility</div>
                  <div className="font-serif text-2xl font-semibold text-charcoal-900">82%</div>
                </div>
                <div className="w-12 h-12 rounded-sm bg-forest-100 border border-forest-200 flex items-center justify-center font-mono text-forest-900 font-bold text-sm">
                  82%
                </div>
              </div>
            </div>

            {/* Metric widgets preview */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white p-3.5 border border-paper-border rounded-sm">
                <div className="text-[10px] font-mono uppercase text-charcoal-500">Skills Detected</div>
                <div className="font-serif text-2xl font-semibold text-charcoal-900 mt-1">14</div>
                <div className="text-[11px] text-forest-700 mt-0.5">8 Strong Matches</div>
              </div>
              <div className="bg-white p-3.5 border border-paper-border rounded-sm">
                <div className="text-[10px] font-mono uppercase text-charcoal-500">Roadmap Progress</div>
                <div className="font-serif text-2xl font-semibold text-charcoal-900 mt-1">56%</div>
                <div className="text-[11px] text-charcoal-500 mt-0.5">Module 5 of 9 Active</div>
              </div>
              <div className="bg-white p-3.5 border border-paper-border rounded-sm">
                <div className="text-[10px] font-mono uppercase text-charcoal-500">Highest Gap</div>
                <div className="font-serif text-2xl font-semibold text-editorial-rust mt-1">-35%</div>
                <div className="text-[11px] text-charcoal-600 mt-0.5">REST API Architecture</div>
              </div>
              <div className="bg-white p-3.5 border border-paper-border rounded-sm">
                <div className="text-[10px] font-mono uppercase text-charcoal-500">Curated Jobs</div>
                <div className="font-serif text-2xl font-semibold text-charcoal-900 mt-1">5</div>
                <div className="text-[11px] text-charcoal-500 mt-0.5">Top: Linear (87% Match)</div>
              </div>
            </div>

            {/* Callout preview */}
            <div className="p-4 bg-white border border-paper-border rounded-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-forest-800 font-semibold">
                  Next Best Action
                </span>
                <div className="text-sm font-semibold text-charcoal-900">
                  Master REST API Design & Error Handling
                </div>
                <p className="text-xs text-charcoal-600 mt-0.5">
                  Closing this gap will lift your Full Stack career readiness score to 91%.
                </p>
              </div>
              <button
                onClick={onEnterDashboard}
                className="shrink-0 px-3 py-1.5 bg-paper-muted hover:bg-paper-dark border border-paper-border text-charcoal-900 text-xs font-medium rounded-sm transition-colors"
              >
                Open Dashboard →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Structured 3-Step Methodology Section */}
      <section className="py-16 px-4 sm:px-6 max-w-5xl mx-auto">
        <div className="text-center max-w-xl mx-auto mb-12">
          <span className="text-xs font-mono uppercase tracking-widest text-forest-800 block mb-1">
            System Architecture
          </span>
          <h2 className="font-serif text-3xl font-medium text-charcoal-900">
            From fragmented coursework to industry readiness.
          </h2>
          <p className="text-sm text-charcoal-600 mt-2">
            No vague generic feedback. A rigorous, evidence-based progression pipeline designed for engineering graduates.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-white border border-paper-border rounded-md space-y-3">
            <div className="w-8 h-8 rounded-sm bg-forest-50 border border-forest-200 text-forest-800 font-mono text-sm font-semibold flex items-center justify-center">
              01
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Detect & Index Skills
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 leading-relaxed">
              Upload your academic resume. The parser indexes your verified frontend, backend, database, and tooling competencies with granular score ratings.
            </p>
          </div>

          <div className="p-6 bg-white border border-paper-border rounded-md space-y-3">
            <div className="w-8 h-8 rounded-sm bg-forest-50 border border-forest-200 text-forest-800 font-mono text-sm font-semibold flex items-center justify-center">
              02
            </div>
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Benchmark Target Roles
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 leading-relaxed">
              Select roles like Full Stack, Backend, or ML Engineer. Get a side-by-side gap table comparing your proficiency against actual entry-level job criteria.
            </p>
          </div>

          <div className="p-6 bg-white border border-paper-border rounded-md space-y-3">
            <div className="w-8 h-8 rounded-sm bg-forest-50 border border-forest-200 text-forest-800 font-mono text-sm font-semibold flex items-center justify-center">
              03
            </div>
            <div className="flex items-center gap-2">
              <Milestone className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Execute Targeted Roadmap
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 leading-relaxed">
              Follow a vertical 9-step timeline complete with why it matters, curated technical video tutorials, capstone deliverables, and matching job listings.
            </p>
          </div>
        </div>
      </section>

      {/* Editorial Footer */}
      <footer className="border-t border-paper-border py-8 px-4 sm:px-6 bg-paper-muted/50">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-charcoal-500 font-mono">
          <div className="flex items-center gap-2">
            <span className="font-serif font-semibold text-charcoal-900">ReSkillAI</span>
            <span>•</span>
            <span>University Career Intelligence Platform</span>
          </div>
          <div>
            <span>Developed for College Engineering Departments</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
