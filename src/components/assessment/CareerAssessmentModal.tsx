import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  X,
  Check,
  ArrowRight,
  Sparkles,
  Layers,
  Compass,
  Zap,
  Target,
  ShieldAlert,
  HelpCircle,
  TrendingUp,
  Activity,
  CheckCircle2,
  RefreshCw,
  GitMerge,
  Award
} from 'lucide-react';
import {
  StudentProfile,
  AssessmentSessionState,
  CareerIntelligenceProfile,
  ConfidenceLevel,
  InterestRating
} from '../../types';
import { api } from '../../services/api';

interface CareerAssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (profile: StudentProfile) => void;
  onNavigateToRoadmap?: () => void;
}

const DOMAINS_LIST = [
  { id: 'cybersecurity', label: 'Cybersecurity', desc: 'Threat detection, incident response, network defense' },
  { id: 'backend', label: 'Backend Development', desc: 'API architecture, database schemas, distributed servers' },
  { id: 'frontend', label: 'Frontend Development', desc: 'Client interfaces, state systems, UI performance' },
  { id: 'cloud_devops', label: 'Cloud & DevOps', desc: 'Containerization, CI/CD, cloud infrastructure resilience' },
  { id: 'ai_ml', label: 'AI / Machine Learning', desc: 'Model architectures, evaluation metrics, deep learning' },
  { id: 'data_science', label: 'Data Science', desc: 'Statistical testing, predictive pipelines, analytical SQL' },
  { id: 'fullstack', label: 'Full Stack Development', desc: 'End-to-end integration, reactive clients & APIs' }
];

const SCENARIO_PREFERENCES = [
  { id: 'threat_hunting', label: 'Investigating security intrusions & attack surfaces', domain: 'cybersecurity' },
  { id: 'api_scaling', label: 'Architecting high-concurrency server APIs and databases', domain: 'backend' },
  { id: 'cloud_infra', label: 'Automating zero-downtime cloud pipelines & containers', domain: 'cloud_devops' },
  { id: 'ai_models', label: 'Training and evaluating predictive machine learning models', domain: 'ai_ml' },
  { id: 'data_insights', label: 'Running statistical experiments and data analytics', domain: 'data_science' },
  { id: 'frontend_ui', label: 'Designing accessible, high-performance user interfaces', domain: 'frontend' }
];

