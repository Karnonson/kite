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
DOCS_COMMAND = REPO_ROOT / "templates" / "commands" / "docs.md"
QA_COMMAND = REPO_ROOT / "templates" / "commands" / "qa.md"
DESIGN_COMMAND = REPO_ROOT / "templates" / "commands" / "design.md"
DISCOVER_COMMAND = REPO_ROOT / "templates" / "commands" / "discover.md"
IMPLEMENT_COMMAND = REPO_ROOT / "templates" / "commands" / "implement.md"
PLAN_COMMAND = REPO_ROOT / "templates" / "commands" / "plan.md"
RESEARCH_COMMAND = REPO_ROOT / "templates" / "commands" / "research.md"
SPECIFY_COMMAND = REPO_ROOT / "templates" / "commands" / "specify.md"
START_COMMAND = REPO_ROOT / "templates" / "commands" / "start.md"
PLAN_TEMPLATE = REPO_ROOT / "templates" / "plan-template.md"
PRE_IMPLEMENTATION_COMMANDS = (
    "constitution",
    "discover",
    "specify",
    "design",
    "clarify",
    "plan",
    "tasks",
)
BROWNFIELD_COMMANDS = (
    START_COMMAND,
    DISCOVER_COMMAND,
    SPECIFY_COMMAND,
    DESIGN_COMMAND,
    PLAN_COMMAND,
    TASKS_COMMAND,
    BACKEND_COMMAND,
    FRONTEND_COMMAND,
    IMPLEMENT_COMMAND,
)
DEPENDENCY_VERSION_COMMANDS = (
    PLAN_COMMAND,
    TASKS_COMMAND,
    BACKEND_COMMAND,
    FRONTEND_COMMAND,
    IMPLEMENT_COMMAND,
    RESEARCH_COMMAND,
)

PERSONA_LABELS = ("[backend]", "[frontend]", "[qa]", "[docs]", "[ops]")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sample_task_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("- [ ] T")]


def _frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    _, frontmatter, _ = content.split("---", 2)
    parsed = yaml.safe_load(frontmatter) or {}
    assert isinstance(parsed, dict), path.name
    return parsed


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

    def test_no_pre_implementation_handoff_auto_sends(self):
        for name in PRE_IMPLEMENTATION_COMMANDS:
            handoffs = _frontmatter(COMMANDS_DIR / f"{name}.md").get("handoffs", [])
            assert all(handoff.get("send") is not True for handoff in handoffs), name

    def test_conversational_commands_ask_one_question_at_a_time(self):
        for name in ("constitution", "discover", "specify", "design", "clarify", "plan"):
            content = _read_text(COMMANDS_DIR / f"{name}.md")
            assert "one question at a time" in content.lower(), name

    def test_no_testing_optional_language_remains(self):
        for path in [
            TASKS_COMMAND,
            TASKS_TEMPLATE,
            BACKEND_COMMAND,
            FRONTEND_COMMAND,
            QA_COMMAND,
        ]:
            content = _read_text(path).lower()
            assert "tests are optional" not in content, path.name
            assert "optional - only if tests" not in content, path.name

    def test_docs_command_exists_and_is_referenced(self):
        assert DOCS_COMMAND.exists()
        assert "Only `[docs]` tasks" in _read_text(DOCS_COMMAND)
        assert "kite.docs" in _read_text(FRONTEND_COMMAND)

    def test_brownfield_commands_inspect_existing_project_before_questions(self):
        for path in BROWNFIELD_COMMANDS:
            content = _read_text(path).lower()
            assert "brownfield" in content, path.name
            assert "existing" in content, path.name
            assert (
                "before asking" in content
                or "ask only" in content
                or "do not ask" in content
            ), path.name

    def test_dependency_prompts_forbid_latest_versions(self):
        for path in DEPENDENCY_VERSION_COMMANDS:
            content = _read_text(path)
            assert "`latest`" in content, path.name
            assert "floating" in content.lower(), path.name

    def test_ui_prompts_default_to_hamburger_sidebar_on_small_screens(self):
        for path in (DESIGN_COMMAND, TASKS_COMMAND, FRONTEND_COMMAND):
            content = _read_text(path).lower()
            assert "left-side hamburger sidebar/drawer" in content, path.name
            assert "small screens" in content, path.name


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

    def test_plan_and_tasks_require_approved_source_layout(self):
        plan_content = _read_text(PLAN_TEMPLATE)
        tasks_content = _read_text(TASKS_TEMPLATE)

        assert "## Approved Source Layout" in plan_content
        assert "Allowed write roots" in plan_content
        assert "Use only paths listed in plan.md's `## Approved Source Layout`" in tasks_content
        assert "Phase 1 MUST include a setup task" in tasks_content


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
        assert "launch the app and complete the primary flow in a browser/dev preview" in content

    def test_backend_frontend_require_fixing_caused_validation_failures(self):
        assert "fix it before continuing" in _read_text(BACKEND_COMMAND)
        assert "fix it before continuing" in _read_text(FRONTEND_COMMAND)

    def test_frontend_and_qa_include_accessibility_defaults(self):
        for path in (FRONTEND_COMMAND, QA_COMMAND, TASKS_TEMPLATE):
            content = _read_text(path)
            assert "keyboard access" in content
            assert "visible focus" in content
            assert "readable contrast" in content
            assert "clear labels" in content
            assert "clear error messages" in content
            assert "non-color" in content
