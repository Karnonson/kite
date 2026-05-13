# Kite Dev Container Template

These files are scaffolded into a user's project by `install-devcontainer.sh`.
They are the user-facing dev container template for new Kite projects.

## Files

| File                 | Purpose                                                                 |
| -------------------- | ----------------------------------------------------------------------- |
| `Dockerfile`         | Thin base-image wrapper that removes the broken Yarn apt source before features install. |
| `devcontainer.json`  | Editor-neutral dev container definition. Universal image baseline, `KITE_DEV_ENV=1`, and no privileged Docker feature by default. |
| `post-create.sh`     | Runs once on build: installs pipx + Kite CLI; runs `kite init --here` if new. |
| `post-start.sh`      | Runs on every start: marks the workspace as a git safe directory.       |

## Environment variables

Set these in `devcontainer.json` → `remoteEnv` to customize behavior:

| Variable                    | Default    | Effect                                                  |
| --------------------------- | ---------- | ------------------------------------------------------- |
| `KITE_DEV_ENV`              | `1`        | Marks the container as an approved Kite dev environment for `check-dev-environment` guarded actions. |
| `KITE_VERSION`              | *(empty)*  | Pin a specific version of `kite-cli` from the configured package source. |
| `KITE_INSTALL_SPEC`         | `git+https://github.com/Karnonson/kite.git@main` | Package spec used by the generated template. Switch to `kite-cli` after the PyPI release or pin a tag or SHA. |
| `KITE_PNPM_VERSION`         | `10.10.0`  | Version of `pnpm` installed for TypeScript workflows. |
| `KITE_DEFAULT_INTEGRATION`  | `copilot`  | Integration passed to `kite init` on a fresh workspace. Change this before the first build if you use a different agent. |

## Isolation

The generated template is intentionally conservative:

- No Docker-in-Docker feature is enabled by default.
- No host Docker socket is mounted by default.
- No editor-specific extensions or prompt recommendations are required by the scaffold.

## Idempotency

- Kite CLI is reinstalled on every container build (`pipx install --force`).
- `kite init` runs **only** when `.kite/` does not already exist in the
  workspace, so rebuilds preserve your work.

## Adding Docker Access

If you need a Docker daemon inside the container, add the feature explicitly to
`devcontainer.json`:

```json5
"features": {
  "ghcr.io/devcontainers/features/docker-in-docker:2": {
    "version": "latest",
    "moby": true
  }
}
```

That opt-in reduces isolation and can fail on restricted hosts such as browser-
or agent-first IDE environments.
