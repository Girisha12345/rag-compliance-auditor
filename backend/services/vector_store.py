from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.config import get_settings
from backend.services.chunker import Chunk
from backend.services.embedder import get_embedder


class VectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = QdrantClient(url=self.settings.qdrant_url)
        self.embedder = get_embedder()
        self.collection_name = self.settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = {collection.name for collection in self.client.get_collections().collections}
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.embedder.dimension, distance=models.Distance.COSINE),
            )

    def upsert_chunks(self, chunks: list[Chunk]) -> list[str]:
        if not chunks:
            return []
        vectors = self.embedder.embed_texts(chunk.text for chunk in chunks)
        points: list[models.PointStruct] = []
        ids: list[str] = []
        for chunk, vector in zip(chunks, vectors, strict=False):
            point_id = str(uuid4())
            ids.append(point_id)
            payload = {**chunk.metadata, "text": chunk.text}
            points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))
        self.client.upsert(collection_name=self.collection_name, points=points)
        return ids

    def delete_document(self, doc_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))])
            ),
        )

    def delete_page(self, doc_id: str, page_number: int) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id)),
                        models.FieldCondition(key="page_number", match=models.MatchValue(value=page_number)),
                    ]
                )
            ),
        )

    def update_page(self, doc_id: str, page_number: int, new_text: str, doc_name: str | None = None) -> list[str]:
        self.delete_page(doc_id, page_number)
        chunk = Chunk(
            text=new_text,
            metadata={
                "doc_id": doc_id,
                "doc_name": doc_name or "updated_document.pdf",
                "page_number": page_number,
                "section": f"Page {page_number}",
                "char_count": len(new_text),
                "ingested_at": self._now_iso(),
                "chunk_index": 1,
            },
        )
        return self.upsert_chunks([chunk])

    def get_document_stats(self) -> dict[str, Any]:
        scroll = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
            with_payload=True,
        )
        points = scroll[0]
        doc_counter = Counter(str(point.payload.get("doc_id")) for point in points if point.payload)
        page_counts = Counter((str(point.payload.get("doc_id")), int(point.payload.get("page_number", 0))) for point in points if point.payload)
        return {
            "corpus_points": len(points),
            "document_count": len(doc_counter),
            "page_count": len(page_counts),
            "documents": [
                {"doc_id": doc_id, "pages": page_total}
                for doc_id, page_total in doc_counter.items()
            ],
        }

    def search(self, query: str, top_k: int = 20) -> list[dict[str, Any]]:
        vector = self.embedder.embed_query(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return [
            {
                "id": str(result.id),
                "score": float(result.score),
                "text": str(result.payload.get("text", "")),
                "payload": dict(result.payload or {}),
            }
            for result in results
        ]

    @staticmethod
    def _now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


vector_store = VectorStore()
