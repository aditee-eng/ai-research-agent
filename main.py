"""
main.py
-------
Entry point for the AI Research Agent.

Run this file to start an interactive research session:
    python main.py

Or pass a topic directly as a command-line argument:
    python main.py "Quantum Computing breakthroughs 2024"
"""

from __future__ import annotations

import sys

from agent import ResearchAgent


def print_banner() -> None:
    """Print a welcome banner when the program starts."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║          🔬  AI Research Assistant Agent  🔬             ║
║                                                          ║
║  Powered by LangChain + OpenAI + SerpAPI                 ║
║  Type a research topic and get a full report!            ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_topic_from_user() -> str:
    """
    Prompt the user to type a research topic.
    Keep asking until they provide a non-empty string.
    """
    while True:
        topic = input("📌 Enter a research topic (or 'quit' to exit): ").strip()

        if topic.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! 👋\n")
            sys.exit(0)

        if topic:
            return topic

        print("  ⚠️  Please enter a topic before pressing Enter.\n")


def main() -> None:
    print_banner()

    # ── Initialise the agent once (loads API keys, builds LangChain objects) ──
    try:
        agent = ResearchAgent()
    except EnvironmentError as exc:
        # validate_config() raises EnvironmentError when keys are missing
        print(f"\n{exc}\n")
        sys.exit(1)

    # ── Support one-shot mode: python main.py "my topic" ─────────────────────
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        print(f"  ℹ️  Topic received from command line: {topic}\n")
        result = agent.research(topic)
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(result["report"])
        return

    # ── Interactive loop ──────────────────────────────────────────────────────
    print("  💡 Tip: type 'quit' at any time to exit.\n")

    while True:
        topic = get_topic_from_user()

        result = agent.research(topic)

        # Display the report in the terminal
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(result["report"])
        print(f"\n  💾 Report also saved to: {result['saved_path']}\n")

        # Ask whether the user wants to research another topic
        another = input("🔄 Research another topic? (yes / no): ").strip().lower()
        if another not in ("yes", "y"):
            print("\nThank you for using the AI Research Agent! 👋\n")
            break


if __name__ == "__main__":
    main()
