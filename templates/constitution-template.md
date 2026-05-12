# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: Verification required for code changes; depth adapts to project/framework; failing checks caused by the change must be fixed before completion -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Accessibility by Default -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: User-facing features must support keyboard access, visible focus, readable contrast, clear labels, clear error messages, and non-color-only signaling -->

### VI. Subagent-First Execution

Parent agents MUST delegate focused research, artifact scanning, contract review, codebase evidence gathering, and validation evidence to bounded subagents before widening their own context. Parent agents remain the final writers of durable artifacts, workflow state, and product code. Browser validation is frontend-owned: only `kite.frontend` may invoke `kite.browser`, and only as a focused subagent after a connected frontend slice exists.
<!-- Add any additional project-specific principle here, such as Observability, Official Docs First for AI Work, or Rationale-Focused Comments. AI-agent work should verify official docs, version guidance, and MCP/skills support before implementation. -->

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, Host Safety Rules, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, official-doc requirements for AI work, verified MCP/skills support expectations, host-environment safety rules, etc. -->

## Agent Collaboration Rules
<!-- Example: Development Workflow, Agent Collaboration Rules, Review Process, Quality Gates, etc. -->

Parent agents MUST use subagent-first execution for bounded official-doc research, artifact scans, contract review, codebase evidence gathering, and validation evidence when an installed Kite subagent can keep the work smaller. Parent agents reconcile the returned evidence and remain the only final writers for their owned artifacts, state updates, and product code.

Frontend-owned browser validation is mandatory. `kite.frontend` may invoke `kite.browser` as a focused subagent after a connected frontend slice exists. QA and all other agents consume `browser-report.md` and MUST NOT invoke browser tooling directly.

[SECTION_3_CONTENT]
<!-- Add project-specific review process, quality gates, deployment approval process, or other collaboration rules here. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Project-wide workflow rules belong here rather than only in downstream prompts; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
