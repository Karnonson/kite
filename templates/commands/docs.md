---
description: Implement tasks tagged [docs] from tasks.md, updating README and docs/ without changing product code before QA.
handoffs:
  - label: Run QA
    agent: kite.qa
    prompt: Documentation is updated. Run QA and produce the final report.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is optional guidance for documentation work (for example, "only update setup docs" or "skip deployment notes"). Your job is to implement unchecked tasks tagged `[docs]` in `tasks.md`.

## Outline

This command runs after `kite.frontend` and before `kite.qa` in the approved implementation pipeline.

### Hard rules for this command

1. **Only `[docs]` tasks.** Filter `tasks.md` to unchecked tasks tagged `[docs]`. Do not implement `[backend]`, `[frontend]`, `[qa]`, or `[ops]` tasks.
2. **No production code.** MUST NOT edit application source, tests, build config, contracts, or generated planning artifacts except `tasks.md` status updates.
3. **Docs ownership boundaries.**
   - `README.md`: project overview, setup, common commands, and user-facing quickstart.
   - `docs/`: durable guides, architecture notes, deployment, operations, and troubleshooting.
   - `specs/<feature>/`: feature-planning artifacts only; do not use specs as user documentation.
4. **Approved layout only.** Read `plan.md` and use its `## Approved Source Layout` and documentation locations. STOP IF a docs task asks for a new root docs path not approved by the plan.
5. **Feature branch guardrail.** If this is a git repository and the current branch is `main` or `master`, STOP before editing. Create/switch to a feature branch if safe; otherwise report the exact branch issue.
6. **Validation required.** Verify changed docs by checking links, commands, referenced paths, and examples against the current project. Do not invent commands or capabilities.
7. **No repeated approval after tasks gate.** If this command is running after the approved `tasks.md` gate, proceed without asking for another approval unless blocked or unsafe. If run directly without prior task approval, ask once before editing.

### Step 1 — Read existing artifacts

Required:

- `FEATURE_DIR/spec.md`
- `FEATURE_DIR/plan.md`
- `FEATURE_DIR/tasks.md`

Optional but useful:

- `FEATURE_DIR/design.md` — user-visible screen names and flows.
- `FEATURE_DIR/contract.md` — public API or integration behavior.
- `FEATURE_DIR/quickstart.md` — commands and demo flow to reflect in docs.
- `README.md` and `docs/` — existing documentation conventions.
- `.kite/state.yml` — confirm previous stage was `frontend`.

If `tasks.md` is missing, abort and tell the user to run `kite.tasks` first.

### Step 2 — Filter documentation tasks

1. Parse `tasks.md`.
2. Build a list of unchecked tasks tagged `[docs]`, preserving phase order.
3. If `$ARGUMENTS` contains a filter, narrow by case-insensitive substring match.
4. If no `[docs]` tasks exist, print "No documentation tasks were generated for this loop" and update `.kite/state.yml` to `docs` without editing docs files.
5. If run directly without prior task approval, ask: "Implement these <N> docs task(s)? [yes]". Otherwise proceed unless blocked.

### Step 3 — Implement documentation tasks

For each `[docs]` task:

1. State the task title and the docs file(s) you plan to touch.
2. Confirm each target path belongs to README.md, docs/, or an approved docs path from `plan.md`.
3. Update only the documentation needed for the task.
4. Keep instructions plain and testable: include exact commands, expected outcomes, and links to durable guides when useful.
5. Keep user-facing accessibility behavior documented when the feature exposes UI: keyboard access, visible focus, readable contrast, clear labels, clear error messages, and non-color-only signaling.
6. Mark the task `[x]` in `tasks.md` and append a one-line summary.

If a docs task requires facts that are not present in the spec, plan, contract, quickstart, or existing docs, ask one question or mark the task blocked. Do not invent.

### Step 4 — Validate documentation

Before finishing:

1. Re-read every changed docs file.
2. Check internal links and referenced paths.
3. Check setup/test commands against `quickstart.md`, package scripts, or project files when available.
4. Confirm README/docs/specs separation is preserved.
5. If validation fails because of your docs change, fix it before marking the task complete. If validation cannot run, note the blocker in `tasks.md`.

### Step 5 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: docs
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     tasks: specs/<latest>/tasks.md
   ```
2. Print a concise summary:
   - Number of `[docs]` tasks completed and blocked.
   - Files changed.
   - Commands/links verified.
   - Any docs facts intentionally left out because source material was missing.
   - Next step: `kite.qa`.

### Step 6 — Handoff

Recommend running `kite.qa` next. The orchestrator (`kite.start`) handles automated progression after the approved task-list gate.

---

**Reminder:** This command edits documentation and `tasks.md` status only. It never edits product code, tests, contracts, or planning content other than task checkboxes/summaries.
