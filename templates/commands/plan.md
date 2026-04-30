---
description: Turn the validated spec and clarified preferences into an implementation plan, using the kite.research subagent for current official guidance when needed.
handoffs: 
  - label: Create Tasks
    agent: kite.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: kite.checklist
    prompt: Create a checklist for the following domain...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before planning)**:
- Check if `.kite/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_plan` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
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
- If no hooks are registered or `.kite/extensions.yml` does not exist, skip silently

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC, `specs/<latest>/design.md` if present, `specs/<latest>/research.md` if present, `kite.config.yml` if present, and `/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Gather planning preferences**: If `kite.config.yml` and the current artifacts do not yet capture the planning-critical preferences, ask the user the minimum set of consolidated questions yourself: framework, hosting target, budget posture, and whether an AI SDK / agent framework is actually needed. Offer a recommended default with a short reason whenever you ask for a preference. Once you have candidate choices, invoke the `kite.research` subagent to verify current official docs, stable versions, hosting fit, and MCP / skill support for any AI SDK or agent framework. Persist any accepted choices into `kite.config.yml` yourself; the research subagent is a helper, not the owner of workflow state.

4. **Execute plan workflow**: Fill Technical Context from `research.md` and `kite.config.yml` first, marking unknowns as `NEEDS CLARIFICATION`. Then fill Constitution Check from the constitution, evaluate gates, refresh `research.md` through the research subagent so the version checks and official-doc references are current, generate `data-model.md`, `contracts/`, and `quickstart.md`, update agent context by running the agent script, and re-evaluate Constitution Check post-design.

5. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

6. **Check for extension hooks**: After reporting, check if `.kite/extensions.yml` exists in the project root.
   - If it exists, read it and look for entries under the `hooks.after_plan` key
   - If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
   - Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
   - For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
     - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
     - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
   - For each executable hook, output the following based on its `optional` flag:
     - **Optional hook** (`optional: true`):
       ```
       ## Extension Hooks

       **Optional Hook**: {extension}
       Command: `/{command}`
       Description: {description}

       Prompt: {prompt}
       To execute: `/{command}`
       ```
     - **Mandatory hook** (`optional: false`):
       ```
       ## Extension Hooks

       **Automatic Hook**: {extension}
       Executing: `/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - If no hooks are registered or `.kite/extensions.yml` does not exist, skip silently

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above: turn each `NEEDS CLARIFICATION`, dependency, integration, framework, hosting target, or AI SDK question into a targeted research task.

2. **Use the `kite.research` subagent or targeted research tasks**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain} and verify the current stable version from official docs"
   For each AI SDK or agent framework:
     Task: "Check official docs for MCP servers, MCP integrations, skills, templates, and recommended setup for {tech}"
   ```

3. **Consolidate findings** in `research.md`: record the decision, rationale, alternatives considered, and the exact official source URL used to verify the version or capability.

4. **Never guess versions from memory**: if an official source or current package registry cannot verify a version, write `NEEDS CLARIFICATION` instead of pinning an unverified version.

**Output**: `research.md` with all `NEEDS CLARIFICATION` items resolved or explicitly deferred.

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

3. **Agent context update**:
   - Update the plan reference between the `<!-- KITE START -->` and `<!-- KITE END -->` markers in `__CONTEXT_FILE__` to point to the plan file created in step 1 (the IMPL_PLAN path)

**Output**: data-model.md, /contracts/*, quickstart.md, updated agent context file

## Plain-English summary block (REQUIRED)

Before you finish writing the plan file, you **MUST** insert a section
titled `## What this means in plain English` immediately after the
document title. The block follows these rules:

- 3 to 5 short bullets, written for a non-technical founder.
- No jargon. Forbidden words: *epic, story, Gherkin, schema, endpoint,
  payload, non-functional, KPI, OKR, RFC, MVP, scope creep*.
- Each bullet answers one of: **What are we building first?**,
  **What pieces does it have?**, **What do we need to figure out before
  we start?**, **What is deliberately left for later?**, **How long until
  we can test something real?**
- If you cannot fill a bullet honestly from the plan, drop the bullet
  rather than inventing content.

A plan without this block is incomplete and must be rewritten.

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation and agent context files
- Never lock framework or AI SDK versions from memory alone. Verify them against current official docs, release notes, or official package registries.
- ERROR on gate failures or unresolved clarifications
