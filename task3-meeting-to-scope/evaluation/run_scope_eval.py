
"""Evaluate Meeting-to-Scope structure, safeguards, and topic coverage.

Uses fictional transcripts. Topic-term coverage is a lexical diagnostic,
not a judgment of semantic correctness or scope quality.
"""

from __future__ import annotations

import csv
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVALUATION_DIR = Path(__file__).resolve().parent
TASK_DIR = EVALUATION_DIR.parent
DATASET_PATH = EVALUATION_DIR / "scope_evaluation_cases.json"
JSON_REPORT_PATH = EVALUATION_DIR / "scope_eval_results.json"
CSV_REPORT_PATH = EVALUATION_DIR / "scope_eval_results.csv"

# This project has used port 8001 for the Knowledge Brain API.
# An explicitly supplied environment value takes precedence.
os.environ.setdefault(
    "KNOWLEDGE_BRAIN_URL",
    "http://127.0.0.1:8001",
)

sys.path.insert(0, str(TASK_DIR))

from meeting_to_scope import (  # noqa: E402
    SCOPE_LIST_FIELDS,
    generate_scope_of_work,
)


TERM_VARIANTS: dict[tuple[str, str, str], tuple[str, ...]] = {
    # Expected topic terms. These preserve the dataset's original labels
    # while accepting explicit wording used by the generated draft.
    ("MS11", "topic", "publication"): ("publishing",),
    ("MS16", "topic", "required fields"): ("mandatory fields",),
    ("MS18", "topic", "requirements"): ("required",),
    ("MS19", "topic", "requirements"): ("desired behavior",),
    # Expected open-question terms. Do not add broad semantic matches here;
    # every alternative names the same decision or clarification topic.
    ("MS04", "open_question", "acceptance criteria"): (
        "criteria for accepting",
    ),
    ("MS05", "open_question", "priority"): ("delivered first",),
    ("MS06", "open_question", "feasibility"): (
        "capable of supporting",
        "automation capabilities",
    ),
    ("MS06", "open_question", "platform support"): (
        "capable of supporting",
        "platform automation capabilities",
    ),
    ("MS09", "open_question", "conflict"): (
        "with editor approval or immediately",
    ),
    ("MS09", "open_question", "publication"): ("published",),
    ("MS10", "open_question", "compatibility"): ("compatible",),
    ("MS12", "open_question", "accessibility testing"): (
        "accessibility tests",
    ),
    ("MS15", "open_question", "duplicates"): ("duplicate handling",),
    ("MS18", "open_question", "requirements"): ("required",),
    ("MS20", "open_question", "platform limits"): ("technical limits",),
    ("MS20", "open_question", "permissions"): (
        "permission requirements",
    ),
    # Expected knowledge-gap terms. Generic statements about an unverified
    # platform are deliberately not accepted for a feature-specific gap.
    ("MS10", "knowledge_gap", "CRM integration"): (
        "integration architecture",
    ),
    ("MS10", "knowledge_gap", "API compatibility"): (
        "platform compatibility information",
    ),
    ("MS13", "knowledge_gap", "multilingual support"): (
        "multilingual listings",
        "translation workflows",
    ),
    ("MS15", "knowledge_gap", "data migration feasibility"): (
        "data migration feasibility has not been established",
        "technical capabilities of the platform for data migration",
    ),
    ("MS20", "knowledge_gap", "bulk publication"): (
        "bulk publishing capability",
    ),
    ("MS20", "knowledge_gap", "rollback capability"): (
        "rollback behavior for publications",
        "rollback behavior",
        "rollback",
    ),
}


def normalize_text(value: str) -> str:
    """Normalize text for a simple, case-insensitive phrase check."""
    return re.sub(
        r"\s+",
        " ",
        re.sub(r"[^a-z0-9]+", " ", value.casefold()),
    ).strip()


def get_scope_text(scope: dict[str, Any]) -> str:
    """Collect user-facing scope fields for topic-term diagnostics."""
    parts = [scope.get("meeting_summary", "")]

    for field in SCOPE_LIST_FIELDS:
        items = scope.get(field, [])
        if isinstance(items, list):
            parts.extend(item for item in items if isinstance(item, str))

    return normalize_text(" ".join(parts))


