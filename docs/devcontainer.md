# Kite Dev Container

The dev container is the easiest way to start with Kite. It gives you a
ready Linux workspace with Python, Node, Git, and the Kite CLI already
installed. The scaffold sticks to an isolated `.devcontainer/` baseline so it
can be opened from Dev Container-capable, VS Code-style IDEs without requiring
privileged Docker features in the container by default.

## What you need first

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or a
  compatible Docker engine
- A Dev Container-capable editor based on VS Code, such as VS Code,
  VSCodium, Cursor, Windsurf, or a similar IDE that supports
  `.devcontainer/devcontainer.json`
- The matching Dev Container support for your editor

## Install in an empty project folder

Open a terminal in the folder where you want to build your app, then run:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
```

This creates a `.devcontainer/` folder. Then:

1. Open the folder in your editor.
2. Use that editor's command to open or reopen the folder in the dev
  container.
3. Wait for the container build to finish.

On the first build, Kite installs automatically and initializes the
workspace with the default `copilot` integration. If you want a different
integration, change `KITE_DEFAULT_INTEGRATION` in
`.devcontainer/devcontainer.json` before the first build. When the build
completes, use the command format for the integration you selected. With the
default `copilot` integration, start with:

```text
/kite.start "Build a tool that helps me <describe your idea>."
```

Kite will guide you through the next steps in plain English.

## Install into another folder

Use `--dest` when you want the script to create or update a different
project folder:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash -s -- --dest ./my-app
```

Then open the folder in your editor and use its dev container command.

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

In your AI coding assistant, use the Kite commands for the integration you
selected. With the default `copilot` integration, they look like this:

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
- An isolated default: no host Docker socket and no Docker-in-Docker feature
  are enabled unless you add them yourself.
- Ports started by tools inside the container are not opened automatically. Use
  your editor's port forwarding UI when you want to expose a generated app
  preview.
- `pnpm` installed globally for TypeScript projects.
- `kite-cli` installed via `pipx` on every build from `KITE_INSTALL_SPEC`, which defaults to `git+https://github.com/Karnonson/kite.git@main` in the scaffolded template until Kite is published to PyPI.
- `KITE_DEV_ENV=1` exported inside the container so Kite's `check-dev-environment` guard treats the dev container as an approved environment for package installs, Docker commands, and other host-affecting actions.
- Dev container editor sessions run as the built-in `codespace` user, and the template leaves `updateRemoteUserUID` disabled by default to avoid server-attach ownership failures seen on some Linux hosts.
- No editor-specific extensions are forced by the scaffold. Install the ones
  your chosen integration needs in your own editor profile.

## What gets re-created on rebuild

| Item                        | Behavior on container rebuild                  |
| --------------------------- | ---------------------------------------------- |
| Kite CLI (`pipx`)           | Re-installed.                                  |
| `pnpm`                      | Re-installed.                                  |
| `.kite/` workspace          | **Preserved.** `kite init` runs only when it's missing. |

## Optional settings

Most users do not need to change these. If you do, edit
`.devcontainer/devcontainer.json` → `remoteEnv`:

If you change `remoteUser`, `containerUser`, or `updateRemoteUserUID`, rebuild
the container instead of just reopening it. On Linux, re-enabling
`updateRemoteUserUID` can help when your host UID does not match the
container's `codespace` user, but it also reintroduces the UID-rewrite path
that this template avoids by default.

| Variable                    | Default in template                                      | Effect |
| --------------------------- | -------------------------------------------------------- | ------ |
| `KITE_DEV_ENV`             | `1`                                                      | Marks the dev container as an approved Kite environment for environment-guarded commands. |
| `KITE_VERSION`             | *(empty)*                                                | Pin a Kite version. |
| `KITE_INSTALL_SPEC`        | `git+https://github.com/Karnonson/kite.git@main`         | Install Kite from a specific package source or git URL. Switch to `kite-cli` after the PyPI release or pin a tag or SHA here. |
| `KITE_PNPM_VERSION`        | `10.10.0`                                                | Pin the `pnpm` version. |
| `KITE_DEFAULT_INTEGRATION` | `copilot`                                                | Default `kite init` integration. Change it before the first build if you use a different agent. |

## Optional Docker access

The default template does not expose a Docker daemon inside the container. If
your generated app really needs in-container Docker, opt in by adding the
following feature to `.devcontainer/devcontainer.json`:

```json5
"features": {
  "ghcr.io/devcontainers/features/docker-in-docker:2": {
    "version": "latest",
    "moby": true
  }
}
```

This weakens isolation and can fail on restricted hosts such as Antigravity or
other cloud IDE environments.

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
