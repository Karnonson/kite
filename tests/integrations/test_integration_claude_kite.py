"""T504 — Kite persona/orchestrator install verification for Claude (skills mode)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kite_cli import app


KITE_REQUIRED = [
    "discover", "design", "backend", "frontend", "qa",
    "start", "specify", "plan", "tasks",
]


@pytest.fixture
def claude_project(tmp_path):
    project = tmp_path / "kite-claude"
    project.mkdir()
    old_cwd = os.getcwd()
    try:
        os.chdir(project)
        result = CliRunner().invoke(
            app,
            ["init", "--here", "--integration", "claude",
             "--script", "sh", "--no-git", "--ignore-agent-tools"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)
    assert result.exit_code == 0, result.output
    return project


class TestClaudeKiteInstall:
    def test_all_kite_skills_present(self, claude_project):
        from kite_cli.integrations import get_integration
        i = get_integration("claude")
        skills_root = claude_project / i.registrar_config["dir"]
        present = {p.name for p in skills_root.iterdir() if p.is_dir()}
        for stem in KITE_REQUIRED:
            assert f"kite-{stem}" in present, (
                f"Missing kite-{stem}/ in {skills_root}. Present: {sorted(present)}"
            )
            assert (skills_root / f"kite-{stem}" / "SKILL.md").exists()

    def test_kite_config_yml_written(self, claude_project):
        cfg = (claude_project / "kite.config.yml").read_text()
        assert "persona: founder" in cfg
