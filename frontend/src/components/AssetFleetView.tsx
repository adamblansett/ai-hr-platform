import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { HardwareAsset, FleetSummary } from '../types';

export const AssetFleetView: React.FC = () => {
  const [assets, setAssets] = useState<HardwareAsset[]>([]);
  const [fleetSummary, setFleetSummary] = useState<FleetSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [showWipeModal, setShowWipeModal] = useState<string | null>(null);
  const [wipeReason, setWipeReason] = useState<string>('Offboarding / Device reclamation protocol');

  // Form state
  const [assetTag, setAssetTag] = useState('');
  const [serialNumber, setSerialNumber] = useState('');
  const [deviceModel, setDeviceModel] = useState('');
  const [category, setCategory] = useState('LAPTOP');
  const [purchaseDate, setPurchaseDate] = useState('2026-01-15');
  const [warrantyExpiry, setWarrantyExpiry] = useState('2029-01-15');
  const [mdmProvider, setMdmProvider] = useState('JAMF_PRO');
  const [notes, setNotes] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [assetList, summary] = await Promise.all([
        api.getHardwareAssets(),
        api.getFleetSummary(),
      ]);
      setAssets(assetList);
      setFleetSummary(summary);
    } catch (err) {
      console.error('Failed to load asset fleet', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assetTag || !serialNumber || !deviceModel) return;

    try {
      await api.createHardwareAsset({
        asset_tag: assetTag,
        serial_number: serialNumber,
        device_model: deviceModel,
        category,
        purchase_date: purchaseDate,
        warranty_expiry: warrantyExpiry,
        device_condition: 'EXCELLENT',
        mdm_provider: mdmProvider,
        notes,
      });
      setShowAddModal(false);
      setAssetTag('');
      setSerialNumber('');
      setDeviceModel('');
      setNotes('');
      fetchData();
    } catch (err) {
      alert('Failed to register asset: ' + err);
    }
  };

  const handleAssign = async (assetId: string) => {
    try {
      await api.assignHardwareAsset(assetId, 'emp-001');
      fetchData();
    } catch (err) {
      alert('Assign failed: ' + err);
    }
  };

  const handleUnassign = async (assetId: string) => {
    try {
      await api.unassignHardwareAsset(assetId);
      fetchData();
    } catch (err) {
      alert('Unassign failed: ' + err);
    }
  };

  const handleRemoteWipe = async (assetId: string) => {
    try {
      await api.triggerRemoteWipe(assetId, wipeReason);
      setShowWipeModal(null);
      fetchData();
    } catch (err) {
      alert('Remote wipe failed: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>💻</span> Enterprise Hardware & IT Fleet Management
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Workstation lifecycle, Jamf & Intune MDM enrollment, serial tracking, and remote cryptographic zero-touch wipe.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          + Provision New Asset
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Fleet Assets</div>
          <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {fleetSummary ? fleetSummary.total_assets : '—'}
          </div>
          <div className="mt-1 text-xs text-indigo-500 font-medium">Enterprise inventory register</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Assigned Workstations</div>
          <div className="mt-1 text-2xl font-bold text-blue-600 dark:text-blue-400">
            {fleetSummary ? fleetSummary.assigned_assets : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Active employee custody</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">In-Stock Spares</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {fleetSummary ? fleetSummary.in_stock_assets : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Staged for onboarding</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">MDM Compliance Rate</div>
          <div className="mt-1 text-2xl font-bold text-green-500">
            {fleetSummary ? `${fleetSummary.mdm_compliance_rate}%` : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Jamf / Intune enforced</div>
        </div>
      </div>

      {/* Assets Register Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-gray-900 dark:text-white">Hardware Asset Directory</h3>
          <span className="text-xs text-gray-500">{assets.length} Devices</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Scanning fleet registry...</div>
        ) : assets.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No hardware registered. Add your first machine above!</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium">
                <tr>
                  <th className="px-6 py-3">Tag & Serial #</th>
                  <th className="px-6 py-3">Device Model</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Assigned To</th>
                  <th className="px-6 py-3">MDM Provider</th>
                  <th className="px-6 py-3">Remote Security</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {assets.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900 dark:text-white">{a.asset_tag}</div>
                      <div className="text-xs text-gray-400 font-mono">{a.serial_number}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">{a.device_model}</div>
                      <div className="text-xs text-gray-400">{a.category} • {a.device_condition}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                          a.status === 'ASSIGNED'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {a.assigned_to_name ? (
                        <div className="font-medium text-gray-900 dark:text-white">{a.assigned_to_name}</div>
                      ) : (
                        <span className="text-gray-400 italic">Unassigned (In-Stock)</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${
                          a.mdm_enrolled
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {a.mdm_provider}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {a.remote_wipe_status === 'COMMAND_SENT' ? (
                        <span className="px-2 py-0.5 text-xs font-bold rounded bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300">
                          WIPE IN-FLIGHT
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Secured</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {a.status === 'IN_STOCK' ? (
                        <button
                          onClick={() => handleAssign(a.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 rounded"
                        >
                          Assign
                        </button>
                      ) : (
                        <button
                          onClick={() => handleUnassign(a.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 rounded"
                        >
                          Return
                        </button>
                      )}
                      {a.mdm_enrolled && a.remote_wipe_status !== 'COMMAND_SENT' && (
                        <button
                          onClick={() => setShowWipeModal(a.id)}
                          className="px-2.5 py-1 text-xs font-medium bg-rose-600 text-white hover:bg-rose-700 rounded"
                        >
                          Remote Wipe
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

      {/* Provision Asset Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Provision Hardware Asset</h3>
            <form onSubmit={handleAddAsset} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Asset Tag</label>
                  <input
                    type="text"
                    required
                    value={assetTag}
                    onChange={(e) => setAssetTag(e.target.value)}
                    placeholder="TAG-MBP-8920"
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Serial Number</label>
                  <input
                    type="text"
                    required
                    value={serialNumber}
                    onChange={(e) => setSerialNumber(e.target.value)}
                    placeholder="C02G..."
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Device Model Specification</label>
                <input
                  type="text"
                  required
                  value={deviceModel}
                  onChange={(e) => setDeviceModel(e.target.value)}
                  placeholder="Apple MacBook Pro 16&quot; M3 Max"
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
                    <option value="LAPTOP">Laptop / Workstation</option>
                    <option value="MONITOR">Monitor / Display</option>
                    <option value="MOBILE">Mobile Phone</option>
                    <option value="SECURITY_KEY">Hardware Security Key</option>
                    <option value="ACCESSORY">Docking Station / Accessory</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">MDM Provider</label>
                  <select
                    value={mdmProvider}
                    onChange={(e) => setMdmProvider(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  >
                    <option value="JAMF_PRO">Jamf Pro (macOS/iOS)</option>
                    <option value="MICROSOFT_INTUNE">Microsoft Intune (Windows)</option>
                    <option value="KANDJI">Kandji</option>
                    <option value="UNMANAGED">Unmanaged Device</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Purchase Date</label>
                  <input
                    type="date"
                    required
                    value={purchaseDate}
                    onChange={(e) => setPurchaseDate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Warranty Expiry</label>
                  <input
                    type="date"
                    required
                    value={warrantyExpiry}
                    onChange={(e) => setWarrantyExpiry(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
                >
                  Provision Device
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Remote Wipe Confirmation Modal */}
      {showWipeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-red-600 flex items-center gap-2">
              <span>⚠️</span> Confirm Remote Device Wipe
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              This action will dispatch a cryptographic remote sanitization command via the active MDM gateway. 
              All onboard NVMe storage will be erased on next network contact.
            </p>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Wipe Justification</label>
              <input
                type="text"
                required
                value={wipeReason}
                onChange={(e) => setWipeReason(e.target.value)}
                className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-3">
              <button
                type="button"
                onClick={() => setShowWipeModal(null)}
                className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleRemoteWipe(showWipeModal)}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg"
              >
                Execute Remote Wipe
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
