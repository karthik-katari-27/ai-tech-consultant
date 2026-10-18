# Task 2 — Inbox Agent

## Overview

The Inbox Agent is a prototype that analyzes incoming support emails, classifies customer intent, retrieves relevant articles from the Knowledge Brain, and prepares a draft reply for human review.

It uses a locally running Ollama model, so it does not require paid Anthropic API credits.

## Features

- Classifies email intent into account/profile, listing publishing, email notifications, billing, technical issues, and other.
- Summarizes the customer's request and assigns a basic urgency level.
- Searches the Knowledge Brain API for relevant articles.
- Generates a draft reply using retrieved reference material.
- Includes source titles and URLs for reviewer verification.
- Requires human review before a draft is sent.

## Requirements

- Python environment with the Task 1 dependencies installed.
- Ollama installed and running.
- The `qwen2.5:7b` model downloaded.
- The Knowledge Brain API running at `http://127.0.0.1:8000`.

## Configuration

The Inbox Agent supports these environment variables:

| Variable | Default |
|---|---|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | `qwen2.5:7b` |
| `KNOWLEDGE_BRAIN_URL` | `http://127.0.0.1:8000` |

## Workflow

1. Accept an email subject and body.
2. Classify the email using the local model.
3. Search the Knowledge Brain for matching articles.
4. Prepare a draft reply using the available references.
5. Return the classification, draft, and source details for human review.

## Human Review and Safety

The current implementation does not send emails. It returns `sent: false` and `requires_human_review: true`.

The sample articles contain fictional test data, not verified Brilliant Directories support documentation. Drafts must be checked against approved sources before being used for real customers.

## Run the Tests

From the `ai-tech-consultant` repository root, run:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task2-inbox-agent\tests -p "test_inbox_agent.py" -v
```

The Inbox Agent currently has five automated tests. These mock model and API calls, so the test run does not send emails or make live AI requests.

## Current Limitations

- No email-provider integration is implemented.
- Emails must be supplied directly to the Python functions.
- Classification and draft generation depend on local model output.
- Retrieval uses the existing keyword-based Knowledge Brain.
- The workflow has not been evaluated on a representative real-world email dataset.
- Human review remains mandatory.
