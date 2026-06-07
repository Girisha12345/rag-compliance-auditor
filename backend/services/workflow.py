from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.config import get_settings
from backend.services.guardrails import guardrails
from backend.services.llm_client import llm_client
from backend.services.prompt_builder import (
    AUDIT_SYSTEM_PROMPT,
    OUTPUT_VERIFICATION_SYSTEM_PROMPT,
    QUESTION_EXTRACTION_SYSTEM_PROMPT,
    build_audit_prompt,
    build_question_extraction_prompt,
    build_verification_prompt,
)
from backend.services.report_generator import report_generator
from backend.services.retriever import retriever


@dataclass(slots=True)
class AuditReport:
    audit_id: str
    status: str
    summary: str
    overall_risk: str
    violations: list[dict[str, Any]]
    recommendations: list[str]
    pdf_path: str | None
    raw_llm_response: dict[str, Any] | None = None
    blocked_reason: str | None = None


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run_compliance_audit(self, contract_text: str) -> AuditReport:
        audit_id = str(uuid4())
        input_check = guardrails.check_input(contract_text)
        if not input_check.allowed:
            return AuditReport(
                audit_id=audit_id,
                status="blocked",
                summary="Audit blocked by input guardrails.",
                overall_risk="unknown",
                violations=[],
                recommendations=[],
                pdf_path=None,
                blocked_reason=input_check.reason,
            )

        question_response = llm_client.generate(
            QUESTION_EXTRACTION_SYSTEM_PROMPT,
            build_question_extraction_prompt(contract_text),
            json_mode=True,
            max_tokens=1000,
        )
        questions = self._parse_questions(question_response.text)

        evidence_map: dict[str, Any] = {}
        reranked_chunks = []
        for query in questions:
            retrieved = retriever.retrieve_and_rerank(query)
            for chunk in retrieved:
                if chunk.id not in evidence_map:
                    evidence_map[chunk.id] = chunk
                    reranked_chunks.append(chunk)

        truncated_chunks = self._truncate_context(reranked_chunks)
        audit_response = llm_client.generate(
            AUDIT_SYSTEM_PROMPT,
            build_audit_prompt(contract_text, questions, truncated_chunks),
            json_mode=True,
            max_tokens=2000,
        )
        audit_result = self._parse_audit_result(audit_response.text)
        audit_result = guardrails.verify_output(audit_result, evidence_map)

        verification_prompt = build_verification_prompt(json.dumps(audit_result), json.dumps({chunk_id: asdict(chunk) for chunk_id, chunk in evidence_map.items()}))
        verification_response = llm_client.generate(OUTPUT_VERIFICATION_SYSTEM_PROMPT, verification_prompt, json_mode=True)
        final_audit_result = self._merge_verified_result(audit_result, verification_response.text)

        pdf_path = report_generator.create_pdf(final_audit_result, filename=f"audit_{audit_id}.pdf")
        return AuditReport(
            audit_id=audit_id,
            status="complete",
            summary=final_audit_result.get("audit_summary", final_audit_result.get("summary", "")),
            overall_risk=str(final_audit_result.get("compliance_score", final_audit_result.get("overall_risk", "medium"))),
            violations=final_audit_result.get("violations", []),
            recommendations=final_audit_result.get("recommendations", final_audit_result.get("compliant_clauses", [])),
            pdf_path=str(pdf_path),
            raw_llm_response={
                "questions": questions,
                "audit_response": audit_response.text,
                "verification_response": verification_response.text,
            },
        )

    def _parse_questions(self, text: str) -> list[str]:
        try:
            data = json.loads(text)
            questions = data.get("questions", []) if isinstance(data, dict) else data
            if isinstance(questions, dict):
                questions = questions.get("questions", [])
            return [question for question in questions if isinstance(question, str) and question.strip()][:10]
        except Exception:
            return ["Does the contract comply with data retention requirements?", "Are security controls specified?"]

    def _parse_audit_result(self, text: str) -> dict[str, Any]:
        try:
            data = json.loads(text)
        except Exception:
            data = {}
        return {
            "audit_summary": data.get("audit_summary", data.get("summary", "Automated compliance audit completed.")),
            "compliance_score": data.get("compliance_score", data.get("overall_risk", 50)),
            "violations": data.get("violations", []),
            "compliant_clauses": data.get("compliant_clauses", data.get("recommendations", [])),
            "uncovered_topics": data.get("uncovered_topics", []),
        }

    def _merge_verified_result(self, audit_result: dict[str, Any], verification_text: str) -> dict[str, Any]:
        try:
            verified = json.loads(verification_text)
        except Exception:
            return audit_result
        if isinstance(verified, dict) and "violations" in verified:
            audit_result["violations"] = verified["violations"]
        return audit_result

    def _truncate_context(self, chunks: list[Any]) -> list[Any]:
        words_budget = self.settings.max_context_tokens * 1.5
        running_words = 0
        selected = []
        for chunk in chunks:
            word_count = len(chunk.text.split())
            if running_words + word_count > words_budget:
                break
            selected.append(chunk)
            running_words += word_count
        if selected:
            return selected
        return chunks[:3]


workflow_orchestrator = WorkflowOrchestrator()
