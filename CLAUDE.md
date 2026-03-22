# Kitap Kurdu — Agent Team

## Project
Parent-child iOS app. Children log reading sessions, parents approve, children earn coin rewards.
**Market:** Turkey + MENA | **Language:** Turkish (Arabic v1.1) | **Platform:** iOS 17+

## Tech Stack
Swift 5.10 · SwiftUI · XCTest · CloudKit Public DB · StoreKit 2 · Xcode Cloud

## XcodeBuildMCP
Config: `.xcodebuildmcp/config.yaml` — enabledWorkflows: simulator, device, project-discovery
- `build_device` — zero-error gate before QA (no device needed)
- `build_run_device` — deploy to physical device at UAT start (device must be connected)
- `list_devices` — get UDID before build_run_device; never hardcode device names
 
## Skills
See individual SKILL.md files. Each skill reads its context from docs/ — no conversation history needed.
`po-market-analyst` · `po-backlog` · `product-intake` · `design-foundation` · `ba-feature-analyst`
`ux-story-designer` · `ui-designer-ios` · `dev-story-implementer` · `qa-story-verifier` · `uat-feedback-processor`
 
## Gates (each step requires the previous step's output files)
| Gate | Required |
|---|---|
| UX/UI work | `docs/design-system.md` exists |
| UX spec | `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/story-plan.md` exists |
| UI implementation | `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/ux.md` exists (UI stories) |
| Dev start | `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/ui-handoff.md` exists (UI stories) |
| QA handoff | `build_device` zero-error + `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/qa-handoff.md` |
| UAT start | `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/qa-report.md` verdict APPROVED + `build_run_device` success |
| Merge | `docs/features/[F-XXX]-[slug]/stories/[S-XX]-[slug]/uat.md` Status: Pass |
 
## Conventions
- Commit messages: `[S-XX] Description`
- Never hardcode hex values in Swift — use `AppColor.*`, `AppFont.*`, `AppSpacing.*` tokens
- Turkish strings hardcoded for MVP — wrap in `LocalizedStringKey` pre-launch
- Story status values: `Draft / In Progress / Done`
- Issue status values: `Open / In Progress / Closed`
- UAT status values: `In Progress / Pass / Fail`
- **Done stories:** If a story file has `**Status:** Done`, do not load its full content into context — read only the ID, title, and status line. Full content is only needed for active (Draft / In Progress) stories.
 
## Doc Structure
See `docs/REFERENCE.md` for full layout.
Key paths: `docs/features/[F-XXX]-[slug]/` · `docs/design-system.md` · `docs/issues/`
 
## Learned Rules
<!-- Confirmed via /learn command. Do not edit manually. -->
<!-- Format: [YYYY-MM-DD] **tool:** Rule. Source: N failures. -->
 