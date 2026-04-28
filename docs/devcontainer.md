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
/kite.implement
```

For most new projects, start with `/kite.start` and let Kite walk you
through the full flow.

## What you get

- Base image: `mcr.microsoft.com/devcontainers/universal:2-linux`
  (Python 3.11, Node 22 LTS, Git, GitHub CLI pre-installed).
- Docker-in-Docker support, so generated apps can use Docker from inside the
  container without exposing your host socket.
- `pnpm` installed globally for TypeScript projects.
- `kite-cli` installed via `pipx` on every build.
- GitHub Copilot and Copilot Chat extensions recommended in VS Code.

## What gets re-created on rebuild

| Item                        | Behavior on container rebuild                  |
| --------------------------- | ---------------------------------------------- |
| Kite CLI (`pipx`)           | Re-installed.                                  |
| `pnpm`                      | Re-installed.                                  |
| `.kite/` workspace          | **Preserved.** `kite init` runs only when it's missing. |

## Optional settings

Most users do not need to change these. If you do, edit
`.devcontainer/devcontainer.json` → `remoteEnv`:

| Variable                    | Effect                                                  |
| --------------------------- | ------------------------------------------------------- |
| `KITE_VERSION`              | Pin a Kite version. |
| `KITE_INSTALL_SPEC`         | Install Kite from a specific package source or git URL. |
| `KITE_PNPM_VERSION`         | Pin the `pnpm` version. |
| `KITE_DEFAULT_INTEGRATION`  | Default `kite init` integration. Defaults to `copilot`. |

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
