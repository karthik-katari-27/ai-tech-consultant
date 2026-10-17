# AI Tech Consultant Capstone

This beginner-friendly capstone explores practical workflows for a technology consultant: organizing knowledge, handling incoming requests, and turning meeting notes into clear project scope.

## Project tasks

1. **Knowledge Brain** (`task1-knowledge-brain`) — a local FastAPI prototype that searches a small JSON dataset.
2. **Inbox Agent** (`task2-inbox-agent`) — planned work for sorting incoming messages and identifying items that need attention.
3. **Meeting to Scope** (`task3-meeting-to-scope`) — planned work for turning meeting notes into goals, requirements, and next steps.

Use `shared-docs` for materials useful across more than one task.

## Current Task 1 status

Task 1 currently provides a local-only Knowledge Brain prototype:

- `GET /health` returns `{"status": "healthy"}` when the API is running.
- `POST /ask` accepts a JSON `question` and performs simple keyword matching against a local JSON file.
- Matching words in an article title receive more weight than matches found only in article text.
- Blank or spaces-only questions return HTTP 400.
- If the local article file is unavailable or invalid, `/ask` returns a safe HTTP 503 message without exposing filesystem details.

The current dataset contains **fictional test articles only**. Results are labelled `fictional_test_data` and are **not verified Brilliant Directories support content**.

The Task 1 test suite covers API behavior, sitemap XML parsing, and article loading and validation. The latest reported test run had **20 passing automated tests**.

## Running Task 1 on Windows

Open PowerShell and move into the Task 1 folder:

```powershell
Set-Location "C:\Users\LENOVO\Documents\Codex\ai-tech-consultant\task1-knowledge-brain"
```

Activate the existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If packages need to be installed or refreshed, use the appropriate requirements file:

```powershell
# Runtime API packages
python -m pip install -r requirements.txt

# Runtime packages plus the automated-test dependency
python -m pip install -r requirements-dev.txt
```

Start the local API:

```powershell
python -m uvicorn main:app --reload
```

Run all automated tests:

```powershell
python -m unittest discover -s tests
```

## Sitemap discovery utility

`task1-knowledge-brain/inspect_sitemap.py` is a separate, read-only discovery utility. When deliberately run, it can inspect the configured sitemap and save approved-host candidate URLs or child sitemap URLs. It does not automatically download child sitemaps or individual articles.

It has not been used to fetch real articles for this project. A sitemap is a discovery tool, not permission to collect or reuse content.

## Future work

The following are not implemented yet:

- AI-based or semantic retrieval.
- Ingestion of approved real support content.
- Stronger source citations and attribution in search responses.
- Content refresh, change detection, and removal handling.
