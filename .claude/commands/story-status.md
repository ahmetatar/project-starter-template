# Story Status — Quick Check

Show the current status for story **$ARGUMENTS**.

## Check these in order

1. **Branch status**: `git branch --list "story/$ARGUMENTS*"` — does the branch exist?
2. **Story file**: `docs/stories/$ARGUMENTS*.md` — what is the Status field?
3. **QA handoff**: `docs/qa/$ARGUMENTS*.md` — does it exist, is it approved?
4. **UAT file**: `docs/uat/$ARGUMENTS*.md` — does it exist, what is the result?
5. **Issue files**: `docs/issues/$ARGUMENTS-issue-*` — any open issues?
6. **Test status**: find relevant test files and run them
7. **Last commit**: last commit message and date on the story branch

## Output Format

```
📋 Story: [S-XX] [Title]
🌿 Branch: story/[S-XX]-[slug] [exists/missing]
📝 Status: [from story file]
🧪 Tests: [X passed / Y failed / not run yet]
🔍 QA: [not started / pending / approved / rejected]
📱 UAT: [not started / in progress / pass / fail]
🐛 Issues: [X open]
📌 Last commit: [message] ([date])

➡️ Next step: [what to do next]
```