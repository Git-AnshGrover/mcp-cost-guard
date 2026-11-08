"""Command-line interface for mcp-cost-guard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .analyzer import MODEL_PRICING, analyze_text, compress_prompt
from .mcp_server import run_stdio_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-cost-guard",
        description="Audit LLM prompt token costs, detect leaked secrets, or run as an MCP server.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-f", "--file", type=str, help="Path to prompt or source file to analyze.")
    parser.add_argument("-t", "--text", type=str, help="Inline text string to analyze.")
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="claude-sonnet-4",
        choices=sorted(MODEL_PRICING.keys()),
        help="Target LLM model for pricing calculation (default: claude-sonnet-4).",
    )
    parser.add_argument(
        "-o",
        "--output-tokens",
        type=int,
        default=1000,
        help="Expected completion output tokens (default: 1000).",
    )
    parser.add_argument(
        "--max-budget",
        type=float,
        default=None,
        help="Fail with exit code 2 if estimated total USD cost exceeds this threshold.",
    )
    parser.add_argument(
        "--fail-on-secrets",
        action="store_true",
        help="Fail with exit code 3 if API keys or credentials are detected in the prompt.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress redundant whitespace before analyzing.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all supported models and their pricing per 1M tokens.",
    )
    parser.add_argument(
        "--mcp-stdio",
        action="store_true",
        help="Launch as a Model Context Protocol (MCP) JSON-RPC stdio server.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output analysis report as formatted JSON.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mcp_stdio:
        run_stdio_server()
        return 0

    if args.list_models:
        print(f"{'MODEL':<22} {'INPUT ($/1M)':<15} {'OUTPUT ($/1M)':<15} {'CONTEXT WINDOW':<15}")
        print("-" * 68)
        for name, data in sorted(MODEL_PRICING.items()):
            print(
                f"{name:<22} ${data['input']:<14.2f} ${data['output']:<14.2f} {int(data['context_window']):,}"
            )
        return 0

    content = ""
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        content = path.read_text(encoding="utf-8", errors="replace")
    elif args.text is not None:
        content = args.text
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        parser.print_help()
        return 0

    if args.compress:
        content = compress_prompt(content)

    result = analyze_text(
        text=content,
        model=args.model,
        expected_output_tokens=args.output_tokens,
        max_budget_usd=args.max_budget,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("=== MCP Cost Guard Analysis ===")
        print(f"Model                 : {result.model}")
        print(f"Characters / Words    : {result.character_count:,} chars / {result.word_count:,} words")
        print(f"Estimated Input Tokens: {result.estimated_input_tokens:,}")
        print(f"Expected Output Tokens: {result.expected_output_tokens:,}")
        print(f"Estimated Total Cost  : ${result.total_estimated_cost_usd:.6f} USD")
        print(
            f"Context Utilization   : {result.context_utilization_pct:.2f}% of {result.context_window_limit:,} tokens"
        )
        if result.detected_secrets:
            print(f"WARNING - Secrets     : {', '.join(result.detected_secrets)}")
        else:
            print("Security Scan         : Clean (0 secrets detected)")

    if args.fail_on_secrets and result.detected_secrets:
        return 3
    if result.budget_exceeded:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
