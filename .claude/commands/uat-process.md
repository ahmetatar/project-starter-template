Read CLAUDE.md to load project context.

Use the uat-feedback-processor skill to process the UAT feedback for story $ARGUMENTS.

The skill will:
1. Read docs/uat/$ARGUMENTS-uat.md
2. Read docs/stories/$ARGUMENTS*.md
3. Read docs/qa/$ARGUMENTS*-qa-report.md
4. Classify and summarise all findings
5. Ask for confirmation before applying any fixes
6. Process Blocker and Fix Now items on the story branch
7. Create issue files for Log as Issue items
8. Confirm merge readiness with the user