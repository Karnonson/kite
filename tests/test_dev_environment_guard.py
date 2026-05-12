"""Tests for the host-environment guard utilities."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BASH_GUARD = REPO_ROOT / "scripts" / "bash" / "check-dev-environment.sh"
POWERSHELL_GUARD = REPO_ROOT / "scripts" / "powershell" / "check-dev-environment.ps1"


def _run_guard(command: str, workspace: Path, *, env: dict[str, str] | None = None, target_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    args = [
        "bash",
        str(BASH_GUARD),
        "--command",
        command,
        "--workspace",
        str(workspace),
        "--cwd",
        str(workspace),
    ]
    if target_path is not None:
        args.extend(["--target-path", str(target_path)])

    return subprocess.run(args, capture_output=True, text=True, env=process_env)


def test_guard_scripts_exist() -> None:
    assert BASH_GUARD.is_file()
    assert POWERSHELL_GUARD.is_file()


def test_bash_guard_allows_workspace_safe_command(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    result = _run_guard("rg contract frontend", workspace)

    assert result.returncode == 0, result.stderr
    assert "ALLOW" in result.stdout


def test_bash_guard_blocks_host_affecting_command_without_dev_env(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    result = _run_guard("npm install -g pnpm", workspace)

    assert result.returncode == 1
    assert "BLOCK" in result.stderr
    assert "npm install -g pnpm" in result.stderr


def test_bash_guard_allows_host_affecting_command_with_dev_env_marker(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    result = _run_guard("docker build .", workspace, env={"KITE_DEV_ENV": "1"})

    assert result.returncode == 0, result.stderr
    assert "ALLOW" in result.stdout


def test_bash_guard_blocks_target_path_outside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"

    result = _run_guard("cp notes.txt ../outside.txt", workspace, target_path=outside)

    assert result.returncode == 1
    assert "outside the approved workspace" in result.stderr


def test_powershell_guard_mentions_dev_env_marker() -> None:
    content = POWERSHELL_GUARD.read_text(encoding="utf-8")

    assert "KITE_DEV_ENV" in content
    assert "BLOCK:" in content
    assert "Test-PathOutsideWorkspace" in content
    assert "OrdinalIgnoreCase" in content


def test_powershell_guard_blocks_prefix_sibling_when_available(tmp_path: Path) -> None:
    pwsh = shutil.which("pwsh")
    if not pwsh:
        return

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sibling = tmp_path / "workspace-other"
    sibling.mkdir()
    target = sibling / "outside.txt"

    result = subprocess.run(
        [
            pwsh,
            "-NoProfile",
            "-File",
            str(POWERSHELL_GUARD),
            "-Command",
            "cp notes.txt ../workspace-other/outside.txt",
            "-Workspace",
            str(workspace),
            "-Cwd",
            str(workspace),
            "-TargetPath",
            str(target),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "outside the approved workspace" in result.stderr


def test_bash_guard_script_passes_syntax_check() -> None:
    result = subprocess.run(["bash", "-n", str(BASH_GUARD)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr