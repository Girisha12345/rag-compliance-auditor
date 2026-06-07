import StatusBadge from './StatusBadge';

export default function AuditReport({ report }) {
  if (!report) {
    return null;
  }

  return (
    <section className="glass-card overflow-hidden p-6">
      <div className="flex flex-col gap-4 border-b border-white/10 pb-5 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="section-title">Latest Audit</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">{report.summary || 'Audit completed'}</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">Audit ID: {report.audit_id}</p>
        </div>
        <div className="flex flex-col items-start gap-3">
          <StatusBadge status={report.status} />
          {report.report_url && (
            <a className="rounded-xl border border-cyan-400/40 px-4 py-2 text-sm font-medium text-cyan-300 transition hover:bg-cyan-400/10" href={report.report_url} target="_blank" rel="noreferrer">
              Download PDF
            </a>
          )}
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl bg-slate-900/75 p-4">
          <p className="text-sm font-semibold text-slate-200">Overall Risk</p>
          <p className="mt-2 text-3xl font-bold text-white">{report.overall_risk ?? 'medium'}</p>
          <p className="mt-3 text-sm text-slate-400">{report.blocked_reason ? `Blocked: ${report.blocked_reason}` : 'Findings are grounded against retrieved policy evidence.'}</p>
        </div>
        <div className="rounded-2xl bg-slate-900/75 p-4">
          <p className="text-sm font-semibold text-slate-200">Recommendations</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            {(report.recommendations ?? []).length > 0 ? report.recommendations.map((item) => <li key={item}>• {item}</li>) : <li>No recommendations returned.</li>}
          </ul>
        </div>
      </div>

      <div className="mt-6 space-y-4">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-300">Flagged Violations</p>
        {(report.violations ?? []).length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 text-sm text-slate-400">No violations flagged.</div>
        ) : (
          report.violations.map((violation, index) => (
            <article key={`${violation.question}-${index}`} className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Question</p>
                  <h3 className="mt-1 text-base font-semibold text-white">{violation.question}</h3>
                </div>
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-200">
                  {violation.severity}
                </span>
              </div>
              <p className="mt-4 text-sm text-slate-300">{violation.finding}</p>
              <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
                <span className="rounded-full bg-white/5 px-3 py-1">{violation.status}</span>
                {(violation.evidence_chunk_ids ?? []).map((chunkId) => (
                  <span key={chunkId} className="rounded-full bg-cyan-400/10 px-3 py-1 text-cyan-200">
                    {chunkId}
                  </span>
                ))}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}