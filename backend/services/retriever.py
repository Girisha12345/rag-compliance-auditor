from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.config import get_settings
from backend.services.vector_store import vector_store

try:
    from flashrank import Ranker, RerankRequest
except Exception:  # pragma: no cover - optional dependency
    Ranker = None
    RerankRequest = None


@dataclass(slots=True)
class RetrievedChunk:
    id: str
    score: float
    text: str
    payload: dict[str, Any]


class Retriever:
    def __init__(self) -> None:
        settings = get_settings()
        self.ranker = Ranker(model_name=settings.flashrank_model) if Ranker is not None else None

    def retrieve_and_rerank(self, query: str, top_k_recall: int = 20, top_k_precision: int = 5) -> list[RetrievedChunk]:
        raw_results = vector_store.search(query=query, top_k=top_k_recall)
        if not raw_results:
            return []
        if self.ranker is None or RerankRequest is None:
            return [
                RetrievedChunk(id=item["id"], score=item["score"], text=item["text"], payload=item["payload"])
                for item in raw_results[:top_k_precision]
            ]

        passages = [{"id": item["id"], "text": item["text"]} for item in raw_results]
        rerank_request = RerankRequest(query=query, passages=passages)
        reranked = self.ranker.rerank(rerank_request)
        rank_lookup = {item["id"]: item for item in raw_results}
        chunks: list[RetrievedChunk] = []
        for ranked in reranked[:top_k_precision]:
            source = rank_lookup.get(str(ranked["id"]))
            if not source:
                continue
            chunks.append(
                RetrievedChunk(
                    id=str(source["id"]),
                    score=float(ranked.get("score", source["score"])),
                    text=source["text"],
                    payload=source["payload"],
                )
            )
        return chunks


retriever = Retriever()
