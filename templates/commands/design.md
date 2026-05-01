---
description: Produce a plain-English design system + page layout brief from the discovery and specification. Text-only — no images, no code.
handoffs:
  - label: Clarify Before Planning
    agent: kite.clarify
    prompt: Run a final clarification pass before we start the technical plan.
  - label: Refine Design
    agent: kite.design
    prompt: I want to revise the design brief.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is optional guidance for the design phase (e.g. "calm + serious, B2B feel, no purple"). Your job is to produce a `design.md` file with two top-level sections — **Design System** and **Layout** — written in plain English. You do **not** write code, CSS, Figma JSON, or wireframe images.

## Pre-Execution Checks

**Check for extension hooks (before design)**:
- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_design` key.
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

This command runs **after** `kite.specify` and **before** the pre-plan clarification and research steps. It is optimised for non-technical users — keep all language plain.

### Hard rules for this command

1. **Plain English only.** Forbidden words in user-facing prompts: *epic, story, schema, endpoint, payload, non-functional, KPI, OKR, RFC, MVP, design tokens (use "style choices"), atomic design*. Use everyday alternatives ("colors", "spacing", "what each page looks like").
2. **Text only.** Never produce images, SVG, base64, Figma JSON, or rendered HTML. ASCII boxes are allowed for layout sketches and must stay under 80 columns wide.
3. **No code.** Do not write CSS, Tailwind classes, React JSX, or component code. That belongs to `kite.frontend`.
4. **Reuse what exists.** If `FEATURE_DIR/discovery.md` declared a vibe or constraints, lift them — do not re-ask.
5. **Interview before writing.** Most answers should come from `FEATURE_DIR/discovery.md` and `FEATURE_DIR/spec.md`, but ask every material design question that remains. Ask exactly one question at a time with a sensible default, and stop only when the design choices are clear or the user says to skip questions / proceed / stop.
6. **One Designer.** This command produces the **system** and the **layout** in one file. Do not split.
7. **Accessibility default.** The design MUST include keyboard access, visible focus, readable contrast, clear labels, clear error messages, and no color-only signaling for every user-facing flow.
8. **Approval before advancing.** MUST NOT invoke or auto-send `kite.clarify` or `kite.plan`. After writing `design.md`, ask the user to approve or revise the design.
9. **Allowed writes.** May write `FEATURE_DIR/design.md` and `.kite/state.yml`.
10. **Forbidden writes.** MUST NOT write code, CSS, framework config, `plan.md`, `tasks.md`, or docs outside the feature directory.

### Step 1 — Read existing artifacts

1. Resolve `FEATURE_DIR`: prefer `.kite/feature.json` if it points to an existing directory, otherwise use the latest directory under `specs/`.
2. Required inputs (refuse to run if any are missing — tell the user which command produces each):
    - `FEATURE_DIR/discovery.md` (produced by `kite.discover`)
    - `FEATURE_DIR/spec.md` (produced by `kite.specify`)
3. Optional inputs (use if present):
   - `kite.config.yml` — read `persona` to tune your tone (founder = warmer, junior = more concise).
   - `.kite/state.yml` — confirm previous stage was `specify`.

If `FEATURE_DIR/discovery.md` or `FEATURE_DIR/spec.md` is missing, abort and tell the user:
> "I need a discovery brief and a specification first. Run `kite.discover` and then `kite.specify`, then come back."

### Step 2 — Decide what is already answered

Score against this checklist (✅ / ⚠️ / ❌):

| # | Topic | Plain-English question (only if ❌ or ⚠️) |
|---|---|---|
| Q1 | Vibe | Three words for the personality of the product. |
| Q2 | Brand colors | Any colors you must keep or must avoid? |
| Q3 | References | Any apps or websites you'd point at and say "feel like that"? |
| Q4 | Density | Should the product feel **roomy** (lots of whitespace) or **dense** (more on screen at once)? |

For every ❌ or ⚠️ topic, ask the user, **one at a time**, with a sensible default in square brackets. Skip ✅ topics. If answers expose another material design choice, ask that follow-up before writing `design.md` unless the user asks to proceed.

### Step 3 — Build the page list

From `FEATURE_DIR/spec.md`, extract every distinct **screen / page / view** the user will encounter. If the spec is light on screens, infer from must-haves in `FEATURE_DIR/discovery.md` and confirm with the user in **one** consolidated message ("I'm planning these 5 screens — sound right?").

For each page, capture:
- **Name** (plain English, not a URL)
- **Purpose** (one sentence)
- **Primary action** (what the user does here)
- **Key elements** (a short list — header, list, form, etc.)

### Step 4 — Write `design.md`

Write the brief to `specs/<latest>/design.md`. Use this exact structure:

```markdown
# Design Brief

