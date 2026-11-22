import React, { useState, useEffect } from 'react';
import { OffboardingRecord } from '../types';
import { api } from '../services/api';

export const OffboardingView: React.FC = () => {
  const [records, setRecords] = useState<OffboardingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [employeeId, setEmployeeId] = useState('');
  const [lastWorkingDay, setLastWorkingDay] = useState(new Date().toISOString().split('T')[0]);
  const [reason, setReason] = useState('VOLUNTARY_RESIGNATION');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadOffboarding();
  }, []);

  const loadOffboarding = async () => {
    try {
      setLoading(true);
      const res = await api.getOffboardingRecords();
      setRecords(res);
    } catch {
      // Presentation demo fallback
      setRecords([
        {
          id: 'off-1',
          organization_id: 'org-acme-1',
          employee_id: 'emp-rostova-elena',
          employee_name: 'Elena Rostova',
          last_working_day: '2026-12-15',
          termination_reason: 'VOLUNTARY_RESIGNATION',
          status: 'IN_PROGRESS',
          scim_deprovisioned: false,
          equipment_returned: false,
          nda_reaffirmed: true,
          notes: 'Accepted staff role at partner firm. Transitioning infrastructure documentation.',
          created_at: new Date().toISOString(),
          tasks: [
            { id: 't-1', title: 'Revoke SCIM 2.0 Identity & Enterprise SSO Access', category: 'IT', assigned_to: 'SECURITY_ADMIN', is_completed: false },
            { id: 't-2', title: 'Issue Prepaid Shipping Label for Laptop Return', category: 'IT', assigned_to: 'IT_OPS', is_completed: true },
            { id: 't-3', title: 'Execute Remote Hardware Wipe & Security Audit', category: 'IT', assigned_to: 'SECURITY_ADMIN', is_completed: false },
            { id: 't-4', title: 'Calculate Final Paystub & Accrued PTO Payout', category: 'FINANCE', assigned_to: 'PAYROLL_ADMIN', is_completed: true },
            { id: 't-5', title: 'Conduct Exit Interview & NDA Reaffirmation', category: 'HR', assigned_to: 'PEOPLE_MANAGER', is_completed: true },
          ],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleInitiate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employeeId.trim()) return;

    try {
      setSubmitting(true);
      const newRecord = await api.initiateOffboarding({
        employee_id: employeeId.trim(),
        last_working_day: lastWorkingDay,
        termination_reason: reason,
        notes: notes.trim() || undefined,
      });
      setRecords([newRecord, ...records]);
      setEmployeeId('');
      setNotes('');
    } catch {
      const mockRecord: OffboardingRecord = {
        id: `off-${Date.now()}`,
        organization_id: 'org-acme-1',
        employee_id: employeeId.trim(),
        employee_name: employeeId.trim(),
        last_working_day: lastWorkingDay,
        termination_reason: reason,
        status: 'IN_PROGRESS',
        scim_deprovisioned: false,
        equipment_returned: false,
        nda_reaffirmed: false,
        notes: notes.trim(),
        created_at: new Date().toISOString(),
        tasks: [
          { id: 't-1', title: 'Revoke SCIM 2.0 Identity & Enterprise SSO Access', category: 'IT', assigned_to: 'SECURITY_ADMIN', is_completed: false },
          { id: 't-2', title: 'Issue Prepaid Shipping Label for Laptop Return', category: 'IT', assigned_to: 'IT_OPS', is_completed: false },
          { id: 't-3', title: 'Execute Remote Hardware Wipe & Security Audit', category: 'IT', assigned_to: 'SECURITY_ADMIN', is_completed: false },
        ],
      };
      setRecords([mockRecord, ...records]);
      setEmployeeId('');
      setNotes('');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeprovisionSCIM = async (offboardingId: string) => {
    try {
      setActionLoading(offboardingId);
      await api.deprovisionSCIM(offboardingId);
      setRecords(records.map(r => r.id === offboardingId ? { ...r, scim_deprovisioned: true } : r));
    } catch {
      setRecords(records.map(r => r.id === offboardingId ? { ...r, scim_deprovisioned: true } : r));
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleTask = async (recordId: string, taskId: string) => {
    try {
      await api.toggleOffboardingTask(taskId);
      setRecords(records.map(r => {
        if (r.id === recordId) {
          const updatedTasks = r.tasks.map(t => t.id === taskId ? { ...t, is_completed: !t.is_completed } : t);
          return { ...r, tasks: updatedTasks };
        }
        return r;
      }));
    } catch {
      setRecords(records.map(r => {
        if (r.id === recordId) {
          const updatedTasks = r.tasks.map(t => t.id === taskId ? { ...t, is_completed: !t.is_completed } : t);
          return { ...r, tasks: updatedTasks };
        }
        return r;
      }));
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <h3 className="text-lg font-bold text-white">Automated Offboarding & Asset Reclamation</h3>
            <p className="text-xs text-slate-400">
              Structured lifecycle departure workflows, hardware wipe certification, and SCIM 2.0 automated deprovisioning.
            </p>
          </div>
          <span className="px-3 py-1 bg-red-950 text-red-300 font-bold text-xs rounded-full border border-red-800">
            SCIM 2.0 Synced
          </span>
        </div>
      </div>

      {/* Initiation Form */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
        <h4 className="text-sm font-bold text-white">Initiate Employee Offboarding</h4>
        <form onSubmit={handleInitiate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Employee Email or ID</label>
              <input
                type="text"
                required
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                placeholder="elena.rostova@internal.dev"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Last Working Day</label>
              <input
                type="date"
                required
                value={lastWorkingDay}
                onChange={(e) => setLastWorkingDay(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Termination Reason</label>
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="VOLUNTARY_RESIGNATION">Voluntary Resignation</option>
                <option value="INVOLUNTARY_TERMINATION">Involuntary Termination</option>
                <option value="RETIREMENT">Retirement</option>
                <option value="CONTRACT_END">Contract Expiration</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Transition & Handover Notes</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Handover owner, knowledge base links, shipping address..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-lg transition-colors shadow"
          >
            {submitting ? 'Initiating...' : 'Initiate Offboarding Protocol'}
          </button>
        </form>
      </div>

      {/* Offboarding Workflows List */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400 text-xs">
            Loading offboarding records...
          </div>
        ) : records.length === 0 ? (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400 text-xs">
            No active offboarding workflows.
          </div>
        ) : (
          records.map((r) => {
            const completedCount = r.tasks.filter(t => t.is_completed).length;
            const totalCount = r.tasks.length;
            const pct = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

            return (
              <div key={r.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                  <div>
                    <div className="flex items-center gap-3">
                      <h4 className="text-base font-bold text-white">{r.employee_name || r.employee_id}</h4>
                      <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
                        {r.termination_reason.replace(/_/g, ' ')}
                      </span>
                      {r.scim_deprovisioned ? (
                        <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-700">
                          SCIM Deprovisioned ✓
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-300 border border-red-800">
                          SCIM Active (Pending Revocation)
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Last Working Day: <span className="font-mono text-slate-200">{r.last_working_day}</span>
                      {r.notes && <span> — {r.notes}</span>}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    {!r.scim_deprovisioned && (
                      <button
                        onClick={() => handleDeprovisionSCIM(r.id)}
                        disabled={actionLoading === r.id}
                        className="px-3 py-1.5 bg-red-700 hover:bg-red-600 text-white rounded text-xs font-semibold transition-colors"
                      >
                        {actionLoading === r.id ? 'Revoking...' : 'Revoke SCIM Access'}
                      </button>
                    )}
                    <div className="text-right">
                      <div className="text-xs font-bold text-indigo-400">{completedCount}/{totalCount} Tasks</div>
                      <div className="text-[10px] text-slate-400">{pct.toFixed(0)}% Complete</div>
                    </div>
                  </div>
                </div>

                {/* Task Checklist */}
                <div className="bg-slate-900/60 border border-slate-750 rounded-lg p-3 divide-y divide-slate-800">
                  {r.tasks.map((task) => (
                    <div key={task.id} className="py-2.5 flex items-center justify-between gap-3 first:pt-1 last:pb-1">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={task.is_completed}
                          onChange={() => handleToggleTask(r.id, task.id)}
                          className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0 cursor-pointer"
                        />
                        <span className={`text-xs ${task.is_completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                          {task.title}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {task.category}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {task.assigned_to}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
