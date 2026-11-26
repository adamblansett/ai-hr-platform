import React, { useState, useMemo } from 'react';
import {
  Bell,
  Briefcase,
  ChevronDown,
  ChevronRight,
  DollarSign,
  Globe,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Shield,
  Users,
  X,
} from 'lucide-react';
import { Employee } from '../types';

interface NavGroup {
  id: string;
  label: string;
  icon: React.ReactNode;
  items: { id: string; label: string; badge?: string }[];
}

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: Employee | null;
  onLogout: () => void;
  unreadNotifications?: number;
}

const NAV_GROUPS: NavGroup[] = [
  {
    id: 'core',
    label: 'Core HR',
    icon: <Users className="w-4 h-4 text-indigo-400" />,
    items: [
      { id: 'dashboard', label: 'Dashboard' },
      { id: 'orgchart', label: 'Org Chart' },
      { id: 'directory', label: 'Directory' },
      { id: 'onboarding', label: 'Onboarding' },
      { id: 'offboarding', label: 'Offboarding' },
      { id: 'leave', label: 'Leave & PTO' },
      { id: 'attendance', label: 'Attendance & Hours' },
    ],
  },
  {
    id: 'comp',
    label: 'Comp & Benefits',
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
    items: [
      { id: 'compensation', label: 'Compensation & Equity' },
      { id: 'benchmarking', label: 'Salary Benchmarks' },
      { id: 'benefits', label: 'Benefits & Health' },
      { id: 'expenses', label: 'Expenses & Audit' },
    ],
  },
  {
    id: 'talent',
    label: 'Talent & Growth',
    icon: <Briefcase className="w-4 h-4 text-amber-400" />,
    items: [
      { id: 'workforce', label: 'Workforce Planning', badge: 'NEW' },
      { id: 'coaching', label: '1:1 Coaching' },
      { id: 'pulse', label: 'Pulse & Sentiment' },
      { id: 'recognition', label: 'Kudos & Rewards' },
      { id: 'learning', label: 'L&D & Compliance' },
      { id: 'performance', label: 'Performance & OKRs' },
    ],
  },
  {
    id: 'ops',
    label: 'Operations & Global',
    icon: <Globe className="w-4 h-4 text-cyan-400" />,
    items: [
      { id: 'assets', label: 'IT Hardware Fleet' },
      { id: 'contractors', label: 'Global EOR & Vendors' },
      { id: 'immigration', label: 'Visa & Relocation' },
      { id: 'localization', label: 'Global & Holidays' },
      { id: 'safety', label: 'Safety & OSHA' },
    ],
  },
  {
    id: 'admin',
    label: 'Security & Admin',
    icon: <Shield className="w-4 h-4 text-rose-400" />,
    items: [
      { id: 'policies', label: 'Policy AI' },
      { id: 'notifications', label: 'Notifications', badge: 'NEW' },
      { id: 'security', label: 'SSO & MFA Security', badge: 'NEW' },
      { id: 'compliance', label: 'Compliance & SOC 2' },
      { id: 'branding', label: 'White-Label & Domain' },
      { id: 'integrations', label: 'Integrations' },
    ],
  },
];

