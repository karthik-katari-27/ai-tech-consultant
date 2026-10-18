"""Local tests for the Claude service without calling the real API."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from claude_service import (
    ClaudeConfigurationError,
    DEFAULT_MODEL,
    ask_claude,
)


class ClaudeServiceTests(unittest.TestCase):
    """Test Claude service behavior with a mocked client."""

    def test_blank_question_is_rejected(self) -> None:
        """A blank question fails before the API client is created."""

        with patch("claude_service.Anthropic") as mock_anthropic:
            with self.assertRaisesRegex(
                ValueError, "Question must not be empty."
            ):
                ask_claude("   ")

        mock_anthropic.assert_not_called()

    def test_missing_api_key_raises_configuration_error(self) -> None:
        """A missing API key produces a safe configuration error."""

        with patch.dict(os.environ, {}, clear=True):
            with patch("claude_service.Anthropic") as mock_anthropic:
                with self.assertRaises(ClaudeConfigurationError) as error:
                    ask_claude("How do I update a profile photo?")

        self.assertEqual(
            str(error.exception),
            "ANTHROPIC_API_KEY is not configured.",
        )
        mock_anthropic.assert_not_called()

    def test_returns_text_from_mocked_response(self) -> None:
        """Text blocks are returned without surrounding whitespace."""

        mock_client = Mock()
        mock_client.messages.create.return_value = SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text="  Here is the answer.  "),
                SimpleNamespace(type="tool_use"),
            ]
        )

        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "test-api-key"},
            clear=True,
        ):
            with patch(
                "claude_service.Anthropic",
                return_value=mock_client,
            ) as mock_anthropic:
                result = ask_claude("  How do I update a profile photo?  ")

        self.assertEqual(result, "Here is the answer.")
        mock_anthropic.assert_called_once_with(
            api_key="test-api-key",
            timeout=30.0,
        )
        mock_client.messages.create.assert_called_once_with(
            model=DEFAULT_MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": "How do I update a profile photo?",
                }
            ],
        )

    def test_empty_text_response_raises_error(self) -> None:
        """A response without text is not treated as a successful answer."""

        mock_client = Mock()
        mock_client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(type="tool_use")]
        )

        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "test-api-key"},
            clear=True,
        ):
            with patch(
                "claude_service.Anthropic",
                return_value=mock_client,
            ):
                with self.assertRaisesRegex(
                    RuntimeError, "Claude returned no text response."
                ):
                    ask_claude("Give me an answer.")


if __name__ == "__main__":
    unittest.main()