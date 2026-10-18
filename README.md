# AI Tech Consultant

A three-part AI-assisted support and consulting prototype built with Python, FastAPI, Ollama, and automated tests.

The project explores three workflows: retrieving support knowledge, drafting replies to customer emails, and preparing draft scopes of work from meeting transcripts.

**Important:** The current sample knowledge articles contain fictional test data. The prototypes are not production-ready and require human review of customer-facing outputs.

## Projects

### Task 1 — Knowledge Brain

Searches a local JSON dataset for relevant articles and provides source references.

Features:
- FastAPI endpoints for health checks, article search, and AI-assisted answers.
- Local article loading and validation.
- Keyword-based article retrieval.
- Claude API integration.
- Local Qwen2.5 7B integration through Ollama.
- Automated API and service tests.

Main endpoints:
- `GET /health`
- `POST /ask`
- `POST /ask-claude`
- `POST /ask-local`

Claude requests require an Anthropic API key and available API credits. The local endpoint uses Ollama and does not require Anthropic API credits.

### Task 2 — Inbox Agent

Prepares customer-email reply drafts for human review.

Features:
- Classifies email intent and summarizes the request.
- Assigns a basic urgency level.
- Searches the Knowledge Brain for relevant articles.
- Generates a draft reply using retrieved references.
- Includes source details for reviewer verification.
- Explicitly marks the draft as requiring human review.

The current implementation is a Python module, not a standalone email application. It does not connect to an email provider or send messages automatically.

### Task 3 — Meeting-to-Scope of Work

Converts a meeting transcript into a structured draft scope of work.

The draft can include:
- Meeting summary and customer goals.
- Requirements and deliverables.
- In-scope and out-of-scope items.
- Assumptions and dependencies.
- Risks and open questions.
- Knowledge gaps and reference sources.

The output remains a draft pending human review. The current implementation is a Python module, not a standalone web application.

## Repository structure

```text
ai-tech-consultant/
├── shared-docs/
├── task1-knowledge-brain/
│   ├── data/
│   ├── tests/
│   ├── main.py
│   ├── search_articles.py
│   ├── claude_service.py
│   ├── local_ai_service.py
│   ├── requirements.txt
│   └── README.md
├── task2-inbox-agent/
│   ├── tests/
│   ├── inbox_agent.py
│   └── README.md
├── task3-meeting-to-scope/
│   ├── tests/
│   ├── meeting_to_scope.py
│   └── README.md
├── AI_LOG.md
├── DESIGN.md
├── EVALS.md
└── README.md
```

## Requirements

- Python 3.10 or later.
- The Python dependencies listed in `task1-knowledge-brain/requirements.txt`.
- Ollama and the `qwen2.5:7b` model for live local-AI workflows.
- An Anthropic API key and available API credits for live Claude requests.

The Python environment used in the development workflow is located under `task1-knowledge-brain/.venv`.

## Setup

Run the following commands from the repository root in Windows PowerShell.

### 1. Install Python dependencies

```powershell
py -m venv task1-knowledge-brain\.venv
.\task1-knowledge-brain\.venv\Scripts\python.exe -m pip install -r .\task1-knowledge-brain\requirements.txt
```

If the virtual environment already exists, you can reuse it.

### 2. Install the local model

Install Ollama for Windows from [ollama.com/download/windows](https://ollama.com/download/windows).

Download Qwen2.5 7B:

```powershell
ollama pull qwen2.5:7b
```

If PowerShell does not recognize the `ollama` command, try the standard per-user installation path:

```powershell
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
& $ollama pull qwen2.5:7b
& $ollama list
```

Keep Ollama running when using the live local-AI workflows.

### 3. Start the Knowledge Brain API

From the repository root:

```powershell
Set-Location .\task1-knowledge-brain
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Example: Ask the local model

With Ollama and the Knowledge Brain API running, open a second PowerShell terminal in the repository root and run:

```powershell
$body = @{
    question = "How do I publish a directory listing?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/ask-local" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

The sample response uses fictional reference material. It must not be treated as verified product guidance.

## Run the automated tests

Run each task's tests separately from the repository root.

### Task 1 — Knowledge Brain

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task1-knowledge-brain\tests -v
```

### Task 2 — Inbox Agent

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task2-inbox-agent\tests -p test_inbox_agent.py -v
```

### Task 3 — Meeting-to-Scope of Work

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task3-meeting-to-scope\tests -p test_meeting_to_scope.py -v
```

At the latest reported test run, the three suites passed separately:
- Task 1: 41 tests passed.
- Task 2: 5 tests passed.
- Task 3: 10 tests passed.
- **Total: 56 tests passed across three separate test runs.**

These are automated test results, primarily using mocked responses. They do not establish the accuracy of AI-generated results on real customer data or prove that all live integrations work end to end.

## Configuration and security

- Keep API keys, passwords, tokens, and other secrets out of source code and Git history.
- Configure `ANTHROPIC_API_KEY` through the runtime environment when live Claude access is needed.
- The local model defaults to `qwen2.5:7b`.
- The local AI services use Ollama's API at `http://127.0.0.1:11434` by default.
- The Inbox Agent and Meeting-to-Scope workflows require human review.
- Do not send customer-facing emails or finalize proposals automatically.
- Obtain the appropriate permissions before collecting or reusing third-party support content.

## Limitations and future work

- The sample articles are fictional test records and are not verified Brilliant Directories support documentation.
- Retrieval currently uses keyword-based matching rather than a production-grade semantic retrieval system.
- The Inbox Agent does not yet integrate with an email provider.
- Meeting-to-Scope does not yet integrate with a meeting platform.
- The Task 2 and Task 3 modules have mocked tests but have not been evaluated on representative real-world datasets.
- Authentication, authorization, production deployment, monitoring, and comprehensive live integration testing remain future work.

See `DESIGN.md`, `EVALS.md`, and `AI_LOG.md` for the design, evaluation plan, and AI-assisted development record.