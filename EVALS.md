# AI Tech Consultant — Evaluation Plan and Results

## 1. Purpose

This document records the evaluation approach, observed automated test results, known limitations, and planned validation activities for the AI Tech Consultant project.

The project contains three prototypes:

1. **Task 1 — Knowledge Brain:** Retrieves relevant articles and supports AI-generated answers using local or external models.
2. **Task 2 — Inbox Agent:** Classifies incoming support emails and prepares draft replies for human review.
3. **Task 3 — Meeting-to-Scope of Work:** Converts meeting transcripts into structured draft scopes of work for human review.

This document distinguishes automated test results from live integration tests and future evaluations. Passing unit tests does not establish production readiness or real-world AI accuracy.

## 2. Evaluation Principles

All reported evaluation results must be based on tests or measurements that were actually performed.

The evaluation process should:

- Record the tested commit, commands, and observed results.
- Distinguish mocked tests from live service requests.
- Preserve known limitations and failure cases.
- Avoid inventing accuracy scores, retrieval metrics, or success rates.
- Keep fictional test data distinct from verified support documentation.
- Require human review of customer-facing drafts.
- Obtain appropriate permissions before collecting or processing third-party content.

## 3. Current Automated Test Results

The latest reported automated test runs passed all 51 tests across three separate runs.

| Project | Tests passed | Test approach |
|---|---:|---|
| Task 1 — Knowledge Brain | 41 | API, article handling, service, and related unit tests |
| Task 2 — Inbox Agent | 5 | Mocked model and Knowledge Brain responses |
| Task 3 — Meeting-to-Scope of Work | 5 | Mocked model and Knowledge Brain responses |
| **Total** | **51** | **Separate test runs** |

These results were reported by the user during development on October 18, 2026.

The Task 2 and Task 3 tests do not make live AI requests. They verify selected behaviors using mocked responses. Their results do not establish real-world classification accuracy, draft quality, or live end-to-end reliability.

The 51 tests were run as three separate suites, not as one combined test-discovery command.

## 4. Reproducing the Automated Tests

Run these commands from the `ai-tech-consultant` repository root in Windows PowerShell.

### Task 1 — Knowledge Brain

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task1-knowledge-brain\tests -v
```

Reported result: 41 tests passed.

### Task 2 — Inbox Agent

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task2-inbox-agent\tests -p test_inbox_agent.py -v
```

Reported result: 5 tests passed.

The tests cover email validation, classification parsing, draft generation, source references, handling of missing article results, and human-review status.

### Task 3 — Meeting-to-Scope of Work

```powershell
.\task1-knowledge-brain\.venv\Scripts\python.exe -m unittest discover -s .\task3-meeting-to-scope\tests -p test_meeting_to_scope.py -v
```

Reported result: 5 tests passed.

The tests cover empty-transcript validation, structured draft generation, missing references, invalid model JSON, and field-type validation.

## 5. Live Integration Test Evidence

### Task 1 — Local AI endpoint

A live request was sent to `POST /ask-local` using the local Qwen2.5 7B model through Ollama.

The question was:

`How do I publish a directory listing?`

The response included three steps supported by the fictional reference article:

1. Review the draft listing.
2. Choose Publish.
3. Verify that the listing appears in the sample directory.

The response also included the source title and URL and identified the material as fictional test data.

**Observed result:** The request succeeded, and the response returned the supported steps with a source reference.

**Limitations:** This was a single live request using fictional reference data. It does not establish general answer accuracy, retrieval quality, or production reliability.

### Task 2 — Inbox Agent

The automated tests used mocked responses from the model and Knowledge Brain API.

**Live end-to-end evaluation:** Not yet recorded.

The workflow still needs to be exercised with a running Knowledge Brain API and Ollama model using fictional email content. No production email integration has been evaluated.

### Task 3 — Meeting-to-Scope of Work

The automated tests used mocked responses from the model and Knowledge Brain API.

**Live end-to-end evaluation:** Not yet recorded.

The workflow still needs to be exercised with a running Knowledge Brain API and Ollama model using a fictional meeting transcript. Generated requirements, assumptions, deliverables, and risks must be checked against the transcript.

## 6. Planned Knowledge Brain Retrieval Evaluation

### Evaluation goals

Evaluate whether retrieval returns relevant articles for questions about the product knowledge represented in the dataset.

The test set should include:

