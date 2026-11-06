# AI Multiple Agent — LangGraph

A Python agent built with **LangGraph** that plans which tool to call, asks a human for approval, executes the tool through an **MCP (Model Context Protocol)** server, and then writes a natural-language answer.

This is the LangGraph + MCP version of [ai-multiple-agent](https://github.com/mishraabhishek11/ai-multiple-agent).

---

## Features

- **Planner node** — an LLM picks exactly one next tool (or `FINISH`) from the tools discovered on the MCP server.
- **Human-in-the-loop approval** — every tool call pauses the graph with LangGraph's `interrupt()` until you type `yes` or `no`.
- **MCP tool server** — tools are served by a local [FastMCP](https://gofastmcp.com) server and discovered dynamically at startup.
- **Step limit** — the loop stops after `max_steps` tool calls (default `5`).
- **Checkpointing** — `InMemorySaver` stores graph state per `thread_id`, which is what makes pause/resume work.
- **OpenAI-compatible LLM** — works with Ollama, OpenAI or any compatible endpoint.

## Available tools

Defined in `agent/server.py`:

| Tool                | Description                                               |
| ------------------- | --------------------------------------------------------- |
| `current_time`      | Returns the current date and time (`dd-mm-YYYY HH:MM:SS`) |
| `roll_dice`         | Rolls a six-sided die                                     |
| `generate_password` | Generates a secure random password (`length`, default 12) |

## How it works

```
START → planner ──FINISH──────────────────────────┐
           ▲  └─tool──→ approval ──no──────────────┤
           │                └─yes─→ tool            │
           │                          │             ▼
           └──── continue ────────────┤          answer → END
                                      └─ max_steps ─┘
```

1. `main.py` starts the MCP server, discovers its tools and builds the graph.
2. **planner** asks the LLM for the next action given the request, completed actions and observations.
3. If the planner returns `FINISH`, the graph goes to **answer**. Otherwise it goes to **approval**.
4. **approval** interrupts the run; `main.py` prompts you. `yes` runs the tool, anything else skips to **answer**.
5. **tool** calls the MCP tool, records the observation, and increments `current_step`.
6. The loop returns to **planner** until it finishes or reaches `max_steps`.
7. **answer** asks the LLM to turn the observations into a final reply.

## Project structure

```
.
├── main.py               # Entry point: connects to MCP, runs graph, handles approval prompts
├── graph.py              # LangGraph definition (nodes, routing, checkpointer)
├── agent/
│   ├── state.py          # AgentState TypedDict
│   ├── planner.py        # LLM planner: chooses next tool or FINISH
│   ├── executor.py       # Executes the chosen tool and extracts text output
│   ├── runner.py         # format_answer: builds the final user-facing answer
│   ├── mcp_client.py     # FastMCP client helpers (connect, discover, execute)
│   ├── server.py         # FastMCP server exposing the tools
│   └── loop.py           # (currently empty)
├── .env                  # Local configuration (not committed)
└── README.md
```

## Tech stack

- Python 3.14 (the repo's `.venv` uses it; 3.10+ should work)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastMCP](https://gofastmcp.com)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Setup

```bash
git clone https://github.com/mishraabhishek11/ai-multiple-agent-langgraph.git
cd ai-multiple-agent-langgraph

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install langgraph fastmcp openai python-dotenv
```

> There is no `requirements.txt` yet; the packages above are what the code imports.

### Configuration

Create a `.env` file in the project root:

| Variable   | Used by         | Description                       |
| ---------- | --------------- | --------------------------------- |
| `BASE_URL` | planner, runner | OpenAI-compatible endpoint        |
| `API_KEY`  | planner, runner | API key (any string for Ollama)   |
| `MODEL`    | planner, runner | Model name served by the endpoint |

`.env` is git-ignored — never commit real keys.

## Usage

```bash
python main.py
```

Example session:

```
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What time is it?

Planner Selected:
current_time

==============================
 HUMAN APPROVAL REQUIRED
==============================
Approve this tool call?
Tool: current_time

Approve? (yes/no): yes
...
Final Answer:
It's 06-11-2026 21:10:00.
```

## Adding a tool

1. Add a function decorated with `@mcp.tool()` and a docstring to `agent/server.py`. The docstring becomes the description the planner sees.
2. Restart `main.py` — tools are discovered automatically.

> **Note:** `execute_action` currently calls tools with no arguments, so tools with required parameters will not receive values from the planner (`generate_password` falls back to its default length).

## Known limitations / future work

- Tool arguments are not planned or passed to MCP tools yet.
- Rejecting an approval jumps straight to the answer step rather than re-planning.
- `InMemorySaver` loses state on exit; use a persistent checkpointer for production.
- `agent/loop.py` is empty and `agent/runner.py` has unused imports.
- Add `requirements.txt`, tests and structured logging.

## Contributing

1. Fork the repo and create a branch: `feat/short-description`
2. Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat(scope): description`)
3. Open a pull request

## Author

Abhishek Mishra — [github.com/mishraabhishek11](https://github.com/mishraabhishek11)
