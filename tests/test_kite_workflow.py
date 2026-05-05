"""Tests for the bundled `kite` SDLC workflow definition.

These tests load `workflows/kite/workflow.yml` and validate its structure,
the founder fast path, the contract gate, and that all referenced commands resolve.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
KITE_WF = REPO_ROOT / "workflows" / "kite" / "workflow.yml"


@pytest.fixture(scope="module")
def kite_workflow() -> dict:
    return yaml.safe_load(KITE_WF.read_text())


class TestKiteWorkflowStructure:
    def test_yaml_is_loadable(self, kite_workflow):
        assert kite_workflow["schema_version"] == "1.0"
        assert kite_workflow["workflow"]["id"] == "kite"

    def test_inputs_include_idea_persona_auto_approve(self, kite_workflow):
        inputs = kite_workflow["inputs"]
        assert "idea" in inputs and inputs["idea"]["required"] is True
        assert "persona" in inputs
        assert inputs["persona"]["enum"] == ["founder", "junior"]
        assert "auto_approve" in inputs
        assert inputs["auto_approve"]["default"] is False

    def test_step_order_covers_full_sdlc(self, kite_workflow):
        commands = [
            s["command"]
            for s in kite_workflow["steps"]
            if "command" in s
        ]
        assert commands == [
            "kite.constitution",
            "kite.discover",
            "kite.specify",
            "kite.design",
            "kite.clarify",
            "kite.plan",
            "kite.tasks",
            "kite.backend",
            "kite.frontend",
            "kite.docs",
            "kite.qa",
        ]

    def test_review_gates_are_skippable_via_auto_approve(self, kite_workflow):
        # Each review gate is wrapped in an `if not inputs.auto_approve` block.
        skippable_ids = {
            "skip-or-gate-constitution",
            "skip-or-gate-discover",
            "skip-or-gate-specify",
            "skip-or-gate-design",
            "skip-or-gate-clarify",
            "skip-or-gate-plan",
        }
        if_steps = [s for s in kite_workflow["steps"] if s.get("type") == "if"]
        if_ids = {s["id"] for s in if_steps}
        assert skippable_ids.issubset(if_ids)
        for s in if_steps:
            if s["id"] in skippable_ids:
                assert "auto_approve" in s["condition"]
                # then must contain a single nested gate step
                assert any(t.get("type") == "gate" for t in s["then"])

    def test_founder_flow_uses_split_implementation_stages(self, kite_workflow):
        steps = kite_workflow["steps"]
        ids = [s["id"] for s in steps]
        assert "constitution" in ids
        assert "clarify" in ids
        assert "backend" in ids
        assert "frontend" in ids
        assert "docs" in ids
        assert "qa" in ids
        assert "contract-gate" in ids
        assert "implement" not in ids
        assert ids.index("design") < ids.index("clarify") < ids.index("plan")
        assert ids.index("tasks") < ids.index("backend")
        assert ids.index("backend") < ids.index("contract-gate") < ids.index("frontend") < ids.index("docs") < ids.index("qa")

    def test_tasks_gate_is_required_before_implementation(self, kite_workflow):
        steps = kite_workflow["steps"]
        ids = [s["id"] for s in steps]
        gate = next(s for s in steps if s["id"] == "gate-tasks")
        assert gate["type"] == "gate"
        assert "tasks.md" in gate["message"]
        assert ids.index("tasks") < ids.index("gate-tasks") < ids.index("backend")
        assert "auto_approve" not in str(gate)

    def test_contract_gate_is_hard_shell_step(self, kite_workflow):
        steps = kite_workflow["steps"]
        gate = next(s for s in steps if s["id"] == "contract-gate")
        assert gate["type"] == "shell"
        assert "contract.md" in gate["run"]
        assert "TODO" in gate["run"]


class TestKiteWorkflowValidates:
    def test_engine_validation_passes(self, kite_workflow, tmp_path):
        from kite_cli.workflows.engine import WorkflowEngine

        # Copy the workflow into a temp .kite/ project so the engine can load it.
        project = tmp_path / "proj"
        wf_dir = project / ".kite" / "workflows" / "kite"
        wf_dir.mkdir(parents=True)
        (wf_dir / "workflow.yml").write_text(KITE_WF.read_text())

        engine = WorkflowEngine(project_root=project)
        wf = engine.load_workflow("kite")
        assert wf.id == "kite"
        errors = engine.validate(wf)
        assert errors == [], f"validation errors: {errors}"
