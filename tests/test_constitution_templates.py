"""Regression tests for constitution scaffolding and constitution command rules."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION_TEMPLATE = REPO_ROOT / "templates" / "constitution-template.md"
CONSTITUTION_COMMAND = REPO_ROOT / "templates" / "commands" / "constitution.md"
PLAN_TEMPLATE = REPO_ROOT / "templates" / "plan-template.md"
SPEC_TEMPLATE = REPO_ROOT / "templates" / "spec-template.md"
TASKS_TEMPLATE = REPO_ROOT / "templates" / "tasks-template.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestConstitutionTemplate:
    def test_template_examples_include_general_workflow_rules(self):
        content = _read_text(CONSTITUTION_TEMPLATE)

        assert "Subagent-First Execution" in content
        assert "Official Docs First" in content
        assert "Rationale-Focused Comments" in content
        assert "Host Safety Rules" in content
        assert "Agent Collaboration Rules" in content
        assert "frontend-owned browser validation" in content.lower()
        assert "mcp/skills support" in content.lower()


class TestConstitutionCommand:
    def test_constitution_command_moves_general_rules_into_constitution(self):
        content = _read_text(CONSTITUTION_COMMAND)

        assert "project-wide workflow or coding rule" in content
        assert "encode it in the constitution" in content
        assert "subagent-first execution" in content
        assert "official-doc requirements for AI work" in content
        assert "comments that explain why rather than what" in content

    def test_constitution_validation_requires_project_wide_rules_to_land_in_constitution(self):
        content = _read_text(CONSTITUTION_COMMAND)

        assert "Project-wide workflow or coding rules supplied by the user" in content
        assert "are reflected in the constitution" in content


class TestConstitutionTemplatePropagation:
    def test_plan_template_turns_constitution_into_explicit_gate_checks(self):
        content = _read_text(PLAN_TEMPLATE)

        assert "**Constitutional Constraints**" in content
        assert "Read `.kite/memory/constitution.md`" in content
        assert "**Applicable principles**:" in content
        assert "**Constitution-driven checks**:" in content
        assert "**Approval**: Constitution Check" in content

    def test_spec_template_includes_constitutional_constraints_section(self):
        content = _read_text(SPEC_TEMPLATE)

        assert "Functional requirements must honor any relevant principles" in content
        assert "## Constitutional Constraints" in content
        assert "official-doc-first AI guidance" in content

    def test_tasks_template_references_constitution_backed_delivery_rules(self):
        content = _read_text(TASKS_TEMPLATE)

        assert "Per `.kite/memory/constitution.md`" in content
        assert "official-doc-first AI work, host safety" in content
        assert "subagent-first execution" in content