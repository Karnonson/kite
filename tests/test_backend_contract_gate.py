"""Tests for the hard contract gate between `kite.backend` and `kite.frontend`."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml


pytestmark = pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="contract gate is a bash script; Windows runners may not have bash on PATH",
)


REPO_ROOT = Path(__file__).resolve().parent.parent
KITE_WF = REPO_ROOT / "workflows" / "kite" / "workflow.yml"


@pytest.fixture(scope="module")
def gate_script() -> str:
    wf = yaml.safe_load(KITE_WF.read_text(encoding="utf-8"))
    gate = next(s for s in wf["steps"] if s.get("id") == "contract-gate")
    assert gate["type"] == "shell"
    return gate["run"]


def _run_gate(gate_script: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", gate_script],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class TestContractGateAborts:
    def test_aborts_when_no_specs_directory(self, gate_script: str, tmp_path: Path):
        result = _run_gate(gate_script, tmp_path)
        assert result.returncode != 0
        assert "no specs" in result.stderr.lower()

    def test_aborts_when_contract_missing(self, gate_script: str, tmp_path: Path):
        spec_dir = tmp_path / "specs" / "001-demo"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# spec", encoding="utf-8")

        result = _run_gate(gate_script, tmp_path)

        assert result.returncode != 0
        assert "contract.md" in result.stderr
        assert "missing" in result.stderr.lower()

    def test_aborts_when_contract_has_todo(self, gate_script: str, tmp_path: Path):
        spec_dir = tmp_path / "specs" / "001-demo"
        spec_dir.mkdir(parents=True)
        (spec_dir / "contract.md").write_text(
            "# Contract\n\n## Endpoint\n\nTODO: fill in\n",
            encoding="utf-8",
        )

        result = _run_gate(gate_script, tmp_path)

        assert result.returncode != 0
        assert "placeholder" in result.stderr.lower() or "todo" in result.stderr.lower()

    def test_aborts_when_contract_has_angle_placeholder(self, gate_script: str, tmp_path: Path):
        spec_dir = tmp_path / "specs" / "001-demo"
        spec_dir.mkdir(parents=True)
        (spec_dir / "contract.md").write_text(
            "# Contract\n\nGET /api/<resource> returns <payload>.\n",
            encoding="utf-8",
        )

        result = _run_gate(gate_script, tmp_path)

        assert result.returncode != 0


class TestContractGatePasses:
    def test_passes_when_contract_complete(self, gate_script: str, tmp_path: Path):
        spec_dir = tmp_path / "specs" / "001-demo"
        spec_dir.mkdir(parents=True)
        (spec_dir / "contract.md").write_text(
            "# Contract\n\n"
            "## GET /api/items\n\n"
            "Returns a JSON array of items with fields id (int) and name (string).\n",
            encoding="utf-8",
        )

        result = _run_gate(gate_script, tmp_path)

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "OK" in result.stdout

    def test_picks_latest_spec_directory(self, gate_script: str, tmp_path: Path):
        old = tmp_path / "specs" / "001-old"
        old.mkdir(parents=True)
        (old / "contract.md").write_text("TODO\n", encoding="utf-8")

        new = tmp_path / "specs" / "002-new"
        new.mkdir(parents=True)
        (new / "contract.md").write_text(
            "# Contract\n\n## GET /api/items\n\nReturns items.\n",
            encoding="utf-8",
        )

        result = _run_gate(gate_script, tmp_path)

        assert result.returncode == 0, f"stderr: {result.stderr}"
