# Installation Guide

## Prerequisites

- **Linux/macOS** (or Windows; PowerShell scripts now supported without WSL)
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Codebuddy CLI](https://www.codebuddy.ai/cli), [Gemini CLI](https://github.com/google-gemini/gemini-cli), or [Pi Coding Agent](https://pi.dev)
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or [pipx](https://pypa.github.io/pipx/) for persistent installation
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## Installation

> **Important:** The only official, maintained packages for Kite come from the [Karnonson/kite](https://github.com/Karnonson/kite) GitHub repository. Any packages with the same name available on PyPI (e.g. `specify-cli` on pypi.org) are **not** affiliated with this project and are not maintained by the Kite maintainers. For normal installs, use the GitHub-based commands shown below. For offline or air-gapped environments, locally built wheels created from this repository are also valid.

### Initialize a New Project

The recommended path is to install `kite` persistently so the CLI is available in every directory after `kite init` (including the new project folder for `kite doctor` / `kite resume`):

```bash
# Persistent install (recommended) — gives you `kite` on PATH everywhere
uv tool install kite-cli --from git+https://github.com/Karnonson/kite.git
kite init <PROJECT_NAME>
```

> [!NOTE]
> `pipx` works equally well for a persistent install:
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

### Specify Integration

You can proactively specify your coding agent integration during initialization:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration claude
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration gemini
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration copilot
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration codebuddy
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --integration pi
```

### Specify Script Type (Shell vs PowerShell)

All automation scripts now have both Bash (`.sh`) and PowerShell (`.ps1`) variants.

Auto behavior:

- Windows default: `ps`
- Other OS default: `sh`
- Interactive mode: you'll be prompted unless you pass `--script`

Force a specific script type:

```bash
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --script sh
uvx --from git+https://github.com/Karnonson/kite.git@vX.Y.Z kite init <project_name> --script ps
```

### Ignore Agent Tools Check

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

- `/kite.specify` - Create specifications
- `/kite.plan` - Generate implementation plans  
- `/kite.tasks` - Break down into actionable tasks

The `.kite/scripts` directory will contain both `.sh` and `.ps1` scripts.

## Troubleshooting

### Enterprise / Air-Gapped Installation

If your environment blocks access to PyPI (you see 403 errors when running `uv tool install` or `pip install`), you can create a portable wheel bundle on a connected machine and transfer it to the air-gapped target.

**Step 1: Build the wheel on a connected machine (same OS and Python version as the target)**

```bash
# Clone the repository
git clone https://github.com/Karnonson/kite.git
cd spec-kit

# Build the wheel
pip install build
python -m build --wheel --outdir dist/

# Download the wheel and all its runtime dependencies
pip download -d dist/ dist/kite_cli-*.whl
```

> **Important:** `pip download` resolves platform-specific wheels (e.g., PyYAML includes native extensions). You must run this step on a machine with the **same OS and Python version** as the air-gapped target. If you need to support multiple platforms, repeat this step on each target OS (Linux, macOS, Windows) and Python version.

**Step 2: Transfer the `dist/` directory to the air-gapped machine**

Copy the entire `dist/` directory (which contains the `specify-cli` wheel and all dependency wheels) to the target machine via USB, network share, or other approved transfer method.

**Step 3: Install on the air-gapped machine**

```bash
pip install --no-index --find-links=./dist specify-cli
```

**Step 4: Initialize a project (no network required)**

```bash
# Initialize a project — no GitHub access needed
kite init my-project --integration claude
```

Bundled assets are used by default — no network access is required.

> **Note:** Python 3.11+ is required.

> **Windows note:** Offline scaffolding requires PowerShell 7+ (`pwsh`), not Windows PowerShell 5.x (`powershell.exe`). Install from https://aka.ms/powershell.

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
