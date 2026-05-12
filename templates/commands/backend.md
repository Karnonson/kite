---
description: Implement tasks tagged [backend] from tasks.md and write a Frontend contract before any UI work begins.
handoffs:
  - label: Build the Frontend
    agent: kite.frontend
    prompt: After the contract gate passes, build the UI from the published contract.
  - label: Run QA For Backend-Only Loop
    agent: kite.qa
    prompt: The backend-only changes are ready for testing. Use this only when no frontend or docs work are in scope.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is optional guidance for the backend phase (e.g. "use Postgres, no ORM" or a task filter like "only the auth tasks"). Your job is to (1) implement the tasks tagged `[backend]` in `tasks.md`, and (2) publish a `contract.md` describing every interface the frontend will consume.

## Pre-Execution Checks

**Check for extension hooks (before backend)**:

- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_backend` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable.
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```

- If no hooks are registered or `.kite/extensions.yml` does not exist, skip silently.

## Outline

This command runs **after** `kite.tasks`. It is the first **implementation** step in the SDLC. The Frontend agent depends on the contract this command writes.

### Hard rules for this command

1. **Only `[backend]` tasks.** Filter `tasks.md` to tasks tagged `[backend]`. Do not implement `[frontend]` or `[qa]` tasks. If a task has no tag, skip it and warn.
2. **Contract first, code second.** Before writing or modifying production code, draft `contract.md` from the spec and the tasks. Iterate on it as code lands, but never finish the command without a complete contract.
3. **No frontend code.** Never edit anything under a frontend folder (e.g. `web/`, `frontend/`, `app/`, `src/components/`). If a task seems to require it, mark the task blocked and stop.
4. **Stack picks once.** If the stack is not yet decided, ask **one** consolidated question with a sensible default in square brackets, then write the choice into `kite.config.yml`.
5. **Plain English summaries.** Every section in `contract.md` includes a one-line plain-English description above the formal definition.
6. **Refuse silent failures.** If a task references a file that does not exist, ask the user before creating it.
7. **Respect tracer-bullet phase gates.** Work through `[backend]` tasks in phase order. When you reach a backend verification task, run it before touching any later-phase backend task. If it fails, stop and report instead of skipping ahead.
8. **Use subagent-first execution before widening your own context.** Delegate bounded official-doc lookups, contract review, and codebase exploration to focused Kite subagents (for example `kite.research`) when installed, and run independent subagent tasks in parallel when the host supports it. The backend agent remains the only writer of backend code and `contract.md`. Browser validation is frontend-owned: never invoke `kite.browser` here, and consume `browser-report.md` only as evidence.
9. **Comments explain why, not what.** Add code comments only when they clarify rationale, invariants, tradeoffs, protocol constraints, or framework workarounds that are not obvious from the code itself.
10. **Use verified framework guidance.** Reuse `research.md` when available and invoke `kite.research` when it is installed before guessing framework-specific or AI-agent implementation patterns. If it is not installed, stop and add a blocking research task instead of guessing.
11. **Honor host-environment safety.** Before global package installs, system package commands, Docker commands, or writes outside the approved workspace, run the appropriate guard utility (`.kite/scripts/bash/check-dev-environment.sh` or `.kite/scripts/powershell/check-dev-environment.ps1`). If it blocks the action, stop and report instead of bypassing it. Approved environments set `KITE_DEV_ENV=1`.

### Step 1 — Read existing artifacts

Run `{SCRIPT}` from the repo root and parse `FEATURE_DIR`. Use that active feature directory for every feature artifact path. Use the latest directory under `specs/` only as a fallback when no active feature context exists.

Required:

- `FEATURE_DIR/discovery.md` (`kite.discover`)
- `FEATURE_DIR/spec.md` (`kite.specify`)
- `FEATURE_DIR/plan.md` (`kite.plan`)
- `FEATURE_DIR/tasks.md` (`kite.tasks`)

Optional:

- `FEATURE_DIR/design.md` — used only to understand which screens consume which data.
- `FEATURE_DIR/design-system.md` — optional reference for shared UI terminology only; never use it to invent frontend behavior.
- `FEATURE_DIR/research.md` — preferred source for verified framework, hosting, and AI-agent guidance.
- `kite.config.yml` — read `persona`, `stack`, `default_integration`.
- `.kite/state.yml` — confirm previous stage was `tasks`.

For a **brownfield** or otherwise **existing** project, inspect the implemented backend, current contract, and existing feature behavior **before asking** new questions. **Ask only** about missing evidence, contradictions, or blockers.

If any required artifact is missing, abort and tell the user which command produces it.

### Step 2 — Confirm or pick the stack

Read `kite.config.yml`:

- If `stack` is set, **reuse it without asking**. Print "Using stack: <stack>".
- If `stack` is null, ask **one** consolidated question:
  > "Pick a backend stack. Defaults are sensible — answer with a number or paste your own:
  > 1. Python + FastAPI + SQLite/Postgres  [default]
  > 2. Node + Express + Postgres
  > 3. Go + chi + Postgres
  > 4. Other (tell me)"

  Map the answer, then update `kite.config.yml`:

  ```yaml
  stack:
    backend:
      language: <python|node|go|other>
      framework: <fastapi|express|chi|...>
      datastore: <sqlite|postgres|...>
  ```

    After you have a candidate stack, invoke the `kite.research` subagent when it is installed before you scaffold dependencies or pin versions. It must verify the current official version guidance for the chosen framework and any AI SDK or agent framework that appears in scope. If it is not installed, add a blocking research task instead of guessing. Never use `latest` or floating dependency versions.

