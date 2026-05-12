# Core Commands

The core `kite` commands handle project initialization, system checks, and version information.

## Initialize a Project

```bash
kite init [<project_name>]
```

| Option                   | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| `--integration <key>`    | AI coding agent integration to use (e.g. `copilot`, `claude`, `gemini`). See the [Integrations reference](integrations.md) for all available keys |
| `--integration-options`  | Options for the integration (e.g. `--integration-options="--commands-dir .myagent/cmds"`) |
| `--profile <name>`       | Command install profile: `minimal`, `standard` (default), or `full`. Controls how many Kite commands are installed |
| `--script sh\|ps`        | Script type: `sh` (bash/zsh) or `ps` (PowerShell)                       |
| `--here`                 | Initialize in the current directory instead of creating a new one        |
| `--force`                | Force merge/overwrite when initializing in an existing directory         |
| `--no-git`               | Skip git repository initialization                                       |
| `--ignore-agent-tools`   | Skip checks for AI coding agent CLI tools                                |
| `--branch-numbering`     | Branch numbering strategy: `sequential` (default) or `timestamp`         |

### Install Profiles

| Profile    | Description                                                                 |
| ---------- | --------------------------------------------------------------------------- |
| `minimal`  | Guided workflow plus required helpers (`kite.analyze`, `kite.browser`, `kite.checklist`) |
| `standard` | Minimal profile + `kite.research` (default, keeps the agent list focused)   |
| `full`     | Every Kite command including optional review and helper agents               |

```bash
kite init --integration copilot --profile minimal   # lean setup
kite init --integration copilot                     # standard (default)
kite init --integration copilot --profile full      # everything
```

Use `kite profile set <name>` to change the profile for an existing project, then run `kite integration upgrade --force` to apply it.

Creates a new Kite project with the necessary directory structure, templates, scripts, and AI coding agent integration files.

Use `<project_name>` to create a new directory, or `--here` (or `.`) to initialize in the current directory. If the directory already has files, use `--force` to merge without confirmation.

### Examples

```bash
# Create a new project with an integration
kite init my-project --integration copilot

# Initialize in the current directory
kite init --here --integration copilot

# Force merge into a non-empty directory
kite init --here --force --integration copilot

# Skip git initialization
kite init my-project --integration copilot --no-git

# Use timestamp-based branch numbering (useful for distributed teams)
kite init my-project --integration copilot --branch-numbering timestamp
```

### Environment Variables

| Variable          | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repositories. Set to the feature directory name (e.g., `001-photo-albums`) to work on a specific feature when not using Git branches. Must be set in the context of the agent prior to using `/kite.plan` or follow-up commands. |

## Check Installed Tools

```bash
kite check
```

Checks that required tools are available on your system: `git` and any CLI-based AI coding agents. IDE-based agents are skipped since they don't require a CLI tool.

To run project validation commands recorded in `.kite/project-context.json`, opt in explicitly:

```bash
kite check --run-validation
```

Use `kite check --run-validation --no-refresh-context` to run the saved validation commands without refreshing detected context first.

## Version Information

```bash
kite version
```

Displays the Kite CLI version, Python version, platform, and architecture.

A quick version check is also available via:

```bash
kite --version
kite -V
```

## Manage the Install Profile

### Show the current profile

```bash
kite profile
kite profile show
```

Displays the active install profile and integration details for the current project:

```text
Kite project profile
  Profile:     standard
  Integration: copilot
  Script type: sh

Available profiles: minimal, standard, full
```

### Change the profile

```bash
kite profile set <name>
```

| Argument / Option | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| `<name>`          | Target profile: `minimal`, `standard`, or `full`                     |
| `--upgrade`       | Immediately run `kite integration upgrade` to apply changes          |

Updates `.kite/init-options.json` with the new profile. Without `--upgrade`, agent files are not regenerated until you run:

```bash
kite integration upgrade --force
```

**Example — switch from standard to full, then apply:**

```bash
kite profile set full --upgrade
```

**Example — switch to minimal, apply manually:**

```bash
kite profile set minimal
kite integration upgrade --force
```
