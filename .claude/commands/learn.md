Read CLAUDE.md to load project context.

Run the pattern analysis script and present its output to the user:

```bash
python3 .claude/hooks/analyze_patterns.py
```

If there are pending rule proposals, for each one:

1. Read the error sample and context clue carefully
2. Write a concise, actionable rule in one sentence — specific enough to prevent the exact
   failure, general enough to apply in future sessions. Good rule format:
   "Always [do X] before [tool Y] — [brief reason]."
3. Present it to the user:
   > "**Proposed rule [N]:**
   > `[Tool name]`: [your proposed rule text]
   >
   > Should I add this rule to CLAUDE.md? (Yes / No / Modify)"

4. If user confirms (Evet):
   Run the confirm script:
   ```bash
   python3 .claude/hooks/confirm_rule.py \
     --fingerprint "[fingerprint from report]" \
     --rule "[confirmed rule text]" \
     --tool "[tool name]"
   ```

5. If user dismisses (Hayır):
   Run with --dismiss flag:
   ```bash
   python3 .claude/hooks/confirm_rule.py \
     --fingerprint "[fingerprint]" \
     --rule "" \
     --tool "[tool name]" \
     --dismiss
   ```

6. If user wants to edit (Change):
   Ask for the corrected rule text, then confirm with the edited version.

After processing all pending rules, show a summary:
- X rules confirmed and added to CLAUDE.md
- Y rules dismissed

If there are no pending proposals, say:
"There's no pattern to learn right now. The failure log looks clean."

If the failure log does not exist yet:
"No errors have been logged yet. Failure logging will start automatically as tool errors occur."