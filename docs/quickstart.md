# Quick Start Guide

This guide helps you start building with Kite.

## 5 commands, no jargon (for founders)

If you're a founder or junior builder and just want to ship something,
these are the only commands you need. Run them in order in your AI
coding assistant (Copilot, Claude, or Codex).

1. **Set up the project (choose one path):**

    Dev container, easiest for new builders:

    ```bash
    mkdir my-app
    cd my-app
    curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
    code .
    ```

    Then run **Dev Containers: Reopen in Container** in VS Code.

    Direct install, if Kite is already installed on your machine:

    ```bash
    kite init my-app --integration copilot
    cd my-app
    ```

    Add `--profile minimal` to install only the guided workflow commands, or
    `--profile full` to include every optional Kite command. The default
    `standard` profile keeps Copilot's visible agent list focused while still
    including `kite.research` for stack guidance. To change the profile later,
    run `kite profile set <name>` (then `kite integration upgrade --force` to apply).

2. **In your AI assistant**, run the orchestrator:

    ```
    /kite.start "Build a tool that does <one sentence about your idea>."
    ```

    Kite will walk you through one stage at a time — Constitution →
    Discover → Specify → Design → Clarify → Plan → Tasks → Backend → Frontend → QA — and ask
    "approve and continue?" between each stage. You only ever
    answer plain-English yes/no questions.

    For an existing codebase, initialize Kite in that repository and describe
    the change you want:

    ```
    /kite.start "Improve the existing dashboard filters."
    ```

    Kite treats this as brownfield work: the agent should read existing docs,
    config, tests, source layout, and relevant implemented features before
    asking you questions. You should only need to clarify the desired change,
    missing evidence, or conflicts. Kite also writes `.kite/project-context.json`
    with detected stack details and validation commands so later agents can
    reuse that context instead of rediscovering the project.

3. **Before or after implementation, run** `kite check` (in the terminal)
   to refresh `.kite/project-context.json` and execute the validation commands
   Kite detected for this project. Use `kite check --tools` when you only want
   to check installed tools and agent CLIs.

4. **If anything pauses or breaks, run** `kite resume` (in the terminal)
   to pick up exactly where you left off.

5. **If you're not sure what's missing**, run `kite doctor` for a
   plain-language report — it tells you which `/kite.*` command to run
   next.

That's it. The five commands you'll actually type are:

| When | What you type | Where |
| --- | --- | --- |
| Once, to set up | Dev container script or `kite init my-app --integration copilot` | Terminal |
| Every new feature | `/kite.start "<idea>"` | AI assistant |
| To validate work | `kite check` | Terminal |
| If a step stalls | `kite resume` | Terminal |
| If you're lost | `kite doctor` | Terminal |
| To pick up later | `/kite.start` (no idea) | AI assistant — auto-resumes |

Everything else in this document is optional context and power-user
controls.

---

## Manual Process

> [!TIP]
> **Context Awareness**: Kite commands automatically detect the active feature based on your current Git branch (e.g., `001-feature-name`). To switch between different specifications, simply switch Git branches.

### Step 1: Install Kite

**In your terminal**, either use the dev container or initialize your project
with the Kite CLI.

Dev container:

```bash
mkdir <PROJECT_NAME>
cd <PROJECT_NAME>
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
code .
```

Then run **Dev Containers: Reopen in Container** in VS Code. Kite installs
and initializes the workspace automatically.

Direct CLI install:

```bash
# Create a new project directory
uvx --from git+https://github.com/Karnonson/kite.git kite init <PROJECT_NAME>

# OR initialize in the current directory
uvx --from git+https://github.com/Karnonson/kite.git kite init .
```

> [!NOTE]
> You can also install the CLI persistently with `pipx`:
> ```bash
> pipx install git+https://github.com/Karnonson/kite.git
> ```
> After installing with `pipx`, run `kite` directly instead of `uvx --from ... kite`, for example:
> ```bash
> kite init <PROJECT_NAME>
> kite init .
> ```

Use Bash scripts explicitly if needed:

```bash
uvx --from git+https://github.com/Karnonson/kite.git kite init <PROJECT_NAME> --script sh
```

### Step 2: Define Your Constitution

**In your coding agent's chat interface**, use the `/kite.constitution` slash command to establish the core rules and principles for your project. You should provide your project's specific principles as arguments.

```markdown
/kite.constitution This project follows a "Library-First" approach. All features must be implemented as standalone libraries first. We use TDD strictly. We prefer functional programming patterns.
```

### Step 3: Create the Spec

**In the chat**, use the `/kite.specify` slash command to describe what you want to build. Focus on the **what** and **why**, not the tech stack.

```markdown
/kite.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
```

### Step 4: Create the Design Brief

**In the chat**, use the `/kite.design` slash command to define the product's screens, interaction shape, and design direction before planning.

