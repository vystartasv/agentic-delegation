# Contributing

Thanks for your interest in improving Agentic Delegation.

## Development Setup

```bash
git clone https://github.com/vystartasv/agentic-delegation.git
cd agentic-delegation
```

No virtual environment needed — the decomposer uses only Python stdlib.

Running the decomposer locally requires either:
- oMLX server running at `localhost:8000` (recommended, free)
- Or a `GEMINI_API_KEY` environment variable (cloud fallback)

## Testing

```bash
# Test with local model (requires oMLX running)
python3.11 scripts/decompose.py "Research GRPO papers and write summary"

# Test with rule-based fallback (no model needed)
python3.11 scripts/decompose.py --fallback "Build auth service and deploy"

# Test validation gate
echo '[{"id":"1","description":"write code","tool":"delegate"}]' | \
  python3.11 scripts/decompose.py --validate-only
```

## What to Contribute

The best contributions improve either:
1. The decision tree rules (SKILL.md) — better classification or new anti-patterns
2. The decomposer (scripts/decompose.py) — better model prompts, stronger validation
3. New triggers for the Hermes skill auto-load system

## Pull Request Checklist

- [ ] README updated if new features added
- [ ] Decomposer tested with `--fallback` (no model dependency)
- [ ] Validation gate still catches coding→delegate misroutes
- [ ] CHANGELOG updated under Unreleased

## Code Style

- Python 3.11+, stdlib only for the decomposer
- Type hints on public functions
- Keep it simple — this is infrastructure, not a framework
