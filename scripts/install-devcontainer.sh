#!/usr/bin/env bash
# install-devcontainer.sh — scaffold a Kite dev container into a project.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
#   curl -fsSL .../install-devcontainer.sh | bash -s -- --force --ref main --dest ./my-project
#
# Flags:
#   --force         Replace an existing .devcontainer/ directory.
#   --ref REF       Git ref to fetch templates from (default: main).
#   --dest DIR      Destination workspace dir (default: current dir).
#   --help          Show this message.
#
# Env overrides (mostly for testing):
#   KITE_TEMPLATE_BASE  Base URL or file:// path for template files.
#                       Defaults to GitHub raw for the resolved --ref.
set -euo pipefail

REPO_SLUG="Karnonson/kite"
DEFAULT_REF="main"
TEMPLATE_FILES=(
  "Dockerfile"
  "devcontainer.json"
  "post-create.sh"
  "post-start.sh"
)

force=0
ref="$DEFAULT_REF"
dest="."

# Usage text is embedded so it works under `curl ... | bash` (where $0 is 'bash').
usage() {
  cat <<'USAGE'
install-devcontainer.sh — scaffold a Kite dev container into a project.

Usage:
  curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
  curl -fsSL .../install-devcontainer.sh | bash -s -- --force --ref main --dest ./my-project

Flags:
  --force         Replace an existing .devcontainer/ directory.
  --ref REF       Git ref to fetch templates from (default: main).
  --dest DIR      Destination workspace dir (default: current dir).
  --help          Show this message.

Env overrides (mostly for testing):
  KITE_TEMPLATE_BASE  Base URL or file:// path for template files.
                      Defaults to GitHub raw for the resolved --ref.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=1; shift ;;
    --ref) ref="${2:?--ref requires a value}"; shift 2 ;;
    --dest) dest="${2:?--dest requires a value}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

base_url="${KITE_TEMPLATE_BASE:-https://raw.githubusercontent.com/${REPO_SLUG}/${ref}/devcontainer-template}"
target_dir="${dest%/}/.devcontainer"

if [[ -e "$target_dir" && $force -ne 1 ]]; then
  echo "Error: $target_dir already exists. Re-run with --force to overwrite." >&2
  exit 1
fi

if [[ -e "$target_dir" && $force -eq 1 ]]; then
  rm -rf "$target_dir"
fi

mkdir -p "$target_dir"

fetch() {
  local rel="$1" out="$2"
  local src="${base_url}/${rel}"
  if [[ "$src" == file://* ]]; then
    cp "${src#file://}" "$out"
  else
    curl -fsSL "$src" -o "$out"
  fi
}

echo "Scaffolding Kite dev container into $target_dir (ref: $ref)"
for f in "${TEMPLATE_FILES[@]}"; do
  echo "  • $f"
  fetch "$f" "$target_dir/$f"
done

chmod +x "$target_dir/post-create.sh" "$target_dir/post-start.sh"

cat <<EOF

✅ Done.

Next steps:
  1. Open the project in your Dev Container-compatible IDE.
  2. Open or reopen the folder in its dev container using that IDE's container command.
  3. Wait for the build — Kite CLI will be installed automatically.

Customize KITE_VERSION / KITE_INSTALL_SPEC in .devcontainer/devcontainer.json
if you need to pin a specific Kite release or install source.
EOF
