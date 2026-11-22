import React, { useState, useEffect } from 'react';
import { TimeSheetEntry, AttendanceSummary } from '../types';
import { api } from '../services/api';

export const TimeAttendanceView: React.FC = () => {
  const [timesheets, setTimesheets] = useState<TimeSheetEntry[]>([]);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Active shift state
  const [isClockedIn, setIsClockedIn] = useState(false);
  const [activeShiftStart, setActiveShiftStart] = useState<string | null>(null);
  const [mealBreakMinutes, setMealBreakMinutes] = useState(30);
  const [shiftNotes, setShiftNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      setLoading(true);
      const [sheetsRes, user] = await Promise.all([
        api.getMyTimesheets(),
        api.getMe(),
      ]);
      setTimesheets(sheetsRes);

      const active = sheetsRes.find((s) => s.status === 'ACTIVE_SHIFT');
      if (active) {
        setIsClockedIn(true);
        setActiveShiftStart(active.clock_in);
      }

      if (user) {
        const sumRes = await api.getAttendanceSummary(user.id).catch(() => null);
        if (sumRes) setSummary(sumRes);
      }
    } catch {
      // Presentation demo fallback
      const mockSheets: TimeSheetEntry[] = [
        {
          id: 'ts-1',
          employee_id: 'emp-1',
          shift_date: '2026-11-20',
          clock_in: '2026-11-20T09:00:00Z',
          clock_out: '2026-11-20T19:30:00Z',
          total_hours: 10.0,
          regular_hours: 8.0,
          overtime_hours: 2.0,
          double_time_hours: 0.0,
          meal_break_minutes: 30,
          meal_penalty_flag: false,
          status: 'COMPLETED',
          notes: 'Standard shift with sprint deployment overtime',
        },
        {
          id: 'ts-2',
          employee_id: 'emp-1',
          shift_date: '2026-11-19',
          clock_in: '2026-11-19T09:00:00Z',
          clock_out: '2026-11-19T17:30:00Z',
          total_hours: 8.0,
          regular_hours: 8.0,
          overtime_hours: 0.0,
          double_time_hours: 0.0,
          meal_break_minutes: 30,
          meal_penalty_flag: false,
          status: 'COMPLETED',
        },
        {
          id: 'ts-3',
          employee_id: 'emp-1',
          shift_date: '2026-11-18',
          clock_in: '2026-11-18T08:00:00Z',
          clock_out: '2026-11-18T21:30:00Z',
          total_hours: 13.0,
          regular_hours: 8.0,
          overtime_hours: 4.0,
          double_time_hours: 1.0,
          meal_break_minutes: 30,
          meal_penalty_flag: false,
          status: 'COMPLETED',
          notes: 'Critical incident response shift',
        },
      ];
      setTimesheets(mockSheets);
      setSummary({
        employee_id: 'emp-1',
        period_start: '2026-11-09',
        period_end: '2026-11-22',
        total_shifts: 3,
        total_regular_hours: 24.0,
        total_overtime_hours: 6.0,
        total_double_time_hours: 1.0,
        meal_penalty_violations: 0,
        estimated_payable_hours: 35.0,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async () => {
    try {
      setActionLoading(true);
      const res = await api.clockIn(shiftNotes || undefined);
      setIsClockedIn(true);
      setActiveShiftStart(res.clock_in);
      setTimesheets([res, ...timesheets]);
      setShiftNotes('');
    } catch {
      setIsClockedIn(true);
      setActiveShiftStart(new Date().toISOString());
    } finally {
      setActionLoading(false);
    }
  };

  const handleClockOut = async () => {
    try {
      setActionLoading(true);
      const res = await api.clockOut(mealBreakMinutes, shiftNotes || undefined);
      setIsClockedIn(false);
      setActiveShiftStart(null);
      setTimesheets(timesheets.map((t) => (t.status === 'ACTIVE_SHIFT' ? res : t)));
      setShiftNotes('');
    } catch {
      setIsClockedIn(false);
      setActiveShiftStart(null);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400 text-xs">
        Loading time & attendance records...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Overtime & FLSA Compliance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Regular Hours (1.0x)</div>
          <div className="text-2xl font-bold text-white mt-1">
            {summary?.total_regular_hours || 0} <span className="text-xs font-normal text-slate-400">hrs</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Standard 8-hour shift limits</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overtime Hours (1.5x)</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            {summary?.total_overtime_hours || 0} <span className="text-xs font-normal text-slate-400">hrs</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Daily hours 8.0 to 12.0</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Double-Time (2.0x)</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {summary?.total_double_time_hours || 0} <span className="text-xs font-normal text-slate-400">hrs</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Statutory daily hours &gt; 12.0</div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Payable Hours Equivalent</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {summary?.estimated_payable_hours || 0} <span className="text-xs font-normal text-slate-400">hrs</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Fed to payroll paystub engine</div>
        </div>
      </div>

      {/* Clock In / Out Action Panel */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h4 className="text-base font-bold text-white">Digital Shift Punch & Break Auditor</h4>
            <p className="text-xs text-slate-400">
              {isClockedIn ? `Active shift started at ${activeShiftStart}` : 'Currently not clocked in'}
            </p>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-bold border ${
              isClockedIn
                ? 'bg-emerald-950 text-emerald-300 border-emerald-800 animate-pulse'
                : 'bg-slate-900 text-slate-400 border-slate-700'
            }`}
          >
            {isClockedIn ? '● SHIFT ACTIVE' : '○ OFF DUTY'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Shift Notes / Project</label>
            <input
              type="text"
              value={shiftNotes}
              onChange={(e) => setShiftNotes(e.target.value)}
              placeholder="e.g. Distributed system maintenance..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          {isClockedIn && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Meal Break Deducted</label>
              <select
                value={mealBreakMinutes}
                onChange={(e) => setMealBreakMinutes(parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                <option value={30}>30 Minutes (Standard Compliant)</option>
                <option value={45}>45 Minutes</option>
                <option value={60}>60 Minutes (Full Hour)</option>
                <option value={0}>0 Minutes (Meal Penalty Check)</option>
              </select>
            </div>
          )}

          <div className="flex items-end">
            {isClockedIn ? (
              <button
                onClick={handleClockOut}
                disabled={actionLoading}
                className="w-full py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-red-600/30"
              >
                {actionLoading ? 'Punches...' : 'Clock Out (End Shift)'}
              </button>
            ) : (
              <button
                onClick={handleClockIn}
                disabled={actionLoading}
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-emerald-600/30"
              >
                {actionLoading ? 'Punches...' : 'Clock In (Start Shift)'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Timesheet History Table */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-lg space-y-4 p-6">
        <h4 className="text-sm font-bold text-white">Logged Timesheets & Statutory Auditing</h4>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Shift Date</th>
                <th className="px-4 py-3">Clock In</th>
                <th className="px-4 py-3">Clock Out</th>
                <th className="px-4 py-3 text-center">Regular (1.0x)</th>
                <th className="px-4 py-3 text-center">Overtime (1.5x)</th>
                <th className="px-4 py-3 text-center">Double-Time (2.0x)</th>
                <th className="px-4 py-3 text-center">Meal Break</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-slate-300">
              {timesheets.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-750/50">
                  <td className="px-4 py-3 font-mono font-semibold text-white">{entry.shift_date}</td>
                  <td className="px-4 py-3 font-mono text-slate-400">{entry.clock_in.split('T')[1]?.slice(0, 5) || entry.clock_in}</td>
                  <td className="px-4 py-3 font-mono text-slate-400">
                    {entry.clock_out ? entry.clock_out.split('T')[1]?.slice(0, 5) : 'Active'}
                  </td>
                  <td className="px-4 py-3 text-center font-bold text-white">{entry.regular_hours} hrs</td>
                  <td className="px-4 py-3 text-center font-bold text-indigo-400">
                    {entry.overtime_hours > 0 ? `${entry.overtime_hours} hrs` : '-'}
                  </td>
                  <td className="px-4 py-3 text-center font-bold text-amber-400">
                    {entry.double_time_hours > 0 ? `${entry.double_time_hours} hrs` : '-'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {entry.meal_penalty_flag ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-300 border border-red-800">
                        Penalty Violation
                      </span>
                    ) : (
                      <span className="text-slate-400">{entry.meal_break_minutes} min</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        entry.status === 'ACTIVE_SHIFT'
                          ? 'bg-emerald-950 text-emerald-300 border-emerald-800 animate-pulse'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}
                    >
                      {entry.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
