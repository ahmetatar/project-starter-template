Read CLAUDE.md to load project context.

Read all files in docs/issues/ with Status: Open.

Present a triage table:

```
Open Issues — PO Triage ([count] total)

| ID | Title | Source Story | Severity | Suggested Action |
|---|---|---|---|---|
| 001 | ... | S-05 | Moderate | New story in P2 |
```

For each issue, suggest one of:
- **New story**: warrants its own BA story — estimate P1/P2/P3
- **Attach to feature**: belongs to an existing feature in the backlog
- **Dismiss**: not worth pursuing — explain why

Ask the user to confirm the action for each issue.
For "New story" decisions: update the issue file Status to "In Progress" and note
that BA Agent should be run to create the story.
For "Dismiss" decisions: update the issue file Status to "Closed" with a note.