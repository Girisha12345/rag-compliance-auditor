import { useEffect, useState } from 'react';
import FileUploader from '../components/FileUploader';
import StatusBadge from '../components/StatusBadge';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

export default function KnowledgeBase({ refreshKey, onRefresh }) {
  const [stats, setStats] = useState(null);
  const [file, setFile] = useState(null);
  const [docId, setDocId] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadStats() {
      const response = await fetch(`${API_BASE}/ingest/stats`);
      const data = await response.json();
      setStats(data);
    }
    loadStats();
  }, [refreshKey]);

  async function uploadPolicyDocument() {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    await fetch(`${API_BASE}/ingest/upload`, { method: 'POST', body: formData });
    setLoading(false);
    setFile(null);
    onRefresh?.();
  }

  async function deleteDocument() {
    if (!docId.trim()) return;
    setLoading(true);
    await fetch(`${API_BASE}/ingest/document/${encodeURIComponent(docId.trim())}`, { method: 'DELETE' });
    setLoading(false);
    setDocId('');
    onRefresh?.();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <section className="glass-card p-6">
        <p className="section-title">Policy Corpus</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Manage the policy knowledge base</h2>
        <p className="mt-2 text-sm text-slate-400">Upload PDFs into Qdrant, inspect corpus growth, and delete whole documents without rebuilding the collection.</p>

        <div className="mt-6 space-y-4">
          <FileUploader
            label="Policy PDF"
            hint="Ingest policy manuals or reference documents into the corpus."
            accept=".pdf"
            onFileChange={setFile}
          />
          <button
            type="button"
            onClick={uploadPolicyDocument}
            disabled={!file || loading}
            className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Uploading...' : 'Ingest Policy Document'}
          </button>
        </div>
      </section>

      <section className="glass-card p-6">
        <p className="section-title">Corpus Status</p>
        <div className="mt-4 flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4">
          <div>
            <p className="text-sm text-slate-400">Collection state</p>
            <p className="mt-1 text-lg font-semibold text-white">policy_corpus</p>
          </div>
          <StatusBadge status="ready" />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <Metric label="Documents" value={stats?.document_count ?? 0} />
          <Metric label="Pages" value={stats?.page_count ?? 0} />
          <Metric label="Points" value={stats?.corpus_points ?? 0} />
        </div>

        <div className="mt-6 space-y-3">
          <label className="block space-y-2">
            <span className="text-sm font-semibold text-white">Delete document by ID</span>
            <input
              value={docId}
              onChange={(event) => setDocId(event.target.value)}
              className="w-full rounded-2xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-400/70"
              placeholder="doc_id"
            />
          </label>
          <button
            type="button"
            onClick={deleteDocument}
            disabled={!docId.trim() || loading}
            className="rounded-2xl border border-rose-400/30 px-5 py-3 text-sm font-semibold text-rose-200 transition hover:bg-rose-400/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Delete Document
          </button>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/75 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}