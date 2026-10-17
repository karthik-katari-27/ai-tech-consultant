\# AI Tech Consultant — Evaluation Plan



\## 1. Purpose



This document describes how the AI Tech Consultant project will be evaluated for correctness, reliability, retrieval quality, safety, and usefulness.



The project has three planned parts:



1\. Task 1 — Knowledge Brain.

2\. Task 2 — Inbox Agent.

3\. Task 3 — Meeting-to-Scope of Work.



The current implementation focuses on the initial Task 1 API and local article search. Evaluations for the other tasks will be added when those features are implemented.



\## 2. Current Implementation



The Knowledge Brain currently uses a local JSON file containing three fictional test articles.



The search function uses keyword matching:

\- Keywords found in article titles receive three points each.

\- Keywords found only in article text receive one point each.

\- Results with higher scores are returned first.

\- Blank or unmatched searches can return an empty result list.



The API provides `GET /health` and `POST /ask`.



The current implementation does not use an AI model, semantic search, or verified Brilliant Directories support content. Its results are fictional test records, not verified answers from a real support knowledge base.



\## 3. Current Automated Test Results



\*\*Latest reported result: 20 tests passed.\*\*



The full command used was:



&#x20;   .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v



The latest reported output ended with:



&#x20;   Ran 20 tests

&#x20;   OK



This result confirms that the automated tests passed at the time they were run. It does not establish that the application is production-ready or that the search system performs well on real customer questions.



\### Test coverage



| Area | What is checked | Status |

|---|---|---|

| API health | The health endpoint returns the expected status | Passed |

| Matching search | A matching question finds the expected fictional article | Passed |

| Unmatched search | A question without matching keywords returns no results | Passed |

| Input validation | Empty and whitespace-only questions return HTTP 400 | Passed |

| Source labelling | API results are clearly identified as fictional test data | Passed |

| Article-data errors | The API returns a safe HTTP 503 response for simulated article-data failures | Passed |

| Sitemap XML parsing | Supported sitemap structures and malformed XML are tested using local XML strings | Passed |

| Article loading | Valid JSON, missing files, malformed JSON, and incorrect root structures are tested | Passed |

| Article-record validation | Missing fields, incorrect field types, and non-dictionary records are rejected | Passed |

| Simulated unreadable file | A mocked permission failure is handled safely | Passed |



The sitemap tests use in-memory XML data. They do not verify access permission to real support content or demonstrate that real articles have been collected.



\## 4. Reproducing the Current Evaluation



Open PowerShell in the main `ai-tech-consultant` project folder.



Move into the Task 1 folder:



&#x20;   Set-Location .\\task1-knowledge-brain



Run the complete test suite:



&#x20;   .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v



A successful run should end with a test count and `OK`.



Record the actual output whenever the suite is run. If tests fail, investigate and fix the cause before reporting that the suite passes.



\## 5. Current Limitations



The existing tests focus on code correctness and expected behavior for controlled inputs.



They do not yet measure:



\- Search relevance across a representative collection of real support questions.

\- Semantic understanding, synonyms, spelling mistakes, or ambiguous questions.

\- Whether generated answers are factually grounded in approved source documents.

\- Citation accuracy or whether cited sources support an answer.

\- Retrieval performance on a large article collection.

\- Content freshness or detection of changed and removed articles.

\- End-to-end performance of the Inbox Agent or Meeting-to-Scope of Work workflow.

\- Production security, load handling, latency, and availability.



The current implementation does not generate AI answers. Search results are article records returned by keyword matching.



\## 6. Planned Retrieval-Quality Evaluation



When approved support content becomes available, create a reviewed test dataset containing representative questions and their expected relevant articles.



Include question types such as:

\- Direct questions using words from an article title.

\- Questions using synonyms or alternative wording.

\- Questions containing spelling mistakes.

\- Questions with insufficient context or ambiguous intent.

\- Questions for which no approved article provides sufficient evidence.



For each test question, record:

\- The question.

\- The expected relevant article identifiers.

\- The actual retrieved articles.

\- Whether the expected article appears in the results.

\- Relevant observations and failure cases.



Potential retrieval metrics include:



\- \*\*Recall@k:\*\* How often a relevant article appears among the first `k` retrieved results.

\- \*\*Precision@k:\*\* How many of the first `k` retrieved results are relevant.

\- \*\*Mean Reciprocal Rank (MRR):\*\* How highly the first relevant result is ranked.



These metrics are planned, not measured. Numerical targets should be selected and justified before the evaluation is run.



\## 7. Planned Grounding and Citation Evaluation



When answer generation and approved-content retrieval are implemented, evaluate whether responses:



\- Are supported by retrieved source material.

\- Cite the correct source URL.

\- Avoid inventing unsupported product features or procedures.

\- Clearly identify when available evidence is insufficient.

\- Distinguish verified support content from fictional or unverified data.



Use manually reviewed examples with expected source documents and documented correctness criteria.



Grounding and citation results must not be reported until the relevant functionality exists and has been evaluated.



\## 8. Planned Inbox Agent Evaluation



When Task 2 is implemented, evaluate:



\- Email classification accuracy.

\- Correct identification of customer intent.

\- Relevance of retrieved knowledge.

\- Factual accuracy and completeness of draft replies.

\- Correct use of source references.

\- Appropriate handling of ambiguous, sensitive, or unsupported requests.

\- Whether drafts are routed for human review rather than sent without approval.



Use a reviewed dataset of representative email examples. Report the evaluation method, sample size, results, and known limitations.



\## 9. Planned Meeting-to-Scope of Work Evaluation



When Task 3 is implemented, evaluate whether the system correctly identifies:



\- Customer requirements and desired outcomes.

\- Deliverables and scope boundaries.

\- Assumptions, dependencies, and exclusions.

\- Risks, constraints, and open questions.

\- Unsupported commitments or missing information.



Compare generated drafts with human-reviewed reference documents. Record omissions, incorrect assumptions, unsupported claims, and the corrections required from a reviewer.



The approval workflow must remain human-controlled.



\## 10. Permissions and Data Safety



Real Brilliant Directories support content has not been ingested into the current dataset.



Before evaluating retrieval on real support content:

\- Confirm applicable collection and reuse permissions.

\- Restrict ingestion to approved sources and URLs.

\- Retain source attribution and provenance.

\- Define how changed, outdated, or no-longer-approved content will be handled.



Public sitemap availability is not, by itself, proof of permission to collect and reuse article content.



Until approval is established, continue using fictional data for development and testing.



\## 11. Evaluation Record Template



Use the following template to record future evaluation runs.



| Field | Value |

|---|---|

| Evaluation date | Not recorded |

| Commit ID | Record the tested commit |

| Feature evaluated | Record the feature |

| Test or dataset | Record the exact test command or dataset |

| Sample size | Record the actual number of cases |

| Metrics | Record the metrics used |

| Results | Record actual observed results |

| Failures and limitations | Describe observed issues |

| Reviewer | Record the responsible reviewer, where applicable |



Do not fill in future results or claim success before performing the evaluation.



\## 12. Next Evaluation Priorities



1\. Keep the existing automated tests passing.

2\. Confirm permission before collecting real support content.

3\. Prepare a reviewed retrieval test set when approved content becomes available.

4\. Measure retrieval relevance and document the results.

5\. Evaluate factual grounding and source attribution when answer generation is implemented.

6\. Add task-specific evaluations for the Inbox Agent and Meeting-to-Scope of Work workflows.

7\. Evaluate security, latency, reliability, and human-review controls before production use.
