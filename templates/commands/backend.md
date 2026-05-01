---
description: Implement tasks tagged [backend] from tasks.md and write a Frontend contract before any UI work begins.
handoffs:
  - label: Build the Frontend
    agent: kite.frontend
    prompt: The backend is in place and the contract is published. Build the UI.
    send: true
  - label: Run QA
    agent: kite.qa
    prompt: The backend changes are ready for testing.
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
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
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
8. **Feature branch guardrail.** If this is a git repository and the current branch is `main` or `master`, STOP before editing code. Create/switch to a feature branch if safe; otherwise report the exact branch issue.
9. **Approved layout only.** Read plan.md's `## Approved Source Layout`. MUST NOT create or edit files outside the approved backend/shared/test paths unless the plan explicitly allows them.
10. **Validation required.** Run relevant backend tests, lint, typecheck, framework-native validation, or exact verification tasks from `tasks.md` after code changes. Fix failures you caused before marking tasks complete.

### Step 1 — Read existing artifacts

Required:
- `FEATURE_DIR/discovery.md` (`kite.discover`)
- `FEATURE_DIR/spec.md` (`kite.specify`)
- `FEATURE_DIR/plan.md` (`kite.plan`)
- `FEATURE_DIR/tasks.md` (`kite.tasks`)

Optional:
- `FEATURE_DIR/design.md` — used only to understand which screens consume which data.
- `kite.config.yml` — read `persona`, `stack`, `default_integration`.
- `.kite/state.yml` — confirm previous stage was `tasks`.

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

    After you have a candidate stack, invoke the `kite.research` subagent before you scaffold dependencies or pin versions. It must verify the current official version guidance for the chosen framework and any AI SDK or agent framework that appears in scope.

### Step 3 — Filter tasks

1. Parse `tasks.md`.
2. Build a list of unchecked tasks where the tag is `[backend]`, preserving phase order.
3. If `$ARGUMENTS` contains a filter (e.g. "only auth"), narrow the list — do a case-insensitive substring match against task titles.
4. Print the filtered list. If this command is running after the approved `tasks.md` implementation gate, do not ask for another approval; proceed unless blocked or unsafe. If run directly without prior task approval, ask once: "Implement these <N> task(s)? [yes]".

### Step 4 — Draft the contract

Write `specs/<latest>/contract.md` (overwrite if it exists, but preserve any custom sections under `## 9. Notes`). Use this structure:

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

```
### <PLAIN NAME — e.g. "List training plans">

- **Plain English:** ...one line...
- **Method + path:** `GET /api/plans`
- **Query / body:** ...or "none"
- **Returns (200):**
  ```json
  { "items": [{ "id": "string", "title": "string" }] }
  ```
- **Errors:** `401` if not signed in, `403` if not allowed, `404` if missing.
```

> Cover **every** endpoint the frontend will hit. If you skip one, the Frontend agent will refuse to run.

## 3. Shared data shapes

Reusable shapes referenced by multiple endpoints. Each has a plain-English description.

## 4. State changes / events

If the backend pushes events (websocket, SSE, polling), describe channels and message shapes here. If none, write "None — pure request/response."

## 5. Error contract

The shape of error responses across all endpoints (single source of truth).

## 6. Auth flows

Sign-in, sign-out, refresh, password reset — only the ones in scope.

## 7. Non-goals

Things the backend will **not** do in this iteration (the frontend should not assume them).

## 8. Versioning

How we will signal breaking changes. Default: "Breaking changes bump the path prefix to `/api/v2/...`."

## 9. Notes
```

### Step 5 — Implement the tasks

For each filtered `[backend]` task:

1. State the task title and the files you plan to touch.
   - Confirm each file is within the Approved Source Layout before editing.
2. Make the change.
3. If the change adds, removes, or alters an endpoint, **immediately update** the relevant section in `contract.md`.
4. If the task is a backend verification task, run the exact terminal command or framework dev-environment flow written in `tasks.md` before marking it done. For frameworks that ship an integrated developer environment or studio, use it when the task tells you to.
5. For any backend code change, run the relevant validation command(s) from `tasks.md`, the backend framework, or the existing test suite. If validation fails because of your change, fix it before continuing. If validation cannot run, mark the task blocked and explain why.
6. Update `tasks.md`: change `[ ]` to `[x]` for the completed task. Do not edit other tasks.
7. After every 3 tasks, print a one-line progress summary.

If a task is ambiguous, ask **one** clarifying question before coding. If it is genuinely blocked (e.g. requires frontend work), mark it `[~]` (in-progress) in `tasks.md` and add a one-line note explaining the blocker.

### Step 6 — Verify the contract is complete

Before finishing:

1. Re-read every `[backend]` task you completed.
2. For every endpoint, request shape, or response shape touched, confirm `contract.md` describes it.
3. If a section is missing, add it. The contract is the gate Frontend agent reads — incomplete contract = frontend cannot proceed.

### Step 7 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: backend
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     contract: specs/<latest>/contract.md
     tasks: specs/<latest>/tasks.md
   ```
2. Print a **5-bullet** summary:
   - Stack used
   - Number of `[backend]` tasks completed (and any blocked)
   - Number of endpoints in the contract
   - Anything the frontend MUST know that is non-obvious
   - Whether the contract is **complete** or has TODOs (must be complete to unblock frontend)
3. State the next step: "Backend is ready for the contract gate and then `kite.frontend`." Do not ask for another approval when the task-list gate has already been approved.

### Step 8 — Handoff

If the user approves and the contract is complete, recommend running `kite.frontend`. The orchestrator gate (`kite.start`) refuses to advance if `contract.md` is missing or marked incomplete.

---

**Reminder:** This command edits backend code and writes `contract.md`. It never edits frontend code, never writes UI, never invents endpoints the spec did not call for.
