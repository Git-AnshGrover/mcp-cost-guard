# mcp-cost-guard 🛡️

[![CI](https://github.com/Git-AnshGrover/mcp-cost-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/Git-AnshGrover/mcp-cost-guard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Zero-dependency CLI and Model Context Protocol (MCP) server** for auditing LLM token costs, enforcing CI/CD prompt budgets, compressing context windows, and scrubbing leaked API keys before sending requests to Claude, OpenAI, or Gemini.

## Features
- **Instant Cost & Token Estimation:** Supports `claude-opus-4`, `claude-sonnet-4`, `claude-3-5-haiku`, `gpt-4o`, and `gemini-2.5-pro`.
- **CI/CD Budget Gatekeeper:** Fail builds automatically (`--max-budget 0.05`) when oversized context files or system prompts exceed budget thresholds.
- **Credential & Secret Scanner:** Detects leaked Anthropic (`sk-ant-...`), OpenAI, GitHub, AWS, and private keys before prompts leave your machine.
- **Native MCP Server:** Plugs directly into **Claude Code** and **Claude Desktop** over stdio with zero third-party dependencies.

## Quick Start

```bash
git clone https://github.com/Git-AnshGrover/mcp-cost-guard.git
cd mcp-cost-guard
pip install -e .
```

### CLI Usage

```bash
# Audit a prompt file against Claude Sonnet 4
mcp-cost-guard --file system_prompt.md --model claude-sonnet-4

# Enforce a strict USD budget and secret scan in CI/CD
mcp-cost-guard --file context.txt --max-budget 0.10 --fail-on-secrets --json

# List all supported models and pricing per 1M tokens
mcp-cost-guard --list-models
```

### Claude Code / Claude Desktop MCP Configuration

Add the following to your `claude_desktop_config.json` or `.mcp.json`:

```json
{
  "mcpServers": {
    "cost-guard": {
      "command": "mcp-cost-guard",
      "args": ["--mcp-stdio"]
    }
  }
}
```

## Contributing

We actively welcome first-time and experienced open-source contributors! Check our [open Good First Issues](https://github.com/Git-AnshGrover/mcp-cost-guard/labels/good%20first%20issue) and read [CONTRIBUTING.md](CONTRIBUTING.md) to get started in under 5 minutes.
