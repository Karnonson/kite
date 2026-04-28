# Implementation Plan: Kite

> Companion to [next-steps/spec.md](next-steps/spec.md). Read the spec first.

## 1. Approach

We hard-fork Spec Kit in place. Rather than designing from scratch, we **re-use every extension point upstream already provides** and add four new persona commands plus one orchestrator workflow. This keeps the diff against upstream small enough to rebase later if we want to absorb upstream changes.

Three layers of change:

1. **Rebrand** — package, CLI binary, command prefix, integration registry keys, context-file names, docs.
2. **New persona commands** — `discover`, `design`, `backend`, `frontend`, `qa` added to [templates/commands/](templates/commands/).
3. **New orchestrator workflow** — `kite` workflow under [workflows/](workflows/) replacing the linear `speckit` chain with a hybrid orchestrator-with-handoffs that includes review gates at every stage.

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  /kite.start "<idea>"           (orchestrator command + workflow)│
└───────────┬──────────────────────────────────────────────────────┘
            │
   ┌────────▼────────┐  gate  ┌────────────┐  gate  ┌──────────────┐
   │ /kite.discover  ├───────▶│ /kite.specify ├────▶│ /kite.design │
   │  (Discovery)    │        │  (re-skin)   │      │  (Designer)  │
   └─────────────────┘        └────────────┘       └───────┬──────┘
                                                           │ gate
                                                  ┌────────▼────────┐
                                                  │ /kite.plan      │
                                                  │  (re-skin)      │
                                                  └────────┬────────┘
                                                           │ gate
                                                  ┌────────▼────────┐
                                                  │ /kite.tasks     │
                                                  │  (tagged)       │
                                                  └────────┬────────┘
                                                           │
                                  ┌────────────────────────┼─────────────────────┐
                                  │                        │                     │
                          ┌───────▼──────┐         ┌───────▼──────┐      ┌───────▼──────┐
                          │ /kite.backend │ writes │ /kite.frontend│      │ /kite.qa     │
                          │  (Backend)    │contract│  (Frontend)   │      │  (QA)        │
                          └──────────────┘ ──────▶ └──────────────┘      └──────────────┘
```

Each persona is **a command file** (Markdown/TOML/YAML depending on integration, per the host's [AGENTS.md](AGENTS.md) rules) — no new runtime, no new abstractions. The orchestrator is a **workflow YAML** (same shape as [workflows/speckit/workflow.yml](workflows/speckit/workflow.yml)).

## 3. Rebrand Plan (Spec Kit → Kite)

| Asset | Before | After |
|---|---|---|
| Python package | `specify_cli` | `kite_cli` |
| CLI binary | `specify` | `kite` |
| PyPI name | `specify-cli` | `kite-cli` (TBD — confirm availability) |
| Command prefix | `speckit.*` | `kite.*` |
| Workflow id | `speckit` | `kite` |
| Default workflow file | [workflows/speckit/workflow.yml](workflows/speckit/workflow.yml) | `workflows/kite/workflow.yml` |
| Integration context files | `CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md` | unchanged (these are owned by the host agent) but their *content* references "Kite" |
| Project marker dir | `.specify/` | `.kite/` |
| Constitution template | `templates/constitution-template.md` | unchanged structurally; copy edited |
| Magic envelope token | `__SPECKIT_COMMAND_*` | `__KITE_COMMAND_*` |

We will keep `speckit.*` command aliases for **one release** behind a deprecation banner emitted to stderr on every invocation (resolves OQ-1: confirmed).

## 4. New Persona Commands

Each lives in `templates/commands/` and is processed by every integration via the existing pipeline (see [AGENTS.md](AGENTS.md)).

### 4.1 `/kite.discover` (Discovery agent)
- **Goal:** turn a one-line idea into a structured `discovery.md` and seed `kite.config.yml`.
- **Behavior:** asks ≤6 plain-English questions, one at a time, with sensible defaults. Writes `discovery.md` containing: audience, problem, must-haves, nice-to-haves, success criteria, constraints, vibe.
- **Handoff:** `kite.specify`.

### 4.2 `/kite.design` (Designer agent — system + layout)
- **Goal:** produce `design.md` with two top-level sections: **Design System** (color, type, spacing, components) and **Layout** (page list, per-page wireframe structure in plain text + ASCII boxes).
- **Inputs:** `discovery.md`, `spec.md`.
- **Behavior:** asks about brand mood/references, picks tokens, produces a component inventory.
- **Handoff:** `kite.plan`.

### 4.3 `/kite.backend` (Backend agent)
- **Goal:** implement tasks tagged `[backend]` from `tasks.md`.
- **Required output:** when an HTTP/RPC interface exists, append a **"Frontend contract"** section to `plan.md` (or write `contract.md`) describing endpoints, payloads, and error shapes — **before** Frontend agent runs. Enforced by the orchestrator gate.
- **Stack:** asks the user (Mara: plain language; Jules: stack flags).

### 4.4 `/kite.frontend` (Frontend agent)
- **Goal:** implement tasks tagged `[frontend]` from `tasks.md`, consuming `design.md` and the Backend contract.
- **Hard rule:** never invents an API endpoint. If `contract.md` is missing, asks Backend agent first (or fails the gate).

### 4.5 `/kite.qa` (QA agent)
- **Goal:** implement/run tests for `[qa]`-tagged tasks. Ensures backend has integration tests and frontend has at least smoke tests.
- **Output:** test report appended to `tasks.md`.

### 4.6 Re-skinned commands
`/kite.specify`, `/kite.plan`, `/kite.tasks`, `/kite.constitution`, `/kite.clarify`, `/kite.analyze`, `/kite.checklist`, `/kite.implement` — copies of the upstream files with prefix swapped, headings re-worded for plain language, and `tasks.md` template extended to support `[backend|frontend|qa]` tags.

## 5. Orchestrator Workflow

`workflows/kite/workflow.yml` mirrors the existing speckit workflow but adds the new stages and gates. Sketch:

```yaml
schema_version: "1.0"
workflow:
  id: "kite"
  name: "Kite Full SDLC"
  version: "0.1.0"

