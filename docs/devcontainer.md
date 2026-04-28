# Kite Dev Container

Run Kite inside an isolated Linux dev container so the agent never touches
your host system. Recommended when you want a reproducible workspace, when
your host can't install Python/Node easily, or when you'd rather keep AI
tooling sandboxed.

> **The standard install paths (`uv tool install kite-cli`, `pipx install
> kite-cli`) remain fully supported.** The dev container is purely opt-in.

## One-line install

From the directory you want to set up:

```bash
curl -fsSL https://raw.githubusercontent.com/Karnonson/kite/main/scripts/install-devcontainer.sh | bash
```

That writes a `.devcontainer/` folder with three files. Then in VS Code:

1. Open the folder.
2. Run **Dev Containers: Reopen in Container** (Command Palette).
3. Wait for the build. Kite is installed automatically; on a fresh
  workspace `kite init --force --integration copilot` runs once.

## What you get

- Base image: `mcr.microsoft.com/devcontainers/universal:2-linux`
  (Python 3.11, Node 22 LTS, Git, GitHub CLI pre-installed).
- **Docker-in-Docker** feature — full Docker access from inside the
  container without exposing your host socket.
- A pinned `pnpm` version installed globally for TypeScript workflows.
- `kite-cli` installed via `pipx` from the configured package source on every build.

## What gets re-created on rebuild

| Item                        | Behavior on container rebuild                  |
| --------------------------- | ---------------------------------------------- |
| Kite CLI (`pipx`)           | Re-installed (`pipx install --force`).         |
| `pnpm` (`npm -g`)           | Re-installed.                                  |
| `.kite/` workspace          | **Preserved.** `kite init` runs only when it's missing. |

## Customize

Edit `.devcontainer/devcontainer.json` → `remoteEnv`:

| Variable                    | Effect                                                  |
| --------------------------- | ------------------------------------------------------- |
| `KITE_VERSION`              | Pin a version of `kite-cli` from the configured package source. |
| `KITE_INSTALL_SPEC`         | Package spec for an approved source, such as `kite-cli` from an internal index or a pinned git URL. |
| `KITE_PNPM_VERSION`         | Version of `pnpm` installed for TypeScript workflows. |
| `KITE_DEFAULT_INTEGRATION`  | Default `kite init` integration. Defaults to `copilot`. |

## Bootstrap script flags

```bash
curl -fsSL .../install-devcontainer.sh | bash -s -- [flags]
```

| Flag             | Default | Description                                       |
| ---------------- | ------- | ------------------------------------------------- |
| `--force`        | off     | Replace an existing `.devcontainer/`.             |
| `--ref REF`      | `main`  | Git ref to fetch templates from.                  |
| `--dest DIR`     | `.`     | Destination workspace directory.                  |
| `--help`         |         | Show usage.                                       |

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

## Validating end-to-end (maintainers)

The repo ships a smoke script that builds the container with the
[`devcontainer` CLI](https://github.com/devcontainers/cli), runs the full
post-create flow, and asserts that Kite installs, `kite init` runs once,
and Docker-in-Docker works:

```bash
npm install -g @devcontainers/cli   # one-time
tests/smoke/smoke-devcontainer.sh
```

Set `KEEP=1` to retain the temporary workspace for inspection on success.
