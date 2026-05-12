#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$script_dir/common.sh"

usage() {
    cat <<'EOF'
Usage: check-dev-environment.sh --command "<command>" [--workspace <path>] [--cwd <path>] [--target-path <path>]

Blocks host-affecting commands when they are not running in an approved Kite dev environment.
EOF
}

normalize_path() {
    local raw="$1"
    if [[ -z "$raw" ]]; then
        return 1
    fi

    if [[ -e "$raw" ]]; then
        if [[ -d "$raw" ]]; then
            (cd -- "$raw" 2>/dev/null && pwd -P)
        else
            local existing_parent existing_base
            existing_parent="$(dirname -- "$raw")"
            existing_base="$(basename -- "$raw")"
            existing_parent="$(cd -- "$existing_parent" 2>/dev/null && pwd -P)" || return 1
            printf '%s/%s\n' "$existing_parent" "$existing_base"
        fi
        return
    fi

    local parent base
    parent="$(dirname -- "$raw")"
    base="$(basename -- "$raw")"
    parent="$(cd -- "$parent" 2>/dev/null && pwd -P)" || return 1
    printf '%s/%s\n' "$parent" "$base"
}

emit_bell() {
    printf '\a' >&2
}

is_approved_dev_env() {
    [[ "${KITE_DEV_ENV:-}" == "1" ]]
}

has_container_evidence() {
    [[ -f "/.dockerenv" || -f "/run/.containerenv" ]]
}

command_is_dangerous() {
    local command_lc="$1"
    case "$command_lc" in
        *"npm install -g"*|*"npm i -g"*|*"pnpm add -g"*|*"yarn global add"*|*"bun add -g"*|\
        *"pip install "*|*"pip3 install "*|*"uv tool install "*|*"cargo install "*|\
        *"apt install "*|*"apt-get install "*|*"yum install "*|*"dnf install "*|*"brew install "*|\
        *"docker build"*|*"docker run"*|*"docker pull"*|*"systemctl "*|*"service "*)
            return 0
            ;;
    esac

    return 1
}

target_is_outside_workspace() {
    local target="$1"
    local workspace="$2"

    [[ -n "$target" ]] || return 1

    case "$target" in
        "$workspace"|"$workspace"/*)
            return 1
            ;;
        *)
            return 0
            ;;
    esac
}

command_text=""
current_dir="$PWD"
workspace_root=""
target_path=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --command)
            command_text="${2:-}"
            shift 2
            ;;
        --cwd)
            current_dir="${2:-}"
            shift 2
            ;;
        --workspace)
            workspace_root="${2:-}"
            shift 2
            ;;
        --target-path)
            target_path="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Unknown argument: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -z "$command_text" ]]; then
    printf 'Missing required --command argument\n' >&2
    usage >&2
    exit 2
fi

workspace_root="${workspace_root:-$(get_repo_root 2>/dev/null || pwd)}"
workspace_root="$(normalize_path "$workspace_root")"
current_dir="$(normalize_path "$current_dir")"

normalized_target=""
if [[ -n "$target_path" ]]; then
    normalized_target="$(normalize_path "$target_path")"
fi

command_lc="${command_text,,}"
dangerous_reason=""

if command_is_dangerous "$command_lc"; then
    dangerous_reason="host-affecting command pattern detected"
fi

if [[ -z "$dangerous_reason" ]] && target_is_outside_workspace "$normalized_target" "$workspace_root"; then
    dangerous_reason="target path is outside the approved workspace"
fi

if [[ -z "$dangerous_reason" ]]; then
    printf 'ALLOW: command is read-only or workspace-safe.\n'
    exit 0
fi

if is_approved_dev_env; then
    container_evidence="no"
    if has_container_evidence; then
        container_evidence="yes"
    fi
    printf 'ALLOW: approved dev environment detected (KITE_DEV_ENV=1, container=%s).\n' "$container_evidence"
    exit 0
fi

emit_bell
printf 'BLOCK: %s.\n' "$dangerous_reason" >&2
printf 'Command: %s\n' "$command_text" >&2
printf 'Workspace: %s\n' "$workspace_root" >&2
printf 'Current directory: %s\n' "$current_dir" >&2
printf 'KITE_DEV_ENV=%s\n' "${KITE_DEV_ENV:-unset}" >&2
printf 'Next step: run inside an approved dev environment or export KITE_DEV_ENV=1 in an approved sandbox before retrying.\n' >&2
exit 1