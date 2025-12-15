<!--
  SYNC IMPACT REPORT
  ==================
  Version Change: 1.0.0 → 1.1.0 → 1.2.0 → 1.3.0
  
  Changes in 1.3.0:
  Added Principles:
    - VI. Documentation Currency: Requires user-facing documentation in docs/ to be
      maintained and updated alongside code changes
  
  Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section already dynamic
  ✅ .specify/templates/spec-template.md - Structure agnostic, no changes needed
  ✅ .specify/templates/tasks-template.md - Polish phase includes "Documentation updates in docs/"
  ✅ AGENTS.md - No changes needed (does not reference specific principles)
  
  Follow-up TODOs: None
  
  Rationale for Version 1.3.0 (MINOR):
  - Adds new principle (VI. Documentation Currency)
  - Establishes mandatory documentation maintenance requirements
  - Aligns with existing UX and transparency principles
  - Does not remove or redefine existing principles
  
  Changes in 1.2.0:
  Modified Principles: None (constitution already correct)
  Modified Templates:
    - plan-template.md: Clarified Python module in project root (not src/)
    - tasks-template.md: Changed all paths from src/ to projectname/
  
  Changes in 1.1.0:
  Modified Principles:
    - II. Testing Standards: Added co-location requirement for test files
  
  Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Reflects Python module at root with co-located tests
  ✅ .specify/templates/tasks-template.md - All paths use projectname/ instead of src/
  ✅ .specify/templates/spec-template.md - No changes needed (structure agnostic)
  ✅ AGENTS.md - No changes needed (does not specify structure)
-->

# CozyReq Constitution

## Core Principles

### I. Code Quality & Maintainability

All code MUST meet high standards of quality, clarity, and maintainability. This ensures
the long-term health and evolution of the CozyReq codebase.

**Rules:**
- Type hints are REQUIRED for all functions and methods (enforced by Pyright)
- Code MUST pass linting (Ruff) and formatting checks before commit
- Functions and public APIs MUST include docstrings explaining purpose, parameters, and return values
- Imports MUST follow PEP 8 ordering: standard library, third-party, local
- Naming conventions MUST be followed: snake_case for functions/variables, PascalCase for classes
- Error handling MUST use specific exceptions; bare except clauses are prohibited
- Indentation MUST use 4 spaces for Python, 2 spaces for other files
- All files MUST end with a newline and use LF line endings
- Code complexity MUST be justified; simpler alternatives must be explored first

**Rationale:** Quality code reduces bugs, simplifies onboarding, and enables confident
refactoring. Type safety catches errors at development time rather than runtime.
Consistent formatting eliminates bikeshedding and merge conflicts.

### II. Testing Standards

Testing is MANDATORY to ensure correctness and prevent regressions. Tests provide
executable documentation and enable confident changes.

**Rules:**
- New features MUST include tests (unit, integration, or contract as appropriate)
- Tests MUST be written BEFORE implementation when test-driven development is appropriate
- All tests MUST pass before merging to main branch
- Tests MUST be run via `uv run pytest` and integrated into CI
- Test files MUST follow naming convention: `test_*.py` or `*_test.py`
- Test files MUST be co-located with the code they test (NOT in separate directories)
- Tests MUST be clear, focused, and test one thing at a time
- Flaky tests MUST be fixed or removed; they cannot be ignored
- Test coverage should be monitored but 100% coverage is NOT a goal; focus on critical paths

**Test Organization:**
```
cozyreq/
├── models/
│   ├── user.py
│   └── test_user.py          # Co-located with user.py
├── services/
│   ├── api.py
│   └── test_api.py           # Co-located with api.py
└── tui.py
    └── test_tui.py           # Co-located with tui.py
```

**Rationale:** Tests catch bugs early, document behavior, and enable fearless refactoring.
The CI integration ensures no broken code reaches main. Test-first development clarifies
requirements and prevents over-engineering. Co-locating tests with code improves
discoverability, reduces cognitive overhead when navigating the codebase, and makes it
easier to ensure tests exist for every module.

### III. User Experience Consistency

CozyReq MUST provide a consistent, intuitive, and delightful user experience that makes
interacting with APIs through AI agents seamless and predictable.

**Rules:**
- Terminal UI (TUI) interactions MUST be responsive and feel instantaneous where possible
- Error messages MUST be clear, actionable, and guide users toward solutions
- User interactions MUST be consistent across features (e.g., keyboard shortcuts, navigation)
- The application MUST provide clear feedback for all user actions
- Loading states MUST be shown for operations that take more than 100ms
- The UI MUST gracefully handle edge cases (empty states, errors, network issues)
- Design changes MUST be evaluated against existing patterns before introducing new ones
- Accessibility MUST be considered: keyboard navigation, screen reader support where feasible

**Rationale:** Users develop mental models of how software works. Consistency reduces
cognitive load and learning time. Clear feedback builds trust. A well-designed UX
differentiates great tools from merely functional ones.

