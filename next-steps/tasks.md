# Tasks: Kite MVP

> Companion to [next-steps/spec.md](next-steps/spec.md) and [next-steps/plan.md](next-steps/plan.md).
> Tags: `[backend]` = CLI/Python, `[frontend]` = command/prompt authoring, `[qa]` = tests, `[docs]` = docs, `[ops]` = repo plumbing.

---

## Phase 0 — Foundations

- [ ] T001 `[ops]` Confirm package names available on PyPI (`kite-cli`) and pick fallback if taken.
- [x] T002 `[ops]` Decide retention period for `speckit.*` aliases — **one release with stderr deprecation, then remove** (resolves spec OQ-1).
- [ ] T003 `[docs]` Add `next-steps/README.md` linking spec, plan, and tasks for newcomers.
- [ ] T004 `[ops]` Create `kite-mvp` working branch off `main`.

## Phase 1 — Rebrand (no behavior change)

- [ ] T101 `[backend]` Rename `src/specify_cli/` → `src/kite_cli/`; update all imports.
- [ ] T102 `[backend]` Update [pyproject.toml](pyproject.toml): `name`, `[project.scripts]` → `kite = "kite_cli:main"`, `force-include` paths to `kite_cli/core_pack/...`.
- [ ] T103 `[backend]` Replace literal `specify_cli` and `specify` references in source (CLI help, error strings) with `kite`.
- [ ] T104 `[backend]` Rename project marker directory `.specify/` → `.kite/` across [scripts/bash/](scripts/bash/) and [scripts/powershell/](scripts/powershell/).
- [ ] T105 `[backend]` Replace magic envelope tokens `__SPECKIT_COMMAND_*` → `__KITE_COMMAND_*` in [templates/commands/](templates/commands/).
- [ ] T106 `[frontend]` Rename command files in [templates/commands/](templates/commands/): `specify.md` stays as-is (plain name) but registry entries become `kite.specify` etc. Update frontmatter `description`, `handoffs.agent` strings.
- [ ] T107 `[backend]` Rename workflow id in [workflows/speckit/workflow.yml](workflows/speckit/workflow.yml) → move to `workflows/kite/workflow.yml`, update `workflow.id` and `requires.speckit_version` → `kite_version`.
- [ ] T108 `[backend]` Update integration registrar keys/labels in [src/specify_cli/integrations/](src/specify_cli/integrations/) (post-rename: `src/kite_cli/integrations/`) where they leak the old brand to users.
- [ ] T109 `[backend]` Add a temporary alias layer so `/speckit.*` commands resolve to `/kite.*` for one release (deprecation banner in stderr).
- [ ] T110 `[qa]` Update every test under [tests/](tests/) to import from `kite_cli` and invoke `kite`. Run full suite — must be green.
- [ ] T111 `[docs]` Sweep [README.md](README.md), [docs/](docs/), [AGENTS.md](AGENTS.md), [DEVELOPMENT.md](DEVELOPMENT.md) for `speckit`/`Specify CLI` strings; rewrite to `Kite`. Keep one short "Forked from GitHub Spec Kit" attribution paragraph.

## Phase 2 — New persona commands

