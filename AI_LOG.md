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
