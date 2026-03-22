#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC}  $*"; }
error()   { echo -e "${RED}[error]${NC} $*"; exit 1; }

# ── 1. Claude Skills ──────────────────────────────────────────────────────────
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
REPO_SKILLS_DIR="$REPO_DIR/skills"

if [[ ! -d "$REPO_SKILLS_DIR" ]]; then
  warn "skills/ folder not found in repo, skipping."
else
  mkdir -p "$CLAUDE_SKILLS_DIR"
  copied=0
  skipped=0

  for skill_dir in "$REPO_SKILLS_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"
    dest="$CLAUDE_SKILLS_DIR/$skill_name"

    if [[ -d "$dest" ]]; then
      warn "Skill already exists, overwriting: $skill_name"
    fi

    cp -r "$skill_dir" "$dest"
    info "Installed skill: $skill_name"
    ((copied++)) || true
  done

  info "Skills installed: $copied  (destination: $CLAUDE_SKILLS_DIR)"
fi

# ── 2. Warp Workflows ─────────────────────────────────────────────────────────
WARP_WORKFLOWS_DIR="$HOME/.warp/workflows"
REPO_WORKFLOWS_DIR="$REPO_DIR/.warp/workflows"

if [[ ! -d "$REPO_WORKFLOWS_DIR" ]]; then
  warn ".warp/workflows/ folder not found in repo, skipping."
else
  mkdir -p "$WARP_WORKFLOWS_DIR"
  copied=0

  for workflow_file in "$REPO_WORKFLOWS_DIR"/*.yml "$REPO_WORKFLOWS_DIR"/*.yaml; do
    [[ -f "$workflow_file" ]] || continue
    workflow_name="$(basename "$workflow_file")"
    dest="$WARP_WORKFLOWS_DIR/$workflow_name"

    if [[ -f "$dest" ]]; then
      warn "Workflow already exists, overwriting: $workflow_name"
    fi

    cp "$workflow_file" "$dest"
    info "Installed workflow: $workflow_name"
    ((copied++)) || true
  done

  info "Warp workflows installed: $copied  (destination: $WARP_WORKFLOWS_DIR)"
fi

# ── 3. MCP Servers ────────────────────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  warn "claude CLI not found, skipping MCP server installation."
else
  info "Installing MCP: XcodeBuildMCP..."
  claude mcp add XcodeBuildMCP -s user \
    -e XCODEBUILDMCP_SENTRY_DISABLED=true \
    -e XCODEBUILDMCP_DYNAMIC_TOOLS=true \
    -- npx -y xcodebuildmcp@latest mcp
  info "MCP installed: XcodeBuildMCP"

  info "Installing MCP: xcode (mcpbridge)..."
  claude mcp add --transport stdio xcode -s user -- xcrun mcpbridge
  info "MCP installed: xcode"
fi

echo ""
info "Setup complete."
