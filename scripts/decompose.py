#!/usr/bin/env python3.11
"""
Agentic Delegation — Task Decomposer

Breaks a complex task into atomic subtasks using a cheap local model.
Each subtask gets a routing label (direct, delegate, terminal, clarify)
based on the Agentic Flow decision tree.

Usage:
    python3.11 decompose.py "Build a login page with tests and deploy"
    echo "Research GRPO papers and summarize" | python3.11 decompose.py
    python3.11 decompose.py --model gemini "Analyze competitor pricing"
    python3.11 decompose.py --fallback "Quick decompose without model"

Output: JSON array of subtasks with tool routing and verification criteria.
"""

import json
import sys
import os
import argparse
import re
import urllib.request
from typing import List, Optional

# ── Model backends ──────────────────────────────────────────────

OMMLX_URL = "http://localhost:8000/v1/chat/completions"
OMMLX_MODEL = "AgenticQwen-8B-oQ4"
GEMINI_MODEL = "gemini-2.0-flash"


def call_omlx(prompt: str) -> dict:
    """Call local oMLX server — free, fast, always available."""
    payload = {
        "model": OMMLX_MODEL,
        "messages": [
            {"role": "system", "content": DECOMPOSER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    req = urllib.request.Request(
        OMMLX_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def call_gemini(prompt: str) -> dict:
    """Call Gemini Flash — cheap cloud fallback."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "No GEMINI_API_KEY or GOOGLE_API_KEY set"}
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": DECOMPOSER_SYSTEM}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read())
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            return {"choices": [{"message": {"content": text}}]}
    except Exception as e:
        return {"error": str(e)}


# ── System prompt ────────────────────────────────────────────────

DECOMPOSER_SYSTEM = """You are a task decomposition engine. Break complex tasks into atomic subtasks.

RULES:
1. Each subtask completable in <5 minutes by a single agent
2. Each subtask independent (no cross-subtask dependencies)
3. Assign "tool" to each subtask:
   - "direct" — creating/editing files, writing code, documentation
   - "delegate" — web research, market analysis, competitor research, reading remote docs ONLY
   - "terminal" — running builds, tests, git operations, package installs, deployments
   - "clarify" — decisions needing user input, ambiguous requirements
4. CRITICAL: NEVER assign "delegate" to coding, file editing, or build tasks
5. Include "verify" field — how to check the subtask succeeded
6. "id" must be sequential integers starting from "1"

Output ONLY valid JSON array. No explanation, no markdown, no backticks.
Format:
[{"id": "1", "description": "...", "tool": "direct|delegate|terminal|clarify", "verify": "..."}]
"""

DECOMPOSER_USER = """Decompose this task into atomic subtasks:

{task}

Return ONLY the JSON array."""


# ── JSON extraction ──────────────────────────────────────────────

def extract_json(content: str) -> list:
    """Robust JSON array extraction from model output.

    Handles: markdown fences, leading text, trailing commas,
    missing closing brackets, and stray non-JSON content.
    """
    content = content.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.match(r"```(?:json)?\s*\n(.*?)\n```", content, re.DOTALL)
    if fence_match:
        content = fence_match.group(1).strip()
    elif content.startswith("```") and content.endswith("```"):
        # Loose fence — strip first and last line
        content = "\n".join(content.split("\n")[1:-1]).strip()

    # Find the JSON array boundaries
    start = content.find("[")
    end = content.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in response")

    content = content[start : end + 1]

    # Fix common model JSON errors
    # Trailing comma before ]
    content = re.sub(r",\s*]", "]", content)
    # Single quotes → double quotes (careful with apostrophes)
    # (skip — too fragile, rely on model producing valid JSON)

    return json.loads(content)


# ── Validation gate ──────────────────────────────────────────────

CODING_KEYWORDS = [
    "code", "implement", "build", "write", "create file", "edit",
    "refactor", "fix", "patch", "scaffold", "generate", "program",
    "script", "module", "function", "class", "import", "api endpoint",
]


def is_coding_task(description: str) -> bool:
    """Heuristic: does this subtask involve writing or editing code?"""
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in CODING_KEYWORDS)


def validate_subtasks(subtasks: list) -> list:
    """Ensure no coding subtasks are routed to delegate_task.

    If a coding subtask is labeled "delegate", reassign to "direct"
    and add a warning. Silently fix — don't reject.
    """
    for st in subtasks:
        if st.get("tool") == "delegate" and is_coding_task(st.get("description", "")):
            st["tool"] = "direct"
            st["verify"] = (
                f"[FIXED: was delegate] {st.get('verify', '')}"
            ).strip()
    return subtasks


# ── Fallback decomposition ───────────────────────────────────────

# Keyword → (category, tool) mapping for rule-based fallback
FALLBACK_RULES = [
    (["research", "analyze", "find papers", "search web", "competitor",
      "market analysis", "literature review"], "delegate"),
    (["write code", "implement", "create file", "scaffold", "build app",
      "code", "refactor", "fix bug", "add feature", "edit file",
      "update readme", "write doc", "documentation", "generate"],
     "direct"),
    (["run test", "pytest", "npm test", "cargo test", "test suite",
      "run build", "compile", "deploy", "publish", "release",
      "git commit", "git push", "install package", "npm install",
      "pip install", "docker build"],
     "terminal"),
    (["decide", "choose", "which approach", "prefer", "opinion",
      "should i", "recommend"],
     "clarify"),
]


def extract_subtasks_from_text(task: str) -> list:
    """Split task by conjunctions and punctuation into clauses."""
    # Split on: "and", "then", ",", ";", "also", "plus"
    clauses = re.split(
        r"\s+(?:and|then|also|plus)\s+|[,;]\s*|\s*\.\s+(?=[A-Z])",
        task,
    )
    # Filter empty and very short clauses
    clauses = [c.strip() for c in clauses if len(c.strip()) > 5]
    return clauses


def classify_clause(clause: str) -> str:
    """Classify a single clause into tool category."""
    clause_lower = clause.lower()
    for keywords, tool in FALLBACK_RULES:
        if any(kw in clause_lower for kw in keywords):
            return tool
    return "direct"  # default


def fallback_decompose(task: str) -> list:
    """Rule-based decomposition — split task into clauses, classify each."""
    clauses = extract_subtasks_from_text(task)

    if not clauses:
        return [{
            "id": "1",
            "description": task,
            "tool": "direct",
            "verify": "Read output, check for errors",
        }]

    subtasks = []
    for i, clause in enumerate(clauses):
        tool = classify_clause(clause)
        verify = {
            "direct": "Check file exists and has correct content",
            "delegate": "Output is non-empty, contains sources, relevant to query",
            "terminal": "Exit code 0, no error lines in output",
            "clarify": "User response is clear and actionable",
        }.get(tool, "Check output is non-empty")

        subtasks.append({
            "id": str(i + 1),
            "description": clause,
            "tool": tool,
            "verify": verify,
        })

    return validate_subtasks(subtasks)


# ── Main decompose function ──────────────────────────────────────

def decompose(task: str, model: str = "omlx", retry: bool = True) -> list:
    """Decompose a task into atomic subtasks."""
    prompt = DECOMPOSER_USER.format(task=task)

    if model == "gemini":
        result = call_gemini(prompt)
    else:
        result = call_omlx(prompt)

    # Retry once on failure with shorter prompt
    if "error" in result and retry and model == "omlx":
        result = call_omlx(DECOMPOSER_USER.format(task=task[:500]))

    if "error" in result:
        return fallback_decompose(task)

    try:
        content = result["choices"][0]["message"]["content"]
        subtasks = extract_json(content)
        return validate_subtasks(subtasks)
    except (KeyError, json.JSONDecodeError, ValueError, IndexError) as e:
        # One retry with stricter instructions
        if retry:
            strict_prompt = (
                DECOMPOSER_USER.format(task=task)
                + "\n\nIMPORTANT: Output ONLY the JSON array. No backticks. No explanation."
            )
            if model == "gemini":
                result2 = call_gemini(strict_prompt)
            else:
                result2 = call_omlx(strict_prompt)
            if "error" not in result2:
                try:
                    content2 = result2["choices"][0]["message"]["content"]
                    return validate_subtasks(extract_json(content2))
                except Exception:
                    pass
        return fallback_decompose(task)


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agentic Flow task decomposer — breaks tasks into atomic subtasks"
    )
    parser.add_argument(
        "task", nargs="?", help="Task description to decompose"
    )
    parser.add_argument(
        "--model", choices=["omlx", "gemini"], default="omlx",
        help="Model backend (default: omlx local)"
    )
    parser.add_argument(
        "--fallback", action="store_true",
        help="Force rule-based fallback (no model call)"
    )
    parser.add_argument(
        "--compact", "-c", action="store_true",
        help="Compact output (no indentation)"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate, don't decompose (pipe JSON in)"
    )
    args = parser.parse_args()

    if args.validate_only:
        raw = sys.stdin.read().strip()
        subtasks = json.loads(raw)
        fixed = validate_subtasks(subtasks)
        indent = None if args.compact else 2
        print(json.dumps(fixed, indent=indent))
        return

    # Read task from stdin if not provided as argument
    task = args.task
    if not task:
        if sys.stdin.isatty():
            print(json.dumps({"error": "No task provided"}, indent=2))
            sys.exit(1)
        task = sys.stdin.read().strip()
    if not task:
        print(json.dumps({"error": "No task provided"}, indent=2))
        sys.exit(1)

    if args.fallback:
        subtasks = fallback_decompose(task)
    else:
        subtasks = decompose(task, args.model)

    indent = None if args.compact else 2
    print(json.dumps(subtasks, indent=indent))


if __name__ == "__main__":
    main()
