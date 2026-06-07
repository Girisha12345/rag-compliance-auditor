from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from backend.config import get_settings

PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"developer message",
    r"reveal hidden",
    r"bypass",
    r"jailbreak",
]

OFF_TOPIC_PATTERNS = [
    r"weather",
    r"sports",
    r"recipe",
]


@dataclass(slots=True)
class GuardrailResult:
    allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] | None = None


class Guardrails:
    def __init__(self) -> None:
        self.settings = get_settings()

    def check_input(self, text: str) -> GuardrailResult:
        if len(text.strip()) < self.settings.audit_min_input_chars:
            return GuardrailResult(allowed=False, reason="Input too short for audit analysis.")
        lowered = text.lower()
        if any(re.search(pattern, lowered) for pattern in PROMPT_INJECTION_PATTERNS):
            return GuardrailResult(allowed=False, reason="Prompt injection detected.")
        if any(re.search(pattern, lowered) for pattern in OFF_TOPIC_PATTERNS):
            return GuardrailResult(allowed=False, reason="Off-topic content detected.")
        return GuardrailResult(allowed=True)

    def verify_output(self, audit_result: dict[str, Any], evidence_chunks: dict[str, Any]) -> dict[str, Any]:
        verified = []
        for violation in audit_result.get("violations", []):
            evidence_ids = [str(chunk_id) for chunk_id in violation.get("evidence_chunk_ids", [])]
            if not evidence_ids:
                violation["status"] = "unverified"
                verified.append(violation)
                continue
            if all(chunk_id in evidence_chunks for chunk_id in evidence_ids):
                violation["status"] = "verified"
                verified.append(violation)
            else:
                violation["status"] = "unverified"
                violation["evidence_chunk_ids"] = [chunk_id for chunk_id in evidence_ids if chunk_id in evidence_chunks]
                verified.append(violation)
        audit_result["violations"] = verified
        return audit_result


guardrails = Guardrails()
