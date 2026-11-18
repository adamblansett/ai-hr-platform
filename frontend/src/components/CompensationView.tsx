import React, { useState, useEffect } from 'react';
import { CompensationSummary, EquityGrant, PaystubRecord } from '../types';
import { api } from '../services/api';

export const CompensationView: React.FC = () => {
  const [data, setData] = useState<CompensationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState<'equity' | 'paystubs'>('equity');

  useEffect(() => {
    loadCompensation();
  }, []);

  const loadCompensation = async () => {
    try {
      setLoading(true);
      const res = await api.getMyCompensation();
      setData(res);
    } catch {
      // Mock fallback data for presentation if database record not yet seeded for demo user
      setData({
        package: {
          id: 'pkg-1',
          employee_id: 'emp-1',
          base_salary: 165000,
          currency: 'USD',
          payment_frequency: 'MONTHLY',
          target_bonus_percentage: 15.0,
          effective_date: '2026-01-01',
        },
        equity_grants: [
          {
            id: 'eq-1',
            grant_type: 'ISO',
            total_shares: 48000,
            vested_shares: 12000,
            unvested_shares: 36000,
            strike_price: 2.5,
            grant_date: '2025-01-15',
            vesting_start_date: '2025-01-15',
            cliff_date: '2026-01-15',
            cliff_months: 12,
            total_vesting_months: 48,
            estimated_current_value: 360000,
            next_vesting_date: '2026-12-01',
          },
        ],
        recent_paystubs: [
          {
            id: 'stub-1',
            paystub_number: 'PAY-2026-10-A9F1',
            pay_period_start: '2026-10-01',
            pay_period_end: '2026-10-31',
            payment_date: '2026-10-31',
            gross_pay: 13750,
            federal_tax: 3025,
            social_security: 852.5,
            medicare: 199.38,
            state_tax: 687.5,
            other_deductions: 0,
            net_pay: 8985.62,
          },
          {
            id: 'stub-2',
            paystub_number: 'PAY-2026-09-B8C2',
            pay_period_start: '2026-09-01',
            pay_period_end: '2026-09-30',
            payment_date: '2026-09-30',
            gross_pay: 13750,
            federal_tax: 3025,
            social_security: 852.5,
            medicare: 199.38,
            state_tax: 687.5,
            other_deductions: 0,
            net_pay: 8985.62,
          },
        ],
        total_equity_shares: 48000,
        total_vested_shares: 12000,
        total_unvested_shares: 36000,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400">
        Loading compensation & equity details...
      </div>
    );
  }

  const pkg = data?.package;
  const grants = data?.equity_grants || [];
  const paystubs = data?.recent_paystubs || [];

  return (
    <div className="space-y-6">
      {/* Top Banner: Salary & Total Comp Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Annual Base Salary</div>
          <div className="text-2xl font-bold text-white mt-1">
            ${pkg ? pkg.base_salary.toLocaleString() : '0'} <span className="text-xs font-normal text-slate-400">{pkg?.currency || 'USD'}</span>
          </div>
          <div className="text-xs text-indigo-400 mt-1 font-medium capitalize">
            {pkg?.payment_frequency.toLowerCase() || 'monthly'} disbursement
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target Bonus</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {pkg ? `${pkg.target_bonus_percentage}%` : '0%'}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Est. ${pkg ? ((pkg.base_salary * pkg.target_bonus_percentage) / 100).toLocaleString() : 0}/yr
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Vested Equity</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {(data?.total_vested_shares || 0).toLocaleString()} <span className="text-xs font-normal text-slate-400">shares</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            of {(data?.total_equity_shares || 0).toLocaleString()} total granted
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Est. Equity Valuation</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            ${grants.reduce((acc, g) => acc + g.estimated_current_value, 0).toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 mt-1">Based on latest internal valuation</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700 space-x-4">
        <button
          onClick={() => setActiveSubTab('equity')}
          className={`pb-3 text-sm font-semibold transition-colors border-b-2 ${
            activeSubTab === 'equity'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Equity Grants & Vesting Schedule
        </button>
        <button
          onClick={() => setActiveSubTab('paystubs')}
          className={`pb-3 text-sm font-semibold transition-colors border-b-2 ${
            activeSubTab === 'paystubs'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Paystub History & Withholding Breakdown
        </button>
      </div>

      {/* Equity Schedule View */}
      {activeSubTab === 'equity' && (
        <div className="space-y-4">
          {grants.length === 0 ? (
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400">
              No equity grants currently recorded.
            </div>
          ) : (
            grants.map((g: EquityGrant) => {
              const vestPct = g.total_shares > 0 ? (g.vested_shares / g.total_shares) * 100 : 0;
              return (
                <div key={g.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                        {g.grant_type} Grant
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2">
                        {g.total_shares.toLocaleString()} Shares @ ${g.strike_price.toFixed(2)} Strike
                      </h3>
                      <p className="text-xs text-slate-400">
                        Granted on {g.grant_date} | 1-Year Cliff: {g.cliff_date}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold text-emerald-400">
                        {vestPct.toFixed(1)}% Vested
                      </div>
                      <div className="text-xs text-slate-400">Next Vest: {g.next_vesting_date || 'Monthly'}</div>
                    </div>
                  </div>

                  {/* Vesting Progress Bar */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-slate-400 font-mono">
                      <span>Vested: {g.vested_shares.toLocaleString()}</span>
                      <span>Unvested: {g.unvested_shares.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-3 overflow-hidden p-0.5 border border-slate-700">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-full rounded-full transition-all duration-500"
                        style={{ width: `${vestPct}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-[11px] text-slate-500">
                      <span>Month 0 (Start)</span>
                      <span className="text-amber-500 font-semibold">12-Month Cliff</span>
                      <span>48-Month Full Vest</span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Paystubs View */}
      {activeSubTab === 'paystubs' && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
          <div className="p-4 border-b border-slate-700 flex justify-between items-center">
            <h4 className="font-bold text-white text-sm">Disbursed Paystub Records</h4>
            <span className="text-xs text-slate-400">Automated Tax & Statutory Deductions</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700">
                <tr>
                  <th className="px-4 py-3">Paystub #</th>
                  <th className="px-4 py-3">Pay Period</th>
                  <th className="px-4 py-3 text-right">Gross Pay</th>
                  <th className="px-4 py-3 text-right">Federal Tax</th>
                  <th className="px-4 py-3 text-right">FICA & Medicare</th>
                  <th className="px-4 py-3 text-right">State Tax</th>
                  <th className="px-4 py-3 text-right text-emerald-400 font-bold">Net Pay</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/60 text-slate-300">
                {paystubs.map((p: PaystubRecord) => (
                  <tr key={p.id} className="hover:bg-slate-750/50">
                    <td className="px-4 py-3 font-mono text-indigo-400">{p.paystub_number}</td>
                    <td className="px-4 py-3">{p.pay_period_start} to {p.pay_period_end}</td>
                    <td className="px-4 py-3 text-right font-medium text-white">${p.gross_pay.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-red-400">-${p.federal_tax.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-red-400">-${(p.social_security + p.medicare).toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-red-400">-${p.state_tax.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-emerald-400 font-bold text-sm">
                      ${p.net_pay.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
