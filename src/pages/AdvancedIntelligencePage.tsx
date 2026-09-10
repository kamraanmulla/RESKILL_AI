import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Layers,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Compass,
  CheckCircle2,
  RefreshCw,
  ShieldCheck,
  Zap,
  Info,
  ExternalLink
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import {
  AdvancedIntelligenceSummary,
  CareerRole,
  StudentProfile
} from '../types';
import { api } from '../services/api';

interface AdvancedIntelligencePageProps {
  student: StudentProfile;
  careers: CareerRole[];
  onSelectCareer?: (careerId: string) => void;
  onNavigateToRoadmap?: () => void;
}

export const AdvancedIntelligencePage: React.FC<AdvancedIntelligencePageProps> = ({
  student,
  careers,
  onSelectCareer,
  onNavigateToRoadmap
}) => {
  const [data, setData] = useState<AdvancedIntelligenceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDestinationCareer, setSelectedDestinationCareer] = useState<string>(
    student.targetCareerId === 'career_cybersecurity' ? 'career_fullstack' : 'career_cybersecurity'
  );
  const [transferabilityLoading, setTransferabilityLoading] = useState(false);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const summary = await api.getAdvancedIntelligenceSummary(selectedDestinationCareer);
      setData(summary);
    } catch (err) {
      console.error('Failed to load advanced intelligence summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleDestinationChange = async (careerId: string) => {
    setSelectedDestinationCareer(careerId);
    setTransferabilityLoading(true);
    try {
      const res = await api.getTransferability(careerId);
      if (res && data) {
        setData({
          ...data,
          transferability: res
        });
      }
    } catch (err) {
      console.error('Failed to update transferability:', err);
    } finally {
      setTransferabilityLoading(false);
    }
  };

  const currentCareer = careers.find(c => c.id === student.targetCareerId) || careers[0];

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <SectionHeader
        title="Advanced Career Intelligence"
        subtitle="Deep multi-vector analysis of your demonstrated competencies, career mobility, and skill portfolio health."
        badge="Multi-Vector Engine"
      />

      {/* Overview Metric Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 bg-white border border-paper-border rounded-md shadow-subtle">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-charcoal-500 uppercase">
            <Sparkles className="w-3.5 h-3.5 text-forest-700" />
            <span>Hidden Competencies</span>
          </div>
          <div className="text-2xl font-serif font-bold text-charcoal-900 mt-1">
            {data?.hiddenCompetencies.length || 0}
          </div>
          <div className="text-[11px] text-charcoal-500 mt-0.5">Inferred from evidence</div>
        </div>

        <div className="p-4 bg-white border border-paper-border rounded-md shadow-subtle">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-charcoal-500 uppercase">
            <TrendingUp className="w-3.5 h-3.5 text-forest-700" />
            <span>Transferability</span>
          </div>
          <div className="text-2xl font-serif font-bold text-charcoal-900 mt-1">
            {data?.transferability?.overallScore || 0}%
          </div>
          <div className="text-[11px] text-charcoal-500 mt-0.5">Cross-career portability</div>
        </div>

        <div className="p-4 bg-white border border-paper-border rounded-md shadow-subtle">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-charcoal-500 uppercase">
            <Zap className="w-3.5 h-3.5 text-amber-700" />
            <span>Synergies</span>
          </div>
          <div className="text-2xl font-serif font-bold text-charcoal-900 mt-1">
            {data?.combinations.length || 0}
          </div>
          <div className="text-[11px] text-charcoal-500 mt-0.5">Unlocked pathways</div>
        </div>

        <div className="p-4 bg-white border border-paper-border rounded-md shadow-subtle">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-charcoal-500 uppercase">
            <ShieldCheck className="w-3.5 h-3.5 text-forest-800" />
            <span>Portfolio Quality</span>
          </div>
          <div className="text-2xl font-serif font-bold text-charcoal-900 mt-1">
            {data?.contradictions.length === 0 ? 'Verified' : `${data?.contradictions.length} Notice(s)`}
          </div>
          <div className="text-[11px] text-charcoal-500 mt-0.5">Evidence calibration</div>
        </div>
      </div>

      {/* VECTOR 1: HIDDEN COMPETENCY DETECTION */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4 shadow-subtle">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-800 text-[10px] font-mono uppercase font-semibold rounded">
                Vector 01
              </span>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Hidden Competency Detection
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 mt-1">
              Skills you demonstrate through real projects and coursework that are not explicitly claimed in your primary skill list.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="py-8 text-center text-xs font-mono text-charcoal-500">Analyzing portfolio evidence...</div>
        ) : (data?.hiddenCompetencies && data.hiddenCompetencies.length > 0) ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {data.hiddenCompetencies.map((comp, idx) => (
              <div key={idx} className="p-3.5 bg-paper rounded border border-paper-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-charcoal-900">{comp.skill}</span>
                  <span className="px-2 py-0.5 bg-white border border-paper-border text-forest-800 font-mono text-[10px] rounded">
                    {(comp.confidence * 100).toFixed(0)}% Confidence
                  </span>
                </div>
                <p className="text-[11px] text-charcoal-600 leading-relaxed">{comp.reasoning}</p>
                <div className="pt-1 flex items-center gap-1.5 text-[10px] font-mono text-charcoal-500 border-t border-paper-border/60">
                  <span className="font-medium text-charcoal-700">Source:</span>
                  <span>{comp.evidence}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 bg-paper rounded text-center text-xs text-charcoal-500">
            No hidden competencies detected yet. Add detailed project artifacts or practical experience to unlock inferred skills.
          </div>
        )}
      </div>

      {/* VECTOR 2: SKILL TRANSFERABILITY SCORE */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-5 shadow-subtle">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-800 text-[10px] font-mono uppercase font-semibold rounded">
                Vector 02
              </span>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Skill Transferability Engine
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 mt-1">
              Measure how your existing competencies translate when transitioning into an adjacent technology domain.
            </p>
          </div>

          {/* Career Switcher for Transferability Target */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-charcoal-500">Compare to:</span>
            <select
              value={selectedDestinationCareer}
              onChange={(e) => handleDestinationChange(e.target.value)}
              className="text-xs px-2.5 py-1.5 bg-paper border border-paper-border rounded text-charcoal-800 font-medium focus:outline-none focus:border-forest-800"
            >
              {careers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {data?.transferability && (
          <div className="space-y-4 pt-1">
            {/* Score & Explanation Bar */}
            <div className="p-4 bg-paper rounded-md border border-paper-border flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <div className="flex items-center gap-3 shrink-0">
                <div className="w-14 h-14 rounded-full bg-white border-2 border-forest-800 flex items-center justify-center font-serif text-lg font-bold text-forest-900 shadow-sm">
                  {data.transferability.overallScore}%
                </div>
                <div>
                  <span className="text-xs font-semibold text-charcoal-900 block">
                    {data.transferability.sourceCareer} → {data.transferability.destinationCareer}
                  </span>
                  <span className="text-[11px] font-mono text-forest-800">
                    {data.transferability.overallScore >= 70 ? 'High Mobility' : data.transferability.overallScore >= 45 ? 'Moderate Transition' : 'Foundational Pivot'}
                  </span>
                </div>
              </div>
              <p className="text-xs text-charcoal-600 border-l border-paper-border pl-4">
                {data.transferability.explanation}
              </p>
            </div>

            {/* Transferable vs Bridge vs Missing Breakdown */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3.5 bg-white border border-paper-border rounded">
                <div className="text-[11px] font-mono uppercase text-forest-800 font-medium mb-2 flex items-center justify-between">
                  <span>Directly Transferable</span>
                  <span>({data.transferability.transferableSkills.length})</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {data.transferability.transferableSkills.length > 0 ? (
                    data.transferability.transferableSkills.map((s, i) => (
                      <span key={i} className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-900 text-[11px] rounded font-mono">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-charcoal-400">No direct overlap</span>
                  )}
                </div>
              </div>

              <div className="p-3.5 bg-white border border-paper-border rounded">
                <div className="text-[11px] font-mono uppercase text-amber-900 font-medium mb-2 flex items-center justify-between">
                  <span>Bridgeable Skills</span>
                  <span>({data.transferability.bridgeSkills.length})</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {data.transferability.bridgeSkills.length > 0 ? (
                    data.transferability.bridgeSkills.map((s, i) => (
                      <span key={i} className="px-2 py-0.5 bg-amber-50 border border-amber-200 text-amber-900 text-[11px] rounded font-mono">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-charcoal-400">None identified</span>
                  )}
                </div>
              </div>

              <div className="p-3.5 bg-white border border-paper-border rounded">
                <div className="text-[11px] font-mono uppercase text-charcoal-500 font-medium mb-2 flex items-center justify-between">
                  <span>Required Skills</span>
                  <span>({data.transferability.missingSkills.length})</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {data.transferability.missingSkills.map((s, i) => (
                    <span key={i} className="px-2 py-0.5 bg-paper border border-paper-border text-charcoal-700 text-[11px] rounded font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* VECTOR 3: SKILL COMBINATION DISCOVERY */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4 shadow-subtle">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-800 text-[10px] font-mono uppercase font-semibold rounded">
              Vector 03
            </span>
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Synergistic Combination Discovery
            </h3>
          </div>
          <p className="text-xs text-charcoal-600 mt-1">
            Combinations of 2 to 5 skills that create unique multi-disciplinary opportunities across the market.
          </p>
        </div>

        {data?.combinations && data.combinations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {data.combinations.map((comb, idx) => (
              <div key={idx} className="p-4 bg-paper rounded border border-paper-border space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="font-serif text-sm font-semibold text-charcoal-900">
                    {comb.career}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-forest-100 text-forest-900 font-medium rounded">
                    {(comb.confidence * 100).toFixed(0)}% Match
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {comb.combination.map((c, i) => (
                    <span key={i} className="px-2 py-0.5 bg-white border border-paper-border text-charcoal-800 text-[11px] font-mono rounded">
                      {c}
                    </span>
                  ))}
                </div>

                <p className="text-[11px] text-charcoal-600 leading-relaxed">
                  {comb.explanation}
                </p>

                {comb.missingSkills.length > 0 && (
                  <div className="pt-2 border-t border-paper-border/60 text-[11px] text-charcoal-500 font-mono">
                    <span className="font-medium text-charcoal-700">Next Unlock:</span> {comb.missingSkills.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 bg-paper rounded text-center text-xs text-charcoal-500">
            Acquire 2 or more complementary skills to uncover combined career opportunities.
          </div>
        )}
      </div>

      {/* VECTOR 4: CONTRADICTION & CALIBRATION MISMATCHES */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4 shadow-subtle">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-800 text-[10px] font-mono uppercase font-semibold rounded">
              Vector 04
            </span>
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Evidence Calibration & Verification
            </h3>
          </div>
          <p className="text-xs text-charcoal-600 mt-1">
            Constructive identification of evidence gaps between self-claimed proficiency, code repositories, and diagnostic assessments.
          </p>
        </div>

        {data?.contradictions && data.contradictions.length > 0 ? (
          <div className="space-y-3 pt-1">
            {data.contradictions.map((contra, idx) => (
              <div key={idx} className="p-4 bg-amber-50/70 border border-amber-200 rounded space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-800 shrink-0" />
                    <span className="text-xs font-semibold text-charcoal-900">{contra.skill}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-white border border-amber-300 text-amber-900 text-[10px] font-mono uppercase font-semibold rounded">
                    {contra.severity} Notice
                  </span>
                </div>

                <p className="text-xs text-charcoal-700 leading-relaxed">
                  {contra.explanation}
                </p>

                <div className="pt-2 border-t border-amber-200/60 flex items-start gap-1.5 text-[11px] text-charcoal-600">
                  <span className="font-semibold text-forest-900 shrink-0">Recommendation:</span>
                  <span>{contra.recommendation}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-forest-50 border border-forest-200 rounded flex items-center gap-2.5 text-xs text-forest-900">
            <CheckCircle2 className="w-4 h-4 text-forest-800 shrink-0" />
            <span>High evidence alignment: Self-claimed competencies are substantiated by corresponding projects and diagnostic signals.</span>
          </div>
        )}
      </div>

      {/* VECTOR 5: OBSOLESCENCE & TREND MONITORING */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4 shadow-subtle">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-forest-50 border border-forest-200 text-forest-800 text-[10px] font-mono uppercase font-semibold rounded">
                Vector 05
              </span>
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Technology Trends & Skill Modernization
              </h3>
            </div>
            <p className="text-xs text-charcoal-600 mt-1">
              Tracks the industry lifecycle of your technologies and recommends adjacent contemporary replacements.
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-paper border border-paper-border text-charcoal-500">
            Curated/Internal Trend Dataset
          </span>
        </div>

        {data?.obsolescence && data.obsolescence.length > 0 ? (
          <div className="space-y-3 pt-1">
            {data.obsolescence.map((obs, idx) => (
              <div key={idx} className="p-3.5 bg-paper rounded border border-paper-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1 max-w-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-charcoal-900">{obs.skill}</span>
                    <span className={`px-2 py-0.2 text-[10px] font-mono rounded ${
                      obs.trend === 'Stable'
                        ? 'bg-forest-100 text-forest-900'
                        : obs.trend === 'Watch'
                        ? 'bg-amber-100 text-amber-900'
                        : 'bg-rose-100 text-rose-900'
                    }`}>
                      {obs.trend}
                    </span>
                  </div>
                  <p className="text-[11px] text-charcoal-600 leading-relaxed">{obs.reason}</p>
                </div>

                <div className="sm:text-right shrink-0">
                  <span className="text-[10px] font-mono text-charcoal-500 uppercase block mb-1">
                    Modern Complement:
                  </span>
                  <div className="flex flex-wrap gap-1 sm:justify-end">
                    {obs.recommendedSkills.map((rec, i) => (
                      <span key={i} className="px-2 py-0.5 bg-white border border-paper-border text-forest-900 text-[10px] font-mono rounded">
                        {rec}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-paper rounded text-center text-xs text-charcoal-500">
            All registered skills are currently aligned with active industry standards.
          </div>
        )}
      </div>
    </div>
  );
};
