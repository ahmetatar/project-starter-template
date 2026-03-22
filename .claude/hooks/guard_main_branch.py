#!/usr/bin/env python3
"""
guard_main_branch.py
Blocks dangerous direct operations on the main branch.
Runs as a PreToolUse hook for Bash tool calls.
"""

import sys
import json
import subprocess

def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps({"decision": "allow"}))
        return

    cmd = input_data.get("tool_input", {}).get("command", "")
    current_branch = get_current_branch()

    blocked_patterns = [
        # Committing while on main
        ("git commit" in cmd and current_branch == "main",
         "You are on 'main'. Commits must go to a story branch (story/S-XX-slug). "
         "Create the story branch first: git checkout -b story/[S-XX]-[slug]"),

        # Pushing directly to main
        ("git push" in cmd and "origin main" in cmd and "--no-ff" not in cmd,
         "Direct push to 'main' is not allowed. "
         "Use the merge workflow: git merge --no-ff story/[S-XX]-[slug]"),

        # Force push to main
        ("git push" in cmd and ("--force" in cmd or "-f" in cmd) and "main" in cmd,
         "Force push to 'main' is never allowed."),

        # Merge without --no-ff
        ("git merge" in cmd and "--no-ff" not in cmd and "story/" in cmd,
         "Story branch merges must use --no-ff to preserve history. "
         "Use: git merge --no-ff story/[S-XX]-[slug]"),
    ]

    for condition, reason in blocked_patterns:
        if condition:
            print(json.dumps({
                "decision": "block",
                "reason": f"🛑 Branch guard: {reason}"
            }))
            return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()