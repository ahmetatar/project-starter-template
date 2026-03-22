Read CLAUDE.md to load project context.

For story $ARGUMENTS:
1. Read docs/qa/$ARGUMENTS*-qa-report.md — confirm verdict is APPROVED.
   If not APPROVED: stop and tell the user QA must approve before UAT can start.

2. Read docs/stories/$ARGUMENTS*.md to get the story title and branch name.

3. Create the UAT feedback file at docs/uat/$ARGUMENTS-uat.md using the
   template from the dev-story-implementer skill (Section 5, UAT Feedback File Template).
   Pre-fill: story title, branch name, today's date.

4. Present the file path to the user and say:

"[S-XX] – [Story Title] Passed QA, ready for UAT. 🎉

Fill in the file: docs/uat/$ARGUMENTS-uat.md

Select the severity for each finding: Blocker / Fix Now / Log as Issue
Once finished, use this in a new session: /uat-process $ARGUMENTS"