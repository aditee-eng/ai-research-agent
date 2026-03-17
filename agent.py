from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.messages import HumanMessage, SystemMessage
import config

SYSTEM_PROMPT = """You are an expert AI Research Assistant.
Your job:
1. Research the given topic using web searches (do at least 3 searches)
2. Analyse the results
3. Write a structured Markdown research report

When you need to search, respond EXACTLY like this (nothing else):
SEARCH: your search query here

When you have enough information, respond with the full report starting with:
FINAL REPORT:

The report must follow this structure:
# Research Report: [Topic]
## Executive Summary
## Key Findings
## Detailed Analysis
## Conclusions
## Sources

Rules:
- Do at least 3 searches before writing the report
- Be factual and objective
- Always include sources
"""

class ResearchAgent:
    def __init__(self) -> None:
        config.validate_config()
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        self.search = SerpAPIWrapper(
            serpapi_api_key=config.SERPAPI_API_KEY,
            params={"num": config.NUM_SEARCH_RESULTS},
        )
        Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    def research(self, topic: str) -> dict[str, str]:
        print(f"\n{'='*60}")
        print(f"  🤖 Researching: {topic}")
        print(f"  🆓 Using Groq — model: {config.GROQ_MODEL}")
        print(f"{'='*60}\n")

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Research this topic and write a comprehensive report:\n\n"
                f"Topic: {topic}\n\n"
                f"Start by searching for information. Do at least 3 searches."
            )),
        ]

        search_count = 0
        organic = []

        for i in range(12):
            response = self.llm.invoke(messages)
            reply = response.content.strip()

            if reply.upper().startswith("SEARCH:"):
                query = reply[7:].strip()
                print(f"  🔍 Search {search_count + 1}: {query}")
                try:
                    raw = self.search.results(query)
                    organic = raw.get("organic_results", [])
                    results_text = self._format_results(organic)
                except Exception as exc:
                    results_text = f"Search failed: {exc}"
                search_count += 1
                messages.append(response)
                messages.append(HumanMessage(content=(
                    f"Search results for '{query}':\n\n{results_text}\n\n"
                    f"You have done {search_count} search(es) so far. "
                    f"{'Do more searches or write FINAL REPORT: when ready.' if search_count < 3 else 'You can now write the FINAL REPORT:'}"
                )))

            elif "FINAL REPORT:" in reply.upper():
                idx = reply.upper().find("FINAL REPORT:")
                report = reply[idx + len("FINAL REPORT:"):].strip()
                saved_path = self._save_report(topic, report)
                print(f"\n  ✅ Done! Report saved to: {saved_path}\n")
                return {"report": report, "saved_path": saved_path}

            else:
                messages.append(response)
                messages.append(HumanMessage(content=(
                    "Please either search with: SEARCH: your query\n"
                    "Or write the report starting with: FINAL REPORT:"
                )))

        report = "Research incomplete. Please try again."
        return {"report": report, "saved_path": self._save_report(topic, report)}

    def _format_results(self, organic: list) -> str:
        if not organic:
            return "No results found."
        lines = []
        for i, r in enumerate(organic[:config.NUM_SEARCH_RESULTS], 1):
            lines.append(f"Result {i}:\n  Title: {r.get('title','N/A')}\n  URL: {r.get('link','N/A')}\n  Snippet: {r.get('snippet','N/A')}\n")
        return "\n".join(lines)

    def _save_report(self, topic: str, report: str) -> str:
        safe_topic = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(config.REPORTS_DIR) / f"{safe_topic}_{timestamp}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        return str(filepath.resolve())
