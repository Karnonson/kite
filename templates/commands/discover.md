---
description: Turn a one-line idea into a structured discovery brief in plain English. The first stop in the Kite SDLC for non-technical builders.
handoffs:
  - label: Write the Specification
    agent: kite.specify
    prompt: Use the discovery brief to draft the feature specification.
  - label: Refine Discovery
    agent: kite.discover
    prompt: I want to revise the discovery brief.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is a one-line product idea written in plain English (e.g. "I want a tool where coaches can publish weekly training plans and athletes can mark them done"). Your job is **not** to write the spec — it is to interview the user and produce a `specs/<feature>/discovery.md` brief that the `kite.specify` command will consume next.

## Pre-Execution Checks

**Check for extension hooks (before discovery)**:
- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_discover` key.
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

The text the user typed after `__KITE_COMMAND_DISCOVER__` in the triggering message **is** the product idea. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

This command is the **first** stop in the Kite SDLC and is optimised for **non-technical users** (founders, PMs, domain experts). Your tone, language, and questions must reflect that audience.

### Hard rules for this command

1. **Plain English only.** No engineering jargon. Forbidden words in user-facing prompts: *epic, story, Gherkin, schema, endpoint, payload, scope creep, non-functional, KPI, OKR, RFC, MVP*. Use everyday alternatives ("must-have", "what success looks like", "what users see", "what users do").
2. **One question at a time.** Never bundle three sub-questions into one prompt. Wait for the user's answer before asking the next.
3. **Interview before writing.** Ask every material discovery question needed to understand the project and the user's needs before writing `discovery.md`. Skip only questions already answered by the user's idea, or when the user says to skip questions / proceed / stop.
4. **Default loudly.** Every question proposes a sensible default in square brackets. The user can answer "ok" / "yes" / Enter to accept it.
5. **Never invent a stack.** This command does not pick a tech stack. That happens later in `kite.plan`. If the user volunteers stack info, capture it in *Constraints* but do not lead with it.
6. **No code.** This command never writes code, schemas, API shapes, or UI wireframes. Those belong to `kite.design`, `kite.backend`, `kite.frontend`.
7. **Approval before advancing.** MUST NOT invoke or auto-send `kite.specify`. After writing `discovery.md`, ask the user to approve or revise the brief before the next stage.
8. **Allowed writes.** May write `.kite/state.yml`, `.kite/feature.json`, `kite.config.yml` only when absent, and `specs/<feature>/discovery.md`.
9. **Forbidden writes.** MUST NOT write `spec.md`, `design.md`, `plan.md`, `tasks.md`, application code, tests, or docs outside the active feature directory.

### Step 1 — Locate or create the project marker

1. If `.kite/` does not exist at the repo root, create it: `mkdir -p .kite`.
2. If `.kite/state.yml` does not exist, create it with:
   ```yaml
   schema_version: "1.0"
   workflow: kite
   stage: discover
   updated_at: "<ISO-8601 timestamp now>"
   artifacts: {}
   ```
3. If `.kite/state.yml` exists, update its `stage` to `discover` and `updated_at`. Preserve other keys.

### Step 2 — Create the feature workspace

Discovery artifacts live with the rest of the feature artifacts under `specs/<feature>/`, never at the repository root.

1. Generate a concise short name (2-4 words) from the user's idea using the same slug style as `kite.specify` (for example, `coach-training-plans`).
2. If `.kite/feature.json` exists and contains a `feature_directory` that already points to an existing directory, reuse that directory and set `FEATURE_DIR` to it.
3. Otherwise create a new feature directory under `specs/`:
   - Read `.kite/init-options.json` if present.
   - If `branch_numbering` is `timestamp`, use prefix `YYYYMMDD-HHMMSS`.
   - If `branch_numbering` is `sequential` or absent, scan `specs/` and use the next available 3+ digit prefix (`001`, `002`, ...).
   - Create `FEATURE_DIR=specs/<prefix>-<short-name>`.
4. Persist the feature directory to `.kite/feature.json`:
   ```json
   {
     "feature_directory": "<FEATURE_DIR>"
   }
   ```
   Store the project-relative path, such as `specs/001-coach-training-plans`.

### Step 3 — Read the user's idea, decide what is already answered

Score the user's one-liner against this checklist. Mark each ✅ (clearly answered), ⚠️ (partial), or ❌ (missing):

| # | Topic | Plain-English question for the user |
|---|---|---|
| Q1 | Audience | Who is this for, and what problem of theirs are we solving? |
| Q2 | Must-haves | If this product only did **three things**, what would they be? |
| Q3 | Nice-to-haves | What would be a delightful bonus that we can do later? |
| Q4 | What success looks like | How will we know, in the first month, that this is working? |
| Q5 | Constraints | Any hard rules? (budget, timeline, must run on phones, must be private, must look "boring corporate", etc.) |
| Q6 | Vibe / brand | Three words for the personality of the product. (e.g. "calm, trustworthy, premium" or "playful, fast, irreverent") |

For every ❌ or ⚠️ topic, ask the user the corresponding question — **one at a time**, in the order above. For each ✅ topic, skip the question and reuse the answer the user already gave.

### Step 4 — Conduct the interview

For each question you ask:

1. State the question in plain English.
2. Suggest a sensible default in square brackets.
3. Wait for the user's answer.
4. **Reflect** the answer back in one sentence ("Got it — so the audience is X, and their pain is Y."). This catches misunderstandings early.
5. Continue until every material discovery topic is answered. If the user asks to skip questions, gives no useful answer after one follow-up, or says to proceed, stop asking and record the gap under Open questions.

If the user gives a vague or empty answer, ask **one** clarifying follow-up. Do not loop.

### Step 5 — Seed `kite.config.yml` (one-time)

If `kite.config.yml` does not yet exist at the repo root, ask exactly one extra question:

> "Last housekeeping question: are you the **builder** (you'll be writing/reading code) or the **founder** (you want the AI to do the building)?  [founder]"

Map their answer:
- "founder", "pm", "owner", "non-technical", default → `persona: founder`
- "builder", "junior", "engineer", "dev" → `persona: junior`

Write `kite.config.yml`:
```yaml
schema_version: "1.0"
persona: <founder|junior>
stack: null            # filled in later by kite.plan
default_integration: null  # filled in later by kite init or kite.plan
created_at: "<ISO-8601 timestamp now>"
```

If `kite.config.yml` already exists, do **not** ask this question and do **not** modify the file.

### Step 6 — Write `discovery.md`

Write the brief to `FEATURE_DIR/discovery.md`. Use this exact structure:

```markdown
# Discovery Brief

