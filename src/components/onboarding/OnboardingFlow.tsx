import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Upload,
  CheckCircle2,
  Plus,
  X,
  HelpCircle,
  GraduationCap,
  Layers,
  Compass,
  Code2,
  Terminal,
  ShieldCheck,
  Check
} from 'lucide-react';
import { MinimalOnboardingRequest, StudentProfile } from '../../types';
import { api } from '../../services/api';

interface OnboardingFlowProps {
  userName?: string;
  isOpen: boolean;
  initialStage?: 'fork' | 'upload' | 'questions';
  onClose: () => void;
  onComplete: (profile: StudentProfile) => void;
}

const DEFAULT_SKILL_OPTIONS = [
  'Python',
  'Java',
  'JavaScript',
  'C++',
  'React',
  'Node.js',
  'SQL',
  'Linux',
  'Networking',
  'Cybersecurity',
  'Cloud',
  'Git',
  'Figma',
  'Excel',
  'Machine Learning',
  'Data Analysis'
];

const INTEREST_OPTIONS = [
  'Cybersecurity',
  'AI / Machine Learning',
  'Software Development',
  'Data Science',
  'Cloud / DevOps',
  'Networking',
  'UI / UX',
  'Mobile Development',
  'Product / Technology',
  'Other'
];

const CAREER_OPTIONS = [
  'Cybersecurity',
  'Software Engineering',
  'AI / ML',
  'Data Science',
  'Cloud / DevOps',
  'Networking',
  'UI / UX',
  'Other',
  "I'm not sure yet"
];

