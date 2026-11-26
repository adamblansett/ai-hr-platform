import React, { Suspense, lazy, useState, useEffect, useCallback } from 'react';
import { Navbar, TopBar } from './components/Navbar';
import { useRoute } from './hooks/useRoute';
import { Employee } from './types';
import { api } from './services/api';

const OnboardingView = lazy(() =>
  import('./components/OnboardingView').then((m) => ({ default: m.OnboardingView }))
);
const DirectoryView = lazy(() =>
  import('./components/DirectoryView').then((m) => ({ default: m.DirectoryView }))
);
const PolicyAssistantView = lazy(() =>
  import('./components/PolicyAssistantView').then((m) => ({ default: m.PolicyAssistantView }))
);
const LeaveManagementView = lazy(() =>
  import('./components/LeaveManagementView').then((m) => ({ default: m.LeaveManagementView }))
);
const CompensationView = lazy(() =>
  import('./components/CompensationView').then((m) => ({ default: m.CompensationView }))
);
const LocalizationView = lazy(() =>
  import('./components/LocalizationView').then((m) => ({ default: m.LocalizationView }))
);
const ComplianceView = lazy(() =>
  import('./components/ComplianceView').then((m) => ({ default: m.ComplianceView }))
);
const IntegrationsView = lazy(() =>
  import('./components/IntegrationsView').then((m) => ({ default: m.IntegrationsView }))
);
const OffboardingView = lazy(() =>
  import('./components/OffboardingView').then((m) => ({ default: m.OffboardingView }))
);
const OrgChartView = lazy(() =>
  import('./components/OrgChartView').then((m) => ({ default: m.OrgChartView }))
);
const CoachingCalibrationView = lazy(() =>
  import('./components/CoachingCalibrationView').then((m) => ({ default: m.CoachingCalibrationView }))
);
const PulseSentimentView = lazy(() =>
  import('./components/PulseSentimentView').then((m) => ({ default: m.PulseSentimentView }))
);
const BenefitsEnrollmentView = lazy(() =>
  import('./components/BenefitsEnrollmentView').then((m) => ({ default: m.BenefitsEnrollmentView }))
);
const TimeAttendanceView = lazy(() =>
  import('./components/TimeAttendanceView').then((m) => ({ default: m.TimeAttendanceView }))
);
const ExpenseAuditView = lazy(() =>
  import('./components/ExpenseAuditView').then((m) => ({ default: m.ExpenseAuditView }))
);
const SafetyComplianceView = lazy(() =>
  import('./components/SafetyComplianceView').then((m) => ({ default: m.SafetyComplianceView }))
);
const RewardsRecognitionView = lazy(() =>
  import('./components/RewardsRecognitionView').then((m) => ({ default: m.RewardsRecognitionView }))
);
const LearningDevelopmentView = lazy(() =>
  import('./components/LearningDevelopmentView').then((m) => ({ default: m.LearningDevelopmentView }))
);
const AssetFleetView = lazy(() =>
  import('./components/AssetFleetView').then((m) => ({ default: m.AssetFleetView }))
);
const ContractorEorView = lazy(() =>
  import('./components/ContractorEorView').then((m) => ({ default: m.ContractorEorView }))
);
const SalaryBenchmarkingView = lazy(() =>
  import('./components/SalaryBenchmarkingView').then((m) => ({ default: m.SalaryBenchmarkingView }))
);
const ImmigrationRelocationView = lazy(() =>
  import('./components/ImmigrationRelocationView').then((m) => ({ default: m.ImmigrationRelocationView }))
);
const TenantBrandingView = lazy(() =>
  import('./components/TenantBrandingView').then((m) => ({ default: m.TenantBrandingView }))
);
const SecuritySsoMfaView = lazy(() =>
  import('./components/SecuritySsoMfaView').then((m) => ({ default: m.SecuritySsoMfaView }))
);
const NotificationsCenterView = lazy(() =>
  import('./components/NotificationsCenterView').then((m) => ({ default: m.NotificationsCenterView }))
);
const WorkforcePlanningView = lazy(() =>
  import('./components/WorkforcePlanningView').then((m) => ({ default: m.WorkforcePlanningView }))
);

