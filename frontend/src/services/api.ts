import {
  Employee,
  OnboardingProgress,
  PolicyDocument,
  PolicyAnswer,
  LeaveBalance,
  LeaveRequest,
  GoalOKR,
  CompensationSummary,
  HolidayItem,
  LanguageDetectionResult,
  FlightRiskRecord,
  SOC2Evidence,
  WebhookSubscription,
  WebhookDeliveryLog,
  WebhookTestPingResult,
  OrgChartNode,
  OrgChartStats,
  OffboardingRecord,
  OneOnOneMeeting,
  CalibrationAnalysis,
  PulseSurvey,
  PulseAnalyticsSummary,
  BenefitPlan,
  BenefitElection,
  BenefitsAdvisorResult,
  TimeSheetEntry,
  AttendanceSummary,
  ExpenseReport,
  ExpenseAuditResult,
  SafetyIncident,
  OSHA300LogSummary,
  PeerRecognition,
  RewardCatalogItem,
  EmployeeWallet,
  MilestoneEvent,
  Course,
  CourseEnrollment,
  ComplianceAuditSummary,
  HardwareAsset,
  FleetSummary,
  ContractorProfile,
  ContractorSOW,
  MilestoneInvoice,
  EORSummary,
} from '../types';

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

  // Compensation & Equity
  async getMyCompensation(): Promise<CompensationSummary> {
    return this.request<CompensationSummary>('/compensation/me');
  }

  async runPayroll(periodStart: string, periodEnd: string) {
    return this.request('/compensation/paystubs/run-payroll', {
      method: 'POST',
      body: JSON.stringify({ pay_period_start: periodStart, pay_period_end: periodEnd }),
    });
  }

  // Localization & Holidays
  async getHolidays(country = 'US', year = 2026): Promise<HolidayItem[]> {
    return this.request<HolidayItem[]>(`/localization/holidays?country=${country}&year=${year}`);
  }

  async detectLanguage(text: string): Promise<LanguageDetectionResult> {
    return this.request<LanguageDetectionResult>('/localization/detect-language', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  // Succession & Flight Risk
  async getFlightRisks(): Promise<FlightRiskRecord[]> {
    return this.request<FlightRiskRecord[]>('/succession/flight-risk');
  }

  async evaluateFlightRisk(employeeId: string): Promise<FlightRiskRecord> {
    return this.request<FlightRiskRecord>(`/succession/flight-risk/evaluate/${employeeId}`, {
      method: 'POST',
    });
  }

  // Compliance & Governance
  async getDSARReport(employeeId: string): Promise<any> {
    return this.request(`/compliance/dsar/${employeeId}`);
  }

  async executeRightToBeForgotten(employeeId: string): Promise<any> {
    return this.request(`/compliance/right-to-be-forgotten/${employeeId}`, {
      method: 'POST',
    });
  }

  async getSoc2Evidence(): Promise<SOC2Evidence> {
    return this.request<SOC2Evidence>('/compliance/soc2/evidence');
  }

  // Outbound Webhooks (Workday / ADP / Gusto)
  async getOutboundSubscriptions(): Promise<WebhookSubscription[]> {
    return this.request<WebhookSubscription[]>('/webhooks/outbound/subscriptions');
  }

  async createOutboundSubscription(data: { target_url: string; event_types: string[]; description?: string }): Promise<WebhookSubscription> {
    return this.request<WebhookSubscription>('/webhooks/outbound/subscriptions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteOutboundSubscription(id: string): Promise<void> {
    return this.request(`/webhooks/outbound/subscriptions/${id}`, {
      method: 'DELETE',
    });
  }

  async testPingOutboundSubscription(id: string): Promise<WebhookTestPingResult> {
    return this.request<WebhookTestPingResult>(`/webhooks/outbound/subscriptions/${id}/test-ping`, {
      method: 'POST',
    });
  }

  async getOutboundDeliveryLogs(subId: string): Promise<WebhookDeliveryLog[]> {
    return this.request<WebhookDeliveryLog[]>(`/webhooks/outbound/subscriptions/${subId}/logs`);
  }

  // Org Chart & Hierarchy
  async getOrgChart(): Promise<OrgChartNode[]> {
    return this.request<OrgChartNode[]>('/employees/org-chart');
  }

  async getOrgChartStats(): Promise<OrgChartStats> {
    return this.request<OrgChartStats>('/employees/org-chart/stats');
  }

  // Offboarding
  async getOffboardingRecords(): Promise<OffboardingRecord[]> {
    return this.request<OffboardingRecord[]>('/offboarding');
  }

  async initiateOffboarding(data: { employee_id: string; last_working_day: string; termination_reason: string; notes?: string }): Promise<OffboardingRecord> {
    return this.request<OffboardingRecord>('/offboarding/initiate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deprovisionSCIM(offboardingId: string): Promise<OffboardingRecord> {
    return this.request<OffboardingRecord>(`/offboarding/${offboardingId}/deprovision-scim`, {
      method: 'POST',
    });
  }

  async toggleOffboardingTask(taskId: string): Promise<any> {
    return this.request(`/offboarding/tasks/${taskId}/toggle`, {
      method: 'PATCH',
    });
  }

  // 1:1 Coaching & Calibration
  async getMyOneOnOnes(): Promise<OneOnOneMeeting[]> {
    return this.request<OneOnOneMeeting[]>('/coaching/1on1/me');
  }

  async generateOneOnOneAgenda(data: { employee_id: string; scheduled_date: string; focus_area?: string }): Promise<OneOnOneMeeting> {
    return this.request<OneOnOneMeeting>('/coaching/1on1/generate-agenda', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeCalibration(data: { cycle_name: string; department: string; ratings: number[] }): Promise<CalibrationAnalysis> {
    return this.request<CalibrationAnalysis>('/coaching/calibration/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCalibrationHistory(): Promise<CalibrationAnalysis[]> {
    return this.request<CalibrationAnalysis[]>('/coaching/calibration/history');
  }

  // Employee Pulse & Sentiment Radar
  async getActiveSurveys(): Promise<PulseSurvey[]> {
    return this.request<PulseSurvey[]>('/pulse/active');
  }

  async submitPulseResponse(surveyId: string, data: { rating: number; feedback_text?: string }): Promise<any> {
    return this.request(`/pulse/surveys/${surveyId}/respond`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPulseAnalytics(): Promise<PulseAnalyticsSummary> {
    return this.request<PulseAnalyticsSummary>('/pulse/analytics');
  }

  // Benefits Administration & AI Advisor
  async getBenefitPlans(): Promise<BenefitPlan[]> {
    return this.request<BenefitPlan[]>('/benefits/plans');
  }

  async getMyBenefitElections(): Promise<BenefitElection[]> {
    return this.request<BenefitElection[]>('/benefits/elections/me');
  }

  async enrollBenefitPlan(data: { plan_id: string; coverage_tier: string; effective_date: string }): Promise<BenefitElection> {
    return this.request<BenefitElection>('/benefits/elections', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async askBenefitsAdvisor(data: { question: string; family_members_count?: number; has_chronic_needs?: boolean }): Promise<BenefitsAdvisorResult> {
    return this.request<BenefitsAdvisorResult>('/benefits/advisor/query', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Time & Attendance (Overtime / FLSA)
  async clockIn(notes?: string): Promise<TimeSheetEntry> {
    return this.request<TimeSheetEntry>('/attendance/clock-in', {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async clockOut(mealBreakMinutes: number = 30, notes?: string): Promise<TimeSheetEntry> {
    return this.request<TimeSheetEntry>('/attendance/clock-out', {
      method: 'POST',
      body: JSON.stringify({ meal_break_minutes: mealBreakMinutes, notes }),
    });
  }

  async getMyTimesheets(): Promise<TimeSheetEntry[]> {
    return this.request<TimeSheetEntry[]>('/attendance/timesheets/me');
  }

  async getAttendanceSummary(employeeId: string): Promise<AttendanceSummary> {
    return this.request<AttendanceSummary>(`/attendance/summary/${employeeId}`);
  }

  // Expense Reports & Policy Audit
  async getExpenseReports(employeeId?: string): Promise<ExpenseReport[]> {
    const q = employeeId ? `?employee_id=${employeeId}` : '';
    return this.request<ExpenseReport[]>(`/expenses/${q}`);
  }

  async createExpenseReport(data: any): Promise<ExpenseReport> {
    return this.request<ExpenseReport>('/expenses/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async auditExpenseReport(reportId: string): Promise<ExpenseAuditResult> {
    return this.request<ExpenseAuditResult>(`/expenses/${reportId}/audit`, {
      method: 'POST',
    });
  }

  async submitExpenseReport(reportId: string): Promise<ExpenseReport> {
    return this.request<ExpenseReport>(`/expenses/${reportId}/submit`, {
      method: 'POST',
    });
  }

  async approveExpenseReport(reportId: string): Promise<ExpenseReport> {
    return this.request<ExpenseReport>(`/expenses/${reportId}/approve`, {
      method: 'POST',
    });
  }

  // Workplace Health, Safety & OSHA Compliance
  async getSafetyIncidents(employeeId?: string): Promise<SafetyIncident[]> {
    const q = employeeId ? `?employee_id=${employeeId}` : '';
    return this.request<SafetyIncident[]>(`/safety/incidents${q}`);
  }

  async reportSafetyIncident(data: any): Promise<SafetyIncident> {
    return this.request<SafetyIncident>('/safety/incidents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getOsha300Log(year: number = 2026): Promise<OSHA300LogSummary> {
    return this.request<OSHA300LogSummary>(`/safety/osha-300-log?year=${year}`);
  }

  // Employee Engagement & Peer Recognition
  async getRecognitionFeed(): Promise<PeerRecognition[]> {
    return this.request<PeerRecognition[]>('/recognition/feed');
  }

  async sendPeerKudos(data: { sender_id: string; recipient_id: string; points: number; core_value: string; message: string }): Promise<PeerRecognition> {
    return this.request<PeerRecognition>('/recognition/kudos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getEmployeeWallet(employeeId: string): Promise<EmployeeWallet> {
    return this.request<EmployeeWallet>(`/recognition/wallet/${employeeId}`);
  }

  async getRewardsCatalog(): Promise<RewardCatalogItem[]> {
    return this.request<RewardCatalogItem[]>('/recognition/rewards');
  }

  async redeemReward(data: { employee_id: string; reward_item_id: string }): Promise<any> {
    return this.request('/recognition/redeem', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUpcomingMilestones(): Promise<MilestoneEvent[]> {
    return this.request<MilestoneEvent[]>('/recognition/milestones');
  }

  // Learning & Development / LMS
  async getCourses(category?: string): Promise<Course[]> {
    const q = category ? `?category=${category}` : '';
    return this.request<Course[]>(`/learning/courses${q}`);
  }

  async enrollCourse(courseId: string, employeeId: string = 'emp-001'): Promise<CourseEnrollment> {
    return this.request<CourseEnrollment>('/learning/enroll', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, employee_id: employeeId }),
    });
  }

  async updateCourseProgress(enrollmentId: string, progress: number, score?: number): Promise<CourseEnrollment> {
    return this.request<CourseEnrollment>(`/learning/enrollments/${enrollmentId}/progress`, {
      method: 'PATCH',
      body: JSON.stringify({ progress_percentage: progress, score }),
    });
  }

  async getMyEnrollments(employeeId: string = 'emp-001'): Promise<CourseEnrollment[]> {
    return this.request<CourseEnrollment[]>(`/learning/enrollments/me?employee_id=${employeeId}`);
  }

  async getComplianceAudit(): Promise<ComplianceAuditSummary> {
    return this.request<ComplianceAuditSummary>('/learning/compliance-audit');
  }

  // Hardware Asset Fleet Management
  async getHardwareAssets(category?: string, status?: string): Promise<HardwareAsset[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    const q = params.toString() ? `?${params.toString()}` : '';
    return this.request<HardwareAsset[]>(`/assets/${q}`);
  }

  async createHardwareAsset(data: any): Promise<HardwareAsset> {
    return this.request<HardwareAsset>('/assets/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async assignHardwareAsset(assetId: string, employeeId: string): Promise<HardwareAsset> {
    return this.request<HardwareAsset>(`/assets/${assetId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ employee_id: employeeId }),
    });
  }

  async unassignHardwareAsset(assetId: string): Promise<HardwareAsset> {
    return this.request<HardwareAsset>(`/assets/${assetId}/unassign`, {
      method: 'POST',
    });
  }

  async triggerRemoteWipe(assetId: string, reason: string): Promise<HardwareAsset> {
    return this.request<HardwareAsset>(`/assets/${assetId}/remote-wipe`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async getFleetSummary(): Promise<FleetSummary> {
    return this.request<FleetSummary>('/assets/summary/fleet');
  }

  // Global Contractor & Vendor EOR Hub
  async getContractors(country?: string): Promise<ContractorProfile[]> {
    const q = country ? `?country=${country}` : '';
    return this.request<ContractorProfile[]>(`/contractors/${q}`);
  }

  async createContractor(data: any): Promise<ContractorProfile> {
    return this.request<ContractorProfile>('/contractors/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async verifyContractorTax(contractorId: string): Promise<ContractorProfile> {
    return this.request<ContractorProfile>(`/contractors/${contractorId}/verify-tax`, {
      method: 'POST',
    });
  }

  async getSOWs(contractorId?: string): Promise<ContractorSOW[]> {
    const q = contractorId ? `?contractor_id=${contractorId}` : '';
    return this.request<ContractorSOW[]>(`/contractors/sows${q}`);
  }

  async createSOW(data: any): Promise<ContractorSOW> {
    return this.request<ContractorSOW>('/contractors/sows', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getContractorInvoices(contractorId?: string): Promise<MilestoneInvoice[]> {
    const q = contractorId ? `?contractor_id=${contractorId}` : '';
    return this.request<MilestoneInvoice[]>(`/contractors/invoices${q}`);
  }

  async submitContractorInvoice(data: any): Promise<MilestoneInvoice> {
    return this.request<MilestoneInvoice>('/contractors/invoices', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async approveContractorInvoice(invoiceId: string): Promise<MilestoneInvoice> {
    return this.request<MilestoneInvoice>(`/contractors/invoices/${invoiceId}/approve`, {
      method: 'POST',
    });
  }

  async payContractorInvoice(invoiceId: string): Promise<MilestoneInvoice> {
    return this.request<MilestoneInvoice>(`/contractors/invoices/${invoiceId}/pay`, {
      method: 'POST',
    });
  }

  async getEORSummary(): Promise<EORSummary> {
    return this.request<EORSummary>('/contractors/summary/eor');
  }
}

export const api = new ApiClient();
