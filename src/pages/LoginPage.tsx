import React, { useState } from 'react';
import {
  Lock,
  Mail,
  User,
  GraduationCap,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { AuthUser } from '../types';
import { api } from '../services/api';

interface LoginPageProps {
  onLoginSuccess: (user: AuthUser) => void;
  onExploreLanding: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLoginSuccess,
  onExploreLanding
}) => {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [academicLevel, setAcademicLevel] = useState('Final Year B.Tech');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
      const user = await api.signup('New Candidate', 'candidate@reskill.ai', 'Prospective Candidate');
      onLoginSuccess(user);
    } catch {
      setError('Could not initialize fresh session.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper flex flex-col justify-center items-center p-4 sm:p-6 antialiased">
      <div className="w-full max-w-md bg-white border border-paper-border rounded-lg shadow-modal overflow-hidden animate-fade-in">
        {/* Top Branding & Mode Header */}
        <div className="p-6 pb-5 bg-paper border-b border-paper-border">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-sm bg-forest-800 text-white font-serif font-bold text-base flex items-center justify-center shadow-subtle">
              R
            </div>
            <div>
              <span className="font-serif font-semibold text-lg text-charcoal-900 tracking-tight leading-none block">
                ReSkill<span className="text-forest-700 font-sans font-normal text-xs ml-0.5">.AI</span>
              </span>
              <span className="text-[10px] text-charcoal-500 uppercase tracking-widest font-mono block mt-0.5">
                Career Intelligence Platform
              </span>
            </div>
          </div>

          <h2 className="font-serif text-2xl font-medium text-charcoal-900">
            {mode === 'signin' ? 'Sign in to your dossier' : 'Create candidate account'}
          </h2>
          <p className="text-xs text-charcoal-600 mt-1 leading-relaxed">
            {mode === 'signin'
              ? 'Enter your credentials to load your calibrated career readiness benchmarks.'
              : 'Start fresh with a zero-knowledge profile calibrated purely from your inputs.'}
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

        {/* Form Body */}
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
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="candidate@university.edu"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs font-mono text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
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
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs font-mono text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
              >
                {loading ? (
                  <span>Signing In...</span>
                ) : (
                  <>
                    <span>Sign In to Dossier</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignUp} className="space-y-3.5">
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
                    placeholder="Your Name"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
                  />
                </div>
              </div>

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
                    placeholder="name@institution.edu"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs font-mono text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-charcoal-600 mb-1.5">
                  Degree / Academic Stage
                </label>
                <div className="relative">
                  <GraduationCap className="w-4 h-4 absolute left-3 top-2.5 text-charcoal-400" />
                  <select
                    value={academicLevel}
                    onChange={(e) => setAcademicLevel(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs text-charcoal-900 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
                  >
                    <option value="Final Year B.Tech">Final Year B.Tech / B.E.</option>
                    <option value="Third Year B.Tech">Third Year B.Tech</option>
                    <option value="Second Year B.Tech">Second Year B.Tech</option>
                    <option value="BCA / MCA">BCA / MCA</option>
                    <option value="Recent Graduate">Recent Graduate</option>
                    <option value="Career Transitioner">Career Transitioner</option>
                  </select>
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
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    className="w-full pl-9 pr-3 py-2 bg-paper border border-paper-border rounded-sm text-xs font-mono text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:border-forest-800 focus:bg-white transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-all flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
              >
                {loading ? (
                  <span>Initializing Fresh Profile...</span>
                ) : (
                  <>
                    <span>Create Fresh Dossier (Zero Knowledge)</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* Testing / Quick Access Bar */}
          <div className="pt-4 border-t border-paper-border space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-charcoal-500 uppercase tracking-wider">
                Evaluation & Testing
              </span>
              <button
                type="button"
                onClick={onExploreLanding}
                className="text-[11px] text-forest-800 hover:underline"
              >
                View Public Landing →
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleGuestEntry}
                disabled={loading}
                className="py-2 px-2.5 bg-paper hover:bg-paper-muted border border-paper-border rounded-sm text-[11px] text-charcoal-800 font-medium transition-colors flex items-center justify-center gap-1.5"
              >
                <UserCheck className="w-3.5 h-3.5 text-charcoal-600" />
                <span>Instant Fresh Start</span>
              </button>

              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={loading}
                className="py-2 px-2.5 bg-white hover:bg-forest-50 border border-forest-800/30 rounded-sm text-[11px] text-forest-900 font-medium transition-colors flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-forest-700" />
                <span>Demo Student</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
