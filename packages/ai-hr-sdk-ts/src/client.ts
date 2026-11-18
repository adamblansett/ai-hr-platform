import { EmployeeProfile, PolicyRAGResponse, WebhookSubscription } from './types';

export class AIHRClient {
  private baseUrl: string;
  private token: string | null = null;

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
      'User-Agent': 'ai-hr-typescript-sdk/1.0.0',
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
    const res = await this.request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.token = res.access_token;
    return this.token;
  }

  async getMe(): Promise<EmployeeProfile> {
    return this.request<EmployeeProfile>('/auth/me');
  }

  async askPolicy(question: string, categoryFilter?: string): Promise<PolicyRAGResponse> {
    return this.request<PolicyRAGResponse>('/policies/chat', {
      method: 'POST',
      body: JSON.stringify({ question, category_filter: categoryFilter }),
    });
  }

  async listWebhooks(): Promise<WebhookSubscription[]> {
    return this.request<WebhookSubscription[]>('/webhooks/outbound/subscriptions');
  }
}