### Step 3 — Filter tasks

1. Parse `tasks.md`.
2. Build a list of unchecked tasks where the tag is `[backend]`, preserving phase order.
3. If `$ARGUMENTS` contains a filter (e.g. "only auth"), narrow the list — do a case-insensitive substring match against task titles.
4. Print the filtered list to the user and ask: "Implement these <N> task(s)? [yes]". Wait for approval unless `auto_approve` is true.

### Step 4 — Draft the contract

Write `FEATURE_DIR/contract.md` (overwrite if it exists, but preserve any custom sections under `## 11. Notes`). Use this structure:

```markdown
# Frontend Contract

**Stage:** backend
**Generated by:** kite.backend
**Date:** <ISO-8601 date>

## What this means in plain English

> One paragraph (≤ 60 words). Tell a non-technical reader: which screens get their data from where, and what shape that data has.

## 1. Base URL & auth

- **Base URL:** <e.g. http://localhost:8000>
- **Auth:** <e.g. "session cookie", "Bearer token in Authorization header", "none">

## 2. Endpoints

For each endpoint:

```text
### <PLAIN NAME — e.g. "List training plans">

- **Plain English:** ...one line...
- **Method + path:** `GET /api/plans`
- **Query / body:** ...or "none"
- **Returns (200):** `{ "items": [{ "id": "string", "title": "string" }] }`
- **Errors:** `401` if not signed in, `403` if not allowed, `404` if missing.
```

> Cover **every** endpoint the frontend will hit. If you skip one, the Frontend agent will refuse to run.

## 3. Shared data shapes

Reusable shapes referenced by multiple endpoints. Each has a plain-English description.

## 4. State changes / events

If the backend pushes events (websocket, SSE, polling), describe channels and message shapes here. If none, write "None — pure request/response."

## 5. Error contract

The shape of error responses across all endpoints (single source of truth).

## 6. Frontend usage map

List each frontend screen, component, or client module that consumes the contract and the endpoint(s) it uses. If no frontend consumes a backend path, say so explicitly.

## 7. Local verification commands

Commands the frontend and QA agents can run locally to verify the backend contract, including the backend server command and at least one endpoint check.

## 8. Auth flows

Sign-in, sign-out, refresh, password reset — only the ones in scope.

## 9. Non-goals

Things the backend will **not** do in this iteration (the frontend should not assume them).

## 10. Versioning

How we will signal breaking changes. Default: "Breaking changes bump the path prefix to `/api/v2/...`."

## 11. Notes

```text
```

### Step 5 — Implement the tasks

For each filtered `[backend]` task:

1. State the task title and the files you plan to touch.
2. Make the change. If you add a code comment, keep it short and explain why the code is shaped this way rather than narrating the next lines.
3. If the change adds, removes, or alters an endpoint, **immediately update** the relevant section in `contract.md`.
4. If the task is a backend verification task, run the exact terminal command or framework dev-environment flow written in `tasks.md` before marking it done. For frameworks that ship an integrated developer environment or studio, use it when the task tells you to. If your change causes a validation or verification failure and the fix is still inside backend scope, fix it before continuing.
5. Update `tasks.md`: change `[ ]` to `[x]` for the completed task. Do not edit other tasks.
6. After every 3 tasks, print a one-line progress summary.

If a task is ambiguous, ask **one** clarifying question before coding. If it is genuinely blocked (e.g. requires frontend work), mark it `[~]` (in-progress) in `tasks.md` and add a one-line note explaining the blocker.

### Step 6 — Verify the contract is complete

Before finishing:

1. Re-read every `[backend]` task you completed.
2. For every endpoint, request shape, or response shape touched, confirm `contract.md` describes it.
3. If a section is missing, add it. At minimum, `contract.md` must include Base URL/auth, endpoint entries with Method + path, an Error contract, a Frontend usage map, and Local verification commands. The contract is the gate Frontend agent reads — incomplete contract = frontend cannot proceed.

### Step 7 — Update state and present a summary

1. Update `.kite/state.yml`:

   ```yaml
   stage: backend
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     contract: FEATURE_DIR/contract.md
     tasks: FEATURE_DIR/tasks.md
   ```

2. Print a **5-bullet** summary:
   - Stack used
   - Number of `[backend]` tasks completed (and any blocked)
   - Number of endpoints in the contract
   - Anything the frontend MUST know that is non-obvious
   - Whether the contract is **complete** or has TODOs (must be complete to unblock frontend)
3. Ask: "Move on to the frontend? Approve to continue with `kite.frontend`, or tell me what to change in the backend or contract."

### Step 8 — Handoff

If the user approves and the contract is complete, recommend running `kite.frontend`. The orchestrator gate (`kite.start`) refuses to advance if `contract.md` is missing or marked incomplete.

---

**Reminder:** This command edits backend code and writes `contract.md`. It never edits frontend code, never writes UI, never invents endpoints the spec did not call for.
