import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  ContractorProfile,
  ContractorSOW,
  MilestoneInvoice,
  EORSummary,
} from '../types';

export const ContractorEorView: React.FC = () => {
  const [contractors, setContractors] = useState<ContractorProfile[]>([]);
  const [sows, setSows] = useState<ContractorSOW[]>([]);
  const [invoices, setInvoices] = useState<MilestoneInvoice[]>([]);
  const [summary, setSummary] = useState<EORSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showAddContractorModal, setShowAddContractorModal] = useState<boolean>(false);
  const [showInvoiceModal, setShowInvoiceModal] = useState<boolean>(false);

  // New Contractor form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [country, setCountry] = useState('Germany');
  const [entityType, setEntityType] = useState('INDIVIDUAL');
  const [taxFormType, setTaxFormType] = useState('W8_BEN');
  const [hourlyRate, setHourlyRate] = useState('85');
  const [currency, setCurrency] = useState('EUR');

  // New Invoice form state
  const [selectedSowId, setSelectedSowId] = useState('');
  const [selectedContractorId, setSelectedContractorId] = useState('');
  const [milestoneTitle, setMilestoneTitle] = useState('');
  const [invoiceAmount, setInvoiceAmount] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [ctrList, sowList, invList, eorData] = await Promise.all([
        api.getContractors(),
        api.getSOWs(),
        api.getContractorInvoices(),
        api.getEORSummary(),
      ]);
      setContractors(ctrList);
      setSows(sowList);
      setInvoices(invList);
      setSummary(eorData);
      if (sowList.length > 0) {
        setSelectedSowId(sowList[0].id);
        setSelectedContractorId(sowList[0].contractor_id);
      }
    } catch (err) {
      console.error('Failed to load EOR data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddContractor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email) return;

    try {
      await api.createContractor({
        full_name: fullName,
        email,
        country,
        entity_type: entityType,
        tax_form_type: taxFormType,
        hourly_rate: parseFloat(hourlyRate) || 75.0,
        currency,
      });
      setShowAddContractorModal(false);
      setFullName('');
      setEmail('');
      fetchData();
    } catch (err) {
      alert('Failed to register contractor: ' + err);
    }
  };

  const handleVerifyTax = async (contractorId: string) => {
    try {
      await api.verifyContractorTax(contractorId);
      fetchData();
    } catch (err) {
      alert('Tax verification failed: ' + err);
    }
  };

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!milestoneTitle || !invoiceAmount || !selectedSowId) return;

    try {
      await api.submitContractorInvoice({
        sow_id: selectedSowId,
        contractor_id: selectedContractorId,
        milestone_title: milestoneTitle,
        amount: parseFloat(invoiceAmount),
        currency: 'EUR',
      });
      setShowInvoiceModal(false);
      setMilestoneTitle('');
      setInvoiceAmount('');
      fetchData();
    } catch (err) {
      alert('Failed to submit invoice: ' + err);
    }
  };

  const handleApproveInvoice = async (invoiceId: string) => {
    try {
      await api.approveContractorInvoice(invoiceId);
      fetchData();
    } catch (err) {
      alert('Invoice approval failed: ' + err);
    }
  };

  const handlePayInvoice = async (invoiceId: string) => {
    try {
      await api.payContractorInvoice(invoiceId);
      fetchData();
    } catch (err) {
      alert('Invoice payout failed: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🌐</span> Global Contractor & Vendor EOR (Employer of Record) Hub
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Multi-currency international talent contracts, automated W-8BEN / W-9 verification, and SEPA/SWIFT milestone disbursements.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowInvoiceModal(true)}
            className="inline-flex items-center px-3.5 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50"
          >
            + New Milestone Invoice
          </button>
          <button
            onClick={() => setShowAddContractorModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            + Onboard Contractor
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Active International Talent</div>
          <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {summary ? summary.active_contractors : '—'}
          </div>
          <div className="mt-1 text-xs text-indigo-500 font-medium">Global cross-border workforce</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Pending Tax Forms</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {summary ? summary.pending_tax_verifications : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">W-8BEN / W-9 audit checks</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Statements of Work</div>
          <div className="mt-1 text-2xl font-bold text-blue-500">
            {summary ? summary.total_active_sows : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">SOW project milestones</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Disbursed This Month</div>
          <div className="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            ${summary ? summary.total_paid_this_month.toLocaleString() : '0'}
          </div>
          <div className="mt-1 text-xs text-gray-400">SEPA & international wires</div>
        </div>
      </div>

      {/* Contractors Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Contractor & Vendor Roster</h3>
          <span className="text-xs text-gray-500">{contractors.length} Contractors</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading contractor records...</div>
        ) : contractors.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No contractors enrolled.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Contractor Name & Email</th>
                  <th className="px-6 py-3">Country & Entity</th>
                  <th className="px-6 py-3">Tax Compliance</th>
                  <th className="px-6 py-3">Hourly Rate</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {contractors.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900 dark:text-white">{c.full_name}</div>
                      <div className="text-xs text-gray-400">{c.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">{c.country}</div>
                      <div className="text-xs text-gray-400">{c.entity_type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          c.tax_form_verified
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                        }`}
                      >
                        {c.tax_form_type} ({c.tax_form_verified ? 'VERIFIED' : 'PENDING AUDIT'})
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-gray-900 dark:text-white">
                      {c.hourly_rate} {c.currency}/hr
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 text-xs font-semibold rounded bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {!c.tax_form_verified && (
                        <button
                          onClick={() => handleVerifyTax(c.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-emerald-600 text-white hover:bg-emerald-700 rounded"
                        >
                          Verify Tax Form
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SOW Milestone Invoices Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Milestone Invoices & Payout Disbursements</h3>
          <span className="text-xs text-gray-500">{invoices.length} Invoices</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
            <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
              <tr>
                <th className="px-6 py-3">Invoice & SOW Title</th>
                <th className="px-6 py-3">Amount</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Submitted</th>
                <th className="px-6 py-3">FX Payout Hash</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900 dark:text-white">{inv.milestone_title}</div>
                    <div className="text-xs text-gray-400 font-mono">SOW: {inv.sow_id}</div>
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-900 dark:text-white">
                    {inv.amount.toLocaleString()} {inv.currency}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                        inv.status === 'PAID'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                          : inv.status === 'APPROVED'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
                      }`}
                    >
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">
                    {new Date(inv.submitted_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-indigo-500">
                    {inv.payout_tx_hash || '—'}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {inv.status === 'SUBMITTED' && (
                      <button
                        onClick={() => handleApproveInvoice(inv.id)}
                        className="px-2.5 py-1 text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 rounded"
                      >
                        Approve
                      </button>
                    )}
                    {inv.status === 'APPROVED' && (
                      <button
                        onClick={() => handlePayInvoice(inv.id)}
                        className="px-2.5 py-1 text-xs font-medium bg-emerald-600 text-white hover:bg-emerald-700 rounded"
                      >
                        Execute Wire Payout
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Onboard Contractor Modal */}
      {showAddContractorModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Onboard Global Contractor</h3>
            <form onSubmit={handleAddContractor} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Full Legal Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Maria Gonzalez"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Corporate / Contact Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="maria@iberiadev.es"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
                  <input
                    type="text"
                    required
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Entity Type</label>
                  <select
                    value={entityType}
                    onChange={(e) => setEntityType(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="INDIVIDUAL">Individual (Sole Prop)</option>
                    <option value="LLC">LLC / Ltd</option>
                    <option value="C_CORP">Corporation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Tax Form</label>
                  <select
                    value={taxFormType}
                    onChange={(e) => setTaxFormType(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="W8_BEN">W-8BEN (Foreign Individual)</option>
                    <option value="W8_BEN_E">W-8BEN-E (Foreign Entity)</option>
                    <option value="W9">W-9 (US Taxpayer)</option>
                    <option value="VAT_REGISTRATION">EU/UK VAT Registered</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Hourly Rate</label>
                  <input
                    type="number"
                    required
                    value={hourlyRate}
                    onChange={(e) => setHourlyRate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Currency</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="CAD">CAD ($)</option>
                    <option value="JPY">JPY (¥)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddContractorModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
                >
                  Create Contractor Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Invoice Modal */}
      {showInvoiceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Submit Milestone Invoice</h3>
            <form onSubmit={handleCreateInvoice} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Active SOW Agreement</label>
                <select
                  value={selectedSowId}
                  onChange={(e) => setSelectedSowId(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                >
                  {sows.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.title} ({s.total_budget} {s.currency})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Milestone Deliverable Title</label>
                <input
                  type="text"
                  required
                  value={milestoneTitle}
                  onChange={(e) => setMilestoneTitle(e.target.value)}
                  placeholder="e.g. Milestone 3: End-to-end integration tests"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Invoice Amount (€ EUR)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={invoiceAmount}
                  onChange={(e) => setInvoiceAmount(e.target.value)}
                  placeholder="8000.00"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowInvoiceModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
                >
                  Submit Invoice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
