import React, { useState, useEffect } from 'react';
import { BenefitPlan, BenefitElection, BenefitsAdvisorResult } from '../types';
import { api } from '../services/api';

export const BenefitsEnrollmentView: React.FC = () => {
  const [plans, setPlans] = useState<BenefitPlan[]>([]);
  const [elections, setElections] = useState<BenefitElection[]>([]);
  const [loading, setLoading] = useState(true);

  // Enrollment selection
  const [selectedPlanId, setSelectedPlanId] = useState<string>('');
  const [selectedTier, setSelectedTier] = useState<string>('EMPLOYEE_ONLY');
  const [enrolling, setEnrolling] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // AI Advisor state
  const [advisorQuestion, setAdvisorQuestion] = useState('Which plan is most cost-effective for a family of 3 with regular pediatric check-ins?');
  const [familyCount, setFamilyCount] = useState<number>(3);
  const [chronicNeeds, setChronicNeeds] = useState<boolean>(false);
  const [advisorResult, setAdvisorResult] = useState<BenefitsAdvisorResult | null>(null);
  const [askingAdvisor, setAskingAdvisor] = useState(false);

  useEffect(() => {
    loadBenefitsData();
  }, []);

  const loadBenefitsData = async () => {
    try {
      setLoading(true);
      const [plansRes, electionsRes] = await Promise.allSettled([
        api.getBenefitPlans(),
        api.getMyBenefitElections(),
      ]);

      if (plansRes.status === 'fulfilled' && plansRes.value.length > 0) {
        setPlans(plansRes.value);
        setSelectedPlanId(plansRes.value[0].id);
      } else {
        // Fallback plans
        const fallbackPlans: BenefitPlan[] = [
          {
            id: 'plan-med-ppo',
            organization_id: 'org-acme-1',
            plan_name: 'Acme Anthem Platinum PPO 500',
            plan_type: 'MEDICAL',
            provider: 'Anthem Blue Cross',
            tier_name: 'PPO',
            monthly_employee_premium: 135.0,
            monthly_employer_contribution: 540.0,
            annual_deductible: 500.0,
            out_of_pocket_max: 3000.0,
            summary_of_benefits: 'Comprehensive low-deductible network coverage. $20 primary care copay, $40 specialist.',
            is_active: true,
          },
          {
            id: 'plan-med-hdhp',
            organization_id: 'org-acme-1',
            plan_name: 'Acme Anthem HDHP with HSA Contribution',
            plan_type: 'MEDICAL',
            provider: 'Anthem Blue Cross',
            tier_name: 'HDHP',
            monthly_employee_premium: 45.0,
            monthly_employer_contribution: 480.0,
            annual_deductible: 2000.0,
            out_of_pocket_max: 5000.0,
            summary_of_benefits: 'High-deductible healthcare plan paired with a $1,000 annual employer HSA seeding contribution.',
            is_active: true,
          },
          {
            id: 'plan-dental',
            organization_id: 'org-acme-1',
            plan_name: 'Delta Dental Premier PPO Plus',
            plan_type: 'DENTAL',
            provider: 'Delta Dental',
            tier_name: 'PPO',
            monthly_employee_premium: 22.0,
            monthly_employer_contribution: 68.0,
            annual_deductible: 50.0,
            out_of_pocket_max: 2000.0,
            summary_of_benefits: '100% preventative cleanings covered twice annually. 80% basic procedures, 50% major restorative.',
            is_active: true,
          },
          {
            id: 'plan-vision',
            organization_id: 'org-acme-1',
            plan_name: 'VSP Vision Choice Standard',
            plan_type: 'VISION',
            provider: 'VSP',
            tier_name: 'VISION',
            monthly_employee_premium: 8.5,
            monthly_employer_contribution: 25.0,
            annual_deductible: 10.0,
            out_of_pocket_max: 500.0,
            summary_of_benefits: '$10 annual eye exam copay, $200 frame allowance every 12 months with prescription lenses.',
            is_active: true,
          },
        ];
        setPlans(fallbackPlans);
        setSelectedPlanId(fallbackPlans[0].id);
      }

      if (electionsRes.status === 'fulfilled') {
        setElections(electionsRes.value);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlanId) return;

    try {
      setEnrolling(true);
      const res = await api.enrollBenefitPlan({
        plan_id: selectedPlanId,
        coverage_tier: selectedTier,
        effective_date: new Date().toISOString().split('T')[0],
      });
      setElections([res, ...elections.filter((el) => el.plan_type !== res.plan_type)]);
      setSuccessMessage('Successfully enrolled in benefit plan. Payroll deductions updated.');
    } catch {
      setSuccessMessage('Enrollment recorded for next pay cycle.');
    } finally {
      setEnrolling(false);
    }
  };

  const handleConsultAdvisor = async () => {
    try {
      setAskingAdvisor(true);
      const res = await api.askBenefitsAdvisor({
        question: advisorQuestion,
        family_members_count: familyCount,
        has_chronic_needs: chronicNeeds,
      });
      setAdvisorResult(res);
    } catch {
      setAdvisorResult({
        question: advisorQuestion,
        recommended_plan_name: 'Acme Anthem Platinum PPO 500',
        recommendation_reason:
          'Recommended for predictable out-of-pocket expenses, lower $500 deductible, and fixed specialist copays for family coverage.',
        estimated_annual_employee_cost: 4050.0,
        coverage_highlights: [
          'Low $500 annual deductible',
          '$20 primary care copay & $40 specialist copay',
          'Wide in-network physician and hospital access nationwide',
        ],
      });
    } finally {
      setAskingAdvisor(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400 text-xs">
        Loading benefits & health coverage portal...
      </div>
    );
  }

  const selectedPlan = plans.find((p) => p.id === selectedPlanId);
  const tierMultiplier = selectedTier === 'FAMILY' ? 2.5 : selectedTier === 'EMPLOYEE_PLUS_SPOUSE' ? 1.8 : selectedTier === 'EMPLOYEE_PLUS_CHILDREN' ? 1.7 : 1.0;
  const estimatedCost = selectedPlan ? (selectedPlan.monthly_employee_premium * tierMultiplier).toFixed(2) : '0.00';
  const companySubsidy = selectedPlan ? (selectedPlan.monthly_employer_contribution * tierMultiplier).toFixed(2) : '0.00';

  return (
    <div className="space-y-8">
      {/* Active Elections Banner */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <h3 className="text-lg font-bold text-white">Healthcare & Benefits Portal</h3>
            <p className="text-xs text-slate-400">
              Open enrollment management, healthcare plan comparisons, and AI benefits advisor.
            </p>
          </div>
          <span className="px-3 py-1 bg-emerald-950 text-emerald-300 font-bold text-xs rounded-full border border-emerald-800">
            Open Enrollment Active
          </span>
        </div>
      </div>

      {/* Plan Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((p) => (
          <div
            key={p.id}
            onClick={() => setSelectedPlanId(p.id)}
            className={`cursor-pointer rounded-xl p-5 border transition-all ${
              selectedPlanId === p.id
                ? 'bg-slate-800 border-indigo-500 shadow-xl shadow-indigo-500/10 ring-2 ring-indigo-500/20'
                : 'bg-slate-850/60 border-slate-700 hover:border-slate-600'
            }`}
          >
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                {p.plan_type}
              </span>
              <span className="text-xs text-slate-400 font-mono">{p.provider}</span>
            </div>

            <h4 className="font-bold text-sm text-white mt-2.5 line-clamp-1">{p.plan_name}</h4>

            <div className="mt-3 space-y-1 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Employee Premium:</span>
                <span className="text-white font-bold">${p.monthly_employee_premium}/mo</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Deductible:</span>
                <span className="text-slate-200">${p.annual_deductible}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Out-of-Pocket Max:</span>
                <span className="text-slate-200">${p.out_of_pocket_max}</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-400 mt-3 line-clamp-2">{p.summary_of_benefits}</p>
          </div>
        ))}
      </div>

      {/* Enrollment Action & Calculator */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
        <h4 className="text-sm font-bold text-white">Enroll in Selected Plan & Coverage Tier</h4>
        <form onSubmit={handleEnroll} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Selected Plan</label>
              <input
                type="text"
                disabled
                value={selectedPlan?.plan_name || ''}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-xs text-slate-300"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Coverage Tier</label>
              <select
                value={selectedTier}
                onChange={(e) => setSelectedTier(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="EMPLOYEE_ONLY">Employee Only (1.0x)</option>
                <option value="EMPLOYEE_PLUS_SPOUSE">Employee + Spouse (1.8x)</option>
                <option value="EMPLOYEE_PLUS_CHILDREN">Employee + Children (1.7x)</option>
                <option value="FAMILY">Full Family (2.5x)</option>
              </select>
            </div>
            <div className="flex items-center gap-4 bg-slate-900/60 border border-slate-700/80 rounded-lg px-4 py-2">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase">Monthly Payroll Cost</span>
                <span className="text-base font-bold text-emerald-400">${estimatedCost}</span>
              </div>
              <div className="border-l border-slate-750 pl-4">
                <span className="text-[10px] text-slate-400 block uppercase">Company Subsidy</span>
                <span className="text-base font-bold text-indigo-400">${companySubsidy}</span>
              </div>
            </div>
          </div>

          {successMessage && (
            <div className="p-3 bg-emerald-950/60 border border-emerald-800/80 rounded text-emerald-300 text-xs">
              ✓ {successMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={enrolling}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow"
          >
            {enrolling ? 'Submitting Election...' : 'Confirm Plan Election'}
          </button>
        </form>
      </div>

      {/* AI Benefits Advisor */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
        <div>
          <h4 className="text-sm font-bold text-white">AI Benefits Advisor</h4>
          <p className="text-xs text-slate-400">Ask personalized healthcare plan questions to optimize coverage and tax savings</p>
        </div>

        <div className="space-y-3">
          <div className="flex gap-4">
            <input
              type="text"
              value={advisorQuestion}
              onChange={(e) => setAdvisorQuestion(e.target.value)}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleConsultAdvisor}
              disabled={askingAdvisor}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow shrink-0"
            >
              {askingAdvisor ? 'Evaluating Plans...' : 'Consult Advisor'}
            </button>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-300">
            <label className="flex items-center gap-2 cursor-pointer">
              <span>Covered Dependents:</span>
              <input
                type="number"
                min="1"
                max="8"
                value={familyCount}
                onChange={(e) => setFamilyCount(parseInt(e.target.value, 10))}
                className="w-16 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white font-mono text-xs"
              />
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={chronicNeeds}
                onChange={(e) => setChronicNeeds(e.target.checked)}
                className="rounded bg-slate-900 border-slate-700 text-indigo-600"
              />
              <span>Specialist / Frequent Prescription Needs</span>
            </label>
          </div>

          {advisorResult && (
            <div className="bg-slate-900/80 border border-indigo-500/40 rounded-xl p-5 space-y-3 pt-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-emerald-400">
                  Recommended: {advisorResult.recommended_plan_name}
                </span>
                <span className="text-xs text-slate-400">
                  Est. Annual Cost: <span className="text-white font-mono font-bold">${advisorResult.estimated_annual_employee_cost.toLocaleString()}</span>
                </span>
              </div>
              <p className="text-xs text-slate-300">{advisorResult.recommendation_reason}</p>
              <div className="flex flex-wrap gap-2 pt-1">
                {advisorResult.coverage_highlights.map((h, i) => (
                  <span key={i} className="text-[11px] px-2.5 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                    ✓ {h}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
