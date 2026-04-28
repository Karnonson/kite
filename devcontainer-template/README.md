# Kite Dev Container Template

These files are scaffolded into a user's project by `install-devcontainer.sh`.
They are the user-facing dev container template for new Kite projects.

## Files

| File                 | Purpose                                                                 |
| -------------------- | ----------------------------------------------------------------------- |
| `devcontainer.json`  | VS Code dev container definition. Universal image + Docker-in-Docker.  |
| `post-create.sh`     | Runs once on build: installs pipx + Kite CLI; runs `kite init` if new. |
| `post-start.sh`      | Runs on every start: marks the workspace as a git safe directory.       |

## Environment variables

Set these in `devcontainer.json` → `remoteEnv` to customize behavior:

| Variable                    | Default    | Effect                                                  |
| --------------------------- | ---------- | ------------------------------------------------------- |
| `KITE_VERSION`              | *(empty)*  | Pin a specific version of `kite-cli` from the configured package source. |
| `KITE_INSTALL_SPEC`         | `kite-cli` | Package spec for an approved source, such as an internal package name or a pinned git URL. |
| `KITE_PNPM_VERSION`         | `10.10.0`  | Version of `pnpm` installed for TypeScript workflows. |
| `KITE_DEFAULT_INTEGRATION`  | `copilot`  | Integration passed to `kite init` on a fresh workspace. |

## Idempotency

- Kite CLI is reinstalled on every container build (`pipx install --force`).
- `kite init` runs **only** when `.kite/` does not already exist in the
  workspace, so rebuilds preserve your work.

## Disabling Docker-in-Docker

If you don't need Docker inside the container, remove the
`ghcr.io/devcontainers/features/docker-in-docker` block from
`devcontainer.json` — startup will be ~30s faster.
