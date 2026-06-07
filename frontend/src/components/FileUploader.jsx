export default function FileUploader({ label, hint, accept = '.pdf', onFileChange, disabled }) {
  return (
    <label className="group flex cursor-pointer flex-col gap-3 rounded-3xl border border-dashed border-slate-700 bg-slate-900/60 p-5 transition hover:border-cyan-400/60 hover:bg-slate-900">
      <div>
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className="mt-1 text-sm text-slate-400">{hint}</p>
      </div>
      <input
        type="file"
        accept={accept}
        onChange={(event) => onFileChange?.(event.target.files?.[0] ?? null)}
        disabled={disabled}
        className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-xl file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:font-semibold file:text-slate-950 file:transition hover:file:bg-cyan-300"
      />
    </label>
  );
}