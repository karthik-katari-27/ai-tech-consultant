"""Search the local fictional article dataset with simple keyword matching."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# This path is based on this file's location, not the PowerShell working directory.
DATA_PATH = Path(__file__).parent / "data" / "sample_articles.json"

# These common words do not help identify the subject of a support question.
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "the",
    "to",
    "what",
    "with",
    "do",
    "can",
    "you",
    "me",
    "my",
    "help",
    "product",
    "support",
}

TOKEN_ALIASES = {
    "listings": "listing",
    "reviewed": "review",
    "reviews": "review",
    "avatar": "photo",
    "avatars": "photo",
}


class ArticleDataError(Exception):
    """Raised when the local article dataset cannot be used safely."""


def keywords(text: str) -> set[str]:
    """Return normalized, lowercase, non-stop-word tokens."""

    tokens = re.findall(r"[a-z0-9]+", text.lower())

    return {
        TOKEN_ALIASES.get(token, token)
        for token in tokens
        if token not in STOP_WORDS
    }

def load_articles() -> list[dict[str, Any]]:
    """Load and validate the local fictional article dataset."""

    try:
        with DATA_PATH.open(encoding="utf-8") as file:
            articles = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ArticleDataError("Article data is unavailable.") from error

    if not isinstance(articles, list):
        raise ArticleDataError("Article data is unavailable.")

    required_fields = ("id", "title", "url", "text", "source_type")

    for article in articles:
        if not isinstance(article, dict):
            raise ArticleDataError("Article data is unavailable.")

        for field in required_fields:
            value = article.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ArticleDataError("Article data is unavailable.")

    return articles


def search_articles(question: str, limit: int = 3) -> list[dict[str, Any]]:
    """Return the highest-scoring fictional test articles for a question.

    A matching keyword in a title receives three points. A matching keyword
    found only in article text receives one point. This deliberately favours
    titles while keeping the scoring simple and easy to inspect.
    """

    query_keywords = keywords(question)
    if not query_keywords or limit <= 0:
        return []

    matches: list[dict[str, Any]] = []
    for article in load_articles():
        title_keywords = keywords(str(article.get("title", "")))
        text_keywords = keywords(str(article.get("text", "")))

        title_matches = query_keywords & title_keywords
        text_only_matches = (query_keywords & text_keywords) - title_matches
        score = (3 * len(title_matches)) + len(text_only_matches)

        if score < 2:
            continue

        # Keep the source label visible; this data is fictional test data,
        # not verified support content.
        matches.append(
            {
                "id": article.get("id"),
                "title": article.get("title"),
                "url": article.get("url"),
                "text": article.get("text"),
                "source_type": article.get("source_type"),
                "score": score,
            }
        )

    return sorted(matches, key=lambda match: (-match["score"], match["title"]))[:limit]


if __name__ == "__main__":
    example_question = "How do I publish a directory listing?"
    example_results = search_articles(example_question)

    print("Fictional test-data matches (not verified support articles):")
    print(json.dumps(example_results, indent=2))
