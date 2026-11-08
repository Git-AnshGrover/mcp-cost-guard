"""mcp-cost-guard: LLM Token Cost Estimator, Context Budget Enforcer, and MCP Server."""

__version__ = "0.2.0"

from .analyzer import (
    MODEL_PRICING,
    AnalysisResult,
    analyze_text,
    compress_prompt,
    estimate_tokens,
    scan_secrets,
)

__all__ = [
    "MODEL_PRICING",
    "AnalysisResult",
    "analyze_text",
    "compress_prompt",
    "estimate_tokens",
    "scan_secrets",
]
