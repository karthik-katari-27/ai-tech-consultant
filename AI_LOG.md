\# AI Tech Consultant — AI Usage Log



\## 1. Purpose



This document records the use of AI tools during development of the AI Tech Consultant capstone project. It summarizes AI-assisted implementation, debugging, testing, documentation, and design decisions.



AI-generated suggestions and code were reviewed during development. Test results are recorded only where a test run was actually performed.



\## 2. Tools Used



\### ChatGPT



Used for:

\- Beginner-friendly implementation guidance.

\- Reviewing code and identifying validation gaps.

\- Explaining errors and suggesting corrections.

\- Preparing documentation drafts.

\- Designing test cases and guiding local verification.

\- Planning next development milestones.



\### Codex



Used for:

\- Reviewing the existing Task 1 implementation.

\- Implementing safe article-data error handling.

\- Adding API error-handling tests.

\- Creating local sitemap parser tests.

\- Updating project README documentation.



The project application itself does not currently use an AI model to generate answers. ChatGPT and Codex were development tools, not components of the running application.



\## 3. AI-Assisted Development Activities



\### Activity 1 — Safe article-data error handling



\*\*Goal:\*\* Prevent local article-data failures from exposing internal error details through the API.



\*\*AI contribution:\*\* Codex was instructed to add an `ArticleDataError` exception, handle missing or unreadable files and malformed or incorrectly shaped JSON data, and return a generic HTTP 503 error from the `/ask` endpoint. It also added API tests for simulated failures and preserved empty-question validation.



\*\*Human verification:\*\* The user ran the automated test suite after implementation.



\*\*Reported result:\*\* Six original tests plus three new API error-handling tests passed as part of a later full run.



\### Activity 2 — Sitemap parser testing



\*\*Goal:\*\* Test sitemap XML parsing without fetching external content.



\*\*AI contribution:\*\* Codex created `tests/test\_inspect\_sitemap.py` with tests for a normal URL list, a sitemap index, and malformed XML.



\*\*Human verification:\*\* The user ran the sitemap tests locally.



\*\*Reported result:\*\* Three tests passed.



\*\*Safety decision:\*\* Sitemap parsing tests use XML strings in memory. The test run did not require downloading real support articles.



\### Activity 3 — Article loader testing



\*\*Goal:\*\* Verify the behavior of `load\_articles()` when local data is valid or unavailable.



\*\*AI contribution:\*\* Codex created temporary-file tests for valid JSON, missing files, malformed JSON, an incorrect JSON root structure, and simulated permission errors.



ChatGPT then guided the user through extending article validation to reject non-dictionary records, missing required fields, incorrect field types, and empty required values. The test fixtures were updated to match the five-field article schema.



\*\*Human verification:\*\* The user ran the article-loader tests and then the complete test suite.



\*\*Reported results:\*\*

\- Eight article-loader tests passed.

\- The full suite subsequently passed all 20 tests.



\### Activity 4 — Documentation updates



\*\*Goal:\*\* Keep project documentation consistent with the implemented features and actual test results.



\*\*AI contribution:\*\* Codex updated the root README and Task 1 README. ChatGPT drafted `DESIGN.md` and `EVALS.md`, and guided the user through updating the README files to reflect 20 passing automated tests.



\*\*Human verification:\*\* The user saved the files, checked their locations and Git status, and committed the documentation to local Git history.



\*\*Outcome:\*\* The project now documents its current API, fictional-data limitation, architecture, evaluation approach, and future implementation plans.



\### Activity 5 — Article record validation



\*\*Goal:\*\* Prevent malformed article records from entering the search process.



\*\*AI contribution:\*\* ChatGPT examined the actual JSON schema and supplied a validation implementation for the user to apply manually. The user updated `search\_articles.py`, adjusted an existing temporary-data fixture, and added three validation tests.



\*\*Human verification:\*\* The user ran eight article-loader tests and then all 20 automated tests.



\*\*Reported result:\*\* Both runs passed.



\### Activity 6 — Git checkpoints



\*\*Goal:\*\* Keep a recoverable local project history.



\*\*AI contribution:\*\* ChatGPT guided the user through checking `.gitignore`, reviewing Git status, removing trailing whitespace, staging intended project files, and creating local commits.



\*\*Human verification:\*\* The user ran the Git commands and inspected their output.



\*\*Outcome:\*\* Three local commits were recorded:

\- `74ccd8e` — Build Task 1 Knowledge Brain starter

\- `5bbca30` — Add system design documentation

\- `dce5d76` — Add evaluation plan and test documentation



The project was also checked with `git status`, which reported a clean working tree at that checkpoint.



\## 4. Test Evidence



The latest reported full-suite run was:



&#x20;   .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v



Reported output:



&#x20;   Ran 20 tests

&#x20;   OK



The individual sitemap and article-loader test runs also passed.



These results demonstrate that the automated tests passed at the time they were executed. They do not establish production readiness, real-world retrieval quality, or permission to reuse third-party support content.



\## 5. Important Design and Safety Decisions



AI assistance helped document and preserve these decisions:



\- Use fictional local records until permission to collect and reuse real support content has been clarified.

\- Do not treat public sitemap availability as proof of permission to scrape or reuse articles.

\- Return generic API errors rather than exposing file paths or internal exception details.

\- Validate article records before searching them.

\- Keep unimplemented AI features clearly labelled as future work.

\- Require human review of future customer-facing replies and scopes of work.

\- Record actual test results rather than inventing evaluation metrics.



\## 6. Current Limitations



The current application:

\- Uses keyword matching against a small fictional JSON dataset.

