from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from backend.config import get_settings
from backend.services.chunker import chunk_pdf
from backend.services.workflow import workflow_orchestrator

router = APIRouter(prefix="/audit", tags=["audit"])
settings = get_settings()


@router.post("/run")
async def run_audit(request: Request):
    resolved_text: str | None = None
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
        resolved_text = str(payload.get("contract_text", "")).strip() or None
    else:
        form = await request.form()
        contract_text = str(form.get("contract_text", "")).strip()
        resolved_text = contract_text or None
        file = form.get("file")
        if isinstance(file, UploadFile):
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF uploads are supported for file-based audits.")
            temp_path = settings.data_dir / f"audit_{file.filename}"
            temp_path.write_bytes(await file.read())
            chunks = chunk_pdf(temp_path, doc_name=file.filename)
            resolved_text = "\n\n".join(chunk.text for chunk in chunks)

    if not resolved_text:
        raise HTTPException(status_code=400, detail="Provide either contract_text or a PDF file.")

    report = workflow_orchestrator.run_compliance_audit(resolved_text)
    response = {
        "audit_id": report.audit_id,
        "status": report.status,
        "summary": report.summary,
        "overall_risk": report.overall_risk,
        "violations": report.violations,
        "recommendations": report.recommendations,
        "blocked_reason": report.blocked_reason,
        "pdf_available": bool(report.pdf_path),
        "report_url": f"{settings.api_prefix}/audit/{report.audit_id}/report" if report.pdf_path else None,
    }
    return JSONResponse(response)


@router.get("/{audit_id}/report")
async def download_report(audit_id: str):
    report_path = settings.reports_dir / f"audit_{audit_id}.pdf"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(report_path, media_type="application/pdf", filename=report_path.name)
