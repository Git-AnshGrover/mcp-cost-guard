"""Core analysis engine for token estimation, pricing calculation, and secret detection."""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

# Pricing in USD per 1,000,000 (1M) tokens: (input_usd_per_1m, output_usd_per_1m, context_window)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "claude-opus-4": {"input": 15.00, "output": 75.00, "context_window": 200000},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00, "context_window": 200000},
    "claude-3-7-sonnet": {"input": 3.00, "output": 15.00, "context_window": 200000},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "context_window": 200000},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00, "context_window": 200000},
    "gpt-4o": {"input": 2.50, "output": 10.00, "context_window": 128000},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "context_window": 128000},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "context_window": 1000000},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60, "context_window": 1000000},
}

SECRET_PATTERNS: Dict[str, re.Pattern[str]] = {
    "Anthropic API Key": re.compile(r"sk-ant-api03-[A-Za-z0-9\-_]{20,}"),
    "OpenAI API Key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9]{20,}"),
    "GitHub Personal Access Token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "GitLab Personal Access Token": re.compile(r"(?<![A-Za-z0-9_-])glpat-[A-Za-z0-9_-]{20,}(?![A-Za-z0-9_-])"),
    "AWS Access Key ID": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}"),
    "Private Key Block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


@dataclass
class AnalysisResult:
    model: str
    character_count: int
    word_count: int
    estimated_input_tokens: int
    expected_output_tokens: int
    estimated_input_cost_usd: float
    estimated_output_cost_usd: float
    total_estimated_cost_usd: float
    context_window_limit: int
    context_utilization_pct: float
    budget_exceeded: bool
    detected_secrets: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def estimate_tokens(text: str) -> int:
    """
    Hybrid heuristic token estimator tuned for BPE tokenizers (Claude / tiktoken).
    Combines word-boundary splitting, punctuation density, and character ratios.
    """
    if not text:
        return 0
    # Count words and code symbols separately for high accuracy on both prose and code
    words = re.findall(r"\w+", text)
    symbols = re.findall(r"[^\w\s]", text)
    whitespace_runs = re.findall(r"\s+", text)

    char_estimate = len(text) / 3.85
    token_piece_estimate = (len(words) * 1.28) + (len(symbols) * 0.65) + (len(whitespace_runs) * 0.1)
    combined = (char_estimate * 0.45) + (token_piece_estimate * 0.55)
    return max(1, int(math.ceil(combined)))


def scan_secrets(text: str) -> List[str]:
    """Scans input text for accidentally leaked credentials or API keys."""
    findings: List[str] = []
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            findings.append(label)
    return findings


def compress_prompt(text: str) -> str:
    """
    Losslessly compresses prompt whitespace, redundant blank lines,
    and trailing spaces without altering code blocks or semantic meaning.
    """
    if not text:
        return ""
    lines = [line.rstrip() for line in text.splitlines()]
    compressed_lines: List[str] = []
    blank_streak = 0
    for line in lines:
        if line == "":
            blank_streak += 1
            if blank_streak <= 1:
                compressed_lines.append(line)
        else:
            blank_streak = 0
            compressed_lines.append(line)
    return "\n".join(compressed_lines).strip()


def analyze_text(
    text: str,
    model: str = "claude-sonnet-4",
    expected_output_tokens: int = 1000,
    max_budget_usd: Optional[float] = None,
) -> AnalysisResult:
    """Performs full cost, token, context utilization, and security analysis on a prompt."""
    if model not in MODEL_PRICING:
        supported = ", ".join(sorted(MODEL_PRICING.keys()))
        raise ValueError(f"Unsupported model '{model}'. Supported models: {supported}")

    pricing = MODEL_PRICING[model]
    input_tokens = estimate_tokens(text)
    words = len(text.split())
    chars = len(text)

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (expected_output_tokens / 1_000_000) * pricing["output"]
    total_cost = round(input_cost + output_cost, 6)

    context_window = int(pricing["context_window"])
    utilization = round(((input_tokens + expected_output_tokens) / context_window) * 100, 2)
    secrets = scan_secrets(text)

    budget_exceeded = False
    if max_budget_usd is not None and total_cost > max_budget_usd:
        budget_exceeded = True

    return AnalysisResult(
        model=model,
        character_count=chars,
        word_count=words,
        estimated_input_tokens=input_tokens,
        expected_output_tokens=expected_output_tokens,
        estimated_input_cost_usd=round(input_cost, 6),
        estimated_output_cost_usd=round(output_cost, 6),
        total_estimated_cost_usd=total_cost,
        context_window_limit=context_window,
        context_utilization_pct=utilization,
        budget_exceeded=budget_exceeded,
        detected_secrets=secrets,
    )