**Stage:** design
**Generated by:** kite.design
**Date:** <ISO-8601 date>

## What this means in plain English

> One paragraph (≤ 60 words). Describe the look, the feel, and the shape of the product so a non-technical reader gets it on first read.

## 1. Design System

### 1.1 Personality

Three words: **<word1>, <word2>, <word3>**.
Anchor reference: <one app or website the user named, or "none">.

### 1.2 Colors

| Role | Choice | Why |
|---|---|---|
| Primary | <name + plain hex if you must> | <one line> |
| Surface | <name> | <one line> |
| Text | <name> | <one line> |
| Accent | <name> | <one line> |
| Danger | <name> | <one line> |

> Pick **at most 5** roles. Do not invent a 12-step neutral ramp.

### 1.3 Typography

- **Headings:** <plain description, e.g. "a friendly geometric sans, slightly bold">
- **Body:** <plain description>
- **Mono / numbers:** <plain description, or "same as body">

### 1.4 Spacing & shape

- **Spacing rhythm:** <e.g. "everything sits on a 4-pixel grid">
- **Corner radius:** <e.g. "soft — about 8px on cards, 6px on buttons">
- **Shadow / elevation:** <one line>

### 1.5 Components inventory

A list of the reusable UI building blocks the product needs. Do **not** describe how to code them.

- [ ] Button (primary, secondary, danger)
- [ ] Text input
- [ ] ...

> Keep this list short. If a component appears on only one page, do not list it here — list it under that page's *Key elements*.

### 1.6 Accessibility defaults

- Keyboard access: <how primary actions can be reached without a mouse>
- Visible focus: <how focused controls are obvious>
- Readable contrast: <plain-language contrast expectation>
- Clear labels: <how fields/buttons are named>
- Clear errors: <how errors explain the problem and next step>
- Non-color signaling: <how status is shown without relying on color alone>

## 2. Layout

### 2.1 Page list

For every page, copy this block:

```
#### <Page name>

- **Purpose:** ...
- **Primary action:** ...
- **Key elements:**
  - ...
- **Sketch:**
  ```
  +-----------------------------+
  |  Header                     |
  +-----------------------------+
  |                             |
  |  <main content shape>       |
  |                             |
  +-----------------------------+
  ```
```

> ASCII boxes are optional. Use them only when they clarify structure.

### 2.2 Navigation

How does the user move between pages? Pick **one** model and explain in one paragraph.

## 3. Open questions for the next stage

> Things `kite.plan` will need to decide. Phrase as yes/no or A-or-B questions.

- [ ] ...

## 4. What happens next

The next command, `kite.plan`, will turn this design and the spec into an implementation plan. After the plan, `kite.tasks` produces the actionable task list.
```

**Rules for the brief:**

- The "What this means in plain English" section is **mandatory** and must come first.
- The Components inventory must contain **at least 3** items (Button, Text input, plus one more) — anything less means the design is too thin.
- Do not include any tech-stack discussion (React vs Vue, Tailwind vs CSS modules). That belongs to `kite.plan`, which can use the `kite.research` subagent when it needs current technical guidance.
- Do not include accessibility code. State the **goals** in plain English under section 1.6; accessibility is mandatory for user-visible UI, not optional polish.

### Step 5 — Update state and present a summary

1. Update `.kite/state.yml`:
   ```yaml
   stage: design
   updated_at: "<ISO-8601 timestamp now>"
   artifacts:
     design: specs/<latest>/design.md
   ```
2. Print a **5-bullet** summary to the user:
   - Three-word vibe
   - Number of colors locked in
   - Number of pages identified
   - Navigation model
   - Number of open questions parked for `kite.plan`
3. Ask: "Ready for a clarification pass before planning? Approve to continue with `kite.clarify`, or tell me what to change in the design."

### Step 6 — Handoff

If the user approves, recommend running `kite.clarify`. Do not run it for them — the orchestrator (`kite.start`) handles that.

---

**Reminder:** This command writes one file (`design.md`) and updates `.kite/state.yml`. It writes nothing in `src/`, no images, no code.
