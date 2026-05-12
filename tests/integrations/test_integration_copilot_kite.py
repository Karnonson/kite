"""T504 — Kite persona/orchestrator install verification for Copilot.

Asserts that `kite init --integration copilot` ships all the new Kite
persona commands (discover, design, backend, frontend, qa) plus the
orchestrator (`start`) alongside the legacy SDLC commands (specify,
plan, tasks). This complements the broader inventory tests in
`test_integration_copilot.py` by focusing only on the Kite contract.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kite_cli import app


KITE_REQUIRED = [
    "analyze", "backend", "browser", "checklist", "clarify", "constitution",
    "design", "discover", "docs", "frontend", "plan", "qa", "research",
    "specify", "start", "tasks",
]


@pytest.fixture
def copilot_project(tmp_path):
    project = tmp_path / "kite-copilot"
    project.mkdir()
    old_cwd = os.getcwd()
    try:
        os.chdir(project)
        result = CliRunner().invoke(
            app,
            ["init", "--here", "--integration", "copilot",
             "--script", "sh", "--no-git", "--ignore-agent-tools"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)
    assert result.exit_code == 0, result.output
    return project


class TestCopilotKiteInstall:
    def test_all_kite_commands_present(self, copilot_project):
        agents_dir = copilot_project / ".github" / "agents"
        present = {p.name for p in agents_dir.glob("*.agent.md")}
        for stem in KITE_REQUIRED:
            assert f"kite.{stem}.agent.md" in present, (
                f"Missing kite.{stem}.agent.md in .github/agents/. Present: {sorted(present)}"
            )

    def test_companion_prompt_files(self, copilot_project):
        prompts_dir = copilot_project / ".github" / "prompts"
        for stem in KITE_REQUIRED:
            assert (prompts_dir / f"kite.{stem}.prompt.md").exists()

    def test_kite_config_yml_written_with_founder_default(self, copilot_project):
        cfg = (copilot_project / "kite.config.yml").read_text()
        assert "persona: founder" in cfg
