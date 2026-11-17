import React, { useState } from 'react';
import { api } from '../services/api';
import { PolicyAnswer } from '../types';

export const PolicyAssistantView: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<PolicyAnswer | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      setLoading(true);
      const res = await api.askPolicyAI(question);
      setAnswer(res);
    } catch (err: any) {
      alert(err.message || 'Error asking AI assistant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-400 text-xs font-semibold uppercase mb-3">
          pgvector RAG Knowledge Base
        </div>
        <h2 className="text-xl font-bold text-white">HR Policy & Compliance AI Assistant</h2>
        <p className="text-slate-400 text-sm mt-1 mb-6">
          Ask questions regarding remote work guidelines, PTO accruals, medical benefits, or SOPs. Responses are grounded strictly in company documentation with cited clauses.
        </p>

        <form onSubmit={handleAsk} className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., How many days in advance do I need to submit a PTO request?"
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors shadow"
          >
            {loading ? 'Consulting Policies...' : 'Ask AI'}
          </button>
        </form>
      </div>

      {answer && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-700 pb-3">
            <h3 className="font-semibold text-white">Answer</h3>
            <span className="text-xs text-slate-400 font-mono">Model: {answer.model_used}</span>
          </div>

          <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
            {answer.answer}
          </div>

          {answer.citations.length > 0 && (
            <div className="pt-4 border-t border-slate-700">
              <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">
                Cited Policy Sources ({answer.citations.length})
              </h4>
              <div className="grid gap-2 sm:grid-cols-2">
                {answer.citations.map((cite, i) => (
                  <div key={i} className="bg-slate-900/80 border border-slate-750 p-3 rounded-lg text-xs">
                    <div className="font-semibold text-white flex justify-between">
                      <span>{cite.title}</span>
                      <span className="text-indigo-400 font-mono">{Math.round(cite.relevance_score * 100)}% match</span>
                    </div>
                    <div className="text-slate-400 text-[11px] mt-1 line-clamp-2">{cite.snippet}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
