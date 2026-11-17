import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { OnboardingProgress } from '../types';

export const OnboardingView: React.FC = () => {
  const [progress, setProgress] = useState<OnboardingProgress | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getMyOnboardingProgress();
      setProgress(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleTask = async (taskId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
    await api.updateTaskStatus(taskId, nextStatus);
    loadData();
  };

  if (loading) {
    return <div className="text-slate-400 p-8 text-center">Loading onboarding roadmap...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-sm">
        <h2 className="text-xl font-bold text-white mb-2">Onboarding Progress</h2>
        <p className="text-slate-400 text-sm mb-4">Complete all checklist items to unlock full access.</p>
        
        <div className="w-full bg-slate-700 h-3 rounded-full overflow-hidden mb-2">
          <div
            className="bg-indigo-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${progress?.completion_percentage || 0}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-slate-400 font-mono">
          <span>{progress?.completed_tasks || 0} of {progress?.total_tasks || 0} completed</span>
          <span>{progress?.completion_percentage || 0}%</span>
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/80">
          <h3 className="font-semibold text-white">Required Tasks</h3>
        </div>
        <div className="divide-y divide-slate-700">
          {progress?.tasks.map((task) => (
            <div key={task.id} className="p-4 flex items-center justify-between hover:bg-slate-750 transition-colors">
              <div className="flex items-start gap-4">
                <input
                  type="checkbox"
                  checked={task.status === 'COMPLETED'}
                  onChange={() => handleToggleTask(task.id, task.status)}
                  className="mt-1 w-5 h-5 rounded border-slate-600 text-indigo-600 focus:ring-indigo-500 bg-slate-700 cursor-pointer"
                />
                <div>
                  <h4 className={`text-sm font-medium ${task.status === 'COMPLETED' ? 'line-through text-slate-400' : 'text-white'}`}>
                    {task.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">{task.description}</p>
                  <div className="flex gap-2 mt-2">
                    <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-slate-700 text-indigo-400 rounded">
                      {task.category}
                    </span>
                    {task.due_date && (
                      <span className="text-[11px] text-slate-400">Due: {task.due_date}</span>
                    )}
                  </div>
                </div>
              </div>
              <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                task.status === 'COMPLETED'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}>
                {task.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
