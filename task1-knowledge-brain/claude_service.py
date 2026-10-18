"""A small service for calling Claude through the Anthropic API."""

import os

from anthropic import Anthropic


DEFAULT_MODEL = "claude-sonnet-5"


class ClaudeConfigurationError(RuntimeError):
    """Raised when Claude cannot be configured safely."""


def ask_claude(question: str) -> str:
    """Send a question to Claude and return its text response.

    No API request is made when this module is imported.
    A configured API key is required when this function is called.
    """

    question = question.strip()

    if not question:
        raise ValueError("Question must not be empty.")

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key or not api_key.strip():
        raise ClaudeConfigurationError(
            "ANTHROPIC_API_KEY is not configured."
        )

    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL).strip()

    if not model:
        model = DEFAULT_MODEL

    client = Anthropic(
        api_key=api_key,
        timeout=30.0,
    )

    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
    )

    text_parts = [
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]

    answer = "\n".join(text_parts).strip()

    if not answer:
        raise RuntimeError("Claude returned no text response.")

    return answer