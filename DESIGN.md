# AI Tech Consultant — System Design

## 1. Project Overview

AI Tech Consultant is a three-part AI-assisted support and consulting prototype.

The project contains three workflows:

1. **Task 1 — Knowledge Brain:** Searches a local article dataset and returns relevant information with source references.
2. **Task 2 — Inbox Agent:** Classifies customer emails, retrieves relevant knowledge, and prepares draft replies for human review.
3. **Task 3 — Meeting-to-Scope of Work:** Analyzes meeting transcripts and prepares structured draft scopes of work for human review.

The prototypes use Python and a local Ollama model for AI-assisted workflows. Task 1 also includes an optional integration with the Anthropic Claude API.

Human review remains mandatory for customer-facing replies and scopes of work.

## 2. Current Implementation Status

All three tasks have initial working prototypes and automated tests.

### Task 1 — Knowledge Brain

Implemented components:

- FastAPI application with `GET /health` and `POST /ask`.
- Local JSON article loading and validation.
- Keyword-based article search with higher scores for title matches.
- Generic errors for unavailable or invalid article data.
- Sitemap XML inspection and parsing utilities.
- Claude integration through `POST /ask-claude`.
- Local Ollama integration through `POST /ask-local`.
- Automated API, article-loader, sitemap, and local-AI service tests.

The latest Task 1 test run on October 19, 2026, passed 46 tests, including regression tests for supported paraphrases, unsupported questions, and multiple-topic retrieval.

### Task 2 — Inbox Agent

Implemented components:

- Email subject and body validation.
- Email classification into configured categories.
- Summary and basic urgency classification.
- Knowledge Brain article retrieval.
- Draft reply generation using Ollama.
- Source references for human reviewers.
- Explicit draft status and human-review fields.
- Automated tests using mocked responses.

The latest dedicated test run passed six tests on October 19, 2026, including regression coverage for Markdown-fenced JSON classification responses.

The prototype does not connect to an email provider and does not send emails automatically.

### Task 3 — Meeting-to-Scope of Work

Implemented components:

- Meeting transcript validation.
- Knowledge Brain article retrieval.
- Structured scope generation using Ollama.
- Extraction of customer goals, requirements, and deliverables.
- In-scope and out-of-scope items.
- Assumptions, dependencies, and risks.
- Open questions and knowledge gaps.
- Source references and source notices.
- Validation of the model-generated JSON structure.
- Explicit human-review and approval-status fields.
- Automated tests using mocked responses.

The latest reported dedicated test run passed ten tests.

The prototype is a Python module, not a standalone HTTP API or meeting-platform integration.


### Verification Summary

The latest recorded automated test results are:


| Project | Tests passed | Verification status |
|---|---:|---|
| Knowledge Brain | 46 | Latest verified run on October 19, 2026 |
| Inbox Agent | 6 | Latest verified run on October 19, 2026 |
| Meeting-to-Scope of Work | 10 | Previously reported run on October 18, 2026 |
| **Total** | **62** | **Results from three separate test runs** |



The Task 1 and Task 2 counts were verified on October 19, 2026. The Task 3 count was previously reported on October 18, 2026, and should be reconfirmed.

Task 2 and Task 3 unit tests use mocked model and API responses. Separate manual live tests using fictional data have also been performed, but those examples do not establish representative real-world accuracy or production reliability.



## 3. Technology and Repository Structure

The project uses:

- Python
- FastAPI for the Knowledge Brain HTTP API
- Local JSON files for article storage
- Ollama with the `qwen2.5:7b` model
- The Anthropic API for optional Claude-based answers
- Python's `unittest` framework for automated tests

Current repository structure:

