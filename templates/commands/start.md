---
description: Run the full Kite SDLC end-to-end (discover → specify → design → plan → tasks → backend → frontend → qa) with optional gates between stages.
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

This command is the **orchestrator entrypoint** for the Kite SDLC. It runs each persona in sequence, pausing for human review between stages unless the user opts into auto-approval.

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
2. **One stage at a time.** Run one persona, then stop and either auto-advance (if `auto_approve` is on) or wait for the user to approve.
3. **Resume-aware.** Always read `.kite/state.yml` first. If a previous run paused mid-flow, offer to resume from that step, not from the top.
4. **Plain English.** Every gate prompt is one short plain-English question. Forbidden: *epic, story, Gherkin, schema, endpoint, payload, scope creep, non-functional, KPI, OKR, RFC, MVP*.
5. **Hard gates are non-negotiable.** The contract gate between `kite.backend` and `kite.frontend` is enforced even when `auto_approve` is on.

### Step 1 — Resolve inputs

1. Parse `$ARGUMENTS` for any of:
   - `idea=<one line>`
   - `persona=<founder|junior>` (default: `founder`)
   - `auto_approve=<true|false>` (default: `false`)
   - `integration=<copilot|claude|codex|...>` (default: read from `kite.config.yml` if present, else `copilot`)
   - Any free-form text not matching the above is treated as the idea.

2. If `idea` is still empty, ask:
   > "What do you want to build? One sentence is enough."

3. If `persona` is unset and `kite.config.yml` exists with a `persona` field, use that. Otherwise default to `founder` and **do not ask** — `kite.discover` will ask once if needed.

4. Print a one-line confirmation:
   > "Running the Kite SDLC. Idea: <idea>. Persona: <persona>. Auto-approve gates: <yes|no>."

### Step 2 — Read or create `.kite/state.yml`

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

### Step 3 — The pipeline

Execute these steps in order. Each numbered item is one persona invocation. Between invocations, run the **gate** unless `auto_approve` is true.

1. `kite.discover` — pass the idea as the argument. Wait for it to complete.
2. **Gate (skippable):** "Discovery looks good — continue to the specification?"
3. `kite.specify` — pass `persona=<persona>` if non-default.
4. **Gate (skippable):** "Spec approved — continue to design?"
5. `kite.design`
6. **Gate (skippable):** "Design approved — continue to planning?"
7. `kite.plan`
8. **Gate (skippable):** "Plan approved — generate the task list?"
9. `kite.tasks`
10. `kite.backend` — implement `[backend]`-tagged tasks; produces `contract.md`.
11. **Contract gate (HARD — never skipped):** verify `specs/<latest>/contract.md` exists and contains no `TODO` or `<placeholder>` markers. If the check fails, **abort** with:
    > "Backend contract is incomplete. Run `kite.backend` again to finish it before the frontend can build."
12. `kite.frontend` — implement `[frontend]`-tagged tasks.
13. `kite.qa` — implement and run `[qa]`-tagged tasks.

For each persona invocation:

- **Print the stage banner:** "Stage X/13 — <persona name>".
- **Invoke the persona command** with the prepared arguments. The persona writes its own files and updates `.kite/state.yml` itself.
- **After the persona returns**, read its 5-bullet summary back to the user (the persona always prints one).
- **Run the gate** if `auto_approve` is false. The gate is one yes/no question. On "no" or "reject", abort the run and tell the user which persona to re-run.

### Step 4 — Hard gates

The contract gate (step 11) is **never** skipped. Algorithm:

1. Find `specs/<latest>/`. The latest spec directory is the highest-numbered one (e.g. `specs/003-…/` beats `specs/002-…/`).
2. Check `<latest>/contract.md` exists. If missing, abort with the message above.
3. `grep -E 'TODO|<[a-zA-Z][^>]*>' <latest>/contract.md`. If any match, abort.
4. On pass, print "✅ Contract gate passed — frontend may proceed."

If the run is aborted at this gate, leave `.kite/state.yml.stage` set to `backend` so a follow-up `kite.start` can resume.

### Step 5 — Closing summary

After `kite.qa` completes:

1. Update `.kite/state.yml`:
   ```yaml
   stage: complete
   updated_at: "<ISO-8601 timestamp now>"
   ```
2. Print a final summary:
   - One-line verdict from the QA report (✅ / ⚠️ / 🛑).
   - Number of tasks completed by persona (`backend`, `frontend`, `qa`).
   - Path to the final `tasks.md` and `contract.md`.
   - One-line "what's next" recommendation:
     - ✅ → "Ship this loop, or open a new one with `kite.start`."
     - ⚠️ → "Fix the failing tests with `kite.backend` or `kite.frontend`, then re-run `kite.qa`."
     - 🛑 → "Investigate the blocker and re-run from the affected persona."

### Step 6 — On error / abort

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
