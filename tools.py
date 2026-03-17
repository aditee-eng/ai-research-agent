"""
tools.py
--------
Custom LangChain tools that the agent can invoke:
  1. WebSearchTool      – searches the internet via SerpAPI
  2. TextSummarizerTool – summarises a long block of text using Groq (free LLM)

Each tool is a plain Python class that inherits from LangChain's BaseTool,
which makes it easy for the agent to decide when and how to use each one.
"""

from __future__ import annotations

from typing import Optional, Type

from langchain.tools import BaseTool
from langchain_community.utilities import SerpAPIWrapper
from langchain_groq import ChatGroq          # ← Groq instead of OpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel, Field

import config


# ── Input schemas (used for validation & agent tool-calling) ──────────────────

class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up on the internet.")


class SummarizerInput(BaseModel):
    text: str = Field(description="The raw text content that needs to be summarised.")
    context: Optional[str] = Field(
        default="",
        description="Optional context or topic to guide the summarisation.",
    )


# ── Tool 1: Web Search ────────────────────────────────────────────────────────

class WebSearchTool(BaseTool):
    """
    Searches the internet using SerpAPI and returns the top results as
    a single formatted string the agent can read.
    """

    name: str = "web_search"
    description: str = (
        "Useful for finding up-to-date information on any topic. "
        "Input should be a clear, specific search query. "
        "Returns a list of results with titles, URLs, and short snippets."
    )
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        """Execute the search and format the results."""
        print(f"\n  🔍 Searching the web for: '{query}'")

        # SerpAPIWrapper handles the HTTP call to SerpAPI
        search = SerpAPIWrapper(
            serpapi_api_key=config.SERPAPI_API_KEY,
            params={"num": config.NUM_SEARCH_RESULTS},
        )

        try:
            raw_results = search.results(query)
        except Exception as exc:
            return f"Search failed: {exc}"

        # Pull out the "organic" (non-ad) results
        organic = raw_results.get("organic_results", [])
        if not organic:
            return "No results found. Try a different query."

        # Format each result so the agent can easily read title, URL, and snippet
        lines: list[str] = []
        for i, result in enumerate(organic[: config.NUM_SEARCH_RESULTS], start=1):
            title   = result.get("title", "No title")
            link    = result.get("link", "No URL")
            snippet = result.get("snippet", "No description available.")
            lines.append(
                f"Result {i}:\n"
                f"  Title  : {title}\n"
                f"  URL    : {link}\n"
                f"  Snippet: {snippet}\n"
            )

        return "\n".join(lines)

    async def _arun(self, query: str) -> str:
        """Async version – delegates to the sync implementation for simplicity."""
        return self._run(query)


# ── Tool 2: Text Summariser ───────────────────────────────────────────────────

class TextSummarizerTool(BaseTool):
    """
    Takes a long piece of text and uses Groq (free LLM) to produce a concise summary.
    Useful when the agent has gathered raw content from multiple sources.
    """

    name: str = "text_summarizer"
    description: str = (
        "Useful for condensing large amounts of text into a clear, concise summary. "
        "Input should be the raw text to summarise, plus an optional topic/context string."
    )
    args_schema: Type[BaseModel] = SummarizerInput

    def _run(self, text: str, context: str = "") -> str:
        """Ask Groq to summarise the provided text."""
        print(f"\n  📝 Summarising content" + (f" about '{context}'" if context else "") + "…")

        # Using Groq — completely free, no billing needed
        llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0.2,    # low temperature → more factual summaries
            max_tokens=800,
        )

        prompt = (
            f"You are a research assistant. "
            f"{'Topic: ' + context + chr(10) if context else ''}"
            f"Summarise the following text in 3-5 clear bullet points. "
            f"Focus on the most important facts, findings, and insights.\n\n"
            f"Text to summarise:\n{text[:4000]}"  # cap at 4000 chars to stay within token limits
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    async def _arun(self, text: str, context: str = "") -> str:
        return self._run(text, context)


# ── Tool registry ─────────────────────────────────────────────────────────────

def get_tools() -> list[BaseTool]:
    """Return all tools that the agent is allowed to use."""
    return [
        WebSearchTool(),
        TextSummarizerTool(),
    ]