```text
ai-tech-consultant/
├── shared-docs/
├── task1-knowledge-brain/
│   ├── data/
│   ├── evaluation/
│   │   ├── knowledge_brain_cases.json
│   │   ├── run_knowledge_brain_eval.py
│   │   ├── knowledge_brain_eval_results.json
│   │   └── knowledge_brain_eval_results.csv
│   ├── tests/
│   ├── main.py
│   ├── search_articles.py
│   ├── inspect_sitemap.py
│   ├── claude_service.py
│   ├── local_ai_service.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
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

## 4. Task 1 Architecture — Knowledge Brain

### Request flow


1. A client sends a question to the FastAPI application.
2. The API validates the input.
3. The search module loads and validates the local JSON dataset.
4. Keyword search tokenizes the query, removes configured stop words, and normalizes selected word variations.
5. Each matching title keyword contributes three points; each matching article-text keyword that did not match the title contributes one point.
6. Articles scoring below two points are excluded. The remaining matches are ranked by score, with up to three results returned by default.
7. Results include source metadata and the fictional-data source label.


### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check whether the API is responding |
| POST | `/ask` | Search the local article dataset |
| POST | `/ask-claude` | Generate an answer using the Claude service |
| POST | `/ask-local` | Generate an answer using Ollama |

The `/ask` endpoint performs keyword-based retrieval. The AI answer endpoints use retrieved articles as reference material.

The Claude endpoint requires appropriate API configuration and available Anthropic API credits. The local endpoint uses the configured Ollama host and model.

### Article data model

Each article record uses five required fields:

| Field | Purpose |
|---|---|
| `id` | Unique article identifier |
| `title` | Article title |
| `url` | Source or reference URL |
| `text` | Article content |
| `source_type` | Identifies the source-data type |

The current sample dataset contains fictional test articles using `example.test` URLs and the `fictional_test_data` source label.

### Sitemap utility

The sitemap utility is separate from the question-answering API. Its tests cover ordinary sitemap URL lists, sitemap indexes, and malformed XML.

Sitemap discovery does not establish permission to download, store, or reuse article content. Real-content ingestion has not been established as part of the current implementation.

## 5. Task 2 Architecture — Inbox Agent

The Inbox Agent is implemented in `task2-inbox-agent/inbox_agent.py`.

### Workflow

1. Accept an email subject and body.
2. Validate that the email contains usable text.
3. Ask the local model to classify the email and summarize its intent.
4. Validate the classification result and use an allowed category and urgency value.
5. Submit the email content to the Knowledge Brain `/ask` endpoint.
6. Retain up to three well-formed article results.
7. Generate a reply draft grounded in the retrieved reference material.
8. Return the classification, draft, source details, and human-review status.

### Current categories

The configured categories are:

- `account_profile`
- `listing_publishing`
- `email_notifications`
- `billing`
- `technical_issue`
- `other`

The urgency field uses `low`, `normal`, or `high`.

These classifications are model-generated and have not been evaluated on a representative real-world email dataset.

### Output and review

The returned result includes:

- Email subject
- Classification and summary
- Draft reply
- Source references
- Source notice
- `requires_human_review`
- `sent`

The prototype marks the result as pending review and sets `sent` to `false`.

There is no email-provider integration or automatic message-sending implementation.

## 6. Task 3 Architecture — Meeting-to-Scope of Work

The workflow is implemented in `task3-meeting-to-scope/meeting_to_scope.py`.

### Workflow

1. Accept and validate a meeting transcript.
2. Submit the transcript to the Knowledge Brain `/ask` endpoint.
3. Retain up to five well-formed article results.
4. Ask the local model to produce a structured JSON scope draft.
5. Validate the JSON object and the expected list fields.
6. Return the structured draft with available sources and review status.

### Scope fields

The draft includes:

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

The output also includes source details, a source notice, `requires_human_review`, `approved`, and `finalized` fields.

### Grounding and uncertainty

The prompt instructs the model not to invent prices, dates, technical capabilities, or customer commitments.

Missing information should be recorded as an open question or knowledge gap rather than treated as an agreed requirement.

The returned status marks the scope as a draft pending human review. The prototype does not approve, finalize, or send a proposal.

## 7. Testing Strategy

Each project's tests are run separately.

### Task 1

Run from the `task1-knowledge-brain` directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The latest reported run on October 19, 2026, passed 46 tests.

### Task 2

Run from the repository root:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task2-inbox-agent\tests -p test_inbox_agent.py -v
```

The latest reported dedicated run passed six tests on October 19, 2026.

### Task 3

Run from the repository root:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task3-meeting-to-scope\tests -p test_meeting_to_scope.py -v
```

The latest reported dedicated run passed ten tests.


### Task 1 — Retrieval evaluation

A separate 20-case evaluation was run on October 19, 2026, against the Knowledge Brain `/ask` endpoint at `http://127.0.0.1:8001`.

