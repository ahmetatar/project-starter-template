#!/usr/bin/env python3
"""
confirm_rule.py
Called by the agent after the user confirms a rule proposal.

Usage:
  python3 .claude/hooks/confirm_rule.py \
    --fingerprint "<fp>" \
    --rule "build_run_device: Always call list_devices first and use the UDID, never hardcode device names." \
    --tool "mcp__XcodeBuildMCP__build_run_device"

Updates:
  1. docs/agent-log/pending-rules.jsonl  → status: confirmed
  2. CLAUDE.md → adds rule to ## Learned Rules section
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import date

PENDING_RULES = Path("docs/agent-log/pending-rules.jsonl")
CLAUDE_MD     = Path("CLAUDE.md")
MARKER        = "## Learned Rules"

def load_jsonl(path):
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def save_jsonl(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def update_claude_md(rule_text: str, tool: str):
    """Append the confirmed rule under ## Learned Rules in CLAUDE.md."""
    if not CLAUDE_MD.exists():
        print(f"WARNING: {CLAUDE_MD} not found. Rule not written to CLAUDE.md.", file=sys.stderr)
        return

    content = CLAUDE_MD.read_text()
    today = date.today().isoformat()
    new_rule_line = f"- [{today}] **{tool}:** {rule_text}"

    if MARKER in content:
        # Insert after the marker line
        parts = content.split(MARKER, 1)
        # Find the end of the marker line
        rest = parts[1]
        # Insert after the first newline following the marker
        nl_pos = rest.find("\n")
        if nl_pos == -1:
            updated = content + "\n" + new_rule_line + "\n"
        else:
            updated = (
                parts[0]
                + MARKER
                + rest[:nl_pos + 1]
                + new_rule_line + "\n"
                + rest[nl_pos + 1:]
            )
    else:
        # Append the entire section at the end
        updated = content.rstrip() + f"\n\n{MARKER}\n<!-- Agent-generated. Review before editing manually. -->\n{new_rule_line}\n"

    CLAUDE_MD.write_text(updated)
    print(f"✅ Rule added to {CLAUDE_MD}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--rule", required=True, help="The confirmed rule text (one sentence)")
    parser.add_argument("--tool", required=True, help="Tool name this rule applies to")
    parser.add_argument("--dismiss", action="store_true", help="Dismiss instead of confirm")
    args = parser.parse_args()

    entries = load_jsonl(PENDING_RULES)
    updated = False

    for entry in entries:
        if entry.get("fingerprint") == args.fingerprint and entry.get("status") == "pending":
            entry["status"] = "dismissed" if args.dismiss else "confirmed"
            entry["confirmed_rule"] = args.rule
            updated = True
            break

    if not updated:
        print(f"ERROR: No pending rule found with fingerprint: {args.fingerprint[:40]}...",
              file=sys.stderr)
        sys.exit(1)

    save_jsonl(PENDING_RULES, entries)

    if not args.dismiss:
        update_claude_md(args.rule, args.tool)
        print(f"Rule confirmed and written to CLAUDE.md.")
    else:
        print(f"Rule dismissed. It will not appear again.")


if __name__ == "__main__":
    main()