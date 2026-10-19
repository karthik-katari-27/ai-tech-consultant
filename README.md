# AI Tech Consultant

A three-part AI-assisted support and consulting prototype built with Python, FastAPI, Ollama, and automated tests.

**Important:** Sample knowledge articles contain fictional test data, not verified Brilliant Directories documentation. The prototypes are not production-ready. Customer-facing outputs require human review.

## Projects

- **Task 1 — Knowledge Brain:** Retrieves relevant articles from a local JSON dataset and supports AI-assisted answers with source references. Includes Claude API and local Qwen2.5 7B integrations.
- **Task 2 — Inbox Agent:** Classifies customer emails, retrieves relevant knowledge, and drafts replies for human review. No email-provider integration or automatic sending is implemented.
- **Task 3 — Meeting-to-Scope of Work:** Converts meeting transcripts into structured draft scopes, including requirements, deliverables, assumptions, risks, and open questions. Human approval remains required.

## Requirements and Setup

Requirements: Python 3.10+, the dependencies in `task1-knowledge-brain/requirements.txt`, and Ollama with `qwen2.5:7b` for local AI workflows. Live Claude requests require an Anthropic API key and available API credits.

Run the following commands from the repository root in Windows PowerShell:

```powershell
py -m venv task1-knowledge-brain\.venv
.\task1-knowledge-brain\.venv\Scripts\python.exe -m pip install -r .\task1-knowledge-brain\requirements.txt
ollama pull qwen2.5:7b
Set-Location .\task1-knowledge-brain
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The Knowledge Brain API is available at `http://127.0.0.1:8000`; interactive API documentation is at `/docs`.

## Automated Tests

Run from the repository root:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task1-knowledge-brain\tests -v
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task2-inbox-agent\tests -p test_inbox_agent.py -v
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task3-meeting-to-scope\tests -p test_meeting_to_scope.py -v
```

**Latest recorded test results:** Task 1 passed 46 tests on October 19, 2026; Task 2 passed 6 tests on October 19, 2026; Task 3 previously passed 10 tests on October 18, 2026. These are separate test runs, not one combined test run. Task 3 should be rerun to reconfirm its current status.


## Knowledge Brain Retrieval Evaluation

The 20-case evaluation using fictional test articles passed **20/20 cases (100%)** in the latest recorded run. All 16 supported retrieval cases passed, all 4 unsupported questions correctly returned no sources, and both multi-topic cases retrieved every expected source.

Observed response times in that run were 20.26 ms average and 15.52 ms median. These measurements describe one local run, not production performance.

Dataset: `task1-knowledge-brain/evaluation/knowledge_brain_cases.json`

Reports: `task1-knowledge-brain/evaluation/knowledge_brain_eval_results.json` and `knowledge_brain_eval_results.csv`.

These results do not establish accuracy on real support-center content.


## Inbox Agent Classification Evaluation

A 50-case fictional email benchmark using Qwen2.5 7B achieved 100% category accuracy (50/50), 80% urgency accuracy (40/50), and 80% exact-case accuracy (40/50) in the latest recorded run. All model calls succeeded. Average classification time was 8.80 seconds and median time was 7.24 seconds. Results are from a hand-authored dataset used during prompt tuning; real-world accuracy has not been established. See `task2-inbox-agent/README.md` and `EVALS.md` for details.


## Limitations and Safety

- Retrieval uses keyword matching with selected token normalization and a minimum score threshold.
- The Inbox Agent and Meeting-to-Scope modules are not standalone applications.
- Representative real-world accuracy and comprehensive live integration reliability have not been established.
- Protect API keys and other secrets; do not commit them to Git.
- Obtain appropriate permissions before collecting or reusing third-party content.

See `DESIGN.md`, `EVALS.md`, and `AI_LOG.md` for architecture, evaluation details, and the AI-assisted development record.