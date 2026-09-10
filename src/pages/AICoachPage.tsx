import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Loader2,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { CoachChatMessage, StudentProfile, CareerRole } from '../types';
import { api } from '../services/api';

interface AICoachPageProps {
  student: StudentProfile;
  targetCareer: CareerRole;
  onNavigateToSkillGap?: () => void;
  onNavigateToRoadmap?: () => void;
}

const SUGGESTED_QUESTIONS = [
  'Why is this career suitable for my current background?',
  'What should I learn next to increase my readiness points?',
  'Which of my skills are transferable to other domains?',
  'What hidden competencies do I already demonstrate?',
  'What specific project should I build for my portfolio?'
];

export const AICoachPage: React.FC<AICoachPageProps> = ({
  student,
  targetCareer,
  onNavigateToSkillGap,
  onNavigateToRoadmap
}) => {
  const [messages, setMessages] = useState<CoachChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello ${student.name || 'Candidate'}! I am your AI Career Coach for ReSkillAI. I have direct access to your verified canonical dossier—including your target role (${targetCareer.title}), current readiness score (${student.careerReadiness || 0}%), and identified skill gaps. How can I guide your trajectory today?`,
      timestamp: 'Just now'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query || loading) return;

    const userMsg: CoachChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);
    setError(null);

    // Build chat history for conversational context
    const historyPayload = messages.map((m) => ({
      role: m.role,
      content: m.content
    }));

    try {
      const response = await api.sendCareerCoachMessage(query, historyPayload);

      // Check if Gemini returned an error
      if (response.status === 'error' || (!response.response && response.error)) {
        setError(response.error || 'AI Career Coach encountered an error. Please try again.');
      } else {
        const assistantMsg: CoachChatMessage = {
          id: `assistant_${Date.now()}`,
          role: 'assistant',
          content: response.response,
          source: response.source,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (err: any) {
      setError(err?.message || 'Could not get guidance from the career coach at this time.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <SectionHeader
        title="AI Career Coach"
        subtitle="Conversational career navigation calibrated against your canonical dossier, readiness points, and skill gaps."
        badge="Gemini Contextual Intelligence"
      />

      {/* Dossier Context Summary Strip */}
      <div className="p-4 bg-white border border-paper-border rounded-md shadow-subtle flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded bg-forest-50 border border-forest-200 text-forest-800 flex items-center justify-center shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <span className="font-semibold text-charcoal-900 block">
              Active Context: {targetCareer.title}
            </span>
            <span className="text-[11px] font-mono text-charcoal-500">
              Readiness: {student.careerReadiness || 0}% • Skills: {student.skills?.length || 0} claimed
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          {onNavigateToSkillGap && (
            <button
              onClick={onNavigateToSkillGap}
              className="text-[11px] font-mono text-forest-800 hover:underline"
            >
              View Skill Gaps →
            </button>
          )}
          {onNavigateToRoadmap && (
            <button
              onClick={onNavigateToRoadmap}
              className="text-[11px] font-mono text-forest-800 hover:underline ml-2"
            >
              View Roadmap →
            </button>
          )}
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="bg-white border border-paper-border rounded-md shadow-subtle flex flex-col h-[520px] overflow-hidden">
        {/* Scrollable Message List */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
              >
                <div
                  className={`w-7 h-7 rounded-sm flex items-center justify-center shrink-0 text-xs ${
                    isUser
                      ? 'bg-charcoal-800 text-white'
                      : 'bg-forest-800 text-white font-serif font-bold'
                  }`}
                >
                  {isUser ? <User className="w-3.5 h-3.5" /> : 'R'}
                </div>

                <div
                  className={`max-w-[82%] rounded-md p-3.5 text-xs leading-relaxed space-y-1.5 ${
                    isUser
                      ? 'bg-charcoal-900 text-white shadow-subtle'
                      : 'bg-paper text-charcoal-800 border border-paper-border shadow-subtle'
                  }`}
                >
                  <div className="whitespace-pre-line">{msg.content}</div>
                  <div
                    className={`text-[10px] font-mono flex items-center justify-between gap-2 pt-1 border-t ${
                      isUser
                        ? 'border-charcoal-700/60 text-charcoal-300'
                        : 'border-paper-border text-charcoal-400'
                    }`}
                  >
                    <span>{msg.timestamp}</span>
                    {msg.source && (
                      <span className="text-[9px] uppercase tracking-wider">
                        {msg.source}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-sm bg-forest-800 text-white font-serif font-bold flex items-center justify-center shrink-0 text-xs">
                R
              </div>
              <div className="p-3.5 bg-paper rounded-md border border-paper-border text-xs text-charcoal-600 flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 text-forest-800 animate-spin" />
                <span>Consulting Gemini career intelligence...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-md text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-700" />
              <span>{error}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Quick Inquiries */}
        <div className="p-3 bg-paper-muted/60 border-t border-paper-border flex items-center gap-1.5 overflow-x-auto text-xs no-scrollbar">
          <span className="text-[11px] font-mono text-charcoal-400 shrink-0 mr-1">
            Quick Inquiries:
          </span>
          {SUGGESTED_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(q)}
              disabled={loading}
              className="px-2.5 py-1 bg-white hover:bg-forest-50 border border-paper-border hover:border-forest-800/40 text-charcoal-700 text-[11px] rounded shrink-0 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Text Input Area */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="p-3 bg-white border-t border-paper-border flex items-center gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask anything about your readiness, skill gaps, projects, or career transition..."
            disabled={loading}
            className="flex-1 px-3.5 py-2.5 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all font-sans"
          />

          <button
            type="submit"
            disabled={!inputText.trim() || loading}
            className="p-2.5 bg-forest-800 hover:bg-forest-900 text-white rounded-sm transition-colors disabled:opacity-40 shadow-subtle shrink-0"
            title="Send inquiry to Gemini Career Coach"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
