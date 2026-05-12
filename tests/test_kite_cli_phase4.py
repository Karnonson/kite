"""Tests for the Phase 4 founder-friendly CLI commands: kite doctor, kite resume, --persona."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from kite_cli import app


runner = CliRunner()


def _make_kite_project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    (proj / ".kite").mkdir(parents=True)
    return proj


class TestDoctor:
    def test_errors_outside_kite_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code != 0
        assert "not a Kite project" in result.stdout.lower() or "not a kite project" in result.stdout.lower()

    def test_reports_missing_artifacts(self, tmp_path, monkeypatch):
        proj = _make_kite_project(tmp_path)
        monkeypatch.chdir(proj)
        result = runner.invoke(app, ["doctor"])
        # No specs at all → blocker
        assert result.exit_code != 0
        assert "specify" in result.stdout.lower()
        assert "discover" in result.stdout.lower()

    def test_passes_on_complete_project(self, tmp_path, monkeypatch):
        proj = _make_kite_project(tmp_path)
        (proj / "kite.config.yml").write_text("persona: founder\n")
        spec = proj / "specs" / "001-demo"
        spec.mkdir(parents=True)
        (spec / "discovery.md").write_text("# Discovery\n")
        (spec / "spec.md").write_text("# Spec\n")
        (spec / "design.md").write_text("# Design\n")
        (spec / "plan.md").write_text("# Plan\n")
        (spec / "tasks.md").write_text("# Tasks\n\n- [x] Ship the first loop\n")
        monkeypatch.chdir(proj)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0, result.stdout
        assert "all good" in result.stdout.lower()

    def test_flags_open_tasks_as_next_step(self, tmp_path, monkeypatch):
        proj = _make_kite_project(tmp_path)
        (proj / "kite.config.yml").write_text("persona: founder\n")
        spec = proj / "specs" / "001-demo"
        spec.mkdir(parents=True)
        for f in ("spec.md", "design.md", "plan.md", "tasks.md", "discovery.md"):
            (spec / f).write_text(f"# {f}\n")
        (spec / "tasks.md").write_text("# Tasks\n\n- [ ] Build the feature\n")
        monkeypatch.chdir(proj)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "analyze" in result.stdout.lower()
        assert "backend" in result.stdout.lower()


class TestResume:
    def test_errors_outside_kite_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["resume"])
        assert result.exit_code != 0
        assert "not a kite project" in result.stdout.lower()

    def test_reports_no_runs_to_resume(self, tmp_path, monkeypatch):
        proj = _make_kite_project(tmp_path)
        monkeypatch.chdir(proj)
        result = runner.invoke(app, ["resume"])
        assert result.exit_code == 0
        assert "no paused" in result.stdout.lower()
