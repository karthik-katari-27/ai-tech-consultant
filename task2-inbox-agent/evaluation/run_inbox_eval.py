
"""Evaluate Inbox Agent email classification and urgency predictions."""

from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Make inbox_agent.py importable when this script is run from the repo root.
TASK_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK_DIR))

from inbox_agent import classify_email  # noqa: E402


EVALUATION_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVALUATION_DIR / "inbox_email_cases.json"
JSON_REPORT_PATH = EVALUATION_DIR / "inbox_eval_results.json"
CSV_REPORT_PATH = EVALUATION_DIR / "inbox_eval_results.csv"


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """Classify one fictional email and compare predictions with expected labels."""
    started = time.perf_counter()

    result: dict[str, Any] = {
        "id": case["id"],
        "subject": case["subject"],
        "body": case["body"],
        "expected_category": case["expected_category"],
        "expected_urgency": case["expected_urgency"],
        "predicted_category": None,
        "predicted_summary": None,
        "predicted_urgency": None,
        "category_correct": False,
        "urgency_correct": False,
        "both_correct": False,
        "latency_ms": None,
        "error": "",
    }

    try:
        prediction = classify_email(case["subject"], case["body"])
        result["predicted_category"] = prediction["category"]
        result["predicted_summary"] = prediction["summary"]
        result["predicted_urgency"] = prediction["urgency"]

        result["category_correct"] = (
            prediction["category"] == case["expected_category"]
        )
        result["urgency_correct"] = (
            prediction["urgency"] == case["expected_urgency"]
        )
        result["both_correct"] = (
            result["category_correct"] and result["urgency_correct"]
        )

    except Exception as exc:
        # Keep the evaluation running if an individual model call fails.
        result["error"] = f"{type(exc).__name__}: {exc}"

    result["latency_ms"] = round(
        (time.perf_counter() - started) * 1000, 2
    )
    return result


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate aggregate metrics, counting failed calls as incorrect."""
    total = len(results)
    successful = [row for row in results if not row["error"]]
    latencies = [row["latency_ms"] for row in successful]

    category_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0}
    )

    confusion: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for row in results:
        expected = row["expected_category"]
        category_counts[expected]["total"] += 1

        if row["category_correct"]:
            category_counts[expected]["correct"] += 1

        predicted = row["predicted_category"] or "ERROR"
        confusion[expected][predicted] += 1

    category_accuracy = (
        sum(row["category_correct"] for row in results) / total
        if total else None
    )
    urgency_accuracy = (
        sum(row["urgency_correct"] for row in results) / total
        if total else None
    )
    exact_accuracy = (
        sum(row["both_correct"] for row in results) / total
        if total else None
    )

    return {
        "total_cases": total,
        "successful_model_calls": len(successful),
        "failed_model_calls": total - len(successful),
        "category_correct_count": sum(
            row["category_correct"] for row in results
        ),
        "category_accuracy": (
            round(category_accuracy, 4)
            if category_accuracy is not None else None
        ),
        "urgency_correct_count": sum(
            row["urgency_correct"] for row in results
        ),
        "urgency_accuracy": (
            round(urgency_accuracy, 4)
            if urgency_accuracy is not None else None
        ),
        "category_and_urgency_both_correct": sum(
            row["both_correct"] for row in results
        ),
        "exact_case_accuracy": (
            round(exact_accuracy, 4)
            if exact_accuracy is not None else None
        ),
        "accuracy_by_expected_category": {
            category: {
                "total": counts["total"],
                "correct": counts["correct"],
                "accuracy": round(
                    counts["correct"] / counts["total"], 4
                ),
            }
            for category, counts in sorted(category_counts.items())
        },
        "category_confusion_matrix": {
            category: dict(sorted(predictions.items()))
            for category, predictions in sorted(confusion.items())
        },
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
        raise ValueError("Dataset must contain a non-empty 'cases' list.")

    required_fields = {
        "id",
        "subject",
        "body",
        "expected_category",
        "expected_urgency",
    }
    seen_ids: set[str] = set()

    for case in cases:
        if not isinstance(case, dict) or not required_fields.issubset(case):
            raise ValueError(
                "Each case must include id, subject, body, "
                "expected_category, and expected_urgency."
            )
        if case["id"] in seen_ids:
            raise ValueError(f"Duplicate case id: {case['id']}")
        seen_ids.add(case["id"])

    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    print(f"Dataset: {DATASET_PATH}")
    print(f"Ollama host: {host}")
    print(f"Model: {model}")
    print(f"Running {len(cases)} classification cases...\n")

    results = []

    for index, case in enumerate(cases, start=1):
        row = evaluate_case(case)
        results.append(row)

        if row["error"]:
            status = "ERROR"
        elif row["both_correct"]:
            status = "PASS"
        else:
            status = "FAIL"

        print(
            f"[{index}/{len(cases)}] {row['id']}: {status} "
            f"(category={row['predicted_category']}, "
            f"urgency={row['predicted_urgency']}, "
            f"{row['latency_ms']} ms)"
        )

        if row["error"]:
            print(f"    Error: {row['error']}")
        else:
            print(
                f"    Expected: category={row['expected_category']}, "
                f"urgency={row['expected_urgency']}"
            )

    report = {
        "dataset_name": dataset.get("dataset_name", ""),
        "dataset_version": dataset.get("dataset_version", ""),
        "data_policy": dataset.get("data_policy", ""),
        "evaluation_scope": dataset.get("evaluation_scope", []),
        "model": model,
        "ollama_host": host,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics_note": (
            "Fictional email benchmark. Accuracy is measured against the "
            "dataset's expected labels, which should be reviewed by a human. "
            "This run evaluates classification and urgency only, not draft "
            "reply quality, Knowledge Brain retrieval, or email sending."
        ),
        "summary": build_summary(results),
        "results": results,
    }

    with JSON_REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    fields = [
        "id",
        "subject",
        "body",
        "expected_category",
        "predicted_category",
        "category_correct",
        "expected_urgency",
        "predicted_urgency",
        "urgency_correct",
        "both_correct",
        "predicted_summary",
        "latency_ms",
        "error",
    ]

    with CSV_REPORT_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("\nEvaluation summary:")
    print(json.dumps(report["summary"], indent=2))
    print(f"\nJSON report: {JSON_REPORT_PATH}")
    print(f"CSV report:  {CSV_REPORT_PATH}")


if __name__ == "__main__":
    main()