import React, { useState } from 'react';
import {
  Briefcase,
  Bookmark,
  Building,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  Info,
  ExternalLink,
  SlidersHorizontal,
  Send
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { Modal } from '../components/common/Modal';
import { JobOpportunity } from '../types';

interface JobsPageProps {
  jobs: JobOpportunity[];
  onToggleSave: (id: string) => void;
}

export const JobsPage: React.FC<JobsPageProps> = ({
  jobs,
  onToggleSave
}) => {
  const [workModeFilter, setWorkModeFilter] = useState<'All' | 'Remote' | 'Hybrid' | 'On-site'>('All');
  const [selectedJob, setSelectedJob] = useState<JobOpportunity | null>(null);
  const [appliedJobs, setAppliedJobs] = useState<Record<string, boolean>>({});

  const filteredJobs = workModeFilter === 'All'
    ? jobs
    : jobs.filter((j) => j.workMode === workModeFilter);

  const handleApply = (jobId: string) => {
    setAppliedJobs({ ...appliedJobs, [jobId]: true });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Opportunities for you"
        subtitle="Curated junior roles and campus internships matched against your current technical capability profile."
        badge="Opportunity Portal"
        action={
          <span className="font-mono text-xs text-charcoal-500">
            {filteredJobs.length} Matched Positions
          </span>
        }
      />

      {/* Mandatory Note Callout */}
      <div className="p-4 bg-paper rounded-sm border border-paper-border flex items-start gap-3 text-xs text-charcoal-600">
        <Info className="w-4 h-4 text-forest-800 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-charcoal-900 font-semibold">Algorithmic Matching:</strong> Job recommendations will be personalized using your profile and skill progress. As you complete roadmap modules, your compatibility score across listings will update in real time.
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 pb-1 border-b border-paper-border text-xs">
        <SlidersHorizontal className="w-3.5 h-3.5 text-charcoal-400 mr-1" />
        <span className="text-charcoal-500 font-mono">Work Mode:</span>
        {(['All', 'Remote', 'Hybrid', 'On-site'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setWorkModeFilter(mode)}
            className={`px-3 py-1 rounded-sm transition-colors ${
              workModeFilter === mode
                ? 'bg-charcoal-900 text-white font-medium'
                : 'text-charcoal-600 hover:bg-paper-muted'
            }`}
          >
            {mode}
          </button>
        ))}
      </div>

      {/* Job Cards List */}
      <div className="space-y-4">
        {filteredJobs.map((job) => {
          const isHighMatch = job.matchPercentage >= 85;
          const isApplied = appliedJobs[job.id];

          return (
            <div
              key={job.id}
              className="bg-white border border-paper-border hover:border-charcoal-400 rounded-md p-5 sm:p-6 transition-all duration-150 space-y-4 shadow-subtle"
            >
              {/* Header: Title, Company, Match % */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      {job.title}
                    </h3>
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-paper-muted text-charcoal-600 border border-paper-border">
                      {job.type}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-charcoal-500 font-mono mt-1.5">
                    <span className="flex items-center gap-1 font-sans font-semibold text-charcoal-800">
                      <Building className="w-3.5 h-3.5 text-charcoal-400" />
                      {job.company}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-charcoal-400" />
                      {job.location} ({job.workMode})
                    </span>
                    <span>•</span>
                    <span>{job.compensation}</span>
                    <span>•</span>
                    <span className="text-charcoal-400">Posted {job.postedAgo}</span>
                  </div>
                </div>

                {/* Match Percentage Pill */}
                <div className="flex items-center gap-2 self-start">
                  <div
                    className={`px-3 py-1 rounded-sm border font-mono text-xs font-semibold flex items-center gap-1.5 ${
                      isHighMatch
                        ? 'bg-forest-100 text-forest-900 border-forest-200'
                        : 'bg-paper-muted text-charcoal-800 border-paper-border'
                    }`}
                  >
                    <span>Match: {job.matchPercentage}%</span>
                  </div>

                  <button
                    onClick={() => onToggleSave(job.id)}
                    className={`p-1.5 rounded border border-paper-border hover:bg-paper-muted transition-colors ${
                      job.isSaved ? 'text-forest-800 bg-forest-50' : 'text-charcoal-400'
                    }`}
                    title={job.isSaved ? 'Saved' : 'Save Opportunity'}
                  >
                    <Bookmark className="w-4 h-4" fill={job.isSaved ? 'currentColor' : 'none'} />
                  </button>
                </div>
              </div>

              {/* Matched vs Missing Skills */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-paper-border text-xs">
                {/* Matched Skills */}
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] font-mono uppercase text-forest-800 font-semibold mr-1 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-forest-700" /> Matched:
                  </span>
                  {job.matchedSkills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 text-[10px] font-mono rounded bg-forest-50 text-forest-900 border border-forest-200"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                {/* Missing Skills */}
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] font-mono uppercase text-editorial-rust font-semibold mr-1 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3 text-editorial-rust" /> Missing:
                  </span>
                  {job.missingSkills.length > 0 ? (
                    job.missingSkills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 text-[10px] font-mono rounded bg-editorial-rustLight text-editorial-rust border border-orange-200"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-[10px] font-mono text-charcoal-500">None</span>
                  )}
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="pt-2 flex items-center justify-between">
                <p className="text-xs text-charcoal-500 line-clamp-1 max-w-xl">
                  {job.description}
                </p>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => onToggleSave(job.id)}
                    className="px-3 py-1.5 text-xs text-charcoal-700 hover:text-charcoal-900 border border-paper-border hover:bg-paper-muted rounded-sm transition-colors"
                  >
                    {job.isSaved ? 'Saved' : 'Save'}
                  </button>

                  <button
                    onClick={() => setSelectedJob(job)}
                    className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1.5"
                  >
                    <span>View Opportunity</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Opportunity Detail Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
          title={selectedJob.title}
          subtitle={`${selectedJob.company} • ${selectedJob.location} (${selectedJob.workMode})`}
          maxWidth="xl"
        >
          <div className="space-y-4 text-xs">
            {/* Header info strip */}
            <div className="p-3 bg-paper rounded-sm border border-paper-border flex items-center justify-between font-mono">
              <div>
                <span className="text-charcoal-500">Compensation: </span>
                <strong className="text-charcoal-900">{selectedJob.compensation}</strong>
              </div>
              <div className="text-forest-800 font-semibold">
                Match Score: {selectedJob.matchPercentage}%
              </div>
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <h4 className="font-serif text-sm font-semibold text-charcoal-900">
                Role Overview
              </h4>
              <p className="text-charcoal-600 leading-relaxed">
                {selectedJob.description}
              </p>
            </div>

            {/* Responsibilities */}
            <div className="space-y-1.5">
              <h4 className="font-serif text-sm font-semibold text-charcoal-900">
                Key Responsibilities
              </h4>
              <ul className="list-disc list-inside space-y-1 text-charcoal-600">
                {selectedJob.responsibilities.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>

            {/* Qualifications */}
            <div className="space-y-1.5">
              <h4 className="font-serif text-sm font-semibold text-charcoal-900">
                Candidate Qualifications
              </h4>
              <ul className="list-disc list-inside space-y-1 text-charcoal-600">
                {selectedJob.qualifications.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>

            {/* Application Action */}
            <div className="pt-4 border-t border-paper-border flex items-center justify-between">
              <span className="text-[11px] text-charcoal-500 font-mono">
                Direct college referral pipeline active
              </span>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedJob(null)}
                  className="px-3 py-1.5 border border-paper-border text-charcoal-600 rounded-sm hover:bg-paper-dark"
                >
                  Close
                </button>

                <button
                  type="button"
                  onClick={() => handleApply(selectedJob.id)}
                  disabled={appliedJobs[selectedJob.id]}
                  className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 disabled:opacity-75 text-white font-medium rounded-sm shadow-subtle flex items-center gap-1.5"
                >
                  {appliedJobs[selectedJob.id] ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Application Logged</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Submit Profile</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
