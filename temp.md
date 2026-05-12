# Kite Agent Workflow Refinements

## Goal

Strengthen Kite's multi-agent workflow so backend, frontend, browser testing, QA, and planning agents hand off through explicit evidence instead of assumptions.

## 1. API-first backend handoff

When a feature includes a backend, the backend should expose every frontend-consumed capability through an API or an equivalent external interface. For web apps, the default should be HTTP routes under an `/api/...` prefix unless the chosen framework recommends a different official pattern.

The backend agent must publish `FEATURE_DIR/contract.md` as the single source of truth for the frontend, using the active feature directory resolved by Kite scripts, `SPECIFY_FEATURE_DIRECTORY`, or `.kite/feature.json` before falling back to the latest `specs/` directory. The contract should include base URL, auth model, endpoints, request examples, response examples, shared data shapes, error responses, events or polling behavior, versioning, non-goals, and local run commands.

The frontend agent should consume only `contract.md`. It should not explore backend code to discover routes. If the UI needs an endpoint that is missing from the contract, the frontend agent should stop, mark the task blocked, and send the work back to the backend agent.

Existing Kite support already points in this direction: `kite.backend` writes `contract.md`, `kite.frontend` refuses incomplete contracts, and the workflow has a `contract-gate`. The implementation should harden those rules rather than replace them.

## 2. Dev-environment command guard

Kite should protect the user's host machine when agents run commands. If an agent is about to run a package install, global install, system package command, Docker/system service command, or write outside the project while it is not inside the approved dev environment, the command should be blocked, a terminal bell should sound, and the agent should report the blocked command to the user in plain English.

Important boundary: Kite can enforce this inside its own commands, generated agent instructions, and integrations that expose real pre-command hooks. It cannot universally intercept every terminal command from every third-party agent unless that agent runtime supports command hooks.

Recommended MVP:

- Add a dev-environment detector with explicit markers such as `KITE_DEV_ENV=1` plus devcontainer/container evidence.
- Add guard scripts for bash and PowerShell that produce a terminal bell with `printf '\a'` or the PowerShell equivalent and return a blocking exit code.
- Add rules to implementation agents requiring a guard check before package installs or host-affecting commands.
- Add provider-specific hook adapters later for integrations that support true pre-command interception.

## 3. Browser validation agent

Create a `kite.browser` agent/command that runs end-to-end browser checks after the backend and frontend are connected.

The browser agent should read `contract.md`, `design.md`, `design-system.md`, `quickstart.md`, and `tasks.md` from the active `FEATURE_DIR`. It should launch or reuse the app's dev server, exercise priority user flows, capture useful browser evidence when available, and write `FEATURE_DIR/browser-report.md`.

The browser agent should not edit product code. It reports frontend-scoped failures back to `kite.frontend`, backend or contract failures back to `kite.backend`, and environment/test-runner blockers back to the user.

The frontend agent should be able to use `kite.browser` as a subagent after each connected frontend slice: build, browser-check, fix frontend-scoped issues, then re-run the browser check until the slice is green or blocked.

## 4. Subagent-first development

Kite should prefer a subagent-first workflow when a specialized subagent can solve a focused part of the problem with less context than the parent agent would need to load itself. This should be the default for repository exploration, official-doc research, browser validation, contract review, and other bounded tasks where focused delegation reduces context growth and tool cost.

The parent agent should stay orchestration-focused: manage the conversation with the user, decide when to delegate, reconcile conflicts between subagent outputs, and remain the final writer of user-facing artifacts or production code in its scope.

Because this is a general workflow rule, it should live in the project constitution rather than only inside individual command prompts.

Guardrails:

- Use subagents first for focused read-heavy or validation-heavy work.
- Keep subagent outputs concise and task-specific so they shrink parent context instead of expanding it.
- Fall back to direct parent-agent work only when no suitable subagent exists or the parent must own the final write.

## 5. Parallel planning subagents

`kite.plan` should use parallel subagents when the selected integration supports them, but the parent planning agent must remain the only writer of final artifacts.

Safe parallel work:

- Official-doc research per selected framework or hosting target.
- Data model draft.
- API/interface contract draft.
- Quickstart and verification-flow draft.
- Risk and open-question review.

Unsafe parallel work:

- Multiple agents editing `plan.md`, `tasks.md`, or `contracts/` at the same time.
- Subagents making final architecture decisions without the parent agent reconciling conflicts.

The parent planning agent should launch read-only or draft-only subagents, wait for their findings, resolve conflicts, and then write the final plan artifacts itself.

## 6. Official-doc rule for AI-agent projects

When the user's project involves AI agents, workflows, tool calling, RAG, MCP, skills, or an AI SDK/agent framework, Kite's agents should use official framework documentation before producing architecture, tasks, or code.

The planning flow should ask the user to confirm the agent framework and budget/operations posture before planning. Kite should prefer established official frameworks over custom orchestration unless the user explicitly chooses a custom approach.

`kite.research` must verify official docs, current install/version guidance, MCP support, skill/template/starter-kit support, and framework-specific best practices. `kite.plan` and `kite.tasks` should translate those findings into framework-native architecture and tasks instead of treating the feature like ordinary CRUD software.

Backend and frontend implementation agents must consult the verified research or installed framework skills before writing code that touches the agent framework. If official guidance cannot be verified, the artifact should say `NEEDS RESEARCH` rather than guessing.

Because this is a durable project-level rule, it should also be written into the constitution.

## 7. Why-oriented code comments

Backend and frontend implementation agents should add comments sparingly and only when the code benefits from explaining rationale, constraints, tradeoffs, invariants, workarounds, or other non-obvious decisions.

Comments should explain why the code exists or why a specific approach was chosen, not narrate what the code is already doing line by line. If the code is self-explanatory, the agent should prefer no comment over a redundant one.

Because this is a general development rule, it should also be part of the constitution.

## Implementation Plan

See [team/agents/github-copilot/2026-05-06-kite-agent-workflow-improvements.md](team/agents/github-copilot/2026-05-06-kite-agent-workflow-improvements.md).
