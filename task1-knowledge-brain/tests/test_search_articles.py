"""Unit tests for loading the local article dataset without touching real data."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from search_articles import ArticleDataError, load_articles, search_articles


class LoadArticlesTests(unittest.TestCase):
    """Test load_articles with temporary files and safe mocked failures."""

    def test_valid_json_list_loads_successfully(self) -> None:
        """A temporary JSON array is returned as the same Python list."""

        expected_articles = [
            {
                "id": "temporary-article",
                "title": "Temporary article",
                "url": "https://example.test/temporary-article",
                "text": "This is temporary fictional test data.",
                "source_type": "fictional_test_data",
            },
            {
                "id": "another-temporary-article",
                "title": "Another temporary article",
                "url": "https://example.test/another-temporary-article",
                "text": "This is another temporary fictional test article.",
                "source_type": "fictional_test_data",
            },
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "articles.json"
            temporary_path.write_text(json.dumps(expected_articles), encoding="utf-8")

            with patch("search_articles.DATA_PATH", temporary_path):
                loaded_articles = load_articles()

        self.assertEqual(loaded_articles, expected_articles)

    def test_missing_file_raises_article_data_error(self) -> None:
        """A temporary path that does not exist returns the safe custom error."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing-articles.json"

            with patch("search_articles.DATA_PATH", missing_path):
                with self.assertRaises(ArticleDataError) as raised_error:
                    load_articles()

        self.assertEqual(str(raised_error.exception), "Article data is unavailable.")

    def test_malformed_json_raises_article_data_error(self) -> None:
        """A temporary file with invalid JSON returns the safe custom error."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "malformed.json"
            temporary_path.write_text("{not valid JSON", encoding="utf-8")

            with patch("search_articles.DATA_PATH", temporary_path):
                with self.assertRaises(ArticleDataError) as raised_error:
                    load_articles()

        self.assertEqual(str(raised_error.exception), "Article data is unavailable.")

    def test_non_list_json_root_raises_article_data_error(self) -> None:
        """A JSON object is rejected because the dataset must be a list."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "object-root.json"
            temporary_path.write_text('{"id": "not-a-list"}', encoding="utf-8")

            with patch("search_articles.DATA_PATH", temporary_path):
                with self.assertRaises(ArticleDataError) as raised_error:
                    load_articles()

        self.assertEqual(str(raised_error.exception), "Article data is unavailable.")

    def test_article_missing_required_field_raises_error(self) -> None:
        """An article missing a required field is rejected."""

        invalid_articles = [
            {
                "id": "temporary-article",
                "title": "Temporary article",
                "url": "https://example.test/temporary-article",
                "source_type": "fictional_test_data",
            }
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "missing-field.json"
            temporary_path.write_text(
                json.dumps(invalid_articles), encoding="utf-8"
            )

            with patch("search_articles.DATA_PATH", temporary_path):
                with self.assertRaises(ArticleDataError):
                    load_articles()

    def test_article_with_incorrect_field_type_raises_error(self) -> None:
        """An article with a non-string title is rejected."""

        invalid_articles = [
            {
                "id": "temporary-article",
                "title": 123,
                "url": "https://example.test/temporary-article",
                "text": "Temporary fictional article.",
                "source_type": "fictional_test_data",
            }
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "wrong-type.json"
            temporary_path.write_text(
                json.dumps(invalid_articles), encoding="utf-8"
            )

            with patch("search_articles.DATA_PATH", temporary_path):
                with self.assertRaises(ArticleDataError):
                    load_articles()

    def test_non_dictionary_article_raises_error(self) -> None:
        """A list item that is not an article dictionary is rejected."""

        invalid_articles = ["not-an-article"]

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory) / "invalid-record.json"
            temporary_path.write_text(
                json.dumps(invalid_articles), encoding="utf-8"
            )

            with patch("search_articles.DATA_PATH", temporary_path):
                with self.assertRaises(ArticleDataError):
                    load_articles()

    def test_unreadable_file_error_raises_article_data_error(self) -> None:
        """A mocked permission error is safely translated without changing any file."""

        unreadable_path = Mock()
        unreadable_path.open.side_effect = PermissionError("Permission denied")

        with patch("search_articles.DATA_PATH", unreadable_path):
            with self.assertRaises(ArticleDataError) as raised_error:
                load_articles()

        self.assertEqual(str(raised_error.exception), "Article data is unavailable.")


class SearchArticlesTests(unittest.TestCase):
    """Regression tests for supported and unsupported search queries."""

    def test_draft_review_paraphrase_finds_listing_article(self) -> None:
        """A draft-review question should retrieve the listing guide."""

        results = search_articles(
            "How are draft listings reviewed before publication?"
        )
        result_urls = {result["url"] for result in results}

        self.assertIn(
            "https://example.test/support/publish-listing",
            result_urls,
        )

    def test_avatar_synonym_finds_profile_photo_article(self) -> None:
        """The word avatar should match the profile photo guide."""

        results = search_articles("How can I change my avatar?")
        result_urls = {result["url"] for result in results}

        self.assertIn(
            "https://example.test/support/profile-photo",
            result_urls,
        )

    def test_unsupported_phone_question_returns_no_results(self) -> None:
        """A question about an unavailable phone number should abstain."""

        results = search_articles(
            "What is the official support phone number?"
        )

        self.assertEqual(results, [])

    def test_ambiguous_product_question_returns_no_results(self) -> None:
        """A vague product question should not return unrelated articles."""

        results = search_articles("Can you help me with the product?")

        self.assertEqual(results, [])

    def test_multiple_topics_finds_both_expected_articles(self) -> None:
        """A question covering two topics should find both relevant guides."""

        results = search_articles(
            "How do I publish a listing, and where can I find "
            "information about email notifications?"
        )
        result_urls = {result["url"] for result in results}

        self.assertIn(
            "https://example.test/support/publish-listing",
            result_urls,
        )
        self.assertIn(
            "https://example.test/support/email-notifications",
            result_urls,
        )


if __name__ == "__main__":
    unittest.main()
