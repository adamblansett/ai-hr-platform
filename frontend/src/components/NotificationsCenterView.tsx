import React, { useState, useEffect } from 'react';
import { Bell, CheckCheck, Send, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { DigestSummary, NotificationItem } from '../types';

export const NotificationsCenterView: React.FC<{ onCountChange?: () => void }> = ({ onCountChange }) => {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [digest, setDigest] = useState<DigestSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [channel, setChannel] = useState('SLACK');
  const [category, setCategory] = useState('COMPLIANCE_LMS');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const data = await api.getNotifications('emp-001');
      setItems(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkRead = async (id: string) => {
    await api.markNotificationRead(id);
    await loadNotifications();
    onCountChange?.();
  };

  const handleTriggerDigest = async () => {
    const res = await api.triggerDailyDigest('org-001');
    setDigest(res);
    await loadNotifications();
    onCountChange?.();
  };

  const handleDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.dispatchNotification({
      recipient_employee_id: 'emp-001',
      channel,
      category,
      title,
      body,
    });
    setTitle('');
    setBody('');
    await loadNotifications();
    onCountChange?.();
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading notification feed & digest history...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Bell className="w-6 h-6 text-indigo-400" />
            Event-Driven Notification & Digest Engine
          </h2>
          <p className="text-sm text-slate-400">
            Multi-channel HR alerts across Email, Slack, Microsoft Teams, and In-App Inbox for visas, leave approvals, LMS deadlines, and reviews.
          </p>
        </div>
        <button
          onClick={handleTriggerDigest}
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg"
        >
          <Sparkles className="w-4 h-4" /> Compile Daily HR Digest
        </button>
      </div>

      {digest && (
        <div className="bg-indigo-950/50 border border-indigo-500/40 rounded-xl p-5 space-y-2">
          <div className="text-sm font-semibold text-indigo-300">Daily HR Operations Digest Dispatched</div>
          <p className="text-sm text-slate-200">{digest.digest_preview}</p>
          <div className="flex flex-wrap gap-3 text-xs text-slate-400 pt-1">
            <span>Expiring Visas: {digest.expiring_visas_count}</span>
            <span>Pending Leave: {digest.pending_leave_approvals_count}</span>
            <span>Overdue LMS: {digest.overdue_compliance_courses_count}</span>
            <span>Review Deadlines: {digest.upcoming_review_deadlines_count}</span>
            <span>Channels: {digest.dispatched_channels.join(', ')}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-3">
          <h3 className="text-lg font-semibold text-white">Recent Dispatches ({items.length})</h3>
          {items.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-lg border ${
                item.status === 'READ' ? 'bg-slate-900/60 border-slate-700/60' : 'bg-slate-900 border-indigo-500/40'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-800 text-indigo-300 border border-slate-700">
                      {item.channel}
                    </span>
                    <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-800 text-slate-300">
                      {item.category}
                    </span>
                    <span className="text-sm font-semibold text-white">{item.title}</span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1.5">{item.body}</p>
                </div>
                {item.status !== 'READ' ? (
                  <button
                    onClick={() => handleMarkRead(item.id)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs rounded border border-slate-700 shrink-0"
                  >
                    <CheckCheck className="w-3.5 h-3.5" /> Mark Read
                  </button>
                ) : (
                  <span className="text-[11px] text-slate-500 font-mono">READ</span>
                )}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleDispatch} className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4 h-fit">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Send className="w-4 h-4 text-indigo-400" /> Dispatch Ad-Hoc Alert
          </h3>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Channel</label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            >
              <option value="SLACK">Slack Interactive Webhook</option>
              <option value="TEAMS">Microsoft Teams Card</option>
              <option value="EMAIL">SMTP / SES Email</option>
              <option value="IN_APP">In-App Inbox</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            >
              <option value="COMPLIANCE_LMS">Compliance LMS Reminder</option>
              <option value="LEAVE_APPROVAL">Leave Approval</option>
              <option value="VISA_EXPIRY">Visa Expiration Alert</option>
              <option value="REVIEW_DEADLINE">Review Cycle Deadline</option>
              <option value="ONBOARDING_REMINDER">Onboarding Reminder</option>
              <option value="SECURITY_ALERT">Security Alert</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Q4 Review Calibration Starts Tomorrow"
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Message</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={3}
              placeholder="Notification details..."
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg"
          >
            Send Notification
          </button>
        </form>
      </div>
    </div>
  );
};
