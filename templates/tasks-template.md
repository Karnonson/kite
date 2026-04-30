---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped into tracer-bullet phases so each phase can be verified on its own before the next one starts. When both backend and frontend are in scope, tasks are split into separate backend and frontend sections so each agent can stay within its lane.

## Format: `[ID] [P?] [Story] [Persona] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **[Persona]**: Which Kite persona owns this task — one of `[backend]`, `[frontend]`, `[qa]`, `[docs]`, `[ops]`. The persona commands (`kite.backend`, `kite.frontend`, `kite.qa`) filter `tasks.md` by this tag. Every task gets exactly one persona label.
- Include exact file paths in descriptions
- Verification tasks must include the command or validation flow that proves the phase works

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The __KITE_COMMAND_TASKS__ command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story and tracer-bullet phase so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  - Verified before the next phase begins

  For projects with both backend and frontend work:
  - Split backend and frontend tasks into separate subsections
  - Do not create mixed-ownership tasks
  - End each subsection with an explicit verification task
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [ops] Create project structure per implementation plan in backend/, frontend/, and tests/
- [ ] T002 [backend] Initialize the backend project skeleton in backend/ with the chosen framework entrypoint
- [ ] T003 [frontend] Initialize the frontend project skeleton in frontend/ with the chosen framework entrypoint
- [ ] T004 [P] [ops] Configure shared linting and formatting tools in .editorconfig, backend/, and frontend/
- [ ] T005 [ops] Verify the project boots with the setup commands documented in specs/[###-feature-name]/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T006 [backend] Setup database schema and migrations framework in backend/
- [ ] T007 [P] [backend] Implement authentication/authorization framework in backend/src/
- [ ] T008 [P] [backend] Setup API routing and middleware structure in backend/src/
- [ ] T009 [frontend] Create the shared API client shell in frontend/src/lib/ so later screens can consume the contract consistently
- [ ] T010 [ops] Configure environment configuration management in .env.example, backend/, and frontend/
- [ ] T011 [backend] Verify foundational backend behavior in the terminal or the framework's integrated dev environment

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Backend Slice for User Story 1

- [ ] T012 [P] [US1] [backend] Create [Entity1] model in backend/src/models/[entity1].py
- [ ] T013 [US1] [backend] Implement [Service] in backend/src/services/[service].py
- [ ] T014 [US1] [backend] Update specs/[###-feature-name]/contract.md for [endpoint/feature]

### Backend Verification for User Story 1

- [ ] T015 [US1] [backend] Verify the story 1 backend slice in the terminal with [command] or in the framework dev environment / studio with [validation flow]

### Frontend Slice for User Story 1

- [ ] T016 [P] [US1] [frontend] Build [screen/component] in frontend/src/[location]/[file].tsx
- [ ] T017 [US1] [frontend] Wire the story 1 data flow in frontend/src/lib/[feature].ts using the published contract

### Frontend Verification for User Story 1

- [ ] T018 [US1] [frontend] Verify the story 1 UI in the browser or component test runner with [command or manual smoke flow]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US1] [qa] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T020 [P] [US1] [qa] Integration test for [user journey] in tests/integration/test_[name].py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Backend Slice for User Story 2

- [ ] T021 [P] [US2] [backend] Create [Entity] model in backend/src/models/[entity].py
- [ ] T022 [US2] [backend] Implement [Service] in backend/src/services/[service].py

### Backend Verification for User Story 2

- [ ] T023 [US2] [backend] Verify the story 2 backend slice in the terminal or framework dev environment with [command / flow]

### Frontend Slice for User Story 2

- [ ] T024 [US2] [frontend] Implement [screen/feature] in frontend/src/[location]/[file].tsx

### Frontend Verification for User Story 2

- [ ] T025 [US2] [frontend] Verify the story 2 UI in the browser or component test runner with [command or flow]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T026 [P] [US2] [qa] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T027 [P] [US2] [qa] Integration test for [user journey] in tests/integration/test_[name].py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Backend Slice for User Story 3

- [ ] T028 [P] [US3] [backend] Create [Entity] model in backend/src/models/[entity].py
- [ ] T029 [US3] [backend] Implement [Service] in backend/src/services/[service].py

### Backend Verification for User Story 3

- [ ] T030 [US3] [backend] Verify the story 3 backend slice in the terminal or framework dev environment with [command / flow]

### Frontend Slice for User Story 3

- [ ] T031 [US3] [frontend] Implement [screen/feature] in frontend/src/[location]/[file].tsx

### Frontend Verification for User Story 3

- [ ] T032 [US3] [frontend] Verify the story 3 UI in the browser or component test runner with [command or flow]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T033 [P] [US3] [qa] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T034 [P] [US3] [qa] Integration test for [user journey] in tests/integration/test_[name].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] [docs] Documentation updates in docs/
- [ ] TXXX [backend] Code cleanup and refactoring in backend/
- [ ] TXXX [frontend] Code cleanup and refactoring in frontend/
- [ ] TXXX [P] [qa] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX [ops] Security hardening across backend/ and frontend/
- [ ] TXXX [ops] Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories until its verification task passes
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Work inside a user-story phase should respect the tracer-bullet order: backend slice → backend verification → frontend slice → frontend verification → QA / acceptance
  - Later user-story phases should not begin until the current phase is verified
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) verification - No dependencies on other stories
- **User Story 2 (P2)**: Starts after User Story 1 verification unless the plan explicitly proves it is independent
- **User Story 3 (P3)**: Starts after earlier verified phases unless the plan explicitly proves it is independent

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Backend tasks complete before backend verification
- Backend verification passes before frontend tasks for the same slice rely on that work
- Frontend verification passes before the phase is marked complete
- Story complete before moving to the next priority phase

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once a phase's verification gate passes, the next approved phase can start
- All tests for a user story marked [P] can run in parallel
- Backend tasks within a story marked [P] can run in parallel
- Frontend tasks within a story marked [P] can run in parallel
- Different personas can work in parallel only when the current phase marks those tasks `[P]` and the verification gate is not skipped

---

## Parallel Example: User Story 1

```bash
# Launch backend build tasks for User Story 1 together:
Task: "Create [Entity1] model in backend/src/models/[entity1].py"
Task: "Implement [supporting repository] in backend/src/repositories/[name].py"

# After backend verification passes, launch frontend build tasks for User Story 1 together:
Task: "Build [screen/component] in frontend/src/[location]/[file].tsx"
Task: "Wire story 1 API client in frontend/src/lib/[feature].ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational and run its verification task
3. Complete Phase 3 backend slice
4. **STOP and VALIDATE**: Run the backend verification task
5. Complete Phase 3 frontend slice
6. **STOP and VALIDATE**: Run the frontend / acceptance verification task
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → verify the foundation works
2. Add User Story 1 backend → verify in terminal or framework dev environment
3. Add User Story 1 frontend → verify in browser / component test flow → Deploy/Demo
4. Repeat the same tracer-bullet pattern for User Story 2 and User Story 3
5. Each phase adds value without breaking previously verified slices

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. For each user-story phase, Developer A takes the `[backend]` tasks for the current phase
3. For each user-story phase, Developer B takes the `[frontend]` tasks that are marked ready after backend verification
4. For each user-story phase, Developer C takes the `[qa]` coverage and acceptance tasks
5. Do not start the next phase until the current phase verification tasks pass

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- [Persona] label tells the owning agent which tasks it may execute
- Each user story should be independently completable and testable
- Each phase must end with an explicit verification task before the next phase starts
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, mixed backend/frontend ownership, cross-story dependencies that break independence
