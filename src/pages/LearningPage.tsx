import React, { useState } from 'react';
import {
  Play,
  Bookmark,
  ExternalLink,
  Clock,
  Video,
  FileText,
  CheckCircle2,
  SlidersHorizontal
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { Modal } from '../components/common/Modal';
import { LearningResource } from '../types';

interface LearningPageProps {
  resources: LearningResource[];
  initialFilterSkill?: string;
  onToggleSave: (id: string) => void;
}

export const LearningPage: React.FC<LearningPageProps> = ({
  resources,
  initialFilterSkill,
  onToggleSave
}) => {
  const [selectedSkill, setSelectedSkill] = useState(initialFilterSkill || 'All');
  const [selectedFormat, setSelectedFormat] = useState('All');
  const [activePlayerResource, setActivePlayerResource] = useState<LearningResource | null>(null);

  const skillFilters = ['All', 'Node.js', 'REST APIs', 'Docker', 'MongoDB', 'Authentication', 'Testing', 'Backend'];
  const formatFilters = ['All', 'YouTube', 'Documentation'];

  const filteredResources = resources.filter((res) => {
    const matchSkill = selectedSkill === 'All' || res.skillTag.toLowerCase() === selectedSkill.toLowerCase();
    const matchFormat = selectedFormat === 'All' || res.platform.toLowerCase() === selectedFormat.toLowerCase();
    return matchSkill && matchFormat;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Recommended Learning"
        subtitle="Curated, peer-reviewed technical tutorials and reference literature aligned with your roadmap gaps."
        badge="Curated Repository"
        action={
          <span className="font-mono text-xs text-charcoal-500">
            {filteredResources.length} Modules Available
          </span>
        }
      />

      {/* Editorial Filter Bar */}
      <div className="bg-white border border-paper-border rounded-md p-4 space-y-3">
        <div className="flex items-center justify-between text-xs text-charcoal-500 font-mono">
          <span className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-charcoal-400" />
            <span>Filter by Target Skill:</span>
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {skillFilters.map((skill) => (
            <button
              key={skill}
              onClick={() => setSelectedSkill(skill)}
              className={`px-3 py-1 text-xs rounded-sm transition-colors ${
                selectedSkill === skill
                  ? 'bg-forest-800 text-white font-medium shadow-subtle'
                  : 'bg-paper hover:bg-paper-muted text-charcoal-700 border border-paper-border'
              }`}
            >
              {skill}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 pt-2 border-t border-paper-border text-xs text-charcoal-500 font-mono">
          <span>Format:</span>
          {formatFilters.map((fmt) => (
            <button
              key={fmt}
              onClick={() => setSelectedFormat(fmt)}
              className={`px-2 py-0.5 rounded text-[11px] transition-colors ${
                selectedFormat === fmt
                  ? 'bg-charcoal-800 text-white font-medium'
                  : 'hover:text-charcoal-900'
              }`}
            >
              {fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Curated Library Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredResources.map((res) => {
          const isVideo = res.platform === 'YouTube';
          return (
            <div
              key={res.id}
              className="bg-white border border-paper-border hover:border-charcoal-400 rounded-md p-5 flex flex-col justify-between transition-all duration-150 group shadow-subtle"
            >
              <div>
                {/* Meta header */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono rounded-sm border ${
                        isVideo
                          ? 'bg-red-50 text-red-800 border-red-200'
                          : 'bg-paper-muted text-charcoal-700 border-paper-border'
                      }`}
                    >
                      {isVideo ? <Video className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
                      <span>{res.platform}</span>
                    </span>

                    <span className="px-1.5 py-0.5 text-[10px] font-mono bg-forest-50 text-forest-800 border border-forest-200 rounded-sm">
                      {res.skillTag}
                    </span>
                  </div>

                  <button
                    onClick={() => onToggleSave(res.id)}
                    className={`p-1 rounded transition-colors ${
                      res.isSaved
                        ? 'text-forest-800'
                        : 'text-charcoal-400 hover:text-charcoal-700'
                    }`}
                    title={res.isSaved ? 'Remove from Saved' : 'Save to Study List'}
                  >
                    <Bookmark
                      className="w-4 h-4"
                      fill={res.isSaved ? 'currentColor' : 'none'}
                    />
                  </button>
                </div>

                {/* Title */}
                <h3 className="font-serif text-lg font-medium text-charcoal-900 group-hover:text-forest-900 leading-snug mb-2">
                  {res.title}
                </h3>

                {/* Metadata */}
                <div className="flex items-center gap-4 text-xs text-charcoal-500 font-mono mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-charcoal-400" />
                    {res.duration}
                  </span>
                  <span>•</span>
                  <span>Level: {res.level}</span>
                  <span>•</span>
                  <span>By {res.instructor}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-paper-border flex items-center justify-between">
                <button
                  onClick={() => setActivePlayerResource(res)}
                  className="px-3 py-1.5 bg-paper-muted hover:bg-forest-100 text-charcoal-900 hover:text-forest-900 text-xs font-medium rounded-sm border border-paper-border transition-colors flex items-center gap-1.5"
                >
                  <Play className="w-3.5 h-3.5 text-forest-800" />
                  <span>Watch in Platform</span>
                </button>

                <a
                  href={res.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-charcoal-500 hover:text-charcoal-900 flex items-center gap-1 font-mono hover:underline"
                >
                  <span>Open External</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          );
        })}
      </div>

      {/* Simulated Video Viewer Modal */}
      {activePlayerResource && (
        <Modal
          isOpen={!!activePlayerResource}
          onClose={() => setActivePlayerResource(null)}
          title={activePlayerResource.title}
          subtitle={`Instructor: ${activePlayerResource.instructor} • ${activePlayerResource.duration} • ${activePlayerResource.level}`}
          maxWidth="2xl"
        >
          <div className="space-y-4">
            {/* Mock Player Screen */}
            <div className="w-full aspect-video bg-charcoal-900 rounded-sm flex flex-col items-center justify-center text-white relative overflow-hidden border border-paper-border">
              <div className="text-center p-6 space-y-3">
                <div className="w-14 h-14 mx-auto rounded-full bg-forest-800/80 border border-forest-600 flex items-center justify-center text-white shadow-card">
                  <Play className="w-6 h-6 ml-1" />
                </div>
                <div className="font-serif text-lg font-medium">
                  {activePlayerResource.title}
                </div>
                <p className="text-xs text-charcoal-300 font-mono">
                  {activePlayerResource.platform} Stream Ready • Duration: {activePlayerResource.duration}
                </p>
              </div>

              <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between text-xs text-charcoal-300 font-mono">
                <span>00:00 / {activePlayerResource.duration}</span>
                <span>1080p HD</span>
              </div>
            </div>

            {/* Study Notes & Links */}
            <div className="p-4 bg-paper rounded-sm border border-paper-border text-xs space-y-2">
              <div className="font-semibold text-charcoal-900 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" />
                <span>Learning Objectives</span>
              </div>
              <p className="text-charcoal-600 leading-relaxed">
                Focus on the modular design patterns and real-world edge cases covered in this resource. Take notes on how these concepts integrate directly with your Roadmap practice project.
              </p>
              <div className="pt-2 flex justify-between items-center text-[11px] font-mono">
                <span className="text-charcoal-500">Skill Tag: {activePlayerResource.skillTag}</span>
                <a
                  href={activePlayerResource.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-forest-800 hover:underline flex items-center gap-1"
                >
                  <span>Open on {activePlayerResource.platform}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
