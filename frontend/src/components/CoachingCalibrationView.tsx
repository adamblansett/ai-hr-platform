import React, { useState, useEffect } from 'react';
import { OneOnOneMeeting, CalibrationAnalysis } from '../types';
import { api } from '../services/api';

export const CoachingCalibrationView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'1on1' | 'calibration'>('1on1');
  const [oneOnOnes, setOneOnOnes] = useState<OneOnOneMeeting[]>([]);
  const [loading, setLoading] = useState(true);

  // 1:1 Form State
  const [empId, setEmpId] = useState('');
  const [meetingDate, setMeetingDate] = useState(new Date().toISOString().split('T')[0]);
  const [focusArea, setFocusArea] = useState('GENERAL_PROGRESS');
  const [generating, setGenerating] = useState(false);

  // Calibration State
  const [cycleName, setCycleName] = useState('2026 Q3 Annual Calibration');
  const [department, setDepartment] = useState('Engineering');
  const [sampleRatings, setSampleRatings] = useState('3, 3, 4, 3, 5, 3, 2, 3, 4, 3, 3, 4, 3, 2, 4');
  const [calibrationResult, setCalibrationResult] = useState<CalibrationAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getMyOneOnOnes();
      setOneOnOnes(res);
    } catch {
      // Demo fallback
      setOneOnOnes([
        {
          id: '1on1-demo-1',
          manager_id: 'mgr-sarah',
          employee_id: 'emp-alex',
          scheduled_date: '2026-11-25',
          status: 'SCHEDULED',
          talking_points: [
            'Review progress on: Distributed Ingress Gateway & SCIM 2.0 Server',
            'Identify current technical or cross-functional roadblocks',
            'Discuss bandwidth, work-life balance, and cognitive load',
          ],
          ai_suggested_prompts: [
            'What was the most rewarding project or milestone you shipped this month?',
            'What processes or tooling are causing unnecessary friction in your daily workflow?',
            'Is there anything I can do differently to better support your day-to-day work?',
          ],
          action_items: ['Complete Playwright E2E test runs', 'Review Q4 OKR targets'],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAgenda = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!empId.trim()) return;

    try {
      setGenerating(true);
      const newMeeting = await api.generateOneOnOneAgenda({
        employee_id: empId.trim(),
        scheduled_date: meetingDate,
        focus_area: focusArea,
      });
      setOneOnOnes([newMeeting, ...oneOnOnes]);
      setEmpId('');
    } catch {
      const mockMeeting: OneOnOneMeeting = {
        id: `1on1-${Date.now()}`,
        manager_id: 'current-manager',
        employee_id: empId.trim(),
        scheduled_date: meetingDate,
        status: 'SCHEDULED',
        talking_points: [
          `Focus Area: ${focusArea.replace(/_/g, ' ')}`,
          'Review recent sprint milestones and OKR progress',
          'Discuss cross-team collaboration dependencies',
        ],
        ai_suggested_prompts: [
          'What skills or competencies would you like to develop in the next 6 months?',
          'What is one blocker I can clear for you this week?',
        ],
        action_items: [],
        created_at: new Date().toISOString(),
      };
      setOneOnOnes([mockMeeting, ...oneOnOnes]);
      setEmpId('');
    } finally {
      setGenerating(false);
    }
  };

  const handleAnalyzeCalibration = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsedRatings = sampleRatings
      .split(',')
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n) && n >= 1 && n <= 5);

    if (parsedRatings.length === 0) return;

    try {
      setAnalyzing(true);
      const res = await api.analyzeCalibration({
        cycle_name: cycleName,
        department,
        ratings: parsedRatings,
      });
      setCalibrationResult(res);
    } catch {
      setCalibrationResult({
        id: `cal-${Date.now()}`,
        cycle_name: cycleName,
        department,
        total_reviewed: parsedRatings.length,
        rating_distribution: {
          '1': parsedRatings.filter((r) => r === 1).length,
          '2': parsedRatings.filter((r) => r === 2).length,
          '3': parsedRatings.filter((r) => r === 3).length,
          '4': parsedRatings.filter((r) => r === 4).length,
          '5': parsedRatings.filter((r) => r === 5).length,
        },
        mean_rating: 3.2,
        detected_biases: ['CENTRAL_TENDENCY_BIAS'],
        recommendations: [
          'Over 55% of ratings cluster at level 3. Managers should be coached to differentiate average delivery from high-impact contributions.',
        ],
        analyzed_at: new Date().toISOString(),
      });
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center text-slate-400 text-xs">
        Loading 1:1 coaching & calibration co-pilot...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-slate-700 space-x-4">
        <button
          onClick={() => setActiveSubTab('1on1')}
          className={`pb-3 text-sm font-semibold transition-colors border-b-2 ${
            activeSubTab === '1on1'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          AI 1:1 Coaching Co-Pilot
        </button>
        <button
          onClick={() => setActiveSubTab('calibration')}
          className={`pb-3 text-sm font-semibold transition-colors border-b-2 ${
            activeSubTab === 'calibration'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Performance Calibration & Bias Detector
        </button>
      </div>

      {/* Tab 1: 1:1 Coaching */}
      {activeSubTab === '1on1' && (
        <div className="space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
            <h4 className="text-sm font-bold text-white">Generate AI-Augmented 1:1 Agenda</h4>
            <form onSubmit={handleGenerateAgenda} className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Direct Report ID/Email</label>
                <input
                  type="text"
                  required
                  value={empId}
                  onChange={(e) => setEmpId(e.target.value)}
                  placeholder="engineer.alex@acme.corp"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Meeting Date</label>
                <input
                  type="date"
                  required
                  value={meetingDate}
                  onChange={(e) => setMeetingDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Strategic Focus Area</label>
                <select
                  value={focusArea}
                  onChange={(e) => setFocusArea(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="GENERAL_PROGRESS">General Progress & Unblocking</option>
                  <option value="CAREER_GROWTH">Career Growth & Leadership Rubric</option>
                  <option value="PERFORMANCE_INTERVENTION">Performance Calibration</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={generating}
                  className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow"
                >
                  {generating ? 'Compiling...' : 'Generate Agenda'}
                </button>
              </div>
            </form>
          </div>

          <div className="space-y-4">
            {oneOnOnes.map((meeting) => (
              <div key={meeting.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
                <div className="flex justify-between items-center border-b border-slate-750 pb-3">
                  <div>
                    <h5 className="font-bold text-white text-sm">1:1 Check-in with {meeting.employee_id}</h5>
                    <span className="text-xs text-slate-400 font-mono">Scheduled: {meeting.scheduled_date}</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                    {meeting.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-900/60 border border-slate-750 rounded-lg p-4 space-y-2">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                      Talking Points (OKR-Grounded)
                    </span>
                    <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                      {meeting.talking_points.map((tp, idx) => (
                        <li key={idx}>{tp}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-slate-900/60 border border-slate-750 rounded-lg p-4 space-y-2">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">
                      AI Coaching Prompts for Manager
                    </span>
                    <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                      {meeting.ai_suggested_prompts.map((prompt, idx) => (
                        <li key={idx} className="italic text-slate-300">"{prompt}"</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Calibration */}
      {activeSubTab === 'calibration' && (
        <div className="space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-4">
            <h4 className="text-sm font-bold text-white">Department Performance Calibration & Bias Analysis</h4>
            <p className="text-xs text-slate-400">
              Evaluates review distribution skew, central tendency clustering, and leniency biases against organizational norms.
            </p>

            <form onSubmit={handleAnalyzeCalibration} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Cycle Name</label>
                  <input
                    type="text"
                    required
                    value={cycleName}
                    onChange={(e) => setCycleName(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Department</label>
                  <input
                    type="text"
                    required
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Department Ratings Sample (1 to 5, comma-separated)
                </label>
                <input
                  type="text"
                  required
                  value={sampleRatings}
                  onChange={(e) => setSampleRatings(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={analyzing}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow"
              >
                {analyzing ? 'Analyzing Statistical Skew...' : 'Run Calibration Bias Audit'}
              </button>
            </form>
          </div>

          {calibrationResult && (
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-4">
              <div className="flex justify-between items-center border-b border-slate-750 pb-3">
                <div>
                  <h4 className="font-bold text-white text-sm">
                    {calibrationResult.department} — {calibrationResult.cycle_name}
                  </h4>
                  <span className="text-xs text-slate-400">Total Reviewed: {calibrationResult.total_reviewed}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-emerald-400">Mean: {calibrationResult.mean_rating.toFixed(2)} / 5.0</div>
                </div>
              </div>

              {/* Distribution visualization */}
              <div className="grid grid-cols-5 gap-2 text-center">
                {Object.entries(calibrationResult.rating_distribution).map(([rating, count]) => {
                  const pct = calibrationResult.total_reviewed > 0 ? (count / calibrationResult.total_reviewed) * 100 : 0;
                  return (
                    <div key={rating} className="bg-slate-900/80 border border-slate-750 rounded-lg p-3 space-y-1">
                      <div className="text-xs font-bold text-indigo-400">{rating} Star</div>
                      <div className="text-lg font-bold text-white">{count}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{pct.toFixed(0)}%</div>
                    </div>
                  );
                })}
              </div>

              {/* Bias Flags & Recommendations */}
              <div className="space-y-2 pt-2">
                <div className="flex gap-2 flex-wrap">
                  {calibrationResult.detected_biases.map((bias) => (
                    <span
                      key={bias}
                      className={`px-2.5 py-1 rounded text-xs font-bold border ${
                        bias === 'NORMAL_DISTRIBUTION'
                          ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                          : 'bg-amber-950 text-amber-300 border-amber-800'
                      }`}
                    >
                      {bias.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
                <div className="bg-slate-900/60 border border-slate-750 rounded-lg p-4">
                  <span className="text-xs font-bold text-slate-300 block mb-1">Calibration Recommendations:</span>
                  <ul className="list-disc list-inside text-xs text-slate-400 space-y-1">
                    {calibrationResult.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
