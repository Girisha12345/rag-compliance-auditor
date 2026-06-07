from __future__ import annotations

import json
from textwrap import dedent
from typing import Iterable

from backend.services.retriever import RetrievedChunk


AUDIT_SYSTEM_PROMPT = dedent(
    """
    You are ComplianceAI, a strict enterprise legal and policy auditor.
    Your ONLY job is to analyze the provided contract against the retrieved policy excerpts.

    Rules:
    - ONLY flag violations that are directly supported by the provided policy excerpts.
    - For every violation, cite the exact policy source using doc_name and page_number.
    - Output ONLY valid JSON. No preamble, no markdown, no explanation outside JSON.
    - If the contract is compliant on a point, state COMPLIANT. Do not invent issues.
    - Never use external knowledge. If the policy excerpts do not address a topic, say NOT COVERED IN CORPUS.

    Return JSON that matches the requested schema exactly.
    """
).strip()

QUESTION_EXTRACTION_SYSTEM_PROMPT = dedent(
    """
    You are analyzing a legal contract for compliance auditing.

    Internal steps:
    1. Identify the major clause types present in the contract.
    2. Formulate 5 to 10 precise compliance questions that can be answered by searching a policy corpus.
    3. Return only a JSON array of strings.

    Requirements:
    - Output only valid JSON.
    - Do not include explanations, markdown, or wrapper objects.
    - Each item must be a concise compliance question.
    - Focus on obligations, prohibited actions, reporting, retention, security, indemnification, termination, data handling, and audit rights.
    """
).strip()

OUTPUT_VERIFICATION_SYSTEM_PROMPT = dedent(
    """
    You are a strict evidence verifier. Remove any compliance finding that is not supported by the cited chunks.
    Return only valid JSON with verified violations.
    """
).strip()


def build_question_extraction_prompt(contract_text: str) -> str:
    return dedent(
        f"""
        Contract text:
        {contract_text}

        Return a JSON array of 5 to 10 specific compliance questions.
        Example:
        ["Does the contract define data retention period?", "Is there an indemnification clause?"]
        """
    ).strip()


def build_audit_prompt(contract_text: str, queries: Iterable[str], reranked_chunks: Iterable[RetrievedChunk]) -> str:
    evidence = [
        {
            "chunk_id": chunk.id,
            "text": chunk.text,
            "source": chunk.payload.get("doc_name"),
            "page_number": chunk.payload.get("page_number"),
            "section": chunk.payload.get("section"),
        }
        for chunk in reranked_chunks
    ]
    return dedent(
        f"""
        Contract text:
        {contract_text}

        Audit questions:
        {json.dumps(list(queries), indent=2)}

        Retrieved evidence:
        {json.dumps(evidence, indent=2)}

                Produce JSON in this schema:
        {{
                    "audit_summary": "string",
                    "compliance_score": 0,
          "violations": [
            {{
                            "issue": "string",
                            "contract_excerpt": "string",
                            "policy_reference": "doc_name, page X",
                            "severity": "HIGH|MEDIUM|LOW",
                            "recommendation": "string"
            }}
          ],
                    "compliant_clauses": ["string"],
                    "uncovered_topics": ["string"]
        }}

                Guidance:
                - If a point is compliant, include it in compliant_clauses using the word COMPLIANT.
                - If a topic is not covered by the retrieved policy excerpts, include it in uncovered_topics using NOT COVERED IN CORPUS.
                - Only use the retrieved evidence shown above.
        """
    ).strip()


def build_verification_prompt(audit_result_json: str, evidence_json: str) -> str:
    return dedent(
        f"""
        Draft audit JSON:
        {audit_result_json}

        Evidence map:
        {evidence_json}

        Remove or mark unverified any violation without direct evidence support.
        Return JSON only.
        """
    ).strip()
