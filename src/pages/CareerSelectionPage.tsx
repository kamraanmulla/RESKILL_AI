import React, { useState } from 'react';
import {
  Compass,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Target,
  SlidersHorizontal,
  Loader2
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { Modal } from '../components/common/Modal';
import { CareerRole } from '../types';

interface CareerSelectionPageProps {
  careers: CareerRole[];
  selectedCareerId: string;
  onSelectCareer: (careerId: string) => void;
  onViewCareerMatch: () => void;
}

export const CareerSelectionPage: React.FC<CareerSelectionPageProps> = ({
  careers,
  selectedCareerId,
  onSelectCareer,
  onViewCareerMatch
}) => {
  const [filterCategory, setFilterCategory] = useState('All');
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [suggestionModalOpen, setSuggestionModalOpen] = useState(false);
  const [suggestedCareer, setSuggestedCareer] = useState<CareerRole | null>(null);

  const categories = ['All', 'Software Engineering', 'Data & Analytics', 'Artificial Intelligence', 'Cloud & Infrastructure', 'Information Security'];

  const filteredCareers = filterCategory === 'All'
    ? careers
    : careers.filter((c) => c.category === filterCategory);

  const handleSuggestCareer = () => {
    setIsSuggesting(true);
    setTimeout(() => {
      const bestCareer = careers.find((c) => c.id === 'career_fullstack') || careers[0];
      setSuggestedCareer(bestCareer);
      setIsSuggesting(false);
      setSuggestionModalOpen(true);
    }, 600);
  };

  const handleAcceptSuggestion = (careerId: string) => {
    onSelectCareer(careerId);
    setSuggestionModalOpen(false);
    onViewCareerMatch();
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Where do you want to go?"
        subtitle="Choose a target role to benchmark your current skills and generate your custom learning path."
        badge="Career Trajectories"
      />

      {/* "Not Sure Yet" Recommendation Banner */}
      <div className="p-5 sm:p-6 bg-forest-50 border border-forest-200 rounded-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-subtle">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-sm bg-forest-800 text-white flex items-center justify-center shrink-0 shadow-subtle">
            <Sparkles className="w-5 h-5 text-forest-100" />
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-forest-800 font-semibold">
              Not sure yet?
            </div>
            <h3 className="font-serif text-lg font-medium text-charcoal-900 mt-0.5">
              Let the system evaluate your current skill profile
            </h3>
            <p className="text-xs text-charcoal-600 mt-0.5 max-w-xl">
              Our career compatibility engine benchmarks your verified skills against 7 core engineering specializations to recommend your highest-velocity trajectory.
            </p>
          </div>
        </div>

        <button
          onClick={handleSuggestCareer}
          disabled={isSuggesting}
          className="shrink-0 px-4 py-2.5 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center gap-2"
        >
          {isSuggesting ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing Trajectories...</span>
            </>
          ) : (
            <>
              <Compass className="w-3.5 h-3.5" />
              <span>Suggest a career for me</span>
            </>
          )}
        </button>
      </div>

      {/* Filter Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-paper-border text-xs">
        <SlidersHorizontal className="w-3.5 h-3.5 text-charcoal-400 shrink-0 mr-1" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-3 py-1.5 rounded-sm whitespace-nowrap transition-colors ${
              filterCategory === cat
                ? 'bg-charcoal-900 text-white font-medium'
                : 'text-charcoal-600 hover:bg-paper-muted hover:text-charcoal-900'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Career Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredCareers.map((career) => {
          const isSelected = career.id === selectedCareerId;
          return (
            <div
              key={career.id}
              className={`bg-white border rounded-md p-5 flex flex-col justify-between transition-all duration-150 relative ${
                isSelected
                  ? 'border-forest-800 ring-1 ring-forest-800 shadow-card bg-forest-50/20'
                  : 'border-paper-border hover:border-charcoal-400 hover:shadow-subtle'
              }`}
            >
              {isSelected && (
                <div className="absolute top-3 right-3 flex items-center gap-1 text-[10px] font-mono bg-forest-800 text-white px-2 py-0.5 rounded-sm shadow-subtle">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Target Selected</span>
                </div>
              )}

              <div>
                <div className="text-[10px] font-mono uppercase tracking-widest text-charcoal-500 mb-1">
                  {career.category}
                </div>

                <h3 className="font-serif text-lg font-medium text-charcoal-900 mb-1.5">
                  {career.title}
                </h3>

                <p className="text-xs text-charcoal-600 line-clamp-3 leading-relaxed mb-4">
                  {career.description}
                </p>

                {/* Compatibility and Experience level metrics */}
                <div className="flex items-center justify-between p-2.5 bg-paper rounded-sm border border-paper-border mb-4 font-mono text-xs">
                  <div>
                    <span className="text-[10px] text-charcoal-500 uppercase block">Compatibility</span>
                    <span className={`font-semibold ${career.currentMatchPercentage >= 75 ? 'text-forest-800' : 'text-charcoal-800'}`}>
                      {career.currentMatchPercentage}% Match
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-charcoal-500 uppercase block">Experience</span>
                    <span className="text-charcoal-800">{career.experienceLevel}</span>
                  </div>
                </div>

                {/* Core required skills tags */}
                <div className="space-y-1.5 mb-5">
                  <div className="text-[10px] uppercase font-mono tracking-wider text-charcoal-500">
                    Core Competencies
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {career.coreSkills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 text-[10px] font-mono rounded bg-paper text-charcoal-700 border border-paper-border"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-paper-border flex items-center justify-between gap-2">
                {isSelected ? (
                  <button
                    onClick={onViewCareerMatch}
                    className="w-full py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Target className="w-3.5 h-3.5" />
                    <span>View Match Dashboard</span>
                  </button>
                ) : (
                  <button
                    onClick={() => onSelectCareer(career.id)}
                    className="w-full py-2 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-800 hover:text-charcoal-900 text-xs font-medium rounded-sm transition-colors flex items-center justify-center gap-1"
                  >
                    <span>Set as Target Role</span>
                    <ArrowRight className="w-3 h-3 text-charcoal-400" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Suggestion Modal */}
      <Modal
        isOpen={suggestionModalOpen}
        onClose={() => setSuggestionModalOpen(false)}
        title="Career Recommendation"
        subtitle="Calculated from your verified skill profile and current market demand."
        maxWidth="md"
      >
        {suggestedCareer && (
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-forest-50 border border-forest-200 rounded-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-wider text-forest-800 font-semibold">
                  Recommended Career Trajectory
                </span>
                <span className="font-mono font-bold text-forest-900 text-sm">
                  {suggestedCareer.currentMatchPercentage}% Match
                </span>
              </div>
              <div className="font-serif text-xl font-medium text-charcoal-900">
                {suggestedCareer.title}
              </div>
              <p className="text-charcoal-700 leading-relaxed text-xs">
                Your strong performance in JavaScript (85%) and React (80%), coupled with your academic projects (CampusTrade MERN app), gives you the fastest ramp into <strong>Full Stack Engineering</strong>.
              </p>
            </div>

            <div className="space-y-2">
              <div className="font-medium text-charcoal-900">Recommended Next Steps:</div>
              <ul className="list-disc list-inside space-y-1 text-charcoal-600 font-mono text-[11px]">
                <li>Benchmark current Node.js and REST API knowledge.</li>
                <li>Close the 35% gap on containerization with Docker.</li>
                <li>Follow the 9-step Full Stack timeline roadmap.</li>
              </ul>
            </div>

            <div className="pt-4 border-t border-paper-border flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setSuggestionModalOpen(false)}
                className="px-3 py-1.5 border border-paper-border text-charcoal-600 rounded-sm hover:bg-paper-dark"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => handleAcceptSuggestion(suggestedCareer.id)}
                className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 text-white font-medium rounded-sm shadow-subtle flex items-center gap-1.5"
              >
                <span>Select Full Stack Developer</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
