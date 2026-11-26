export interface EmployeeProfile {
  id: string;
  organization_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  department: string;
  job_title: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface PolicyRAGResponse {
  question: string;
  answer: string;
  citations: Array<{
    policy_id: string;
    title: string;
    snippet: string;
    relevance_score: number;
  }>;
  model_used: string;
  pii_redacted: boolean;
}

export interface WebhookSubscription {
  id: string;
  target_url: string;
  event_types: string[];
  is_active: boolean;
  description?: string;
}

export interface SSOProviderConfig {
  id: string;
  organization_id: string;
  provider_type: string;
  provider_name: string;
  issuer_url: string;
  sso_login_url: string;
  enforced_for_admins: boolean;
  is_active: boolean;
}

export interface MFASetupResponse {
  employee_id: string;
  secret: string;
  otpauth_uri: string;
  backup_codes: string[];
  is_enabled: boolean;
}

export interface MFAStatusResponse {
  employee_id: string;
  is_enabled: boolean;
  enforced_by_policy: boolean;
  backup_codes_remaining: number;
}

export interface NotificationItem {
  id: string;
  channel: string;
  category: string;
  title: string;
  body: string;
  status: string;
  created_at: string;
}

export interface WorkforcePlan {
  id: string;
  fiscal_year: number;
  department: string;
  current_headcount: number;
  target_headcount: number;
  approved_budget_usd: number;
  status: string;
}

export interface ScenarioForecastResult {
  plan_id: string;
  department: string;
  scenario: string;
  net_new_hires: number;
  attrition_backfills: number;
  total_hiring_need: number;
  estimated_total_fully_loaded_cost: number;
  budget_variance_usd: number;
  ai_recommendation: string;
}
