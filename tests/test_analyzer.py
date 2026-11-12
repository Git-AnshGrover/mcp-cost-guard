"""Unit tests for mcp-cost-guard."""

import json
from mcp_cost_guard.analyzer import analyze_text, compress_prompt, estimate_tokens, scan_secrets
from mcp_cost_guard.cli import main
from mcp_cost_guard.mcp_server import handle_request


def test_estimate_tokens_basic() -> None:
    assert estimate_tokens("") == 0
    tokens = estimate_tokens("Hello world, this is a test prompt for Claude Code.")
    assert 8 <= tokens <= 20


def test_secret_scanner_detects_keys() -> None:
    fake_prompt = "Here is my key: sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    findings = scan_secrets(fake_prompt)
    assert "Anthropic API Key" in findings


def test_secret_scanner_detects_gitlab_personal_access_tokens() -> None:
    synthetic_token = "glpat-" + "aB09" * 5
    assert "GitLab Personal Access Token" in scan_secrets(f"token={synthetic_token}")
    assert "GitLab Personal Access Token" not in scan_secrets("glpat-short")
    assert "GitLab Personal Access Token" not in scan_secrets("prefix-" + synthetic_token)
    assert "GitLab Personal Access Token" not in scan_secrets("glpaz-" + "aB09" * 5)


def test_secret_scanner_clean_text() -> None:
    assert scan_secrets("Normal developer prompt with zero credentials.") == []


def test_compress_prompt() -> None:
    raw = "Line 1   \n\n\n\nLine 2  \n"
    compressed = compress_prompt(raw)
    assert compressed == "Line 1\n\nLine 2"


def test_analyze_text_budget_check() -> None:
    res = analyze_text(
        "Sample text " * 500,
        model="claude-opus-4",
        expected_output_tokens=2000,
        max_budget_usd=0.0001,
    )
    assert res.budget_exceeded is True
    assert res.total_estimated_cost_usd > 0.0001


def test_cli_json_output(capsys) -> None:
    exit_code = main(["--text", "Testing CLI execution", "--model", "claude-sonnet-4", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["model"] == "claude-sonnet-4"
    assert payload["estimated_input_tokens"] > 0


def test_mcp_server_initialize_and_tool_call() -> None:
    init_resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_resp is not None
    assert init_resp["result"]["serverInfo"]["name"] == "mcp-cost-guard"

    call_resp = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "audit_prompt_cost",
                "arguments": {"text": "Analyze this prompt", "model": "claude-3-5-haiku"},
            },
        }
    )
    assert call_resp is not None
    content_text = call_resp["result"]["content"][0]["text"]
    parsed = json.loads(content_text)
    assert parsed["model"] == "claude-3-5-haiku"