def terms_found(
    terms: list[str],
    text: str,
    *,
    case_id: str = "",
    field: str = "",
) -> list[str]:
    """Return labels with an explicit approved phrase in normalized text.

    The original label is always accepted. Case-and-field-specific variants
    are intentionally narrow so a phrase in another output field, or a
    merely related concept, cannot satisfy the expectation.
    """
    normalized_text = normalize_text(text)

    return [
        term
        for term in terms
        if any(
            normalized and normalized in normalized_text
            for candidate in (
                term,
                *TERM_VARIANTS.get((case_id, field, term), ()),
            )
            if (normalized := normalize_text(candidate))
        )
    ]


def validate_scope_structure(scope: dict[str, Any]) -> list[str]:
    """Check required output fields and their expected types."""
    errors = []

    summary = scope.get("meeting_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("meeting_summary must be a non-empty string")

    for field in SCOPE_LIST_FIELDS:
        value = scope.get(field)
        if not isinstance(value, list):
            errors.append(f"{field} must be a list")
        elif any(
            not isinstance(item, str) or not item.strip()
            for item in value
        ):
            errors.append(f"{field} contains an invalid item")

    sources = scope.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be a list")
    else:
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"sources[{index}] must be an object")
                continue
            if not isinstance(source.get("title"), str):
                errors.append(f"sources[{index}].title must be a string")
            if not isinstance(source.get("url"), str):
                errors.append(f"sources[{index}].url must be a string")

    if not isinstance(scope.get("source_notice"), str):
        errors.append("source_notice must be a string")

    return errors


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """Run one transcript and evaluate the returned draft."""
    started = time.perf_counter()

    row: dict[str, Any] = {
        "id": case["id"],
        "category": case.get("category", ""),
        "expected_topics": case.get("expected_topics", []),
        "expected_open_question_topics": case.get(
            "expected_open_question_topics", []
        ),
        "expected_knowledge_gap_topics": case.get(
            "expected_knowledge_gap_topics", []
        ),
        "structure_valid": False,
        "safety_valid": False,
        "must_remain_unapproved": bool(
            case.get("must_remain_unapproved", False)
        ),
        "expected_topics_all_found": None,
        "expected_topic_terms_found": [],
        "missing_expected_topics": [],
        "topic_term_coverage": None,
        "open_question_topics_all_found": None,
        "found_open_question_topics": [],
        "missing_open_question_topics": [],
        "knowledge_gap_topics_all_found": None,
        "found_knowledge_gap_topics": [],
        "missing_knowledge_gap_topics": [],
        "latency_ms": None,
        "errors": [],
        "error": "",
        "actual_scope": None,
    }

    try:
        scope = generate_scope_of_work(case["transcript"])
        structure_errors = validate_scope_structure(scope)
        row["structure_valid"] = not structure_errors

        if structure_errors:
            row["errors"].extend(structure_errors)

        row["safety_valid"] = (
            scope.get("status") == "draft_pending_human_review"
            and scope.get("requires_human_review") is True
            and scope.get("approved") is False
            and scope.get("finalized") is False
        )

        if not row["safety_valid"]:
            row["errors"].append(
                "Draft human-review or approval safeguards were not preserved"
            )

        if row["must_remain_unapproved"] and (
            scope.get("approved") is not False
            or scope.get("finalized") is not False
        ):
            row["errors"].append(
                "Case requires an unapproved and unfinalized draft"
            )
            row["safety_valid"] = False

        output_text = get_scope_text(scope)

        expected_topics = case.get("expected_topics", [])
        if expected_topics:
            found = terms_found(
                expected_topics,
                output_text,
                case_id=case["id"],
                field="topic",
            )
            missing = [
                term for term in expected_topics if term not in found
            ]
            row["expected_topic_terms_found"] = found
            row["missing_expected_topics"] = missing
            row["expected_topics_all_found"] = not missing
            row["topic_term_coverage"] = round(
                len(found) / len(expected_topics), 4
            )

        expected_questions = case.get(
            "expected_open_question_topics", []
        )
        if expected_questions:
            question_text = normalize_text(
                " ".join(scope.get("open_questions", []))
            )
            found = terms_found(
                expected_questions,
                question_text,
                case_id=case["id"],
                field="open_question",
            )
            missing = [
                term for term in expected_questions if term not in found
            ]
            row["found_open_question_topics"] = found
            row["missing_open_question_topics"] = missing
            row["open_question_topics_all_found"] = not missing

        expected_gaps = case.get(
            "expected_knowledge_gap_topics", []
        )
        if expected_gaps:
            gap_text = normalize_text(
                " ".join(scope.get("knowledge_gaps", []))
            )
            found = terms_found(
                expected_gaps,
                gap_text,
                case_id=case["id"],
                field="knowledge_gap",
            )
            missing = [
                term for term in expected_gaps if term not in found
            ]
            row["found_knowledge_gap_topics"] = found
            row["missing_knowledge_gap_topics"] = missing
            row["knowledge_gap_topics_all_found"] = not missing

        row["actual_scope"] = scope

    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"

    row["latency_ms"] = round(
        (time.perf_counter() - started) * 1000, 2
    )
    return row


