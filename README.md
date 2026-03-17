# 🔬 AI Research Assistant Agent

An intelligent research agent that **searches the internet, analyses multiple sources, and generates a structured research report** on any topic — all from a single Python command.

Built with **LangChain**, **Groq**, and **SerpAPI**.

---

## ✨ Features

- 🔍 **Multi-query web search** — automatically performs several searches to cover a topic from different angles
- 📝 **Automatic summarisation** — condenses raw search results into clear bullet points
- 📄 **Structured Markdown reports** — outputs a professional report with headings, findings, analysis, conclusions, and sources
- 💾 **Auto-save** — every report is saved to the `reports/` directory with a timestamped filename
- 🔄 **Interactive loop** — research multiple topics in one session
- ⚡ **CLI one-shot mode** — pass a topic directly as a command-line argument

---

## 🗂️ Project Structure

```
ai-research-agent/
│
├── main.py              # Entry point — run this to start the agent
├── agent.py             # ResearchAgent class (LangChain agent setup & workflow)
├── tools.py             # Custom LangChain tools: WebSearchTool, TextSummarizerTool
├── config.py            # Configuration & environment variable loading
│
├── requirements.txt     # Python dependencies
├── .env.example         # Template for your API keys (copy → .env)
├── .gitignore           # Files Git should never track
├── example_prompts.md   # Ready-to-use research topics for testing
└── README.md            # This file
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-research-agent.git
cd ai-research-agent
```

### 2. Create a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API keys

```bash
cp .env.example .env
```

Open `.env` in any text editor and fill in your keys:

```env
OPENAI_API_KEY=sk-...          # https://platform.openai.com/api-keys
SERPAPI_API_KEY=...            # https://serpapi.com/manage-api-key
```

> **Free tiers available:**  
> - OpenAI offers $5 in free credits for new accounts.  
> - SerpAPI offers 100 free searches per month on its free plan.

### 5. Run the agent

**Interactive mode** (recommended for beginners):

```bash
python main.py
```

You will see a prompt asking for a research topic:

```
📌 Enter a research topic (or 'quit' to exit): Quantum computing breakthroughs 2024
```

**One-shot CLI mode:**

```bash
python main.py "Impact of AI on the job market"
```

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | — | Your OpenAI API key |
| `SERPAPI_API_KEY` | ✅ Yes | — | Your SerpAPI key |
| `OPENAI_MODEL` | No | `gpt-4o` | LLM model (`gpt-4o`, `gpt-3.5-turbo`, …) |
| `MAX_TOKENS` | No | `2000` | Max tokens per LLM response |
| `TEMPERATURE` | No | `0.3` | LLM temperature (0 = precise, 1 = creative) |
| `NUM_SEARCH_RESULTS` | No | `5` | Web results fetched per query |
| `REPORTS_DIR` | No | `reports` | Directory for saved reports |

---

## 📋 Example Output

After running the agent on `"Quantum computing breakthroughs 2024"`, you get a Markdown report like:

```markdown
# Research Report: Quantum Computing Breakthroughs 2024

## Executive Summary
Quantum computing reached several major milestones in 2024, with Google, IBM,
and a number of startups demonstrating significant advances in qubit stability
and error correction...

## Key Findings
- Google's Willow chip achieved a 105-qubit milestone with improved error rates
- IBM expanded its Quantum Network to over 400 partners worldwide
- Error correction techniques advanced significantly, bringing fault-tolerant
  quantum computing closer to reality
...

## Sources
1. https://blog.google/technology/research/google-willow-quantum-chip/
2. https://newsroom.ibm.com/quantum-computing
...
```

Reports are saved automatically to `reports/quantum_computing_breakthroughs_2024_20241215_143022.md`.

---

## 🧠 How It Works

```
User Input (topic)
       │
       ▼
  ResearchAgent
       │
       ├──► WebSearchTool ──► SerpAPI ──► formatted search results
       │         (called 3+ times with different queries)
       │
       ├──► TextSummarizerTool ──► OpenAI LLM ──► bullet-point summaries
       │
       └──► Final report generation ──► OpenAI LLM ──► Markdown report
                                                │
                                         saved to disk
```

1. **`main.py`** — starts the program and manages the user interaction loop.
2. **`config.py`** — loads `.env` and validates that API keys are present.
3. **`tools.py`** — defines `WebSearchTool` (SerpAPI) and `TextSummarizerTool` (LLM).
4. **`agent.py`** — wires everything together using LangChain's OpenAI Functions agent, which autonomously decides which tool to call and when.

---

## 🛠️ Customisation Tips

| Goal | What to change |
|---|---|
| Use a cheaper model | Set `OPENAI_MODEL=gpt-3.5-turbo` in `.env` |
| Longer / shorter reports | Adjust `MAX_TOKENS` in `.env` |
| More search results | Increase `NUM_SEARCH_RESULTS` in `.env` |
| Change report format | Edit `SYSTEM_PROMPT` in `agent.py` |
| Add a new tool | Create a class in `tools.py` and add it to `get_tools()` |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `langchain` | Agent framework and tool orchestration |
| `langchain-openai` | OpenAI LLM integration |
| `langchain-community` | SerpAPI wrapper |
| `openai` | OpenAI Python SDK |
| `google-search-results` | SerpAPI Python client |
| `python-dotenv` | `.env` file loading |
| `pydantic` | Tool input validation |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 💬 Support

If you run into issues:
- Check that your `.env` file exists and both API keys are filled in.
- Make sure your virtual environment is activated before running `pip install`.
- Consult `example_prompts.md` for tested research topics.
- Open a GitHub Issue with the error message and your Python version.
