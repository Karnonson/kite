# Feature Specification: Kite — End-to-End SDLC Workflow on Spec Kit

**Status:** Draft
**Owner:** karnon
**Source repo:** hard fork of `github/spec-kit` (this checkout)
**Target users:** Non-technical founders / PMs (primary), junior engineers (secondary)

---

## 1. Problem Statement

Spec Kit's `speckit` workflow ships a 4-step loop: **specify → plan → tasks → implement** (see [workflows/speckit/workflow.yml](workflows/speckit/workflow.yml)). It is excellent for engineers who already know what they want to build, but it has gaps for the user persona we are targeting:

1. **No structured ideation/discovery stage.** Users land on `/speckit.specify` already needing a coherent feature description.
2. **No design stage.** Spec Kit jumps from spec → plan → code. There is no artifact that captures design system, layout, or interaction decisions before frontend code is written.
3. **One generic `/speckit.implement` command.** Backend and frontend concerns are mashed into a single agent invocation, which produces uneven results when the stack spans both.
4. **Workflow assumes a technical author.** Prompts use jargon (e.g., "constitution", "non-functional requirements") and expect engineering vocabulary.

We will hard-fork Spec Kit into **Kite**: a guided, plain-language SDLC workflow that adds Discovery, Designer, Frontend, and Backend specialist agents and packages them behind a single orchestrator command suitable for non-technical users.

## 2. Goals (MVP)

| # | Goal | Measurable outcome |
|---|---|---|
| G1 | Cover the SDLC stages **Discovery → Spec → Design → Plan → Tasks → Backend impl → Frontend impl → QA** | A non-technical user running `/kite.start "<idea>"` can reach a working, tested feature without manually invoking sub-commands. |
| G2 | Add four specialist personas: **Discovery, Designer, Backend, Frontend** | Each persona ships as a dedicated command/skill on Copilot, Claude Code, and Codex CLI. |
| G3 | Hybrid orchestration | A single `/kite.start` command (orchestrator) hands off to persona subagents at each stage, with explicit human review gates between stages. |
| G4 | Plain-language UX | All user-facing prompts pass a "explain it to a non-engineer" review; jargon is either removed or annotated. |
| G5 | Stack-agnostic | The Backend and Frontend agents always ask for stack preferences (or read them from a `kite.config.yml`) instead of assuming. |
| G6 | Hard rebrand to **Kite** | Package, CLI, command prefix (`kite.*`), context files, and integrations registry all use the new identifier. Distinct PyPI/npm names. No accidental `speckit.` leakage in user-visible surfaces. |

## 3. Non-Goals (MVP)

- Deployment automation (CI/CD pipelines, cloud provisioning).
- Production monitoring, logging, alerting, observability.
- Analytics / telemetry on workflow usage.
- Migrating *every* upstream integration. MVP targets Copilot, Claude, Codex; others tracked as fast-follow.
- Replacing Spec Kit's existing Constitution/Clarify/Analyze commands — we will keep them and re-skin where useful.

## 4. Target Personas

- **Primary — "Mara the founder":** non-technical, can describe a product in plain English, cannot read a Mermaid diagram, will give up if the tool asks for "acceptance criteria in Gherkin".
- **Secondary — "Jules the junior":** 0–2 yrs experience, comfortable reading code but wants guardrails and won't push back on AI suggestions.

UX rule: any prompt the user sees must be readable by Mara. Anything technical (e.g., test plans, schema, API contracts) is generated *for* the user but presented with a one-line plain-English summary.

## 5. User Journeys

### 5.1 Mara's happy path
1. Mara runs `/kite.start "I want a tool where coaches can publish weekly training plans and athletes can mark them done."`
2. **Discovery agent** asks 3–6 plain-English questions (audience, must-haves, vibe, success criteria, constraints) and writes `discovery.md`.
3. Review gate → Mara approves.
4. **Specify agent** (re-skinned `speckit.specify`) produces `spec.md` and shows a 5-bullet plain-English summary.
5. Review gate → Mara approves.
6. **Designer agent** asks about visual direction (mood, references, brand colors) and produces `design.md` containing both a design-system section (tokens, type, components) and a layout section (page list + wireframe-level structure).
7. Review gate → Mara approves.
8. **Plan agent** (re-skinned `speckit.plan`) produces `plan.md`. Asks Mara for stack preferences in plain language ("Do you want this to run in a browser? On a phone? Do you have a preferred language?").
9. Review gate → Mara approves.
10. **Tasks agent** (re-skinned `speckit.tasks`) produces `tasks.md` with the existing checkbox format, but tagged `[backend]`, `[frontend]`, `[qa]`.
11. **Backend agent** picks up `[backend]` tasks, implements them.
12. **Frontend agent** picks up `[frontend]` tasks, implements them, consuming the API contract written by the Backend agent into `plan.md`.
13. **QA agent** runs/validates tests for `[qa]` tasks.
14. Mara sees a final summary: what was built, how to run it locally, what was skipped.

