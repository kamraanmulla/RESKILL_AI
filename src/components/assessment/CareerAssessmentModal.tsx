import React, { useState, useEffect } from 'react';
import {
  Compass,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Target,
  BrainCircuit,
  ShieldCheck,
  X,
  Check
} from 'lucide-react';
import { AssessmentQuestion, StudentProfile } from '../../types';
import { api } from '../../services/api';

interface CareerAssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (profile: StudentProfile) => void;
}

export const CareerAssessmentModal: React.FC<CareerAssessmentModalProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [calibrating, setCalibrating] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      loadQuestions();
    }
  }, [isOpen]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const qs = await api.getAssessmentQuestions();
      setQuestions(qs);
      // Pre-select first option for ease or leave empty
    } catch (e) {
      console.error('Failed to load assessment questions:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentQ = questions[currentIndex];
  const selectedOptionId = currentQ ? answers[currentQ.id] : undefined;

  const handleSelectOption = (optionId: string) => {
    if (!currentQ) return;
    setAnswers((prev) => ({
      ...prev,
      [currentQ.id]: optionId
    }));
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setCalibrating(true);
    try {
      // Simulate calibration pause
      await new Promise((r) => setTimeout(r, 900));
      const updatedProfile = await api.submitAssessment(answers);
      onComplete(updatedProfile);
    } catch (err) {
      console.error('Failed to submit assessment:', err);
    } finally {
      setSubmitting(false);
      setCalibrating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/65 backdrop-blur-sm animate-fade-in">
      <div className="bg-paper border border-paper-border rounded-lg shadow-2xl max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-paper-border bg-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-forest-800 text-white flex items-center justify-center">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-medium text-charcoal-900 leading-tight">
                Career Cognitive Assessment
              </h3>
              <p className="text-[11px] font-mono text-charcoal-500">
                4 questions • How do you think & what kind of work suits you?
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
        <div className="p-6 overflow-y-auto flex-1">
          {loading ? (
            <div className="py-12 text-center space-y-3 font-mono text-xs text-charcoal-500">
              <div className="w-6 h-6 border-2 border-forest-800 border-t-transparent rounded-full animate-spin mx-auto" />
              <p>Loading assessment signals...</p>
            </div>
          ) : calibrating ? (
            <div className="py-12 text-center space-y-4 animate-fade-in">
              <div className="w-12 h-12 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center mx-auto animate-pulse">
                <Sparkles className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h4 className="font-serif text-xl font-medium text-charcoal-900">
                  Calibrating Career Intelligence
                </h4>
                <p className="text-xs text-charcoal-600 max-w-xs mx-auto leading-relaxed">
                  Synthesizing your problem-solving style with industry taxonomy to calculate your hiring readiness score.
                </p>
              </div>
              <span className="inline-block px-3 py-1 bg-forest-50 border border-forest-200 text-forest-900 text-[11px] font-mono rounded-full">
                Scoring Engine Active
              </span>
            </div>
          ) : currentQ ? (
            <div className="space-y-5 animate-fade-in">
              {/* Question Index Progress */}
              <div className="flex items-center justify-between text-xs font-mono text-charcoal-500">
                <span>Question {currentIndex + 1} of {questions.length}</span>
                <div className="flex gap-1">
                  {questions.map((_, i) => (
                    <div
                      key={i}
                      className={`w-5 h-1 rounded-full transition-colors ${
                        i === currentIndex
                          ? 'bg-forest-800'
                          : i < currentIndex
                          ? 'bg-forest-400'
                          : 'bg-paper-border'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Question Text */}
              <div className="space-y-1">
                <h3 className="font-serif text-xl font-medium text-charcoal-900">
                  {currentQ.question}
                </h3>
                <p className="text-xs text-charcoal-500">
                  {currentQ.subtext}
                </p>
              </div>

              {/* Options list */}
              <div className="space-y-2 pt-2">
                {currentQ.options.map((opt) => {
                  const isSelected = selectedOptionId === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => handleSelectOption(opt.id)}
                      className={`w-full p-3.5 text-left rounded-md border text-xs transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-forest-50 border-forest-800 text-forest-900 shadow-sm'
                          : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                      }`}
                    >
                      <div className="space-y-0.5 pr-2">
                        <p className="font-medium text-charcoal-900">{opt.text}</p>
                        <span className="text-[10px] font-mono text-charcoal-400">
                          Signal: {opt.domainSignal} ({opt.styleSignal})
                        </span>
                      </div>
                      {isSelected ? (
                        <div className="w-5 h-5 rounded-full bg-forest-800 text-white flex items-center justify-center shrink-0">
                          <Check className="w-3 h-3" />
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full border border-paper-border bg-paper shrink-0" />
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Footer navigation */}
              <div className="flex items-center justify-between pt-4 border-t border-paper-border">
                <button
                  type="button"
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex((prev) => prev - 1)}
                  className="flex items-center gap-1 text-xs font-mono text-charcoal-500 hover:text-charcoal-800 disabled:opacity-30"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Previous
                </button>

                <button
                  type="button"
                  disabled={!selectedOptionId || submitting}
                  onClick={handleNext}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5"
                >
                  <span>{currentIndex === questions.length - 1 ? 'Finish & Calibrate Dossier' : 'Next Question'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
