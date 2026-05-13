"""Tests for the `kite self` sub-app (`self check` and `self upgrade`).

Network isolation contract (SC-004 / FR-014): every test that exercises
`kite self check` or `_fetch_latest_release_tag()` MUST mock
`urllib.request.urlopen` so no real outbound call ever reaches
api.github.com. `kite self upgrade` MUST mock `_fetch_latest_release_tag()`
so dry-runs remain network-isolated while still exercising the release-check
contract. Run this module under `pytest-socket` (if installed) with
`--disable-socket` as an extra safety net.
"""

import json
import urllib.error
import importlib.metadata
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from kite_cli import (
    _get_installed_version,
    _fetch_latest_release_tag,
    _is_newer,
    _normalize_tag,
    app,
)

from tests.conftest import strip_ansi

runner = CliRunner()

SENTINEL_GH_TOKEN = "SENTINEL-GH-TOKEN-VALUE"
SENTINEL_GITHUB_TOKEN = "SENTINEL-GITHUB-TOKEN-VALUE"


def _mock_urlopen_response(payload: dict) -> MagicMock:
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    cm = MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = False
    return cm


def _http_error(code: int, message: str = "error") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://api.github.com/repos/Karnonson/kite/releases/latest",
        code=code,
        msg=message,
        hdrs={},  # type: ignore[arg-type]
        fp=None,
    )


class TestSelfUpgrade:
    def test_default_dry_run_detects_uv_and_does_not_run_installer(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)
        ) as fetch_latest, patch(
            "kite_cli.sys.executable",
            "/home/user/.local/share/uv/tools/kite-cli/bin/python",
        ), patch("kite_cli.subprocess.run") as run:
            result = runner.invoke(app, ["self", "upgrade"])

        output = strip_ansi(result.output)
        assert result.exit_code == 0
        fetch_latest.assert_called_once_with()
        run.assert_not_called()
        assert "Installed: 0.7.4" in output
        assert "Latest release: 0.9.0" in output
        assert "Install method: uv tool" in output
        assert "Update available: 0.7.4 → 0.9.0" in output
        assert (
            "uv tool install kite-cli --force --from "
            "git+https://github.com/Karnonson/kite.git@v0.9.0"
        ) in output
        assert "Dry run only" in output

    def test_explicit_dry_run_is_network_isolated_through_mocked_helper(self):
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=AssertionError("upgrade must use the mocked release helper"),
        ), patch("kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)), patch(
            "kite_cli._get_installed_version", return_value="0.7.4"
        ), patch(
            "kite_cli.sys.executable",
            "/home/user/.local/share/uv/tools/kite-cli/bin/python",
        ), patch("kite_cli.subprocess.run") as run:
            result = runner.invoke(app, ["self", "upgrade", "--dry-run"])

        assert result.exit_code == 0
        run.assert_not_called()

    def test_dry_run_detects_pipx_and_prints_pipx_command(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)
        ), patch(
            "kite_cli.sys.executable",
            "/home/user/.local/share/pipx/venvs/kite-cli/bin/python",
        ), patch("kite_cli.subprocess.run") as run:
            result = runner.invoke(app, ["self", "upgrade"])

        output = strip_ansi(result.output)
        assert result.exit_code == 0
        run.assert_not_called()
        assert "Install method: pipx" in output
        assert "pipx install --force git+https://github.com/Karnonson/kite.git@v0.9.0" in output

    def test_unknown_install_method_prints_manual_commands_and_does_not_apply(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)
        ), patch("kite_cli.sys.executable", "/opt/kite/bin/python"), patch(
            "kite_cli.subprocess.run"
        ) as run:
            result = runner.invoke(app, ["self", "upgrade", "--apply", "--yes"])

        output = strip_ansi(result.output)
        assert result.exit_code == 1
        run.assert_not_called()
        assert "Install method: unknown" in output
        assert "could not safely detect" in output
        assert "uv tool install kite-cli --force --from git+https://github.com/Karnonson/kite.git@v0.9.0" in output
        assert "pipx install --force git+https://github.com/Karnonson/kite.git@v0.9.0" in output

    def test_apply_requires_confirmation_when_yes_is_not_set(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)
        ), patch(
            "kite_cli.sys.executable",
            "/home/user/.local/share/uv/tools/kite-cli/bin/python",
        ), patch("kite_cli.subprocess.run") as run:
            result = runner.invoke(app, ["self", "upgrade", "--apply"], input="n\n")

        output = strip_ansi(result.output)
        assert result.exit_code != 0
        run.assert_not_called()
        assert "Run this command now?" in output

    def test_apply_with_yes_runs_detected_installer_command(self):
        completed = MagicMock(returncode=0)
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli._fetch_latest_release_tag", return_value=("v0.9.0", None)
        ), patch(
            "kite_cli.sys.executable",
            "/home/user/.local/share/uv/tools/kite-cli/bin/python",
        ), patch("kite_cli.subprocess.run", return_value=completed) as run:
            result = runner.invoke(app, ["self", "upgrade", "--apply", "--yes"])

        assert result.exit_code == 0
        run.assert_called_once_with(
            [
                "uv",
                "tool",
                "install",
                "kite-cli",
                "--force",
                "--from",
                "git+https://github.com/Karnonson/kite.git@v0.9.0",
            ],
            check=False,
        )
        assert "upgrade command completed" in strip_ansi(result.output)


