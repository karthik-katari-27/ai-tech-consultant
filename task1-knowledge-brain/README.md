# Knowledge Brain API — Local Prototype

This Task 1 project is a small FastAPI Knowledge Brain prototype. It searches a local JSON dataset using simple keyword matching. It does not use AI, embeddings, a database, authentication, or real Brilliant Directories support content.

## Current endpoints

| Endpoint | What it does |
| --- | --- |
| `GET /health` | Returns `{"status": "healthy"}` to show that the API is running. |
| `POST /ask` | Accepts a JSON `question`, searches the local dataset, and returns matching articles with scores. |

`POST /ask` removes leading and trailing spaces from the question. Empty or spaces-only questions return HTTP 400 with `Question must not be empty.` If the local dataset cannot be read or is invalid, the endpoint returns HTTP 503 with a safe message rather than exposing internal file details.

## Local fictional test data

`data/sample_articles.json` contains three fictional articles for development and testing. Every record has `source_type` set to `fictional_test_data` and uses an `example.test` URL.

These articles are **not verified Brilliant Directories support content**. The API repeats that warning in its `source_notice` response field. A search result is a keyword match, not an AI-generated answer or a verified support recommendation.

The current search:

- Converts text to lowercase and removes common stop words.
- Gives title keyword matches more weight than text-only matches.
- Returns up to three results, including each article's source label and numeric score.
- Returns an empty result list when no meaningful keywords match.

## Activate the existing virtual environment

Open PowerShell and move to this folder:

```powershell
Set-Location "C:\Users\LENOVO\Documents\Codex\ai-tech-consultant\task1-knowledge-brain"
```

Activate the existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the environment has not been created yet, create it first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install requirements when needed

For the API only:

```powershell
python -m pip install -r requirements.txt
```

For the API and automated tests:

```powershell
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes the runtime requirements and `httpx`, which FastAPI's test client uses.

## Start the API

Run this while the virtual environment is active:

```powershell
python -m uvicorn main:app --reload
```

The local API is available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Try the endpoints manually

Keep the API running and open a second PowerShell window.

Health check:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Matching fictional-data search:

```powershell
$body = @{ question = "How do I publish a directory listing?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

No-match search:

```powershell
$body = @{ question = "How do I configure airplane navigation?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

Empty-question validation:

```powershell
$body = @{ question = "   " } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
} catch {
    $_.ErrorDetails.Message
}
```

Press `Ctrl+C` in the first PowerShell window when you are finished running the API.

## Automated tests

Run all tests from the Task 1 folder:

```powershell
python -m unittest discover -s tests
```

The latest reported test run had **20 passing automated tests**. The tests cover the API's health, matching, no-match, validation, source-labelling, and unavailable-data behaviors. They also test sitemap XML parsing with in-memory XML strings only. They also test article loading and validation using temporary files and simulated errors.

## Sitemap discovery utility

`inspect_sitemap.py` is separate from the API and test dataset. It is a cautious discovery utility for the configured support sitemap:

- It can identify approved-host candidate URLs and optional `lastmod` values.
- It can report child sitemap URLs when given a sitemap index.
- It does not automatically fetch child sitemaps or individual articles.

It has not been used to fetch real articles for this project. Before running it, verify the site's terms, crawl guidance, approved URL scope, and permission to collect or reuse content.

## Future work

The following are future work, not current features:

- AI-based or semantic retrieval.
- Ingestion of approved real Brilliant Directories support content.
- Stronger citations, attribution, and source metadata in responses.
- Content refresh, change detection, and removal handling.
