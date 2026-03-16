"""
agent.py
--------
Defines the ResearchAgent class.

The agent is built on LangChain's OpenAI Functions agent, which lets the LLM
decide *which* tool to call and *when*, based on the user's research topic.

Workflow:
  1. User provides a research topic.
  2. Agent searches the web (multiple queries if needed).
  3. Agent summarises gathered content.
  4. Agent generates a structured Markdown research report.
  5. Report is returned as a string AND saved to disk.
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage

import config
from tools import get_tools


# ── System prompt ─────────────────────────────────────────────────────────────
# This instructs the LLM on its role and how to produce the final report.

SYSTEM_PROMPT = """You are an expert AI Research Assistant. Your job is to:

1. Conduct thorough internet research on the topic provided by the user.
2. Search for information using multiple different search queries to cover the topic from different angles.
3. Summarise the collected information clearly and concisely.
4. Produce a well-structured research report in Markdown format.

When writing the final research report, use this structure:

# Research Report: [Topic]

## Executive Summary
A 2-3 sentence overview of the most important findings.

## Key Findings
Bullet-point list of the most important facts and insights.

## Detailed Analysis
### [Sub-topic 1]
...
### [Sub-topic 2]
...

## Conclusions
What can we conclude from this research?

## Sources
Numbered list of URLs used during research.

---

Guidelines:
- Be factual and objective.
- Use clear, simple language suitable for a general audience.
- Always include sources at the end.
- If you find conflicting information, mention both viewpoints.
- Conduct at least 3 different searches to ensure comprehensive coverage.
"""


class ResearchAgent:
    """
    Wraps LangChain's OpenAI Functions agent with research-specific tools
    and a structured report-generation workflow.
    """

    def __init__(self) -> None:
        # Validate that API keys are present before doing anything
        config.validate_config()

        # ── LLM ───────────────────────────────────────────────────────────────
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )

        # ── Tools the agent may use ───────────────────────────────────────────
        self.tools = get_tools()

        # ── Prompt template ───────────────────────────────────────────────────
        # MessagesPlaceholder("agent_scratchpad") is required by LangChain's
        # OpenAI Functions agent to store intermediate reasoning steps.
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # ── Build the agent ───────────────────────────────────────────────────
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        # AgentExecutor runs the agent in a loop until it produces a final answer
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,           # prints each step so users can follow along
            max_iterations=10,      # safety cap: never loop more than 10 times
            handle_parsing_errors=True,
        )

        # Ensure the reports output directory exists
        Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    # ── Public API ─────────────────────────────────────────────────────────────

    def research(self, topic: str) -> dict[str, str]:
        """
        Run a full research session on *topic*.

        Returns a dict with:
          - "report"    : the full Markdown report string
          - "saved_path": absolute path to the saved .md file
        """
        print(f"\n{'='*60}")
        print(f"  🤖 Starting research on: {topic}")
        print(f"{'='*60}\n")

        # Build the user message that kicks off the agent
        user_message = (
            f"Please research the following topic thoroughly and produce a "
            f"comprehensive, structured research report:\n\n**Topic:** {topic}\n\n"
            f"Make sure to:\n"
            f"- Search for information using at least 3 different queries\n"
            f"- Cover multiple aspects of the topic\n"
            f"- Include recent and relevant sources\n"
            f"- Format the final output as a complete Markdown research report"
        )

        # Invoke the agent — it will loop, calling tools as needed
        result = self.executor.invoke({"input": user_message})

        report: str = result.get("output", "No report generated.")

        # Save the report to disk
        saved_path = self._save_report(topic, report)

        print(f"\n{'='*60}")
        print(f"  ✅ Research complete!")
        print(f"  📄 Report saved to: {saved_path}")
        print(f"{'='*60}\n")

        return {"report": report, "saved_path": saved_path}

    # ── Private helpers ────────────────────────────────────────────────────────

    def _save_report(self, topic: str, report: str) -> str:
        """
        Write the report to a .md file in the reports directory.
        The filename is derived from the topic and the current timestamp
        so that multiple reports on the same topic don't overwrite each other.
        """
        # Turn the topic into a safe filename fragment
        safe_topic = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename   = f"{safe_topic}_{timestamp}.md"
        filepath   = Path(config.REPORTS_DIR) / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        return str(filepath.resolve())
