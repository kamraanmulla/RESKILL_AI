import React, { useState } from 'react';
import {
  X,
  Lock,
  Mail,
  User,
  GraduationCap,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { AuthUser } from '../../types';
import { api } from '../../services/api';


interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: AuthUser) => void;
  initialMode?: 'signin' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onLoginSuccess,
  initialMode = 'signin'
}) => {
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [academicLevel, setAcademicLevel] = useState('Final Year B.Tech');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) {
      setError('Please fill in both email and password.');
      return;
    }

    setLoading(true);
    try {
      const user = await api.login(email, password);
      onLoginSuccess(user);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!name || !email || !password) {
      setError('Please provide your name, email, and password.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);
    try {
      const user = await api.signup(name, email, academicLevel);
      onLoginSuccess(user);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = await api.login('parvez.ahmed@apex.edu.in', 'demo123');
      onLoginSuccess(user);
      onClose();
    } catch {
      setError('Could not initialize demo profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestEntry = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = await api.signup('Guest Candidate', 'guest@reskill.ai', 'Prospective Candidate');
      onLoginSuccess(user);
      onClose();
    } catch {
      setError('Could not initialize guest session.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="bg-white border border-paper-border rounded-lg shadow-modal w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
      >
        {/* Top Decorative Header */}
        <div className="p-6 pb-5 bg-paper border-b border-paper-border relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-sm text-charcoal-400 hover:text-charcoal-700 hover:bg-paper-muted transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-7 h-7 rounded-sm bg-forest-800 text-white font-serif font-bold text-sm flex items-center justify-center shadow-subtle">
              R
            </div>
            <span className="font-serif font-semibold text-charcoal-900 tracking-tight">
              ReSkill<span className="text-forest-700 font-sans font-normal text-xs ml-0.5">.AI</span>
            </span>
          </div>

          <h2 className="font-serif text-2xl font-medium text-charcoal-900">
            {mode === 'signin' ? 'Sign in to your dossier' : 'Create candidate account'}
          </h2>
          <p className="text-xs text-charcoal-600 mt-1">
            {mode === 'signin'
              ? 'Access your personalized learning roadmap and career readiness benchmarks.'
              : 'Start fresh with a zero-knowledge profile calibrated to your pace.'}
          </p>

          {/* Mode Switcher Tabs */}
          <div className="flex border-b border-paper-border mt-5 -mb-5">
            <button
              onClick={() => {
                setMode('signin');
                setError(null);
              }}
              className={`flex-1 py-2.5 text-xs font-medium text-center border-b-2 transition-all ${
                mode === 'signin'
                  ? 'border-forest-800 text-forest-900 font-semibold'
                  : 'border-transparent text-charcoal-500 hover:text-charcoal-800'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => {
                setMode('signup');
                setError(null);
              }}
              className={`flex-1 py-2.5 text-xs font-medium text-center border-b-2 transition-all ${
                mode === 'signup'
                  ? 'border-forest-800 text-forest-900 font-semibold'
                  : 'border-transparent text-charcoal-500 hover:text-charcoal-800'
              }`}
            >
              Create Account (Fresh Start)
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {error && (
            <div className="p-3 bg-editorial-rustLight/60 border border-editorial-rust/30 text-editorial-rust text-xs rounded-sm">
              {error}
            </div>
          )}

          {mode === 'signin' ? (
            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Academic / Personal Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student@university.edu"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-charcoal-600">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="rounded text-forest-800 focus:ring-forest-800 border-paper-border"
                  />
                  <span>Remember session</span>
                </label>
                <a href="#reset" onClick={(e) => { e.preventDefault(); alert('Demo environment: Please sign in or use Demo Login.'); }} className="text-forest-800 hover:underline">
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignUp} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Alex Rivera"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Academic Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="alex@college.edu"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Current Academic Status
                </label>
                <div className="relative">
                  <GraduationCap className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <select
                    value={academicLevel}
                    onChange={(e) => setAcademicLevel(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  >
                    <option value="Final Year B.Tech">Final Year Undergrad (2026)</option>
                    <option value="Pre-Final Year">Pre-Final Year Undergrad (2027)</option>
                    <option value="Recent Graduate">Recent Graduate</option>
                    <option value="Self-Taught Engineer">Self-Taught / Career Transitioner</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Create Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <div className="p-3 bg-forest-50 border border-forest-200 rounded-sm text-[11px] text-forest-900 flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
                <p>
                  <strong>Zero-Knowledge Initial State:</strong> Your profile starts with 0 assumptions. You can upload your resume or enter skills anytime to calibrate.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <span>{loading ? 'Registering...' : 'Create Account & Begin'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>
          )}

          {/* Quick Demo & Guest Actions */}
          <div className="pt-3 border-t border-paper-border space-y-2">
            <div className="flex items-center justify-between text-[11px] text-charcoal-500 font-mono">
              <span>Quick Access For Testing:</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleDemoLogin}
                className="py-2 px-3 bg-paper hover:bg-paper-dark border border-paper-border text-charcoal-800 text-xs font-medium rounded-sm transition-colors flex items-center justify-center gap-1.5"
                title="Loads full sample student profile (Parvez Ahmed)"
              >
                <Sparkles className="w-3.5 h-3.5 text-forest-800" />
                <span>Demo Profile</span>
              </button>

              <button
                type="button"
                onClick={handleGuestEntry}
                className="py-2 px-3 bg-paper hover:bg-paper-dark border border-paper-border text-charcoal-800 text-xs font-medium rounded-sm transition-colors flex items-center justify-center gap-1.5"
                title="Enters platform in zero-knowledge mode"
              >
                <UserCheck className="w-3.5 h-3.5 text-charcoal-600" />
                <span>Zero-Knowledge Guest</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