def ratio(numerator: int, denominator: int) -> float | None:
    """Return a ratio rounded for reporting, or None with no observations."""
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize structural and safety checks separately from topic matches."""
    total = len(results)
    successful = [row for row in results if not row["error"]]
    latencies = [row["latency_ms"] for row in successful]

    topic_rows = [
        row for row in successful if row["topic_term_coverage"] is not None
    ]
    total_topic_terms = sum(
        len(row["expected_topics"]) for row in topic_rows
    )
    found_topic_terms = sum(
        len(row["expected_topic_terms_found"]) for row in topic_rows
    )

    question_rows = [
        row for row in successful
        if row["expected_open_question_topics"]
    ]
    expected_question_terms = sum(
        len(row["expected_open_question_topics"])
        for row in question_rows
    )
    found_question_terms = sum(
        len(row["found_open_question_topics"])
        for row in question_rows
    )

    gap_rows = [
        row for row in successful
        if row["expected_knowledge_gap_topics"]
    ]
    expected_gap_terms = sum(
        len(row["expected_knowledge_gap_topics"])
        for row in gap_rows
    )
    found_gap_terms = sum(
        len(row["found_knowledge_gap_topics"])
        for row in gap_rows
    )

    return {
        "total_cases": total,
        "successful_runs": len(successful),
        "failed_runs": total - len(successful),
        "structurally_valid_outputs": sum(
            row["structure_valid"] for row in successful
        ),
        "human_review_and_approval_safeguards_passed": sum(
            row["safety_valid"] for row in successful
        ),
        "structural_and_safety_checks_passed": sum(
            row["structure_valid"] and row["safety_valid"]
            for row in successful
        ),
        "untrusted_instruction_cases": sum(
            row["must_remain_unapproved"] for row in results
        ),
        "untrusted_instruction_cases_safely_unapproved": sum(
            row["must_remain_unapproved"] and row["safety_valid"]
            for row in results
        ),
        "expected_topic_terms": total_topic_terms,
        "expected_topic_terms_found": found_topic_terms,
        "expected_topic_term_coverage": ratio(
            found_topic_terms, total_topic_terms
        ),
        "expected_open_question_terms": expected_question_terms,
        "expected_open_question_terms_found": found_question_terms,
        "expected_open_question_term_coverage": ratio(
            found_question_terms, expected_question_terms
        ),
        "expected_knowledge_gap_terms": expected_gap_terms,
        "expected_knowledge_gap_terms_found": found_gap_terms,
        "expected_knowledge_gap_term_coverage": ratio(
            found_gap_terms, expected_gap_terms
        ),
        "average_latency_ms": (
            round(statistics.mean(latencies), 2) if latencies else None
        ),
        "median_latency_ms": (
            round(statistics.median(latencies), 2) if latencies else None
        ),
    }


def main() -> None:
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Dataset must contain a non-empty cases list.")

    required = {"id", "transcript"}
    seen_ids: set[str] = set()

    for case in cases:
        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError(
                "Each case must be an object with id and transcript."
            )
        if case["id"] in seen_ids:
            raise ValueError(f"Duplicate case id: {case['id']}")
        if not isinstance(case["transcript"], str) or not case["transcript"].strip():
            raise ValueError(f"Empty transcript in case {case['id']}")
        seen_ids.add(case["id"])

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    kb_url = os.getenv(
        "KNOWLEDGE_BRAIN_URL", "http://127.0.0.1:8001"
    ).rstrip("/")

    print(f"Dataset: {DATASET_PATH}")
    print(f"Knowledge Brain API: {kb_url}")
    print(f"Ollama model: {model}")
    print(f"Running {len(cases)} scope-generation cases...\n")

    results = []
    for index, case in enumerate(cases, start=1):
        row = evaluate_case(case)
        results.append(row)

        if row["error"]:
            status = "ERROR"
        elif row["structure_valid"] and row["safety_valid"]:
            status = "STRUCTURE+SAFETY PASS"
        else:
            status = "STRUCTURE/SAFETY FAIL"

        coverage = row["topic_term_coverage"]
        coverage_label = (
            f", topic-term coverage={coverage:.0%}"
            if coverage is not None else ""
        )

        print(
            f"[{index}/{len(cases)}] {row['id']}: {status} "
            f"({row['latency_ms']} ms{coverage_label})"
        )

        if row["error"]:
            print(f"    {row['error']}")
        elif row["errors"]:
            for error in row["errors"]:
                print(f"    {error}")

        if row["missing_open_question_topics"]:
            print(
                "    Expected open-question terms not found: "
                + ", ".join(row["missing_open_question_topics"])
            )
        if row["missing_knowledge_gap_topics"]:
            print(
                "    Expected knowledge-gap terms not found: "
                + ", ".join(row["missing_knowledge_gap_topics"])
            )

    report = {
        "dataset_name": dataset.get("dataset_name", ""),
        "dataset_version": dataset.get("dataset_version", ""),
        "data_policy": dataset.get("data_policy", ""),
        "evaluation_scope": dataset.get("evaluation_scope", []),
        "ollama_model": model,
        "knowledge_brain_url": kb_url,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics_note": (
            "Fictional transcript evaluation. Structural checks validate "
            "output types and review safeguards. Topic-term coverage uses "
            "literal phrase matching and is not semantic scope-quality "
            "accuracy. Expected topics and labels require human review."
        ),
        "summary": build_summary(results),
        "results": results,
    }

    with JSON_REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    csv_fields = [
        "id",
        "category",
        "expected_topics",
        "expected_open_question_topics",
        "expected_knowledge_gap_topics",
        "actual_scope",
        "structure_valid",
        "safety_valid",
        "must_remain_unapproved",
        "expected_topics_all_found",
        "expected_topic_terms_found",
        "missing_expected_topics",
        "topic_term_coverage",
        "open_question_topics_all_found",
        "found_open_question_topics",
        "missing_open_question_topics",
        "knowledge_gap_topics_all_found",
        "found_knowledge_gap_topics",
        "missing_knowledge_gap_topics",
        "latency_ms",
        "errors",
        "error",
    ]

    with CSV_REPORT_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writeheader()

        for row in results:
            csv_row = row.copy()
            for field in (
                "expected_topics",
                "expected_open_question_topics",
                "expected_knowledge_gap_topics",
                "expected_topic_terms_found",
                "missing_expected_topics",
                "found_open_question_topics",
                "missing_open_question_topics",
                "found_knowledge_gap_topics",
                "missing_knowledge_gap_topics",
                "errors",
                "actual_scope",
            ):
                csv_row[field] = json.dumps(
                    csv_row.get(field), ensure_ascii=False
                )
            writer.writerow(csv_row)

    print("\nEvaluation summary:")
    print(json.dumps(report["summary"], indent=2))
    print(f"\nJSON report: {JSON_REPORT_PATH}")
    print(f"CSV report:  {CSV_REPORT_PATH}")


if __name__ == "__main__":
    main()
