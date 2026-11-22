import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Course, CourseEnrollment, ComplianceAuditSummary } from '../types';

export const LearningDevelopmentView: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [enrollments, setEnrollments] = useState<CourseEnrollment[]>([]);
  const [audit, setAudit] = useState<ComplianceAuditSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [courseData, enrData, auditData] = await Promise.all([
        api.getCourses(),
        api.getMyEnrollments('emp-001'),
        api.getComplianceAudit(),
      ]);
      setCourses(courseData);
      setEnrollments(enrData);
      setAudit(auditData);
    } catch (err) {
      console.error('Failed to load learning data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleEnroll = async (courseId: string) => {
    try {
      await api.enrollCourse(courseId, 'emp-001');
      fetchData();
    } catch (err) {
      alert('Enrollment failed: ' + err);
    }
  };

  const handleCompleteLesson = async (enrollmentId: string) => {
    try {
      await api.updateCourseProgress(enrollmentId, 100, 95.0);
      fetchData();
    } catch (err) {
      alert('Progress update failed: ' + err);
    }
  };

  const filteredCourses = selectedCategory === 'ALL'
    ? courses
    : courses.filter((c) => c.category === selectedCategory);

  const getEnrollmentForCourse = (courseId: string) =>
    enrollments.find((e) => e.course_id === courseId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🎓</span> Learning & Development (L&D) / Compliance LMS
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Mandatory annual compliance certifications, verified digital credentials, and role-based engineering upskilling.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Company Compliance Rate</div>
          <div className="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {audit ? `${audit.compliance_rate_percentage}%` : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">SOC 2 / ISO 27001 readiness</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Mandatory Modules</div>
          <div className="mt-1 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {audit ? audit.total_mandatory_courses : '—'}
          </div>
          <div className="mt-1 text-xs text-gray-400">Statutory annual training</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">My Completed Certifications</div>
          <div className="mt-1 text-2xl font-bold text-amber-500">
            {enrollments.filter((e) => e.status === 'COMPLETED').length}
          </div>
          <div className="mt-1 text-xs text-gray-400">Verified digital badges</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Overdue Recertifications</div>
          <div className="mt-1 text-2xl font-bold text-green-500">
            {audit ? audit.overdue_recertifications_count : 0}
          </div>
          <div className="mt-1 text-xs text-gray-400">100% on-track status</div>
        </div>
      </div>

      {/* Compliance Audit Recommendation Banner */}
      {audit && audit.recommendations.length > 0 && (
        <div className="p-4 rounded-xl border border-indigo-200 dark:border-indigo-900 bg-indigo-50 dark:bg-indigo-950/40 text-xs text-indigo-900 dark:text-indigo-200 space-y-1">
          <div className="font-bold flex items-center gap-1">
            <span>🛡️</span> Automated Auditor Insights:
          </div>
          <ul className="list-disc list-inside space-y-0.5">
            {audit.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2">
        {['ALL', 'COMPLIANCE', 'TECHNICAL', 'LEADERSHIP'].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              selectedCategory === cat
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Course Catalog Grid */}
      {loading ? (
        <div className="p-12 text-center text-gray-500">Loading learning catalog & certifications...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCourses.map((c) => {
            const enr = getEnrollmentForCourse(c.id);
            return (
              <div
                key={c.id}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 flex flex-col justify-between shadow-sm space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-indigo-50 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300">
                      {c.category}
                    </span>
                    {c.is_mandatory && (
                      <span className="px-2 py-0.5 text-xs font-semibold rounded bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300">
                        MANDATORY
                      </span>
                    )}
                  </div>

                  <h3 className="font-bold text-base text-gray-900 dark:text-white leading-snug">{c.title}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{c.description}</p>

                  <div className="text-xs text-gray-400 flex items-center gap-3 pt-1">
                    <span>⏱️ {c.duration_minutes} mins</span>
                    <span>🎯 Passing: {c.passing_score_percentage}%</span>
                    <span>🗓️ Validity: {c.certification_validity_days} days</span>
                  </div>
                </div>

                {/* Enrollment & Status Action */}
                <div className="pt-3 border-t border-gray-100 dark:border-gray-700/60">
                  {!enr ? (
                    <button
                      onClick={() => handleEnroll(c.id)}
                      className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg"
                    >
                      Enroll in Module
                    </button>
                  ) : enr.status === 'COMPLETED' ? (
                    <div className="p-3 rounded-lg bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-900 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-green-800 dark:text-green-300 flex items-center gap-1">
                          <span>✅</span> Certified & Compliant (Score: {enr.score}%)
                        </span>
                        <span className="font-mono text-[10px] text-gray-500">{enr.certificate_id}</span>
                      </div>
                      <div className="text-[11px] text-gray-500">
                        Completed: {enr.completed_at ? new Date(enr.completed_at).toLocaleDateString() : '—'} • Expires:{' '}
                        {enr.expires_at ? new Date(enr.expires_at).toLocaleDateString() : '—'}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>In Progress</span>
                        <span className="font-bold text-indigo-600">{enr.progress_percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all"
                          style={{ width: `${enr.progress_percentage}%` }}
                        />
                      </div>
                      <button
                        onClick={() => handleCompleteLesson(enr.id)}
                        className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium rounded-lg"
                      >
                        Complete Module & Pass Exam
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
