# Security

## Reporting a Vulnerability

If you discover a security vulnerability in Agentic Delegation, please report it privately.

**Do not open a public issue.** Instead, email:

- **vilius.vystartas@gmail.com**

Include:
- A description of the vulnerability
- Steps to reproduce
- Affected versions

You will receive a response within 72 hours. We aim to patch confirmed vulnerabilities within 7 days and will credit reporters (with permission) in the release notes.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | ✅ Currently supported |

## Security Considerations

This tool does not handle authentication credentials, user data, or network services directly. The decomposer script calls local LLM APIs (oMLX) or Google Gemini — ensure your API keys are stored in environment variables, not in source code.

The tool's primary security concern is preventing subagents from taking unauthorized actions through misrouted tasks. The validation gate (`--validate-only`) can be used to audit task routing before execution.