- [ ] T201 `[frontend]` Author `templates/commands/discover.md` (Discovery agent) per plan §4.1. ≤6 plain-English questions; writes `discovery.md` and seeds `kite.config.yml`. Uses `$ARGUMENTS` for markdown integrations and `{{args}}` for TOML.
- [ ] T202 `[frontend]` Author `templates/commands/design.md` (Designer agent) per plan §4.2. Output schema: Design System table + Layout page list.
- [ ] T203 `[frontend]` Author `templates/commands/backend.md` (Backend agent). Filters `[backend]` tasks; mandatory `contract.md` write step.
- [ ] T204 `[frontend]` Author `templates/commands/frontend.md` (Frontend agent). Reads `design.md` + `contract.md`; refuses to run if either missing.
- [ ] T205 `[frontend]` Author `templates/commands/qa.md` (QA agent). Filters `[qa]` tasks; appends report to `tasks.md`.
- [ ] T206 `[frontend]` Update [templates/tasks-template.md](templates/tasks-template.md) so generated `tasks.md` carries `[backend|frontend|qa]` tags.
- [ ] T207 `[frontend]` Add a plain-language summary block requirement to `templates/commands/specify.md`, `plan.md`, `tasks.md` (Mara's NFR).
- [ ] T208 `[backend]` Register the 5 new commands in the integration pipeline so they ship with `kite init` for Copilot, Claude, Codex.
- [ ] T209 `[qa]` Snapshot test: a fresh `kite init demo --integration copilot` lists all 8 `/kite.*` commands in `.github/prompts/`.

## Phase 3 — Orchestrator workflow + gates

- [ ] T301 `[backend]` Create `workflows/kite/workflow.yml` with the step list from plan §5 (discover → gates → … → qa).
- [ ] T302 `[backend]` Implement `auto_approve` input handling so gates short-circuit when `true`.
- [ ] T303 `[backend]` Add a workflow-level `persona` input (`founder` | `junior`) and propagate it to each command via `input.args`.
- [ ] T304 `[backend]` Implement the **contract gate**: orchestrator fails fast if `contract.md` (or "Frontend contract" section in `plan.md`) is missing before frontend step.
- [ ] T305 `[frontend]` Author `templates/commands/start.md` — the `/kite.start` orchestrator entry command for hosts that don't natively run workflow YAML.
- [ ] T306 `[qa]` `tests/workflows/test_kite_workflow.py`: dry-run the YAML, assert step order and gate placement.
- [ ] T307 `[qa]` `tests/test_backend_contract_gate.py`: orchestrator aborts when contract missing.

## Phase 4 — UX polish for non-technical users

- [ ] T401 `[frontend]` Plain-language review pass on every persona prompt — no Gherkin, no "non-functional", no "epic". Linter or checklist enforced.
- [ ] T402 `[backend]` `kite init` defaults `persona: founder` if user does not pass `--persona`.
- [ ] T403 `[frontend]` Add a `## What this means in plain English` block at the top of generated `spec.md`, `plan.md`, `tasks.md`.
- [ ] T404 `[backend]` Implement `kite resume` — reads `.kite/state.yml`, returns to the next pending step (in-MVP per resolved OQ-4).
- [ ] T405 `[backend]` Add `kite doctor` plain-language diagnostic ("Your project is missing `design.md` — run `/kite.design`").

## Phase 5 — Day-one integrations

- [ ] T501 `[backend]` Verify [src/kite_cli/integrations/copilot/](src/specify_cli/integrations/copilot/) installs all 8 commands (default mode + `--skills` mode).
- [ ] T502 `[backend]` Verify [src/kite_cli/integrations/claude/](src/specify_cli/integrations/claude/) installs all 8 commands as skills.
- [ ] T503 `[backend]` Verify [src/kite_cli/integrations/codex/](src/specify_cli/integrations/codex/) installs all 8 commands as skills.
- [ ] T504 `[qa]` Add `tests/integrations/test_integration_copilot_kite.py`, `..._claude_kite.py`, `..._codex_kite.py`.
- [ ] T505 `[ops]` Mark all other integrations `experimental: true` in their config; document in [docs/reference/integrations.md](docs/reference/integrations.md).

## Phase 6 — Release

- [ ] T601 `[ops]` Update [CHANGELOG.md](CHANGELOG.md) with a "Forked → Kite 0.1.0" entry.
- [ ] T602 `[ops]` Bump version in [pyproject.toml](pyproject.toml) to `0.1.0`.
- [ ] T603 `[docs]` Replace [README.md](README.md) hero with Kite positioning ("SDLC for non-technical builders").
- [ ] T604 `[docs]` Write a short [docs/quickstart.md](docs/quickstart.md) for Mara: 5 commands, no jargon.
- [ ] T605 `[ops]` Cut `v0.1.0` tag.

---

## Out of MVP (tracked, not started)

- [ ] X01 Deployment automation persona (`/kite.deploy`).
- [ ] X02 Monitoring + logging persona (`/kite.observe`).
- [ ] X03 Mockup/HTML preview output for Designer agent (resolves spec OQ-3).
- [ ] X04 Telemetry on workflow usage.
- [ ] X05 Fast-follow integrations beyond Copilot/Claude/Codex.

---

## Acceptance gate (mirrors spec §10)

- [ ] A1 `kite init my-app --integration copilot` scaffolds all 8 `/kite.*` commands.
- [ ] A2 `/kite.start "build me a TODO app"` runs end-to-end without manual sub-command invocation.
- [ ] A3 No `speckit` string visible in user-facing CLI output or generated artifact headers.
- [ ] A4 Full test suite green on Linux, macOS, Windows.
