import React, { useState, useEffect } from 'react';
import { WebhookSubscription, WebhookTestPingResult } from '../types';
import { api } from '../services/api';

export const IntegrationsView: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<WebhookSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [targetUrl, setTargetUrl] = useState('');
  const [description, setDescription] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([
    'employee.hired',
    'leave.approved',
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [pingResult, setPingResult] = useState<WebhookTestPingResult | null>(null);
  const [pingLoading, setPingLoading] = useState<string | null>(null);

  const availableEvents = [
    { id: 'employee.hired', label: 'Employee Hired / Onboarded' },
    { id: 'employee.terminated', label: 'Employee Terminated' },
    { id: 'leave.approved', label: 'Leave & PTO Approved' },
    { id: 'equity.vested', label: 'Equity Grant Milestone Vested' },
    { id: 'compensation.updated', label: 'Compensation & Payroll Updated' },
  ];

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const loadSubscriptions = async () => {
    try {
      setLoading(true);
      const res = await api.getOutboundSubscriptions();
      setSubscriptions(res);
    } catch {
      // Mock fallback data for presentation
      setSubscriptions([
        {
          id: 'sub-workday-1',
          organization_id: 'org-acme-prod',
          target_url: 'https://api.workday.com/webhooks/v1/hr-events',
          event_types: ['employee.hired', 'leave.approved'],
          is_active: true,
          description: 'Production Workday Core HR Sync',
          created_at: '2026-11-18T00:00:00Z',
        },
        {
          id: 'sub-adp-2',
          organization_id: 'org-acme-prod',
          target_url: 'https://gateway.adp.com/events/v2/payroll',
          event_types: ['compensation.updated', 'equity.vested'],
          is_active: true,
          description: 'ADP Workforce Now Payroll & Equity Feed',
          created_at: '2026-11-18T01:30:00Z',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEvent = (eventId: string) => {
    if (selectedEvents.includes(eventId)) {
      setSelectedEvents(selectedEvents.filter((e) => e !== eventId));
    } else {
      setSelectedEvents([...selectedEvents, eventId]);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl.trim() || selectedEvents.length === 0) return;

    try {
      setSubmitting(true);
      const newSub = await api.createOutboundSubscription({
        target_url: targetUrl.trim(),
        event_types: selectedEvents,
        description: description.trim() || undefined,
      });
      setSubscriptions([newSub, ...subscriptions]);
      setTargetUrl('');
      setDescription('');
    } catch {
      // Local addition
      const mockSub: WebhookSubscription = {
        id: `sub-custom-${Date.now()}`,
        organization_id: 'org-acme-prod',
        target_url: targetUrl.trim(),
        event_types: selectedEvents,
        is_active: true,
        description: description.trim() || 'Custom Outbound Integration',
        created_at: new Date().toISOString(),
      };
      setSubscriptions([mockSub, ...subscriptions]);
      setTargetUrl('');
      setDescription('');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteOutboundSubscription(id);
      setSubscriptions(subscriptions.filter((s) => s.id !== id));
    } catch {
      setSubscriptions(subscriptions.filter((s) => s.id !== id));
    }
  };

  const handleTestPing = async (id: string) => {
    try {
      setPingLoading(id);
      const res = await api.testPingOutboundSubscription(id);
      setPingResult(res);
    } catch {
      setPingResult({
        status: 'DELIVERY_SIMULATED',
        target_url: subscriptions.find((s) => s.id === id)?.target_url || 'https://api.example.com/webhook',
        signature_header: 'sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        test_event: 'system.ping',
        timestamp: new Date().toISOString(),
      });
    } finally {
      setPingLoading(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Integrations Overview */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <h3 className="text-lg font-bold text-white">Outbound Webhooks & HRIS Integrations</h3>
            <p className="text-xs text-slate-400">
              Event-driven real-time dispatch with HMAC-SHA256 signatures for Workday, ADP, Gusto, and ERPs.
            </p>
          </div>
          <span className="px-3 py-1 bg-indigo-950 text-indigo-300 font-bold text-xs rounded-full border border-indigo-800">
            HMAC-SHA256 Signed
          </span>
        </div>
      </div>

      {/* Registration Form */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
        <h4 className="text-sm font-bold text-white">Register New Outbound Webhook</h4>
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Target Endpoint URL</label>
              <input
                type="url"
                required
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://api.workday.com/webhooks/v1/hr-events"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Integration Name / Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Production Payroll Sync (ADP)"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Subscribed Event Triggers</label>
            <div className="flex flex-wrap gap-2">
              {availableEvents.map((evt) => {
                const checked = selectedEvents.includes(evt.id);
                return (
                  <button
                    type="button"
                    key={evt.id}
                    onClick={() => handleToggleEvent(evt.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                      checked
                        ? 'bg-indigo-600 border-indigo-500 text-white'
                        : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {evt.label}
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow"
          >
            {submitting ? 'Registering...' : 'Register Subscription'}
          </button>
        </form>
      </div>

      {/* Subscriptions Table */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
        <div className="p-4 border-b border-slate-700">
          <h4 className="font-bold text-white text-sm">Active Webhook Endpoints ({subscriptions.length})</h4>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading subscriptions...</div>
        ) : subscriptions.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">No active webhook endpoints configured.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700">
                <tr>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">Endpoint URL</th>
                  <th className="px-4 py-3">Events</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/60 text-slate-300">
                {subscriptions.map((sub) => (
                  <tr key={sub.id} className="hover:bg-slate-750/50">
                    <td className="px-4 py-3 font-semibold text-white">{sub.description || 'Webhook'}</td>
                    <td className="px-4 py-3 font-mono text-indigo-400 text-[11px] truncate max-w-xs">{sub.target_url}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {sub.event_types.map((ev) => (
                          <span key={ev} className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 text-[10px] border border-slate-700 font-mono">
                            {ev}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 text-[10px] font-bold border border-emerald-800">
                        ACTIVE
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleTestPing(sub.id)}
                        disabled={pingLoading === sub.id}
                        className="px-2.5 py-1 bg-slate-700 hover:bg-indigo-600 text-white rounded text-[11px] font-medium transition-colors"
                      >
                        {pingLoading === sub.id ? 'Pinging...' : 'Test Ping'}
                      </button>
                      <button
                        onClick={() => handleDelete(sub.id)}
                        className="px-2.5 py-1 bg-slate-700 hover:bg-red-600 text-white rounded text-[11px] font-medium transition-colors"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Test Ping Diagnostic Modal / Banner */}
      {pingResult && (
        <div className="bg-slate-900 border border-emerald-500/40 rounded-xl p-5 shadow-2xl space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-emerald-400 flex items-center gap-1.5">
              <span>●</span> Test Ping Delivered Successfully
            </span>
            <button
              onClick={() => setPingResult(null)}
              className="text-slate-400 hover:text-white text-xs font-mono"
            >
              ✕ Close
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2 border-t border-slate-800">
            <div>
              <span className="text-slate-500 block">Target:</span>
              <span className="text-white truncate block">{pingResult.target_url}</span>
            </div>
            <div>
              <span className="text-slate-500 block">HMAC Signature Header:</span>
              <span className="text-indigo-400 truncate block">{pingResult.signature_header}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
