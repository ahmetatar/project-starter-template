#!/usr/bin/env python3
"""
analyze_patterns.py
Called by the /learn slash command.

Reads docs/agent-log/failures.jsonl and docs/agent-log/pending-rules.jsonl,
produces a human-readable pattern report, and prints it to stdout for the
agent to present to the user.

Usage:
  python3 .claude/hooks/analyze_patterns.py [--pending-only]
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

FAILURE_LOG   = Path("docs/agent-log/failures.jsonl")
PENDING_RULES = Path("docs/agent-log/pending-rules.jsonl")
CLAUDE_MD     = Path("CLAUDE.md")
LEARNED_RULES_MARKER = "## Learned Rules"

def load_jsonl(path: Path) -> list:
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


def format_pending_rules(pending: list) -> str:
    if not pending:
        return "No pending rule proposals."

    lines = ["## Pending Rule Proposals\n"]
    for i, rule in enumerate(pending, 1):
        lines.append(f"### [{i}] Tool: `{rule['tool']}`")
        lines.append(f"- **Occurrences:** {rule['occurrence_count']}x "
                     f"(first: {rule['first_seen'][:10]}, last: {rule['last_seen'][:10]})")
        lines.append(f"- **Error sample:**\n  ```\n  {rule['error_sample'][:200]}\n  ```")
        if rule.get("context_clue"):
            lines.append(f"- **Context clue:** `{rule['context_clue'][:150]}`")
        lines.append(f"- **Suggested rule:** *(agent should fill this in)*")
        lines.append(f"- **Fingerprint:** `{rule['fingerprint'][:60]}...`")
        lines.append("")
    return "\n".join(lines)


def format_top_failures(failures: list, top_n: int = 5) -> str:
    counts = defaultdict(list)
    for f in failures:
        counts[f["fingerprint"]].append(f)

    sorted_patterns = sorted(counts.items(), key=lambda x: -len(x[1]))[:top_n]

    if not sorted_patterns:
        return "No failures logged yet."

    lines = ["## Top Recurring Failures\n"]
    for fp, occurrences in sorted_patterns:
        sample = occurrences[-1]
        lines.append(f"### `{sample['tool']}` — {len(occurrences)}x")
        lines.append(f"- **Error:** {sample['error_text'][:150]}...")
        lines.append(f"- **Last seen:** {sample['timestamp'][:10]}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pending-only", action="store_true",
                        help="Only show pending rule proposals, skip failure stats")
    args = parser.parse_args()

    failures = load_jsonl(FAILURE_LOG)
    pending  = [r for r in load_jsonl(PENDING_RULES) if r.get("status") == "pending"]

    report_parts = [
        f"# Agent Learning Report",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Total failures logged: {len(failures)}",
        f"Pending rule proposals: {len(pending)}",
        "",
    ]

    if not args.pending_only:
        report_parts.append(format_top_failures(failures))

    report_parts.append(format_pending_rules(pending))

    if pending:
        report_parts += [
            "---",
            "## Next Steps",
            "",
            "For each pending rule, the agent should:",
            "1. Review the error sample and context clue",
            "2. Write a concise, actionable rule (one sentence)",
            "3. Ask the user to confirm the rule",
            "4. On confirmation: add it to CLAUDE.md under `## Learned Rules`",
            "   and update the rule status to `confirmed` in pending-rules.jsonl",
            "5. On dismissal: update the rule status to `dismissed`",
        ]

    print("\n".join(report_parts))


if __name__ == "__main__":
    main()