class TestIsNewer:
    def test_latest_strictly_greater_returns_true(self):
        assert _is_newer("0.8.0", "0.7.4") is True

    def test_equal_versions_returns_false(self):
        assert _is_newer("0.7.4", "0.7.4") is False

    def test_current_greater_than_latest_returns_false(self):
        assert _is_newer("0.7.0", "0.7.4") is False

    def test_dev_build_ahead_of_release_returns_false(self):
        assert _is_newer("0.7.4", "0.7.5.dev0") is False

    def test_invalid_version_returns_false(self):
        assert _is_newer("not-a-version", "0.7.4") is False

    def test_local_version_containing_unknown_is_not_treated_as_sentinel(self):
        assert _is_newer("1.2.4", "1.2.3+unknown") is True


class TestInstalledVersion:
    def test_invalid_metadata_error_returns_unknown(self):
        invalid_metadata_error = getattr(importlib.metadata, "InvalidMetadataError", None)
        if invalid_metadata_error is None:
            # Python versions without InvalidMetadataError: simulate with a
            # custom exception to verify the guarded except path works.
            class _FakeInvalidMetadataError(Exception):
                pass
            invalid_metadata_error = _FakeInvalidMetadataError
            # Patch the attribute onto importlib.metadata so the production
            # getattr() finds it during this test.
            with patch.object(importlib.metadata, "InvalidMetadataError", invalid_metadata_error, create=True):
                with patch(
                    "importlib.metadata.version",
                    side_effect=invalid_metadata_error("bad metadata"),
                ):
                    assert _get_installed_version() == "unknown"
        else:
            with patch(
                "importlib.metadata.version",
                side_effect=invalid_metadata_error("bad metadata"),
            ):
                assert _get_installed_version() == "unknown"


class TestNormalizeTag:
    def test_strips_single_leading_v(self):
        assert _normalize_tag("v0.7.4") == "0.7.4"

    def test_idempotent_when_no_leading_v(self):
        assert _normalize_tag("0.7.4") == "0.7.4"

    def test_strips_exactly_one_v(self):
        assert _normalize_tag("vv0.7.4") == "v0.7.4"

    def test_empty_string_passthrough(self):
        assert _normalize_tag("") == ""


class TestUserStory1:
    def test_newer_available_prints_update_and_install_command(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen",
            return_value=_mock_urlopen_response({"tag_name": "v0.9.0"}),
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Update available" in output
        assert "0.7.4" in output
        assert "0.9.0" in output
        assert "git+https://github.com/Karnonson/kite.git@v0.9.0" in output

    def test_up_to_date_prints_current_only(self):
        with patch("kite_cli._get_installed_version", return_value="0.9.0"), patch(
            "kite_cli.urllib.request.urlopen",
            return_value=_mock_urlopen_response({"tag_name": "v0.9.0"}),
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Up to date: 0.9.0" in output
        assert "Update available" not in output
        assert "git+https://" not in output

    def test_dev_build_ahead_of_release_is_up_to_date(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.5.dev0"), patch(
            "kite_cli.urllib.request.urlopen",
            return_value=_mock_urlopen_response({"tag_name": "v0.7.4"}),
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Update available" not in output
        assert "Up to date" in output

    def test_unknown_installed_still_prints_latest_and_reinstall(self):
        with patch("kite_cli._get_installed_version", return_value="unknown"), patch(
            "kite_cli.urllib.request.urlopen",
            return_value=_mock_urlopen_response({"tag_name": "v0.7.4"}),
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Current version could not be determined" in output
        assert "0.7.4" in output
        assert "git+https://github.com/Karnonson/kite.git@v0.7.4" in output

    def test_unparseable_tag_routes_to_indeterminate(self):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen",
            return_value=_mock_urlopen_response({"tag_name": "not-a-version"}),
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Update available" not in output
        assert "Up to date" in output
        assert "0.7.4" in output


class TestFailureCategorization:
    def test_urlerror_maps_to_offline(self):
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=urllib.error.URLError("no route to host"),
        ):
            tag, reason = _fetch_latest_release_tag()
        assert tag is None
        assert reason == "offline or timeout"

    def test_timeout_maps_to_offline(self):
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=TimeoutError(),
        ):
            tag, reason = _fetch_latest_release_tag()
        assert tag is None
        assert reason == "offline or timeout"

    def test_403_maps_to_rate_limited(self):
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=_http_error(403, "rate limited"),
        ):
            tag, reason = _fetch_latest_release_tag()
        assert tag is None
        assert reason == "rate limited (try setting GH_TOKEN or GITHUB_TOKEN)"

    @pytest.mark.parametrize("code", [404, 500, 502])
    def test_other_http_uses_code_string(self, code):
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=_http_error(code, "oops"),
        ):
            tag, reason = _fetch_latest_release_tag()
        assert tag is None
        assert reason == f"HTTP {code}"

    def test_generic_exception_propagates(self):
        # Per research D-006, no catch-all exists; RuntimeError MUST bubble.
        with patch(
            "kite_cli.urllib.request.urlopen",
            side_effect=RuntimeError("boom"),
        ):
            with pytest.raises(RuntimeError):
                _fetch_latest_release_tag()


