# Kite Dev Container

The dev container is the easiest way to start with Kite. It gives you a
ready Linux workspace with Python, Node, Git, Docker, GitHub Copilot for VS
Code, and the Kite CLI already installed. Use it when you do not want to
set up developer tools on your computer by hand.

## What you need first

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or a
  compatible Docker engine
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Install in an empty project folder

Open a terminal in the folder where you want to build your app, then run:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
```

This creates a `.devcontainer/` folder. Then:

1. Open the folder in VS Code.
2. Run **Dev Containers: Reopen in Container** (Command Palette).
3. Wait for the container build to finish.

On the first build, Kite installs automatically and initializes the
workspace with the default `copilot` integration. When the build completes,
open Copilot Chat and run:

```text
/kite.start "Build a tool that helps me <describe your idea>."
```

Kite will guide you through the next steps in plain English.

## Install into another folder

Use `--dest` when you want the script to create or update a different
project folder:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash -s -- --dest ./my-app
code ./my-app
```

Then run **Dev Containers: Reopen in Container** from VS Code.

## Reinstall or replace the container files

If `.devcontainer/` already exists and you want Kite to replace it:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash -s -- --force
```

Your `.kite/` folder and app files are not deleted by this command.

## Use Kite after the container starts

Inside the container terminal, these commands are available:

```bash
kite version
kite doctor
kite resume
```

In your AI coding assistant, use the Kite commands:

```text
/kite.start "Build a simple booking app for a small salon."
/kite.specify "Add appointment reminders by email."
/kite.plan
/kite.tasks
/kite.analyze
# approve the task gate
/kite.backend
# contract gate must pass
/kite.frontend
/kite.docs
/kite.qa
```

On the default `standard` profile, Copilot also gets helper commands such as `/kite.browser`, `/kite.checklist`, and `/kite.research`. `kite.browser` is frontend-only and is usually invoked from `/kite.frontend` after a connected slice rather than as a top-level workflow step.

For most new projects, start with `/kite.start` and let Kite walk you
through the full flow.

## What you get

- Base image: `mcr.microsoft.com/devcontainers/universal:2-linux`
  (Python 3.11, Node 22 LTS, Git, GitHub CLI pre-installed).
- Docker-in-Docker support, so generated apps can use Docker from inside the
  container without exposing your host socket.
- Ports started by tools inside the container are not opened automatically. Use
  the VS Code Ports view when you want to expose a generated app preview.
- `pnpm` installed globally for TypeScript projects.
- `kite-cli` installed via `pipx` on every build from `KITE_INSTALL_SPEC`, which defaults to `git+https://github.com/Karnonson/kite.git@main` in the scaffolded template until Kite is published to PyPI.
- `KITE_DEV_ENV=1` exported inside the container so Kite's `check-dev-environment` guard treats the dev container as an approved environment for package installs, Docker commands, and other host-affecting actions.
- GitHub Copilot and Copilot Chat extensions recommended in VS Code, with prompt recommendations enabled for guided workflow commands and helpers such as `/kite.analyze`, `/kite.browser`, `/kite.checklist`, `/kite.docs`, and `/kite.research`.

## What gets re-created on rebuild

| Item                        | Behavior on container rebuild                  |
| --------------------------- | ---------------------------------------------- |
| Kite CLI (`pipx`)           | Re-installed.                                  |
| `pnpm`                      | Re-installed.                                  |
| `.kite/` workspace          | **Preserved.** `kite init` runs only when it's missing. |

## Optional settings

Most users do not need to change these. If you do, edit
`.devcontainer/devcontainer.json` → `remoteEnv`:

| Variable                    | Default in template                                      | Effect |
| --------------------------- | -------------------------------------------------------- | ------ |
| `KITE_DEV_ENV`             | `1`                                                      | Marks the dev container as an approved Kite environment for environment-guarded commands. |
| `KITE_VERSION`             | *(empty)*                                                | Pin a Kite version. |
| `KITE_INSTALL_SPEC`        | `git+https://github.com/Karnonson/kite.git@main`         | Install Kite from a specific package source or git URL. Switch to `kite-cli` after the PyPI release or pin a tag or SHA here. |
| `KITE_PNPM_VERSION`        | `10.10.0`                                                | Pin the `pnpm` version. |
| `KITE_DEFAULT_INTEGRATION` | `copilot`                                                | Default `kite init` integration. |

## Security note

`curl ... | bash` runs whatever the URL serves. If you'd rather inspect
first:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh -o install-devcontainer.sh
less install-devcontainer.sh
bash install-devcontainer.sh
```

Pin a specific commit by passing `--ref <sha>` (the SHA is what the script
uses to fetch the matching template files).

## Removing it

```bash
rm -rf .devcontainer
```

Your `.kite/` workspace is untouched.
