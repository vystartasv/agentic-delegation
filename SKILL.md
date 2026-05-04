---
name: agentic-delegation
description: Agentic Flow delegation protocol — task decomposition, tool routing, verification gates, and retry. Load BEFORE any delegate_task call to prevent token waste. Implements Patterns 4, 6, 7, 9, 10 from the Agentic Methodology.
triggers:
  - delegate
  - delegation
  - subagent
  - delegate_task
  - multi-agent
  - parallel
  - split
  - orchestrate
  - "burn tokens"
  - "Agentic Flow"
  - agentic-delegation
---

# Agentic Delegation Protocol

Implements Patterns 4 (Orchestration), 6 (Never-Stop), 7 (Context), 9 (Quality Gates), 10 (Tool Composition) from the Agentic Methodology.

**HOW TO USE:** When you are about to call delegate_task — STOP. Run this decision tree first. If the task is complex or ambiguous, decompose it with the script below. If you forgot and already delegated and it failed, jump to the Self-Correction Protocol.

---

## ⛔ Quick Reference (READ FIRST)

```
CODING → write_file / patch / terminal        (NEVER delegate_task)
RESEARCH → delegate_task (verify output, max 2 retries)
COMPLEX → decompose first → route each → verify each
FAILED DELEGATION → do it yourself (max 2 retries then STOP)
SUBAGENT CLAIMS "file written" → stat the file yourself
```

---

## ⛔ Core Rule — NEVER VIOLATE

**delegate_task is FORBIDDEN for coding.**

- Multi-file coding → direct authoring (write_file + patch). 10x faster, 100% reliable.
- Single-file editing → direct authoring. Subagent overhead exceeds the edit time.
- Build debugging → terminal(), not delegate_task.
- Subagents time out at 600s on coding. They produce garbage or nothing.
- Exception: delegate_task is ALLOWED for web research, market analysis, data synthesis — read-only tasks with no file writes.

If you already called delegate_task for coding and it failed: do NOT retry with delegate_task. Write the code directly.

### Self-Correction Protocol (if you ignored the rule above)

1. **Admit it**: You called delegate_task for coding and it failed/timed out/produced garbage.
2. **Don't retry delegate_task**: No "let me try again with better context." That burns more tokens.
3. **Read the failure**: What did the subagent actually return? Extract any useful fragments.
4. **Do it yourself**: Use write_file, patch, and terminal directly. You have the full context the subagent lacked.
5. **Save the lesson**: If a pattern of failure emerges, save it to memory.

## Decision Tree — Run BEFORE Every delegate_task Call

```
Task type?
├─ Coding (any files changed) → ❌ BLOCKED — use write_file/patch/terminal
├─ Research / analysis → ✅ ALLOWED — but verify output
├─ Search / data gathering → ✅ ALLOWED — bounded, time-limited
├─ Multi-stream (code+research) → split:
│   ├─ Code stream → direct authoring
│   └─ Research stream → delegate_task
└─ Unknown → decompose first (see below), then route each subtask
```

### When delegate_task IS appropriate:

- Web research on a bounded topic (<5 search terms)
- Market analysis with structured output format
- Reading and summarizing a remote document
- Parallel independent research streams
- Competitor analysis requiring multiple sources

### When delegate_task is NEVER appropriate:

- Any task that writes, edits, or creates files
- Any task requiring >10 minutes of work
- Any task where the output must be pixel-perfect
- Any task requiring interactive user input
- Any task the main agent can do in <5 tool calls

### Worked Example: "Research GRPO papers and add summary to README"

