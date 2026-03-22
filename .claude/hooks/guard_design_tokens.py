#!/usr/bin/env python3
"""
guard_design_tokens.py
Blocks hardcoded hex colours and font sizes in Swift view files.
Runs as a PreToolUse hook for Write, Edit, and MultiEdit tool calls.
"""

import sys
import json
import re

# Patterns that indicate hardcoded values in Swift files
BLOCKED_PATTERNS = [
    (r'Color\(hex:\s*"#[0-9A-Fa-f]{3,8}"',
     "Hardcoded hex colour via Color(hex:). Use AppColor.* tokens instead."),

    (r'"#[0-9A-Fa-f]{6}"',
     "Raw hex string detected. Use AppColor.* semantic colour tokens."),

    (r'\.foregroundColor\(\.init\(red:',
     "Raw RGB colour value. Use AppColor.* tokens from design-system.md."),

    (r'Font\.system\(size:\s*\d+',
     "Hardcoded font size. Use AppFont.* tokens (e.g. AppFont.body, AppFont.headline)."),

    (r'\.padding\(\s*\d+\s*\)',
     "Hardcoded padding value. Use AppSpacing.* tokens (e.g. AppSpacing.md)."),

    (r'\.cornerRadius\(\s*\d+\s*\)',
     "Hardcoded corner radius. Use AppRadius.* tokens (e.g. AppRadius.md)."),
]

SWIFT_VIEW_INDICATORS = ["View", "SwiftUI", "import SwiftUI", "var body:"]

def is_swift_view_file(path: str, content: str) -> bool:
    if not path.endswith(".swift"):
        return False
    # Only enforce in UI view files, not in token definition files
    if "AppTokens" in path or "Tokens" in path or "Extensions" in path:
        return False
    return any(indicator in content for indicator in SWIFT_VIEW_INDICATORS)

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit", "create_file", "str_replace"):
        print(json.dumps({"decision": "allow"}))
        return

    tool_input = input_data.get("tool_input", {})
    path = tool_input.get("path", "") or tool_input.get("file_path", "")
    content = (
        tool_input.get("file_text", "") or
        tool_input.get("new_str", "") or
        tool_input.get("content", "")
    )

    if not content or not is_swift_view_file(path, content):
        print(json.dumps({"decision": "allow"}))
        return

    violations = []
    for pattern, message in BLOCKED_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            violations.append(f"• {message}\n  Found: {matches[0]}")

    if violations:
        violation_text = "\n".join(violations)
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"🎨 Design token guard — hardcoded values detected in {path}:\n\n"
                f"{violation_text}\n\n"
                f"See docs/ui/design-system.md for the correct token to use."
            )
        }))
        return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()