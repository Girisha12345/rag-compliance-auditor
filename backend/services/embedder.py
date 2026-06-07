from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import httpx

from backend.config import get_settings

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


class Embedder:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        if self.settings.embedding_provider == "local" and SentenceTransformer is not None:
            self._model = SentenceTransformer(self.settings.embedding_model_name)

    @property
    def dimension(self) -> int:
        return self.settings.embedding_dimension if self.settings.embedding_provider == "local" else 1536

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []
        if self.settings.embedding_provider == "openai" and self.settings.openai_api_key:
            return self._embed_openai(text_list)
        if self._model is None:
            return [self._fallback_embed(text) for text in text_list]
        vectors = self._model.encode(text_list, normalize_embeddings=True).tolist()
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"input": texts, "model": self.settings.openai_embedding_model}
        response = httpx.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()["data"]
        return [item["embedding"] for item in data]

    @staticmethod
    def _fallback_embed(text: str, dimension: int = 384) -> list[float]:
        vector = [0.0] * dimension
        for index, token in enumerate(text.lower().split()):
            slot = abs(hash(token)) % dimension
            vector[slot] += 1.0 + (index % 7) * 0.01
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
