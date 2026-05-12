# CLI Reference

The Kite CLI (`kite`) helps non-technical builders initialize a project, connect an AI coding agent, and move through the software lifecycle with guided commands, helper commands, and install profiles.

## Core Commands

The foundational commands for creating and managing Kite projects. Initialize a new project with the necessary directory structure, templates, and scripts. Verify that your system has the required tools installed. Check version and system information.

Includes `kite profile` commands for viewing and changing the active install profile (`minimal` / `standard` / `full`).

[Core Commands reference →](core.md)

## Workflows

The built-in founder workflow runs constitution -> discover -> specify -> design -> clarify -> plan -> tasks -> analyze -> task gate -> backend -> contract gate -> frontend -> docs -> qa. The `minimal` profile installs that guided flow plus `kite.analyze`, `kite.browser`, and `kite.checklist`. The default `standard` profile adds `kite.research`.

`kite.browser` is a frontend-only helper used after a connected frontend slice. `kite.analyze` is the required consistency pass before the task gate and backend implementation.

[Workflows reference →](workflows.md)

## Integrations

Integrations connect Kite to your AI coding agent. Each integration sets up the appropriate command files, context rules, and directory structures for a specific agent. Only one integration is active per project at a time, and you can switch between them at any point.

[Integrations reference →](integrations.md)

## Extensions

Extensions add optional commands and domain-specific capabilities on top of the built-in guided workflow.

[Extensions reference →](extensions.md)

## Presets

Presets let teams replace or override templates, commands, and terminology without forking Kite itself.

[Presets reference →](presets.md)
