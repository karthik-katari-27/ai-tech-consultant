# Task 3 — Meeting-to-Scope of Work

## Overview

The Meeting-to-Scope of Work prototype converts a meeting transcript into a structured draft scope of work using a locally running Ollama model.

It searches the Knowledge Brain for potentially relevant reference articles and asks the model to organize the transcript into requirements, deliverables, scope boundaries, assumptions, dependencies, risks, and open questions.

The generated document is a draft and must be reviewed by a human before it is approved or shared.

## Features

- Accepts a meeting transcript as a Python string.
- Searches the Knowledge Brain API for matching reference articles.
- Generates a structured scope of work using a local Ollama model.
- Identifies customer goals and requirements.
- Lists proposed deliverables and in-scope items.
- Records out-of-scope items, assumptions, and dependencies.
- Highlights risks, open questions, and knowledge gaps.
- Preserves source titles, URLs, and source types.
- Validates the structure of the model-generated JSON.
- Marks the result as pending human review.

## Requirements

- Python environment with the Task 1 dependencies installed.
- Ollama installed and running.
- The `qwen2.5:7b` model downloaded.
- The Knowledge Brain API running at `http://127.0.0.1:8000`.

## Configuration

The prototype supports the following environment variables:

| Variable | Default |
|---|---|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | `qwen2.5:7b` |
| `KNOWLEDGE_BRAIN_URL` | `http://127.0.0.1:8000` |

## Scope Output

The `generate_scope_of_work(transcript)` function returns a dictionary containing:

- `meeting_summary`
- `customer_goals`
- `requirements`
- `deliverables`
- `in_scope`
- `out_of_scope`
- `assumptions`
- `dependencies`
- `risks`
- `open_questions`
- `knowledge_gaps`
- `sources`
- `source_notice`

The output also includes workflow status fields indicating that human review is required and the draft has not been approved or finalized.

## Run the Prototype

Start Ollama with the configured model available:

```powershell
ollama run qwen2.5:7b
```

Start the Knowledge Brain API in a separate terminal from the `task1-knowledge-brain` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

In another PowerShell terminal, navigate to the Task 3 directory:

```powershell
Set-Location "C:\Users\LENOVO\Documents\Codex\ai-tech-consultant\task3-meeting-to-scope"
```

Start the Python interpreter using the Task 1 virtual environment:

```powershell
& "..\task1-knowledge-brain\.venv\Scripts\python.exe"
```

At the Python prompt, call the function with a sample transcript:

```python
from meeting_to_scope import generate_scope_of_work

transcript = """
Customer: We need a website where members can publish directory listings.
Customer: We need to confirm who will provide the listing details.
Consultant: The requirements and project timeline still need clarification.
"""

draft = generate_scope_of_work(transcript)
print(draft)
```

The Knowledge Brain API and Ollama must be available for this live workflow.

## Run the Tests

From the `ai-tech-consultant` repository root, run:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task3-meeting-to-scope\tests -p "test_meeting_to_scope.py" -v
```

The current Task 3 test file contains five automated tests. They mock Knowledge Brain and model responses, so the tests do not make live AI requests.

## Human Review and Safety

The prototype does not approve, finalize, or send a proposal. It returns a draft marked as pending human review.

Meeting transcripts and reference articles are treated as untrusted input. The model is instructed not to invent prices, dates, technical capabilities, or customer commitments. Missing information should be recorded as open questions or knowledge gaps.

The sample Knowledge Brain articles are fictional test data, not verified Brilliant Directories support documentation. They must not be represented as authoritative product guidance.

## Current Limitations

- The prototype is a Python function, not a standalone HTTP API or web application.
- It has no meeting-platform integration.
- It uses the existing keyword-based Knowledge Brain for retrieval.
- It depends on a locally running Ollama model.
- It has not been evaluated on a representative collection of real meeting transcripts.
- Generated requirements, assumptions, risks, and deliverables require human verification.
- No production deployment, authentication, or authorization has been implemented.