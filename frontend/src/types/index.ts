export type EmployeeRole = 'SUPER_ADMIN' | 'HR_ADMIN' | 'PEOPLE_MANAGER' | 'EMPLOYEE';
export type EmploymentStatus = 'ONBOARDING' | 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED';
export type EmploymentType = 'FULL_TIME' | 'PART_TIME' | 'CONTRACTOR' | 'INTERN';

export interface Employee {
  id: string;
  organization_id: string;
  email: string;
  first_name: string;
  last_name: string;
  preferred_name?: string;
  phone_number?: string;
  role: EmployeeRole;
  status: EmploymentStatus;
  employment_type: EmploymentType;
  department: string;
  job_title: string;
  manager_id?: string;
  hire_date: string;
}

export interface OnboardingTask {
  id: string;
  organization_id: string;
  employee_id: string;
  title: string;
  description: string;
  category: 'DOCUMENTATION' | 'EQUIPMENT' | 'ACCESS_PROVISIONING' | 'TRAINING' | 'COMPLIANCE';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED' | 'WAIVED';
  due_date?: string;
  completed_at?: string;
  assigned_to_role: string;
  document_url?: string;
}

export interface OnboardingProgress {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  blocked_tasks: number;
  completion_percentage: number;
  tasks: OnboardingTask[];
}

export interface PolicyDocument {
  id: string;
  title: string;
  category: string;
  version: string;
  content: string;
  chunk_index: number;
  requires_acknowledgment: boolean;
}

export interface PolicyCitation {
  policy_id: string;
  title: string;
  category: string;
  chunk_index: number;
  snippet: string;
  relevance_score: number;
}

export interface PolicyAnswer {
  question: string;
  answer: string;
  citations: PolicyCitation[];
  model_used: string;
  pii_redacted: boolean;
}

export interface LeaveBalance {
  id: string;
  policy_id: string;
  policy_name: string;
  leave_type: string;
  year: number;
  accrued_days: number;
  used_days: number;
  remaining_days: number;
}

export interface LeaveRequest {
  id: string;
  policy_name: string;
  employee_name: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  calendar_conflict_flag: boolean;
}

export interface GoalOKR {
  id: string;
  title: string;
  description: string;
  progress_percentage: number;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'ACHIEVED' | 'EXCEEDED' | 'MISSED';
}

export interface EquityGrant {
  id: string;
  grant_type: 'ISO' | 'NSO' | 'RSU';
  total_shares: number;
  vested_shares: number;
  unvested_shares: number;
  strike_price: number;
  grant_date: string;
  vesting_start_date: string;
  cliff_date: string;
  cliff_months: number;
  total_vesting_months: number;
  estimated_current_value: number;
  next_vesting_date?: string;
}

export interface CompensationPackage {
  id: string;
  employee_id: string;
  base_salary: number;
  currency: string;
  payment_frequency: 'MONTHLY' | 'BIWEEKLY' | 'SEMIMONTHLY';
  target_bonus_percentage: number;
  effective_date: string;
}

export interface PaystubRecord {
  id: string;
  paystub_number: string;
  pay_period_start: string;
  pay_period_end: string;
  payment_date: string;
  gross_pay: number;
  federal_tax: number;
  social_security: number;
  medicare: number;
  state_tax: number;
  other_deductions: number;
  net_pay: number;
}

export interface CompensationSummary {
  package?: CompensationPackage;
  equity_grants: EquityGrant[];
  recent_paystubs: PaystubRecord[];
  total_equity_shares: number;
  total_vested_shares: number;
  total_unvested_shares: number;
}

export interface HolidayItem {
  name: string;
  date: string;
  country: string;
  jurisdiction: string;
}

export interface LanguageDetectionResult {
  detected_language: string;
  language_name: string;
  supported: boolean;
}

export interface FlightRiskRecord {
  id: string;
  employee_id: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  contributing_factors: string[];
  recommended_interventions: string[];
  evaluated_at: string;
}

export interface SOC2Evidence {
  report_name: string;
  organization_id: string;
  generated_at: string;
  overall_status: string;
  controls: Record<string, {
    status: string;
    description: string;
    [key: string]: any;
  }>;
}

export interface WebhookSubscription {
  id: string;
  organization_id: string;
  target_url: string;
  event_types: string[];
  is_active: boolean;
  description?: string;
  created_at: string;
}

export interface WebhookDeliveryLog {
  id: string;
  subscription_id: string;
  event_type: string;
  status_code?: number;
  attempt_count: number;
  delivered_at: string;
  error_message?: string;
}

export interface WebhookTestPingResult {
  status: string;
  target_url: string;
  signature_header: string;
  test_event: string;
  timestamp: string;
}

export interface OrgChartNode {
  id: string;
  name: string;
  email: string;
  job_title: string;
  department: string;
  manager_id?: string;
  direct_reports: OrgChartNode[];
}

export interface OrgChartStats {
  total_active_employees: number;
  total_people_managers: number;
  average_span_of_control: number;
  overloaded_managers_count: number;
  overloaded_managers: Array<{
    id: string;
    name: string;
    job_title: string;
    direct_reports: number;
  }>;
}

export interface OffboardingTask {
  id: string;
  title: string;
  category: string;
  assigned_to: string;
  is_completed: boolean;
  completed_at?: string;
}

export interface OffboardingRecord {
  id: string;
  organization_id: string;
  employee_id: string;
  employee_name?: string;
  last_working_day: string;
  termination_reason: string;
  status: string;
  scim_deprovisioned: boolean;
  equipment_returned: boolean;
  nda_reaffirmed: boolean;
  notes?: string;
  tasks: OffboardingTask[];
  created_at: string;
  completed_at?: string;
}

export interface OneOnOneMeeting {
  id: string;
  manager_id: string;
  employee_id: string;
  scheduled_date: string;
  status: string;
  talking_points: string[];
  ai_suggested_prompts: string[];
  manager_notes?: string;
  action_items: string[];
  created_at: string;
}

export interface CalibrationAnalysis {
  id: string;
  cycle_name: string;
  department: string;
  total_reviewed: number;
  rating_distribution: Record<string, number>;
  mean_rating: number;
  detected_biases: string[];
  recommendations: string[];
  analyzed_at: string;
}
