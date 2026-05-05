---
description: Implement and run tasks tagged [qa] from tasks.md. Verifies backend has integration tests, frontend has at least smoke tests, and appends a plain-English report.
handoffs:
  - label: Ready for review
    agent: kite.start
    prompt: QA passed. Show me the final summary.
  - label: Fix a failure
    agent: kite.backend
    prompt: A backend test is failing — please fix it.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is optional guidance for QA (e.g. "skip slow tests" or a task filter like "only the auth tests"). Your job is to (1) implement any pending `[qa]` tasks in `tasks.md`, (2) run the test suite, and (3) append a plain-English report to `tasks.md`.

## Pre-Execution Checks

**Check for extension hooks (before qa)**:
- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_qa` key.
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

This command runs **after** `kite.docs` (or after `kite.frontend`/`kite.backend` if no docs or frontend work is in scope). It is the final implementation gate before the project is considered "done for this loop".

### Hard rules for this command

1. **Only `[qa]` tasks for implementation work.** Filter `tasks.md` to tasks tagged `[qa]` for new test authoring. Running existing tests is always allowed.
2. **Coverage minimums.**
   - Backend: every endpoint in `contract.md` Section 2 has at least one **integration test** (request in → response out, with a real or fake datastore — not a unit test of the handler).
    - Frontend: every page in `design.md` Section 2.1 has at least one **smoke test** (renders without crashing, primary action is reachable).
    - Accessibility: user-visible flows verify keyboard access, visible focus, readable contrast, clear labels, clear error messages, and non-color-only signaling.
    - Docs: if `[docs]` tasks or docs files changed, verify relevant links, setup commands, and user-facing instructions.
   - If a coverage minimum is not met, mark a follow-up `[qa]` task in `tasks.md` and add it to today's report.
3. **Never modify production code.** Test fixtures and test-only helpers under `tests/` are allowed. If a failure clearly requires a code fix, **stop**, mark the task blocked, and recommend `kite.backend` or `kite.frontend`.
4. **Plain English report.** The report appended to `tasks.md` is for the founder to read. Keep it short, no stack traces, no file paths longer than the project root.
5. **Honest pass/fail.** Never tweak a test to make it pass. If a test is genuinely wrong, mark it `[~]` (in-progress) and explain why in the report.
6. **Feature branch guardrail.** If this is a git repository and the current branch is `main` or `master`, STOP before writing test files or reports. Create/switch to a feature branch if safe; otherwise report the exact branch issue.

### Step 1 — Read existing artifacts

Required:
- `specs/<latest>/spec.md`
- `specs/<latest>/plan.md`
- `specs/<latest>/tasks.md`

Optional but used:
- `specs/<latest>/contract.md` — for backend coverage check.
- `specs/<latest>/design.md` — for frontend coverage check.
- `README.md` and `docs/` — for docs verification when docs changed.
- `kite.config.yml` — read `persona`, `stack`.
- `.kite/state.yml` — confirm previous stage was `backend` or `frontend`.

If `tasks.md` is missing, abort and tell the user to run `kite.tasks` first.

### Step 2 — Detect the test runner

From `kite.config.yml` `stack` and the project layout, pick the runner:

| Backend stack | Default runner |
|---|---|
| Python / FastAPI | `pytest` |
| Node / Express | `vitest` (or `jest` if `jest.config.*` exists) |
| Go / chi | `go test ./...` |

| Frontend stack | Default runner |
|---|---|
| React / Vite | `vitest` |
| SvelteKit | `vitest` |
| Next.js | `vitest` (or `jest` if configured) |
| Plain HTML | `playwright` if installed, else "smoke tests skipped — no runner" |

If the runner cannot be determined automatically, ask **one** question with a default. Tests/verification are required for code changes; if a runner is unavailable, record the blocker and add a follow-up `[qa]` task instead of treating testing as optional.

### Step 3 — Filter and implement `[qa]` tasks

1. Parse `tasks.md` and list unchecked `[qa]` tasks.
2. If `$ARGUMENTS` includes a filter, narrow by case-insensitive substring match.
3. For each task, write the test file:
   - Backend tests live under `tests/` (or the framework's idiomatic location).
   - Frontend tests live alongside the component (`*.test.tsx`) or under `tests/frontend/` — match what already exists.
   - Each test file starts with a `## What this tests` plain-English comment block (or its language-equivalent docstring).
4. Mark tasks `[x]` as you complete them.

### Step 4 — Coverage sweep

Before running anything, do a static check:

1. **Backend:** for every endpoint in `contract.md` Section 2, search the test files for a test that hits that path. If missing, append a new task to `tasks.md`:
   ```
   - [ ] [qa] Add integration test for <METHOD> <path>
   ```
2. **Frontend:** for every page in `design.md` Section 2.1, search test files for a smoke test referencing that page or its primary component. If missing, append:
   ```
   - [ ] [qa] Add smoke test for <Page name>
   ```
3. List any newly appended tasks to the user and ask: "Add these to today's QA run? [yes]"

### Step 5 — Run the suite

Run the chosen runner(s). Capture:

- Total tests run
- Passed / failed / skipped counts
- For each failure: test name, one-line plain-English description of what failed, and the file the failure points at (relative path only).

If any runner is missing from the environment, do **not** install it. Log "runner missing — skipped" and add a follow-up `[qa]` task.

### Step 6 — Append the report to `tasks.md`

Append a section at the end of `specs/<latest>/tasks.md` (do not overwrite — append, dated):

```markdown
---

## QA Report — <ISO-8601 date>

### What this means in plain English

> One paragraph (≤ 60 words). Did the build work? What still needs attention?

### Backend

- Tests run: <N> (passed: <P>, failed: <F>, skipped: <S>)
- Endpoint coverage: <covered>/<total> endpoints have an integration test
- Failures:
  - **<test name>** — <plain English what failed>

### Frontend

- Tests run: <N> (passed: <P>, failed: <F>, skipped: <S>)
- Page coverage: <covered>/<total> pages have a smoke test
- Failures:
  - **<test name>** — <plain English what failed>

### Follow-up tasks added

- [ ] [qa] ...

### Recommendation

- ✅ All green — ready to ship this loop.
- ⚠️ <N> failures — fix before shipping (see follow-up tasks).
- 🛑 Blocked — <reason>.
```

### Step 7 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: qa
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     qa_report: specs/<latest>/tasks.md
   ```
2. Print a **5-bullet** summary:
   - Total tests run
   - Pass count / fail count
   - Backend endpoint coverage (covered / total)
   - Frontend page coverage (covered / total)
   - Recommendation (one of: ready to ship / fix N items / blocked)
3. State the result and suggest the next manual command. Do not auto-send `kite.start`.

### Step 8 — Handoff

If everything is green, recommend running `kite.start` to plan the next loop. If there are failures, recommend the appropriate persona command (`kite.backend` or `kite.frontend`) to fix them.

---

**Reminder:** This command writes test files and appends a report to `tasks.md`. It never modifies production code, never silently installs runners, never tweaks tests to make them pass.
