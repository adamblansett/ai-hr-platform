import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OnboardingView } from './components/OnboardingView';
import { DirectoryView } from './components/DirectoryView';
import { PolicyAssistantView } from './components/PolicyAssistantView';
import { LeaveManagementView } from './components/LeaveManagementView';
import { CompensationView } from './components/CompensationView';
import { LocalizationView } from './components/LocalizationView';
import { ComplianceView } from './components/ComplianceView';
import { Employee } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [user, setUser] = useState<Employee | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    // Check if token already exists
    if (api.getToken()) {
      api.getMe()
        .then(setUser)
        .catch(() => api.setToken(''));
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoginLoading(true);
      await api.login(email, password);
      const currentUser = await api.getMe();
      setUser(currentUser);
    } catch (err: any) {
      alert(err.message || 'Login failed');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('ai_hr_token');
    window.location.reload();
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-6">
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-indigo-600 rounded-xl mx-auto flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-600/30">
              HR
            </div>
            <h1 className="text-2xl font-bold text-white">ai-hr-platform</h1>
            <p className="text-slate-400 text-xs">
              Automated Employee Lifecycle & AI Operations Microservice
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="elena.rostova@internal.dev"
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              type="submit"
              disabled={loginLoading}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg transition-colors shadow-lg shadow-indigo-600/30"
            >
              {loginLoading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-indigo-900/60 to-purple-900/40 border border-indigo-500/20 rounded-2xl p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-white">Welcome back, {user.first_name}!</h2>
              <p className="text-indigo-200/80 text-sm mt-1">
                Role: <span className="font-mono text-white">{user.role}</span> | Department: <span className="text-white">{user.department}</span>
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <OnboardingView />
              <LeaveManagementView />
            </div>
          </div>
        )}

        {activeTab === 'onboarding' && <OnboardingView />}
        {activeTab === 'directory' && <DirectoryView />}
        {activeTab === 'policies' && <PolicyAssistantView />}
        {activeTab === 'leave' && <LeaveManagementView />}
        {activeTab === 'compensation' && <CompensationView />}
        {activeTab === 'localization' && <LocalizationView />}
        {activeTab === 'compliance' && <ComplianceView />}
        {activeTab === 'performance' && (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center space-y-3">
            <h3 className="text-lg font-bold text-white">Continuous Performance & 360 Reviews</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Quarterly OKR tracking and AI-synthesized peer review feedback cycles.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