const EDUCATION_OPTIONS = [
  'B.E. Computer Science',
  'B.Tech IT',
  'BCA',
  'MCA',
  'Diploma in Computer Engineering',
  '12th / Higher Secondary',
  'Other'
];

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({
  userName = 'Candidate',
  isOpen,
  initialStage = 'fork',
  onClose,
  onComplete
}) => {
  // Mode: 'fork' (Resume vs No-Resume), 'upload' (Resume flow), 'questions' (5 Core questions)
  const [stage, setStage] = useState<'fork' | 'upload' | 'questions'>(initialStage);
  const [questionIndex, setQuestionIndex] = useState<number>(0);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Sync initialStage whenever modal opens
  React.useEffect(() => {
    if (isOpen) {
      setStage(initialStage);
      setQuestionIndex(0);
    }
  }, [isOpen, initialStage]);

  // Resume Upload State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // 5 Core Questions State
  const [education, setEducation] = useState<string>('B.E. Computer Science');
  const [customEducation, setCustomEducation] = useState<string>('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>(['Python', 'Git']);
  const [customSkillInput, setCustomSkillInput] = useState<string>('');
  const [selectedInterests, setSelectedInterests] = useState<string[]>(['Software Development']);
  const [careerDirection, setCareerDirection] = useState<string>("I'm not sure yet");
  const [practicalExperience, setPracticalExperience] = useState<string>('');

  if (!isOpen) return null;

  // Toggle skills
  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const handleAddCustomSkill = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    const trimmed = customSkillInput.trim();
    if (trimmed && !selectedSkills.includes(trimmed)) {
      setSelectedSkills((prev) => [...prev, trimmed]);
      setCustomSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setSelectedSkills((prev) => prev.filter((s) => s !== skill));
  };

  // Toggle interests
  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  };

  // Handle Resume Upload & Ingestion
  const handleResumeSubmit = async () => {
    if (!selectedFile) {
      setUploadError('Please choose a PDF or DOCX file.');
      return;
    }
    setSubmitting(true);
    setUploadError(null);
    try {
      // Direct ingestion via backend
      const result = await api.uploadResume(selectedFile);
      onComplete(result.student);
    } catch (err: any) {
      setUploadError(err?.message || 'Resume parsing encountered an error. Please try again or use the 5 questions.');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle 5 Questions Submission
  const handleQuestionsSubmit = async () => {
    setSubmitting(true);
    try {
      const finalEducation = education === 'Other' && customEducation ? customEducation : education;
      const requestPayload: MinimalOnboardingRequest = {
        name: userName,
        education: finalEducation,
        degree: finalEducation,
        skills: selectedSkills,
        interests: selectedInterests,
        careerDirection: careerDirection,
        practicalExperienceText: practicalExperience || "I haven't worked on anything yet"
      };

      const profile = await api.submitMinimalOnboarding(requestPayload);
      onComplete(profile);
    } catch (err) {
      console.error('Error submitting onboarding:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-paper border border-paper-border rounded-lg shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="px-6 py-5 border-b border-paper-border bg-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="w-7 h-7 rounded bg-forest-800 text-white flex items-center justify-center font-serif text-sm font-bold">
              R
            </span>
            <div>
              <h3 className="font-serif text-lg font-medium text-charcoal-900 leading-tight">
                Profile Calibration
              </h3>
              <p className="text-[11px] font-mono text-charcoal-500">
                Ask less. Understand more.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-charcoal-400 hover:text-charcoal-700 hover:bg-paper-muted rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 text-charcoal-800">
          {/* STAGE 0: FORK (Do you have a resume?) */}
          {stage === 'fork' && (
            <div className="space-y-6 py-2">
              <div className="text-center max-w-md mx-auto space-y-2">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-forest-50 text-forest-800 border border-forest-200">
                  Initial Dossier Setup
                </span>
                <h2 className="font-serif text-2xl font-medium text-charcoal-900">
                  Do you have a resume?
                </h2>
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  Both options lead to the same high-precision Career Intelligence. Choose whatever feels easiest right now.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                {/* Option A: I have a resume */}
                <button
                  type="button"
                  onClick={() => setStage('upload')}
                  className="p-5 text-left bg-white border border-paper-border hover:border-forest-800 hover:shadow-subtle rounded-md transition-all group flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded bg-forest-50 text-forest-800 flex items-center justify-center group-hover:bg-forest-800 group-hover:text-white transition-colors">
                      <FileText className="w-5 h-5" />
                    </div>
                    <h3 className="font-serif text-lg font-medium text-charcoal-900">
                      I have a resume
                    </h3>
                    <p className="text-xs text-charcoal-500 leading-relaxed">
                      Upload your existing PDF. Our Gemini layer will extract your education, skills, and projects in one step.
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs font-mono text-forest-800 font-medium pt-2 border-t border-paper-border">
                    <span>Upload Resume</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </button>

                {/* Option B: I don't have a resume */}
                <button
                  type="button"
                  onClick={() => setStage('questions')}
                  className="p-5 text-left bg-white border border-paper-border hover:border-forest-800 hover:shadow-subtle rounded-md transition-all group flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded bg-amber-50 text-amber-900 flex items-center justify-center group-hover:bg-charcoal-900 group-hover:text-white transition-colors">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <h3 className="font-serif text-lg font-medium text-charcoal-900">
                      I don't have a resume
                    </h3>
                    <p className="text-xs text-charcoal-500 leading-relaxed">
                      Smart Minimal Onboarding: answer 5 focused questions in under 2 minutes. No forms, no credentials required.
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs font-mono text-charcoal-800 font-medium pt-2 border-t border-paper-border">
                    <span>Answer 5 Quick Questions</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* STAGE: RESUME UPLOAD */}
          {stage === 'upload' && (
            <div className="space-y-5 py-2">
              <button
                type="button"
                onClick={() => setStage('fork')}
                className="flex items-center gap-1 text-xs font-mono text-charcoal-500 hover:text-charcoal-800 transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back to choices
              </button>

              <div>
                <h3 className="font-serif text-xl font-medium text-charcoal-900">
                  Upload your resume
                </h3>
                <p className="text-xs text-charcoal-500 mt-1">
                  Gemini extracts your verified skills once and reuses them across career matching and roadmaps.
                </p>
              </div>

              <div className="border-2 border-dashed border-paper-border hover:border-forest-800 bg-white rounded-lg p-8 text-center transition-colors">
                <input
                  type="file"
                  id="resume-file-input"
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setSelectedFile(e.target.files[0]);
                      setUploadError(null);
                    }
                  }}
                />
                <label
                  htmlFor="resume-file-input"
                  className="cursor-pointer flex flex-col items-center space-y-3"
                >
                  <div className="w-12 h-12 rounded-full bg-forest-50 text-forest-800 flex items-center justify-center">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-forest-800 hover:underline">
                      Click to choose a file
                    </span>
                    <span className="text-xs text-charcoal-500"> or drag and drop here</span>
                  </div>
                  <p className="text-[11px] font-mono text-charcoal-400">
                    PDF, DOCX up to 10 MB
                  </p>
                </label>

                {selectedFile && (
                  <div className="mt-4 p-3 bg-paper rounded border border-paper-border flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="w-4 h-4 text-forest-800 shrink-0" />
                      <span className="font-medium text-charcoal-800 truncate">{selectedFile.name}</span>
                      <span className="text-charcoal-400 font-mono">({(selectedFile.size / 1024).toFixed(0)} KB)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="text-charcoal-400 hover:text-editorial-rust p-1"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>

              {uploadError && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded">
                  {uploadError}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setStage('questions')}
                  className="text-xs font-mono text-charcoal-500 hover:text-charcoal-800"
                >
                  I'd rather answer 5 questions
                </button>
                <button
                  type="button"
                  disabled={!selectedFile || submitting}
                  onClick={handleResumeSubmit}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-2"
                >
                  {submitting ? 'Analyzing with Gemini...' : 'Analyze Resume'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* STAGE: 5 CORE QUESTIONS */}
          {stage === 'questions' && (
            <div className="space-y-6">
              {/* Progress pill & Back button */}
              <div className="flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => {
                    if (questionIndex === 0) setStage('fork');
                    else setQuestionIndex((prev) => prev - 1);
                  }}
                  className="flex items-center gap-1 text-xs font-mono text-charcoal-500 hover:text-charcoal-800 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> {questionIndex === 0 ? 'Back to choices' : 'Previous'}
                </button>

                <div className="flex items-center gap-1.5 font-mono text-xs text-charcoal-500">
                  <span>Question {questionIndex + 1} of 5</span>
                  <div className="flex gap-1 ml-2">
                    {[0, 1, 2, 3, 4].map((idx) => (
                      <div
                        key={idx}
                        className={`w-4 h-1 rounded-full transition-colors ${
                          idx === questionIndex
                            ? 'bg-forest-800'
                            : idx < questionIndex
                            ? 'bg-forest-300'
                            : 'bg-paper-border'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* QUESTION 1: EDUCATION */}
              {questionIndex === 0 && (
                <div className="space-y-4 animate-fade-in">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono uppercase text-forest-800 font-semibold tracking-wider">
                      Signal 01 • Academic Foundation
                    </span>
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      What are you currently studying or what is your highest level of education?
                    </h3>
                    <p className="text-xs text-charcoal-500">
                      Select your current academic path. We extract your degree, field, and level from this single response.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                    {EDUCATION_OPTIONS.map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => setEducation(opt)}
                        className={`p-3 text-left rounded border text-xs font-medium transition-all ${
                          education === opt
                            ? 'border-forest-800 bg-forest-50 text-forest-900 shadow-sm'
                            : 'border-paper-border bg-white text-charcoal-700 hover:border-charcoal-400'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span>{opt}</span>
                          {education === opt && <Check className="w-3.5 h-3.5 text-forest-800" />}
                        </div>
                      </button>
                    ))}
                  </div>

                  {education === 'Other' && (
                    <div className="pt-2">
                      <label className="block text-xs font-mono text-charcoal-600 mb-1">
                        Specify your degree or diploma:
                      </label>
                      <input
                        type="text"
                        value={customEducation}
                        onChange={(e) => setCustomEducation(e.target.value)}
                        placeholder="e.g. B.Sc Electronics, M.Tech Data Science..."
                        className="w-full px-3 py-2 bg-white border border-paper-border rounded text-xs focus:outline-none focus:border-forest-800"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* QUESTION 2: SKILLS */}
              {questionIndex === 1 && (
                <div className="space-y-4 animate-fade-in">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono uppercase text-forest-800 font-semibold tracking-wider">
                      Signal 02 • Technical Capabilities
                    </span>
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      What are you comfortable working with?
                    </h3>
                    <p className="text-xs text-charcoal-500">
                      Select technologies you have explored or written code in. You don't need manual rating numbers.
                    </p>
                  </div>

                  {/* Selected Pills */}
                  {selectedSkills.length > 0 && (
                    <div className="p-3 bg-white border border-paper-border rounded-md">
                      <span className="text-[10px] font-mono uppercase text-charcoal-400 block mb-2">
                        Selected Skills ({selectedSkills.length})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedSkills.map((s) => (
                          <span
                            key={s}
                            className="inline-flex items-center gap-1 px-2.5 py-1 bg-forest-100 text-forest-900 border border-forest-200 text-xs rounded-full font-mono"
                          >
                            <span>{s}</span>
                            <button
                              type="button"
                              onClick={() => removeSkill(s)}
                              className="hover:text-red-700"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Available Chips */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-mono uppercase text-charcoal-400 block">
                      Common Skills (Click to add)
                    </span>
                    <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-1">
                      {DEFAULT_SKILL_OPTIONS.map((sk) => {
                        const active = selectedSkills.includes(sk);
                        return (
                          <button
                            key={sk}
                            type="button"
                            onClick={() => toggleSkill(sk)}
                            className={`px-3 py-1 rounded-full text-xs font-mono transition-all border ${
                              active
                                ? 'bg-forest-800 text-white border-forest-800'
                                : 'bg-white text-charcoal-700 border-paper-border hover:border-charcoal-400'
                            }`}
                          >
                            {sk}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Add Custom Skill */}
                  <div className="flex items-center gap-2 pt-1">
                    <input
                      type="text"
                      value={customSkillInput}
                      onChange={(e) => setCustomSkillInput(e.target.value)}
                      onKeyDown={handleAddCustomSkill}
                      placeholder="Type a skill and press Enter..."
                      className="flex-1 px-3 py-2 bg-white border border-paper-border rounded text-xs focus:outline-none focus:border-forest-800"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomSkill}
                      className="px-3 py-2 bg-paper-muted hover:bg-paper-dark border border-paper-border rounded text-xs font-mono text-charcoal-700 flex items-center gap-1"
                    >
                      <Plus className="w-3.5 h-3.5" /> Add
                    </button>
                  </div>
                </div>
              )}

              {/* QUESTION 3: INTERESTS */}
              {questionIndex === 2 && (
                <div className="space-y-4 animate-fade-in">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono uppercase text-forest-800 font-semibold tracking-wider">
                      Signal 03 • Domain Curiosity
                    </span>
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      Which areas do you enjoy exploring or would like to work in?
                    </h3>
                    <p className="text-xs text-charcoal-500">
                      Select any domains that excite you. Multiple selections help our recommendation engine rank alternatives.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2">
                    {INTEREST_OPTIONS.map((interest) => {
                      const active = selectedInterests.includes(interest);
                      return (
                        <button
                          key={interest}
                          type="button"
                          onClick={() => toggleInterest(interest)}
                          className={`p-3 rounded border text-left text-xs font-medium transition-all ${
                            active
                              ? 'bg-forest-50 border-forest-800 text-forest-900 shadow-sm'
                              : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span>{interest}</span>
                            {active && <Check className="w-3.5 h-3.5 text-forest-800" />}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* QUESTION 4: CAREER DIRECTION */}
              {questionIndex === 3 && (
                <div className="space-y-4 animate-fade-in">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono uppercase text-forest-800 font-semibold tracking-wider">
                      Signal 04 • Target Horizon
                    </span>
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      If you could choose your ideal career today, what would you want to work toward?
                    </h3>
                    <p className="text-xs text-charcoal-500">
                      This is an interest signal, not a final locked choice. If you're exploring, select "I'm not sure yet".
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
                    {CAREER_OPTIONS.map((car) => {
                      const active = careerDirection === car;
                      const isUnsure = car === "I'm not sure yet";
                      return (
                        <button
                          key={car}
                          type="button"
                          onClick={() => setCareerDirection(car)}
                          className={`p-3 rounded border text-left text-xs font-medium transition-all ${
                            active
                              ? 'bg-forest-50 border-forest-800 text-forest-900 shadow-sm'
                              : isUnsure
                              ? 'bg-paper-muted border-dashed border-charcoal-400 text-charcoal-800 hover:border-charcoal-700'
                              : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className={isUnsure ? 'font-mono text-charcoal-900' : ''}>
                              {car}
                            </span>
                            {active && <Check className="w-3.5 h-3.5 text-forest-800" />}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* QUESTION 5: PRACTICAL EXPERIENCE */}
              {questionIndex === 4 && (
                <div className="space-y-4 animate-fade-in">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono uppercase text-forest-800 font-semibold tracking-wider">
                      Signal 05 • Hands-on Context
                    </span>
                    <h3 className="font-serif text-xl font-medium text-charcoal-900">
                      What have you actually built, worked on, or learned outside your classes?
                    </h3>
                    <p className="text-xs text-charcoal-500">
                      A simple free-text sentence is enough. No resume formatting or bullet points required.
                    </p>
                  </div>

                  <div className="space-y-2 pt-1">
                    <textarea
                      rows={4}
                      value={practicalExperience}
                      onChange={(e) => setPracticalExperience(e.target.value)}
                      placeholder="Example: Built a React website, made a Python project, completed a cybersecurity lab, worked on a college project..."
                      className="w-full p-3 bg-white border border-paper-border rounded-md text-xs focus:outline-none focus:border-forest-800 leading-relaxed"
                    />

                    {/* Quick Button for beginners */}
                    <button
                      type="button"
                      onClick={() => setPracticalExperience("I haven't worked on anything yet")}
                      className="text-[11px] font-mono text-charcoal-500 hover:text-forest-800 underline block"
                    >
                      "I haven't worked on anything yet" (Early learner / zero penalty)
                    </button>
                  </div>
                </div>
              )}

              {/* Footer Controls */}
              <div className="flex items-center justify-between pt-4 border-t border-paper-border">
                <span className="text-[11px] font-mono text-charcoal-400">
                  {questionIndex === 4 ? 'Ready to calibrate dossier' : 'Next question saves progress'}
                </span>

                <button
                  type="button"
                  disabled={submitting}
                  onClick={() => {
                    if (questionIndex < 4) {
                      setQuestionIndex((prev) => prev + 1);
                    } else {
                      handleQuestionsSubmit();
                    }
                  }}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5"
                >
                  <span>{questionIndex === 4 ? (submitting ? 'Calibrating...' : 'Complete Onboarding') : 'Continue'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