_FAILURE_CASES = [
    ("offline or timeout", urllib.error.URLError("down")),
    ("rate limited (try setting GH_TOKEN or GITHUB_TOKEN)", _http_error(403)),
    ("HTTP 500", _http_error(500)),
]


class TestUserStory2:
    @pytest.mark.parametrize("expected_reason, side_effect", _FAILURE_CASES)
    def test_failure_prints_installed_plus_one_line_reason(
        self, expected_reason, side_effect
    ):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen", side_effect=side_effect
        ):
            result = runner.invoke(app, ["self", "check"])
        output = strip_ansi(result.output)
        assert "Installed: 0.7.4" in output
        if expected_reason == "rate limited (try setting GH_TOKEN or GITHUB_TOKEN)":
            assert "Could not check latest release: rate limited" in output
            assert "GH_TOKEN" in output
            assert "GITHUB_TOKEN" in output
        else:
            assert f"Could not check latest release: {expected_reason}" in output

    @pytest.mark.parametrize("_expected_reason, side_effect", _FAILURE_CASES)
    def test_failure_exits_zero(self, _expected_reason, side_effect):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen", side_effect=side_effect
        ):
            result = runner.invoke(app, ["self", "check"])
        assert result.exit_code == 0

    @pytest.mark.parametrize("_expected_reason, side_effect", _FAILURE_CASES)
    def test_failure_output_contains_no_traceback_no_url(
        self, _expected_reason, side_effect
    ):
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen", side_effect=side_effect
        ):
            result = runner.invoke(app, ["self", "check"])
        combined = (result.output or "") + (result.stderr or "")
        combined = strip_ansi(combined)
        assert "Traceback" not in combined
        assert "https://api.github.com" not in combined


def _capture_request_via_urlopen():
    captured = {}

    def _side_effect(req, timeout=None):
        captured["request"] = req
        return _mock_urlopen_response({"tag_name": "v0.7.4"})

    return captured, _side_effect


class TestUserStory3:
    def test_gh_token_attached_as_bearer_header(self, monkeypatch):
        monkeypatch.setenv("GH_TOKEN", SENTINEL_GH_TOKEN)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") == f"Bearer {SENTINEL_GH_TOKEN}"

    def test_github_token_used_when_gh_token_unset(self, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_TOKEN", SENTINEL_GITHUB_TOKEN)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") == f"Bearer {SENTINEL_GITHUB_TOKEN}"

    def test_no_authorization_header_when_both_unset(self, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") is None

    def test_empty_string_gh_token_treated_as_unset(self, monkeypatch):
        monkeypatch.setenv("GH_TOKEN", "")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") is None

    def test_whitespace_only_gh_token_treated_as_unset(self, monkeypatch):
        monkeypatch.setenv("GH_TOKEN", "   ")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") is None

    def test_whitespace_only_gh_token_falls_back_to_github_token(self, monkeypatch):
        monkeypatch.setenv("GH_TOKEN", "   ")
        monkeypatch.setenv("GITHUB_TOKEN", SENTINEL_GITHUB_TOKEN)
        captured, side_effect = _capture_request_via_urlopen()
        with patch("kite_cli.urllib.request.urlopen", side_effect=side_effect):
            _fetch_latest_release_tag()
        req = captured["request"]
        assert req.get_header("Authorization") == f"Bearer {SENTINEL_GITHUB_TOKEN}"

    @pytest.mark.parametrize("_reason, side_effect", _FAILURE_CASES)
    def test_gh_token_never_appears_in_failure_output(
        self, _reason, side_effect, monkeypatch
    ):
        monkeypatch.setenv("GH_TOKEN", SENTINEL_GH_TOKEN)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen", side_effect=side_effect
        ):
            result = runner.invoke(app, ["self", "check"])
        combined = strip_ansi((result.output or "") + (result.stderr or ""))
        assert SENTINEL_GH_TOKEN not in combined

    @pytest.mark.parametrize("_reason, side_effect", _FAILURE_CASES)
    def test_github_token_never_appears_in_failure_output(
        self, _reason, side_effect, monkeypatch
    ):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_TOKEN", SENTINEL_GITHUB_TOKEN)
        with patch("kite_cli._get_installed_version", return_value="0.7.4"), patch(
            "kite_cli.urllib.request.urlopen", side_effect=side_effect
        ):
            result = runner.invoke(app, ["self", "check"])
        combined = strip_ansi((result.output or "") + (result.stderr or ""))
        assert SENTINEL_GITHUB_TOKEN not in combined
