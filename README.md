# Warp + Claude Code — Full Team Workflow

## How It Works

This project uses three complementary layers to automate the development workflow:

| Layer | What it is | Where it lives |
|---|---|---|
| **Skills** | Specialized AI agents with deep role knowledge | `skills/` → installed to `~/.claude/skills/` |
| **Slash Commands** | Thin wrappers that invoke skills with story context | `.claude/commands/` |
| **Hooks** | Pre/post-tool guardrails and learning system | `.claude/hooks/` |

Slash commands are the primary interface. Each command loads the right skill, validates prerequisites, and drives the agent for that phase.

---

## Setup

### Quick Start

```bash
bash setup.sh
```

`setup.sh` does three things automatically:

| Step | What it installs | Destination |
|---|---|---|
| Skills | All `skills/*/` folders | `~/.claude/skills/` |
| Warp Workflows | All `.warp/workflows/*.yml` | `~/.warp/workflows/` |
| MCP Servers | XcodeBuildMCP + xcode (mcpbridge) | Claude Code user config |

After running setup, open a new Claude Code session from the project directory — slash commands and hooks load automatically.

### Hooks (`.claude/settings.json`)

Hooks are already configured in `.claude/settings.json`. No manual editing needed after `setup.sh`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/guard_main_branch.py" }]
      },
      {
        "matcher": "Write|Edit|MultiEdit|create_file|str_replace",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/guard_design_tokens.py" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/log_failures.py" }]
      }
    ]
  }
}
```

Use `/update-config` to modify hook configuration through Claude Code instead of editing the file manually.

### XcodeBuildMCP (`.xcodebuildmcp/config.yml`)

```yaml
enabledWorkflows:
  - simulator
  - device
  - project-discovery
```

Enables simulator, physical device, and project discovery workflows. See [XcodeBuildMCP configuration docs](https://github.com/getsentry/XcodeBuildMCP/blob/main/docs/CONFIGURATION.md) to enable additional workflows (debugging, UI automation, etc.).

---

## Slash Commands

### Workflow Commands

```
PO   → /po-analyze          → market_analysis_report.md + feature_backlog.md
       /design-init         → docs/ui/design-system.md (once per project)
BA   → /ba-breakdown        → F-XXX feature summary + S-XX story files
UX   → /ux-spec             → S-XX UX spec (stories with UI only)
UI   → /ui-design           → SwiftUI views + ViewModel shells + UI handoff
Dev  → /story-plan          → implementation plan (no code, review first)
       /story-start         → branch + implement (UI-first if needed)
       /quick-test          → run tests, show summary
       /story-diff          → summarize branch changes
       /qa-handoff          → prepare QA handoff document
