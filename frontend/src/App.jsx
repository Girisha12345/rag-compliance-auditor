import { useMemo, useState } from 'react';
import Dashboard from './pages/Dashboard';
import AuditPage from './pages/AuditPage';
import KnowledgeBase from './pages/KnowledgeBase';

const tabs = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'audit', label: 'Audit' },
  { id: 'knowledge-base', label: 'Knowledge Base' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [lastAudit, setLastAudit] = useState(null);
  const [statsRefreshKey, setStatsRefreshKey] = useState(0);

  const activeLabel = useMemo(() => tabs.find((tab) => tab.id === activeTab)?.label ?? 'Dashboard', [activeTab]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="glass-card mb-6 flex flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="section-title">Enterprise RAG Workflow</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Automated Compliance Auditor
            </h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-300">
              Process-driven contract analysis with policy retrieval, reranking, guardrails, and downloadable PDF evidence packs.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-slate-900/70 p-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                  activeTab === tab.id ? 'bg-cyan-400 text-slate-950' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </header>

        <main className="grid flex-1 gap-6">
          {activeTab === 'dashboard' && (
            <Dashboard
              activeLabel={activeLabel}
              lastAudit={lastAudit}
              onGoToAudit={() => setActiveTab('audit')}
              onGoToKnowledgeBase={() => setActiveTab('knowledge-base')}
            />
          )}
          {activeTab === 'audit' && (
            <AuditPage
              onAuditComplete={(result) => {
                setLastAudit(result);
                setActiveTab('dashboard');
              }}
            />
          )}
          {activeTab === 'knowledge-base' && (
            <KnowledgeBase refreshKey={statsRefreshKey} onRefresh={() => setStatsRefreshKey((value) => value + 1)} />
          )}
        </main>
      </div>
    </div>
  );
}