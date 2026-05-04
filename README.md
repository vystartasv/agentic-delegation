# Agentic Delegation

**A decision gate that stops AI agents from burning tokens on subagents that can't deliver.**

---

## Summary

Most AI coding agents have a delegation feature — spawn a subagent to handle part of the work. It sounds great in theory. In practice, subagents time out after 10 minutes, produce garbage, or claim success while delivering nothing. Developers watch thousands of tokens evaporate with no output to show for it.

Agentic Delegation fixes this by adding a decision gate. Before any delegation call, it runs a task through a classifier: coding tasks get blocked and routed to direct file operations (10x faster, 100% reliable). Research tasks get through — but with verification gates and a two-retry maximum. Complex tasks get decomposed into atomic subtasks first, then each subtask goes to the right tool.

It's not a new framework or platform. It's a protocol — a small set of rules that sit between your agent and its delegation tool, making sure it never wastes tokens on a task a subagent can't complete.

The protocol is a direct implementation of the Agentic Flow methodology: ten patterns for working with AI agents, developed over months of running 19 autonomous agents in production.

---

## Who it's for

- **Developers running multi-agent workflows** — if your agent spawns subagents that keep timing out, this stops that
- **Hermes agent users** — install it as a skill, it loads automatically when you're about to delegate
- **Anyone who's watched a subagent spin for 10 minutes and return nothing** — the decision tree blocks those calls before they start
- **Teams adopting agent workflows in production** — the verification gate means subagent output gets checked, not trusted

## Who it's NOT for

- **Single-agent-only users** — if you never use delegate_task, you don't need this
- **People who want a full agent platform** — this is a decision protocol, not an orchestration framework
- **Teams that only use cloud SaaS agents** — this works with any agent, but the Python decomposer uses a local model by default
- **"Just let the agent figure it out" workflows** — this adds structure. If you prefer unstructured delegation, skip it

---

## Install

### As a Hermes skill

```bash
# From the skills hub (coming soon)
hermes skills install agentic-delegation

# Or directly from GitHub
git clone https://github.com/vystartasv/agentic-delegation.git ~/.hermes/skills/software-development/agentic-delegation
```

### Standalone (decomposer script only)

```bash
pip install agentic-delegation
# or
git clone https://github.com/vystartasv/agentic-delegation.git
cd agentic-delegation
```

---

## Quick Start

### Decompose a task before delegating

```bash
python3.11 scripts/decompose.py "Research GRPO training papers, write a summary, and add it to README"
```

Output:
```json
[
  {"id": "1", "description": "Research GRPO training papers",        "tool": "delegate", "verify": "3-5 relevant papers with summaries"},
  {"id": "2", "description": "Write a summary of the findings",      "tool": "direct",   "verify": "Summary document with key points"},
  {"id": "3", "description": "Update the project README",            "tool": "direct",   "verify": "README.md contains new section"}
]
```

The decomposer correctly routes research to `delegate` and all file-editing to `direct` — so your agent never sends a coding task to a subagent again.

### Validation gate

The decomposer includes a hard validation layer. If the model hallucinates "delegate" for a coding task, it gets reassigned:

```bash
echo '[{"id":"1","description":"implement JWT auth","tool":"delegate"}]' \
  | python3.11 scripts/decompose.py --validate-only
```

```json
[{"id": "1", "description": "implement JWT auth", "tool": "direct", "verify": "[FIXED: was delegate]"}]
```

### As a Hermes skill

Once installed, the skill auto-loads when your agent encounters delegation-related triggers. The decision tree fires before any `delegate_task` call:

```
CODING → write_file / patch / terminal    (NEVER delegate_task)
RESEARCH → delegate_task (verify, max 2 retries)
COMPLEX → decompose first → route each
FAILED DELEGATION → do it yourself
```

---

## Architecture

```
User gives agent a complex task
         │
         ▼
┌─────────────────────┐
│  Decision Tree      │  ← SKILL.md rules
│  Coding? → BLOCKED  │
│  Research? → ALLOW  │
│  Unknown? → SPLIT   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Task Decomposer    │  ← decompose.py
│  oMLX (local, free) │
│  or Gemini Flash    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Validation Gate    │  ← Hard rule check
│  No coding→delegate │
│  Fixed if violated  │
└────────┬────────────┘
         │
         ▼
    Route each subtask:
    direct → write_file / patch
    delegate → delegate_task (bounded)
    terminal → terminal()
    clarify → ask user
```

- **Model:** AgenticQwen-8B-oQ4 (local, free) or Gemini 2.0 Flash (cloud fallback)
- **Language:** Python 3.11+
- **Dependencies:** None beyond stdlib (urllib for model calls)
- **Hermes integration:** SKILL.md with auto-load triggers

---

## License

MIT — see [LICENSE](LICENSE)
