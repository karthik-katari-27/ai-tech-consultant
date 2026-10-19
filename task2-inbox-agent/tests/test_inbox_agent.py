
"""Tests for the human-reviewed Inbox Agent."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Make the sibling inbox_agent.py module importable during test discovery.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from inbox_agent import (
    InboxAgentError,
    _parse_classification,
    classify_email,
    process_email,
)


class InboxAgentTests(unittest.TestCase):
    """Test the Inbox Agent with mocked model and API responses."""

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
            "score": 5,
        }

    def test_empty_email_is_rejected(self):
        with patch("inbox_agent._ask_local_model") as mock_model:
            with self.assertRaisesRegex(
                ValueError,
                "Email subject and body must not both be empty.",
            ):
                process_email({"subject": " ", "body": " "})

        mock_model.assert_not_called()

    def test_classifies_email_from_model_json(self):
        model_result = json.dumps(
            {
                "category": "listing_publishing",
                "summary": "The customer asks how to publish a listing.",
                "urgency": "normal",
            }
        )

        with patch(
            "inbox_agent._ask_local_model",
            return_value=model_result,
        ) as mock_model:
            result = classify_email(
                "Publishing help",
                "How do I publish my directory listing?",
            )

        self.assertEqual(result["category"], "listing_publishing")
        self.assertEqual(result["urgency"], "normal")
        self.assertIn("publish a listing", result["summary"])
        prompt = mock_model.call_args.args[0]
        self.assertIn("Publishing help", prompt)
        self.assertIn("How do I publish my directory listing?", prompt)

    def test_process_email_returns_draft_and_requires_review(self):
        classification = json.dumps(
            {
                "category": "listing_publishing",
                "summary": "The customer needs publishing instructions.",
                "urgency": "normal",
            }
        )
        draft = (
            "Please review your draft, choose Publish, and verify "
            "that the listing appears in the sample directory."
        )
        article = self.sample_article()
        search_response = {
            "results": [article],
            "source_notice": "Fictional test articles only.",
        }

        with (
            patch(
                "inbox_agent._ask_local_model",
                side_effect=[classification, draft],
            ) as mock_model,
            patch(
                "inbox_agent._post_json",
                return_value=search_response,
            ) as mock_post,
        ):
            result = process_email(
                {
                    "subject": "Publishing my listing",
                    "body": "How do I publish my directory listing?",
                }
            )

        self.assertEqual(
            result["status"],
            "draft_pending_human_review",
        )
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["sent"])
        self.assertEqual(result["draft_reply"], draft)
        self.assertEqual(
            result["classification"]["category"],
            "listing_publishing",
        )
        self.assertEqual(
            result["sources"][0]["url"],
            "https://example.test/support/publish-listing",
        )
        self.assertEqual(
            result["source_notice"],
            "Fictional test articles only.",
        )

        mock_post.assert_called_once()
        self.assertTrue(mock_post.call_args.args[0].endswith("/ask"))
        self.assertEqual(mock_model.call_count, 2)

    def test_no_matching_articles_returns_safe_generic_draft(self):
        classification = json.dumps(
            {
                "category": "other",
                "summary": "The customer's request needs review.",
                "urgency": "normal",
            }
        )

        with (
            patch(
                "inbox_agent._ask_local_model",
                return_value=classification,
            ) as mock_model,
            patch(
                "inbox_agent._post_json",
                return_value={
                    "results": [],
                    "source_notice": "No matching references.",
                },
            ),
        ):
            result = process_email(
                {
                    "subject": "Unusual request",
                    "body": "Can you help with this request?",
                }
            )

        self.assertEqual(result["sources"], [])
        self.assertIn("verify", result["draft_reply"].lower())
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["sent"])
        mock_model.assert_called_once()


    def test_classification_accepts_json_in_markdown_fences(self):
        """Valid JSON wrapped in Markdown code fences is accepted."""

        model_response = (
            '```json\n'
            '{\n'
            '  "category": "account_profile",\n'
            '  "summary": "The customer wants to update their profile.",\n'
            '  "urgency": "low"\n'
            '}\n'
            '```'
        )

        result = _parse_classification(model_response)

        self.assertEqual(result["category"], "account_profile")
        self.assertEqual(result["summary"], "The customer wants to update their profile.")
        self.assertEqual(result["urgency"], "low")


    def test_invalid_classification_json_is_rejected(self):
        with patch(
            "inbox_agent._ask_local_model",
            return_value="not valid JSON",
        ):
            with self.assertRaises(InboxAgentError):
                classify_email(
                    "Account question",
                    "I need help with my account.",
                )


if __name__ == "__main__":
    unittest.main()