const ViewFallback: React.FC = () => (
  <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-10 text-center text-slate-400 text-sm">
    Loading module...
  </div>
);

export const App: React.FC = () => {
  const [user, setUser] = useState<Employee | null>(null);
  const { activeRoute, navigate } = useRoute();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  const refreshUnreadCount = useCallback(async () => {
    try {
      const res = await api.getUnreadNotificationCount('emp-001');
      setUnreadCount(res.unread_count);
    } catch {
      // Non-fatal in background poll
    }
  }, []);

  useEffect(() => {
    if (api.getToken()) {
      api
        .getMe()
        .then((u) => {
          setUser(u);
          refreshUnreadCount();
        })
        .catch(() => api.setToken(''));
    }
  }, [refreshUnreadCount]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoginLoading(true);
      await api.login(email, password);
      const currentUser = await api.getMe();
      setUser(currentUser);
      await refreshUnreadCount();
    } catch (err: any) {
      alert(err.message || 'Login failed');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    navigate('dashboard');
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Navbar
        activeTab={activeRoute}
        setActiveTab={navigate}
        user={user}
        onLogout={handleLogout}
        unreadNotifications={unreadCount}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((c) => !c)}
        mobileOpen={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <TopBar
          user={user}
          onLogout={handleLogout}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          unreadNotifications={unreadCount}
          onNavigateNotifications={() => navigate('notifications')}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
          <Suspense fallback={<ViewFallback />}>
            {activeRoute === 'dashboard' && (
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-indigo-900/60 to-purple-900/40 border border-indigo-500/20 rounded-2xl p-6 sm:p-8">
                  <h2 className="text-2xl font-bold text-white">Welcome back, {user.first_name}!</h2>
                  <p className="text-indigo-200/80 text-sm mt-1">
                    Role: <span className="font-mono text-white">{user.role}</span> | Department:{' '}
                    <span className="text-white">{user.department}</span>
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <OnboardingView />
                  <LeaveManagementView />
                </div>
              </div>
            )}

            {activeRoute === 'orgchart' && <OrgChartView />}
            {activeRoute === 'directory' && <DirectoryView />}
            {activeRoute === 'onboarding' && <OnboardingView />}
            {activeRoute === 'offboarding' && <OffboardingView />}
            {activeRoute === 'attendance' && <TimeAttendanceView />}
            {activeRoute === 'expenses' && <ExpenseAuditView />}
            {activeRoute === 'safety' && <SafetyComplianceView />}
            {activeRoute === 'recognition' && <RewardsRecognitionView />}
            {activeRoute === 'learning' && <LearningDevelopmentView />}
            {activeRoute === 'assets' && <AssetFleetView />}
            {activeRoute === 'contractors' && <ContractorEorView />}
            {activeRoute === 'leave' && <LeaveManagementView />}
            {activeRoute === 'compensation' && <CompensationView />}
            {activeRoute === 'benchmarking' && <SalaryBenchmarkingView />}
            {activeRoute === 'immigration' && <ImmigrationRelocationView />}
            {activeRoute === 'branding' && <TenantBrandingView />}
            {activeRoute === 'benefits' && <BenefitsEnrollmentView />}
            {activeRoute === 'pulse' && <PulseSentimentView />}
            {activeRoute === 'coaching' && <CoachingCalibrationView />}
            {activeRoute === 'localization' && <LocalizationView />}
            {activeRoute === 'policies' && <PolicyAssistantView />}
            {activeRoute === 'compliance' && <ComplianceView />}
            {activeRoute === 'integrations' && <IntegrationsView />}
            {activeRoute === 'security' && <SecuritySsoMfaView />}
            {activeRoute === 'notifications' && (
              <NotificationsCenterView onCountChange={refreshUnreadCount} />
            )}
            {activeRoute === 'workforce' && <WorkforcePlanningView />}
            {activeRoute === 'performance' && (
              <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center space-y-3">
                <h3 className="text-lg font-bold text-white">Continuous Performance & 360 Reviews</h3>
                <p className="text-slate-400 text-sm max-w-md mx-auto">
                  Quarterly OKR tracking and AI-synthesized peer review feedback cycles.
                </p>
              </div>
            )}
          </Suspense>
        </main>
      </div>
    </div>
  );
};

export default App;
