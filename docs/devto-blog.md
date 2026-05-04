# My AI Agents Kept Burning Tokens on Subagents That Can't Code — So I Built a Decision Gate

*By Vilius Vystartas | May 2026*

I run 19 autonomous AI agents in production. They handle research, content, monitoring, deployment — the kind of always-on work that makes a solo developer's output look like a small team's.

The delegation feature was supposed to be the multiplier. Spawn a subagent, give it a task, get results in parallel. In theory, it turns one agent into many. In practice, it was burning thousands of tokens for exactly zero output.

The problem wasn't the agents. It was that nobody had taught them *when not to delegate*.

---

## The Problem That Forced My Hand

Here's what happens when you ask a subagent to code something:

1. The subagent spawns, reads the context, starts working — looks promising
2. It tries to write a file. The file operation fails silently. The subagent doesn't notice
3. It tries again with a different approach. Same silent failure
4. Six hundred seconds later: timeout. Zero output. Thousands of tokens gone

The core issue is structural: subagents can't reliably write files, can't run builds, can't verify their own output. They're built for **read-only work** — research, analysis, data gathering. But nothing in the agent's training tells it that. It just sees "task → delegate" and fires.

I watched this happen dozens of times. Every failure was another chunk of the context window gone, another session wasted, another moment of wondering whether multi-agent workflows were fundamentally broken.

They weren't. The delegation call just needed a bouncer at the door.

---

## What I Built: Agentic Delegation

Agentic Delegation is a decision protocol that sits between your agent and its delegation tool. It has three layers:

### 1. The Decision Tree

Before any `delegate_task` call, the protocol classifies the work:

```
CODING → BLOCKED. Routed to write_file/patch/terminal (10x faster, 100% reliable)
RESEARCH → ALLOWED. But verified after completion, max 2 retries
UNKNOWN → DECOMPOSED. Broken into atomic subtasks first, then routed individually
```

This is a hard rule, not a suggestion. The skill document literally says "NEVER VIOLATE" at the top of the coding section. If your agent ignores it and delegates coding anyway, there's a self-correction protocol that kicks in after the inevitable timeout.

### 2. The Task Decomposer

Complex tasks get broken into atomic subtasks by a lightweight classifier — either your local LLM (free) or Gemini Flash (cheap cloud fallback). No dependencies beyond Python's stdlib.

```bash
$ python3.11 scripts/decompose.py \
  "Research GRPO training papers, write a summary, and add it to README"
```
```json
[
  {"id": "1", "description": "Research GRPO training papers",  "tool": "delegate"},
  {"id": "2", "description": "Write a summary of the findings", "tool": "direct"},
  {"id": "3", "description": "Update the project README",        "tool": "direct"}
]
```

Three subtasks. One delegated (the research). Two handled directly (the writing). No subagent ever touches a file.

### 3. The Validation Gate

Models hallucinate. Sometimes the decomposer labels a coding task as "delegate." The validation gate catches this with a hard keyword check and reassigns it:

```bash
$ echo '[{"id":"1","description":"implement JWT auth","tool":"delegate"}]' \
  | python3.11 scripts/decompose.py --validate-only
```
```json
[{"id": "1", "description": "implement JWT auth", "tool": "direct",
  "verify": "[FIXED: was delegate]"}]
```

The annotation is deliberate. It leaves a paper trail so you can see what the model wanted to do vs what the gate enforced.

---

## Architecture

The protocol is surprisingly thin — under 400 lines total. The decision tree is a markdown file. The decomposer is a single Python script. The validation gate is a 20-line function.

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
│  Local LLM (free)   │
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

It runs as a Hermes skill that auto-loads when delegation triggers fire, or as a standalone Python tool. Either way, it adds about 200ms of overhead per delegation decision.

---

## What I Learned

**1. The delegation feature is a UI demo, not a production primitive.**

It works in a 2-minute screen recording. In production, with real tasks and real context windows, it falls apart. The gap between demo and production is where all the work lives.

**2. The right answer is usually "don't delegate."**

After decomposing dozens of complex tasks, a pattern emerged: roughly 85% of subtasks should be handled directly by the main agent. Delegation is only the right call for bounded, read-only research tasks. Everything else is faster and more reliable via direct tool calls.

**3. A validation gate is worth more than a better prompt.**

I spent time trying to engineer the perfect decomposition prompt — more examples, stricter formatting, longer system instructions. What actually worked was adding a 20-line validation function that just checks if a coding task got mislabeled and fixes it. Defensive engineering beats prompt engineering.

---

## Get It

- **Repo:** [github.com/vystartasv/agentic-delegation](https://github.com/vystartasv/agentic-delegation)
- **License:** MIT
- **Stack:** Python 3.11+, oMLX AgenticQwen-8B (local, free), Hermes Agent skills system

```bash
# Install as Hermes skill
git clone https://github.com/vystartasv/agentic-delegation.git \
  ~/.hermes/skills/software-development/agentic-delegation

# Or use standalone
git clone https://github.com/vystartasv/agentic-delegation.git
python3.11 agentic-delegation/scripts/decompose.py "your task here"
```

The protocol is a direct implementation of the Agentic Flow methodology — ten patterns for working with AI agents, developed over months of running a 19-agent fleet. The delegation pattern is the one that saves the most tokens.

Feedback welcome — especially from anyone else running multi-agent setups who's hit the delegation wall.
