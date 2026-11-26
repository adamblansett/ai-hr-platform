import {
  EmployeeProfile,
  MFASetupResponse,
  MFAStatusResponse,
  NotificationItem,
  PolicyRAGResponse,
  ScenarioForecastResult,
  SSOProviderConfig,
  TokenPair,
  WebhookSubscription,
  WorkforcePlan,
} from './types';

export class AIHRClient {
  private baseUrl: string;
  private token: string | null = null;
  private refreshTokenValue: string | null = null;

  constructor(options: { baseUrl?: string; token?: string } = {}) {
    this.baseUrl = (options.baseUrl || 'http://localhost:8000/api/v1').replace(/\/$/, '');
    this.token = options.token || null;
  }

  setToken(token: string): void {
    this.token = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'ai-hr-typescript-sdk/2.1.0',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
      throw new Error(err.detail || `Error ${response.status}`);
    }

    return response.json();
  }

  async authenticate(email: string, password: string): Promise<string> {
    const res = await this.request<TokenPair>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.token = res.access_token;
    this.refreshTokenValue = res.refresh_token;
    return this.token;
  }

  async refreshToken(refreshToken?: string): Promise<TokenPair> {
    const token = refreshToken || this.refreshTokenValue;
    if (!token) {
      throw new Error('No refresh token available');
    }
    const res = await this.request<TokenPair>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: token }),
    });
    this.token = res.access_token;
    this.refreshTokenValue = res.refresh_token;
    return res;
  }

  async logout(): Promise<{ status: string; revoked_tokens: number }> {
    const res = await this.request<{ status: string; revoked_tokens: number }>('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: this.refreshTokenValue }),
    });
    this.token = null;
    this.refreshTokenValue = null;
    return res;
  }

  async getMe(): Promise<EmployeeProfile> {
    return this.request<EmployeeProfile>('/auth/me');
  }

  async listEmployees(page = 1, search = ''): Promise<{ items: EmployeeProfile[]; total: number }> {
    const q = new URLSearchParams({ page: String(page), search });
    return this.request<{ items: EmployeeProfile[]; total: number }>(`/employees?${q}`);
  }

  async askPolicy(question: string, categoryFilter?: string): Promise<PolicyRAGResponse> {
    return this.request<PolicyRAGResponse>('/policies/chat', {
      method: 'POST',
      body: JSON.stringify({ question, category_filter: categoryFilter }),
    });
  }

  async getCompensation(): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>('/compensation/me');
  }

  async listWebhooks(): Promise<WebhookSubscription[]> {
    return this.request<WebhookSubscription[]>('/webhooks/outbound/subscriptions');
  }

  async getSalaryBenchmarks(department?: string): Promise<Array<Record<string, unknown>>> {
    const q = department ? `?department=${encodeURIComponent(department)}` : '';
    return this.request<Array<Record<string, unknown>>>(`/benchmarking/${q}`);
  }

  async listImmigrationCases(employeeId?: string): Promise<Array<Record<string, unknown>>> {
    const q = employeeId ? `?employee_id=${encodeURIComponent(employeeId)}` : '';
    return this.request<Array<Record<string, unknown>>>(`/immigration/cases${q}`);
  }

  async getTenantBranding(organizationId = 'org-001'): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(`/branding/?organization_id=${encodeURIComponent(organizationId)}`);
  }

  async listSSOProviders(): Promise<SSOProviderConfig[]> {
    return this.request<SSOProviderConfig[]>('/security/sso/providers');
  }

  async setupMFA(employeeId = 'emp-001', email = 'elena.rostova@acme.corp'): Promise<MFASetupResponse> {
    return this.request<MFASetupResponse>(
      `/security/mfa/setup?employee_id=${encodeURIComponent(employeeId)}&email=${encodeURIComponent(email)}`,
      { method: 'POST' }
    );
  }

  async verifyMFA(employeeId: string, code: string): Promise<MFAStatusResponse> {
    return this.request<MFAStatusResponse>('/security/mfa/verify', {
      method: 'POST',
      body: JSON.stringify({ employee_id: employeeId, code }),
    });
  }

  async listNotifications(recipientId = 'emp-001', unreadOnly = false): Promise<NotificationItem[]> {
    return this.request<NotificationItem[]>(
      `/notifications/me?recipient_id=${encodeURIComponent(recipientId)}&unread_only=${unreadOnly}`
    );
  }

  async listWorkforcePlans(): Promise<WorkforcePlan[]> {
    return this.request<WorkforcePlan[]>('/workforce-planning/plans');
  }

  async simulateWorkforcePlan(
    planId: string,
    scenario: 'CONSERVATIVE' | 'BASELINE' | 'HYPERGROWTH' = 'BASELINE',
    avgBaseSalary = 175000
  ): Promise<ScenarioForecastResult> {
    return this.request<ScenarioForecastResult>(`/workforce-planning/plans/${planId}/simulate`, {
      method: 'POST',
      body: JSON.stringify({ scenario, avg_base_salary: avgBaseSalary }),
    });
  }
}
