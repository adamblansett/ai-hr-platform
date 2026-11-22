import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SalaryBenchmark, DepartmentBenchmarkingSummary } from '../types';

export const SalaryBenchmarkingView: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<SalaryBenchmark[]>([]);
  const [auditSummary, setAuditSummary] = useState<DepartmentBenchmarkingSummary | null>(null);
  const [department, setDepartment] = useState<string>('Engineering');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [bmData, auditData] = await Promise.all([
        api.getSalaryBenchmarks(department),
        api.auditDepartmentCompensation(department),
      ]);
      setBenchmarks(bmData);
      setAuditSummary(auditData);
    } catch (err) {
      console.error('Failed to load compensation benchmarks', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [department]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>📊</span> AI Compensation Benchmarking & Market Salary Intelligence
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Real-time Radford / Option Impact market percentiles, geographic labor cost multipliers, and compa-ratio retention audits.
          </p>
        </div>

        {/* Department Switcher */}
        <div className="flex items-center gap-2">
          {['Engineering', 'DevOps'].map((dept) => (
            <button
              key={dept}
              onClick={() => setDepartment(dept)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                department === dept
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50'
              }`}
            >
              {dept}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Department Avg Compa-Ratio</div>
          <div className="mt-1 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {auditSummary ? `${(auditSummary.average_compa_ratio * 100).toFixed(1)}%` : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">100% = Exact Market Median (P50)</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Below P50 Median Count</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {auditSummary ? auditSummary.employees_below_p50_count : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Merit review candidates</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Budget Gap to P50</div>
          <div className="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            ${auditSummary ? auditSummary.total_budget_gap_to_p50.toLocaleString() : '0'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Required annual pool adjustment</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Market Data Freshness</div>
          <div className="mt-1 text-2xl font-bold text-green-500">Q4 2026</div>
          <div className="mt-1 text-xs text-gray-400">Radford / Option Impact verified</div>
        </div>
      </div>

      {/* Employee Compensation Audit Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Active Employee Compa-Ratio & Pay Parity Audit</h3>
          <span className="text-xs text-gray-500">{auditSummary?.audits.length || 0} Employees</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Calculating compensation parity...</div>
        ) : !auditSummary || auditSummary.audits.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No active employees found for this department.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Employee & Title</th>
                  <th className="px-6 py-3">Level & Geo Zone</th>
                  <th className="px-6 py-3">Current Base</th>
                  <th className="px-6 py-3">Market P50</th>
                  <th className="px-6 py-3">Compa-Ratio</th>
                  <th className="px-6 py-3">Band Position</th>
                  <th className="px-6 py-3">Suggested Merit</th>
                  <th className="px-6 py-3 text-right">Flight Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {auditSummary.audits.map((a) => (
                  <tr key={a.employee_id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900 dark:text-white">{a.employee_name}</div>
                      <div className="text-xs text-gray-400">{a.job_title}</div>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <div className="font-bold text-gray-900 dark:text-white">{a.job_level}</div>
                      <div className="text-gray-400">{a.geo_zone.replace(/_/g, ' ')}</div>
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-gray-900 dark:text-white">
                      ${a.current_base_salary.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 font-mono text-gray-500">
                      ${a.market_p50.toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`font-mono font-bold text-xs ${
                          a.compa_ratio < 0.9
                            ? 'text-red-500'
                            : a.compa_ratio < 0.98
                            ? 'text-amber-500'
                            : 'text-green-500'
                        }`}
                      >
                        {(a.compa_ratio * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          a.band_position === 'LOWER_QUARTILE' || a.band_position === 'BELOW_RANGE'
                            ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                            : a.band_position === 'AT_MARKET'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                        }`}
                      >
                        {a.band_position.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-indigo-600 dark:text-indigo-400 font-bold">
                      {a.suggested_merit_adjustment > 0
                        ? `+$${a.suggested_merit_adjustment.toLocaleString()}`
                        : 'On Market Target'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span
                        className={`px-2 py-0.5 text-xs font-semibold rounded ${
                          a.retention_risk_level === 'HIGH'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                            : a.retention_risk_level === 'MODERATE'
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
                            : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                        }`}
                      >
                        {a.retention_risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Market Benchmarks Reference Grid */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm space-y-4">
        <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <span>🎯</span> Verified Market Salary Bands (Percentile Curves)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {benchmarks.map((bm) => (
            <div key={bm.id} className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 space-y-2">
              <div className="flex justify-between items-start">
                <div className="font-bold text-sm text-gray-900 dark:text-white">{bm.job_title}</div>
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">
                  {bm.job_level}
                </span>
              </div>
              <div className="text-xs text-gray-400">{bm.geo_zone.replace(/_/g, ' ')}</div>

              <div className="grid grid-cols-4 gap-1 text-center pt-2 border-t border-gray-200 dark:border-gray-700">
                <div>
                  <div className="text-[10px] text-gray-400">P25</div>
                  <div className="text-xs font-mono font-semibold">${(bm.base_salary_p25 / 1000).toFixed(0)}k</div>
                </div>
                <div>
                  <div className="text-[10px] text-indigo-500 font-bold">P50</div>
                  <div className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400">${(bm.base_salary_p50 / 1000).toFixed(0)}k</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">P75</div>
                  <div className="text-xs font-mono font-semibold">${(bm.base_salary_p75 / 1000).toFixed(0)}k</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">P90</div>
                  <div className="text-xs font-mono font-semibold">${(bm.base_salary_p90 / 1000).toFixed(0)}k</div>
                </div>
              </div>

              <div className="text-[11px] text-gray-500 pt-1 flex justify-between">
                <span>Equity P50: {bm.equity_shares_p50.toLocaleString()} shs</span>
                <span>Bonus: {bm.variable_bonus_target_pct}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
