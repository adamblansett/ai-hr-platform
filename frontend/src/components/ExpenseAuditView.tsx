import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ExpenseReport, ExpenseAuditResult } from '../types';

export const ExpenseAuditView: React.FC = () => {
  const [reports, setReports] = useState<ExpenseReport[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedAudit, setSelectedAudit] = useState<ExpenseAuditResult | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);

  // New report form state
  const [title, setTitle] = useState('');
  const [merchant, setMerchant] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('MEALS');
  const [expenseDate, setExpenseDate] = useState('2026-11-22');
  const [receiptUrl, setReceiptUrl] = useState('');
  const [description, setDescription] = useState('');

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await api.getExpenseReports();
      setReports(data);
    } catch (err) {
      console.error('Failed to fetch expense reports', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleAudit = async (reportId: string) => {
    try {
      const res = await api.auditExpenseReport(reportId);
      setSelectedAudit(res);
      fetchReports();
    } catch (err) {
      alert('Audit failed: ' + err);
    }
  };

  const handleSubmit = async (reportId: string) => {
    try {
      await api.submitExpenseReport(reportId);
      fetchReports();
    } catch (err) {
      alert('Failed to submit: ' + err);
    }
  };

  const handleApprove = async (reportId: string) => {
    try {
      await api.approveExpenseReport(reportId);
      fetchReports();
    } catch (err) {
      alert('Failed to approve: ' + err);
    }
  };

  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !merchant || !amount) return;

    try {
      await api.createExpenseReport({
        employee_id: 'emp-001',
        title,
        items: [
          {
            category,
            amount: parseFloat(amount),
            currency: 'USD',
            expense_date: expenseDate,
            merchant,
            description,
            receipt_url: receiptUrl || undefined,
          },
        ],
      });
      setShowCreateModal(false);
      setTitle('');
      setMerchant('');
      setAmount('');
      setDescription('');
      setReceiptUrl('');
      fetchReports();
    } catch (err) {
      alert('Failed to create report: ' + err);
    }
  };

  const totalAmount = reports.reduce((acc, r) => acc + r.total_amount, 0);
  const compliantCount = reports.filter((r) => r.audit_status === 'COMPLIANT').length;
  const passRate = reports.length > 0 ? Math.round((compliantCount / reports.length) * 100) : 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>💳</span> Expense Reimbursement & OCR Policy Auditor
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Autonomous multi-tier travel & per-diem policy audit, instant receipt itemization, and automated payout disbursement.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          + File Expense Report
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Outlay Audited</div>
          <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">${totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
          <div className="mt-1 text-xs text-indigo-500 font-medium">Enterprise multi-currency pipeline</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Reports Under Review</div>
          <div className="mt-1 text-2xl font-bold text-yellow-500">{reports.filter((r) => r.status === 'SUBMITTED' || r.status === 'DRAFT').length}</div>
          <div className="mt-1 text-xs text-gray-400">Pending manager sign-off</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">AI Compliance Pass Rate</div>
          <div className="mt-1 text-2xl font-bold text-green-500">{passRate}%</div>
          <div className="mt-1 text-xs text-green-600 dark:text-green-400">Zero audit leakage</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Reimbursed to Date</div>
          <div className="mt-1 text-2xl font-bold text-blue-500">
            ${reports.filter((r) => r.status === 'APPROVED').reduce((acc, r) => acc + r.total_amount, 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="mt-1 text-xs text-gray-400">Automated ACH batches</div>
        </div>
      </div>

      {/* Audit Modal/Alert if open */}
      {selectedAudit && (
        <div className="p-5 rounded-xl border border-indigo-200 dark:border-indigo-900 bg-indigo-50 dark:bg-indigo-950/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-indigo-900 dark:text-indigo-200 flex items-center gap-2">
              <span>🤖</span> AI Policy Audit Breakdown (Report: {selectedAudit.report_id})
            </h3>
            <button
              onClick={() => setSelectedAudit(null)}
              className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              Close ✕
            </button>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                selectedAudit.overall_status === 'COMPLIANT'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                  : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
              }`}
            >
              Status: {selectedAudit.overall_status}
            </span>
            <span className="text-xs text-gray-600 dark:text-gray-300">
              Audited Outlay: ${selectedAudit.total_audited.toFixed(2)} | Flagged Items: {selectedAudit.flagged_items_count}
            </span>
          </div>

          {selectedAudit.flags.length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-bold text-red-700 dark:text-red-300">Policy Flags Triggered:</div>
              <ul className="list-disc list-inside text-xs text-red-600 dark:text-red-400 space-y-0.5">
                {selectedAudit.flags.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {selectedAudit.remediation_actions.length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-bold text-indigo-800 dark:text-indigo-300">Recommended Remediation:</div>
              <ul className="list-disc list-inside text-xs text-indigo-700 dark:text-indigo-300 space-y-0.5">
                {selectedAudit.remediation_actions.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Reports Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Active & Historical Expense Reports</h3>
          <span className="text-xs text-gray-500">{reports.length} Reports</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading expense ledger...</div>
        ) : reports.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No expense reports recorded. File one above!</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Report Title & ID</th>
                  <th className="px-6 py-3">Total Amount</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">AI Audit</th>
                  <th className="px-6 py-3">Line Items</th>
                  <th className="px-6 py-3">Payout Reference</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">{r.title}</div>
                      <div className="text-xs text-gray-400 font-mono">{r.id}</div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-gray-900 dark:text-white">
                      ${r.total_amount.toFixed(2)} {r.currency}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                          r.status === 'APPROVED'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                            : r.status === 'SUBMITTED'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-0.5 text-xs font-semibold rounded ${
                          r.audit_status === 'COMPLIANT'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                            : r.audit_status === 'FLAGGED'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {r.audit_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      {r.items.length} item(s) • {r.items.map((i) => i.merchant).join(', ')}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-indigo-500">
                      {r.reimbursement_reference || '—'}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => handleAudit(r.id)}
                        className="px-2.5 py-1 text-xs font-medium bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 hover:bg-indigo-100 rounded"
                      >
                        Inspect
                      </button>
                      {r.status === 'DRAFT' && (
                        <button
                          onClick={() => handleSubmit(r.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 rounded"
                        >
                          Submit
                        </button>
                      )}
                      {r.status === 'SUBMITTED' && (
                        <button
                          onClick={() => handleApprove(r.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-green-600 text-white hover:bg-green-700 rounded"
                        >
                          Approve Payout
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

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create New Expense Report</h3>
            <form onSubmit={handleCreateReport} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Report Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Q4 Client Workshop"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="MEALS">Meals & Per Diem</option>
                    <option value="TRAVEL">Flight & Rail</option>
                    <option value="LODGING">Hotel & Lodging</option>
                    <option value="SOFTWARE">Software & Tools</option>
                    <option value="OFFICE_SUPPLIES">Office Supplies</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Amount ($ USD)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="65.00"
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Merchant</label>
                  <input
                    type="text"
                    required
                    value={merchant}
                    onChange={(e) => setMerchant(e.target.value)}
                    placeholder="e.g. Sweetgreen"
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Expense Date</label>
                  <input
                    type="date"
                    required
                    value={expenseDate}
                    onChange={(e) => setExpenseDate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Receipt URL (Mandatory &gt; $25)</label>
                <input
                  type="url"
                  value={receiptUrl}
                  onChange={(e) => setReceiptUrl(e.target.value)}
                  placeholder="https://storage.local/receipts/rec.pdf"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Business Description</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the business purpose..."
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
                >
                  Save Expense
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
