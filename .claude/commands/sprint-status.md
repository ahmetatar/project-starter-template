Read CLAUDE.md to load project context.

Read all files in docs/stories/ as follows:
- For each story file, read ONLY the header lines (first 6 lines) to get: ID, title, Status
- Do NOT load the full content of any story file — only the status metadata
- Exception: if a story is "In Progress", also read its current phase/last commit note if present

Group stories by Status and output a sprint health summary:

```
Sprint Status — [today's date]

✅ Done ([count]):
  [S-XX] Title

🔄 In Progress ([count]):
  [S-XX] Title — [current phase: Dev / QA / UAT]

⬜ Not Started ([count]):
  [S-XX] Title

🐛 Open Issues: [count from docs/issues/ — Status: Open only]

Velocity: [done] / [total] stories complete
Next up: [first Not Started story]
```

Important: Read only story metadata (first 6 lines per file), not full story content.
This keeps context lean regardless of how many stories exist.