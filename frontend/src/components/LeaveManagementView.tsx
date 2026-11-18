import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LeaveBalance, LeaveRequest } from '../types';

export const LeaveManagementView: React.FC = () => {
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [showModal, setShowModal] = useState(false);

  // Form
  const [selectedPolicy, setSelectedPolicy] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      const [b, r] = await Promise.all([
        api.getMyLeaveBalances(),
        api.getMyLeaveRequests(),
      ]);
      setBalances(b);
      setRequests(r);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPolicy || !startDate || !endDate || !reason) return;

    try {
      setSubmitting(true);
      await api.submitLeaveRequest({
        policy_id: selectedPolicy,
        start_date: startDate,
        end_date: endDate,
        reason,
      });
      setShowModal(false);
      setReason('');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Error submitting leave request');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white">Leave & Attendance</h2>
          <p className="text-slate-400 text-sm">Review accrued balances and submit time-off requests.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-lg transition-colors shadow"
        >
          + Request Time Off
        </button>
      </div>

      {/* Balances grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {balances.map((b) => (
          <div key={b.id} className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{b.policy_name}</div>
            <div className="text-3xl font-extrabold text-white mt-2">{b.remaining_days}</div>
            <div className="text-xs text-slate-400 mt-1 font-mono">
              Accrued: {b.accrued_days}d | Used: {b.used_days}d
            </div>
          </div>
        ))}
      </div>

      {/* Request History */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h3 className="font-semibold text-white">Leave Request History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-750 text-xs uppercase font-mono text-slate-400">
              <tr>
                <th className="px-6 py-3">Policy</th>
                <th className="px-6 py-3">Dates</th>
                <th className="px-6 py-3">Duration</th>
                <th className="px-6 py-3">Reason</th>
                <th className="px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {requests.map((r) => (
                <tr key={r.id} className="hover:bg-slate-750 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">{r.policy_name}</td>
                  <td className="px-6 py-4 font-mono text-xs">{r.start_date} to {r.end_date}</td>
                  <td className="px-6 py-4">{r.total_days} days</td>
                  <td className="px-6 py-4 text-slate-400 max-w-xs truncate">{r.reason}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                      r.status === 'APPROVED'
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : r.status === 'REJECTED'
                        ? 'bg-rose-500/10 text-rose-400'
                        : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {r.status}
                    </span>
                    {r.calendar_conflict_flag && (
                      <span className="ml-2 text-[10px] text-amber-400 border border-amber-500/30 px-1.5 py-0.5 rounded">
                        Team Overlap
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {requests.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    No time off requests filed yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Request Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-white">Submit Time-Off Request</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Select Policy</label>
                <select
                  value={selectedPolicy}
                  onChange={(e) => setSelectedPolicy(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                  required
                >
                  <option value="">-- Select --</option>
                  {balances.map((b) => (
                    <option key={b.policy_id} value={b.policy_id}>
                      {b.policy_name} ({b.remaining_days} days remaining)
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Reason</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                  placeholder="Personal vacation, family event, medical..."
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm font-medium rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg"
                >
                  {submitting ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
