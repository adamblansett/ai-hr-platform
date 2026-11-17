import { Employee, OnboardingProgress, PolicyDocument, PolicyAnswer, LeaveBalance, LeaveRequest, GoalOKR } from '../types';

const API_BASE = '/api/v1';

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('ai_hr_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('ai_hr_token');
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Network request failed' }));
      throw new Error(err.detail || `Error ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    const res = await this.request<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<Employee> {
    return this.request<Employee>('/auth/me');
  }

  // Directory
  async getEmployees(page = 1, search = '') {
    const query = new URLSearchParams({ page: String(page), search });
    return this.request<{ items: Employee[]; total: number; total_pages: number }>(`/employees?${query}`);
  }

  // Onboarding
  async getMyOnboardingProgress(): Promise<OnboardingProgress> {
    return this.request<OnboardingProgress>('/onboarding/me/progress');
  }

  async updateTaskStatus(taskId: string, status: string) {
    return this.request(`/onboarding/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Policies & RAG Chat
  async getPolicies(): Promise<PolicyDocument[]> {
    return this.request<PolicyDocument[]>('/policies');
  }

  async askPolicyAI(question: string, category_filter?: string): Promise<PolicyAnswer> {
    return this.request<PolicyAnswer>('/policies/chat', {
      method: 'POST',
      body: JSON.stringify({ question, category_filter }),
    });
  }

  async acknowledgePolicy(policyId: string, signatureName: string) {
    return this.request(`/policies/${policyId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ signature_name: signatureName }),
    });
  }

  // Leave
  async getMyLeaveBalances(): Promise<LeaveBalance[]> {
    return this.request<LeaveBalance[]>('/leave/balances/me');
  }

  async getMyLeaveRequests(): Promise<LeaveRequest[]> {
    return this.request<LeaveRequest[]>('/leave/requests/me');
  }

  async submitLeaveRequest(data: { policy_id: string; start_date: string; end_date: string; reason: string }) {
    return this.request('/leave/requests', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Performance & Goals
  async getMyGoals(): Promise<GoalOKR[]> {
    return this.request<GoalOKR[]>('/performance/goals/me');
  }
}

export const api = new ApiClient();
