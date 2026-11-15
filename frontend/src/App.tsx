import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-6">
      <header className="max-w-2xl text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-400 text-sm font-medium">
          Open-Source HR & Employee Operations Microservice
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
          ai-hr-platform
        </h1>
        <p className="text-slate-400 text-base leading-relaxed">
          Automated employee onboarding, policy compliance RAG, leave tracking,
          and AI-assisted performance cycles with multi-model local LLM inference.
        </p>
      </header>
    </div>
  );
};

export default App;
