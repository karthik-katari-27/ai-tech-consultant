"""Automated tests for the local Knowledge Brain FastAPI application."""
from local_ai_service import LocalAIServiceError
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
import main
from claude_service import ClaudeConfigurationError, ClaudeServiceError
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


class AskClaudeEndpointTests(unittest.TestCase):
    """Test /ask-claude without making live API requests."""

    def setUp(self):
        self.client = TestClient(main.app)

    def sample_articles(self):
        return [
            {
                "id": "test-article-1",
                "title": "Fictional Profile Guide",
                "url": "https://example.test/profile-guide",
                "text": "This is fictional profile guidance.",
                "source_type": "fictional_test_data",
                "score": 3,
            }
        ]

    def test_success_returns_answer_and_sources(self):
        articles = self.sample_articles()
        question = "How do I update my profile?"
        answer = "The fictional reference describes profile updates."

        with (
            patch("main.search_articles", return_value=articles),
            patch("main.ask_claude", return_value=answer) as mock_claude,
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": question},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], answer)
        self.assertEqual(data["question"], question)
        self.assertEqual(
            data["response_type"],
            "claude_answer_with_fictional_context",
        )
        self.assertIn("not verified", data["source_notice"])
        self.assertEqual(
            data["sources"],
            [
                {
                    "title": "Fictional Profile Guide",
                    "url": "https://example.test/profile-guide",
                    "source_type": "fictional_test_data",
                }
            ],
        )
        mock_claude.assert_called_once_with(
            question,
            articles=articles,
        )

    def test_blank_question_returns_400(self):
        with (
            patch("main.search_articles") as mock_search,
            patch("main.ask_claude") as mock_claude,
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": "   "},
            )

        self.assertEqual(response.status_code, 400)
        mock_search.assert_not_called()
        mock_claude.assert_not_called()

    def test_no_matching_articles_skips_claude(self):
        with (
            patch("main.search_articles", return_value=[]),
            patch("main.ask_claude") as mock_claude,
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": "unrelated topic"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["response_type"],
            "no_matching_reference_articles",
        )
        self.assertEqual(data["sources"], [])
        mock_claude.assert_not_called()

    def test_missing_claude_configuration_returns_503(self):
        with (
            patch(
                "main.search_articles",
                return_value=self.sample_articles(),
            ),
            patch(
                "main.ask_claude",
                side_effect=ClaudeConfigurationError(
                    "ANTHROPIC_API_KEY is not configured."
                ),
            ),
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": "How do I update my profile?"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn("not configured", response.json()["detail"])
        self.assertNotIn("ANTHROPIC_API_KEY", response.json()["detail"])

    def test_claude_failure_returns_502(self):
        with (
            patch(
                "main.search_articles",
                return_value=self.sample_articles(),
            ),
            patch(
                "main.ask_claude",
                side_effect=ClaudeServiceError(
                    "Internal diagnostic detail."
                ),
            ),
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": "How do I update my profile?"},
            )

        self.assertEqual(response.status_code, 502)
        self.assertNotIn(
            "Internal diagnostic detail",
            response.json()["detail"],
        )

    def test_article_data_error_returns_503(self):
        with (
            patch(
                "main.search_articles",
                side_effect=ArticleDataError(
                    "Internal article data detail."
                ),
            ),
            patch("main.ask_claude") as mock_claude,
        ):
            response = self.client.post(
                "/ask-claude",
                json={"question": "How do I update my profile?"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertNotIn(
            "Internal article data detail",
            response.json()["detail"],
        )
        mock_claude.assert_not_called()

class AskLocalEndpointTests(unittest.TestCase):
    """Test /ask-local without calling a real Ollama server."""

    def setUp(self):
        self.client = TestClient(main.app)

    def sample_articles(self):
        return [
            {
                "id": "fictional-directory-listing",
                "title": "Fictional Guide: Publishing a Directory Listing",
                "url": "https://example.test/support/publish-listing",
                "text": (
                    "This is fictional test data. An editor reviews a "
                    "draft listing, chooses Publish, and verifies that "
                    "it appears in a sample directory."
                ),
                "source_type": "fictional_test_data",
                "score": 5,
            }
        ]

    def test_success_returns_answer_and_sources(self):
        articles = self.sample_articles()
        question = "How do I publish a directory listing?"
        answer = (
            "Review the draft, choose Publish, and verify the listing."
        )

        with (
            patch("main.search_articles", return_value=articles),
            patch(
                "main.ask_local_model",
                return_value=answer,
            ) as mock_local_ai,
        ):
            response = self.client.post(
                "/ask-local",
                json={"question": question},
            )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["answer"], answer)
        self.assertEqual(data["question"], question)
        self.assertEqual(
            data["response_type"],
            "local_ai_answer_with_fictional_context",
        )
        self.assertIn("not verified", data["source_notice"])
        self.assertEqual(
            data["sources"],
            [
                {
                    "title": (
                        "Fictional Guide: Publishing a Directory Listing"
                    ),
                    "url": "https://example.test/support/publish-listing",
                    "source_type": "fictional_test_data",
                }
            ],
        )

        mock_local_ai.assert_called_once_with(
            question,
            articles=articles,
        )

    def test_blank_question_returns_400(self):
        with (
            patch("main.search_articles") as mock_search,
            patch("main.ask_local_model") as mock_local_ai,
        ):
            response = self.client.post(
                "/ask-local",
                json={"question": "   "},
            )

        self.assertEqual(response.status_code, 400)
        mock_search.assert_not_called()
        mock_local_ai.assert_not_called()

    def test_no_matching_articles_skips_local_model(self):
        with (
            patch("main.search_articles", return_value=[]),
            patch("main.ask_local_model") as mock_local_ai,
        ):
            response = self.client.post(
                "/ask-local",
                json={"question": "unrelated topic"},
            )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(
            data["response_type"],
            "no_matching_reference_articles",
        )
        self.assertEqual(data["sources"], [])
        mock_local_ai.assert_not_called()

    def test_local_service_failure_returns_502(self):
        with (
            patch(
                "main.search_articles",
                return_value=self.sample_articles(),
            ),
            patch(
                "main.ask_local_model",
                side_effect=LocalAIServiceError(
                    "Internal diagnostic detail."
                ),
            ),
        ):
            response = self.client.post(
                "/ask-local",
                json={"question": "How do I publish a directory listing?"},
            )

        self.assertEqual(response.status_code, 502)
        self.assertNotIn(
            "Internal diagnostic detail",
            response.json()["detail"],
        )

    def test_article_data_error_returns_503(self):
        with (
            patch(
                "main.search_articles",
                side_effect=ArticleDataError(
                    "Internal article data detail."
                ),
            ),
            patch("main.ask_local_model") as mock_local_ai,
        ):
            response = self.client.post(
                "/ask-local",
                json={"question": "How do I publish a listing?"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertNotIn(
            "Internal article data detail",
            response.json()["detail"],
        )
        mock_local_ai.assert_not_called()


if __name__ == "__main__":
    unittest.main()
