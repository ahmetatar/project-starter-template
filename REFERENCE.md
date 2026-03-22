# Project Reference — [App Name]

## Full Doc Structure

```
docs/
  market_analysis_report.md         ← PO: market analysis output
  feature_backlog.md                ← PO: prioritised feature list (F-XXX)
  design-system.md                  ← Design Foundation: single source of truth
                                       (read before ANY UI/UX work)
  features/
    [F-XXX]-[feature-slug]/
      feature-analysis.md           ← BA: feature summary + stories overview
      stories/
        [S-XX]-[story-slug]/
          story-plan.md             ← BA: story file (ACs, edge cases, UX flag)
          ux.md                     ← UX: screen spec (if Needs UX Spec: Yes)
          ui-handoff.md             ← UI: SwiftUI files + ViewModel notes for Dev
          qa-handoff.md             ← Dev → QA handoff
          qa-report.md              ← QA verdict (APPROVED / REJECTED)
          uat.md                    ← UAT feedback (human fills, processor reads)

  issues/
    [S-XX]-issue-[NNN]-[slug].md    ← Open issues from UAT (global, not per-feature)
  intake/
    [YYYY-MM-DD]-[slug].md          ← product-intake reports
  agent-log/
    failures.jsonl                  ← tool failure log (auto-written by hook)
    pending-rules.jsonl             ← rule proposals awaiting /learn confirmation

.claude/
  settings.json                     ← hook configuration
  commands/                         ← slash commands
    story-start.md
    story-status.md
    uat-start.md
    uat-process.md
    sprint-status.md
    issue-triage.md
    learn.md
  hooks/
    guard_main_branch.py            ← PreToolUse: blocks direct main commits
    guard_design_tokens.py          ← PreToolUse: blocks hardcoded values in Swift
    log_failures.py                 ← PostToolUse: logs tool failures, detects patterns
    analyze_patterns.py             ← called by /learn to generate pattern report
    confirm_rule.py                 ← called by /learn to write confirmed rules to CLAUDE.md
```

---

## Example: F-002 Parent Approval Flow

```
docs/features/F-002-parent-approval-flow/
  feature-analysis.md
  stories/
    S-01-child-submits-session/
      story-plan.md
      ux.md
      ui-handoff.md
      qa-handoff.md
      qa-report.md
      uat.md
    S-02-parent-pending-list/
      story-plan.md
      ux.md
      ui-handoff.md
      qa-handoff.md
      qa-report.md
      uat.md
    S-04-coin-credit-on-approval/
      story-plan.md
      qa-handoff.md    ← no ux.md or ui-handoff.md (Needs UX Spec: No)
      qa-report.md
      uat.md
```

---

## Personas

- **Ayşe (child, 7):** Primary child user. Responds to rewards, streaks, big colourful visuals. Cannot read the parent panel.
- **Murat (parent, 35):** Downloads app at 9pm. Wants 3-minute setup. Approves sessions during commute.
- **Fatma (parent, 38):** Uses physical library books. Proud of streaks — shares with family.

---

## Workflow Summary

**Initial product setup:**
```
po-market-analyst → po-backlog → design-foundation → ba-feature-analyst
→ ux-story-designer → ui-designer-ios → dev-story-implementer
→ qa-story-verifier → uat-feedback-processor → merge
```

**Adding new features (ongoing):**
```
product-intake → ba-feature-analyst → ux-story-designer → ui-designer-ios
→ dev-story-implementer → qa-story-verifier → uat-feedback-processor → merge
```

---

## Current Sprint

**Sprint goal:** P0 stories — launch blocker features
**Last updated:** [update this date when stories change]

| ID | Story | Feature | Status |
|---|---|---|---|
| S-01 | Child submits reading session | F-002 | Not Started |
| S-02 | Parent views pending approvals | F-002 | Not Started |
| S-03 | Parent approves or rejects | F-002 | Not Started |
| S-04 | Coin reward credited on approval | F-002 | Not Started |
| S-05 | Child views approval result | F-002 | Not Started |
| S-06 | Parent rejects with a note | F-002 | Not Started |
| S-07 | Approval request expires after 48h | F-002 | Not Started |

> Run `/sprint-status` for a live view generated from story files.