### 5.2 Jules's path
Same as Mara, but Jules can drop into any stage with `/kite.<stage>` directly and skip review gates with `--auto`.

## 6. Functional Requirements

- **FR-1** `/kite.start <idea>` orchestrates the full chain with review gates between every stage.
- **FR-2** Each stage is *also* available as a standalone command: `/kite.discover`, `/kite.specify`, `/kite.design`, `/kite.plan`, `/kite.tasks`, `/kite.backend`, `/kite.frontend`, `/kite.qa`.
- **FR-3** `tasks.md` items must carry a persona tag in `[backend]` / `[frontend]` / `[qa]` so the implementation agents can filter.
- **FR-4** Backend agent must write a "Frontend contract" section into `plan.md` (or a sibling `contract.md`) before Frontend implementation begins.
- **FR-5** All review gates default to `interactive` for Mara persona and `auto-approve` when `--auto` is passed.
- **FR-6** A `kite.config.yml` at repo root captures: persona (founder/junior), default stack, default integration. Generated by Discovery on first run.
- **FR-7** Kite ships as integrations for Copilot, Claude Code, and Codex CLI on day one.
- **FR-8** Existing Spec Kit `constitution`, `clarify`, `analyze`, `checklist` commands remain available, prefixed `kite.` and reachable from review gates as escape hatches.

## 7. Non-Functional Requirements

- **NFR-1** Time-to-first-spec from a cold `/kite.start` ≤ 5 user turns.
- **NFR-2** Workflow must run identically on Linux, macOS, Windows (matches upstream — bash + powershell scripts).
- **NFR-3** No network calls beyond the underlying AI integration. Air-gap parity with Spec Kit retained.
- **NFR-4** All persona prompts ≤ 200 lines each (keeps context-window cost predictable).
- **NFR-5** Backwards-compatible artifact names where possible (`spec.md`, `plan.md`, `tasks.md`) so users can grep upstream docs.

## 8. Artifacts Produced

| Stage | Artifact | New / reused |
|---|---|---|
| Discovery | `discovery.md`, `kite.config.yml` | New |
| Specify | `spec.md` | Reused (lightly re-skinned) |
| Design | `design.md` (system + layout) | New |
| Plan | `plan.md` (+ `contract.md` if API exists) | Reused + extended |
| Tasks | `tasks.md` (with persona tags) | Reused + tagged |
| Backend impl | source code, tests | New persona prompt |
| Frontend impl | source code, tests | New persona prompt |
| QA | test reports, coverage summary | New persona prompt |

## 9. Open Questions

- **OQ-1** Do we keep `/speckit.*` aliases for one release to ease migration, or hard-cut to `/kite.*`? => hard cut with deprecation warnings on `/speckit.*` for one release.

- **OQ-2** Does Kite ship its own constitution template, or inherit Spec Kit's verbatim?
=> Inherit Spec Kit's constitution for MVP, but add a Kite-specific example in `docs/` and update the template's example section to be more generic (remove `speckit`-specific language). Longer-term, we could add a `kite.constitution` command that scaffolds a constitution tailored to the new workflow and personas.

- **OQ-3** Should the Designer agent emit a generated mockup (e.g., HTML preview) or stay text/markdown only for MVP?
=> Text-only for MVP to keep scope manageable and maintain air-gap parity. The design output will be a `design.md` containing both a design system section (tokens, type, components, colors) and a layout section (page list + wireframe-level structure). We can explore visual outputs in a future iteration once the core workflow is solid.

- **OQ-4** Does the orchestrator persist state across sessions (so Mara can `/kite.resume`)? Likely yes via a `.kite/state.yml` — confirm scope for MVP.
=> Yes, implement `kite resume` for MVP to read `.kite/state.yml` and return the user to the next pending step. This addresses OQ-4 and enhances the user experience by allowing them to pick up where they left off without confusion.

- **OQ-5** Pricing/licensing implications of forking Spec Kit's MIT codebase under a new brand — assumed fine, confirm.
=> MIT license allows forking and rebranding with proper attribution. We will include a clear attribution in the README and documentation, stating that Kite is a fork of GitHub Spec Kit, and link back to the original repository. We will also ensure that no trademarked names or logos are used without permission.

## 10. Acceptance Criteria

The MVP is "done" when:
- A fresh `kite init my-app --integration copilot` scaffolds a project with all eight `/kite.*` commands present.
- Running `/kite.start "build me a TODO app"` end-to-end produces `discovery.md`, `spec.md`, `design.md`, `plan.md`, `tasks.md`, working backend + frontend code, and passing tests — without the user invoking any other command.
- No string `speckit` appears in user-visible CLI output, command names, or generated artifact headers.
- All four new persona agents have an integration test under `tests/integrations/` and `tests/workflows/`.
