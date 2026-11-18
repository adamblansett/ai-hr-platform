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
