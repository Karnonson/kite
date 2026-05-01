# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `__KITE_COMMAND_PLAN__` command. See `.kite/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**AI SDK / Agent Framework**: [e.g., none, Mastra, Google ADK, Vercel AI SDK or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing/Verification**: [required; e.g., pytest, XCTest, cargo test, browser smoke flow, framework-native validation, or NEEDS CLARIFICATION]  
**Deployment/Hosting**: [e.g., Vercel, Fly.io, Cloud Run, self-hosted or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (__KITE_COMMAND_PLAN__ command output)
├── research.md          # Phase 0 output (__KITE_COMMAND_PLAN__ command)
├── data-model.md        # Phase 1 output (__KITE_COMMAND_PLAN__ command)
├── quickstart.md        # Phase 1 output (__KITE_COMMAND_PLAN__ command)
├── contracts/           # Phase 1 output (__KITE_COMMAND_PLAN__ command)
└── tasks.md             # Phase 2 output (__KITE_COMMAND_TASKS__ command - NOT created by __KITE_COMMAND_PLAN__)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Approved Source Layout

<!--
  ACTION REQUIRED: Replace this section with the exact repository paths that
  implementation tasks may create or edit. The __KITE_COMMAND_TASKS__ command
  MUST keep every code, test, docs, and ops task inside this approved layout.

  Choose one structure and delete unused examples. Framework-native layouts are
  allowed only when this section explains why (for example, a single Next.js app
  may use app/, lib/, and prisma/ at the repository root because it is one
  framework-native project). Full-stack multi-surface apps should prefer grouped
  roots such as apps/web, apps/api, packages/shared, tests/e2e, and docs.
-->

```text
[approved-root-or-file]/
├── [approved-child]/
└── [approved-child]/
```

**Layout rationale**: [Why this layout fits the feature and framework]

**Allowed write roots**:

- `[path]` — [owner/persona and purpose]

**Framework-native exceptions**: [N/A or explain why root-level framework folders are approved]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
