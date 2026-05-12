#!/usr/bin/env bash
# Kite Dev Container — post-create hook.
# Runs once after the container is built. Idempotent across rebuilds.
set -euo pipefail

KITE_VERSION="${KITE_VERSION:-}"
KITE_INSTALL_SPEC="${KITE_INSTALL_SPEC:-kite-cli}"
KITE_DEFAULT_INTEGRATION="${KITE_DEFAULT_INTEGRATION:-copilot}"
KITE_PNPM_VERSION="${KITE_PNPM_VERSION:-10.10.0}"

log() { printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
ok()  { printf '\033[0;32m  ✓ %s\033[0m\n' "$*"; }

# --- Ensure pipx is available ------------------------------------------------
log "Ensuring pipx is on PATH"
if ! command -v pipx >/dev/null 2>&1; then
  python3 -m pip install --user --quiet pipx
  python3 -m pipx ensurepath >/dev/null
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "pipx ready ($(pipx --version 2>/dev/null || echo 'unknown'))"

# --- Install Kite CLI --------------------------------------------------------
if [[ -n "$KITE_VERSION" ]]; then
  log "Installing kite-cli==$KITE_VERSION"
  pipx install --force "${KITE_INSTALL_SPEC}==${KITE_VERSION}"
else
  log "Installing Kite CLI from configured source: $KITE_INSTALL_SPEC"
  pipx install --force "$KITE_INSTALL_SPEC"
fi
ok "kite $(kite --version 2>/dev/null || echo 'installed')"
ok "KITE_DEV_ENV=${KITE_DEV_ENV:-unset}"

# --- Optional: pnpm for TypeScript projects ----------------------------------
if command -v npm >/dev/null 2>&1; then
  log "Installing pnpm $KITE_PNPM_VERSION globally"
  npm install -g "pnpm@${KITE_PNPM_VERSION}" >/dev/null 2>&1 || true
  ok "pnpm $(pnpm --version 2>/dev/null || echo 'unavailable')"
fi

# --- First-run init (only when no .kite/ present) ----------------------------
WORKSPACE_DIR="${CONTAINER_WORKSPACE_FOLDER:-$PWD}"
cd "$WORKSPACE_DIR"

if [[ -d ".kite" ]]; then
  log "Existing .kite/ detected — skipping kite init"
else
  log "Bootstrapping Kite workspace (integration: $KITE_DEFAULT_INTEGRATION)"
  kite init \
    --here \
    --force \
    --integration "$KITE_DEFAULT_INTEGRATION" \
    --ignore-agent-tools
  ok "Kite workspace initialized"
fi

printf '\n\033[1;32m✅ Kite dev container ready.\033[0m\n'