**Stage:** discover
**Generated by:** kite.discover
**Date:** <ISO-8601 date>

## What this means in plain English

> One paragraph (≤ 60 words) that a friend with no tech background could read and understand. State who this is for, the problem they have, and the smallest version of the solution.

## 1. Audience and problem

- **Who:** ...
- **Problem:** ...
- **Why now:** ... (skip if user did not address it; do not invent)

## 2. Must-haves (the "if it doesn't do this, it's broken" list)

1. ...
2. ...
3. ...

## 3. Nice-to-haves (later, not now)

- ...

## 4. What success looks like in the first month

- ...

## 5. Constraints

- ...

## 6. Accessibility expectations

Accessible by default: keyboard access, visible focus, readable contrast, clear labels, clear error messages, and information that is not conveyed by color alone.

## 7. Vibe

Three words: **<word1>, <word2>, <word3>**.

## 8. Open questions for the next stage

> Things you (the agent) noticed that `kite.specify` will need a clearer answer to. Phrase each as a yes/no or A-or-B question so the user can answer fast.

- [ ] ...

## 9. What happens next

The next command, `kite.specify`, will turn this brief into a formal feature specification. You'll get to review it before any planning happens.
```

**Rules for the brief:**

- The "What this means in plain English" section is **mandatory** and must come first.
- Section 2 must contain **exactly three** must-haves. If the user gave fewer, ask one more question (counts toward the six-question budget). If they gave more, pick the top three and put the rest in section 3.
- Do not include any tech-stack discussion. That belongs to `kite.plan`.
- Do not number constraints if there are zero — write "None stated."

### Step 7 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: discover
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     discovery: <FEATURE_DIR>/discovery.md
   ```
2. Print a **5-bullet** summary to the user:
   - Who it's for
   - The problem
   - The three must-haves
   - The vibe
   - Number of open questions parked for `kite.specify`
3. Ask: "Ready to turn this into a formal specification? Approve to continue with `kite.specify`, or tell me what to change in the brief."

### Step 8 — Handoff

If the user approves, recommend running `kite.specify`. Tell them it will reuse the same `FEATURE_DIR` from `.kite/feature.json`. Do not run it for them — the orchestrator (`kite.start`) handles that. If the user is running this command standalone, they will invoke `kite.specify` themselves.

---

**Reminder:** This command writes one feature artifact (`FEATURE_DIR/discovery.md`) and state/config files (`.kite/state.yml`, `.kite/feature.json`, optionally `kite.config.yml`). It writes nothing in `src/`.
