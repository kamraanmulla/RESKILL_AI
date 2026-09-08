import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  X,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { SkillBar } from '../components/common/SkillBar';
import { StudentProfile } from '../types';

interface ResumeUploadPageProps {
  student: StudentProfile;
  onUploadSuccess: (fileInfo: { name: string; size: string; uploadedAt: string }) => void;
  onContinueToProfile: () => void;
}

export const ResumeUploadPage: React.FC<ResumeUploadPageProps> = ({
  student,
  onUploadSuccess,
  onContinueToProfile
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [currentFile, setCurrentFile] = useState<{
    name: string;
    size: string;
    uploadedAt: string;
  } | null>(student.resumeFile);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showDetectedPreview, setShowDetectedPreview] = useState(!!student.resumeFile);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const processMockFile = (name: string, sizeBytes: number) => {
    setIsProcessing(true);
    const sizeStr = `${(sizeBytes / 1024).toFixed(0)} KB`;

    setTimeout(() => {
      const fileData = {
        name,
        size: sizeStr === '0 KB' ? '248 KB' : sizeStr,
        uploadedAt: 'Just now'
      };
      setCurrentFile(fileData);
      setIsProcessing(false);
      setShowDetectedPreview(true);
      onUploadSuccess(fileData);
    }, 700);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processMockFile(file.name, file.size);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processMockFile(file.name, file.size);
    }
  };

  const handleRemoveFile = () => {
    setCurrentFile(null);
    setShowDetectedPreview(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleLoadSample = () => {
    processMockFile('Parvez_Ahmed_CSE_Resume_2026.pdf', 254000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <SectionHeader
        title="Start with your resume"
        subtitle="Upload your resume and we'll build your initial skill profile."
        badge="Resume Ingestion"
      />

      {/* Main Upload Box */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={handleFileInput}
        />

        {!currentFile && !isProcessing && (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-md p-8 sm:p-12 text-center transition-all ${
              dragActive
                ? 'border-forest-800 bg-forest-50/50'
                : 'border-paper-border hover:border-charcoal-400 bg-paper/40'
            }`}
          >
            <div className="w-12 h-12 mx-auto rounded-sm bg-paper-muted flex items-center justify-center text-charcoal-700 mb-4 border border-paper-border">
              <UploadCloud className="w-6 h-6 text-forest-800" />
            </div>

            <h3 className="font-serif text-lg font-medium text-charcoal-900 mb-1">
              Drag and drop your resume here
            </h3>
            <p className="text-xs text-charcoal-500 mb-5 font-mono">
              Supported formats: PDF, DOCX (Max size: 10MB)
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-5 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors"
              >
                Browse files
              </button>

              <button
                type="button"
                onClick={handleLoadSample}
                className="px-4 py-2 bg-white hover:bg-paper-muted border border-paper-border text-charcoal-700 text-xs font-medium rounded-sm transition-colors flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-forest-700" />
                <span>Load Sample Student Resume</span>
              </button>
            </div>
          </div>
        )}

        {/* Processing State */}
        {isProcessing && (
          <div className="py-12 text-center space-y-3">
            <Loader2 className="w-8 h-8 mx-auto text-forest-800 animate-spin" />
            <div className="font-serif text-base font-medium text-charcoal-900">
              Analyzing resume structure & extracting skills...
            </div>
            <p className="text-xs text-charcoal-500 font-mono">
              Identifying coursework, projects, internships, and technical competencies...
            </p>
          </div>
        )}

        {/* Uploaded File Preview */}
        {currentFile && !isProcessing && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-paper border border-paper-border rounded-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-sm bg-forest-100 border border-forest-200 flex items-center justify-center text-forest-900">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-charcoal-900 flex items-center gap-2">
                    <span>{currentFile.name}</span>
                    <span className="text-[10px] font-mono font-normal text-forest-700 bg-forest-50 px-1.5 py-0.2 rounded border border-forest-200">
                      Parsed
                    </span>
                  </div>
                  <div className="text-[11px] text-charcoal-500 font-mono mt-0.5">
                    {currentFile.size} • Uploaded {currentFile.uploadedAt}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="p-1.5 text-charcoal-400 hover:text-editorial-rust rounded-sm transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="text-xs text-charcoal-500 flex items-center gap-1.5 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" />
                <span>14 skills extracted across Frontend, Backend & Database</span>
              </div>

              <button
                type="button"
                onClick={onContinueToProfile}
                className="px-5 py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center gap-2"
              >
                <span>Continue to Student Profile</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        <div className="p-3 bg-paper-muted border border-paper-border rounded-sm flex items-start gap-2.5 text-xs text-charcoal-600">
          <AlertCircle className="w-4 h-4 text-charcoal-500 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong>Frontend Mock Mode:</strong> In this phase, the resume is indexed via mock data simulating our ML entity extractor. No external files leave your browser.
          </p>
        </div>
      </div>

      {/* Initial Skills Detected Preview */}
      {showDetectedPreview && (
        <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6 animate-in fade-in">
          <div className="flex items-center justify-between pb-3 border-b border-paper-border">
            <div>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Skills Detected From Profile
              </h3>
              <p className="text-xs text-charcoal-500">
                Initial proficiency estimated from academic projects and coursework keywords.
              </p>
            </div>
            <span className="text-xs font-mono text-charcoal-500">
              Student: {student.name}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {student.skills.slice(0, 8).map((skill) => (
              <SkillBar
                key={skill.name}
                name={skill.name}
                percentage={skill.proficiency}
                level={skill.level}
                verified={skill.verified}
              />
            ))}
          </div>

          <div className="pt-4 border-t border-paper-border flex justify-end">
            <button
              onClick={onContinueToProfile}
              className="px-4 py-2 bg-charcoal-900 hover:bg-black text-white text-xs font-medium rounded-sm transition-colors flex items-center gap-1.5"
            >
              <span>View Full Skill Breakdown</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
