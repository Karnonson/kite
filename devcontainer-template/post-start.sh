#!/usr/bin/env bash
# Kite Dev Container — post-start hook.
# Runs every time the container starts. Keep this fast.
set -euo pipefail

git config --global --add safe.directory "${CONTAINER_WORKSPACE_FOLDER:-$PWD}" 2>/dev/null || true

if command -v kite >/dev/null 2>&1; then
  printf '\033[0;36mkite %s ready\033[0m\n' "$(kite --version 2>/dev/null || echo '?')"
fi
