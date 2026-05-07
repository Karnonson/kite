"""Copilot integration — GitHub Copilot in VS Code.

Copilot has several unique behaviors compared to standard markdown agents:
- Commands use ``.agent.md`` extension (not ``.md``)
- Each command gets a companion ``.prompt.md`` file in ``.github/prompts/``
- Installs ``.vscode/settings.json`` with prompt file recommendations
- Context file lives at ``.github/copilot-instructions.md``
- Selected command templates can be emitted as ``.github/skills/kite-*/SKILL.md``
  instead of agent/prompt pairs

When ``--skills`` is passed via ``--integration-options``, Copilot scaffolds
commands as ``kite-<name>/SKILL.md`` directories under ``.github/skills/``
instead.
"""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Any

import yaml

from ..base import IntegrationBase, IntegrationOption, SkillsIntegration
from ..manifest import IntegrationManifest


def _allow_all() -> bool:
    """Return True if the Copilot CLI should run with full permissions.

    Checks ``KITE_COPILOT_ALLOW_ALL_TOOLS`` first (new canonical name).
    Falls back to the deprecated ``KITE_ALLOW_ALL_TOOLS`` if set,
    emitting a deprecation warning.  Default when neither is set: enabled.
    """
    new_var = os.environ.get("KITE_COPILOT_ALLOW_ALL_TOOLS")
    if new_var is not None:
        return new_var != "0"

    old_var = os.environ.get("KITE_ALLOW_ALL_TOOLS")
    if old_var is not None:
        warnings.warn(
            "KITE_ALLOW_ALL_TOOLS is deprecated; "
            "use KITE_COPILOT_ALLOW_ALL_TOOLS instead.",
            UserWarning,
            stacklevel=2,
        )
        return old_var != "0"

    return True


class _CopilotSkillsHelper(SkillsIntegration):
    """Internal helper used when Copilot is scaffolded in skills mode.

    Not registered in the integration registry — only used as a delegate
    by ``CopilotIntegration`` when ``--skills`` is passed.
    """

    key = "copilot"
    config = {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "commands_subdir": "skills",
        "install_url": "https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".github/skills",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": "/SKILL.md",
    }
    context_file = ".github/copilot-instructions.md"


