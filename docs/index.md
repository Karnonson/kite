# Kite

*Build software with AI agents, even if you are not a developer.*

Kite helps non-technical builders turn an idea into working software by guiding an AI coding agent through constitution, discovery, specification, design, clarification, planning, task generation, consistency analysis, implementation, docs, and QA in plain English.

## What is Spec-Driven Development?

Kite uses Spec-Driven Development as its operating model, but packages it as a guided workflow for builders who want a clear loop instead of tooling ceremony. The spec is an active asset that drives design, planning, tasks, and implementation.

## Getting Started

- [Installation Guide](installation.md)
- [Dev Container Guide](devcontainer.md)
- [Quick Start Guide](quickstart.md)
- [Upgrade Guide](upgrade.md)

## Guided Workflow

The default founder-friendly flow runs constitution -> discover -> specify -> design -> clarify -> plan -> tasks -> analyze -> task gate -> backend -> contract gate -> frontend -> docs -> qa.

The `minimal` profile installs the guided workflow plus the required helpers `kite.analyze`, `kite.browser`, and `kite.checklist`. The default `standard` profile adds `kite.research`. `kite.browser` is a frontend-only validation helper that `kite.frontend` can invoke after a connected slice.

## Core Philosophy

Kite's workflow emphasizes:

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## Development Phases

| Phase | Focus | Key Activities |
|-------|-------|----------------|
| **0-to-1 Development** ("Greenfield") | Generate from scratch | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration** | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul> |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul> |

## Support

For support, please search existing GitHub issues and discussions first, or review the [Support Guide](https://github.com/Karnonson/kite/blob/main/SUPPORT.md) before opening a new issue.
