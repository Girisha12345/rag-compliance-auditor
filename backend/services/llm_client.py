from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from backend.config import get_settings

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - optional dependency
    Anthropic = None


@dataclass(slots=True)
class LLMResponse:
    text: str
    provider: str
    raw: Any | None = None


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.anthropic_client = Anthropic(api_key=self.settings.anthropic_api_key) if Anthropic and self.settings.anthropic_api_key else None

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False, max_tokens: int = 2000) -> LLMResponse:
        try:
            if self.anthropic_client is not None:
                return self._generate_anthropic(system_prompt, user_prompt, json_mode=json_mode, max_tokens=max_tokens)
            if self.settings.openai_api_key:
                return self._generate_openai(system_prompt, user_prompt, json_mode=json_mode, max_tokens=max_tokens)
        except Exception:
            pass
        return self._fallback_response(user_prompt, json_mode=json_mode)

    def _generate_anthropic(self, system_prompt: str, user_prompt: str, json_mode: bool, max_tokens: int) -> LLMResponse:
        message = self.anthropic_client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in message.content if hasattr(block, "text"))
        return LLMResponse(text=text, provider="anthropic", raw=message)

    def _generate_openai(self, system_prompt: str, user_prompt: str, json_mode: bool, max_tokens: int) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.openai_chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        return LLMResponse(text=text, provider="openai", raw=data)

    def _fallback_response(self, user_prompt: str, json_mode: bool) -> LLMResponse:
        if "extract" in user_prompt.lower() and "question" in user_prompt.lower():
            text = json.dumps({"questions": ["Does the contract mention data retention?", "Does it require incident reporting?", "Does it define access controls?"]})
        else:
            text = json.dumps(
                {
                    "summary": "Fallback analysis generated without an external LLM.",
                    "violations": [
                        {
                            "finding": "Potential policy mismatch requires human review.",
                            "severity": "medium",
                            "evidence_chunk_ids": [],
                            "status": "unverified",
                        }
                    ],
                }
            ) if json_mode else "Fallback analysis generated without an external LLM."
        return LLMResponse(text=text, provider="fallback")


llm_client = LLMClient()