- Questions using wording found directly in article titles.
- Questions using synonyms or alternative wording.
- Questions containing spelling mistakes.
- Questions containing insufficient context or ambiguous intent.
- Questions for which no approved article provides sufficient evidence.

### Recording each case

For each test question, record:

- The question.
- Expected relevant article identifiers.
- Actual retrieved articles.
- Whether an expected article appears in the results.
- Relevant observations and failure cases.

### Potential retrieval metrics

Possible metrics include:

- **Recall@k:** Whether relevant articles appear among the first `k` results.
- **Precision@k:** The proportion of the first `k` results that are relevant.
- **Mean Reciprocal Rank (MRR):** How highly the first relevant article is ranked.

These metrics have not been measured. Numerical targets should be selected and justified before a retrieval evaluation is run.

The current keyword-based retrieval system should be evaluated on an explicitly reviewed dataset before claims about its quality are made.

## 7. Planned Grounding and Citation Evaluation

When evaluating generated answers, examine whether responses:

- Are supported by retrieved source material.
- Cite the correct source URL.
- Avoid inventing unsupported product features or procedures.
- Clearly identify when the available evidence is insufficient.
- Distinguish verified support content from fictional or unverified data.

Use manually reviewed examples with expected source documents and documented correctness criteria.

Grounding and citation accuracy results must not be reported until the relevant evaluation has been performed.

## 8. Planned Inbox Agent Evaluation

Evaluate the Inbox Agent using a reviewed dataset of representative email examples.

Measure or review:

- Email classification accuracy.
- Correct identification of customer intent.
- Relevance of retrieved knowledge.
- Factual accuracy and completeness of draft replies.
- Correct use of source references.
- Handling of ambiguous, sensitive, or unsupported requests.
- Correct routing of drafts for human review rather than automatic sending.

Record the evaluation method, sample size, results, and known limitations.

The current five automated tests are functional tests using mocked responses, not an email classification benchmark. Classification accuracy has not been measured.

## 9. Planned Meeting-to-Scope of Work Evaluation

Evaluate whether generated drafts correctly identify:

- Customer requirements and desired outcomes.
- Deliverables and scope boundaries.
- Assumptions, dependencies, and exclusions.
- Risks, constraints, and open questions.
- Unsupported commitments or missing information.
- Knowledge gaps that require source verification.

Compare generated drafts with human-reviewed reference documents. Record omissions, incorrect assumptions, unsupported claims, and corrections required from reviewers.

The approval workflow must remain human-controlled.

The current five automated tests validate selected behavior and output structure. They do not establish the accuracy or completeness of generated scopes on real meeting transcripts.

## 10. Permissions and Data Safety

Real Brilliant Directories support content has not been ingested into the current dataset.

Before evaluating retrieval on real support content:

- Confirm applicable collection and reuse permissions.
- Restrict ingestion to approved sources and URLs.
- Retain source attribution and provenance.
- Define how changed, outdated, or no-longer-approved content will be handled.

Public sitemap availability is not, by itself, proof of permission to collect or reuse article content.

Until approval is established, continue using fictional data for development and testing.

Customer emails and meeting transcripts may contain confidential or personal information. Use fictional or appropriately authorized and protected data during development and evaluation.

## 11. Evaluation Record Template

Complete this template whenever a meaningful evaluation run is performed.

| Field | Value |
|---|---|
| Evaluation date | Record the actual date |
| Commit ID | Record the tested commit |
| Feature evaluated | Record the feature |
| Test command or dataset | Record the exact command or dataset |
| Sample size | Record the actual number of cases |
| Metrics | Record the metrics used |
| Results | Record observed results |
| Failures and limitations | Describe observed issues |
| Reviewer | Record the responsible reviewer, where applicable |

Do not fill in future results or claim success before performing the evaluation.

## 12. Next Evaluation Priorities

1. Keep all existing automated tests passing.
2. Verify Task 2 and Task 3 through live end-to-end tests using fictional data.
3. Prepare a reviewed retrieval test set when approved content becomes available.
4. Measure retrieval relevance and document the results.
5. Evaluate factual grounding and source attribution.
6. Evaluate email classification and draft quality on a reviewed dataset.
7. Evaluate scope extraction, omissions, and unsupported assumptions.
8. Evaluate security, latency, reliability, and human-review controls before production use.

The current prototypes are initial development implementations. Production readiness, representative real-world accuracy, and comprehensive live integration behavior have not been established.