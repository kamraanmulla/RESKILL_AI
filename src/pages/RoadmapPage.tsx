import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  ExternalLink,
  BookOpen,
  FolderGit2,
  Check,
  ChevronRight,
  CircleDot
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { Modal } from '../components/common/Modal';
import { RoadmapStep, CareerRole } from '../types';

interface RoadmapPageProps {
  roadmap: RoadmapStep[];
  targetCareer?: CareerRole;
  onToggleStepStatus: (stepId: string, newStatus: 'completed' | 'in_progress' | 'upcoming') => void;
  onNavigateToLearning: (skillTag?: string) => void;
}

export const RoadmapPage: React.FC<RoadmapPageProps> = ({
  roadmap,
  targetCareer,
  onToggleStepStatus,
  onNavigateToLearning
}) => {
  const [selectedStep, setSelectedStep] = useState<RoadmapStep | null>(null);

  const completedCount = roadmap.filter((s) => s.status === 'completed').length;
  const progressPercent = roadmap.length > 0 ? Math.round((completedCount / roadmap.length) * 100) : 0;

  const handleOpenStep = (step: RoadmapStep) => {
    setSelectedStep(step);
  };

  const handleStatusChange = (newStatus: 'completed' | 'in_progress' | 'upcoming') => {
    if (!selectedStep) return;
    onToggleStepStatus(selectedStep.id, newStatus);
    setSelectedStep({
      ...selectedStep,
      status: newStatus
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <SectionHeader
        title={`${targetCareer?.title || 'Personalized'} Career Roadmap`}
        subtitle={`A sequential, ${roadmap.length}-stage curriculum tailored to your capability profile and active skill gaps.`}
        badge="Curriculum Timeline"
        action={
          <div className="flex items-center gap-2 font-mono text-xs text-charcoal-600">
            <span>{completedCount} of {roadmap.length} Completed ({progressPercent}%)</span>
          </div>
        }
      />

      {/* Progress Metric Banner */}
      <div className="bg-white border border-paper-border rounded-md p-5 space-y-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="font-serif font-medium text-charcoal-900">
            Roadmap Completion Cadence
          </span>
          <span className="font-mono text-charcoal-500 font-medium">
            {progressPercent}% Finished
          </span>
        </div>
        <div className="h-2 w-full bg-paper-dark border border-paper-border overflow-hidden">
          <div
            className="h-full bg-forest-800 transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Vertical Career Timeline */}
      <div className="relative pl-6 sm:pl-8 space-y-6 before:content-[''] before:absolute before:top-4 before:bottom-4 before:left-[17px] sm:before:left-[21px] before:w-0.5 before:bg-paper-border">
        {roadmap.map((step) => {
          const isCompleted = step.status === 'completed';
          const isInProgress = step.status === 'in_progress';
          const isUpcoming = step.status === 'upcoming';

          return (
            <div
              key={step.id}
              onClick={() => handleOpenStep(step)}
              className={`relative group cursor-pointer transition-all duration-150 ${
                isInProgress ? 'scale-[1.01]' : ''
              }`}
            >
              {/* Timeline indicator node */}
              <div
                className={`absolute -left-[27px] sm:-left-[31px] top-4 w-6 h-6 rounded-sm flex items-center justify-center text-xs font-mono transition-colors shadow-subtle ${
                  isCompleted
                    ? 'bg-forest-800 text-white'
                    : isInProgress
                    ? 'bg-white border-2 border-forest-800 text-forest-800 ring-2 ring-forest-100'
                    : 'bg-paper-dark border border-paper-border text-charcoal-400'
                }`}
              >
                {isCompleted ? (
                  <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                ) : isInProgress ? (
                  <CircleDot className="w-3.5 h-3.5 text-forest-800" />
                ) : (
                  <span className="text-[10px]">{step.stepNumber}</span>
                )}
              </div>

              {/* Step Card */}
              <div
                className={`p-5 rounded-md border transition-all ${
                  isInProgress
                    ? 'bg-white border-forest-800 ring-1 ring-forest-800 shadow-card'
                    : isCompleted
                    ? 'bg-paper/70 border-paper-border hover:bg-white hover:border-charcoal-400'
                    : 'bg-paper/40 border-paper-border opacity-70 hover:opacity-100 hover:bg-white'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-semibold text-charcoal-400">
                      {step.stepNumber}
                    </span>
                    <h3 className="font-serif text-lg font-medium text-charcoal-900 group-hover:text-forest-900 transition-colors">
                      {step.title}
                    </h3>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="flex items-center gap-1 text-charcoal-500 font-mono text-[11px]">
                      <Clock className="w-3 h-3 text-charcoal-400" />
                      {step.estimatedTime}
                    </span>

                    <span
                      className={`px-2 py-0.5 text-[10px] font-mono rounded-sm border uppercase tracking-wider ${
                        isCompleted
                          ? 'bg-forest-100 text-forest-900 border-forest-200 font-medium'
                          : isInProgress
                          ? 'bg-editorial-amberLight text-editorial-amber border-amber-200 font-semibold'
                          : 'bg-paper-muted text-charcoal-500 border-paper-border'
                      }`}
                    >
                      {isCompleted ? 'Completed' : isInProgress ? 'Active Focus' : 'Upcoming'}
                    </span>

                    <ChevronRight className="w-4 h-4 text-charcoal-400 group-hover:text-charcoal-900 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </div>

                <p className="mt-2 text-xs text-charcoal-600 leading-relaxed max-w-2xl">
                  {step.whyItMatters}
                </p>

                {/* Key topics pills */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {(step.topics || []).slice(0, 3).map((topic, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-[10px] font-mono rounded bg-paper-muted text-charcoal-600 border border-paper-border"
                    >
                      {topic}
                    </span>
                  ))}
                  {(step.topics || []).length > 3 && (
                    <span className="px-1.5 py-0.5 text-[10px] font-mono text-charcoal-400">
                      +{(step.topics || []).length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step Detail Modal */}
      {selectedStep && (
        <Modal
          isOpen={!!selectedStep}
          onClose={() => setSelectedStep(null)}
          title={`${selectedStep.stepNumber} • ${selectedStep.title}`}
          subtitle={`Estimated duration: ${selectedStep.estimatedTime} • Module for ${selectedStep.skillKey}`}
          maxWidth="xl"
        >
          <div className="space-y-5 text-xs">
            {/* Status Switcher */}
            <div className="flex items-center justify-between p-3 bg-paper rounded-sm border border-paper-border">
              <span className="font-mono text-charcoal-600">Current Status:</span>
              <div className="flex items-center gap-1.5 font-mono text-[11px]">
                <button
                  onClick={() => handleStatusChange('completed')}
                  className={`px-2.5 py-1 rounded-sm border transition-colors flex items-center gap-1 ${
                    selectedStep.status === 'completed'
                      ? 'bg-forest-800 text-white border-forest-800'
                      : 'bg-white text-charcoal-700 hover:bg-paper-muted border-paper-border'
                  }`}
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Completed</span>
                </button>
                <button
                  onClick={() => handleStatusChange('in_progress')}
                  className={`px-2.5 py-1 rounded-sm border transition-colors ${
                    selectedStep.status === 'in_progress'
                      ? 'bg-editorial-amber text-white border-editorial-amber'
                      : 'bg-white text-charcoal-700 hover:bg-paper-muted border-paper-border'
                  }`}
                >
                  In Progress
                </button>
                <button
                  onClick={() => handleStatusChange('upcoming')}
                  className={`px-2.5 py-1 rounded-sm border transition-colors ${
                    selectedStep.status === 'upcoming'
                      ? 'bg-charcoal-800 text-white border-charcoal-800'
                      : 'bg-white text-charcoal-700 hover:bg-paper-muted border-paper-border'
                  }`}
                >
                  Upcoming
                </button>
              </div>
            </div>

            {/* Why It Matters */}
            <div className="space-y-1.5">
              <h4 className="font-serif text-sm font-semibold text-charcoal-900">
                Why It Matters
              </h4>
              <p className="text-charcoal-600 leading-relaxed">
                {selectedStep.whyItMatters}
              </p>
            </div>

            {/* Topics to Learn */}
            <div className="space-y-1.5">
              <h4 className="font-serif text-sm font-semibold text-charcoal-900">
                Core Topics & Deliverables
              </h4>
              <ul className="list-disc list-inside space-y-1 text-charcoal-600">
                {selectedStep.topics.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </div>

            {/* Practice Project */}
            <div className="p-3.5 bg-paper rounded-sm border border-paper-border space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-charcoal-900">
                <FolderGit2 className="w-4 h-4 text-forest-800" />
                <span>Capstone Exercise: {selectedStep.practiceProject.title}</span>
              </div>
              <p className="text-charcoal-600 text-[11px] leading-relaxed">
                {selectedStep.practiceProject.description}
              </p>
              <div className="text-[10px] font-mono text-forest-800 font-medium pt-1">
                Benchmark Deliverable: {selectedStep.practiceProject.deliverable}
              </div>
            </div>

            {/* Recommended Learning Resources */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-serif text-sm font-semibold text-charcoal-900 flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-forest-800" />
                  <span>Recommended Tutorials & Docs</span>
                </h4>
                <button
                  onClick={() => {
                    setSelectedStep(null);
                    onNavigateToLearning(selectedStep.skillKey);
                  }}
                  className="text-xs text-forest-800 hover:underline flex items-center gap-1 font-mono"
                >
                  <span>View All in Library</span>
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>

              <div className="space-y-2">
                {selectedStep.recommendedResources.map((res, i) => (
                  <a
                    key={i}
                    href={res.url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2.5 bg-paper-muted hover:bg-paper-dark rounded-sm border border-paper-border flex items-center justify-between transition-colors block text-xs"
                  >
                    <div>
                      <div className="font-medium text-charcoal-900">{res.title}</div>
                      <div className="text-[10px] font-mono text-charcoal-500 mt-0.5">
                        {res.platform} • {res.duration} • {res.type}
                      </div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-charcoal-400" />
                  </a>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-paper-border flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedStep(null)}
                className="px-4 py-1.5 bg-charcoal-900 hover:bg-black text-white text-xs font-medium rounded-sm"
              >
                Close Details
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
