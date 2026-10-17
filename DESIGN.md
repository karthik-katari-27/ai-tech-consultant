\# AI Tech Consultant — System Design



\## 1. Project Overview



AI Tech Consultant is a three-part project designed to help a technical support team retrieve product knowledge, respond to customer emails, and prepare statements of work from meeting transcripts.



The project is planned around three main tasks:



1\. \*\*Task 1 — Knowledge Brain:\*\* Search approved support documentation and provide relevant information with source references.

2\. \*\*Task 2 — Inbox Agent:\*\* Analyze incoming emails, retrieve relevant knowledge, and prepare response drafts for human review.

3\. \*\*Task 3 — Meeting-to-Scope of Work:\*\* Analyze meeting transcripts and prepare draft scopes of work and proposals for human approval.



The goal is to make support and consulting workflows more efficient while keeping humans responsible for reviewing important customer-facing outputs.



\## 2. Current Implementation Status



The current implementation is an initial version of Task 1.



Implemented components:



\- A FastAPI application with `GET /health` and `POST /ask`.

\- Local JSON-based article loading.

\- Keyword-based article search with higher scores for title matches.

\- Validation of article records.

\- Generic errors for unavailable or invalid article data.

\- A separate sitemap inspection and XML parsing utility.

\- Automated tests for the API, sitemap parsing, and article loading and validation.



The current dataset contains three fictional test articles. It does not contain verified Brilliant Directories support content.



The latest complete automated test run reported 20 passing tests.



The Inbox Agent, Meeting-to-Scope of Work workflow, AI-powered retrieval, approved real-content ingestion, and production deployment are not yet implemented.



\## 3. Current Task 1 Architecture



The current request flow is:



1\. A client sends a question to `POST /ask`.

2\. FastAPI validates that the question is not empty.

3\. The search module loads and validates the local JSON dataset.

4\. The search module extracts keywords from the question and article fields.

5\. Matching title keywords receive three points each, while matching text-only keywords receive one point each.

6\. The highest-scoring matches are returned, up to the configured result limit.

7\. The response clearly labels the results as fictional test data.



If the question is empty, the API returns HTTP 400. If the article data cannot be loaded or validated, the API returns HTTP 503 with a generic error message.



If no keywords match, the API returns an empty result list.



\## 4. API Design



\### Health endpoint



\*\*Method:\*\* `GET`



\*\*Path:\*\* `/health`



Purpose: Confirm that the API process is responding.



Example response:



&#x20;   {

&#x20;     "status": "healthy"

&#x20;   }



\### Question endpoint



\*\*Method:\*\* `POST`



\*\*Path:\*\* `/ask`



Example request:



&#x20;   {

&#x20;     "question": "How do I publish a directory listing?"

&#x20;   }



The response includes the original question, the response type, a notice identifying the data as fictional, the number of matches, and the matching article records.



The endpoint currently uses local keyword search. It does not call an AI model or retrieve verified support content.



\## 5. Article Data Design



Each article record must contain these five fields:



| Field | Purpose |

|---|---|

| `id` | Unique article identifier |

| `title` | Article title |

| `url` | Source or reference URL |

| `text` | Article content |

| `source\_type` | Indicates the type of source data |



All five fields must contain non-empty strings.



The current sample records use fictional `example.test` URLs and the `fictional\_test\_data` source label.



\### Planned metadata for approved content



When approved real content becomes available, records should additionally track appropriate provenance metadata, such as:



\- Canonical source URL and retrieval time.

\- Source modification time, when available.

\- Content hash for detecting changes.

\- Source type and permission status.

\- Content version or ingestion status.



These additions are planned and are not part of the current five-field schema.



\## 6. Sitemap Discovery and Ingestion



The sitemap utility is separate from the question-answering API.



It is intended to inspect sitemap XML, recognize supported sitemap structures, and identify candidate URLs within the configured hostname and URL restrictions.



Local tests cover ordinary sitemap URL lists, sitemap indexes, and malformed XML.



The utility has not been used to fetch real articles. Sitemap discovery alone does not establish permission to collect, store, redistribute, or use the discovered content in an AI system.



