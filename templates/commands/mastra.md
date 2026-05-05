---
description: Install the official Mastra framework skills into this project so the agent can write accurate, version-matched Mastra code.
context_hint: "When the user mentions Mastra, wants to build AI agents or workflows with Mastra, or asks how to integrate the Mastra framework, invoke `/kite.mastra` before writing any code."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Download the official Mastra agent skill from `https://github.com/mastra-ai/skills` and install it into this project so that future Mastra development uses verified, up-to-date API patterns.

### Step 1 — Check if already installed

Look for `.kite/skills/mastra/SKILL.md` in the project root.

- **If it exists**: print "✅ Mastra skill already installed at `.kite/skills/mastra/`. Skipping download." and proceed to **Step 4**.
- **If it does not exist**: continue to Step 2.

### Step 2 — Download the Mastra skill files

Create the directory `.kite/skills/mastra/references/` and `.kite/skills/mastra/scripts/`.

Fetch the following files from the official Mastra skills repository and save them to the corresponding paths under `.kite/skills/mastra/`:

| Source URL | Local path |
|---|---|
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/SKILL.md` | `.kite/skills/mastra/SKILL.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/references/create-mastra.md` | `.kite/skills/mastra/references/create-mastra.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/references/embedded-docs.md` | `.kite/skills/mastra/references/embedded-docs.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/references/remote-docs.md` | `.kite/skills/mastra/references/remote-docs.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/references/common-errors.md` | `.kite/skills/mastra/references/common-errors.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/references/migration-guide.md` | `.kite/skills/mastra/references/migration-guide.md` |
| `https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra/scripts/provider-registry.mjs` | `.kite/skills/mastra/scripts/provider-registry.mjs` |

Use `curl`, `wget`, or the HTTP client available in this environment. Example:

```bash
mkdir -p .kite/skills/mastra/references .kite/skills/mastra/scripts
BASE="https://raw.githubusercontent.com/mastra-ai/skills/main/skills/mastra"
curl -fsSL "$BASE/SKILL.md" -o .kite/skills/mastra/SKILL.md
curl -fsSL "$BASE/references/create-mastra.md"    -o .kite/skills/mastra/references/create-mastra.md
curl -fsSL "$BASE/references/embedded-docs.md"    -o .kite/skills/mastra/references/embedded-docs.md
curl -fsSL "$BASE/references/remote-docs.md"      -o .kite/skills/mastra/references/remote-docs.md
curl -fsSL "$BASE/references/common-errors.md"    -o .kite/skills/mastra/references/common-errors.md
curl -fsSL "$BASE/references/migration-guide.md"  -o .kite/skills/mastra/references/migration-guide.md
curl -fsSL "$BASE/scripts/provider-registry.mjs"  -o .kite/skills/mastra/scripts/provider-registry.mjs
```

If any download fails, report the specific file that failed and stop — do not proceed with a partial install.

### Step 3 — Register in `.kite/skills.json`

Read `.kite/skills.json` (create it if it does not exist — start with `{}`).

Upsert the following entry under the key `"mastra"`:

```json
{
  "mastra": {
    "id": "mastra",
    "name": "Mastra Framework",
    "version": "fetched",
    "source": "https://github.com/mastra-ai/skills",
    "skill_file": ".kite/skills/mastra/SKILL.md",
    "installed_at": "<ISO-8601 timestamp>"
  }
}
```

Write the updated JSON back to `.kite/skills.json`.

### Step 4 — Load the skill into context

Read `.kite/skills/mastra/SKILL.md` and treat its contents as active instructions for the remainder of this session. In particular:

- **Never rely on internal training knowledge about Mastra APIs.** Always verify against embedded docs or remote docs as instructed in the skill.
- Before writing any Mastra code, follow the priority order defined in the skill: embedded docs → source code → remote docs.
- Use `.kite/skills/mastra/references/` for targeted lookups (setup, errors, migration, API signatures).
- Use `.kite/skills/mastra/scripts/provider-registry.mjs` to validate model names before using them.

### Step 5 — Confirm to the user

Print a short confirmation:

```
✅ Mastra skill installed.

Files:
  .kite/skills/mastra/SKILL.md
  .kite/skills/mastra/references/  (5 reference files)
  .kite/skills/mastra/scripts/provider-registry.mjs

The Mastra skill is now active. I will verify all Mastra APIs against
the embedded docs in your node_modules before writing any code.

Next step: tell me what you want to build with Mastra.
```

If the user provided input in `$ARGUMENTS`, use it as the starting point for the next step rather than waiting for a prompt.
