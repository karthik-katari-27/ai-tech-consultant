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

## Knowledge Brain — Setup and Usage

### Overview

Knowledge Brain is a FastAPI application that searches a local article dataset and provides AI-generated answers using either Anthropic's Claude API or a locally running model through Ollama.

The sample dataset contains **fictional test articles**. It is not verified Brilliant Directories support documentation.

### Features

- `GET /health` — checks whether the API is running.
- `POST /ask` — searches local articles using keyword matching.
- `POST /ask-claude` — retrieves matching articles and passes them to Claude for a grounded answer.
- `POST /ask-local` — retrieves matching articles and uses a local Ollama model to generate an answer.
- Source details are returned with AI-generated answers.
- Automated tests use mocked AI clients and do not require live API access.

### Requirements

- Python 3.10 or later
- Windows PowerShell (commands below use Windows syntax)
- Ollama for local AI responses
- An Anthropic API key with available credits for live Claude API requests (optional)

### 1. Set up the Python environment

Open PowerShell and navigate to the project directory:

```powershell
Set-Location "C:\Users\LENOVO\Documents\Codex\ai-tech-consultant\task1-knowledge-brain"
```

Create a virtual environment if you do not already have one:

```powershell
py -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Run the local AI model

Install Ollama from [ollama.com/download/windows](https://ollama.com/download/windows).

Download the Qwen2.5 7B model:

```powershell
ollama pull qwen2.5:7b
```

If PowerShell cannot find the `ollama` command, open a new terminal or use the executable directly:

```powershell
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
& $ollama pull qwen2.5:7b
```

Check the installed models:

```powershell
& $ollama list
```

Ollama must be running for `/ask-local` to work. The default model is `qwen2.5:7b`; you can override it by setting the `OLLAMA_MODEL` environment variable. The default local API address is `http://127.0.0.1:11434`, configurable with `OLLAMA_HOST`.

### 3. Start the FastAPI application

From the `task1-knowledge-brain` directory, run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Keep the terminal running while using the API.

Open the interactive API documentation in your browser:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Test the endpoints

The examples below use PowerShell.

**Health check**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

**Search local articles**

```powershell
$body = @{
    question = "How do I publish a directory listing?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/ask" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Get an answer from the local model**

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

**Get an answer from Claude (optional)**

The Claude endpoint requires `ANTHROPIC_API_KEY` to be set in the server's environment and an Anthropic account with available API credits.

To enter the key without displaying it as you type, use the following in the PowerShell terminal that will start the server:

```powershell
$secureKey = Read-Host "Anthropic API key" -AsSecureString
$env:ANTHROPIC_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
Remove-Variable secureKey
```

Then send a request to `http://127.0.0.1:8000/ask-claude` using the same request body shown above. Do not store API keys in source files or commit them to Git.

### 5. Run the automated tests

From the `task1-knowledge-brain` directory, run the complete test suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The current test suite contains **41 tests**. The AI service tests use mocks, so the test run does not require a real Anthropic API key or live AI requests.

### Article data

The fictional sample articles are stored in:

`data/sample_articles.json`

The keyword search implementation is in `search_articles.py`. Claude integration is in `claude_service.py`, and the local Ollama integration is in `local_ai_service.py`.

### Important limitations

- The sample articles are fictional test data, not verified product support documentation.
- AI-generated answers should be checked before being treated as authoritative.
- `/ask-claude` requires usable Anthropic API credits.
- `/ask-local` requires Ollama to be running with the configured model installed.
- Successful mocked tests do not guarantee that an external service will be available or that live credentials and billing are configured.