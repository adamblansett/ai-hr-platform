import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SafetyIncident, OSHA300LogSummary } from '../types';

export const SafetyComplianceView: React.FC = () => {
  const [incidents, setIncidents] = useState<SafetyIncident[]>([]);
  const [oshaLog, setOshaLog] = useState<OSHA300LogSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [selectedIncident, setSelectedIncident] = useState<SafetyIncident | null>(null);

  // Form state
  const [incidentType, setIncidentType] = useState('INJURY');
  const [severity, setSeverity] = useState('MEDICAL_TREATMENT');
  const [incidentDate, setIncidentDate] = useState('2026-11-22');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [lostWorkdays, setLostWorkdays] = useState('0');
  const [restrictedDays, setRestrictedDays] = useState('0');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [incList, oshaSummary] = await Promise.all([
        api.getSafetyIncidents(),
        api.getOsha300Log(2026),
      ]);
      setIncidents(incList);
      setOshaLog(oshaSummary);
    } catch (err) {
      console.error('Failed to load safety data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleReportIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!location || !description) return;

    try {
      await api.reportSafetyIncident({
        employee_id: 'emp-001',
        incident_type: incidentType,
        severity,
        incident_date: incidentDate,
        location,
        description,
        lost_workday_count: parseInt(lostWorkdays) || 0,
        restricted_days_count: parseInt(restrictedDays) || 0,
      });
      setShowReportModal(false);
      setLocation('');
      setDescription('');
      setLostWorkdays('0');
      setRestrictedDays('0');
      fetchData();
    } catch (err) {
      alert('Failed to report incident: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🛡️</span> Workplace Health, Safety & OSHA Incident Tracker
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            29 CFR 1904 compliance auditing, automated OSHA 300 log generation, and AI 5-Whys root-cause hazard mitigation.
          </p>
        </div>
        <button
          onClick={() => setShowReportModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
        >
          + Report Safety Incident
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">OSHA Recordable Cases (2026)</div>
          <div className="mt-1 text-2xl font-bold text-red-600 dark:text-red-400">
            {oshaLog ? oshaLog.osha_recordable_cases : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">29 CFR Part 1904.7 standard</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Lost Workdays</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {oshaLog ? oshaLog.total_lost_workdays : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Days away from work</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Restricted / Transfer Days</div>
          <div className="mt-1 text-2xl font-bold text-blue-500">
            {oshaLog ? oshaLog.total_restricted_days : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Modified duty days</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Lost Workday Rate (LWDR)</div>
          <div className="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {oshaLog ? oshaLog.lost_workday_rate : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Per 200,000 labor hours</div>
        </div>
      </div>

      {/* Incident Detail / AI Root Cause Modal */}
      {selectedIncident && (
        <div className="p-5 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-red-900 dark:text-red-200 flex items-center gap-2">
              <span>🔬</span> AI Root-Cause Analysis & Action Plan ({selectedIncident.id})
            </h3>
            <button
              onClick={() => setSelectedIncident(null)}
              className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              Close ✕
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <span className="font-semibold text-gray-700 dark:text-gray-300">Location:</span> {selectedIncident.location}
            </div>
            <div>
              <span className="font-semibold text-gray-700 dark:text-gray-300">OSHA Case #:</span> {selectedIncident.osha_case_number || 'N/A (Non-recordable)'}
            </div>
          </div>

          <div className="text-xs text-gray-700 dark:text-gray-300">
            <span className="font-semibold">Incident Narrative:</span> {selectedIncident.description}
          </div>

          {selectedIncident.ai_root_cause_analysis && (
            <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-red-200 dark:border-red-900">
              <div className="font-semibold text-red-800 dark:text-red-300 text-xs mb-1">Root Cause Synthesis (5-Whys):</div>
              <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{selectedIncident.ai_root_cause_analysis}</p>
            </div>
          )}

          {selectedIncident.corrective_actions && (
            <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="font-semibold text-gray-900 dark:text-white text-xs mb-1">Corrective Engineering Controls:</div>
              <pre className="text-xs text-gray-600 dark:text-gray-300 font-sans whitespace-pre-line">{selectedIncident.corrective_actions}</pre>
            </div>
          )}
        </div>
      )}

      {/* Incidents Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">OSHA Form 300 Incident Register</h3>
          <span className="text-xs text-gray-500">{incidents.length} Records</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading OSHA logs...</div>
        ) : incidents.length === 0 ? (
          <div className="p-8 text-center text-gray-500">Zero safety incidents reported. Safe workplace achieved!</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Case / Incident ID</th>
                  <th className="px-6 py-3">Type & Severity</th>
                  <th className="px-6 py-3">Date & Facility</th>
                  <th className="px-6 py-3">OSHA Recordable</th>
                  <th className="px-6 py-3">Lost / Restricted</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {incidents.map((inc) => (
                  <tr key={inc.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">{inc.osha_case_number || inc.id}</div>
                      <div className="text-xs text-gray-400 font-mono">{inc.id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">{inc.incident_type}</div>
                      <div className="text-xs text-gray-400">{inc.severity}</div>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <div>{inc.incident_date}</div>
                      <div className="text-gray-400">{inc.location}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          inc.is_osha_recordable
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                            : 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                        }`}
                      >
                        {inc.is_osha_recordable ? 'RECORDABLE' : 'NON-RECORDABLE'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {inc.lost_workday_count} lost / {inc.restricted_days_count} restricted
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                        {inc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedIncident(inc)}
                        className="px-2.5 py-1 text-xs font-medium bg-red-50 text-red-700 dark:bg-red-900/40 dark:text-red-300 hover:bg-red-100 rounded"
                      >
                        Root Cause
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Report Incident Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-lg w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Report Workplace Safety Incident</h3>
            <form onSubmit={handleReportIncident} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Incident Type</label>
                  <select
                    value={incidentType}
                    onChange={(e) => setIncidentType(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="INJURY">Physical Injury</option>
                    <option value="ILLNESS">Occupational Illness</option>
                    <option value="NEAR_MISS">Near-Miss Hazard</option>
                    <option value="ENVIRONMENTAL">Environmental Spill</option>
                    <option value="PROPERTY_DAMAGE">Property Damage</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Severity Tier</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="FIRST_AID">First Aid Only</option>
                    <option value="MEDICAL_TREATMENT">Medical Treatment beyond First Aid</option>
                    <option value="RESTRICTED_DUTY">Restricted Duty / Transfer</option>
                    <option value="DAYS_AWAY">Days Away from Work</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Incident Date</label>
                  <input
                    type="date"
                    required
                    value={incidentDate}
                    onChange={(e) => setIncidentDate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Facility / Location</label>
                  <input
                    type="text"
                    required
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Bldg B Loading Dock"
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Lost Workdays</label>
                  <input
                    type="number"
                    min="0"
                    value={lostWorkdays}
                    onChange={(e) => setLostWorkdays(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Restricted Days</label>
                  <input
                    type="number"
                    min="0"
                    value={restrictedDays}
                    onChange={(e) => setRestrictedDays(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Incident Description & Sequence</label>
                <textarea
                  rows={3}
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Detail what occurred, equipment involved, and injuries sustained..."
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg"
                >
                  Submit Incident Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