```bash
/kite.design persona=founder
```

### Step 5: Refine the Spec After Design

**In the chat**, use the `/kite.clarify` slash command to identify and resolve ambiguities in your specification. You can provide specific focus areas as arguments.

```bash
/kite.clarify Focus on security and performance requirements.
```

### Step 6: Create a Technical Implementation Plan

**In the chat**, use the `/kite.plan` slash command to provide your tech stack and architecture choices. The planning agent should use the `kite.research` subagent internally when it needs current official framework versions, hosting guidance, or AI SDK capability checks.

```markdown
/kite.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

### Step 7: Break Down and Implement

**In the chat**, use the `/kite.tasks` slash command to create an actionable task list.

```markdown
/kite.tasks
```

If your integration installs optional review commands, you can validate the plan with `/kite.analyze`:

```markdown
/kite.analyze
```

Then, run the split implementation commands in order.

```markdown
/kite.backend
/kite.frontend
/kite.docs
/kite.qa
```

> [!TIP]
> **Phased Implementation**: For complex projects, implement in phases to avoid overwhelming the agent's context. Start with core functionality, validate it works, then add features incrementally.

## Detailed Example: Building Taskify

Here's a complete example of building a team productivity platform:

### Step 1: Define Constitution

Initialize the project's constitution to set ground rules:

```markdown
/kite.constitution Taskify is a "Security-First" application. All user inputs must be validated. We use a microservices architecture. Code must be fully documented.
```

### Step 2: Define Requirements with `/kite.specify`

```text
Develop Taskify, a team productivity platform. It should allow users to create projects, add team members,
assign tasks, comment and move tasks between boards in Kanban style. In this initial phase for this feature,
let's call it "Create Taskify," let's have multiple users but the users will be declared ahead of time, predefined.
I want five users in two different categories, one product manager and four engineers. Let's create three
different sample projects. Let's have the standard Kanban columns for the status of each task, such as "To Do,"
"In Progress," "In Review," and "Done." There will be no login for this application as this is just the very
first testing thing to ensure that our basic features are set up.
```

### Step 3: Refine the Specification

Use the `/kite.clarify` command to interactively resolve any ambiguities in your specification. You can also provide specific details you want to ensure are included.

```bash
/kite.clarify I want to clarify the task card details. For each task in the UI for a task card, you should be able to change the current status of the task between the different columns in the Kanban work board. You should be able to leave an unlimited number of comments for a particular card. You should be able to, from that task card, assign one of the valid users.
```

You can continue to refine the spec with more details using `/kite.clarify`:

```bash
/kite.clarify When you first launch Taskify, it's going to give you a list of the five users to pick from. There will be no password required. When you click on a user, you go into the main view, which displays the list of projects. When you click on a project, you open the Kanban board for that project. You're going to see the columns. You'll be able to drag and drop cards back and forth between different columns. You will see any cards that are assigned to you, the currently logged in user, in a different color from all the other ones, so you can quickly see yours. You can edit any comments that you make, but you can't edit comments that other people made. You can delete any comments that you made, but you can't delete comments anybody else made.
```

### Step 4: Validate the Spec

If your integration installs optional review commands, validate the specification checklist using the `/kite.checklist` command:

```bash
/kite.checklist
```

### Step 5: Generate Technical Plan with `/kite.plan`

Be specific about your tech stack and technical requirements:

```bash
/kite.plan We are going to generate this using .NET Aspire, using Postgres as the database. The frontend should use Blazor server with drag-and-drop task boards, real-time updates. There should be a REST API created with a projects API, tasks API, and a notifications API.
```

### Step 6: Define Tasks

Generate an actionable task list using the `/kite.tasks` command:

```bash
/kite.tasks
```

### Step 7: Validate and Implement

If available, have your coding agent audit the implementation plan using `/kite.analyze`:

```bash
/kite.analyze
```

Finally, implement the solution:

```bash
/kite.backend
/kite.frontend
/kite.qa
```

> [!TIP]
> **Phased Implementation**: For large projects like Taskify, consider implementing in phases (e.g., Phase 1: Basic project/task structure, Phase 2: Kanban functionality, Phase 3: Comments and assignments). This prevents context saturation and allows for validation at each stage.

## Key Principles

- **Be explicit** about what you're building and why
- **Don't focus on tech stack** during specification phase
- **Iterate and refine** your specifications before implementation
- **Validate** the plan before coding begins
- **Let the coding agent handle** the implementation details

## Next Steps

- Read the [complete methodology](https://github.com/Karnonson/kite/blob/main/spec-driven.md) for in-depth guidance
- Check out [more examples](https://github.com/Karnonson/kite/tree/main/templates) in the repository
- Explore the [source code on GitHub](https://github.com/Karnonson/kite)
