"""Zero-dependency Model Context Protocol (MCP) JSON-RPC 2.0 Server over stdio."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from . import __version__
from .analyzer import MODEL_PRICING, analyze_text, compress_prompt


def handle_request(request: Dict[str, Any]) -> Dict[str, Any] | None:
    """Processes a single JSON-RPC 2.0 request from an MCP client (e.g., Claude Code)."""
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {}) or {}

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mcp-cost-guard", "version": __version__},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "audit_prompt_cost",
                        "description": "Estimates token count, USD API cost, context window usage, and scans for leaked secrets.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Prompt or file content to audit."},
                                "model": {
                                    "type": "string",
                                    "description": f"Target model name ({', '.join(MODEL_PRICING.keys())})",
                                    "default": "claude-sonnet-4",
                                },
                                "expected_output_tokens": {
                                    "type": "integer",
                                    "default": 1000,
                                },
                            },
                            "required": ["text"],
                        },
                    },
                    {
                        "name": "optimize_prompt",
                        "description": "Compresses redundant whitespace in a prompt and reports token savings.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Prompt text to compress."}
                            },
                            "required": ["text"],
                        },
                    },
                ]
            },
        }

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {}) or {}

        if tool_name == "audit_prompt_cost":
            text = str(args.get("text", ""))
            model = str(args.get("model", "claude-sonnet-4"))
            expected_out = int(args.get("expected_output_tokens", 1000))
            result = analyze_text(text=text, model=model, expected_output_tokens=expected_out)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result.to_dict(), indent=2)}]
                },
            }

        if tool_name == "optimize_prompt":
            raw_text = str(args.get("text", ""))
            compressed = compress_prompt(raw_text)
            before = analyze_text(raw_text)
            after = analyze_text(compressed)
            payload = {
                "original_tokens": before.estimated_input_tokens,
                "compressed_tokens": after.estimated_input_tokens,
                "tokens_saved": before.estimated_input_tokens - after.estimated_input_tokens,
                "compressed_text": compressed,
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(payload, indent=2)}]
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def run_stdio_server() -> None:
    """Runs the blocking MCP JSON-RPC loop over standard input/output."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse or execution error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
