"""Tests for --integration flag on kite init (CLI-level)."""

import json
import os
import shutil
import subprocess
import sys

import pytest
import yaml

from tests.conftest import strip_ansi


def _normalize_cli_output(output: str) -> str:
    output = strip_ansi(output)
    output = " ".join(output.split())
    return output.strip()


class TestInitIntegrationFlag:
    def test_integration_and_ai_mutually_exclusive(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        result = runner.invoke(app, [
            "init", str(tmp_path / "test-project"), "--ai", "claude", "--integration", "copilot",
        ])
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output

    def test_unknown_integration_rejected(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        result = runner.invoke(app, [
            "init", str(tmp_path / "test-project"), "--integration", "nonexistent",
        ])
        assert result.exit_code != 0
        assert "Unknown integration" in result.output

    def test_integration_copilot_creates_files(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        project = tmp_path / "int-test"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, [
                "init", "--here", "--integration", "copilot", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)
        assert result.exit_code == 0, f"init failed: {result.output}"
        assert (project / ".github" / "agents" / "kite.plan.agent.md").exists()
        assert (project / ".github" / "prompts" / "kite.plan.prompt.md").exists()
        assert (project / ".kite" / "scripts" / "bash" / "common.sh").exists()

        data = json.loads((project / ".kite" / "integration.json").read_text(encoding="utf-8"))
        assert data["integration"] == "copilot"

        opts = json.loads((project / ".kite" / "init-options.json").read_text(encoding="utf-8"))
        assert opts["integration"] == "copilot"
        assert opts["context_file"] == ".github/copilot-instructions.md"
        assert opts["profile"] == "standard"

        assert (project / ".kite" / "integrations" / "copilot.manifest.json").exists()

        # Context section should be upserted into the copilot instructions file
        ctx_file = project / ".github" / "copilot-instructions.md"
        assert ctx_file.exists()
        ctx_content = ctx_file.read_text(encoding="utf-8")
        assert "<!-- KITE START -->" in ctx_content
        assert "<!-- KITE END -->" in ctx_content

        shared_manifest = project / ".kite" / "integrations" / "kite.manifest.json"
        assert shared_manifest.exists()

    def test_integration_copilot_profile_minimal(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        project = tmp_path / "int-profile-minimal"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, [
                "init", "--here", "--integration", "copilot",
                "--profile", "minimal", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"
        assert (project / ".github" / "agents" / "kite.start.agent.md").exists()
        assert not (project / ".github" / "agents" / "kite.research.agent.md").exists()
        assert not (project / ".github" / "agents" / "kite.analyze.agent.md").exists()
        assert not (project / ".github" / "skills" / "kite-mastra" / "SKILL.md").exists()

        opts = json.loads((project / ".kite" / "init-options.json").read_text(encoding="utf-8"))
        assert opts["profile"] == "minimal"

    def test_integration_copilot_profile_standard_keeps_core_plus_research(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        project = tmp_path / "int-profile-standard"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, [
                "init", "--here", "--integration", "copilot",
                "--profile", "standard", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"
        assert (project / ".github" / "agents" / "kite.research.agent.md").exists()
        assert not (project / ".github" / "agents" / "kite.analyze.agent.md").exists()
        assert not (project / ".github" / "agents" / "kite.implement.agent.md").exists()

    def test_integration_copilot_profile_full(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        project = tmp_path / "int-profile-full"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, [
                "init", "--here", "--integration", "copilot",
                "--profile", "full", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"
        assert (project / ".github" / "agents" / "kite.implement.agent.md").exists()
        assert (project / ".github" / "agents" / "kite.analyze.agent.md").exists()
        assert (project / ".github" / "skills" / "kite-mastra" / "SKILL.md").exists()

        opts = json.loads((project / ".kite" / "init-options.json").read_text(encoding="utf-8"))
        assert opts["profile"] == "full"

    def test_integration_copilot_profile_rejects_unknown(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        runner = CliRunner()
        project = tmp_path / "int-profile-invalid"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, [
                "init", "--here", "--integration", "copilot",
                "--profile", "tiny", "--script", "sh", "--no-git",
            ])
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 1
        assert "Unknown install profile 'tiny'" in strip_ansi(result.output)

    def test_init_writes_project_context_for_brownfield_project(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "brownfield"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps(
                {
                    "scripts": {
                        "lint": "eslint .",
                        "test": "vitest run",
                        "build": "vite build",
                    },
                    "dependencies": {"react": "18.2.0", "vite": "5.0.0"},
                    "devDependencies": {"vitest": "1.0.0"},
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                [
                    "init",
                    "--here",
                    "--force",
                    "--integration",
                    "copilot",
                    "--script",
                    "sh",
                    "--no-git",
                ],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        context_path = project / ".kite" / "project-context.json"
        assert context_path.exists()
        context = json.loads(context_path.read_text(encoding="utf-8"))
        assert context["brownfield"] is True
        assert context["summary"]["package_manager"] == "npm"
        assert "react" in context["summary"]["frameworks"]
        command_ids = {command["id"] for command in context["validation_commands"]}
        assert {"package-lint", "package-test", "package-build"} <= command_ids

    def test_project_check_runs_commands_from_context(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "check-pass"
        (project / ".kite").mkdir(parents=True)
        (project / ".kite" / "project-context.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "validation_commands": [
                        {
                            "id": "unit",
                            "label": "Unit tests",
                            "command": [sys.executable, "-c", "print('ok')"],
                            "source": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["check", "--run-validation", "--no-refresh-context"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        normalized_output = _normalize_cli_output(result.output)
        assert "Project validation passed" in normalized_output
        assert "Unit tests" in normalized_output

    def test_project_check_fails_when_context_command_fails(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "check-fail"
        (project / ".kite").mkdir(parents=True)
        (project / ".kite" / "project-context.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "validation_commands": [
                        {
                            "id": "unit",
                            "label": "Unit tests",
                            "command": [
                                sys.executable,
                                "-c",
                                "import sys; print('boom'); sys.exit(7)",
                            ],
                            "source": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["check", "--run-validation", "--no-refresh-context"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 1
        normalized_output = _normalize_cli_output(result.output)
        assert "1 validation command(s) failed" in normalized_output
        assert "boom" in normalized_output

    def test_project_check_rejects_string_validation_commands(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "check-string"
        (project / ".kite").mkdir(parents=True)
        (project / ".kite" / "project-context.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "validation_commands": [
                        {
                            "id": "shell",
                            "label": "Shell command",
                            "command": "echo unsafe",
                            "source": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["check", "--run-validation", "--no-refresh-context"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 1
        normalized_output = _normalize_cli_output(result.output)
        assert "array of strings" in normalized_output

    def test_project_check_reports_missing_validation_executable(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "check-missing-exec"
        (project / ".kite").mkdir(parents=True)
        (project / ".kite" / "project-context.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "validation_commands": [
                        {
                            "id": "missing",
                            "label": "Missing executable",
                            "command": ["definitely-not-a-kite-test-command"],
                            "source": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["check", "--run-validation", "--no-refresh-context"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 1
        normalized_output = _normalize_cli_output(result.output)
        assert "Could not run validation command" in normalized_output

    def test_project_check_refresh_preserves_existing_commands(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "check-refresh-merge"
        (project / ".kite").mkdir(parents=True)
        (project / "package.json").write_text(
            json.dumps({"scripts": {"test": "node should-not-replace.js"}}),
            encoding="utf-8",
        )
        context_path = project / ".kite" / "project-context.json"
        context_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "brownfield": False,
                    "custom_note": "keep me",
                    "validation_commands": [
                        {
                            "id": "custom",
                            "label": "Custom validation",
                            "command": [sys.executable, "-c", "print('custom ok')"],
                            "source": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["check", "--run-validation"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        refreshed = json.loads(context_path.read_text(encoding="utf-8"))
        assert refreshed["custom_note"] == "keep me"
        assert refreshed["brownfield"] is False
        assert [command["id"] for command in refreshed["validation_commands"]] == ["custom"]
        assert refreshed["summary"]["package_manager"] == "npm"

    def test_project_context_uses_package_manager_field(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "context-package-manager"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps(
                {
                    "packageManager": "pnpm@9.12.0",
                    "scripts": {"test": "vitest run"},
                }
            ),
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                [
                    "init",
                    "--here",
                    "--force",
                    "--integration",
                    "copilot",
                    "--script",
                    "sh",
                    "--no-git",
                ],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        context = json.loads((project / ".kite" / "project-context.json").read_text())
        assert context["summary"]["package_manager"] == "pnpm"
        assert context["validation_commands"][0]["command"] == ["pnpm", "run", "test"]

    def test_init_with_git_uses_main_branch(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        if shutil.which("git") is None:
            pytest.skip("git required")

        runner = CliRunner()
        project = tmp_path / "git-main"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                [
                    "init",
                    "--here",
                    "--integration",
                    "generic",
                    "--ai-commands-dir",
                    ".myagent/commands",
                    "--script",
                    "sh",
                    "--ignore-agent-tools",
                ],
                catch_exceptions=False,
                env={
                    "GIT_AUTHOR_NAME": "Kite Test",
                    "GIT_AUTHOR_EMAIL": "kite@example.com",
                    "GIT_COMMITTER_NAME": "Kite Test",
                    "GIT_COMMITTER_EMAIL": "kite@example.com",
                },
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch == "main"

    def test_ai_copilot_auto_promotes(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app
        project = tmp_path / "promote-test"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "copilot", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)
        assert result.exit_code == 0
        assert (project / ".github" / "agents" / "kite.plan.agent.md").exists()

    def test_ai_emits_deprecation_warning_with_integration_replacement(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "warn-ai"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "copilot", "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        normalized_output = _normalize_cli_output(result.output)
        assert result.exit_code == 0, result.output
        assert "Deprecation Warning" in normalized_output
        assert "--ai" in normalized_output
        assert "deprecated" in normalized_output
        assert "no longer be available" in normalized_output
        assert "0.10.0" in normalized_output
        assert "--integration copilot" in normalized_output
        assert normalized_output.index("Deprecation Warning") < normalized_output.index("Next Steps")
        assert (project / ".github" / "agents" / "kite.plan.agent.md").exists()

    def test_ai_generic_warning_suggests_integration_options_equivalent(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "warn-generic"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "generic", "--ai-commands-dir", ".myagent/commands",
                "--script", "sh", "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        normalized_output = _normalize_cli_output(result.output)
        assert result.exit_code == 0, result.output
        assert "Deprecation Warning" in normalized_output
        assert "--integration generic" in normalized_output
        assert "--integration-options" in normalized_output
        assert ".myagent/commands" in normalized_output
        assert normalized_output.index("Deprecation Warning") < normalized_output.index("Next Steps")
        assert (project / ".myagent" / "commands" / "kite.plan.md").exists()

    def test_ai_claude_here_preserves_preexisting_commands(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "claude-here-existing"
        project.mkdir()
        commands_dir = project / ".claude" / "skills"
        commands_dir.mkdir(parents=True)
        skill_dir = commands_dir / "kite-specify"
        skill_dir.mkdir(parents=True)
        command_file = skill_dir / "SKILL.md"
        command_file.write_text("# preexisting command\n", encoding="utf-8")

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--force", "--ai", "claude", "--ai-skills", "--script", "sh", "--no-git", "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        assert command_file.exists()
        # init replaces skills (not additive); verify the file has valid skill content
        assert command_file.exists()
        assert "kite-specify" in command_file.read_text(encoding="utf-8")
        assert (project / ".claude" / "skills" / "kite-plan" / "SKILL.md").exists()

    def test_shared_infra_skips_existing_files_without_force(self, tmp_path):
        """Pre-existing shared files are not overwritten without --force."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "skip-test"
        project.mkdir()
        (project / ".kite").mkdir()

        # Pre-create a shared script with custom content
        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        custom_content = "# user-modified common.sh\n"
        (scripts_dir / "common.sh").write_text(custom_content, encoding="utf-8")

        # Pre-create a shared template with custom content
        templates_dir = project / ".kite" / "templates"
        templates_dir.mkdir(parents=True)
        custom_template = "# user-modified spec-template\n"
        (templates_dir / "spec-template.md").write_text(custom_template, encoding="utf-8")

        _install_shared_infra(project, "sh", force=False)

        # User's files should be preserved (not overwritten)
        assert (scripts_dir / "common.sh").read_text(encoding="utf-8") == custom_content
        assert (templates_dir / "spec-template.md").read_text(encoding="utf-8") == custom_template

        # Other shared files should still be installed
        assert (scripts_dir / "setup-plan.sh").exists()
        assert (templates_dir / "plan-template.md").exists()

    def test_shared_infra_overwrites_existing_files_with_force(self, tmp_path):
        """Pre-existing shared files ARE overwritten when force=True."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "force-test"
        project.mkdir()
        (project / ".kite").mkdir()

        # Pre-create a shared script with custom content
        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        custom_content = "# user-modified common.sh\n"
        (scripts_dir / "common.sh").write_text(custom_content, encoding="utf-8")

        # Pre-create a shared template with custom content
        templates_dir = project / ".kite" / "templates"
        templates_dir.mkdir(parents=True)
        custom_template = "# user-modified spec-template\n"
        (templates_dir / "spec-template.md").write_text(custom_template, encoding="utf-8")

        _install_shared_infra(project, "sh", force=True)

        # Files should be overwritten with bundled versions
        assert (scripts_dir / "common.sh").read_text(encoding="utf-8") != custom_content
        assert (templates_dir / "spec-template.md").read_text(encoding="utf-8") != custom_template

        # Other shared files should also be installed
        assert (scripts_dir / "setup-plan.sh").exists()
        assert (templates_dir / "plan-template.md").exists()

    def test_shared_infra_skip_warning_displayed(self, tmp_path, capsys):
        """Console warning is displayed when files are skipped."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "warn-test"
        project.mkdir()
        (project / ".kite").mkdir()

        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "common.sh").write_text("# custom\n", encoding="utf-8")

        _install_shared_infra(project, "sh", force=False)

        captured = capsys.readouterr()
        assert "already exist and were not updated" in captured.out
        assert "kite init --here --force" in captured.out
        # Rich may wrap long lines; normalize whitespace for the second command
        normalized = " ".join(captured.out.split())
        assert "kite integration upgrade --force" in normalized

    def test_shared_infra_no_warning_when_forced(self, tmp_path, capsys):
        """No skip warning when force=True (all files overwritten)."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "no-warn-test"
        project.mkdir()
        (project / ".kite").mkdir()

        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "common.sh").write_text("# custom\n", encoding="utf-8")

        _install_shared_infra(project, "sh", force=True)

        captured = capsys.readouterr()
        assert "already exist and were not updated" not in captured.out

    def test_init_here_force_overwrites_shared_infra(self, tmp_path):
        """E2E: kite init --here --force overwrites shared infra files."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "e2e-force"
        project.mkdir()

        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        custom_content = "# user-modified common.sh\n"
        (scripts_dir / "common.sh").write_text(custom_content, encoding="utf-8")

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--force",
                "--integration", "copilot",
                "--script", "sh",
                "--no-git",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        # --force should overwrite the custom file
        assert (scripts_dir / "common.sh").read_text(encoding="utf-8") != custom_content

    def test_init_here_without_force_preserves_shared_infra(self, tmp_path):
        """E2E: kite init --here (no --force) preserves existing shared infra files."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "e2e-no-force"
        project.mkdir()

        scripts_dir = project / ".kite" / "scripts" / "bash"
        scripts_dir.mkdir(parents=True)
        custom_content = "# user-modified common.sh\n"
        (scripts_dir / "common.sh").write_text(custom_content, encoding="utf-8")

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here",
                "--integration", "copilot",
                "--script", "sh",
                "--no-git",
            ], input="y\n", catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        # Without --force, custom file should be preserved
        assert (scripts_dir / "common.sh").read_text(encoding="utf-8") == custom_content
        # Warning about skipped files should appear
        assert "not updated" in result.output


class TestForceExistingDirectory:
    """Tests for --force merging into an existing named directory."""

    def test_force_merges_into_existing_dir(self, tmp_path):
        """kite init <dir> --force succeeds when the directory already exists."""
        from typer.testing import CliRunner
        from kite_cli import app

        target = tmp_path / "existing-proj"
        target.mkdir()
        # Place a pre-existing file to verify it survives the merge
        marker = target / "user-file.txt"
        marker.write_text("keep me", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(app, [
            "init", str(target), "--integration", "copilot", "--force",
            "--no-git", "--script", "sh",
        ], catch_exceptions=False)

        assert result.exit_code == 0, f"init --force failed: {result.output}"

        # Pre-existing file should survive
        assert marker.read_text(encoding="utf-8") == "keep me"

        # Kite files should be installed
        assert (target / ".kite" / "init-options.json").exists()
        assert (target / ".kite" / "templates" / "spec-template.md").exists()

    def test_without_force_errors_on_existing_dir(self, tmp_path):
        """kite init <dir> without --force errors when directory exists."""
        from typer.testing import CliRunner
        from kite_cli import app

        target = tmp_path / "existing-proj"
        target.mkdir()

        runner = CliRunner()
        result = runner.invoke(app, [
            "init", str(target), "--integration", "copilot",
            "--no-git", "--script", "sh",
        ], catch_exceptions=False)

        assert result.exit_code == 1
        assert "already exists" in _normalize_cli_output(result.output)


class TestGitExtensionAutoInstall:
    """Tests for auto-installation of the git extension during kite init."""

    def test_git_extension_auto_installed(self, tmp_path):
        """Without --no-git, the git extension is installed during init."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "git-auto"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "claude", "--script", "sh",
                "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        # Check that the tracker didn't report a git error
        assert "install failed" not in result.output, f"git extension install failed: {result.output}"

        # Git extension files should be installed
        ext_dir = project / ".kite" / "extensions" / "git"
        assert ext_dir.exists(), "git extension directory not installed"
        assert (ext_dir / "extension.yml").exists()
        assert (ext_dir / "scripts" / "bash" / "create-new-feature.sh").exists()
        assert (ext_dir / "scripts" / "bash" / "initialize-repo.sh").exists()

        # Hooks should be registered
        extensions_yml = project / ".kite" / "extensions.yml"
        assert extensions_yml.exists(), "extensions.yml not created"
        hooks_data = yaml.safe_load(extensions_yml.read_text(encoding="utf-8"))
        assert "hooks" in hooks_data
        assert "before_specify" in hooks_data["hooks"]
        assert "before_constitution" in hooks_data["hooks"]

        gitignore = project / ".gitignore"
        assert gitignore.exists(), ".gitignore not created"
        gitignore_text = gitignore.read_text(encoding="utf-8")
        assert ".kite/extensions/*/local-config.yml" in gitignore_text

    def test_no_git_skips_extension(self, tmp_path):
        """With --no-git, the git extension is NOT installed."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "no-git"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "claude", "--script", "sh",
                "--no-git", "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        # Git extension should NOT be installed
        ext_dir = project / ".kite" / "extensions" / "git"
        assert not ext_dir.exists(), "git extension should not be installed with --no-git"

    def test_no_git_emits_deprecation_warning(self, tmp_path):
        """Using --no-git emits a visible deprecation warning."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "no-git-warn"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "claude", "--script", "sh",
                "--no-git", "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        normalized_output = _normalize_cli_output(result.output)
        assert result.exit_code == 0, result.output
        assert "--no-git" in normalized_output
        assert "deprecated" in normalized_output
        assert "0.10.0" in normalized_output
        assert "kite extension" in normalized_output
        assert "will be removed" in normalized_output
        assert "git extension will no longer be enabled by default" in normalized_output

    def test_git_extension_commands_registered(self, tmp_path):
        """Git extension commands are registered with the agent during init."""
        from typer.testing import CliRunner
        from kite_cli import app

        project = tmp_path / "git-cmds"
        project.mkdir()
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            runner = CliRunner()
            result = runner.invoke(app, [
                "init", "--here", "--ai", "claude", "--script", "sh",
                "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        # Git extension commands should be registered with the agent
        claude_skills = project / ".claude" / "skills"
        assert claude_skills.exists(), "Claude skills directory was not created"
        git_skills = [f for f in claude_skills.iterdir() if f.name.startswith("kite-git-")]
        assert len(git_skills) > 0, "no git extension commands registered"


class TestSharedInfraCommandRefs:
    """Verify _install_shared_infra resolves __KITE_COMMAND_*__ in page templates."""

    def test_dot_separator_in_page_templates(self, tmp_path):
        """Markdown agents get /kite.<name> in page templates."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "dot-test"
        project.mkdir()
        (project / ".kite").mkdir()

        _install_shared_infra(project, "sh", invoke_separator=".")

        plan = project / ".kite" / "templates" / "plan-template.md"
        assert plan.exists()
        content = plan.read_text(encoding="utf-8")
        assert "__KITE_COMMAND_" not in content, "unresolved placeholder in plan-template.md"
        assert "/kite.plan" in content

        checklist = project / ".kite" / "templates" / "checklist-template.md"
        content = checklist.read_text(encoding="utf-8")
        assert "__KITE_COMMAND_" not in content
        assert "/kite.checklist" in content

    def test_hyphen_separator_in_page_templates(self, tmp_path):
        """Skills agents get /kite-<name> in page templates."""
        from kite_cli import _install_shared_infra

        project = tmp_path / "hyphen-test"
        project.mkdir()
        (project / ".kite").mkdir()

        _install_shared_infra(project, "sh", invoke_separator="-")

        plan = project / ".kite" / "templates" / "plan-template.md"
        assert plan.exists()
        content = plan.read_text(encoding="utf-8")
        assert "__KITE_COMMAND_" not in content, "unresolved placeholder in plan-template.md"
        assert "/kite-plan" in content
        assert "/kite.plan" not in content, "dot-notation leaked into skills page template"

        tasks = project / ".kite" / "templates" / "tasks-template.md"
        content = tasks.read_text(encoding="utf-8")
        assert "__KITE_COMMAND_" not in content
        assert "/kite-tasks" in content
        assert "### Backend Slice for User Story 1" in content
        assert "### Frontend Verification for User Story 1" in content
        assert "Verify the story 1 backend slice in the terminal" in content

    def test_full_init_claude_resolves_page_templates(self, tmp_path):
        """Full CLI init with Claude (skills agent) produces hyphen refs in page templates."""
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "init-claude"
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, [
                "init", str(project),
                "--integration", "claude",
                "--script", "sh",
                "--no-git",
                "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        plan = project / ".kite" / "templates" / "plan-template.md"
        content = plan.read_text(encoding="utf-8")
        assert "/kite-plan" in content, "Claude (skills) should use /kite-plan"
        assert "__KITE_COMMAND_" not in content

    def test_full_init_copilot_resolves_page_templates(self, tmp_path):
        """Full CLI init with Copilot (markdown agent) produces dot refs in page templates."""
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "init-copilot"
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, [
                "init", str(project),
                "--integration", "copilot",
                "--script", "sh",
                "--no-git",
                "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        plan = project / ".kite" / "templates" / "plan-template.md"
        content = plan.read_text(encoding="utf-8")
        assert "/kite.plan" in content, "Copilot (markdown) should use /kite.plan"
        assert "__KITE_COMMAND_" not in content

    def test_full_init_copilot_skills_resolves_page_templates(self, tmp_path):
        """Full CLI init with Copilot --skills produces hyphen refs in page templates."""
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "init-copilot-skills"
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, [
                "init", str(project),
                "--integration", "copilot",
                "--integration-options", "--skills",
                "--script", "sh",
                "--no-git",
                "--ignore-agent-tools",
            ], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, f"init failed: {result.output}"

        plan = project / ".kite" / "templates" / "plan-template.md"
        content = plan.read_text(encoding="utf-8")
        assert "/kite-plan" in content, "Copilot --skills should use /kite-plan"
        assert "/kite.plan" not in content, "dot-notation leaked into Copilot skills page template"
        assert "__KITE_COMMAND_" not in content


class TestProfileCommands:
    """Tests for `kite profile show` and `kite profile set`."""

    def _init_project(self, runner, project: "Path", profile: str = "standard") -> None:
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                __import__("kite_cli").app,
                ["init", "--here", "--integration", "copilot", "--profile", profile,
                 "--script", "sh", "--no-git"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)
        assert result.exit_code == 0, f"init failed: {result.output}"

    def test_profile_show_displays_current_profile(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "show-test"
        project.mkdir()
        self._init_project(runner, project, profile="minimal")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, ["profile", "show"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        output = strip_ansi(result.output)
        assert "minimal" in output
        assert "Profile" in output

    def test_profile_show_via_subcommand_default(self, tmp_path):
        """Running `kite profile` with no subcommand should show the profile."""
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "show-default"
        project.mkdir()
        self._init_project(runner, project, profile="full")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, ["profile"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        output = strip_ansi(result.output)
        assert "full" in output

    def test_profile_show_outside_kite_project_exits_nonzero(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["profile", "show"])
        finally:
            os.chdir(old_cwd)

        assert result.exit_code != 0
        assert "Not a Kite project" in strip_ansi(result.output)

    def test_profile_set_changes_profile(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "set-test"
        project.mkdir()
        self._init_project(runner, project, profile="standard")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, ["profile", "set", "full"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        opts = json.loads((project / ".kite" / "init-options.json").read_text())
        assert opts["profile"] == "full"
        output = strip_ansi(result.output)
        assert "full" in output

    def test_integration_upgrade_uses_saved_profile(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "upgrade-saved-profile"
        project.mkdir()
        self._init_project(runner, project, profile="standard")

        assert not (project / ".github" / "agents" / "kite.implement.agent.md").exists()

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            set_result = runner.invoke(
                app,
                ["profile", "set", "full"],
                catch_exceptions=False,
            )
            upgrade_result = runner.invoke(
                app,
                ["integration", "upgrade", "--force"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert set_result.exit_code == 0, set_result.output
        assert upgrade_result.exit_code == 0, upgrade_result.output
        assert (project / ".github" / "agents" / "kite.implement.agent.md").exists()
        opts = json.loads((project / ".kite" / "init-options.json").read_text())
        assert opts["profile"] == "full"

    def test_profile_set_upgrade_applies_profile(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "set-upgrade"
        project.mkdir()
        self._init_project(runner, project, profile="standard")

        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(
                app,
                ["profile", "set", "full", "--upgrade"],
                catch_exceptions=False,
            )
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        assert (project / ".github" / "agents" / "kite.implement.agent.md").exists()
        output = strip_ansi(result.output)
        assert "Profile updated" in output
        assert "upgraded successfully" in output

    def test_profile_set_rejects_unknown_profile(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "set-bad"
        project.mkdir()
        self._init_project(runner, project, profile="standard")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, ["profile", "set", "ultramax"])
        finally:
            os.chdir(old_cwd)

        assert result.exit_code != 0
        assert "Unknown install profile 'ultramax'" in strip_ansi(result.output)

    def test_profile_set_outside_kite_project_exits_nonzero(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["profile", "set", "minimal"])
        finally:
            os.chdir(old_cwd)

        assert result.exit_code != 0
        assert "Not a Kite project" in strip_ansi(result.output)

    def test_profile_set_same_profile_is_idempotent(self, tmp_path):
        from typer.testing import CliRunner
        from kite_cli import app

        runner = CliRunner()
        project = tmp_path / "set-same"
        project.mkdir()
        self._init_project(runner, project, profile="minimal")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project)
            result = runner.invoke(app, ["profile", "set", "minimal"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0, result.output
        output = strip_ansi(result.output)
        assert "already set" in output
        opts = json.loads((project / ".kite" / "init-options.json").read_text())
        assert opts["profile"] == "minimal"
