
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


if __name__ == "__main__":
    unittest.main()