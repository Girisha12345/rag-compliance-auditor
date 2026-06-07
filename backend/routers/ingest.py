from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.config import get_settings
from backend.services.chunker import chunk_pdf
from backend.services.vector_store import vector_store

router = APIRouter(prefix="/ingest", tags=["ingest"])
settings = get_settings()


class PageUpdateRequest(BaseModel):
    doc_id: str
    page_number: int
    new_text: str
    doc_name: str | None = None


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    doc_id = str(uuid4())
    upload_path = settings.data_dir / f"{doc_id}_{file.filename}"
    upload_path.write_bytes(await file.read())

    chunks = chunk_pdf(upload_path, doc_name=file.filename, doc_id=doc_id)
    point_ids = vector_store.upsert_chunks(chunks)
    return JSONResponse(
        {
            "doc_id": doc_id,
            "doc_name": file.filename,
            "chunks_indexed": len(point_ids),
            "message": "Document ingested successfully.",
        }
    )


@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    vector_store.delete_document(doc_id)
    return {"doc_id": doc_id, "status": "deleted"}


@router.put("/page")
async def update_page(payload: PageUpdateRequest):
    point_ids = vector_store.update_page(payload.doc_id, payload.page_number, payload.new_text, doc_name=payload.doc_name)
    return {"doc_id": payload.doc_id, "page_number": payload.page_number, "point_ids": point_ids, "status": "updated"}


@router.get("/stats")
async def stats():
    return vector_store.get_document_stats()
