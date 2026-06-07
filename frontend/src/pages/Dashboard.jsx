export default function Dashboard({ activeLabel, lastAudit, onGoToAudit, onGoToKnowledgeBase }) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <section className="glass-card p-6">
        <p className="section-title">Workflow Overview</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">A process engine for compliance review</h2>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
          Contracts move through input guardrails, question extraction, retrieval, reranking, evidence grounding, and PDF report generation. The system is built for repeatable auditing, not chat.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[
            ['Guardrails', 'Injection detection + short-input blocking'],
            ['Retriever', 'Qdrant search with page-level metadata'],
            ['Reranker', 'FlashRank precision filtering'],
            ['Reporter', 'Structured PDF output with citations'],
          ].map(([title, description]) => (
            <div key={title} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm font-semibold text-white">{title}</p>
              <p className="mt-2 text-sm text-slate-400">{description}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button type="button" onClick={onGoToAudit} className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
            Start Audit
          </button>
          <button type="button" onClick={onGoToKnowledgeBase} className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/5">
            Manage Knowledge Base
          </button>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="glass-card p-6">
          <p className="section-title">Session State</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Current View: {activeLabel}</h3>
          <p className="mt-3 text-sm text-slate-400">
            The UI keeps the latest audit result in memory and refreshes corpus statistics on demand.
          </p>
        </section>

        <section className="glass-card p-6">
          <p className="section-title">Latest Audit</p>
          {lastAudit ? (
            <div className="mt-3 space-y-3 text-sm text-slate-300">
              <p><span className="font-semibold text-white">Risk:</span> {lastAudit.overall_risk}</p>
              <p><span className="font-semibold text-white">Status:</span> {lastAudit.status}</p>
              <p><span className="font-semibold text-white">Violations:</span> {lastAudit.violations?.length ?? 0}</p>
              <p className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-400">{lastAudit.summary}</p>
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-400">No audit has been run in this session yet.</p>
          )}
        </section>
      </aside>
    </div>
  );
}