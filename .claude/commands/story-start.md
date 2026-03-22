# Story Start — Branch & Implement

Act as the **Developer Agent** using the `dev-story-implementer` skill.

Begin implementation for story **$ARGUMENTS** after the plan has been reviewed.

## Pre-checks

1. Confirm that `/story-plan $ARGUMENTS` was already run and the plan was approved
2. If no plan exists in conversation history, STOP and say:
   "You must run `/story-plan $ARGUMENTS` first and approve the plan before starting."
3. Read the story file: `docs/stories/$ARGUMENTS*.md`
4. If `Needs UX Spec: Yes`:
   - `docs/ux/$ARGUMENTS*-ux.md` must exist → if not: STOP → "Run `/ux-spec $ARGUMENTS` first."
   - `docs/ui/$ARGUMENTS*-ui-handoff.md` must exist → if not: STOP → "Run `/ui-design $ARGUMENTS` first."

## Workflow

1. `git checkout main && git pull`
2. Create branch: `git checkout -b story/$ARGUMENTS-[slug]`
3. Follow the implementation phases from the approved plan:
   - **Phase 2 (UI)** — if `Needs UX Spec: Yes`: integrate the SwiftUI views from UI Designer Agent.
     Fill ViewModel placeholders with real business logic. Do not rewrite UI — adapt logic to it.
   - **Phase 3 (Business Logic)** — implement against the UI scaffold (if UI exists) or standalone
   - **Phase 4 (Tests)** — unit, integration, UI tests. Every AC and edge case covered.
4. Commit after each logical unit with format: `[$ARGUMENTS] description`

## Rules

- Write at least one test for every AC
- Handle every edge case or explicitly flag it as out of scope
- Do not leave TODOs — implement or mark as scope-out
- Keep commits atomic
- No story is done with failing tests — fix the code, not the tests
- After all phases complete, run `/qa-handoff $ARGUMENTS` to prepare for QA