
"""Tests for the Meeting-to-Scope of Work prototype."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Make the sibling meeting_to_scope.py module importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from meeting_to_scope import (
    MeetingToScopeError,
    _enforce_transcript_constraints,
    generate_scope_of_work,
)


class MeetingToScopeTests(unittest.TestCase):
    """Test scope generation without live AI or API requests."""

    def sample_article(self):
        return {
            "id": "fictional-directory-listing",
            "title": "Fictional Guide: Publishing a Directory Listing",
            "url": "https://example.test/support/publish-listing",
            "text": (
                "This is fictional test data. An editor reviews a draft "
                "listing, chooses Publish, and verifies that it appears "
                "in a sample directory."
            ),
            "source_type": "fictional_test_data",
        }

    def sample_scope(self):
        return {
            "meeting_summary": "The customer wants to publish a directory listing.",
            "customer_goals": ["Publish a directory listing."],
            "requirements": ["The listing must appear in the sample directory."],
            "deliverables": ["A draft directory listing."],
            "in_scope": ["Review and publish the draft listing."],
            "out_of_scope": [],
            "assumptions": ["The customer will provide listing details."],
            "dependencies": ["Listing details are available."],
            "risks": ["The listing may not appear as expected."],
            "open_questions": ["Who will provide the final listing details?"],
            "knowledge_gaps": [],
        }

    def test_empty_transcript_is_rejected(self):
        with (
            patch("meeting_to_scope._search_knowledge_brain") as mock_search,
            patch("meeting_to_scope._ask_local_model") as mock_model,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Meeting transcript must not be empty.",
            ):
                generate_scope_of_work("   ")

        mock_search.assert_not_called()
        mock_model.assert_not_called()

    def test_generates_structured_draft_and_requires_human_review(self):
        transcript = (
            "Customer: We need to publish a directory listing. "
            "We should confirm who will provide the listing details."
        )
        article = self.sample_article()
        scope_json = json.dumps(self.sample_scope())

        with (
            patch(
                "meeting_to_scope._search_knowledge_brain",
                return_value={
                    "results": [article],
                    "source_notice": "Fictional test articles only.",
                },
            ) as mock_search,
            patch(
                "meeting_to_scope._ask_local_model",
                return_value=scope_json,
            ) as mock_model,
        ):
            result = generate_scope_of_work(transcript)

        mock_search.assert_called_once_with(transcript)
        mock_model.assert_called_once()

        prompt = mock_model.call_args.args[0]
        self.assertIn(transcript, prompt)
        self.assertIn(
            "Fictional Guide: Publishing a Directory Listing",
            prompt,
        )
        self.assertIn(
            "https://example.test/support/publish-listing",
            prompt,
        )
        self.assertIn("Do not invent prices", prompt)
        self.assertIn("feature-specific verification gap", prompt)
        self.assertIn("notification triggers", prompt)

        self.assertEqual(
            result["status"],
            "draft_pending_human_review",
        )
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["approved"])
        self.assertFalse(result["finalized"])

        self.assertEqual(
            result["meeting_summary"],
            self.sample_scope()["meeting_summary"],
        )
        self.assertEqual(
            result["customer_goals"],
            self.sample_scope()["customer_goals"],
        )
        self.assertEqual(
            result["open_questions"],
            self.sample_scope()["open_questions"],
        )
        self.assertEqual(
            result["sources"][0]["url"],
            "https://example.test/support/publish-listing",
        )
        self.assertEqual(
            result["source_notice"],
            "Fictional test articles only.",
        )

    def test_no_matching_articles_produces_draft_without_sources(self):
        with (
            patch(
                "meeting_to_scope._search_knowledge_brain",
                return_value={
                    "results": [],
                    "source_notice": "No matching references found.",
                },
            ) as mock_search,
            patch(
                "meeting_to_scope._ask_local_model",
                return_value=json.dumps(self.sample_scope()),
            ) as mock_model,
        ):
            result = generate_scope_of_work(
                "We need a new service integration."
            )

        mock_search.assert_called_once()
        mock_model.assert_called_once()

        prompt = mock_model.call_args.args[0]
        self.assertIn("No matching Knowledge Brain articles were found", prompt)

        self.assertEqual(result["sources"], [])
        self.assertEqual(
            result["source_notice"],
            "No matching references found.",
        )
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["approved"])

    def test_invalid_model_json_is_rejected(self):
        with (
            patch(
                "meeting_to_scope._search_knowledge_brain",
                return_value={"results": []},
            ),
            patch(
                "meeting_to_scope._ask_local_model",
                return_value="not valid JSON",
            ),
        ):
            with self.assertRaisesRegex(
                MeetingToScopeError,
                "The local model returned invalid scope JSON.",
            ):
                generate_scope_of_work("Discuss project requirements.")

    def test_invalid_scope_field_type_is_rejected(self):
        invalid_scope = self.sample_scope()
        invalid_scope["requirements"] = "This should be a list."

        with (
            patch(
                "meeting_to_scope._search_knowledge_brain",
                return_value={"results": []},
            ),
            patch(
                "meeting_to_scope._ask_local_model",
                return_value=json.dumps(invalid_scope),
            ),
        ):
            with self.assertRaisesRegex(
                MeetingToScopeError,
                "invalid 'requirements' field",
            ):
                generate_scope_of_work("Discuss project requirements.")

    def test_prompt_separates_assumptions_from_open_questions(self):
        scope = self.sample_scope()
        scope["assumptions"] = []
        scope["open_questions"] = [
            "What is the budget?",
            "What is the delivery date?",
            "What are the final acceptance criteria?",
        ]

        with (
            patch(
                "meeting_to_scope._search_knowledge_brain",
                return_value={"results": []},
            ),
            patch(
                "meeting_to_scope._ask_local_model",
                return_value=json.dumps(scope),
            ) as mock_model,
        ):
            result = generate_scope_of_work(
                "The budget, delivery date, and acceptance criteria "
                "are undecided."
            )

        prompt = mock_model.call_args.args[0]

        self.assertIn(
            "Put unresolved decisions, missing information",
            prompt,
        )
        self.assertIn(
            "Do not list the same unresolved issue under both assumptions",
            prompt,
        )
        self.assertEqual(result["assumptions"], [])
        self.assertIn(
            "What is the budget?",
            result["open_questions"],
        )
        self.assertIn(
            "What is the delivery date?",
            result["open_questions"],
        )


    def test_removes_unsupported_automation_claim(self):
        scope = self.sample_scope()
        scope["requirements"] = [
            "The publication process should be automated."
        ]

        result = _enforce_transcript_constraints(
            scope,
            "Members need to create and publish directory listings.",
        )

        self.assertEqual(result["requirements"], [])
        self.assertTrue(
            any(
                "automated or remain manual" in question
                for question in result["open_questions"]
            )
        )

    def test_moves_unverified_platform_assumption_to_question(self):
        scope = self.sample_scope()
        scope["assumptions"] = [
            "The sample directory exists and is accessible for verification."
        ]

        result = _enforce_transcript_constraints(
            scope,
            "The customer wants published directory listings.",
        )

        self.assertEqual(result["assumptions"], [])
        self.assertTrue(
            any(
                "sample directory" in question.lower()
                and "confirmed" in question.lower()
                for question in result["open_questions"]
            )
        )

    def test_removes_dependencies_duplicated_by_open_questions(self):
        scope = self.sample_scope()
        scope["dependencies"] = [
            "Budget and delivery date to be confirmed",
            "Editor role availability",
        ]
        scope["open_questions"] = [
            "What is the project budget?",
            "What is the delivery date?",
        ]

        result = _enforce_transcript_constraints(
            scope,
            "The budget and delivery date have not been agreed.",
        )

        self.assertEqual(
            result["dependencies"],
            ["Editor role availability"],
        )
        self.assertEqual(
            result["open_questions"],
            [
                "What is the project budget?",
                "What is the delivery date?",
            ],
        )


    def test_fictional_guide_assumptions_become_questions(self):
        scope = self.sample_scope()
        scope["assumptions"] = [
            "Editor review process as described in the fictional guide",
            "Verification process for listing appearance as described in the fictional guide",
        ]
        scope["knowledge_gaps"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "Members need to create and publish directory listings. "
                "The editor workflow and listing verification process "
                "have not been confirmed."
            ),
        )

        self.assertEqual(result["assumptions"], [])

        self.assertTrue(
            any(
                "editor-review workflow" in question.lower()
                for question in result["open_questions"]
            )
        )
        self.assertTrue(
            any(
                "verified in the directory" in question.lower()
                for question in result["open_questions"]
            )
        )
        self.assertTrue(
            any(
                "fictional reference material" in gap.lower()
                for gap in result["knowledge_gaps"]
            )
        )

    def test_adds_question_when_approval_details_are_missing(self):
        scope = self.sample_scope()
        scope["open_questions"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "The team wants editors to review listings before publication. "
                "Please ask what review rules and approvals are needed."
            ),
        )

        self.assertIn(
            "What approval rules apply, and who can approve publication?",
            result["open_questions"],
        )

    def test_adds_questions_for_missing_scope_document_and_baseline(self):
        scope = self.sample_scope()
        scope["open_questions"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "The earlier scope document was not provided. "
                "Do not claim that a baseline comparison has been completed."
            ),
        )

        self.assertIn(
            "Please provide the earlier scope document for comparison.",
            result["open_questions"],
        )
        self.assertIn(
            "What approved baseline or previous scope should be used for comparison?",
            result["open_questions"],
        )

    def test_adds_notification_trigger_question_when_unspecified(self):
        scope = self.sample_scope()
        scope["open_questions"] = []

        result = _enforce_transcript_constraints(
            scope,
            "Email notifications are required, but their triggers are unspecified.",
        )

        self.assertIn(
            "Which notification triggers are required?",
            result["open_questions"],
        )

    def test_preserves_explicitly_confirmed_notification_trigger(self):
        scope = self.sample_scope()
        scope["open_questions"] = []

        result = _enforce_transcript_constraints(
            scope,
            "Send email notifications only when an editor approves a listing.",
        )

        self.assertEqual(result["open_questions"], [])

    def test_unconfirmed_capability_assumptions_become_questions_and_gaps(self):
        cases = (
            (
                "The platform allows bulk publication.",
                "We have not confirmed whether the platform allows bulk publication.",
            ),
            (
                "The platform can roll back publications.",
                "The platform rollback capability is unverified.",
            ),
            (
                "The platform supports multilingual listings.",
                "We have not confirmed whether the platform supports multilingual listings.",
            ),
        )

        for assumption, transcript in cases:
            with self.subTest(assumption=assumption):
                scope = self.sample_scope()
                scope["assumptions"] = [assumption]
                scope["knowledge_gaps"] = []

                result = _enforce_transcript_constraints(scope, transcript)

                self.assertEqual(result["assumptions"], [])
                self.assertTrue(
                    any(
                        "can this assumption be confirmed" in question.lower()
                        for question in result["open_questions"]
                    )
                )
                self.assertTrue(
                    any(
                        assumption.rstrip(".").lower() in gap.lower()
                        for gap in result["knowledge_gaps"]
                    )
                )

    def test_preserves_explicitly_confirmed_platform_capabilities(self):
        cases = (
            (
                "The platform allows bulk publication.",
                "The platform allows bulk publication.",
            ),
            (
                "The platform can roll back publications.",
                "The platform can roll back publications.",
            ),
            (
                "The platform supports multilingual listings.",
                "The platform supports multilingual listings.",
            ),
        )

        for assumption, transcript in cases:
            with self.subTest(assumption=assumption):
                scope = self.sample_scope()
                scope["assumptions"] = [assumption]
                scope["knowledge_gaps"] = []

                result = _enforce_transcript_constraints(scope, transcript)

                self.assertEqual(result["assumptions"], [assumption])
                self.assertEqual(result["knowledge_gaps"], [])

    def test_adds_specific_gap_for_explicitly_unverified_capability(self):
        scope = self.sample_scope()
        scope["assumptions"] = []
        scope["knowledge_gaps"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "We have not established whether the current platform supports "
                "multilingual listings."
            ),
        )

        self.assertTrue(
            any(
                "supports multilingual listings" in gap.lower()
                and "not been verified" in gap.lower()
                for gap in result["knowledge_gaps"]
            )
        )


    def test_records_missing_crm_integration_details_as_knowledge_gaps(self):
        scope = self.sample_scope()
        scope["assumptions"] = []
        scope["knowledge_gaps"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "The customer wants directory listing changes synchronized "
                "with their external CRM. No API documentation, credentials, "
                "integration architecture, or platform compatibility "
                "information has been provided."
            ),
        )

        gaps = " ".join(result["knowledge_gaps"]).casefold()

        self.assertIn("crm", gaps)
        self.assertIn("api documentation", gaps)
        self.assertIn("platform compatibility", gaps)

    def test_records_unknown_data_migration_feasibility_as_knowledge_gap(self):
        scope = self.sample_scope()
        scope["assumptions"] = []
        scope["knowledge_gaps"] = []

        result = _enforce_transcript_constraints(
            scope,
            (
                "The customer wants to migrate existing business listings "
                "into the new workflow. The feasibility and details of the "
                "data, including format, count, quality, duplicates, and "
                "migration date, are unknown. Do not assume migration is "
                "feasible until data inspection is complete."
            ),
        )

        gaps = " ".join(result["knowledge_gaps"]).casefold()

        self.assertIn("migration", gaps)
        self.assertIn("feasibility", gaps)

if __name__ == "__main__":
    unittest.main()
