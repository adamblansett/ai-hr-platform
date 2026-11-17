import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Employee } from '../types';

export const DirectoryView: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = async (query = '') => {
    try {
      setLoading(true);
      const res = await api.getEmployees(1, query);
      setEmployees(res.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadData(search);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Employee Directory</h2>
          <p className="text-slate-400 text-sm">Centralized roster and departmental reporting tree.</p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2 w-full sm:w-auto">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, role, department..."
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 w-full sm:w-64"
          />
          <button
            type="submit"
            className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg shadow"
          >
            Search
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {employees.map((emp) => (
          <div key={emp.id} className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center font-bold text-indigo-400 border border-slate-600">
                {emp.first_name[0]}{emp.last_name[0]}
              </div>
              <div>
                <h4 className="font-semibold text-white text-sm">
                  {emp.first_name} {emp.last_name}
                </h4>
                <div className="text-xs text-slate-400">{emp.job_title}</div>
              </div>
            </div>

            <div className="text-xs text-slate-400 space-y-1 font-mono pt-2 border-t border-slate-700/60">
              <div className="flex justify-between">
                <span className="text-slate-500">Department:</span>
                <span className="text-slate-300">{emp.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Email:</span>
                <span className="text-indigo-400 truncate max-w-[180px]">{emp.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Status:</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                  emp.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                }`}>
                  {emp.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
