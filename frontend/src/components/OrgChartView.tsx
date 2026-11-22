import React, { useState, useEffect } from 'react';
import { OrgChartNode, OrgChartStats } from '../types';
import { api } from '../services/api';

export const OrgChartView: React.FC = () => {
  const [tree, setTree] = useState<OrgChartNode[]>([]);
  const [stats, setStats] = useState<OrgChartStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [collapsedNodes, setCollapsedNodes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadOrgChart();
  }, []);

  const loadOrgChart = async () => {
    try {
      setLoading(true);
      const [chartRes, statsRes] = await Promise.allSettled([
        api.getOrgChart(),
        api.getOrgChartStats(),
      ]);

      if (chartRes.status === 'fulfilled' && chartRes.value.length > 0) {
        setTree(chartRes.value);
      } else {
        // Fallback demo hierarchy
        setTree([
          {
            id: 'node-ceo',
            name: 'David Vance',
            email: 'david.vance@acme.corp',
            job_title: 'Chief Executive Officer',
            department: 'Executive',
            direct_reports: [
              {
                id: 'node-mgr-sarah',
                name: 'Sarah Jenkins',
                email: 'manager.sarah@acme.corp',
                job_title: 'Director of Engineering',
                department: 'Engineering',
                direct_reports: [
                  {
                    id: 'node-eng-alex',
                    name: 'Alex Chen',
                    email: 'engineer.alex@acme.corp',
                    job_title: 'Senior Software Engineer',
                    department: 'Engineering',
                    direct_reports: [],
                  },
                  {
                    id: 'node-eng-elena',
                    name: 'Elena Rostova',
                    email: 'elena.rostova@internal.dev',
                    job_title: 'Senior Distributed Systems Engineer',
                    department: 'Engineering',
                    direct_reports: [],
                  },
                  {
                    id: 'node-eng-marcus',
                    name: 'Marcus Bell',
                    email: 'marcus.bell@acme.corp',
                    job_title: 'DevOps / SRE Engineer',
                    department: 'Engineering',
                    direct_reports: [],
                  },
                ],
              },
              {
                id: 'node-hr-admin',
                name: 'Rachel Adams',
                email: 'admin@acme.corp',
                job_title: 'VP of People & Culture',
                department: 'People Operations',
                direct_reports: [
                  {
                    id: 'node-hr-rep',
                    name: 'Michael Scott',
                    email: 'michael.scott@acme.corp',
                    job_title: 'People Operations Generalist',
                    department: 'People Operations',
                    direct_reports: [],
                  },
                ],
              },
            ],
          },
        ]);
      }

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value);
      } else {
        setStats({
          total_active_employees: 6,
          total_people_managers: 2,
          average_span_of_control: 2.5,
          overloaded_managers_count: 0,
          overloaded_managers: [],
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleCollapse = (nodeId: string) => {
    setCollapsedNodes((prev) => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  const renderNode = (node: OrgChartNode, depth: number = 0) => {
    const isCollapsed = collapsedNodes[node.id];
    const hasReports = node.direct_reports && node.direct_reports.length > 0;
    const isOverloaded = node.direct_reports && node.direct_reports.length > 8;

    return (
      <div key={node.id} className="flex flex-col items-center">
        {/* Card */}
        <div
          className={`relative bg-slate-800 border rounded-xl p-4 shadow-xl transition-all duration-200 w-64 ${
            depth === 0
              ? 'border-indigo-500/80 bg-gradient-to-b from-indigo-950/40 to-slate-800'
              : isOverloaded
              ? 'border-amber-500/80'
              : 'border-slate-700 hover:border-slate-500'
          }`}
        >
          <div className="flex justify-between items-start">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-indigo-400 border border-slate-700">
              {node.department}
            </span>
            {hasReports && (
              <span className="text-[10px] font-semibold text-slate-400">
                {node.direct_reports.length} Reports
              </span>
            )}
          </div>

          <div className="mt-2.5">
            <h5 className="font-bold text-sm text-white truncate">{node.name}</h5>
            <p className="text-xs text-indigo-300 font-medium truncate mt-0.5">{node.job_title}</p>
            <p className="text-[11px] text-slate-500 truncate mt-0.5">{node.email}</p>
          </div>

          {hasReports && (
            <button
              onClick={() => toggleCollapse(node.id)}
              className="mt-3 w-full py-1 text-[11px] font-semibold rounded bg-slate-900/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
            >
              {isCollapsed ? `▼ Expand (${node.direct_reports.length})` : '▲ Collapse'}
            </button>
          )}
        </div>

        {/* Children connector */}
        {hasReports && !isCollapsed && (
          <div className="flex flex-col items-center">
            {/* Vertical stem */}
            <div className="w-0.5 h-6 bg-slate-700" />

            {/* Horizontal bar if multiple children */}
            <div className="relative flex justify-center gap-6 pt-2">
              {node.direct_reports.map((child) => renderNode(child, depth + 1))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Top Banner: Span of Control Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Headcount</div>
          <div className="text-2xl font-bold text-white mt-1">
            {stats?.total_active_employees || 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">Full-time employees & contractors</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">People Managers</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            {stats?.total_people_managers || 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">With active direct reports</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Span of Control</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {stats?.average_span_of_control || 0} <span className="text-xs font-normal text-slate-400">reports/mgr</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Optimal target: 4.0 - 7.0</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overloaded Managers</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {stats?.overloaded_managers_count || 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">&gt; 8 Direct reports threshold</div>
        </div>
      </div>

      {/* Org Chart Visual Canvas */}
      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-8 shadow-2xl overflow-x-auto min-h-[500px]">
        <div className="text-center mb-6">
          <h3 className="text-lg font-bold text-white">Organizational Reporting Hierarchy</h3>
          <p className="text-xs text-slate-400">Interactive recursive tree mapping reporting structures across all departments</p>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs">
            Assembling organizational hierarchy...
          </div>
        ) : tree.length === 0 ? (
          <div className="py-16 text-center text-slate-400 text-xs">
            No organizational nodes found.
          </div>
        ) : (
          <div className="flex justify-center gap-12 py-4">
            {tree.map((root) => renderNode(root, 0))}
          </div>
        )}
      </div>
    </div>
  );
};
