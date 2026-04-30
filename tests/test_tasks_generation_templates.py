"""Regression tests for tracer-bullet task generation guidance.

These assertions protect the task-generation prompt and sample tasks template
from drifting away from the intended phase-gated, persona-owned structure.
"""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO_ROOT / "templates" / "commands"
TASKS_COMMAND = REPO_ROOT / "templates" / "commands" / "tasks.md"
TASKS_TEMPLATE = REPO_ROOT / "templates" / "tasks-template.md"
BACKEND_COMMAND = REPO_ROOT / "templates" / "commands" / "backend.md"
FRONTEND_COMMAND = REPO_ROOT / "templates" / "commands" / "frontend.md"

PERSONA_LABELS = ("[backend]", "[frontend]", "[qa]", "[docs]", "[ops]")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sample_task_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("- [ ] T")]


class TestTasksPromptRules:
    def test_all_command_frontmatter_is_valid_yaml(self):
        for command_file in sorted(COMMANDS_DIR.glob("*.md")):
            content = command_file.read_text(encoding="utf-8")
            assert content.startswith("---"), f"missing frontmatter: {command_file.name}"
            _, frontmatter, _ = content.split("---", 2)
            parsed = yaml.safe_load(frontmatter) or {}
            assert isinstance(parsed, dict), command_file.name

    def test_requires_tracer_bullet_phase_verification(self):
        content = _read_text(TASKS_COMMAND)

        assert "Use tracer-bullet planning." in content
        assert "Every phase MUST end with a concrete verification task" in content
        assert (
            "Backend verification must use a terminal command or the framework's integrated development environment"
            in content
        )
        assert "Mastra Dev Studio" in content

    def test_requires_split_backend_frontend_ownership(self):
        content = _read_text(TASKS_COMMAND)

        assert "NEVER create a mixed ownership task" in content
        assert "split backend and frontend work into separate task groups whenever both are in scope" in content
        assert "[Persona] label" in content
        assert "task count per persona" in content.lower()


class TestTasksTemplate:
    def test_sample_tasks_have_exactly_one_persona_label(self):
        task_lines = _sample_task_lines(_read_text(TASKS_TEMPLATE))

        assert task_lines, "expected sample task lines in tasks-template.md"
        for line in task_lines:
            matches = [label for label in PERSONA_LABELS if label in line]
            assert len(matches) == 1, f"expected exactly one persona label in: {line}"

    def test_story_phase_samples_include_backend_frontend_and_verification_sections(self):
        content = _read_text(TASKS_TEMPLATE)

        assert "### Backend Slice for User Story 1" in content
        assert "### Backend Verification for User Story 1" in content
        assert "### Frontend Slice for User Story 1" in content
        assert "### Frontend Verification for User Story 1" in content
        assert "Verify the story 1 backend slice in the terminal" in content
        assert "Verify the story 1 UI in the browser or component test runner" in content


class TestImplementationPrompts:
    def test_backend_prompt_preserves_phase_order_and_runs_verification_tasks(self):
        content = _read_text(BACKEND_COMMAND)

        assert "Respect tracer-bullet phase gates." in content
        assert "Build a list of unchecked tasks where the tag is `[backend]`, preserving phase order." in content
        assert (
            "If the task is a backend verification task, run the exact terminal command or framework dev-environment flow written in `tasks.md` before marking it done."
            in content
        )

    def test_frontend_prompt_preserves_phase_order_and_runs_verification_tasks(self):
        content = _read_text(FRONTEND_COMMAND)

        assert "Respect tracer-bullet phase gates." in content
        assert "Build a list of unchecked tasks tagged `[frontend]`, preserving phase order." in content
        assert (
            "If the task is a frontend verification task, run the exact browser, component-test, or dev-preview flow written in `tasks.md` before marking it done."
            in content
        )