export const CareerAssessmentModal: React.FC<CareerAssessmentModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  onNavigateToRoadmap
}) => {
  const [session, setSession] = useState<AssessmentSessionState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [calibrating, setCalibrating] = useState<boolean>(false);

  // Current question inputs
  const [selectedOptionId, setSelectedOptionId] = useState<string>('');
  const [confidence, setConfidence] = useState<ConfidenceLevel>('confident');

  // Interest phase inputs
  const [domainInterests, setDomainInterests] = useState<Record<string, InterestRating>>({
    cybersecurity: 'interested',
    backend: 'interested',
    frontend: 'interested',
    cloud_devops: 'interested',
    ai_ml: 'interested',
    data_science: 'interested',
    fullstack: 'interested'
  });
  const [scenarioPref, setScenarioPref] = useState<string>('threat_hunting');

  // Practical phase inputs
  const [selectedPracticalOption, setSelectedPracticalOption] = useState<string>('');
  const [practicalReasoning, setPracticalReasoning] = useState<string>('');

  // Final Intelligence Profile
  const [profile, setProfile] = useState<CareerIntelligenceProfile | null>(null);

  useEffect(() => {
    if (isOpen) {
      initAssessment();
    }
  }, [isOpen]);

  const initAssessment = async () => {
    setLoading(true);
    try {
      // First check if user already completed the profile
      const existingProfile = await api.getCareerIntelligenceProfile();
      if (existingProfile) {
        setProfile(existingProfile);
        setLoading(false);
        return;
      }

      const sess = await api.startAssessmentSession(false);
      setSession(sess);
      if (sess.profile) {
        setProfile(sess.profile);
      }
    } catch (e) {
      console.error('Failed to initialize assessment session:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = async () => {
    setLoading(true);
    setProfile(null);
    setSelectedOptionId('');
    setSelectedPracticalOption('');
    setPracticalReasoning('');
    try {
      const sess = await api.startAssessmentSession(true);
      setSession(sess);
    } catch (e) {
      console.error('Failed to restart assessment:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!session || !session.currentQuestion || !selectedOptionId) return;

    setSubmitting(true);
    try {
      const updatedSess = await api.answerAssessmentQuestion(
        session.currentQuestion.id,
        selectedOptionId,
        confidence
      );
      setSession(updatedSess);
      setSelectedOptionId('');
      setConfidence('confident');

      if (updatedSess.isComplete && updatedSess.profile) {
        setProfile(updatedSess.profile);
      }
    } catch (e) {
      console.error('Failed to submit question answer:', e);
    } finally {
      setSubmitting(false);
    }
  };

  const handleInterestSubmit = async () => {
    setSubmitting(true);
    try {
      const interestPayload = Object.entries(domainInterests).map(([domain, interestLevel]) => ({
        domain,
        interestLevel
      }));

      const updatedSess = await api.submitAssessmentInterests(interestPayload, scenarioPref);
      setSession(updatedSess);
    } catch (e) {
      console.error('Failed to submit domain interests:', e);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePracticalSubmit = async () => {
    if (!session || !session.currentPracticalScenario || !selectedPracticalOption) return;

    setSubmitting(true);
    setCalibrating(true);
    try {
      // Short pause for intelligence synthesis visual feedback
      await new Promise((r) => setTimeout(r, 700));

      const intelProfile = await api.submitAssessmentPractical(
        session.currentPracticalScenario.id,
        selectedPracticalOption,
        practicalReasoning
      );
      setProfile(intelProfile);

      // Refresh student profile
      const updatedProfile = await api.getProfile();
      onComplete(updatedProfile);
    } catch (e) {
      console.error('Failed to submit practical challenge:', e);
    } finally {
      setSubmitting(false);
      setCalibrating(false);
    }
  };

  if (!isOpen) return null;

  // Render Phase Badge
  const getPhaseDisplay = () => {
    if (profile) return 'Career Intelligence Profile';
    if (!session) return 'Loading...';
    switch (session.currentPhase) {
      case 'MIXED_DISCOVERY':
        return 'Phase 1: Mixed Discovery';
      case 'ADAPTIVE_EXPLORATION':
        return 'Phase 2: Adaptive Exploration';
      case 'INTEREST_DISCOVERY':
        return 'Phase 3: Interest Discovery';
      case 'PRACTICAL_CHALLENGE':
        return 'Phase 4: Practical Challenge';
      default:
        return 'Career Assessment';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-charcoal-900/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-paper border border-paper-border rounded-lg shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-paper-border bg-white flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded bg-forest-800 text-white flex items-center justify-center shadow-subtle">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-lg font-medium text-charcoal-900 leading-tight">
                  Adaptive Career Intelligence Assessment
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-200">
                  {getPhaseDisplay()}
                </span>
              </div>
              <p className="text-[11px] font-mono text-charcoal-500">
                Evidence-driven discovery • Calibrating knowledge, interest, confidence & practical ability
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            {profile && (
              <button
                onClick={handleRestart}
                title="Retake assessment"
                className="p-1.5 text-charcoal-400 hover:text-charcoal-700 hover:bg-paper-muted rounded transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 text-charcoal-400 hover:text-charcoal-700 hover:bg-paper-muted rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {loading ? (
            <div className="py-16 text-center space-y-3 font-mono text-xs text-charcoal-500">
              <div className="w-6 h-6 border-2 border-forest-800 border-t-transparent rounded-full animate-spin mx-auto" />
              <p>Initializing Adaptive Assessment Engine...</p>
            </div>
          ) : calibrating ? (
            <div className="py-16 text-center space-y-4 animate-fade-in">
              <div className="w-12 h-12 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center mx-auto animate-pulse">
                <Sparkles className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h4 className="font-serif text-xl font-medium text-charcoal-900">
                  Synthesizing Career Intelligence Profile
                </h4>
                <p className="text-xs text-charcoal-600 max-w-sm mx-auto leading-relaxed">
                  Correlating demonstrated knowledge signals, explicit interest, confidence calibration, and practical challenge evidence across 7 canonical domains.
                </p>
              </div>
              <span className="inline-block px-3 py-1 bg-forest-50 border border-forest-200 text-forest-900 text-[11px] font-mono rounded-full">
                Intelligence Engines Active: Combination, Transferability, Gap & Roadmap
              </span>
            </div>
          ) : profile ? (
            /* ================================================================
               FINAL RESULT SCREEN: YOUR CAREER INTELLIGENCE PROFILE
               ================================================================ */
            <div className="space-y-6 animate-fade-in">
              {/* Profile Top Banner */}
              <div className="p-4 bg-forest-50/70 border border-forest-200 rounded-md space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="w-4 h-4 text-forest-800" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-forest-900 font-mono">
                      Your Career Intelligence Profile
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-charcoal-500">
                    {profile.completedAt}
                  </span>
                </div>
                <p className="text-xs text-charcoal-700 leading-relaxed">
                  {profile.profileObservation}
                </p>
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  {profile.isMultiDomain && (
                    <span className="px-2 py-0.5 bg-forest-800 text-white text-[10px] font-mono rounded-full flex items-center gap-1">
                      <GitMerge className="w-3 h-3" /> Multi-Domain Profile
                    </span>
                  )}
                  <span className="px-2 py-0.5 bg-white border border-paper-border text-charcoal-700 text-[10px] font-mono rounded-full">
                    {profile.breadthVsDepth}
                  </span>
                  <span className="px-2 py-0.5 bg-white border border-paper-border text-charcoal-700 text-[10px] font-mono rounded-full">
                    {profile.theoryVsPractical}
                  </span>
                </div>
              </div>

              {/* 1. Demonstrated Knowledge & Interest Signals Map */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-charcoal-700">
                    Demonstrated Knowledge Signals
                  </h4>
                  <span className="text-[10px] font-mono text-charcoal-400">
                    Assessment signals, not absolute expertise percentages
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {Object.values(profile.domainSignals).map((sig) => (
                    <div
                      key={sig.domain}
                      className="p-3 bg-white border border-paper-border rounded-md space-y-1.5 hover:border-charcoal-400 transition-colors"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-charcoal-900">{sig.domainLabel}</span>
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px] font-mono text-charcoal-500">
                            Interest: <strong className="text-charcoal-800">{sig.interestLevel}</strong>
                          </span>
                          <span className="font-mono font-bold text-forest-800 text-xs">
                            {sig.demonstratedKnowledge}
                          </span>
                        </div>
                      </div>

                      {/* Knowledge Signal Bar */}
                      <div className="w-full h-1.5 bg-paper rounded-full overflow-hidden border border-paper-border">
                        <div
                          className="h-full bg-forest-700 transition-all rounded-full"
                          style={{ width: `${sig.demonstratedKnowledge}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[10px] font-mono text-charcoal-400 pt-0.5">
                        <span>Evidence: {sig.evidenceStrength}</span>
                        <span>Confidence: {sig.confidenceSignal}</span>
                        <span>Practical: {sig.practicalScore}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 2. Discovered Skill Combinations (Multi-Domain Synergy) */}
              {profile.discoveredCombinations && profile.discoveredCombinations.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                    <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-charcoal-700">
                      Discovered Skill Combinations
                    </h4>
                  </div>

                  <div className="space-y-2">
                    {profile.discoveredCombinations.slice(0, 3).map((combo, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-amber-50/50 border border-amber-200/80 rounded-md text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-charcoal-900">
                            {combo.career} Pathway
                          </span>
                          <span className="font-mono text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-900 rounded">
                            {Math.round(combo.confidence * 100)}% Synergy
                          </span>
                        </div>
                        <p className="text-[11px] text-charcoal-600 leading-relaxed">
                          {combo.explanation}
                        </p>
                        <div className="flex flex-wrap items-center gap-1 text-[10px] font-mono text-charcoal-500">
                          <span>Skills:</span>
                          {combo.supportingSkills.map((s, si) => (
                            <span key={si} className="px-1.5 py-0.2 bg-white border border-amber-200 rounded text-amber-950 font-medium">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 3. Relevant Career Pathways */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-charcoal-700">
                    Relevant Career Pathways
                  </h4>
                  <span className="text-[10px] font-mono text-charcoal-400">
                    You decide the outcome • Multiple paths supported
                  </span>
                </div>

                <div className="space-y-2.5">
                  {profile.relevantPathways.slice(0, 4).map((pathway) => (
                    <div
                      key={pathway.careerId}
                      className="p-3.5 bg-white border border-paper-border rounded-md space-y-2 hover:border-forest-800/60 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h5 className="font-semibold text-charcoal-900 text-xs">
                              {pathway.title}
                            </h5>
                            <span className="text-[10px] font-mono text-charcoal-400">
                              ({pathway.category})
                            </span>
                          </div>
                          <p className="text-[11px] text-charcoal-600 mt-0.5 leading-relaxed">
                            {pathway.explanation}
                          </p>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="font-mono font-bold text-forest-800 text-sm">
                            {pathway.matchScore}%
                          </span>
                          <span className="block text-[9px] font-mono text-charcoal-400">
                            Alignment
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-[10px] font-mono pt-1 border-t border-paper-border text-charcoal-500">
                        {pathway.existingSkills.length > 0 && (
                          <span>
                            Demonstrated: <strong className="text-forest-800">{pathway.existingSkills.join(', ')}</strong>
                          </span>
                        )}
                        {pathway.transferableSkills.length > 0 && (
                          <span>
                            Transferable: <strong className="text-charcoal-700">{pathway.transferableSkills.slice(0, 2).join(', ')}</strong>
                          </span>
                        )}
                        {pathway.missingSkills.length > 0 && (
                          <span>
                            Priority Gap: <strong className="text-amber-700">{pathway.missingSkills[0]}</strong>
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. Suggested Next Development Priorities */}
              {profile.suggestedNextDevelopment && profile.suggestedNextDevelopment.length > 0 && (
                <div className="p-3.5 bg-paper-muted border border-paper-border rounded-md text-xs space-y-1.5">
                  <div className="flex items-center gap-1.5 text-charcoal-800 font-medium font-mono text-[11px]">
                    <Target className="w-3.5 h-3.5 text-forest-800" />
                    Recommended Immediate Development Focus
                  </div>
                  <ul className="space-y-1 text-[11px] text-charcoal-600 list-disc list-inside">
                    {profile.suggestedNextDevelopment.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-3 border-t border-paper-border">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 bg-white hover:bg-paper-muted border border-paper-border text-xs font-medium text-charcoal-700 rounded transition-colors"
                >
                  Close & View Dashboard
                </button>

                {onNavigateToRoadmap && (
                  <button
                    type="button"
                    onClick={() => {
                      onClose();
                      onNavigateToRoadmap();
                    }}
                    className="px-5 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5 transition-colors"
                  >
                    <span>Open My Personalized Roadmap</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          ) : session && session.currentPhase === 'INTEREST_DISCOVERY' ? (
            /* ================================================================
               PHASE 3: INTEREST DISCOVERY
               ================================================================ */
            <div className="space-y-5 animate-fade-in">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-200">
                    Phase 3: Interest Discovery
                  </span>
                </div>
                <h4 className="font-serif text-xl font-medium text-charcoal-900">
                  What domains do you actually want to explore?
                </h4>
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  Careers are outcomes. Interests represent where you want to spend your energy. We store this strictly separately from your demonstrated knowledge.
                </p>
              </div>

              {/* Domain Interest Sliders/Options */}
              <div className="space-y-2.5">
                {DOMAINS_LIST.map((d) => (
                  <div
                    key={d.id}
                    className="p-3 bg-white border border-paper-border rounded-md flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs"
                  >
                    <div>
                      <p className="font-medium text-charcoal-900">{d.label}</p>
                      <p className="text-[11px] text-charcoal-500">{d.desc}</p>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {(['not_interested', 'slightly_interested', 'interested', 'very_interested'] as InterestRating[]).map((rating) => {
                        const isSelected = domainInterests[d.id] === rating;
                        const labels: Record<InterestRating, string> = {
                          not_interested: 'Not interested',
                          slightly_interested: 'Slight',
                          interested: 'Interested',
                          very_interested: 'Very High'
                        };
                        return (
                          <button
                            key={rating}
                            type="button"
                            onClick={() =>
                              setDomainInterests((prev) => ({
                                ...prev,
                                [d.id]: rating
                              }))
                            }
                            className={`px-2 py-1 text-[10px] font-mono rounded border transition-all ${
                              isSelected
                                ? 'bg-forest-800 text-white border-forest-800 font-semibold'
                                : 'bg-paper text-charcoal-600 border-paper-border hover:bg-white'
                            }`}
                          >
                            {labels[rating]}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>

              {/* Scenario Preference (Indirect Interest) */}
              <div className="space-y-2 pt-2 border-t border-paper-border">
                <label className="block text-xs font-semibold text-charcoal-800 font-mono">
                  Scenario Preference: Which type of problem would you enjoy investigating most?
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {SCENARIO_PREFERENCES.map((pref) => {
                    const isSelected = scenarioPref === pref.id;
                    return (
                      <button
                        key={pref.id}
                        type="button"
                        onClick={() => setScenarioPref(pref.id)}
                        className={`p-2.5 text-left rounded border text-xs transition-all ${
                          isSelected
                            ? 'bg-forest-50 border-forest-800 text-forest-900 font-medium'
                            : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                        }`}
                      >
                        {pref.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Submit Interest */}
              <div className="pt-3 border-t border-paper-border flex justify-end">
                <button
                  type="button"
                  disabled={submitting}
                  onClick={handleInterestSubmit}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5 transition-colors"
                >
                  <span>Proceed to Practical Challenge</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : session && session.currentPhase === 'PRACTICAL_CHALLENGE' && session.currentPracticalScenario ? (
            /* ================================================================
               PHASE 4: PRACTICAL CHALLENGE
               ================================================================ */
            <div className="space-y-5 animate-fade-in">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-200">
                    Phase 4: Practical Application Challenge
                  </span>
                  <span className="text-[10px] font-mono text-charcoal-500">
                    Domain: {session.currentPracticalScenario.domainLabel}
                  </span>
                </div>
                <h4 className="font-serif text-xl font-medium text-charcoal-900">
                  {session.currentPracticalScenario.title}
                </h4>
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  {session.currentPracticalScenario.scenarioText}
                </p>
              </div>

              {/* Context Code / Telemetry Snippet */}
              {session.currentPracticalScenario.contextSnippet && (
                <div className="p-3 bg-charcoal-900 text-emerald-400 font-mono text-[11px] rounded-md overflow-x-auto border border-charcoal-800">
                  <pre className="whitespace-pre-wrap leading-relaxed">
                    {session.currentPracticalScenario.contextSnippet}
                  </pre>
                </div>
              )}

              {/* Practical Options */}
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-charcoal-800 font-mono">
                  Select your applied remediation strategy:
                </label>
                {session.currentPracticalScenario.options.map((opt) => {
                  const isSelected = selectedPracticalOption === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setSelectedPracticalOption(opt.id)}
                      className={`w-full p-3 text-left rounded-md border text-xs transition-all flex items-start gap-2.5 ${
                        isSelected
                          ? 'bg-forest-50 border-forest-800 text-forest-900 font-medium'
                          : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                      }`}
                    >
                      <div className="w-4 h-4 rounded-full border border-paper-border mt-0.5 flex items-center justify-center shrink-0 bg-white">
                        {isSelected && <div className="w-2 h-2 rounded-full bg-forest-800" />}
                      </div>
                      <span className="whitespace-pre-wrap leading-relaxed">{opt.text}</span>
                    </button>
                  );
                })}
              </div>

              {/* Optional Open-Ended Reasoning Box */}
              <div className="space-y-1.5 pt-1">
                <label className="block text-[11px] font-mono text-charcoal-600">
                  Applied Reasoning Reflection (Optional — explains your decision-making sequence):
                </label>
                <textarea
                  value={practicalReasoning}
                  onChange={(e) => setPracticalReasoning(e.target.value)}
                  placeholder="Explain why you would prioritize these steps and how you would prevent recurrence..."
                  rows={2}
                  className="w-full p-2.5 text-xs bg-white border border-paper-border rounded-md focus:border-forest-800 focus:outline-none"
                />
              </div>

              {/* Submit Practical */}
              <div className="pt-3 border-t border-paper-border flex justify-end">
                <button
                  type="button"
                  disabled={!selectedPracticalOption || submitting}
                  onClick={handlePracticalSubmit}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5 transition-colors"
                >
                  <span>Synthesize Career Intelligence Profile</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : session && session.currentQuestion ? (
            /* ================================================================
               PHASES 1 & 2: MIXED DISCOVERY & ADAPTIVE EXPLORATION
               ================================================================ */
            <div className="space-y-5 animate-fade-in">
              {/* Question Progress & Domain Pill */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono text-charcoal-500">
                <div className="flex items-center gap-2">
                  <span>Question {session.questionsAnsweredCount + 1} of ~{session.totalEstimatedQuestions}</span>
                  <span className="px-2 py-0.5 bg-paper-muted border border-paper-border rounded text-[10px] text-charcoal-700">
                    {session.currentQuestion.domainLabel} • {session.currentQuestion.skill}
                  </span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-white border border-paper-border text-charcoal-500">
                  {session.currentQuestion.difficulty} • {session.currentQuestion.questionType}
                </span>
              </div>

              {/* Adaptive Feedback Context Note */}
              {session.currentQuestion.contextNote && (
                <div className="p-2.5 bg-forest-50/70 border border-forest-200 rounded text-[11px] text-forest-900 flex items-center gap-2 animate-fade-in">
                  <Sparkles className="w-3.5 h-3.5 text-forest-800 shrink-0" />
                  <span>{session.currentQuestion.contextNote}</span>
                </div>
              )}

              {/* Question Text */}
              <div className="space-y-1">
                <h4 className="font-serif text-xl font-medium text-charcoal-900 leading-tight">
                  {session.currentQuestion.question}
                </h4>
                {session.currentQuestion.scenario && (
                  <p className="text-xs text-charcoal-600 italic">
                    Scenario: {session.currentQuestion.scenario}
                  </p>
                )}
              </div>

              {/* Options */}
              <div className="space-y-2 pt-1">
                {session.currentQuestion.options.map((opt) => {
                  const isSelected = selectedOptionId === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setSelectedOptionId(opt.id)}
                      className={`w-full p-3.5 text-left rounded-md border text-xs transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-forest-50 border-forest-800 text-forest-900 font-medium shadow-sm'
                          : 'bg-white border-paper-border text-charcoal-700 hover:border-charcoal-400'
                      }`}
                    >
                      <span className="pr-3 leading-relaxed">{opt.text}</span>
                      <div className="w-4 h-4 rounded-full border border-paper-border shrink-0 flex items-center justify-center bg-white">
                        {isSelected && <div className="w-2 h-2 rounded-full bg-forest-800" />}
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Confidence Selector */}
              <div className="pt-2 border-t border-paper-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 text-[11px] font-mono text-charcoal-600">
                  <HelpCircle className="w-3.5 h-3.5 text-charcoal-400" />
                  <span>How confident are you in this answer?</span>
                </div>
                <div className="flex items-center gap-1">
                  {(['guessing', 'somewhat_confident', 'confident', 'very_confident'] as ConfidenceLevel[]).map((level) => {
                    const isSelected = confidence === level;
                    const labels: Record<ConfidenceLevel, string> = {
                      guessing: 'Guessing',
                      somewhat_confident: 'Somewhat',
                      confident: 'Confident',
                      very_confident: 'Very Confident'
                    };
                    return (
                      <button
                        key={level}
                        type="button"
                        onClick={() => setConfidence(level)}
                        className={`px-2.5 py-1 text-[10px] font-mono rounded border transition-all ${
                          isSelected
                            ? 'bg-forest-800 text-white border-forest-800 font-semibold'
                            : 'bg-paper text-charcoal-600 border-paper-border hover:bg-white'
                        }`}
                      >
                        {labels[level]}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Footer */}
              <div className="pt-3 border-t border-paper-border flex justify-end">
                <button
                  type="button"
                  disabled={!selectedOptionId || submitting}
                  onClick={handleAnswerSubmit}
                  className="px-5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-50 text-white text-xs font-medium rounded shadow-subtle flex items-center gap-1.5 transition-colors"
                >
                  <span>Submit & Next Question</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-charcoal-500 font-mono">
              <p>Session completed. Loading profile...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
