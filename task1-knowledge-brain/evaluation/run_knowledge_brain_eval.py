
"""Evaluate Knowledge Brain source retrieval against a JSON test dataset.

This evaluates retrieval and abstention using fictional test articles.
It does not evaluate the factual accuracy of real product documentation.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


EVALUATION_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVALUATION_DIR / "knowledge_brain_cases.json"
JSON_REPORT_PATH = EVALUATION_DIR / "knowledge_brain_eval_results.json"
CSV_REPORT_PATH = EVALUATION_DIR / "knowledge_brain_eval_results.csv"

API_BASE_URL = os.getenv(
    "KNOWLEDGE_BRAIN_URL",
    "http://127.0.0.1:8001",
).rstrip("/")

REQUEST_TIMEOUT_SECONDS = 60


def ask_knowledge_brain(question: str) -> dict:
    """Send one question to the Knowledge Brain /ask endpoint."""
    body = json.dumps({"question": question}).encode("utf-8")

    request = Request(
        f"{API_BASE_URL}/ask",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("The API response was not a JSON object.")

    if not isinstance(payload.get("results"), list):
        raise ValueError(
            "The API response did not contain a 'results' list."
        )

    return payload


def evaluate_case(case: dict) -> dict:
    """Evaluate one dataset case and return its result."""
    expected_urls = case.get("expected_source_urls", [])
    expected_behavior = case.get("expected_behavior", "")
    started = time.perf_counter()

    try:
        payload = ask_knowledge_brain(case["question"])
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        sources = payload["results"]
        actual_urls = [
            source["url"]
            for source in sources
            if isinstance(source, dict) and source.get("url")
        ]

        matched_urls = [
            url for url in expected_urls if url in actual_urls
        ]

        if expected_behavior == "return_no_supported_source":
            passed = len(sources) == 0
            recall = None
        else:
            recall = (
                len(matched_urls) / len(expected_urls)
                if expected_urls
                else None
            )
            # Multi-topic cases pass only when every expected source
            # appears in the retrieved results.
            passed = bool(expected_urls) and len(matched_urls) == len(
                expected_urls
            )

        return {
            "id": case["id"],
            "category": case.get("category", ""),
            "question": case["question"],
            "expected_behavior": expected_behavior,
            "expected_source_urls": expected_urls,
            "actual_source_urls": actual_urls,
            "matched_source_urls": matched_urls,
            "expected_source_count": len(expected_urls),
            "retrieved_source_count": len(actual_urls),
            "source_recall": recall,
            "latency_ms": latency_ms,
            "passed": passed,
            "error": "",
        }

    except (HTTPError, URLError, TimeoutError, OSError, ValueError,
            KeyError, json.JSONDecodeError) as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "id": case.get("id", ""),
            "category": case.get("category", ""),
            "question": case.get("question", ""),
            "expected_behavior": expected_behavior,
            "expected_source_urls": expected_urls,
            "actual_source_urls": [],
            "matched_source_urls": [],
            "expected_source_count": len(expected_urls),
            "retrieved_source_count": 0,
            "source_recall": None,
            "latency_ms": latency_ms,
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def build_summary(results: list[dict]) -> dict:
    """Calculate headline retrieval, abstention, and latency metrics."""
    successful_calls = [row for row in results if not row["error"]]
    passed_count = sum(row["passed"] for row in results)

    supported = [
        row for row in results if row["expected_source_urls"]
    ]
    unsupported = [
        row for row in results if not row["expected_source_urls"]
    ]
    multiple_topic = [
        row for row in supported
        if row["expected_behavior"] == "retrieve_multiple_relevant_sources"
    ]

    supported_passed = sum(row["passed"] for row in supported)
    unsupported_passed = sum(row["passed"] for row in unsupported)
    multiple_topic_passed = sum(row["passed"] for row in multiple_topic)

    latencies = [row["latency_ms"] for row in successful_calls]

    return {
        "total_cases": len(results),
        "api_calls_without_error": len(successful_calls),
        "api_call_errors": len(results) - len(successful_calls),
        "overall_passed_cases": passed_count,
        "overall_case_accuracy": (
            round(passed_count / len(results), 4) if results else None
        ),
        "supported_cases": len(supported),
        "supported_cases_passed": supported_passed,
        "supported_case_accuracy": (
            round(supported_passed / len(supported), 4)
            if supported else None
        ),
        "unsupported_cases": len(unsupported),
        "unsupported_cases_correctly_abstained": unsupported_passed,
        "abstention_accuracy": (
            round(unsupported_passed / len(unsupported), 4)
            if unsupported else None
        ),
        "unsupported_false_positive_count": (
            sum(
                row["retrieved_source_count"] > 0
                for row in unsupported
                if not row["error"]
            )
        ),
        "multiple_topic_cases": len(multiple_topic),
        "multiple_topic_cases_with_all_sources": multiple_topic_passed,
        "average_latency_ms": (
            round(statistics.mean(latencies), 2) if latencies else None
        ),
        "median_latency_ms": (
            round(statistics.median(latencies), 2) if latencies else None
        ),
    }


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("The dataset must contain a non-empty 'cases' list.")

    print(f"API: {API_BASE_URL}")
    print(f"Dataset: {DATASET_PATH}")
    print(f"Running {len(cases)} evaluation cases...\n")

    results = []
    for index, case in enumerate(cases, start=1):
        row = evaluate_case(case)
        results.append(row)

        if row["error"]:
            status = "ERROR"
        else:
            status = "PASS" if row["passed"] else "FAIL"

        print(
            f"[{index}/{len(cases)}] {row['id']}: {status} "
            f"({row['latency_ms']} ms)"
        )
        if row["error"]:
            print(f"    {row['error']}")
        elif row["expected_source_urls"]:
            print(
                f"    Expected URLs found: "
                f"{len(row['matched_source_urls'])}/"
                f"{row['expected_source_count']}"
            )
        else:
            print(
                f"    Sources returned for abstention case: "
                f"{row['retrieved_source_count']}"
            )

    report = {
        "dataset_name": dataset.get("dataset_name", ""),
        "dataset_version": dataset.get("dataset_version", ""),
        "data_policy": dataset.get("data_policy", ""),
        "api_base_url": API_BASE_URL,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics_note": (
            "Retrieval-only evaluation using the provided fictional test "
            "dataset. Results do not establish accuracy against official "
            "product documentation."
        ),
        "summary": build_summary(results),
        "results": results,
    }

    with JSON_REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    csv_fields = [
        "id",
        "category",
        "question",
        "expected_behavior",
        "expected_source_urls",
        "actual_source_urls",
        "matched_source_urls",
        "expected_source_count",
        "retrieved_source_count",
        "source_recall",
        "latency_ms",
        "passed",
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
                "expected_source_urls",
                "actual_source_urls",
                "matched_source_urls",
            ):
                csv_row[field] = json.dumps(
                    csv_row[field], ensure_ascii=False
                )
            writer.writerow(csv_row)

    print("\nEvaluation summary:")
    print(json.dumps(report["summary"], indent=2))
    print(f"\nJSON report: {JSON_REPORT_PATH}")
    print(f"CSV report:  {CSV_REPORT_PATH}")


if __name__ == "__main__":
    main()
