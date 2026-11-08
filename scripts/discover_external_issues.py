#!/usr/bin/env python3
"""Finds active, recently updated external Python/AI issues labeled 'good first issue' with 0 linked PRs."""

import json
import subprocess
import sys


def discover_issues(limit: int = 15) -> None:
    # Get current user to filter out self-owned repos
    user_res = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True)
    current_user = user_res.stdout.strip() if user_res.returncode == 0 else ""

    cmd = [
        "gh",
        "search",
        "issues",
        "--label",
        "good first issue",
        "--language",
        "python",
        "--state",
        "open",
        "--no-assignee",
        "--sort",
        "updated",
        "--limit",
        str(limit * 2),
        "--json",
        "repository,title,url,number,updatedAt,labels",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    raw_issues = json.loads(result.stdout)

    # Filter out own repo so it highlights truly external issues
    issues = [
        item for item in raw_issues
        if not (current_user and item["repository"]["nameWithOwner"].startswith(f"{current_user}/"))
    ][:limit]

    print(f"=== Found {len(issues)} Active External 'Good First Issues' ===")
    for idx, item in enumerate(issues, 1):
        repo_name = item["repository"]["nameWithOwner"]
        title = item["title"]
        url = item["url"]
        print(f"{idx:02d}. [{repo_name}] {title}")
        print(f"    URL: {url}")


if __name__ == "__main__":
    try:
        discover_issues()
    except Exception as exc:
        print(f"Error searching issues: {exc}", file=sys.stderr)
        sys.exit(1)
