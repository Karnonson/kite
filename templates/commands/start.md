---
description: Run the founder-friendly Kite SDLC end-to-end (constitution → discover → specify → design → clarify → plan → tasks → analyze → task gate → backend → contract gate → frontend → docs → qa) with human planning gates and mandatory implementation gates.
handoffs:
  - label: Discovery only
    agent: kite.discover
    prompt: Just take me through the discovery step.
  - label: Resume in progress
    agent: kite.start
    prompt: Resume the in-progress Kite SDLC run.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is:

- A one-line product idea **or**
- A free-form preference list (e.g. "auto-approve gates, persona=junior, idea=…")
- Or empty — in which case ask the user for the idea.

This command is the **orchestrator entrypoint** for the Kite SDLC. It coordinates gates and resume points; it does not cause persona commands to run ahead of the approved stage.

## Pre-Execution Checks

**Check for extension hooks (before start)**:

- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_start` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions.
- For each executable hook, output the standard pre-hook block (see other Kite commands for the format) and either pause for the user to run it (optional hooks) or wait for it to run automatically (mandatory hooks).
- If no hooks are registered or `.kite/extensions.yml` does not exist, skip silently.

## Outline

This command is for hosts that do **not** natively run workflow YAML. If the host **does** run workflows, prefer `kite workflow run kite` over invoking this prompt.

### Hard rules for this command

1. **Never write code, design, or specs yourself.** Every artifact comes from the persona command that owns it. This command only **chains** persona commands and presents review gates.
2. **One stage at a time through planning.** Run one persona, then stop at the gate unless the stage is routine and explicitly auto-approved. Persona commands from constitution through plan MUST still ask one question at a time and MUST NOT write or advance when material decisions are missing.
3. **Resume-aware.** Always read `.kite/state.yml` first. If a previous run paused mid-flow, offer to resume from that step, not from the top.
4. **Brownfield-first.** If the repository already has application code, docs, config, tests, or specs, instruct every stage to inspect that evidence before asking feature or architecture questions. Existing implemented behavior is answered context; ask only about the desired change, missing evidence, or conflicts.
5. **Plain English.** Every gate prompt is one short plain-English question. Forbidden: *epic, story, Gherkin, schema, endpoint, payload, scope creep, non-functional, KPI, OKR, RFC, MVP*.
6. **Split implementation stages.** In the founder fast path, building happens through `kite.backend`, the hard contract gate, `kite.frontend`, `kite.docs`, then `kite.qa`. Do not use `kite.implement` for the default guided flow.
7. **Feature branch guardrail.** If this is a git repository and the current branch is `main` or `master`, stop before writing feature artifacts and tell the user to create or switch to a feature branch. If there is no git repository, continue without branch changes.
8. **No self-recursive auto-send.** NEVER invoke or hand off to `kite.start` automatically. It is acceptable to tell the user to run `kite.start` manually to resume.
9. **Subagent-first execution and browser ownership.** Each persona command MUST use subagent-first delegation before widening its own context. `kite.browser` is invoked only by `kite.frontend` after a connected frontend slice exists; QA and other stages consume `browser-report.md` instead of invoking browser tooling.

### Step 1 — Resolve inputs

1. Parse `$ARGUMENTS` for any of:
   - `idea=<one line>`
   - `persona=<founder|junior>` (default: `founder`)
   - `auto_approve=<true|false>` (default: `false`; never skips the task-list approval gate)
   - `integration=<copilot|claude|codex|...>` (default: read from `kite.config.yml` if present, else `copilot`)
   - Any free-form text not matching the above is treated as the idea.

2. If `idea` is still empty, ask:
   > "What do you want to build? One sentence is enough."

3. If `persona` is unset and `kite.config.yml` exists with a `persona` field, use that. Otherwise default to `founder` and **do not ask** — `kite.discover` will ask once if needed.

4. Print a one-line confirmation:
   > "Running the Kite SDLC. Idea: <idea>. Persona: <persona>. Auto-approve gates: <yes|no>."

### Step 2 — Branch and state guardrails

1. If `.git/` exists or `git rev-parse --is-inside-work-tree` succeeds, read the current branch.
2. If the branch is `main` or `master`, STOP before writing feature artifacts. Tell the user to create or switch to a feature branch named from the idea (for example `kite/<short-feature-name>` or the numbering convention already configured by Kite), then rerun or resume the workflow.
3. Do not proceed on `main` or `master`; print the exact command the user can run after resolving the issue.
4. If no git repository exists, skip this guardrail and continue.

### Step 3 — Read or create `.kite/state.yml`

1. If `.kite/state.yml` does not exist, create it:

   ```yaml
   schema_version: "1.0"
   workflow: kite
   stage: start
   updated_at: "<ISO-8601 timestamp now>"
   artifacts: {}
   ```

2. If it exists and `stage` is not `start`, ask:
   > "I see a previous Kite run paused at stage `<stage>`. Resume from there? [yes]"
   - On "yes": skip past every step whose stage is already complete.
   - On "no": confirm reset, then overwrite `stage` to `start`.

### Step 4 — The pipeline

Execute these steps in order. Each numbered item is one persona invocation. Constitution through plan are conversational planning stages; each persona owns its interview and MUST NOT auto-send the next command. After the plan is approved, generate tasks.md, then require exactly one approval gate before automated implementation starts.

1. `kite.constitution` — use the idea as context to draft practical project principles.
2. **Gate (skippable):** "Principles look good — continue to discovery?"
3. `kite.discover` — pass the idea as the argument. Wait for it to complete.
4. **Gate (skippable):** "Discovery looks good — continue to the specification?"
5. `kite.specify` — pass the idea as the argument.
6. **Gate (skippable):** "Spec approved — continue to design?"
7. `kite.design` — pass `persona=<persona>` if non-default.
8. **Gate (skippable):** "Design approved — run a final clarification pass?"
9. `kite.clarify` — pass `persona=<persona>` if non-default.
10. **Gate (skippable):** "Clarification looks complete — continue to planning?"
11. `kite.plan` — pass `persona=<persona>` if non-default.
12. **Gate (skippable):** "Plan approved — generate the task list?"
13. `kite.tasks` — pass `persona=<persona>` if non-default.
14. `kite.analyze` — run a read-only consistency pass across spec, plan, tasks, constitution, design, and contract readiness.
15. **Gate (REQUIRED — never skipped by `auto_approve`):** "Approve tasks.md and the consistency analysis before automated implementation starts?"
16. `kite.backend` — implement `[backend]`-tagged tasks and produce `contract.md`.
17. **Contract gate (HARD — never skipped):** verify the active `FEATURE_DIR/contract.md` exists, contains no `TODO` or `<placeholder>` markers, and includes filled Base URL/auth, endpoint Method + path entries, an Error contract, a Frontend usage map, and Local verification commands. If the check fails, **abort** with: "Backend contract is incomplete. Run `kite.backend` again to finish it before the frontend can build."
18. `kite.frontend` — implement `[frontend]`-tagged tasks against the published contract.
19. `kite.docs` — implement `[docs]`-tagged documentation tasks.
20. `kite.qa` — implement and run `[qa]`-tagged tasks and append the QA report.

For each persona invocation:

- **Print the stage banner:** "Stage X/12 — <persona name>".
- **Invoke the persona command** with the prepared arguments. The persona writes its own files and updates `.kite/state.yml` itself.
- **For brownfield repositories**, include the instruction: "Read existing docs, config, tests, source layout, and relevant implemented features first. Do not ask the user to restate existing behavior unless the repository evidence conflicts or is missing."
- **After the persona returns**, read its 5-bullet summary back to the user (the persona always prints one).
- **Run the gate** if required. Planning gates are one yes/no question and may be skipped only when `auto_approve` is true. The tasks gate is ALWAYS required. After the tasks gate is approved, continue backend → contract gate → frontend → docs → qa without repeated approval prompts unless blocked or unsafe.

### Step 5 — Hard gates

The contract gate is **never** skipped. Algorithm:

1. Resolve the active feature directory from the prerequisite scripts, `SPECIFY_FEATURE_DIRECTORY`, or `.kite/feature.json`. Use highest-numbered `specs/` only as a fallback when no active feature context exists.
2. Check `FEATURE_DIR/contract.md` exists. If missing, abort with the message above.
3. Reject `TODO` or `<placeholder>` markers.
4. Require `## 1. Base URL & auth`, `## 2. Endpoints`, `## 5. Error contract`, `## 6. Frontend usage map`, and `## 7. Local verification commands` to be filled.
5. Require at least one endpoint entry, `**Method + path:**` for every endpoint entry, and at least one local verification command.
6. On pass, print `contract gate: OK (<contract path>)`.

If the run is aborted at this gate, leave `.kite/state.yml.stage` set to `backend` so a follow-up `kite.start` can resume.

### Step 6 — Closing summary

After `kite.qa` completes:

1. Update `.kite/state.yml`:

   ```yaml
   stage: complete
   updated_at: "<ISO-8601 timestamp now>"
   ```

2. Print a final summary:
   - One-line verdict from the QA report.
   - Number of tasks completed by persona (`backend`, `frontend`, `docs`, `qa`).
   - Path to the final `tasks.md` and `contract.md`.
   - What to do next: ship this loop, re-run the failing layer command, or investigate the blocker and resume from the affected persona.

### Step 7 — On error / abort

If any persona returns an error, or the user rejects a gate:

1. Update `.kite/state.yml`:

   ```yaml
   stage: <name of stage that failed>
   updated_at: "<ISO-8601 timestamp now>"
   error: "<one-line reason>"
   ```

2. Tell the user:
   - Which stage stopped.
   - What the persona reported (one line).
   - The single command to resume — usually re-running the same persona, or `kite.start` to resume the whole pipeline.

---

**Reminder:** This command is a coordinator. It writes to `.kite/state.yml` only — every other artifact is owned by the persona command that produced it.
