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

export interface PulseSurvey {
  id: string;
  organization_id: string;
  title: string;
  question: string;
  category: string;
  is_active: boolean;
  created_at: string;
}

export interface DepartmentSentiment {
  department: string;
  period: string;
  enps_score: number;
  avg_rating: number;
  burnout_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'ELEVATED';
  total_responses: number;
  ai_action_recommendations: string[];
}

export interface PulseAnalyticsSummary {
  overall_enps: number;
  overall_avg_rating: number;
  total_responses: number;
  departments: DepartmentSentiment[];
  burnout_watchlists: string[];
}

export interface BenefitPlan {
  id: string;
  organization_id: string;
  plan_name: string;
  plan_type: string;
  provider: string;
  tier_name: string;
  monthly_employee_premium: number;
  monthly_employer_contribution: number;
  annual_deductible: number;
  out_of_pocket_max: number;
  summary_of_benefits?: string;
  is_active: boolean;
}

export interface BenefitElection {
  id: string;
  employee_id: string;
  plan_id: string;
  plan_name?: string;
  plan_type?: string;
  coverage_tier: string;
  effective_date: string;
  employee_monthly_cost: number;
  employer_monthly_cost: number;
  status: string;
  created_at: string;
}

export interface BenefitsAdvisorResult {
  question: string;
  recommended_plan_name: string;
  recommendation_reason: string;
  estimated_annual_employee_cost: number;
  coverage_highlights: string[];
}

export interface TimeSheetEntry {
  id: string;
  employee_id: string;
  shift_date: string;
  clock_in: string;
  clock_out?: string;
  total_hours: number;
  regular_hours: number;
  overtime_hours: number;
  double_time_hours: number;
  meal_break_minutes: number;
  meal_penalty_flag: boolean;
  status: string;
  notes?: string;
}

export interface AttendanceSummary {
  employee_id: string;
  period_start: string;
  period_end: string;
  total_shifts: number;
  total_regular_hours: number;
  total_overtime_hours: number;
  total_double_time_hours: number;
  meal_penalty_violations: number;
  estimated_payable_hours: number;
}

// v1.8.0 Interfaces

export interface ExpenseItem {
  id: string;
  report_id: string;
  category: string;
  amount: number;
  currency: string;
  expense_date: string;
  merchant: string;
  description?: string;
  receipt_url?: string;
  is_compliant: boolean;
  policy_flags?: string;
}

export interface ExpenseReport {
  id: string;
  employee_id: string;
  title: string;
  status: string;
  total_amount: number;
  currency: string;
  audit_status: string;
  audit_notes?: string;
  reimbursement_reference?: string;
  created_at: string;
  submitted_at?: string;
  approved_at?: string;
  items: ExpenseItem[];
}

export interface ExpenseAuditResult {
  report_id: string;
  overall_status: string;
  total_audited: number;
  flagged_items_count: number;
  flags: string[];
  remediation_actions: string[];
}

export interface SafetyIncident {
  id: string;
  employee_id: string;
  incident_type: string;
  severity: string;
  incident_date: string;
  location: string;
  description: string;
  is_osha_recordable: boolean;
  osha_case_number?: string;
  lost_workday_count: number;
  restricted_days_count: number;
  ai_root_cause_analysis?: string;
  corrective_actions?: string;
  status: string;
  created_at: string;
}

export interface OSHA300LogSummary {
  year: number;
  total_incidents: number;
  osha_recordable_cases: number;
  total_lost_workdays: number;
  total_restricted_days: number;
  injuries_count: number;
  illnesses_count: number;
  near_misses_count: number;
  lost_workday_rate: number;
}

export interface PeerRecognition {
  id: string;
  sender_id: string;
  recipient_id: string;
  points: number;
  core_value: string;
  message: string;
  is_public: boolean;
  created_at: string;
}

export interface RewardCatalogItem {
  id: string;
  title: string;
  category: string;
  points_cost: number;
  description: string;
  is_available: boolean;
  image_url?: string;
}

export interface EmployeeWallet {
  employee_id: string;
  points_balance: number;
  monthly_allowance_remaining: number;
  updated_at: string;
}

export interface MilestoneEvent {
  employee_id: string;
  employee_name: string;
  milestone_type: string;
  milestone_date: string;
  anniversary_years?: number;
  suggested_award_points: number;
}

