import React, { useState, useEffect } from 'react';
import { Shield, KeyRound, CheckCircle2, AlertTriangle, RefreshCw, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { MFAStatusResponse, MFASetupResponse, OIDCAuthorizeResponse, SSOProviderConfig } from '../types';

export const SecuritySsoMfaView: React.FC = () => {
  const [providers, setProviders] = useState<SSOProviderConfig[]>([]);
  const [mfaStatus, setMfaStatus] = useState<MFAStatusResponse | null>(null);
  const [mfaSetup, setMfaSetup] = useState<MFASetupResponse | null>(null);
  const [oidcPreview, setOidcPreview] = useState<OIDCAuthorizeResponse | null>(null);
  const [totpCode, setTotpCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [providerType, setProviderType] = useState<'OIDC' | 'SAML_2_0'>('OIDC');
  const [providerName, setProviderName] = useState('');
  const [issuerUrl, setIssuerUrl] = useState('');
  const [ssoLoginUrl, setSsoLoginUrl] = useState('');
  const [clientId, setClientId] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [provs, mfa] = await Promise.all([api.getSSOProviders(), api.getMFAStatus('emp-001')]);
      setProviders(provs);
      setMfaStatus(mfa);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load SSO & MFA settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartMFASetup = async () => {
    try {
      setError(null);
      const res = await api.setupMFA('emp-001', 'elena.rostova@acme.corp');
      setMfaSetup(res);
      setMessage('TOTP secret provisioned. Enter a 6-digit code from your authenticator app to activate.');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleVerifyMFA = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      const res = await api.verifyMFA('emp-001', totpCode);
      setMfaStatus(res);
      setMfaSetup(null);
      setTotpCode('');
      setMessage('Two-factor authentication verified and activated.');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleTestOIDC = async (providerId: string) => {
    try {
      setError(null);
      const res = await api.initiateOIDCAuthorize(providerId);
      setOidcPreview(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleAddProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await api.createSSOProvider({
        provider_type: providerType,
        provider_name: providerName,
        issuer_url: issuerUrl,
        sso_login_url: ssoLoginUrl,
        client_id: clientId || undefined,
        enforced_for_admins: true,
      });
      setProviderName('');
      setIssuerUrl('');
      setSsoLoginUrl('');
      setClientId('');
      setMessage('Enterprise SSO provider registered.');
      await loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Enterprise SSO & MFA security console...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-indigo-400" />
            Enterprise SSO (SAML 2.0 / OIDC) & MFA Security
          </h2>
          <p className="text-sm text-slate-400">
            Federated workforce authentication, PKCE S256 OIDC handshakes, XXE-hardened SAML 2.0 assertions, and RFC 6238 TOTP MFA.
          </p>
        </div>
        <button
          onClick={loadData}
          className="inline-flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-medium text-slate-200"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-950/60 border border-red-500/40 text-red-200 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}
      {message && (
        <div className="bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" /> {message}
        </div>
      )}

      {/* MFA Card */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <KeyRound className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">TOTP Multi-Factor Authentication (RFC 6238)</h3>
              <p className="text-xs text-slate-400">
                Status:{' '}
                <span className={mfaStatus?.is_enabled ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
                  {mfaStatus?.is_enabled ? 'ENABLED' : 'NOT ENABLED'}
                </span>{' '}
                | Backup codes remaining: {mfaStatus?.backup_codes_remaining ?? 0}
              </p>
            </div>
          </div>
          <button
            onClick={handleStartMFASetup}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg"
          >
            Rotate / Provision TOTP Secret
          </button>
        </div>

        {mfaSetup && (
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 space-y-3">
            <div className="text-xs text-slate-300">
              <span className="font-semibold text-white">Secret Key:</span>{' '}
              <code className="bg-slate-800 px-2 py-1 rounded text-indigo-300">{mfaSetup.secret}</code>
            </div>
            <div className="text-xs text-slate-400 break-all">
              <span className="font-semibold text-slate-300">otpauth URI:</span> {mfaSetup.otpauth_uri}
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-300 mb-1">One-Time Recovery Codes:</div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {mfaSetup.backup_codes.map((code) => (
                  <code key={code} className="bg-slate-800 px-2 py-1 rounded text-xs text-emerald-300 text-center">
                    {code}
                  </code>
                ))}
              </div>
            </div>
            <form onSubmit={handleVerifyMFA} className="flex gap-2 pt-2">
              <input
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                placeholder="Enter 6-digit TOTP or backup code"
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                required
              />
              <button type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg">
                Verify & Enable
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Configured SSO Providers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
          <h3 className="text-lg font-semibold text-white">Configured Identity Providers</h3>
          <div className="space-y-3">
            {providers.map((p) => (
              <div key={p.id} className="bg-slate-900 border border-slate-700 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm">{p.provider_name}</span>
                  <span className="px-2 py-0.5 text-xs rounded bg-indigo-500/20 text-indigo-300 font-mono">{p.provider_type}</span>
                </div>
                <div className="text-xs text-slate-400 break-all">Issuer: {p.issuer_url}</div>
                <div className="flex items-center justify-between pt-1">
                  <span className="text-xs text-emerald-400">{p.enforced_for_admins ? 'Admin SSO Enforced' : 'Optional'}</span>
                  {p.provider_type === 'OIDC' && (
                    <button
                      onClick={() => handleTestOIDC(p.id)}
                      className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300"
                    >
                      Generate PKCE Handshake <ExternalLink className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {oidcPreview && (
            <div className="bg-slate-900 border border-indigo-500/40 rounded-lg p-3 text-xs space-y-1">
              <div className="font-semibold text-indigo-300">OIDC PKCE ({oidcPreview.code_challenge_method}) Ready</div>
              <div className="text-slate-400 break-all">State: {oidcPreview.state}</div>
              <div className="text-slate-400 break-all">Challenge: {oidcPreview.code_challenge}</div>
            </div>
          )}
        </div>

        {/* Register New Provider */}
        <form onSubmit={handleAddProvider} className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
          <h3 className="text-lg font-semibold text-white">Register New Identity Provider</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Protocol</label>
              <select
                value={providerType}
                onChange={(e) => setProviderType(e.target.value as 'OIDC' | 'SAML_2_0')}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              >
                <option value="OIDC">OpenID Connect (OIDC + PKCE)</option>
                <option value="SAML_2_0">SAML 2.0 Enterprise Assertion</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Provider Name</label>
              <input
                type="text"
                value={providerName}
                onChange={(e) => setProviderName(e.target.value)}
                placeholder="e.g. Google Workspace SSO"
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Issuer URL</label>
              <input
                type="url"
                value={issuerUrl}
                onChange={(e) => setIssuerUrl(e.target.value)}
                placeholder="https://accounts.google.com"
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">SSO Authorization / Login URL</label>
              <input
                type="url"
                value={ssoLoginUrl}
                onChange={(e) => setSsoLoginUrl(e.target.value)}
                placeholder="https://accounts.google.com/o/oauth2/v2/auth"
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Client ID (Optional for SAML)</label>
              <input
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="client-id-123"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
          </div>
          <button
            type="submit"
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg"
          >
            Register Identity Provider
          </button>
        </form>
      </div>
    </div>
  );
};
