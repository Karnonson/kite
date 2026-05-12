# Installation Guide

## Choose an Install Path

For most non-technical builders, use the dev container. It installs Kite
inside a ready VS Code workspace and avoids manual Python, Node, and Docker
setup on your computer.

If you are comfortable with command-line tools, install Kite directly with
`uv` or `pipx` instead.

## Option 1: Install the Dev Container

### What you need first

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or a
  compatible Docker engine
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Create the container files

Open a terminal in the folder where you want to build your app, then run:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
```

Then:

1. Open the folder in VS Code.
2. Run **Dev Containers: Reopen in Container** from the Command Palette.
3. Wait for the build to finish.

Kite installs automatically and initializes the workspace with the default
`copilot` integration. When the container is ready, open Copilot Chat and
run:

```text
/kite.start "Build a tool that helps me <describe your idea>."
```

For more details, see the [Dev Container Guide](devcontainer.md).

## Option 2: Install Kite Directly

### Prerequisites

- **Linux**
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Codebuddy CLI](https://www.codebuddy.ai/cli), [Gemini CLI](https://github.com/google-gemini/gemini-cli), or [Pi Coding Agent](https://pi.dev)
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or [pipx](https://pypa.github.io/pipx/) for persistent installation
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Installation

> **Important:** The only official, maintained Kite builds come from the [Karnonson/kite](https://github.com/Karnonson/kite) GitHub repository. Similar or legacy package names on PyPI are **not** affiliated with this project and are not maintained by the Kite maintainers. For normal installs, use the GitHub-based commands shown below. For offline or air-gapped environments, locally built wheels created from this repository are also valid.

#### Initialize a New Project

The recommended path is to install `kite` persistently so the CLI is available in every directory after `kite init` (including the new project folder for `kite doctor` / `kite resume`):

```bash
# Persistent install (recommended) — gives you `kite` on PATH everywhere
uv tool install kite-cli --from git+https://github.com/Karnonson/kite.git
kite init <PROJECT_NAME>
```

> [!NOTE]
> `pipx` works equally well for a persistent install:
>
> ```bash
> pipx install git+https://github.com/Karnonson/kite.git
> ```

If you only want to scaffold a single project and don't need the CLI afterwards, you can run a one-shot init via `uvx`:

```bash
# One-shot — leaves no `kite` binary behind; `kite doctor` / `kite resume` won't work in the new dir
uvx --from git+https://github.com/Karnonson/kite.git kite init <PROJECT_NAME>
```

Or initialize in the current directory:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init .
# or use the --here flag
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init --here
```

#### Specify Integration

You can proactively specify your coding agent integration during initialization:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration claude
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration gemini
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration copilot
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration codebuddy
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration pi
```

#### Specify Script Type

Use Bash scripts for the currently supported Linux setup:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --script sh
```

#### Ignore Agent Tools Check

If you prefer to get the templates without checking for the right tools:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration claude --ignore-agent-tools
```

## Verification

After installation, run the following command to confirm the correct version is installed:

```bash
kite version
```

This helps verify you are running the official Kite build from GitHub, not an unrelated package with the same name.

After initialization, you should see the following commands available in your coding agent:

- `/kite.constitution` - Establish project principles
- `/kite.discover` - Frame the problem and user need
- `/kite.specify` - Create specifications
- `/kite.design` - Create design and design-system artifacts
- `/kite.clarify` - Resolve missing decisions before planning
- `/kite.plan` - Generate implementation plans
- `/kite.tasks` - Break down into actionable tasks
- `/kite.analyze` - Run the required consistency pass before implementation
- `/kite.backend` - Implement backend tasks and publish the frontend contract
- `/kite.frontend` - Implement frontend tasks against the published contract
- `/kite.docs` - Update user-facing documentation
- `/kite.qa` - Run QA tasks and append a plain-English report

Standard installs also include helper commands such as `/kite.browser`, `/kite.checklist`, and `/kite.research`.

The `.kite/scripts` directory will contain both `.sh` and `.ps1` scripts.

## Troubleshooting

### Enterprise / Air-Gapped Installation

If your environment blocks access to PyPI (you see 403 errors when running `uv tool install` or `pip install`), you can create a portable wheel bundle on a connected machine and transfer it to the air-gapped target.

**Step 1: Build the wheel on a connected machine (same OS and Python version as the target)**

```bash
# Clone the repository
git clone https://github.com/Karnonson/kite.git
cd kite

# Build the wheel
pip install build
python -m build --wheel --outdir dist/

# Download the wheel and all its runtime dependencies
pip download -d dist/ dist/kite_cli-*.whl
```

> **Important:** `pip download` resolves platform-specific wheels (e.g., PyYAML includes native extensions). You must run this step on a Linux machine with the **same Python version** as the air-gapped target.

**Step 2: Transfer the `dist/` directory to the air-gapped machine**

Copy the entire `dist/` directory (which contains the `kite-cli` wheel and all dependency wheels) to the target machine via USB, network share, or other approved transfer method.

**Step 3: Install on the air-gapped machine**

```bash
pip install --no-index --find-links=./dist kite-cli
```

**Step 4: Initialize a project (no network required)**

```bash
# Initialize a project — no GitHub access needed
kite init my-project --integration claude
```

Bundled assets are used by default — no network access is required.

> **Note:** Python 3.11+ is required.

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux, you can install Git Credential Manager:

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```
