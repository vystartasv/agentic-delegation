# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-04

### Added
- Initial release
- Decision tree for delegate_task routing (blocks coding, allows research)
- Task decomposer script using oMLX (local) or Gemini Flash (cloud)
- Validation gate — prevents coding tasks from being routed to delegate_task
- Rule-based fallback decomposition for when models are unavailable
- Hermes SKILL.md with auto-load triggers
- Self-correction protocol for failed delegations
- Verification gate for subagent output
- Context packing rules for lean subagent context
- Two-retry maximum with escalation to direct execution