QA   → /qa-review           → independent test run + AC verification + approve/reject
UAT  → "UAT feedback ready" → uat-feedback-processor skill → merge or fix
```

### Utility Commands

| Command | What it does |
|---|---|
| `/story-status S-XX` | Quick status check across all phases for a story |
| `/story-diff S-XX` | Concise diff summary vs main |
| `/quick-test` | Run tests and show pass/fail summary |
| `/sprint-status` | Show status of all active stories in the sprint |
| `/issue-triage` | List and triage open issue files |
| `/uat-start S-XX` | Load UAT context for manual testing |
| `/uat-process S-XX` | Process a completed UAT feedback file |
| `/learn` | Review agent failure patterns and confirm rules to CLAUDE.md |

### How to invoke

Type a slash command inside Claude Code interactive mode:

```
claude
> /story-plan S-01
```

Pass story IDs as arguments — the command substitutes `$ARGUMENTS` automatically.

---

## Skills

Skills are the agent implementations behind each slash command. They contain the role logic, output format rules, and prerequisite validation. You can also invoke them directly by describing what you need:

| Skill | Role | Direct trigger |
|---|---|---|
| `po-market-analyst` | Product Owner | "analyze app store category", "competitor research" |
| `product-intake` | Product Owner | "I have an idea", "add this feature", "users are asking for" |
| `design-foundation` | Product Designer | "create design system", "design tokens" |
| `ba-feature-analyst` | Business Analyst | "break down feature", "write user stories" |
| `ux-story-designer` | UX Designer | "ux spec for story", "wireframe this" |
| `ui-designer-ios` | UI Designer | "build the ui", "swiftui implementation" |
| `dev-story-implementer` | Developer | "implement story", "start development" |
| `qa-story-verifier` | QA Engineer | "qa this story", "verify story" |
| `uat-feedback-processor` | UAT Processor | "UAT feedback ready", "process UAT for S-XX" |

**Slash commands vs skills:** Slash commands are the preferred way to invoke skills — they pass story context automatically and enforce the workflow order. Calling a skill directly is equivalent but skips the auto-argument substitution.

---

## Hooks

Hooks are Python scripts that run automatically before or after tool calls. They enforce project rules and power the agent learning system.

### PreToolUse: `guard_main_branch.py`

**Trigger:** Before any `Bash` tool call
**Purpose:** Blocks unsafe git operations on the `main` branch

| Blocked operation | Reason |
|---|---|
| `git commit` while on `main` | All commits must go to a `story/S-XX-slug` branch |
| `git push origin main` (direct) | Use merge workflow instead |
| `git push --force ... main` | Force push to main is never allowed |
| `git merge story/...` without `--no-ff` | Story merges must preserve history with `--no-ff` |

When blocked, the hook explains exactly what to run instead.

### PreToolUse: `guard_design_tokens.py`

**Trigger:** Before any `Write`, `Edit`, `MultiEdit`, `create_file`, or `str_replace` tool call on `.swift` files
**Purpose:** Blocks hardcoded style values in SwiftUI view files

| Blocked pattern | Correct alternative |
|---|---|
| `Color(hex: "#...")` | `AppColor.*` semantic token |
| Raw hex string `"#RRGGBB"` | `AppColor.*` semantic token |
| `.foregroundColor(.init(red:...))` | `AppColor.*` semantic token |
| `Font.system(size: 16)` | `AppFont.*` token (e.g. `AppFont.body`) |
| `.padding(12)` | `AppSpacing.*` token (e.g. `AppSpacing.md`) |
| `.cornerRadius(8)` | `AppRadius.*` token (e.g. `AppRadius.md`) |

Does not apply to token definition files (`AppTokens`, `Tokens`, `Extensions`).
See `docs/ui/design-system.md` for the full token reference.

### PostToolUse: `log_failures.py`

**Trigger:** After every tool call
**Purpose:** Logs tool failures to `docs/agent-log/failures.jsonl` and detects recurring patterns

When the same error occurs 3+ times, a rule proposal is written to `docs/agent-log/pending-rules.jsonl` and the agent is notified. Run `/learn` to review and confirm pending rules — confirmed rules are written automatically to the `## Learned Rules` section of `CLAUDE.md`.

### Support scripts (called by `/learn`)

| Script | What it does |
|---|---|
| `analyze_patterns.py` | Reads failure + pending-rules logs, produces a human-readable pattern report |
| `confirm_rule.py` | Marks a rule as confirmed/dismissed and appends it to `CLAUDE.md` |

---

## Doc Structure

```
docs/
  market_analysis_report.md       ← PO: market analysis output
  feature_backlog.md              ← PO: prioritised feature list (F-XXX)
  features/
    [F-XXX]-[slug].md             ← BA: feature summary + stories overview
  stories/
    [S-XX]-[slug].md              ← BA: individual story files
  ux/
    [S-XX]-[slug]-ux.md           ← UX: screen specs per story
  ui/
    design-system.md              ← Design Foundation: single source of truth
    [S-XX]-[slug]-ui-handoff.md   ← UI: SwiftUI files + ViewModel notes for Dev
  qa/
    [S-XX]-[slug]-qa-handoff.md   ← Dev → QA handoff
    [S-XX]-[slug]-qa-report.md    ← QA verdict (APPROVED / REJECTED)
  uat/
    [S-XX]-[slug]-uat.md          ← UAT feedback (human fills, uat-feedback-processor reads)
  issues/
    [S-XX]-issue-[NNN]-[slug].md  ← Open issues from UAT
  intake/
    [YYYY-MM-DD]-[slug].md        ← product-intake reports
  agent-log/
    failures.jsonl                ← tool failure log (auto-written by PostToolUse hook)
    pending-rules.jsonl           ← rule proposals awaiting /learn confirmation
```

---

## Full Project Lifecycle

### Phase 1 — Project Setup (once)
**Warp Workflow: `Project Init`** (`Ctrl+Shift+R` → Project Init)

```
Warp asks: category, market
  ↓ runs /po-analyze → market_analysis_report.md + feature_backlog.md
  ↓ runs /design-init → docs/ui/design-system.md
```

### Phase 2 — Feature Breakdown (per feature)
**Warp Workflow: `Feature Cycle`** (`Ctrl+Shift+R` → Feature Cycle)

```
Warp asks: feature_id
  ↓ runs /ba-breakdown → feature summary + story files
  ↓ auto-detects stories with "Needs UX Spec: Yes"
  ↓ runs /ux-spec for each UI story → UX specs
  ↓ runs /ui-design for each UI story → SwiftUI views + ViewModel shells
```

### Phase 3 — Design (per story with UI)

```
/ux-spec S-05
  ↓ produces UX spec (screens, states, components)
/ui-design S-05
  ↓ produces SwiftUI views + ViewModel shells + UI handoff
```

