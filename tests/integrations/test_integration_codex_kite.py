"""T504 — Kite persona/orchestrator install verification for Codex (skills mode)."""

from __future__ import annotations

import os

import pytest
from typer.testing import CliRunner

from kite_cli import app


KITE_REQUIRED = [
    "discover", "design", "backend", "frontend", "qa",
    "start", "specify", "plan", "tasks",
]


@pytest.fixture
def codex_project(tmp_path):
    project = tmp_path / "kite-codex"
    project.mkdir()
    old_cwd = os.getcwd()
    try:
        os.chdir(project)
        result = CliRunner().invoke(
            app,
            ["init", "--here", "--integration", "codex",
             "--script", "sh", "--no-git", "--ignore-agent-tools"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)
    assert result.exit_code == 0, result.output
    return project


class TestCodexKiteInstall:
    def test_all_kite_skills_present(self, codex_project):
        from kite_cli.integrations import get_integration
        i = get_integration("codex")
        skills_root = codex_project / i.registrar_config["dir"]
        present = {p.name for p in skills_root.iterdir() if p.is_dir()}
        for stem in KITE_REQUIRED:
            assert f"kite-{stem}" in present, (
                f"Missing kite-{stem}/ in {skills_root}. Present: {sorted(present)}"
            )
            assert (skills_root / f"kite-{stem}" / "SKILL.md").exists()

    def test_kite_config_yml_written(self, codex_project):
        cfg = (codex_project / "kite.config.yml").read_text()
        assert "persona: founder" in cfg
