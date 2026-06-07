import { useState } from 'react';
import AuditReport from '../components/AuditReport';
import FileUploader from '../components/FileUploader';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

export default function AuditPage({ onAuditComplete }) {
  const [contractText, setContractText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState(null);

  async function runAudit() {
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (contractText.trim()) {
        formData.append('contract_text', contractText.trim());
      }
      const response = await fetch(`${API_BASE}/audit/run`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error((await response.json()).detail ?? 'Audit request failed');
      }
      const data = await response.json();
      setReport(data);
      onAuditComplete?.(data);
    } catch (exception) {
      setError(exception.message || 'Failed to run audit');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section className="glass-card p-6">
        <p className="section-title">Audit Input</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Run a structured compliance audit</h2>
        <p className="mt-2 text-sm text-slate-400">Upload a contract PDF or paste extracted text, then let the workflow extract questions, retrieve evidence, and generate the report.</p>

        <div className="mt-6 space-y-4">
          <FileUploader
            label="Contract PDF"
            hint="Optional. If provided, the server extracts and audits the document page-by-page."
            accept=".pdf"
            onFileChange={setFile}
          />

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-white">Contract text</span>
            <textarea
              value={contractText}
              onChange={(event) => setContractText(event.target.value)}
              rows={14}
              className="w-full rounded-3xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-400/70"
              placeholder="Paste the contract text here when a PDF is not available..."
            />
          </label>
        </div>

        {error && <p className="mt-4 rounded-2xl border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</p>}

        <button
          type="button"
          onClick={runAudit}
          disabled={loading}
          className="mt-5 rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Running audit...' : 'Generate Audit Report'}
        </button>
      </section>

      <div className="space-y-6">
        <section className="glass-card p-6">
          <p className="section-title">Pipeline Stages</p>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            {[
              'Input guardrail validation',
              'Question extraction from contract',
              'Qdrant retrieval and FlashRank reranking',
              'LLM synthesis with failover',
              'Evidence verification and PDF creation',
            ].map((item, index) => (
              <div key={item} className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-cyan-400/15 text-xs font-semibold text-cyan-300">
                  {index + 1}
                </span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </section>

        <AuditReport report={report} />
      </div>
    </div>
  );
}