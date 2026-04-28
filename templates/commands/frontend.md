---
description: Implement tasks tagged [frontend] from tasks.md, consuming design.md and the backend contract. Refuses to run if either is missing.
handoffs:
  - label: Run QA
    agent: kite.qa
    prompt: The frontend is in place. Run the test suite and report.
    send: true
  - label: Refine the Design
    agent: kite.design
    prompt: I want to revise the design before continuing.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is optional guidance for the frontend phase (e.g. "use Tailwind, no animations" or a task filter like "only the dashboard"). Your job is to implement the tasks tagged `[frontend]` in `tasks.md`, consuming `design.md` and `contract.md` produced by previous stages.

## Pre-Execution Checks

**Check for extension hooks (before frontend)**:
- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_frontend` key.
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

This command runs **after** `kite.backend` has produced `contract.md`. It is the second implementation step in the SDLC.

### Hard rules for this command

1. **Refuse to run without inputs.** If `design.md` is missing, abort and say "Run `kite.design` first." If `contract.md` is missing or marked incomplete, abort and say "The backend contract is not ready. Run `kite.backend` first."
2. **Only `[frontend]` tasks.** Filter `tasks.md` to tasks tagged `[frontend]`. Do not touch backend code.
3. **Never invent an endpoint.** Every network call must reference an endpoint declared in `contract.md`. If a task needs an endpoint that does not exist, **stop**, mark the task blocked with the line "needs new endpoint", and tell the user to run `kite.backend` again.
4. **Match the design.** Colors, spacing, typography, and component inventory come from `design.md`. Do not freelance new tokens. If a screen needs a component not listed in the design's inventory, ask the user before adding it.
5. **No backend code.** Do not edit anything under `api/`, `server/`, `backend/`, or modify the database. If a task seems to require it, mark blocked.
6. **Plain English commit messages.** Every task you complete gets a one-line summary in the task list ("Built the sign-in screen — calls `POST /api/auth/login`.").

### Step 1 — Read existing artifacts

Required (abort with the indicated message if missing):
- `discovery.md` — "Run `kite.discover` first."
- `specs/<latest>/spec.md` — "Run `kite.specify` first."
- `specs/<latest>/design.md` — "Run `kite.design` first."
- `specs/<latest>/plan.md` — "Run `kite.plan` first."
- `specs/<latest>/tasks.md` — "Run `kite.tasks` first."
- `specs/<latest>/contract.md` — "The backend contract is not ready. Run `kite.backend` first."

Optional:
- `kite.config.yml` — read `persona`, `stack.frontend`.
- `.kite/state.yml` — confirm previous stage was `backend`.

### Step 2 — Validate the contract is complete

Open `contract.md` and check:
- Section 1 (Base URL & auth) is filled.
- Section 2 (Endpoints) has at least one endpoint **and** no `TODO` / `<...>` placeholder strings.
- Section 5 (Error contract) is filled.

If anything is missing or contains a placeholder, **abort** with:
> "The backend contract is incomplete (missing: <list>). Run `kite.backend` again before I can build the UI."

### Step 3 — Confirm or pick the frontend stack

Read `kite.config.yml`:
- If `stack.frontend` is set, **reuse it without asking**.
- If unset, ask **one** consolidated question:
  > "Pick a frontend stack. Defaults are sensible — answer with a number or paste your own:
  > 1. React + Vite + Tailwind  [default]
  > 2. SvelteKit + Tailwind
  > 3. Next.js (App Router) + Tailwind
  > 4. Plain HTML + CSS
  > 5. Other (tell me)"

  Map the answer, then update `kite.config.yml`:
  ```yaml
  stack:
    frontend:
      framework: <react|svelte|next|html|other>
      styling: <tailwind|css|other>
      bundler: <vite|next|none>
  ```

### Step 4 — Filter tasks

1. Parse `tasks.md`.
2. Build a list of unchecked tasks tagged `[frontend]`.
3. If `$ARGUMENTS` includes a filter, narrow by case-insensitive substring match.
4. For each task, check the contract: list which endpoints the task will consume. If a task implies an endpoint not in `contract.md`, mark it as **blocked: needs new endpoint** and exclude it from the implementation list.
5. Print the filtered list (with the per-task endpoint mapping) to the user and ask: "Implement these <N> task(s)? [yes]". Wait for approval unless `auto_approve` is true.

### Step 5 — Implement the tasks

For each `[frontend]` task:

1. State the task title and the files you plan to touch.
2. Pull the relevant page block from `design.md` Section 2.1 ("Page list") and the relevant endpoints from `contract.md` Section 2.
3. Build the screen / component:
   - Use the colors, spacing, and typography from `design.md` Section 1. **Do not introduce new tokens.**
   - Use only endpoints declared in `contract.md`. The base URL and auth model come from the contract — do not hard-code anything else.
   - Handle the errors listed in `contract.md` Section 5. At minimum: a generic error message and a sign-in redirect on `401`.
   - Add a `## What this screen does` plain-English comment block at the top of each new component file.
4. Update `tasks.md`: change `[ ]` to `[x]` for the completed task and append the one-line summary.
5. After every 3 tasks, print a one-line progress summary.

If you discover the design is unclear (e.g. a page in the spec has no entry in `design.md` Section 2.1), ask **one** consolidated question. If the user wants to revise the design, abort cleanly and recommend `kite.design`.

### Step 6 — Wire up the data layer

If this is the first frontend task in the project, create one shared module that:
- Reads the base URL from a single config entry (no scattered hard-codes).
- Wraps fetch / axios with the auth header described in the contract.
- Exposes one typed function per endpoint (or, for plain HTML, one fetch helper per endpoint).

All subsequent tasks use this module. If the module already exists, extend it — do not duplicate it.

### Step 7 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: frontend
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     tasks: specs/<latest>/tasks.md
   ```
2. Print a **5-bullet** summary:
   - Frontend stack used
   - Number of `[frontend]` tasks completed (and any blocked, with reason)
   - Number of screens built
   - Whether every screen ties back to a `design.md` page block
   - Whether every network call ties back to a `contract.md` endpoint
3. Ask: "Run QA next? Approve to continue with `kite.qa`, or tell me what to change in the UI."

### Step 8 — Handoff

If the user approves, recommend running `kite.qa`. Do not run it for them — the orchestrator (`kite.start`) handles that.

---

**Reminder:** This command edits frontend code only. It never edits backend code, never invents endpoints, never freelances design tokens.
