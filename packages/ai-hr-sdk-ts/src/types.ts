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