### Phase 4 — Development (per story)
**Warp Workflow: `Story Cycle`** (`Ctrl+Shift+R` → Story Cycle)

```
Warp asks: story_id
  ↓ runs /story-plan → implementation plan (pauses for your review)
  ↓ you press Enter to approve
  ↓ runs /story-start → branch + implement
  ↓ runs /quick-test → verify tests pass
  ↓ runs /qa-handoff → prepare QA document
```

### Phase 5 — Quality & Release (per story)
**Warp Workflow: `QA & UAT`** (`Ctrl+Shift+R` → QA & UAT)

```
Warp asks: story_id
  ↓ runs /qa-review → independent QA review
  ↓ pauses: you test on device via TestFlight
  ↓ you fill UAT file, press Enter
  ↓ runs uat-feedback-processor → fix/merge/fail
```

### Adding Features to an Existing Product

```
"I have an idea" / "add this feature"
  ↓ product-intake skill → updated feature_backlog.md + optional intake report
  ↓ /ba-breakdown F-XXX → story files
  ↓ continue from Phase 3
```

---

## Dependency Chain

Each command validates its prerequisites before starting. If something is missing, it stops and tells you exactly what to run first:

```
/po-analyze
  └── /design-init (requires PO output)
       └── /ba-breakdown (requires backlog)
            └── /ux-spec (requires story file + design system)
                 └── /ui-design (requires UX spec + design system)
                      └── /story-plan (requires story file)
                           └── /story-start (requires approved plan + UI if needed)
                                └── /qa-handoff (requires passing tests)
                                     └── /qa-review (requires QA handoff)
                                          └── UAT (requires QA approval)
                                               └── merge (requires UAT pass)
```

Stories without UI skip `/ux-spec` and `/ui-design` — they go straight from `/ba-breakdown` to `/story-plan`.

---

## Warp Split Pane Layout

```
┌─────────────────────────────┬───────────────────────────────┐
│  LEFT PANE (Claude Code)    │  RIGHT PANE (Monitoring)      │
│                             │                               │
│  claude                     │  # Read docs                  │
│  > /story-plan S-05         │  cat docs/stories/S-05*.md    │
│                             │                               │
│  [review plan, approve]     │  # Watch tests                │
│                             │  swift test 2>&1 | tail -20   │
│  > /story-start S-05        │                               │
│                             │  # Track changes              │
│  [implementation ongoing]   │  watch -n 5 git diff --stat   │
│                             │                               │
│  > /quick-test              │  # Review QA handoff          │
│  > /qa-handoff S-05         │  cat docs/qa/S-05*.md         │
└─────────────────────────────┴───────────────────────────────┘
```

Open with `Cmd+D` (vertical split). Left: `claude` interactive. Right: monitoring.

---

## Warp Shortcuts

| Shortcut | What it does |
|---|---|
| `Cmd+D` | Split pane vertically |
| `Cmd+Shift+D` | Split pane horizontally |
| `Cmd+W` | Close active pane |
| `Ctrl+Shift+R` | Workflow menu |
| `Cmd+F` | Search within block |
| `#` + command | Warp AI — quick terminal command suggestion |
| `Cmd+K` | Command palette |

---

## Tips

1. **Run `bash setup.sh` once** — it installs skills, Warp workflows, and MCP servers in one shot.

2. **Run PO and Design Init only once per project** — these establish the foundation.
   All other commands run per-feature or per-story.

3. **Use `product-intake` for new ideas mid-project** — when the backlog already exists and you want to add a feature, describe your idea naturally and the skill will structure, prioritize, and add it.

4. **The dependency chain protects you** — every command checks its prerequisites.
   You can't accidentally skip a step. If you try `/story-start` without a plan, it stops and tells you.

5. **Hooks are silent when everything is correct** — you only see them when they block.
   If a hook fires, read its message — it tells you exactly what to fix.

6. **Use `/learn` periodically** — the `log_failures.py` hook tracks recurring errors silently.
   `/learn` surfaces patterns and proposes rules. Confirmed rules land in `CLAUDE.md` automatically.

7. **Keep Claude Code in interactive mode** — slash commands benefit from conversation context.
   Use `-p` flag only for one-off queries.

8. **Right pane for monitoring** — while Claude Code runs in the left pane, use
   `watch -n 5 git diff --stat` or `cat docs/...` on the right.

9. **Stories without UI are faster** — they skip UX and UI phases entirely.
   The flow is: `/ba-breakdown` → `/story-plan` → `/story-start` → `/qa-handoff` → `/qa-review`.

10. **UAT is always human-in-the-loop** — no command bypasses this. The
    `uat-feedback-processor` skill handles feedback processing after you test on device.

11. **Switching between stories** — check current status with `/story-status S-XX`
    before switching. Commit unfinished work first.