From the repository root, run the evaluation with the API already running:

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe .\task1-knowledge-brain\evaluation\run_knowledge_brain_eval.py
```

The latest recorded run passed 20/20 cases. All 16 supported retrieval cases passed, all four unsupported questions returned no sources, and both multi-topic cases retrieved every expected source. The measured average response time was 20.26 ms, with a median of 15.52 ms.

The evaluation dataset and generated JSON and CSV reports are stored in `task1-knowledge-brain/evaluation/`. The dataset uses fictional `example.test` articles and does not establish accuracy on verified support documentation or generated-answer factuality.



### Task 2 — Classification evaluation

A 50-case fictional email benchmark was run on October 19, 2026, using the local Ollama model `qwen2.5:7b`.

The latest recorded results were:

| Metric | Result |
|---|---:|
| Email cases | 50 |
| Successful model calls | 50/50 |
| Category accuracy | 50/50 (100%) |
| Urgency accuracy | 40/50 (80%) |
| Category and urgency both correct | 40/50 (80%) |
| Average classification latency | 8,797.94 ms |
| Median classification latency | 7,236.28 ms |

The benchmark and generated JSON/CSV reports are stored in `task2-inbox-agent/evaluation/`. The evaluation is reproducible using `run_inbox_eval.py` with Ollama running.

The classifier was updated to accept valid JSON surrounded by Markdown code fences after this format caused classification parsing errors. A regression test covers that format.

The latest results are based on a hand-authored fictional dataset used during prompt tuning. The urgency labels have not been independently validated, and the results do not establish accuracy on unseen or real customer emails.


### Testing limitations

The reported combined total of 51 passing tests represents separate test runs, not a single combined discovery run.

The automated Task 2 and Task 3 tests use mocked model and Knowledge Brain responses. Separate manual live tests were also completed for both workflows using fictional data with Ollama and the Knowledge Brain API. These tests demonstrate that the workflows can run end to end for the tested examples; they do not establish representative real-world accuracy or production reliability.

Task 1's local AI endpoint has had a live test with fictional reference material. The Inbox Agent and Meeting-to-Scope workflows still require live end-to-end verification.

## 8. Security, Permissions, and Human Oversight

The project follows these design principles:

- Keep credentials and environment-specific secrets out of source control.
- Return generic API errors rather than exposing internal file paths or stack traces.
- Treat incoming emails, meeting transcripts, and retrieved documents as untrusted input.
- Avoid unsupported claims and invented product procedures.
- Preserve source titles, URLs, and source-type labels.
- Require human review for email drafts and scopes of work.
- Obtain appropriate permissions before collecting or reusing third-party support content.

The current sample articles are fictional test data, not verified Brilliant Directories support documentation.

Authentication, authorization, production monitoring, request limits, secure deployment, and comprehensive security testing remain future work.

## 9. Current Limitations and Future Work

Current limitations include:

- Keyword-based article retrieval rather than a production-grade semantic retrieval system.
- A small fictional article dataset.
- No real support-content ingestion with confirmed permissions.
- No email-provider integration for Task 2.
- No meeting-platform integration for Task 3.
- No production deployment for the Inbox Agent or Meeting-to-Scope workflows.
- No representative real-world evaluation dataset for Tasks 2 and 3.
- A 20-case fictional retrieval evaluation has been completed, but retrieval accuracy on verified support content and AI-generated answer accuracy have not been established.

Recommended future work:

1. Expand live end-to-end testing for Task 2 and Task 3 across additional fictional examples, edge cases, and failure scenarios.
2. Add reviewed evaluation examples for email classification and scope extraction.
3. Measure retrieval relevance and document the evaluation method.
4. Evaluate grounding, source attribution, and unsupported claims.
5. Add authentication, authorization, and secure deployment controls.
6. Evaluate reliability, latency, and failure handling before production use.

Evaluation claims should be recorded only after the relevant tests or measurements have actually been performed.

## 10. Related Documentation

- `README.md` — repository overview and setup instructions.
- `task1-knowledge-brain/README.md` — Knowledge Brain setup and API usage.
- `task2-inbox-agent/README.md` — Inbox Agent behavior and tests.
- `task3-meeting-to-scope/README.md` — Meeting-to-Scope workflow and tests.
- `EVALS.md` — evaluation plans, criteria, and result-recording guidance.
- `AI_LOG.md` — AI-assisted development activities and reported verification results.