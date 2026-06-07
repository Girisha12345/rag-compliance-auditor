export default function StatusBadge({ status }) {
  const styles = {
    complete: 'bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-400/30',
    blocked: 'bg-rose-400/15 text-rose-300 ring-1 ring-rose-400/30',
    processing: 'bg-amber-400/15 text-amber-300 ring-1 ring-amber-400/30',
    ready: 'bg-cyan-400/15 text-cyan-300 ring-1 ring-cyan-400/30',
  };

  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${styles[status] ?? styles.ready}`}>{status}</span>;
}