#!/usr/bin/env python3
"""Seeds 22 well-scoped 'good first issue' tasks to attract 20+ external contributors."""

import subprocess
import time

ISSUES = [
    (
        "feat(pricing): add DeepSeek R1 and V3 model pricing to MODEL_PRICING",
        "Add `deepseek-r1` and `deepseek-v3` entries to `MODEL_PRICING` in `src/mcp_cost_guard/analyzer.py` along with a unit test in `tests/test_analyzer.py`.",
    ),
    (
        "feat(pricing): add Meta Llama 3.3 70B pricing entry",
        "Add `llama-3.3-70b` to `MODEL_PRICING` in `src/mcp_cost_guard/analyzer.py` and verify it appears in `mcp-cost-guard --list-models`.",
    ),
    (
        "feat(pricing): add Mistral Large 2 model pricing preset",
        "Add `mistral-large-2` to `MODEL_PRICING` in `src/mcp_cost_guard/analyzer.py` with unit test coverage.",
    ),
    (
        "feat(pricing): add OpenAI o3-mini and o1 model pricing presets",
        "Add `o3-mini` and `o1` to `MODEL_PRICING` in `src/mcp_cost_guard/analyzer.py` and add a test case in `tests/test_analyzer.py`.",
    ),
    (
        "feat(security): detect Google Cloud (GCP) API keys (`AIza...`) in scan_secrets",
        "Add a regex pattern `AIza[0-9A-Za-z\\-_]{35}` for `Google Cloud API Key` inside `SECRET_PATTERNS` in `src/mcp_cost_guard/analyzer.py` with a corresponding unit test.",
    ),
    (
        "feat(security): detect HuggingFace tokens (`hf_...`) in scan_secrets",
        "Add a regex pattern `hf_[A-Za-z0-9]{30,}` for `HuggingFace Token` in `SECRET_PATTERNS` and write a unit test in `tests/test_analyzer.py`.",
    ),
    (
        "feat(security): detect Stripe live secret keys (`sk_live_...`) in scan_secrets",
        "Add a regex pattern for Stripe secret keys in `SECRET_PATTERNS` in `src/mcp_cost_guard/analyzer.py` and add a test in `tests/test_analyzer.py`.",
    ),
    (
        "feat(security): detect GitLab Personal Access Tokens (`glpat-...`) in scan_secrets",
        "Add a regex pattern `glpat-[0-9a-zA-Z\\-_]{20}` in `SECRET_PATTERNS` and test it in `tests/test_analyzer.py`.",
    ),
    (
        "feat(security): detect npm access tokens (`npm_...`) in scan_secrets",
        "Add a regex pattern for npm tokens in `SECRET_PATTERNS` inside `src/mcp_cost_guard/analyzer.py` and add a unit test.",
    ),
    (
        "feat(cli): add `--markdown` flag to output analysis report as a Markdown table",
        "Add a `--markdown` argument in `src/mcp_cost_guard/cli.py` that prints the `AnalysisResult` fields as a clean Markdown table for GitHub Actions PR comments.",
    ),
    (
        "feat(cli): add `--csv` output flag for spreadsheet logging",
        "Add a `--csv` flag to `src/mcp_cost_guard/cli.py` that prints a single header row and comma-separated values row for `AnalysisResult`.",
    ),
    (
        "feat(analyzer): add `redact_secrets(text: str)` helper function",
        "Implement a `redact_secrets(text: str) -> str` function in `src/mcp_cost_guard/analyzer.py` that replaces any matched secret pattern with `[REDACTED]` and add a unit test.",
    ),
    (
        "feat(cli): add `--redact` CLI flag to print prompt with secrets masked",
        "Expose secret redaction in `src/mcp_cost_guard/cli.py` so users can scrub files before piping them to an LLM.",
    ),
    (
        "feat(mcp): add `list_supported_models` tool to MCP server",
        "Register a third tool `list_supported_models` in `src/mcp_cost_guard/mcp_server.py` that returns `MODEL_PRICING` as JSON when called via `tools/call`.",
    ),
    (
        "test(cli): add unit test for `--list-models` CLI flag",
        "Write a test in `tests/test_analyzer.py` verifying that `main(['--list-models'])` returns exit code `0` and outputs `claude-sonnet-4`.",
    ),
    (
        "test(cli): add unit test for `--fail-on-secrets` exit code 3",
        "Write a unit test in `tests/test_analyzer.py` verifying that passing a prompt with an `sk-ant-api03-...` key and `--fail-on-secrets` exits with code `3`.",
    ),
    (
        "test(cli): add unit test for missing file error handling",
        "Write a unit test in `tests/test_analyzer.py` verifying that `main(['--file', 'non_existent_file.txt'])` returns exit code `1`.",
    ),
    (
        "test(mcp): add unit test for `optimize_prompt` MCP tool call",
        "Add a unit test in `tests/test_analyzer.py` testing the `optimize_prompt` tool in `handle_request()` inside `mcp_server.py`.",
    ),
    (
        "docs(readme): add GitHub Actions workflow example for automated PR prompt auditing",
        "Add a short YAML snippet to `README.md` showing how developers can run `mcp-cost-guard` inside their own `.github/workflows/` pipeline.",
    ),
    (
        "docs(readme): add Cursor and Windsurf MCP configuration examples",
        "Update `README.md` with JSON configuration snippets showing how to connect `mcp-cost-guard --mcp-stdio` in Cursor and Windsurf.",
    ),
    (
        "feat(analyzer): support analyzing multiple files via glob or directory path",
        "Allow passing multiple file paths or a directory to estimate total repository context tokens and costs.",
    ),
    (
        "chore(ci): add ruff linter check to `.github/workflows/ci.yml`",
        "Add a step in `.github/workflows/ci.yml` to run `ruff check src tests` to keep code formatting clean.",
    ),
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=False)


def main() -> None:
    print("Ensuring labels exist on repository...")
    run(["gh", "label", "create", "good first issue", "--color", "7057ff", "--force"])
    run(["gh", "label", "create", "help wanted", "--color", "008672", "--force"])

    for idx, (title, body) in enumerate(ISSUES, 1):
        full_body = (
            f"### Overview\n{body}\n\n"
            "### Acceptance Criteria\n"
            "- [ ] Implementation added with clean type annotations\n"
            "- [ ] Unit test added or updated in `tests/test_analyzer.py`\n"
            "- [ ] `pytest -v` passes completely\n\n"
            "*This issue is reserved for first-time or external contributors! Comment below if you'd like to work on it or open a PR directly.*"
        )
        print(f"[{idx}/{len(ISSUES)}] Creating issue: {title}")
        run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                title,
                "--body",
                full_body,
                "--label",
                "good first issue,help wanted",
            ]
        )
        time.sleep(1.5)


if __name__ == "__main__":
    main()
