import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { TenantBrandingConfig, DomainVerificationResult } from '../types';

export const TenantBrandingView: React.FC = () => {
  const [branding, setBranding] = useState<TenantBrandingConfig | null>(null);
  const [verificationResult, setVerificationResult] = useState<DomainVerificationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);

  // Form state
  const [companyName, setCompanyName] = useState('');
  const [customDomain, setCustomDomain] = useState('');
  const [portalTitle, setPortalTitle] = useState('');
  const [supportEmail, setSupportEmail] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#4F46E5');
  const [secondaryColor, setSecondaryColor] = useState('#10B981');
  const [logoUrl, setLogoUrl] = useState('');

  const fetchBranding = async () => {
    try {
      setLoading(true);
      const data = await api.getTenantBranding('org-001');
      setBranding(data);
      setCompanyName(data.company_name);
      setCustomDomain(data.custom_domain);
      setPortalTitle(data.portal_title);
      setSupportEmail(data.support_email);
      setPrimaryColor(data.primary_color_hex);
      setSecondaryColor(data.secondary_color_hex);
      setLogoUrl(data.logo_url);
    } catch (err) {
      console.error('Failed to load branding', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranding();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const updated = await api.updateTenantBranding({
        company_name: companyName,
        custom_domain: customDomain,
        portal_title: portalTitle,
        support_email: supportEmail,
        primary_color_hex: primaryColor,
        secondary_color_hex: secondaryColor,
        logo_url: logoUrl,
      });
      setBranding(updated);
      alert('Tenant white-label branding saved successfully!');
    } catch (err) {
      alert('Save failed: ' + err);
    } finally {
      setSaving(false);
    }
  };

  const handleVerifyDomain = async () => {
    try {
      const res = await api.verifyCustomDomain('org-001');
      setVerificationResult(res);
      fetchBranding();
    } catch (err) {
      alert('Domain verification failed: ' + err);
    }
  };

  if (loading || !branding) {
    return <div className="p-8 text-center text-gray-500">Loading enterprise tenant settings...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <span>🎨</span> Multi-Tenant Enterprise White-Labeling & Domain Routing
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          White-label customer portals, custom CNAME domain routing with automated TLS, and dedicated KMS encryption key isolation.
        </p>
      </div>

      {/* Verification Alert */}
      {verificationResult && (
        <div className="p-4 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/40 text-green-800 dark:text-green-300 flex justify-between items-center text-xs">
          <div>{verificationResult.message}</div>
          <button onClick={() => setVerificationResult(null)} className="font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid: Form (2 cols) & Live Preview (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Form */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm space-y-6">
          <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <span>⚙️</span> Portal Branding & Visual Palette
          </h3>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Company Legal Name</label>
                <input
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Portal Display Title</label>
                <input
                  type="text"
                  required
                  value={portalTitle}
                  onChange={(e) => setPortalTitle(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Corporate Support Email</label>
                <input
                  type="email"
                  required
                  value={supportEmail}
                  onChange={(e) => setSupportEmail(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Logo URL (.svg or .png)</label>
                <input
                  type="url"
                  value={logoUrl}
                  onChange={(e) => setLogoUrl(e.target.value)}
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Primary Brand Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={primaryColor}
                    onChange={(e) => setPrimaryColor(e.target.value)}
                    className="w-10 h-10 rounded border border-gray-300 cursor-pointer"
                  />
                  <input
                    type="text"
                    value={primaryColor}
                    onChange={(e) => setPrimaryColor(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 font-mono text-gray-900 dark:text-white"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Accent / Success Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={secondaryColor}
                    onChange={(e) => setSecondaryColor(e.target.value)}
                    className="w-10 h-10 rounded border border-gray-300 cursor-pointer"
                  />
                  <input
                    type="text"
                    value={secondaryColor}
                    onChange={(e) => setSecondaryColor(e.target.value)}
                    className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 font-mono text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            </div>

            {/* Custom Domain Section */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
              <h4 className="font-semibold text-xs text-gray-900 dark:text-white uppercase tracking-wider">
                Custom Domain & TLS Ingress
              </h4>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={customDomain}
                  onChange={(e) => setCustomDomain(e.target.value)}
                  placeholder="people.yourcompany.com"
                  className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                />
                <button
                  type="button"
                  onClick={handleVerifyDomain}
                  className="px-4 py-2 text-xs font-medium bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg whitespace-nowrap"
                >
                  Verify CNAME
                </button>
              </div>

              <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700 text-xs space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">Domain Status:</span>
                  <span className={`font-bold ${branding.custom_domain_verified ? 'text-green-600' : 'text-amber-500'}`}>
                    {branding.custom_domain_verified ? '✓ ACTIVE & VERIFIED' : 'PENDING DNS CNAME'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">TLS Certificate:</span>
                  <span className="font-mono text-indigo-500 font-bold">{branding.ssl_cert_status}</span>
                </div>
                <div className="text-[11px] text-gray-400 pt-1">
                  CNAME Target: <span className="font-mono text-gray-700 dark:text-gray-300">ingress.global.ai-hr-platform.cloud</span>
                </div>
              </div>
            </div>

            {/* KMS Encryption Key */}
            <div className="pt-2">
              <div className="text-xs text-gray-500">Dedicated Tenant KMS Key:</div>
              <div className="font-mono text-[11px] text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-900 px-3 py-1.5 rounded-lg mt-1 truncate">
                {branding.kms_key_id}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm"
              >
                {saving ? 'Saving...' : 'Apply Brand Theme'}
              </button>
            </div>
          </form>
        </div>

        {/* Live White-Label Preview Card */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <span>👁️</span> Live Portal Preview
            </h3>

            {/* Mock Branded Header */}
            <div className="rounded-xl overflow-hidden border border-gray-300 dark:border-gray-700 shadow-md">
              <div
                className="p-4 flex items-center justify-between text-white"
                style={{ backgroundColor: primaryColor }}
              >
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded bg-white/20 flex items-center justify-center font-bold text-xs">
                    {companyName.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="font-bold text-sm tracking-wide">{portalTitle}</div>
                </div>
                <span
                  className="px-2 py-0.5 text-[10px] font-bold rounded-full text-white"
                  style={{ backgroundColor: secondaryColor }}
                >
                  LIVE
                </span>
              </div>

              {/* Mock Dashboard Body */}
              <div className="p-4 bg-gray-50 dark:bg-gray-900 text-xs space-y-3">
                <div className="font-semibold text-gray-700 dark:text-gray-300">
                  Welcome to {companyName}!
                </div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 space-y-1">
                  <div className="text-[11px] text-gray-500">Corporate Portal Route</div>
                  <div className="font-mono text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                    https://{customDomain}
                  </div>
                </div>
                <div className="flex justify-between items-center text-[11px] text-gray-400 pt-1">
                  <span>Support: {supportEmail}</span>
                  <span className="font-mono text-green-600">TLS Secured</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