inputs:
  idea: { type: string, required: true, prompt: "What do you want to build?" }
  persona: { type: string, default: "founder", enum: ["founder", "junior"] }
  auto_approve: { type: bool, default: false }

steps:
  - { id: discover, command: kite.discover, input: { args: "{{ inputs.idea }}" } }
  - { id: gate-discover, type: gate, message: "Approve the discovery?", on_reject: abort }
  - { id: specify,  command: kite.specify }
  - { id: gate-specify, type: gate }
  - { id: design,   command: kite.design }
  - { id: gate-design, type: gate }
  - { id: plan,     command: kite.plan }
  - { id: gate-plan, type: gate }
  - { id: tasks,    command: kite.tasks }
  - { id: backend,  command: kite.backend }
  - { id: gate-contract, type: gate, message: "Backend contract ready?" }
  - { id: frontend, command: kite.frontend }
  - { id: qa,       command: kite.qa }
```

Gates default to interactive; `auto_approve: true` skips them (Jules's path).

## 6. Integration Strategy

Day-one integrations: **Copilot**, **Claude Code (skills)**, **Codex CLI (skills)**.

For each, follow the recipe in [AGENTS.md](AGENTS.md):
- Create `src/kite_cli/integrations/<key>/` (renamed from `specify_cli`).
- Update `_register_builtins()` for the three day-one targets first.
- The remaining ~20 upstream integrations stay registered but are marked `experimental` until each is smoke-tested.

## 7. Tests

- Port every test under [tests/](tests/) to use `kite_cli` imports + `kite` CLI invocations.
- New tests:
  - `tests/integrations/test_integration_copilot_kite.py` — verifies all 8 `/kite.*` commands install correctly.
  - `tests/workflows/test_kite_workflow.py` — orchestrator dry-run.
  - `tests/test_persona_tags.py` — `tasks.md` parser respects `[backend|frontend|qa]` tags.
  - `tests/test_backend_contract_gate.py` — Frontend agent fails fast if `contract.md` missing.

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Rebrand churn breaks downstream users | Ship one release with `speckit.*` aliases + deprecation banner. |
| Non-technical users still see jargon leaking from `spec.md` | Add a "plain-language summary" header to every artifact, generated by the persona that wrote it. |
| Backend/Frontend handoff produces inconsistent contracts | Make `contract.md` mandatory at the gate; QA agent verifies frontend never references undocumented endpoints. |
| Diverging from upstream Spec Kit makes future merges hard | Keep persona commands as *additive* files where possible; only rebrand strings live in upstream files. |
| Designer output too vague to drive Frontend agent | Require a fixed schema in `design.md` (tokens table + page structure list) — Frontend agent validates it. |

## 9. Phased Delivery

- **Phase 0 — Scaffolding (this folder):** spec.md, plan.md, tasks.md. ✅ what we are producing now.
- **Phase 1 — Rebrand only:** rename package/CLI/prefix, all tests green, no behavioral change.
- **Phase 2 — Persona commands:** add 5 new commands (discover, design, backend, frontend, qa).
- **Phase 3 — Orchestrator + gates:** new `kite` workflow YAML + gate UX.
- **Phase 4 — UX polish for Mara:** plain-language pass, summaries, default `--persona founder`.
- **Phase 5 — Fast-follow integrations:** beyond Copilot/Claude/Codex.
- **Out of MVP:** deploy, monitoring, logging — tracked separately.

## 10. Resolved Decisions

From clarifying interview:
- Hard fork, not preset/extension layer.
- Day-one integrations: Copilot, Claude, Codex.
- Orchestration model: hybrid (one orchestrator command + persona subagents).
- One Designer agent (system + layout merged).
- Stack-agnostic; ask the user.
- Primary persona: non-technical founder.

From open questions (now closed):
- **OQ-1 →** Hard cut to `/kite.*`; keep `/speckit.*` aliases for one release with stderr deprecation warning, then remove.
- **OQ-2 →** Inherit Spec Kit's constitution template for MVP; generic-ify the example section to drop `speckit`-specific language. A bespoke `kite.constitution` is post-MVP.
- **OQ-3 →** Designer is text/markdown only for MVP. Visual previews are post-MVP.
- **OQ-4 →** `kite resume` is in-MVP. State persists in `.kite/state.yml`.
- **OQ-5 →** MIT permits the fork; ship attribution ("Forked from GitHub Spec Kit") in [README.md](README.md) and docs; no upstream trademarks/logos.
