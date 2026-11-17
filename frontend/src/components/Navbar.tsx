import React from 'react';
import { Employee } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: Employee | null;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, user, onLogout }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'onboarding', label: 'Onboarding' },
    { id: 'directory', label: 'Directory' },
    { id: 'policies', label: 'Policy AI Assistant' },
    { id: 'leave', label: 'Leave & PTO' },
    { id: 'performance', label: 'Performance & OKRs' },
  ];

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
              HR
            </div>
            <span className="font-bold text-lg text-white tracking-wide">ai-hr-platform</span>
          </div>

          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === item.id
                    ? 'bg-indigo-600 text-white shadow'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-3 text-right">
                <div>
                  <div className="text-sm font-semibold text-white">
                    {user.first_name} {user.last_name}
                  </div>
                  <div className="text-xs text-indigo-400 font-mono">{user.role}</div>
                </div>
                <button
                  onClick={onLogout}
                  className="px-3 py-1 text-xs font-medium text-slate-300 bg-slate-700 hover:bg-red-600/80 hover:text-white rounded border border-slate-600 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
