"""Automated tests for the local Knowledge Brain FastAPI application."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from search_articles import ArticleDataError


class KnowledgeBrainApiTests(unittest.TestCase):
    """Test one API behavior at a time using the local FastAPI application."""

    def setUp(self) -> None:
        # TestClient calls the app in-process; it does not start a real web server.
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def test_health_returns_healthy_status(self) -> None:
        """The health endpoint confirms that the service is available."""

        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_matching_question_returns_expected_fictional_article(self) -> None:
        """A directory-listing question finds the matching fictional article."""

        response = self.client.post(
            "/ask",
            json={"question": "How do I publish a directory listing?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["match_count"], 1)
        self.assertEqual(len(body["results"]), 1)
        self.assertEqual(body["results"][0]["id"], "fictional-directory-listing")

    def test_unrelated_question_returns_no_results(self) -> None:
        """A question with no matching keywords returns an empty result list."""

        response = self.client.post(
            "/ask",
            json={"question": "How do I configure airplane navigation?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["match_count"], 0)
        self.assertEqual(body["results"], [])

    def test_empty_question_returns_bad_request(self) -> None:
        """An empty question keeps the API's existing validation behavior."""

        response = self.client.post("/ask", json={"question": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Question must not be empty."})

    def test_spaces_only_question_returns_bad_request(self) -> None:
        """A question containing only spaces is also invalid."""

        response = self.client.post("/ask", json={"question": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Question must not be empty."})

    @patch("main.search_articles", side_effect=ArticleDataError("Article data is unavailable."))
    def test_unavailable_article_data_returns_service_unavailable(self, mock_search) -> None:
        """Known local-data failures return a safe HTTP 503 response."""

        response = self.client.post(
            "/ask",
            json={"question": "How do I publish a directory listing?"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"detail": "Article search is temporarily unavailable. Please try again later."},
        )
        mock_search.assert_called_once_with("How do I publish a directory listing?")

    @patch(
        "main.search_articles",
        side_effect=ArticleDataError(
            "C:\\private\\data\\sample_articles.json caused JSONDecodeError"
        ),
    )
    def test_data_error_response_hides_internal_details(self, mock_search) -> None:
        """API users receive no paths or parser details when article data fails."""

        response = self.client.post(
            "/ask",
            json={"question": "How do I publish a directory listing?"},
        )

        self.assertEqual(response.status_code, 503)
        detail = response.json()["detail"]
        self.assertEqual(detail, "Article search is temporarily unavailable. Please try again later.")
        self.assertNotIn("sample_articles.json", detail)
        self.assertNotIn("JSONDecodeError", detail)
        self.assertNotIn("C:\\private", detail)
        mock_search.assert_called_once()

    @patch("main.search_articles", side_effect=ArticleDataError("Article data is unavailable."))
    def test_empty_question_validation_runs_before_article_search(self, mock_search) -> None:
        """Blank input keeps its HTTP 400 response even when data is unavailable."""

        response = self.client.post("/ask", json={"question": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Question must not be empty."})
        mock_search.assert_not_called()

    def test_results_are_labelled_as_fictional_test_data(self) -> None:
        """Returned records and the API response identify data as fictional."""

        response = self.client.post(
            "/ask",
            json={"question": "How do I publish a directory listing?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("fictional test data", body["source_notice"].lower())
        self.assertIn("not verified", body["source_notice"].lower())
        self.assertTrue(body["results"], "Expected at least one fictional test result.")

        for article in body["results"]:
            self.assertEqual(article["source_type"], "fictional_test_data")


if __name__ == "__main__":
    unittest.main()
