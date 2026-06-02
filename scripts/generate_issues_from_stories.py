#!/usr/bin/env python3
"""Generate issue markdown files from docs/user_stories.md for stories marked Priority: High.

Creates files under docs/issues/ and can optionally call the GitHub API to create issues.

Usage:
  python scripts/generate_issues_from_stories.py [--create-remote]

Environment:
  GITHUB_TOKEN (optional) - if --create-remote is provided, used to authenticate to GitHub API.

This script is intentionally conservative and writes local files for review before remote creation.
"""
import os
import re
import sys
import textwrap
import json
from pathlib import Path
import argparse
import requests


ROOT = Path(__file__).resolve().parents[1]
STORIES = ROOT / "docs" / "user_stories.md"
OUT_DIR = ROOT / "docs" / "issues"


def parse_high_priority_blocks(text):
    # Find all occurrences of "Priority: High" and capture a block of up to 20 lines before it
    lines = text.splitlines()
    results = []
    for idx, line in enumerate(lines):
        if "Priority: High" in line:
            start = max(0, idx - 20)
            # find nearest blank line before start of block to get full story header
            for s in range(idx - 1, start - 1, -1):
                if lines[s].strip() == "":
                    start = s + 1
                    break
            block = []
            for j in range(start, idx + 1):
                block.append(lines[j])
            results.append("\n".join(block).strip())
    return results


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "story"


def extract_title(block: str) -> str:
    # Try first line that looks like a title (contains ':' or 'As a')
    for line in block.splitlines():
        if line.strip().startswith("US-"):
            # e.g., US-041 | Epic: Test Generation | Title: Generate test plan from natural language
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                return parts[2].replace("Title:", "").strip()
            return line.strip()
        if line.strip().lower().startswith("as a "):
            # use the next non-empty line as title if available
            continue
    # fallback: first non-empty line
    for line in block.splitlines():
        if line.strip():
            return line.strip()
    return "User Story"


def make_issue_md(title: str, body: str, idx: int) -> str:
    content = f"---\nlayout: issue\n---\n\n# {title}\n\n{body}\n"
    return content


def write_issue_files(blocks):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for i, block in enumerate(blocks, start=1):
        title = extract_title(block)
        slug = slugify(title)[:60]
        filename = OUT_DIR / f"{i:03d}-{slug}.md"
        md = make_issue_md(title, textwrap.dedent(block), i)
        filename.write_text(md, encoding="utf-8")
        created.append(filename)
    return created


def create_github_issue(token: str, repo: str, title: str, body: str, labels=None):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Failed to create issue: {r.status_code} {r.text}")
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-remote", action="store_true", help="Create issues on GitHub using GITHUB_TOKEN and REPO env vars")
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY"), help="repository (owner/repo)")
    args = parser.parse_args()

    if not STORIES.exists():
        print(f"Stories file not found: {STORIES}")
        sys.exit(1)
    text = STORIES.read_text(encoding="utf-8")
    blocks = parse_high_priority_blocks(text)
    if not blocks:
        print("No 'Priority: High' stories found in user_stories.md")
        sys.exit(0)
    created = write_issue_files(blocks)
    print(f"Wrote {len(created)} issue files under {OUT_DIR}")

    if args.create_remote:
        token = os.getenv("GITHUB_TOKEN")
        repo = args.repo
        if not token or not repo:
            print("GITHUB_TOKEN and repo are required to create remote issues. Set env vars or pass --repo.")
            sys.exit(2)
        for md in created:
            txt = md.read_text(encoding="utf-8")
            title_line = txt.splitlines()[2] if len(txt.splitlines()) > 2 else md.stem
            title = title_line.lstrip("# ").strip()
            body = "\n".join(txt.splitlines()[4:])
            print(f"Creating issue: {title}")
            try:
                resp = create_github_issue(token, repo, title, body, labels=["user-story", "priority:high"])
                print(f"Created issue #{resp['number']}: {resp['html_url']}")
            except Exception as e:
                print(f"Failed to create issue for {md}: {e}")


if __name__ == "__main__":
    main()