### IV. Local-First Architecture

CozyReq MUST prioritize local-first principles: user data lives primarily on the user's
device, the application works offline, and users retain full ownership and control.

**Rules:**
- The primary copy of data MUST reside on the user's local device
- All core features MUST work without network connectivity
- Network operations MUST be asynchronous and never block the user interface
- Local data MUST be readable and modifiable without requiring external services
- The application MUST start instantly without waiting for network checks
- Data synchronization (if added) MUST happen in the background without user intervention
- Users MUST be able to export their data in standard, readable formats
- The application MUST never depend on external services for basic functionality

**Local-First Ideals (from Ink & Switch):**
1. **No spinners:** Work is at your fingertips; local operations are instantaneous
2. **Multi-device:** Data syncs across devices (future consideration)
3. **Offline-first:** Network is optional, not required
4. **Collaboration:** Support for collaboration without sacrificing ownership (future)
5. **Longevity:** Data outlives the application; standard formats ensure accessibility
6. **Privacy:** Data stays local; no unnecessary transmission to servers
7. **User control:** Users own their data and can manipulate it freely

**Rationale:** Cloud-centric applications take ownership away from users. Local-first
software respects user autonomy, works reliably in any network condition, and ensures
data longevity. Users can trust that their work is safe and accessible.

### V. Data Ownership & Privacy

Users MUST have complete ownership and control over their data. CozyReq MUST NOT
compromise user privacy or transmit data without explicit user consent.

**Rules:**
- User data MUST be stored locally on the user's filesystem
- File formats MUST be human-readable or easily exportable (JSON, YAML, SQLite, etc.)
- The application MUST NOT send analytics, telemetry, or user data to external servers
- If external services are used, users MUST provide explicit configuration (API keys, endpoints)
- Users MUST be able to inspect, modify, and delete their data files directly
- Credentials and secrets MUST be stored securely (encrypted at rest)
- Documentation MUST clearly explain what data is stored and where

**Rationale:** Privacy is a fundamental right. Users should not have to trust a company
to protect their data — they should control it directly. Transparent data storage builds
trust and enables power users to automate and customize.

### VI. Documentation Currency

User-facing documentation in the `docs/` directory MUST be maintained and updated to
accurately reflect the current state of the application, its features, and usage patterns.

**Rules:**
- Documentation updates MUST accompany feature additions, modifications, or removals
- The `docs/` directory MUST contain accurate, up-to-date user guides and references
- Documentation MUST be written in clear, accessible language for the target audience
- Breaking changes or significant feature updates MUST be documented before release
- Examples and code snippets in documentation MUST be tested and verified
- Deprecated features MUST be clearly marked in documentation with migration guidance
- Documentation MUST include getting started guides, core concepts, and common workflows
- Screenshots, diagrams, or visual aids MUST be updated when UI/UX changes occur

**Rationale:** Outdated documentation erodes user trust and creates frustration. Users
rely on documentation to learn, troubleshoot, and maximize value from the tool.
Maintaining documentation alongside code ensures it remains a reliable source of truth
and reduces support burden. Good documentation is a force multiplier for adoption and
user satisfaction.

## Development Workflow

### Continuous Integration

All changes MUST pass the following checks before merging:
- `uv run ruff format --check` (formatting validation)
- `uv run ruff check` (linting validation)
- `uv run pyright` (type checking)
- `uv run pytest` (test execution)

These checks are enforced automatically in GitHub Actions on all pull requests to main.

### Code Review

- Pull requests MUST be reviewed before merging
- Reviewers MUST verify compliance with constitution principles
- Breaking changes MUST be explicitly flagged and justified
- Reviewers should ask: "Is there a simpler way to achieve this?"

### Development Process

- Install dependencies: `mise install && uv sync`
- Add new dependencies: `uv add <package>` (or `uv add --dev <package>` for dev)
- Run locally: `python main.py`
- Fix linting issues: `uv run ruff check --fix`
- Python version: 3.14+

## Governance

### Constitutional Authority

This constitution defines the non-negotiable principles for CozyReq development. All
decisions — architectural, implementation, and design — MUST align with these principles.

### Amendment Process

Amendments to this constitution require:
1. A written proposal explaining the change and rationale
2. Review and discussion among maintainers
3. Consensus approval from project maintainers
4. Version increment following semantic versioning rules
5. Update to dependent templates and documentation

### Compliance

- All pull requests and code reviews MUST verify compliance with constitutional principles
- Violations MUST be justified with documented rationale in complexity tracking
- Reviewers MUST challenge unjustified complexity or principle violations
- The constitution supersedes all other development practices and conventions

### Versioning

Constitution versions follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR:** Backward-incompatible changes, principle removals, or redefinitions
- **MINOR:** New principles added or material expansions to existing principles
- **PATCH:** Clarifications, wording improvements, typo fixes, non-semantic changes

**Version**: 1.3.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