Before real-content ingestion is implemented, the project must establish the applicable access permissions, reuse rights, attribution requirements, URL restrictions, and request limits.



Once permission is established, ingestion should be restricted to approved sources and should retain source provenance. The process should also support safe refreshes, change detection, and removal of content that is no longer approved.



\## 7. Planned Task 2 — Inbox Agent



The planned Inbox Agent will:



1\. Receive or read an incoming customer email through an approved integration.

2\. Classify the email's intent and identify the customer's issue.

3\. Query the Knowledge Brain API for relevant information.

4\. Prepare a draft response grounded in the retrieved information.

5\. Include source references when supported by approved knowledge.

6\. Send the draft to a human for review and approval.

7\. Record review feedback for evaluation and future improvement.



Sending customer-facing messages automatically is not part of the initial human-review workflow.



This task has not yet been implemented.



\## 8. Planned Task 3 — Meeting-to-Scope of Work



The planned workflow will:



1\. Accept a meeting transcript.

2\. Extract customer needs, requirements, assumptions, dependencies, and open questions.

3\. Query the Knowledge Brain API for relevant approved product information.

4\. Prepare a draft scope of work or proposal.

5\. Highlight uncertainties, missing requirements, and assumptions.

6\. Require human review and approval before the document is finalized or shared.



This task has not yet been implemented.



\## 9. Target System Architecture



The intended high-level architecture is:



&#x20;   Incoming support documentation

&#x20;               |

&#x20;               v

&#x20;      Approved ingestion process

&#x20;               |

&#x20;               v

&#x20;       Knowledge Brain storage

&#x20;               |

&#x20;               v

&#x20;      Knowledge Brain API

&#x20;          /          \\

&#x20;         v            v

&#x20;    Inbox Agent   Meeting-to-SOW

&#x20;         |            |

&#x20;         v            v

&#x20;    Draft reply   Draft proposal

&#x20;         |            |

&#x20;         v            v

&#x20;    Human review  Human review



The current implementation only covers the early local-data and API portions of Task 1.



Persistent storage, approved content ingestion, AI-powered retrieval, the Inbox Agent, the Meeting-to-Scope of Work workflow, and integrations remain future work.



\## 10. Reliability and Testing



The current test suite covers:



\- API health and question handling.

\- Matching and unmatched questions.

\- Empty-input validation and error responses.

\- Fictional-source labelling.

\- Sitemap XML parsing.

\- Article loading and invalid-data handling.



The latest complete test run reported 20 passing tests.



Future development should add tests for approved-content ingestion, source attribution, retrieval quality, content refresh and deletion, and the end-to-end behavior of the Inbox Agent and Meeting-to-Scope of Work workflow.



Evaluation results must be based on tests that were actually run. Expected behavior must not be reported as a measured result.



\## 11. Security, Permissions, and Human Oversight



The project must follow these principles:



\- Do not ingest real support articles until collection and reuse permissions have been clarified.

\- Do not expose internal file paths, stack traces, or sensitive configuration in API error responses.

\- Keep credentials and environment-specific secrets out of version control.

\- Restrict ingestion to approved sources and URLs.

\- Keep source references associated with retrieved content.

\- Identify missing evidence and uncertainty rather than inventing answers.

\- Require human approval for customer-facing replies and proposed scopes of work.

\- Preserve a record of significant human corrections and evaluation results where appropriate.



Authentication, authorization, request limits, production monitoring, and secure deployment must be designed before exposing the service to untrusted clients.



\## 12. Implementation Roadmap



1\. Maintain the working Task 1 baseline and its automated tests.

2\. Confirm permission to use real support content.

3\. Build and test a small ingestion workflow using approved sources.

4\. Improve retrieval quality and add source attribution.

5\. Add evaluation cases for answer relevance, grounding, and unsupported answers.

6\. Build the Inbox Agent with human-reviewed draft replies.

7\. Build the Meeting-to-Scope of Work workflow with human approval.

8\. Complete end-to-end evaluation, security review, documentation, and demo preparation.



Each milestone should be tested and documented before the next major integration is introduced.