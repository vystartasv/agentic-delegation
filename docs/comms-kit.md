# Comms Kit — Agentic Delegation v0.1.0

> Channel-specific posts for launch. Practical, pattern-driven, no AI hype.
> Repo: https://github.com/vystartasv/agentic-delegation

---

## 1. Twitter/X Thread

**Tweet 1:**
My AI agent has a delegation feature. It sounded great — spawn subagents for parallel work.
Reality: subagents time out after 10 minutes, produce garbage, or claim success while delivering nothing.
Thousands of tokens, zero output.
So I built a decision gate that stops it before the call happens.

**Tweet 2:**
The problem isn't subagents. It's that agents try to delegate EVERYTHING — including coding tasks that subagents physically can't complete.
The fix: a decision tree that classifies tasks BEFORE delegation.
Coding → blocked, routed to direct file ops (10x faster)
Research → allowed, with verification gates

**Tweet 3:**
The task decomposer uses a local model (AgenticQwen-8B) to break complex work into atomic subtasks.
"Build auth service + research OWASP + deploy" becomes 7 subtasks, each routed to the right tool.
1 of 7 goes to delegate_task. The other 6 go to direct file ops and terminal commands.

**Tweet 4:**
Validation gate catches the inevitable: when the model hallucinates "delegate" for a coding task, it gets reassigned to "direct" with `[FIXED: was delegate]`.
Been running this on my 19-agent fleet. Subagent timeout rate → zero.

**Tweet 5:**
Open source, MIT license. Works as a Hermes skill (auto-loads) or standalone Python tool.
repo: github.com/vystartasv/agentic-delegation
Part of the Agentic Flow methodology — ten patterns for working with AI agents. The delegation pattern is the one that saves the most tokens.

---

## 2. LinkedIn Post

**Headline:** My AI subagents kept burning tokens and producing nothing. Here's how I fixed it.

Most AI coding agents have a delegation feature — spawn subagents for parallel work. It's a great demo. In production, it's a liability.

I run 19 autonomous agents. When one of them delegates a coding task to a subagent, the subagent times out at 10 minutes. Zero output. Thousands of tokens gone. I watched this happen dozens of times before accepting that the feature was fundamentally broken for coding work.

The fix wasn't making subagents better. It was adding a decision gate *before* the delegation call.

Agentic Delegation is a small protocol: a decision tree, a task decomposer, and a validation gate. Before any delegation call, it classifies the task. Coding → blocked, routed to direct file operations (10x faster, 100% reliable). Research → allowed but verified. Complex tasks get decomposed into atomic subtasks first, each routed to the right tool.

The decomposer uses your local LLM — no cloud dependency, no API costs. The validation gate catches hallucinated routing. If the model tries to send "implement JWT auth" to a subagent, it gets reassigned to direct with `[FIXED: was delegate]`.

Open source under MIT. Works standalone or as a Hermes skill.

Repo: github.com/vystartasv/agentic-delegation

#aiagents #agenticflow #opensource #hermesagent #agentops

---

## 3. Short (for Telegram/Discord)

**Agentic Delegation v0.1.0 is live** 🦞

A decision gate that stops AI agents from burning tokens on subagents that can't deliver.

→ Blocks delegate_task for coding (routes to direct file ops instead)
→ Decomposes complex tasks into atomic subtasks
→ Validation gate catches misrouted tasks

```
python3.11 scripts/decompose.py "Research GRPO, write summary, update README"
# Output: 3 atomic subtasks, 1 delegate (research), 2 direct (code)

echo '[{"id":"1","description":"implement JWT","tool":"delegate"}]' | \
  python3.11 scripts/decompose.py --validate-only
# Output: tool → "direct" [FIXED: was delegate]
```

Python 3.11+, stdlib only. Local model (free) or Gemini Flash fallback.
MIT license — github.com/vystartasv/agentic-delegation

---

## 4. Hacker News / Reddit Show HN

**Title:** Show HN: Agentic Delegation — a decision gate that stops AI agents wasting tokens on broken subagents

**Text:**

I run 19 autonomous AI agents in production. They use delegate_task for parallel work — spawning subagents to handle parts of a task.

The problem: subagents can't do coding. They time out at 10 minutes, produce garbage, or claim "file written" when nothing was created. Every failure burns thousands of tokens with zero output.

Agentic Delegation is a protocol that sits between your agent and its delegation tool. Before any delegate_task call, it runs a decision tree:

- Coding task → blocked, routed to write_file/patch (10x faster, 100% reliable)
- Research task → allowed, but verified after completion
- Complex task → decomposed into atomic subtasks first, each routed to the right tool

The decomposer uses a local LLM (free) or Gemini Flash. A validation gate catches model hallucinations — if the LLM labels "implement JWT auth" as delegate, it gets force-reassigned to direct with a `[FIXED]` annotation.

It's a Hermes skill that auto-loads when delegation triggers fire, or a standalone Python tool. No dependencies beyond stdlib. Been running on my 19-agent fleet for a week — subagent timeouts dropped to zero.

Stack: Python 3.11, oMLX AgenticQwen-8B (local), Hermes Agent skills system. MIT license.

Repo: https://github.com/vystartasv/agentic-delegation

Feedback welcome — especially from anyone else running multi-agent setups who's hit the delegation wall.