\- Does not connect to an AI model.

\- Does not ingest verified Brilliant Directories support articles.

\- Does not yet implement the Inbox Agent or Meeting-to-Scope of Work workflows.

\- Has not been evaluated on a representative real-world support-question dataset.



These limitations should remain visible in project documentation until they are addressed and verified.



\## 7. Responsible AI Use



AI tools supported implementation and explanation, but their output was not treated as proof of correctness by itself. The user applied changes, inspected command output, and ran tests to verify key behaviors.



Future AI-assisted development should follow the same approach:

1\. State the task and constraints clearly.

2\. Review the proposed code or design before accepting changes.

3\. Test behavior locally.

4\. Record observed results and known limitations.

5\. Obtain required permissions before collecting or processing third-party content.



\## 8. Ongoing Log



Add future entries whenever AI tools contribute significant code, design decisions, debugging, evaluation, or documentation.



For each entry, record the date, tool, task, proposed changes, human review, and actual test results where applicable. Keep the log factual and distinguish suggestions from implemented work.

## 9. Activity 7 — Local Ollama Integration

**Date:** October 18, 2026

**Goal:** Add a local-model option for generating Knowledge Brain answers without requiring Anthropic API credits.

**AI contribution:** ChatGPT guided the implementation of `local_ai_service.py`, the `/ask-local` endpoint, prompt construction, error handling, and automated tests. Diagnostic logging was also added to the Claude service.

**Human verification:** The user ran the local service tests and the complete Task 1 test suite.

**Reported results:**
- Five local AI service tests passed.
- The complete Task 1 suite passed 41 tests.
- A live `/ask-local` request using Qwen2.5 7B through Ollama succeeded with fictional reference material.

**Limitations:** The live test used a single question and fictional data. It does not establish general answer accuracy or production readiness.

**Git checkpoint:** `b23d42c` — Add local Ollama-backed answer endpoint.

## 10. Activity 8 — Inbox Agent Prototype

**Date:** October 18, 2026

**Goal:** Classify incoming support emails, retrieve potentially relevant Knowledge Brain articles, and prepare reply drafts for human review.

**AI contribution:** ChatGPT guided the implementation of `task2-inbox-agent/inbox_agent.py`, its README, and `tests/test_inbox_agent.py`.

The prototype classifies email intent, summarizes the request, assigns basic urgency, retrieves article results, prepares draft replies, and returns source details. It does not send emails automatically.

**Human verification:** The user ran the dedicated Inbox Agent tests.

**Reported result:** Five automated tests passed using mocked model and API responses.

**Limitations:** Live end-to-end testing has not been recorded. The prototype has no email-provider integration and has not been evaluated on representative real-world emails.

**Git checkpoint:** `2669daf` — Add human-reviewed Inbox Agent prototype.

## 11. Activity 9 — Meeting-to-Scope of Work Prototype

**Date:** October 18, 2026

**Goal:** Generate structured draft scopes of work from meeting transcripts.

**AI contribution:** ChatGPT guided the implementation of `task3-meeting-to-scope/meeting_to_scope.py`, its README, and `tests/test_meeting_to_scope.py`.

The prototype extracts meeting summaries, customer goals, requirements, deliverables, scope boundaries, assumptions, dependencies, risks, open questions, and knowledge gaps. It includes source details and marks the output as pending human review.

**Human verification:** The user ran the dedicated Meeting-to-Scope tests.

**Reported result:** Five automated tests passed using mocked model and API responses.

**Limitations:** Live end-to-end testing has not been recorded. The prototype has no meeting-platform integration and has not been evaluated against representative real-world scopes of work.

**Git checkpoint:** `9c03a27` — Add human-reviewed meeting-to-scope prototype.

## 12. Activity 10 — Repository Documentation and Publication

**Date:** October 18, 2026

**Goal:** Update repository documentation to describe all three prototypes and their current verification status.

**AI contribution:** ChatGPT guided updates to the root `README.md`, `DESIGN.md`, and `EVALS.md`.

**Human verification:** The user checked formatting, staged the intended files, committed the updates, and pushed them to the public GitHub repository.

**Documentation commits:**
- `9b834ec` — Update root README for all three AI projects.
- `aeb6a89` — Update system design for all three prototypes.
- `017ee62` — Update evaluation plan and test evidence.

Repository: https://github.com/karthik-katari-27/ai-tech-consultant

## 13. Activity 11 — Automated Test Summary

**Date:** October 18, 2026

The user ran the three test suites separately and reported the following results:

| Project | Tests passed |
|---|---:|
| Task 1 — Knowledge Brain | 41 |
| Task 2 — Inbox Agent | 5 |
| Task 3 — Meeting-to-Scope of Work | 5 |
| **Total across separate runs** | **51** |

**Reported result:** All 51 tests passed across the three separate runs.

**Limitations:** Task 2 and Task 3 tests use mocked model and API responses. Their passing results do not establish live end-to-end reliability, real-world model accuracy, or production readiness.

## 14. Current Development Status

As of October 18, 2026:

- Task 1 has a tested article-search API, a Claude integration, and a locally tested Ollama answer endpoint.
- Task 2 has an initial Inbox Agent prototype and five passing mocked tests.
- Task 3 has an initial Meeting-to-Scope of Work prototype and five passing mocked tests.
- The root README, system design, and evaluation documentation have been updated and pushed to GitHub.
- Live end-to-end testing of Task 2 and Task 3 remains outstanding.
- Real support-content ingestion, permission verification, representative evaluation datasets, and production security controls remain future work.

Test counts reflect the results reported during development. Update this record when additional tests or evaluations are performed.