class CopilotIntegration(IntegrationBase):
    """Integration for GitHub Copilot (VS Code IDE + CLI).

    The IDE integration (``requires_cli: False``) installs ``.agent.md``
    command files.  Workflow dispatch additionally requires the
    ``copilot`` CLI to be installed separately.

    When ``--skills`` is passed via ``--integration-options``, all commands
    are scaffolded as ``kite-<name>/SKILL.md`` under ``.github/skills/``.
    Default scaffolding uses ``.agent.md`` + ``.prompt.md`` except for
    templates listed in ``_skill_only_templates``.
    """

    key = "copilot"
    config = {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "commands_subdir": "agents",
        "install_url": "https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".github/agents",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".agent.md",
    }
    context_file = ".github/copilot-instructions.md"

    # Mutable flag set by setup() — indicates the active scaffolding mode.
    _skills_mode: bool = False
    _default_agent_templates = {
        "backend",
        "clarify",
        "constitution",
        "design",
        "discover",
        "docs",
        "frontend",
        "plan",
        "qa",
        "research",
        "specify",
        "start",
        "tasks",
    }
    _skill_only_templates = {"mastra"}
    standard_command_templates = frozenset(_default_agent_templates)

    def effective_invoke_separator(
        self, parsed_options: dict[str, Any] | None = None
    ) -> str:
        """Return ``"-"`` when skills mode is requested, ``"."`` otherwise."""
        if parsed_options and parsed_options.get("skills"):
            return "-"
        if self._skills_mode:
            return "-"
        return self.invoke_separator

    @classmethod
    def options(cls) -> list[IntegrationOption]:
        return [
            IntegrationOption(
                "--skills",
                is_flag=True,
                default=False,
                help="Scaffold commands as agent skills (kite-<name>/SKILL.md) instead of .agent.md files",
            ),
        ]

    def build_exec_args(
        self,
        prompt: str,
        *,
        model: str | None = None,
        output_json: bool = True,
    ) -> list[str] | None:
        # GitHub Copilot CLI uses ``copilot -p "prompt"`` for
        # non-interactive mode.  --yolo enables all permissions
        # (tools, paths, and URLs) so the agent can perform file
        # edits and shell commands without interactive prompts.
        # Controlled by KITE_COPILOT_ALLOW_ALL_TOOLS env var
        # (default: enabled).  The deprecated KITE_ALLOW_ALL_TOOLS
        # is also honoured as a fallback.
        args = ["copilot", "-p", prompt]
        if _allow_all():
            args.append("--yolo")
        if model:
            args.extend(["--model", model])
        if output_json:
            args.extend(["--output-format", "json"])
        return args

    def build_command_invocation(self, command_name: str, args: str = "") -> str:
        """Build the native invocation for a Copilot command.

        Default mode: agents are not slash-commands — return args as prompt.
        Skills mode: ``/kite-<stem>`` slash-command dispatch.
        """
        if self._skills_mode:
            stem = command_name
            if stem.startswith("kite."):
                stem = stem[len("kite."):]
            invocation = "/kite-" + stem.replace(".", "-")
            if args:
                invocation = f"{invocation} {args}"
            return invocation
        return args or ""

    def dispatch_command(
        self,
        command_name: str,
        args: str = "",
        *,
        project_root: Path | None = None,
        model: str | None = None,
        timeout: int = 600,
        stream: bool = True,
    ) -> dict[str, Any]:
        """Dispatch via ``--agent kite.<stem>`` instead of slash-commands.

        Copilot ``.agent.md`` files are agents, not skills.  The CLI
        selects them with ``--agent <name>`` and the prompt is just
        the user's arguments.

        In skills mode, the prompt includes the skill invocation
        (``/kite-<stem>``).
        """
        import subprocess

        stem = command_name
        if stem.startswith("kite."):
            stem = stem[len("kite."):]

        # Detect skills mode from the requested command's project layout when
        # not set via setup(). Default Copilot scaffolding writes only selected
        # commands (currently Mastra) as skills, so the presence of any skill
        # must not force every command down the skills path.
        skills_mode = self._skills_mode
        if not skills_mode and project_root:
            skills_mode = self._skill_file(project_root, stem).is_file()

        if skills_mode:
            prompt = "/kite-" + stem.replace(".", "-")
            if args:
                prompt = f"{prompt} {args}"
        else:
            agent_name = f"kite.{stem}"
            prompt = args or ""

        cli_args = ["copilot", "-p", prompt]
        if not skills_mode:
            cli_args.extend(["--agent", agent_name])
        if _allow_all():
            cli_args.append("--yolo")
        if model:
            cli_args.extend(["--model", model])
        if not stream:
            cli_args.extend(["--output-format", "json"])

        cwd = str(project_root) if project_root else None

        if stream:
            try:
                result = subprocess.run(
                    cli_args,
                    text=True,
                    cwd=cwd,
                )
            except KeyboardInterrupt:
                return {
                    "exit_code": 130,
                    "stdout": "",
                    "stderr": "Interrupted by user",
                }
            return {
                "exit_code": result.returncode,
                "stdout": "",
                "stderr": "",
            }

        result = subprocess.run(
            cli_args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def command_filename(self, template_name: str) -> str:
        """Copilot commands use ``.agent.md`` extension."""
        return f"kite.{template_name}.agent.md"

    def post_process_skill_content(self, content: str) -> str:
        """Inject Copilot-specific ``mode:`` field into SKILL.md frontmatter.

        Inserts ``mode: kite.<stem>`` before the closing ``---`` so
        Copilot can associate the skill with its agent mode.
        """
        lines = content.splitlines(keepends=True)

        # Extract skill name from frontmatter to derive the mode value
        dash_count = 0
        skill_name = ""
        for line in lines:
            stripped = line.rstrip("\n\r")
            if stripped == "---":
                dash_count += 1
                if dash_count == 2:
                    break
                continue
            if dash_count == 1:
                if stripped.startswith("mode:"):
                    return content  # already present
                if stripped.startswith("name:"):
                    # Parse: name: "kite-plan" → kite.plan
                    val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    # Convert kite-plan → kite.plan
                    if val.startswith("kite-"):
                        skill_name = "kite." + val[len("kite-"):]
                    else:
                        skill_name = val

        if not skill_name:
            return content

        # Inject mode: before the closing --- of frontmatter
        out: list[str] = []
        dash_count = 0
        injected = False
        for line in lines:
            stripped = line.rstrip("\n\r")
            if stripped == "---":
                dash_count += 1
                if dash_count == 2 and not injected:
                    if line.endswith("\r\n"):
                        eol = "\r\n"
                    elif line.endswith("\n"):
                        eol = "\n"
                    else:
                        eol = ""
                    out.append(f"mode: {skill_name}{eol}")
                    injected = True
            out.append(line)
        return "".join(out)

    def setup(
        self,
        project_root: Path,
        manifest: IntegrationManifest,
        parsed_options: dict[str, Any] | None = None,
        **opts: Any,
    ) -> list[Path]:
        """Install copilot commands, selected skills, and VS Code settings.

        When ``parsed_options["skills"]`` is truthy, delegates to skills
        scaffolding (``kite-<name>/SKILL.md`` under ``.github/skills/``).
        Otherwise uses the default ``.agent.md`` + ``.prompt.md`` layout
        except for skill-only templates.
        """
        parsed_options = parsed_options or {}
        self._skills_mode = bool(parsed_options.get("skills"))
        if self._skills_mode:
            return self._setup_skills(project_root, manifest, parsed_options, **opts)
        return self._setup_default(project_root, manifest, parsed_options, **opts)

    def _setup_default(
        self,
        project_root: Path,
        manifest: IntegrationManifest,
        parsed_options: dict[str, Any] | None = None,
        **opts: Any,
    ) -> list[Path]:
        """Default mode: agent/prompt pairs plus selected skill-only templates."""
        project_root_resolved = project_root.resolve()
        if manifest.project_root != project_root_resolved:
            raise ValueError(
                f"manifest.project_root ({manifest.project_root}) does not match "
                f"project_root ({project_root_resolved})"
            )

        templates = self.filter_command_templates(
            self.list_command_templates(), parsed_options
        )
        if not templates:
            return []
        agent_templates = [
            template for template in templates
            if template.stem not in self._skill_only_templates
        ]
        skill_templates = [
            template for template in templates
            if template.stem in self._skill_only_templates
        ]

        dest = self.commands_dest(project_root)
        dest_resolved = dest.resolve()
        try:
            dest_resolved.relative_to(project_root_resolved)
        except ValueError as exc:
            raise ValueError(
                f"Integration destination {dest_resolved} escapes "
                f"project root {project_root_resolved}"
            ) from exc
        if agent_templates:
            dest.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []

        script_type = opts.get("script_type", "sh")
        arg_placeholder = self.registrar_config.get("args", "$ARGUMENTS")

        # 1. Process and write command files as .agent.md
        for src_file in agent_templates:
            raw = src_file.read_text(encoding="utf-8")
            processed = self.process_template(
                raw, self.key, script_type, arg_placeholder,
                context_file=self.context_file or "",
            )
            dst_name = self.command_filename(src_file.stem)
            dst_file = self.write_file_and_record(
                processed, dest / dst_name, project_root, manifest
            )
            created.append(dst_file)

        # 2. Generate companion .prompt.md files from the templates we just wrote
        prompts_dir = project_root / ".github" / "prompts"
        for src_file in agent_templates:
            cmd_name = f"kite.{src_file.stem}"
            prompt_content = f"---\nagent: {cmd_name}\n---\n"
            prompt_file = self.write_file_and_record(
                prompt_content,
                prompts_dir / f"{cmd_name}.prompt.md",
                project_root,
                manifest,
            )
            created.append(prompt_file)

        # 3. Generate selected commands as Copilot skills only.
        for src_file in skill_templates:
            created.append(
                self._write_skill_template(src_file, project_root, manifest, **opts)
            )

        # Write .vscode/settings.json
        settings_src = self._vscode_settings_path()
        if settings_src and settings_src.is_file():
            dst_settings = project_root / ".vscode" / "settings.json"
            dst_settings.parent.mkdir(parents=True, exist_ok=True)
            settings_data = self._vscode_settings_data(settings_src, agent_templates)
            if dst_settings.exists():
                # Merge into existing — don't track since we can't safely
                # remove the user's settings file on uninstall.
                self._merge_vscode_settings_data(settings_data, dst_settings)
            else:
                dst_settings = self.write_file_and_record(
                    json.dumps(settings_data, indent=4) + "\n",
                    dst_settings,
                    project_root,
                    manifest,
                )
                created.append(dst_settings)

        # 4. Upsert managed context section into the agent context file
        self.upsert_context_section(project_root)

        return created

    @staticmethod
    def _skill_name(command_name: str) -> str:
        stem = command_name
        if stem.startswith("kite."):
            stem = stem[len("kite."):]
        return "kite-" + stem.replace(".", "-")

    def _skill_file(self, project_root: Path, command_name: str) -> Path:
        return (
            project_root
            / ".github"
            / "skills"
            / self._skill_name(command_name)
            / "SKILL.md"
        )

    def _write_skill_template(
        self,
        src_file: Path,
        project_root: Path,
        manifest: IntegrationManifest,
        **opts: Any,
    ) -> Path:
        raw = src_file.read_text(encoding="utf-8")
        command_name = src_file.stem
        skill_name = self._skill_name(command_name)

        frontmatter: dict[str, Any] = {}
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    if isinstance(fm, dict):
                        frontmatter = fm
                except yaml.YAMLError:
                    pass

        processed_body = self.process_template(
            raw,
            self.key,
            opts.get("script_type", "sh"),
            "$ARGUMENTS",
            context_file=self.context_file or "",
            invoke_separator="-",
        )
        if processed_body.startswith("---"):
            parts = processed_body.split("---", 2)
            if len(parts) >= 3:
                processed_body = parts[2]

        description = frontmatter.get("description", "")
        if not description:
            description = f"Kite: {command_name} workflow"

        def _quote(v: str) -> str:
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'

        skill_content = (
            f"---\n"
            f"name: {_quote(skill_name)}\n"
            f"description: {_quote(description)}\n"
            f"compatibility: {_quote('Requires Kite project structure with .kite/ directory')}\n"
            f"metadata:\n"
            f"  author: {_quote('kite-core')}\n"
            f"  source: {_quote('templates/commands/' + src_file.name)}\n"
            f"---\n"
            f"{processed_body}"
        )
        skill_content = self.post_process_skill_content(skill_content)

        return self.write_file_and_record(
            skill_content,
            self._skill_file(project_root, command_name),
            project_root,
            manifest,
        )

    def _setup_skills(
        self,
        project_root: Path,
        manifest: IntegrationManifest,
        parsed_options: dict[str, Any] | None = None,
        **opts: Any,
    ) -> list[Path]:
        """Skills mode: delegate to ``_CopilotSkillsHelper`` then post-process."""
        helper = _CopilotSkillsHelper()
        created = SkillsIntegration.setup(
            helper, project_root, manifest, parsed_options, **opts
        )

        # Post-process generated skill files with Copilot-specific frontmatter
        skills_dir = helper.skills_dest(project_root).resolve()
        for path in created:
            try:
                path.resolve().relative_to(skills_dir)
            except ValueError:
                continue
            if path.name != "SKILL.md":
                continue

            content = path.read_text(encoding="utf-8")
            updated = self.post_process_skill_content(content)
            if updated != content:
                path.write_bytes(updated.encode("utf-8"))
                self.record_file_in_manifest(path, project_root, manifest)

        return created

    def _vscode_settings_path(self) -> Path | None:
        """Return path to the bundled vscode-settings.json template."""
        tpl_dir = self.shared_templates_dir()
        if tpl_dir:
            candidate = tpl_dir / "vscode-settings.json"
            if candidate.is_file():
                return candidate
        return None

    @staticmethod
    def _vscode_settings_data(src: Path, agent_templates: list[Path]) -> dict[str, Any]:
        """Load VS Code settings and limit prompt recommendations to installed agents."""
        settings = json.loads(src.read_text(encoding="utf-8"))
        recommendations = settings.get("chat.promptFilesRecommendations")
        if isinstance(recommendations, dict):
            settings["chat.promptFilesRecommendations"] = {
                f"kite.{template.stem}": True for template in agent_templates
            }
        return settings

    @staticmethod
    def _merge_vscode_settings(src: Path, dst: Path) -> None:
        """Merge settings from *src* into existing *dst* JSON file."""
        CopilotIntegration._merge_vscode_settings_data(
            json.loads(src.read_text(encoding="utf-8")), dst
        )

    @staticmethod
    def _merge_vscode_settings_data(new_settings: dict[str, Any], dst: Path) -> None:
        """Merge settings from *src* into existing *dst* JSON file.

        Top-level keys from *new_settings* are added only if missing in *dst*.
        For dict-valued keys, sub-keys are merged the same way.

        If *dst* cannot be parsed (e.g. JSONC with comments), the merge
        is skipped to avoid overwriting user settings.
        """
        try:
            existing = json.loads(dst.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Cannot parse existing file (likely JSONC with comments).
            # Skip merge to preserve the user's settings, but show
            # what they should add manually.
            import logging
            logging.getLogger(__name__).warning(
                "Could not parse %s (may contain JSONC comments). "
                "Skipping settings merge to preserve existing file.\n"
                "Please add the following settings manually:\n%s",
                dst, json.dumps(new_settings, indent=4),
            )
            return

        if not isinstance(existing, dict) or not isinstance(new_settings, dict):
            import logging
            logging.getLogger(__name__).warning(
                "Skipping settings merge: %s or template is not a JSON object.", dst
            )
            return

        changed = False
        for key, value in new_settings.items():
            if key not in existing:
                existing[key] = value
                changed = True
            elif isinstance(existing[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in existing[key]:
                        existing[key][sub_key] = sub_value
                        changed = True

        if not changed:
            return

        dst.write_text(
            json.dumps(existing, indent=4) + "\n", encoding="utf-8"
        )
