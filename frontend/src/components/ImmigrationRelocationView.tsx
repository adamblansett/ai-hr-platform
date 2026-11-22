import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ImmigrationCase, ImmigrationSummary } from '../types';

export const ImmigrationRelocationView: React.FC = () => {
  const [cases, setCases] = useState<ImmigrationCase[]>([]);
  const [summary, setSummary] = useState<ImmigrationSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showCaseModal, setShowCaseModal] = useState<boolean>(false);
  const [disbursementMessage, setDisbursementMessage] = useState<string | null>(null);

  // Form state
  const [employeeId, setEmployeeId] = useState('emp-001');
  const [visaType, setVisaType] = useState('H1B');
  const [expiryDate, setExpiryDate] = useState('2029-09-30');
  const [receiptNumber, setReceiptNumber] = useState('');
  const [stipendAmount, setStipendAmount] = useState('10000');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [caseList, sumData] = await Promise.all([
        api.getImmigrationCases(),
        api.getImmigrationSummary(),
      ]);
      setCases(caseList);
      setSummary(sumData);
    } catch (err) {
      console.error('Failed to load immigration cases', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createImmigrationCase({
        employee_id: employeeId,
        visa_type: visaType,
        expiry_date: expiryDate,
        uscis_receipt_number: receiptNumber || undefined,
        relocation_stipend_amount: parseFloat(stipendAmount) || 10000.0,
      });
      setShowCaseModal(false);
      setReceiptNumber('');
      fetchData();
    } catch (err) {
      alert('Failed to initiate visa petition: ' + err);
    }
  };

  const handleAdvanceStatus = async (caseId: string, currentStatus: string) => {
    let nextStatus = 'USCIS_SUBMITTED';
    if (currentStatus === 'INTAKE') nextStatus = 'DOL_PREVAILING_WAGE';
    else if (currentStatus === 'DOL_PREVAILING_WAGE') nextStatus = 'USCIS_SUBMITTED';
    else if (currentStatus === 'USCIS_SUBMITTED') nextStatus = 'APPROVED';

    try {
      await api.updateImmigrationStatus(caseId, nextStatus);
      fetchData();
    } catch (err) {
      alert('Status update failed: ' + err);
    }
  };

  const handleDisburseStipend = async (caseId: string) => {
    try {
      const res = await api.disburseRelocationStipend(caseId);
      setDisbursementMessage(res.message);
      fetchData();
    } catch (err) {
      alert('Disbursement failed: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🛂</span> Visa, Global Immigration & Relocation Hub
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            H-1B/L-1/O-1 petition tracking, USCIS receipt integration, document verification, and tax gross-up relocation stipends.
          </p>
        </div>
        <button
          onClick={() => setShowCaseModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          + Initiate Visa Petition
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Legal Cases</div>
          <div className="mt-1 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {summary ? summary.active_cases : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Global mobility portfolio</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">USCIS Pending Adjudication</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {summary ? summary.pending_uscis_receipts : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">California & Nebraska Centers</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Expiring in &lt; 90 Days</div>
          <div className="mt-1 text-2xl font-bold text-green-500">
            {summary ? summary.expiring_within_90_days_count : 0}
          </div>
          <div className="mt-1 text-xs text-gray-400">Zero immediate lapse risks</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Relocation Outlay</div>
          <div className="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            ${summary ? summary.total_relocation_outlay.toLocaleString() : '0'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Grossed-up relocation funds</div>
        </div>
      </div>

      {/* Disbursement Alert */}
      {disbursementMessage && (
        <div className="p-4 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/40 text-green-800 dark:text-green-300 flex justify-between items-center text-xs">
          <div>{disbursementMessage}</div>
          <button onClick={() => setDisbursementMessage(null)} className="font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Immigration Cases Register */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Active Visa Petitions & Document Checklists</h3>
          <span className="text-xs text-gray-500">{cases.length} Petitions</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading immigration petitions...</div>
        ) : cases.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No immigration cases currently active.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Employee & Petition Type</th>
                  <th className="px-6 py-3">USCIS Receipt #</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Expiry Date</th>
                  <th className="px-6 py-3">Relocation Stipend</th>
                  <th className="px-6 py-3">Verified Docs</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900 dark:text-white">{c.employee_name || c.employee_id}</div>
                      <div className="text-xs text-indigo-500 font-bold">{c.visa_type} Petition</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-gray-900 dark:text-white">
                      {c.uscis_receipt_number || <span className="text-gray-400 italic">Pre-filing</span>}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          c.case_status === 'APPROVED'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                            : c.case_status === 'USCIS_SUBMITTED'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                        }`}
                      >
                        {c.case_status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-mono">
                      {c.expiry_date}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <div>${c.relocation_stipend_amount.toLocaleString()} + ${c.tax_gross_up_amount.toLocaleString()} tax</div>
                      <span className={`text-[10px] font-bold ${c.stipend_disbursed ? 'text-green-600' : 'text-amber-500'}`}>
                        {c.stipend_disbursed ? '✓ DISBURSED' : 'PENDING APPROVAL'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {c.documents.length} verified doc(s)
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {!c.stipend_disbursed && (
                        <button
                          onClick={() => handleDisburseStipend(c.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-emerald-600 text-white hover:bg-emerald-700 rounded"
                        >
                          Disburse Stipend
                        </button>
                      )}
                      {c.case_status !== 'APPROVED' && (
                        <button
                          onClick={() => handleAdvanceStatus(c.id, c.case_status)}
                          className="px-2.5 py-1 text-xs font-medium bg-indigo-600 text-white hover:bg-indigo-700 rounded"
                        >
                          Advance Status
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

      {/* Case Creation Modal */}
      {showCaseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Initiate Immigration Case</h3>
            <form onSubmit={handleCreateCase} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Employee</label>
                <select
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                >
                  <option value="emp-001">Alex Chen</option>
                  <option value="emp-002">Sarah Miller</option>
                  <option value="emp-004">Elena Rostova</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Visa Classification</label>
                  <select
                    value={visaType}
                    onChange={(e) => setVisaType(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="H1B">H-1B Specialty Occupation</option>
                    <option value="O1">O-1 Extraordinary Ability</option>
                    <option value="L1A">L-1A Intracompany Manager</option>
                    <option value="L1B">L-1B Specialized Knowledge</option>
                    <option value="TN">TN USMCA Professional</option>
                    <option value="PERM_GREEN_CARD">PERM Permanent Residency</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Expiry Date</label>
                  <input
                    type="date"
                    required
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">USCIS Receipt Number (if issued)</label>
                <input
                  type="text"
                  value={receiptNumber}
                  onChange={(e) => setReceiptNumber(e.target.value)}
                  placeholder="e.g. WAC-26-901-44120"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Relocation Stipend ($ USD)</label>
                <input
                  type="number"
                  value={stipendAmount}
                  onChange={(e) => setStipendAmount(e.target.value)}
                  placeholder="10000"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
                <div className="text-[10px] text-gray-400 mt-1">32% tax gross-up will automatically be calculated on disbursement.</div>
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCaseModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
                >
                  Create Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
