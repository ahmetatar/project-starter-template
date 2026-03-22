#!/usr/bin/env python3
"""
log_failures.py
PostToolUse hook — logs tool failures to docs/agent-log/failures.jsonl
and checks if a pattern (3+ identical failures) has emerged.

When a pattern is detected, it writes a pending rule proposal to
docs/agent-log/pending-rules.jsonl for the agent to review and confirm.
"""

import sys
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
FAILURE_LOG   = Path("docs/agent-log/failures.jsonl")
PENDING_RULES = Path("docs/agent-log/pending-rules.jsonl")
PATTERN_THRESHOLD = 3   # how many identical failures trigger a rule proposal

# Minimum error text length to bother logging — filters out trivial/empty failures
MIN_ERROR_LENGTH = 10

# ── Helpers ───────────────────────────────────────────────────────────────────

def fingerprint(tool_name: str, error_text: str) -> str:
    """
    Produce a stable short fingerprint for a (tool, error) pair.
    Strips variable parts like device IDs, paths, timestamps.
    """
    # Remove UUIDs
    cleaned = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<uuid>', error_text, flags=re.I)
    # Remove absolute paths (keep last two path components)
    cleaned = re.sub(r'(/[\w./-]+/)+([\w.-]+)', r'<path>/\2', cleaned)
    # Remove line numbers
    cleaned = re.sub(r':\d+:\d+', ':<line>', cleaned)
    # Truncate to first 120 chars for fingerprint stability
    cleaned = cleaned[:120].strip()
    return f"{tool_name}|{cleaned}"


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


def append_jsonl(path: Path, entry: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def existing_rule_fingerprints() -> set:
    """Return fingerprints that already have a pending or confirmed rule."""
    rules = load_jsonl(PENDING_RULES)
    return {r["fingerprint"] for r in rules}


def check_patterns(new_fingerprint: str) -> dict | None:
    """
    Count occurrences of this fingerprint in the failure log.
    If >= PATTERN_THRESHOLD, return the pattern data.
    """
    failures = load_jsonl(FAILURE_LOG)
    matches = [f for f in failures if f.get("fingerprint") == new_fingerprint]
    if len(matches) >= PATTERN_THRESHOLD:
        return {
            "count": len(matches),
            "first_seen": matches[0]["timestamp"],
            "last_seen": matches[-1]["timestamp"],
            "tool": matches[-1]["tool"],
            "error_sample": matches[-1]["error_text"][:300],
            "context_sample": matches[-1].get("context", ""),
        }
    return None


def build_rule_suggestion(pattern: dict, fingerprint: str) -> dict:
    """Construct a pending rule entry for agent review."""
    return {
        "fingerprint": fingerprint,
        "status": "pending",          # pending → confirmed → dismissed
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": pattern["tool"],
        "occurrence_count": pattern["count"],
        "first_seen": pattern["first_seen"],
        "last_seen": pattern["last_seen"],
        "error_sample": pattern["error_sample"],
        "suggested_rule": "",          # agent fills this in during review
        "context_clue": pattern["context_sample"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
    except Exception:
        return

    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    response   = data.get("tool_response", {})

    # Only log failures
    is_error = (
        response.get("is_error", False)
        or "error" in str(response.get("content", "")).lower()[:100]
        or "failed" in str(response.get("content", "")).lower()[:100]
        or response.get("exit_code", 0) != 0
    )
    if not is_error:
        return

    # Skip trivially short errors — not useful for pattern learning
    content_preview = str(response.get("content", ""))
    if len(content_preview.strip()) < MIN_ERROR_LENGTH:
        return

    # Extract error text
    content = response.get("content", "")
    if isinstance(content, list):
        error_text = " ".join(
            c.get("text", "") if isinstance(c, dict) else str(c)
            for c in content
        )
    else:
        error_text = str(content)

    # Build failure entry
    fp = fingerprint(tool_name, error_text)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "fingerprint": fp,
        "error_text": error_text[:500],
        "context": str(tool_input)[:200],
    }

    # Append to failure log
    append_jsonl(FAILURE_LOG, entry)

    # Check if pattern threshold reached and no rule exists yet
    if fp not in existing_rule_fingerprints():
        pattern = check_patterns(fp)
        if pattern:
            rule_entry = build_rule_suggestion(pattern, fp)
            append_jsonl(PENDING_RULES, rule_entry)

            # Signal to the agent via stdout
            print(json.dumps({
                "type": "pattern_detected",
                "message": (
                    f"⚠️  Pattern detected: '{tool_name}' has failed {pattern['count']} times "
                    f"with the same error. A rule proposal has been added to "
                    f"docs/agent-log/pending-rules.jsonl. Run `/learn` to review and confirm."
                )
            }))


if __name__ == "__main__":
    main()