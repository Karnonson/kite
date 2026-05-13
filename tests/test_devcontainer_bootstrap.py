"""Tests for the dev container scaffold and bootstrap script."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "devcontainer-template"
BOOTSTRAP = REPO_ROOT / "scripts" / "install-devcontainer.sh"

TEMPLATE_FILES = ("Dockerfile", "devcontainer.json", "post-create.sh", "post-start.sh")


pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash required for dev container scaffold tests"
)


# --- Static checks ----------------------------------------------------------


def test_template_files_exist() -> None:
    for name in TEMPLATE_FILES:
        assert (TEMPLATE_DIR / name).is_file(), f"missing template file: {name}"
    assert (TEMPLATE_DIR / "README.md").is_file()


def test_bootstrap_script_exists() -> None:
    assert BOOTSTRAP.is_file()


def test_shell_scripts_pass_bash_syntax_check() -> None:
    for script in (
        BOOTSTRAP,
        TEMPLATE_DIR / "post-create.sh",
        TEMPLATE_DIR / "post-start.sh",
        REPO_ROOT / "tests" / "smoke" / "smoke-devcontainer.sh",
    ):
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{script}: {result.stderr}"


def test_devcontainer_json_parses_and_has_required_keys() -> None:
    import json5

    data = json5.loads((TEMPLATE_DIR / "devcontainer.json").read_text(encoding="utf-8"))

    assert data["build"]["dockerfile"] == "Dockerfile"
    assert data["build"]["context"] == "."
    assert data["containerUser"] == "codespace"
    assert data["updateRemoteUserUID"] is True
    assert data["otherPortsAttributes"]["onAutoForward"] == "ignore"
    assert data.get("features", {}) == {}
    assert data["postCreateCommand"] == "bash .devcontainer/post-create.sh"
    assert data["postStartCommand"] == "bash .devcontainer/post-start.sh"
    assert data["remoteEnv"]["KITE_DEV_ENV"] == "1"
    assert data["remoteEnv"]["KITE_DEFAULT_INTEGRATION"] == "copilot"
    # Until kite-cli is on PyPI, the default install source must be a git ref.
    assert data["remoteEnv"]["KITE_INSTALL_SPEC"].startswith("git+")
    assert data["remoteEnv"]["KITE_PNPM_VERSION"] == "10.10.0"
    assert "customizations" not in data


# --- Bootstrap script behavior ---------------------------------------------


def _run_bootstrap(args: list[str], env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KITE_TEMPLATE_BASE"] = f"file://{TEMPLATE_DIR}"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(BOOTSTRAP), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def test_bootstrap_scaffolds_into_empty_dir(tmp_path: Path) -> None:
    result = _run_bootstrap(["--dest", str(tmp_path)])
    assert result.returncode == 0, result.stderr
    assert "Dev Container-compatible IDE" in result.stdout
    assert "VS Code" not in result.stdout

    dc = tmp_path / ".devcontainer"
    assert dc.is_dir()
    for name in TEMPLATE_FILES:
        assert (dc / name).is_file(), f"missing scaffolded file: {name}"

    # Shell scripts must be executable after scaffold.
    for name in ("post-create.sh", "post-start.sh"):
        mode = (dc / name).stat().st_mode
        assert mode & stat.S_IXUSR, f"{name} not executable"


def test_bootstrap_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    (tmp_path / ".devcontainer").mkdir()

    result = _run_bootstrap(["--dest", str(tmp_path)])
    assert result.returncode != 0
    assert "already exists" in result.stderr


def test_bootstrap_force_overwrites(tmp_path: Path) -> None:
    dc = tmp_path / ".devcontainer"
    dc.mkdir()
    (dc / "stale.txt").write_text("old")

    result = _run_bootstrap(["--dest", str(tmp_path), "--force"])
    assert result.returncode == 0, result.stderr
    assert (dc / "devcontainer.json").is_file()
    assert not (dc / "stale.txt").exists()


def test_bootstrap_help_exits_zero() -> None:
    result = _run_bootstrap(["--help"])
    assert result.returncode == 0
    assert "install-devcontainer.sh" in result.stdout


def test_bootstrap_rejects_unknown_flag(tmp_path: Path) -> None:
    result = _run_bootstrap(["--dest", str(tmp_path), "--bogus"])
    assert result.returncode == 2
    assert "Unknown argument" in result.stderr


# --- Post-create script semantics ------------------------------------------


def test_post_create_skips_init_when_kite_dir_exists() -> None:
    """Static check: the script must guard `kite init` behind `[ ! -d .kite ]`."""
    text = (TEMPLATE_DIR / "post-create.sh").read_text(encoding="utf-8")
    assert 'if [[ -d ".kite" ]]; then' in text
    assert "skipping kite init" in text
    assert 'kite init \\' in text
    assert "--here" in text
    assert "--force" in text