**BAD approach** (what you'd do without this skill):
```
delegate_task(goal="Research GRPO papers and update the README")
→ subagent times out at 600s trying to edit files
→ 0 tokens burned, nothing produced
```

**CORRECT approach** (with decomposition):
```bash
python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py \
  "Research GRPO training papers, write a summary, and add it to README"
```
Output:
```json
[
  {"id": "1", "description": "Research GRPO training papers", "tool": "delegate", "verify": "3-5 relevant papers with summaries"},
  {"id": "2", "description": "Write a summary of the research findings", "tool": "direct", "verify": "Summary doc with key points"},
  {"id": "3", "description": "Update the project README with the summary", "tool": "direct", "verify": "README.md contains new section"}
]
```

Then execute:
1. `delegate_task` for subtask 1 (research only, no file writes)
2. Read the research results yourself
3. `write_file` for the summary (direct, fast)
4. `patch` to update README (direct, fast)

Result: 3 minutes, 2 delegate_task calls, 1 verified output. No timeout. No garbage.

## Task Decomposition Protocol (Pattern 4 + 10)

Before delegating ANY task, run this checklist:

### 1. Decompose
Break the task into atomic subtasks. Each subtask must be:
- Completable in <10 tool calls
- Completable in <5 minutes
- Verifiable (clear pass/fail criteria)
- Independent (no cross-subtask dependencies)

Use the decomposer script for complex tasks:

```bash
# Full decomposition via local oMLX model
python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py "user's task description"

# Fast rule-based fallback (no model call)
python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py --fallback "task"

# Cloud fallback via Gemini Flash
python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py --model gemini "task"

# Compact output for piping
python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py -c "task"

# Validate existing decomposition (fixes coding→delegate routing errors)
cat subtasks.json | python3.11 ~/.hermes/skills/software-development/agentic-delegation/scripts/decompose.py --validate-only
```

**The --validate-only flag** can fix already-decomposed JSON — if any subtask is a coding task labeled "delegate", it silently reassigns it to "direct" with a `[FIXED]` annotation. This is your safety net when the model hallucinates bad routing.

### 2. Route Each Subtask
| Subtask type | Tool to use | Why |
|-------------|-------------|-----|
| Write code | `write_file` | Direct, fast, verifiable |
| Edit code | `patch` | Targeted, no context loss |
| Run build/test | `terminal` | Real output, real errors |
| Search files | `search_files` | Faster than grep |
| Read files | `read_file` | Paginated, safe |
| Web research | `delegate_task` | Parallel, bounded |
| Data processing | `execute_code` | Python sandbox, fast |
| User decision | `clarify` | Direct, no middleman |

### 3. Execute in Priority Order
1. First: all direct subtasks (write_file, terminal, search_files)
2. Then: parallel delegate_task subtasks (if any)
3. Verify each before moving to next

## Delegation Rules (Pattern 6 — Never-Stop)

When delegate_task IS the right tool:

### Before delegating:
- Timeout: set expectations clearly — "return in <5 min or report partial results"
- Toolsets: restrict to what's needed. Research = `["web"]`, no terminal/file access.
- Context: pack ONLY what the subagent needs. Not the whole conversation.
- Output format: specify exact structure (JSON, markdown, bullet list).

### After delegating:
- **Verify immediately.** Subagent self-reports are unreliable.
- If output is empty/garbage → do NOT delegate again. Do it yourself or use a different tool.
- If output is partial but useful → extract what works, discard the rest.
- If subagent timed out → the task was too big. Decompose further.

### Retry protocol (max 2 retries):
1. First retry: repack context with more specific instructions
2. Second retry: different model or reduced scope
3. After 2 failures: **STOP.** Do it yourself. Never retry delegate_task 3+ times for the same task.

## Verification Gate (Pattern 9)

After EVERY subtask (direct OR delegated), verify before proceeding:

| Task type | Verification |
|-----------|-------------|
| File written | `read_file` first 10 lines, check syntax |
| Code edited | `search_files` for the change, `terminal` for syntax check |
| Build/test | Check exit code, grep for FAIL/ERROR |
| Research result | Check for: non-empty, relevant, not hallucinated |
| delegate_task output | Read it yourself. If it claims "file written", stat the file. Never trust subagent self-reports. |

## Anti-Patterns — What You Must NOT Do

| Anti-pattern | Why it fails | What to do instead |
|-------------|-------------|-------------------|
| delegate_task for coding | 600s timeout, garbage output | write_file + patch directly |
| delegate_task for "the whole thing" | Task too large for subagent context | Decompose into atomic subtasks |
| Trust subagent self-reports | Subagents claim success falsely | Verify every output yourself |
| Retry 3+ times on failure | Burns tokens with no improvement | Do it yourself after 2 failures |
| Delegate with full conversation | Context window explodes | Pack only what subagent needs |
| Delegate interactive work | Subagents can't ask questions | clarify() yourself, then act |
| Delegate multi-step builds | Each step compounds errors | terminal() with the full command chain |

## Context Packing (Pattern 7)

When preparing context for delegate_task, include ONLY:
1. The specific question or task (1-2 sentences)
2. Any relevant file paths (absolute paths only)
3. Constraints: time limit, output format, model to use
4. What NOT to do (if applicable)

Do NOT include:
- Full conversation history
- Code that the subagent doesn't need to read
- The methodology itself (subagents don't need it)
- "Good luck" or filler

## Integration with Other Skills

- When `delegated-agent-harnesses` is available, prefer Codex CLI for large coding tasks over direct authoring. But NEVER use delegate_task as a Codex fallback — if Codex isn't available, write directly.
- When `context-packer` is available, use it to prepare subagent context for large repos.
- After resolving a delegation failure, load `post-task-capture` to save the pattern.

## Validation Checklist

Before finishing any task that involved delegation, verify:

- [ ] No delegate_task was used for coding/file-editing tasks
- [ ] Every delegate_task output was independently verified
- [ ] No subagent self-report was trusted without verification
- [ ] Max 2 retries were observed (no 3+ retry loops)
- [ ] Context was packed lean (no full conversation dumps)
