"""Minimal FastAPI service for the Knowledge Brain milestone."""
from claude_service import (
    ClaudeConfigurationError,
    ClaudeServiceError,
    ask_claude,
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from search_articles import ArticleDataError, search_articles


app = FastAPI(
    title="Knowledge Brain API",
    description="A starter API with no connected knowledge source or AI features.",
)


class AskRequest(BaseModel):
    """The JSON body accepted by the /ask endpoint."""

    question: str


@app.get("/health")
def health() -> dict[str, str]:
    """Report that this API is running."""

    return {"status": "healthy"}


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    """Search local fictional test articles; it does not use AI or real support data."""

    question = request.question.strip()
    if not question:
        # A blank string (including spaces only) is not a valid question.
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        articles = search_articles(question)
    except ArticleDataError as error:
        raise HTTPException(
            status_code=503,
            detail="Article search is temporarily unavailable. Please try again later.",
        ) from error

    return {
        "response_type": "fictional_test_article_search",
        "source_notice": (
            "All results are fictional test data and are not verified "
            "Brilliant Directories support content."
        ),
        "question": question,
        "match_count": len(articles),
        "results": articles,
    }

@app.post("/ask-claude")
def ask_with_claude(request: AskRequest) -> dict[str, object]:
    """Answer using Claude and matching fictional reference articles."""

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    try:
        articles = search_articles(question)
    except ArticleDataError as error:
        raise HTTPException(
            status_code=503,
            detail="Article search is temporarily unavailable. Please try again later.",
        ) from error

    if not articles:
        return {
            "response_type": "no_matching_reference_articles",
            "source_notice": (
                "The local dataset contains fictional test data, "
                "not verified support documentation."
            ),
            "question": question,
            "answer": (
                "No matching reference articles were found. "
                "A reliable answer cannot be provided from the "
                "available reference material."
            ),
            "sources": [],
        }

    try:
        answer = ask_claude(question, articles=articles)
    except ClaudeConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail="Claude service is not configured. Please try again later.",
        ) from error
    except ClaudeServiceError as error:
        raise HTTPException(
            status_code=502,
            detail="Claude service is temporarily unavailable. Please try again later.",
        ) from error

    return {
        "response_type": "claude_answer_with_fictional_context",
        "source_notice": (
            "The reference articles are fictional test data and are not "
            "verified Brilliant Directories support content."
        ),
        "question": question,
        "answer": answer,
        "sources": [
            {
                "title": article["title"],
                "url": article["url"],
                "source_type": article["source_type"],
            }
            for article in articles
        ],
    }
