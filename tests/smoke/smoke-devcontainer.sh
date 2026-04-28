#!/usr/bin/env bash
# smoke-devcontainer.sh — end-to-end validation of the Kite dev container scaffold.
#
# What this verifies (without launching VS Code):
#   1. install-devcontainer.sh scaffolds .devcontainer/ from a local checkout.
#   2. devcontainer CLI builds the container from the scaffolded files.
#   3. post-create.sh installs kite-cli inside the container.
#   4. `kite init` ran on a fresh workspace and produced .kite/.
#   5. Re-running post-create.sh leaves the existing .kite/ untouched (idempotent).
#   6. docker-in-docker actually works inside the container.
#
# Requires on the host:
#   - docker (running)
#   - @devcontainers/cli  (npm i -g @devcontainers/cli)
#
# Usage:
#   tests/smoke/smoke-devcontainer.sh
#   KEEP=1 tests/smoke/smoke-devcontainer.sh   # don't tear down on success
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KEEP="${KEEP:-0}"

step()  { printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
ok()    { printf '\033[0;32m  ✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[0;31m  ✗ %s\033[0m\n' "$*"; exit 1; }

# --- Preflight ---------------------------------------------------------------
step "Preflight: required host tools"
command -v docker >/dev/null            || fail "docker not found on PATH"
docker info >/dev/null 2>&1             || fail "docker daemon not reachable"
command -v devcontainer >/dev/null      || fail "devcontainer CLI not found (npm i -g @devcontainers/cli)"
ok "docker $(docker --version | awk '{print $3}' | tr -d ,)"
ok "devcontainer $(devcontainer --version)"

# --- Workspace setup ---------------------------------------------------------
WORK="$(mktemp -d -t kite-smoke.XXXXXX)"
trap '[[ "$KEEP" = "1" ]] || { echo; echo "Cleaning up $WORK"; rm -rf "$WORK"; }' EXIT

step "Scaffolding into $WORK using local templates"
KITE_TEMPLATE_BASE="file://$REPO_ROOT/devcontainer-template" \
  bash "$REPO_ROOT/scripts/install-devcontainer.sh" --dest "$WORK"

[[ -f "$WORK/.devcontainer/devcontainer.json" ]] || fail "devcontainer.json missing"
[[ -x "$WORK/.devcontainer/post-create.sh" ]]    || fail "post-create.sh not executable"
ok "scaffold present and executable"

# --- Build container ---------------------------------------------------------
step "Building dev container (this can take several minutes the first run)"
devcontainer up --workspace-folder "$WORK" >/tmp/kite-smoke-up.log 2>&1 \
  || { tail -50 /tmp/kite-smoke-up.log; fail "devcontainer up failed (see /tmp/kite-smoke-up.log)"; }
ok "container up"

run() { devcontainer exec --workspace-folder "$WORK" -- bash -lc "$*"; }

# --- In-container assertions ------------------------------------------------
step "Verifying kite-cli inside the container"
run 'command -v kite >/dev/null && kite --version' >/dev/null \
  || fail "kite not on PATH inside the container"
ok "kite present"

step "Verifying .kite/ was created on first run"
# devcontainer exec lands in the workspace folder by default; check $PWD.
run 'test -d "$PWD/.kite"' \
  || fail ".kite/ was not created by post-create"
ok ".kite/ exists"

step "Verifying docker-in-docker"
run 'docker version --format "{{.Server.Version}}"' >/dev/null \
  || fail "docker-in-docker not functional"
ok "docker-in-docker functional"

# --- Idempotency check ------------------------------------------------------
step "Re-running post-create.sh (should NOT re-init Kite)"
out="$(run 'bash .devcontainer/post-create.sh 2>&1')"
echo "$out" | grep -q "skipping kite init" \
  || { echo "$out" | tail -20; fail "second run did not skip kite init"; }
ok "second run is idempotent"

# --- Done -------------------------------------------------------------------
step "Tearing down container"
docker ps --filter "label=devcontainer.local_folder=$WORK" -q \
  | xargs -r docker rm -f >/dev/null
ok "container removed"

printf '\n\033[1;32m✅ All smoke checks passed.\033[0m  workspace: %s\n' "$WORK"
[[ "$KEEP" = "1" ]] && printf '   (kept for inspection — set KEEP=0 to auto-clean next time)\n' || true
