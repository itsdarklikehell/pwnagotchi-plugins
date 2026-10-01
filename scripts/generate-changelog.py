#!/usr/bin/env python3
"""
Generate CHANGELOG.md from git commit history.
Groups commits by type (feat, fix, docs, ci, chore, etc.) and formats them.
"""

import subprocess
import sys
import re
from collections import defaultdict
from datetime import datetime


def get_commits(since_tag=None):
    """Get commits from git log."""
    cmd = ["git", "log", "--pretty=format:%H|%s|%ad", "--date=short"]
    if since_tag:
        cmd.append(f"{since_tag}..HEAD")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running git log: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip().split("\n")


def parse_commit(line):
    """Parse a commit line into (hash, subject, date)."""
    parts = line.split("|", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def categorize_commit(subject):
    """Categorize a commit by its conventional commit type."""
    # Match conventional commit format: type(scope): subject
    match = re.match(r"^(\w+)(\([^)]*\))?:\s*(.+)", subject)
    if match:
        commit_type = match.group(1).lower()
        scope = match.group(2) or ""
        message = match.group(3)
        return commit_type, scope, message
    return "other", "", subject


def get_emoji_for_type(commit_type):
    """Get emoji for commit type."""
    emojis = {
        "feat": "✨",
        "fix": "🐛",
        "docs": "📚",
        "style": "💎",
        "refactor": "♻️",
        "perf": "⚡",
        "test": "🧪",
        "ci": "🔧",
        "chore": "🔨",
        "build": "📦",
        "revert": "⏪",
    }
    return emojis.get(commit_type, "📝")


def generate_changelog(commits, version=None):
    """Generate changelog markdown from commits."""
    categorized = defaultdict(list)
    
    for line in commits:
        if not line.strip():
            continue
        parsed = parse_commit(line)
        if not parsed:
            continue
        hash_val, subject, date = parsed
        commit_type, scope, message = categorize_commit(subject)
        categorized[commit_type].append({
            "hash": hash_val[:7],
            "scope": scope,
            "message": message,
            "date": date,
        })
    
    # Build changelog
    lines = []
    version_str = version or "Unreleased"
    lines.append(f"## [{version_str}] - {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    
    # Order of sections
    type_order = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "ci", "chore", "build", "revert", "other"]
    type_names = {
        "feat": "Features",
        "fix": "Bug Fixes",
        "docs": "Documentation",
        "style": "Code Style",
        "refactor": "Refactoring",
        "perf": "Performance",
        "test": "Tests",
        "ci": "CI/CD",
        "chore": "Chores",
        "build": "Build",
        "revert": "Reverts",
        "other": "Other Changes",
    }
    
    for commit_type in type_order:
        if commit_type not in categorized:
            continue
        emoji = get_emoji_for_type(commit_type)
        lines.append(f"### {emoji} {type_names.get(commit_type, commit_type.title())}")
        lines.append("")
        for commit in categorized[commit_type]:
            scope_str = f"**{commit['scope']}** " if commit["scope"] else ""
            lines.append(f"- {scope_str}{commit['message']} ({commit['hash']})")
        lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate CHANGELOG.md from git history")
    parser.add_argument("--version", help="Version number for the changelog")
    parser.add_argument("--output", default="CHANGELOG.md", help="Output file")
    parser.add_argument("--since", help="Generate changelog since this tag")
    args = parser.parse_args()
    
    commits = get_commits(args.since)
    changelog = generate_changelog(commits, args.version)
    
    # Read existing changelog if it exists
    existing = ""
    try:
        with open(args.output, "r") as f:
            existing = f.read()
    except FileNotFoundError:
        pass
    
    # Prepend new changelog
    header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
    if existing:
        # Remove old header if present
        if existing.startswith("# Changelog"):
            existing = existing.split("\n\n", 2)[-1] if "\n\n" in existing else ""
        new_content = header + changelog + "\n" + existing
    else:
        new_content = header + changelog + "\n"
    
    with open(args.output, "w") as f:
        f.write(new_content)
    
    print(f"Changelog written to {args.output}")


if __name__ == "__main__":
    main()