export const TopBar: React.FC<{
  user: Employee | null;
  onLogout: () => void;
  onOpenMobileMenu: () => void;
  unreadNotifications?: number;
  onNavigateNotifications: () => void;
}> = ({ user, onLogout, onOpenMobileMenu, unreadNotifications = 0, onNavigateNotifications }) => {
  return (
    <header className="bg-slate-800/95 backdrop-blur border-b border-slate-700 sticky top-0 z-30 h-14 px-4 sm:px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 lg:hidden">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-xs text-white">
            HR
          </div>
          <span className="font-bold text-sm text-white">ai-hr-platform</span>
        </div>
        <span className="hidden lg:inline-block text-xs font-mono text-slate-400">
          v2.1.0 Enterprise Edition
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onNavigateNotifications}
          className="relative p-2 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          {unreadNotifications > 0 && (
            <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-indigo-500 text-white text-[10px] font-bold flex items-center justify-center">
              {unreadNotifications}
            </span>
          )}
        </button>

        {user && (
          <div className="flex items-center gap-3">
            <div className="hidden sm:block text-right">
              <div className="text-xs font-semibold text-white leading-tight">
                {user.first_name} {user.last_name}
              </div>
              <div className="text-[11px] text-indigo-400 font-mono leading-tight">{user.role}</div>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700 hover:bg-red-600/80 hover:text-white rounded-lg border border-slate-600 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export const Navbar: React.FC<
  NavbarProps & {
    collapsed?: boolean;
    onToggleCollapse?: () => void;
    mobileOpen?: boolean;
    onCloseMobile?: () => void;
  }
> = ({
  activeTab,
  setActiveTab,
  unreadNotifications = 0,
  collapsed = false,
  onToggleCollapse,
  mobileOpen = false,
  onCloseMobile,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    core: true,
    comp: true,
    talent: true,
    ops: true,
    admin: true,
  });

  const toggleGroup = (id: string) => {
    setOpenGroups((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredGroups = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return NAV_GROUPS;
    return NAV_GROUPS.map((group) => ({
      ...group,
      items: group.items.filter((item) => item.label.toLowerCase().includes(q)),
    })).filter((group) => group.items.length > 0);
  }, [searchQuery]);

  const handleSelect = (id: string) => {
    setActiveTab(id);
    onCloseMobile?.();
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      <div className="h-14 px-4 flex items-center justify-between border-b border-slate-800 shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-600/30 text-sm">
              HR
            </div>
            <span className="font-bold text-sm text-white tracking-wide">ai-hr-platform</span>
          </div>
        )}
        <button
          type="button"
          onClick={onToggleCollapse}
          className="hidden lg:inline-flex p-1.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
        </button>
        <button
          type="button"
          onClick={onCloseMobile}
          className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {!collapsed && (
        <div className="p-3 border-b border-slate-800/80 shrink-0">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Jump to module..."
              className="w-full bg-slate-800/70 border border-slate-700/80 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-2.5 py-3 space-y-3">
        {filteredGroups.map((group) => {
          const isOpen = searchQuery.trim().length > 0 || openGroups[group.id];
          return (
            <div key={group.id}>
              {!collapsed ? (
                <button
                  type="button"
                  onClick={() => toggleGroup(group.id)}
                  className="w-full flex items-center justify-between px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 hover:text-slate-200"
                >
                  <span className="flex items-center gap-2">
                    {group.icon}
                    {group.label}
                  </span>
                  {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                </button>
              ) : (
                <div className="flex justify-center py-1.5 border-t border-slate-800/60" title={group.label}>
                  {group.icon}
                </div>
              )}

              {(isOpen || collapsed) && (
                <div className="mt-1 space-y-0.5">
                  {group.items.map((item) => {
                    const active = activeTab === item.id;
                    const countBadge =
                      item.id === 'notifications' && unreadNotifications > 0
                        ? String(unreadNotifications)
                        : item.badge;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => handleSelect(item.id)}
                        title={item.label}
                        className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          active
                            ? 'bg-indigo-600 text-white shadow-sm'
                            : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                        }`}
                      >
                        <span className={collapsed ? 'truncate w-full text-center' : 'truncate'}>
                          {collapsed ? item.label.slice(0, 2).toUpperCase() : item.label}
                        </span>
                        {!collapsed && countBadge && (
                          <span
                            className={`ml-2 px-1.5 py-0.5 text-[10px] font-mono rounded ${
                              active ? 'bg-indigo-500 text-white' : 'bg-indigo-500/20 text-indigo-300'
                            }`}
                          >
                            {countBadge}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      <aside
        className={`hidden lg:block shrink-0 transition-all duration-200 ${
          collapsed ? 'w-16' : 'w-64'
        }`}
      >
        <div className="sticky top-0 h-screen">{sidebarContent}</div>
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="fixed inset-0 bg-black/60" onClick={onCloseMobile} />
          <div className="relative w-64 max-w-[80vw] h-full z-10">{sidebarContent}</div>
        </div>
      )}
    </>
  );
};
