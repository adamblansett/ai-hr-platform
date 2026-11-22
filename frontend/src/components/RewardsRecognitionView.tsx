import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  PeerRecognition,
  RewardCatalogItem,
  EmployeeWallet,
  MilestoneEvent,
} from '../types';

export const RewardsRecognitionView: React.FC = () => {
  const [feed, setFeed] = useState<PeerRecognition[]>([]);
  const [rewards, setRewards] = useState<RewardCatalogItem[]>([]);
  const [wallet, setWallet] = useState<EmployeeWallet | null>(null);
  const [milestones, setMilestones] = useState<MilestoneEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Send Kudos Modal state
  const [showKudosModal, setShowKudosModal] = useState<boolean>(false);
  const [recipientId, setRecipientId] = useState('emp-002');
  const [points, setPoints] = useState('50');
  const [coreValue, setCoreValue] = useState('INNOVATION_EXCELLENCE');
  const [message, setMessage] = useState('');

  // Redemption Notification
  const [redemptionSuccess, setRedemptionSuccess] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [feedData, rewardsData, walletData, milestonesData] = await Promise.all([
        api.getRecognitionFeed(),
        api.getRewardsCatalog(),
        api.getEmployeeWallet('emp-001'),
        api.getUpcomingMilestones(),
      ]);
      setFeed(feedData);
      setRewards(rewardsData);
      setWallet(walletData);
      setMilestones(milestonesData);
    } catch (err) {
      console.error('Failed to load recognition data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSendKudos = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message) return;

    try {
      await api.sendPeerKudos({
        sender_id: 'emp-001',
        recipient_id: recipientId,
        points: parseInt(points) || 50,
        core_value: coreValue,
        message,
      });
      setShowKudosModal(false);
      setMessage('');
      fetchData();
    } catch (err) {
      alert('Failed to send kudos: ' + err);
    }
  };

  const handleRedeem = async (item: RewardCatalogItem) => {
    if (!wallet) return;
    if (wallet.points_balance < item.points_cost) {
      alert(`Insufficient points! You need ${item.points_cost} points, but have ${wallet.points_balance}.`);
      return;
    }

    try {
      const res = await api.redeemReward({
        employee_id: 'emp-001',
        reward_item_id: item.id,
      });
      setRedemptionSuccess(res.message);
      fetchData();
    } catch (err) {
      alert('Redemption failed: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🎉</span> Rewards, Kudos & Peer Recognition Engine
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Discretionary peer points, corporate core value alignment, anniversary milestones, and swag/gift card redemption.
          </p>
        </div>
        <button
          onClick={() => setShowKudosModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-amber-500 hover:bg-amber-600"
        >
          ✨ Give Peer Kudos
        </button>
      </div>

      {/* Wallet Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-amber-500 to-orange-600 text-white p-5 rounded-xl shadow-sm">
          <div className="text-xs uppercase font-semibold tracking-wider opacity-80">Redeemable Balance</div>
          <div className="mt-2 text-3xl font-extrabold">{wallet ? wallet.points_balance : '—'} <span className="text-base font-normal">pts</span></div>
          <div className="mt-2 text-xs opacity-90">Ready to spend on perks, gift cards, or PTO</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Monthly Giving Allowance</div>
          <div className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">
            {wallet ? wallet.monthly_allowance_remaining : '—'} <span className="text-sm font-normal text-gray-500">pts</span>
          </div>
          <div className="mt-1 text-xs text-amber-500 font-medium">Resets on 1st of every month</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Upcoming Milestones</div>
          <div className="mt-1 text-3xl font-bold text-indigo-600 dark:text-indigo-400">
            {milestones.length}
          </div>
          <div className="mt-1 text-xs text-gray-400">Anniversaries & Celebrations</div>
        </div>
      </div>

      {/* Redemption Success Alert */}
      {redemptionSuccess && (
        <div className="p-4 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/40 text-green-800 dark:text-green-300 flex justify-between items-center text-sm">
          <div>{redemptionSuccess}</div>
          <button onClick={() => setRedemptionSuccess(null)} className="text-xs font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Upcoming Milestones Ticker */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
        <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <span>🎂</span> Upcoming Team Milestones
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {milestones.map((m, idx) => (
            <div key={idx} className="p-3 rounded-lg border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 flex items-center justify-between">
              <div>
                <div className="font-semibold text-xs text-gray-900 dark:text-white">{m.employee_name}</div>
                <div className="text-xs text-gray-500">
                  {m.milestone_type === 'WORK_ANNIVERSARY' ? `${m.anniversary_years} Year Anniversary` : m.milestone_type} • {m.milestone_date}
                </div>
              </div>
              <span className="px-2 py-0.5 text-xs font-bold text-amber-600 bg-amber-50 dark:bg-amber-900/30 rounded-full">
                +{m.suggested_award_points} pts
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Grid: Kudos Feed & Rewards Catalog */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Kudos Feed (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <span>💬</span> Live Kudos Feed
              </h3>
              <span className="text-xs text-gray-400">Public recognitions</span>
            </div>

            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading recognitions...</div>
            ) : feed.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No recognitions yet. Send the first kudos above!</div>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {feed.map((r) => (
                  <div key={r.id} className="p-5 hover:bg-gray-50 dark:hover:bg-gray-750 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-semibold text-gray-900 dark:text-white">
                        <span className="text-indigo-600 dark:text-indigo-400">{r.sender_id}</span> recognized{' '}
                        <span className="text-amber-600 dark:text-amber-400">{r.recipient_id}</span>
                      </div>
                      <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                        +{r.points} pts
                      </span>
                    </div>

                    <div className="text-xs inline-block px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium">
                      🎯 {r.core_value.replace(/_/g, ' ')}
                    </div>

                    <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                      "{r.message}"
                    </p>

                    <div className="text-xs text-gray-400 pt-1">
                      {new Date(r.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Rewards Catalog (1 col) */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <span>🎁</span> Rewards Catalog
              </h3>
            </div>

            <div className="p-4 space-y-4">
              {rewards.map((it) => (
                <div key={it.id} className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 space-y-2">
                  <div className="flex justify-between items-start">
                    <div className="font-bold text-sm text-gray-900 dark:text-white">{it.title}</div>
                    <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-0.5 rounded-full">
                      {it.points_cost} pts
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                    {it.description}
                  </p>
                  <button
                    onClick={() => handleRedeem(it)}
                    disabled={!wallet || wallet.points_balance < it.points_cost}
                    className={`w-full py-1.5 text-xs font-medium rounded-lg transition-colors ${
                      wallet && wallet.points_balance >= it.points_cost
                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {wallet && wallet.points_balance >= it.points_cost ? 'Redeem Item' : 'Insufficient Points'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Give Kudos Modal */}
      {showKudosModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Give Peer Recognition & Kudos</h3>
            <form onSubmit={handleSendKudos} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Colleague</label>
                <select
                  value={recipientId}
                  onChange={(e) => setRecipientId(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                >
                  <option value="emp-002">Sarah Miller (VP Engineering)</option>
                  <option value="emp-003">David Patel (DevOps Lead)</option>
                  <option value="emp-004">Elena Rostova (Senior Frontend)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Points to Award</label>
                  <input
                    type="number"
                    min="10"
                    max={wallet ? wallet.monthly_allowance_remaining : 200}
                    value={points}
                    onChange={(e) => setPoints(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                  <div className="text-[10px] text-gray-400 mt-0.5">Allowance: {wallet?.monthly_allowance_remaining} pts</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Core Value</label>
                  <select
                    value={coreValue}
                    onChange={(e) => setCoreValue(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="CUSTOMER_OBSESSION">Customer Obsession</option>
                    <option value="BIAS_FOR_ACTION">Bias for Action</option>
                    <option value="INNOVATION_EXCELLENCE">Innovation Excellence</option>
                    <option value="INCLUSION_AND_RESPECT">Inclusion & Respect</option>
                    <option value="DELIVER_RESULTS">Deliver Results</option>
                    <option value="OWNERSHIP">Ownership</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Recognition Message</label>
                <textarea
                  rows={3}
                  required
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Share what they did and how it exemplified this core value..."
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowKudosModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg"
                >
                  Send Kudos
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
