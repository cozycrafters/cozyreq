# Agent Guidelines for CozyReq

This is a **monorepo** with three workspaces:

- **Python (UV)**: Root project + `apps/api/`
- **TypeScript (Bun)**: `apps/web/`
- **Rust (Cargo)**: `apps/cli/`

## Root-Level Commands

All quality and testing commands can be run from the project root:

### Bun (TypeScript)

- Test: `bun run test`
- Lint: `bun run lint`
- Format: `bun run fmt`
- Format check: `bun run fmt:check`
- Type check: `bun run type-check`

### UV (Python)

- Test: `pytest`
- Lint: `ruff check`
- Format: `ruff format`
- Format check: `ruff format --check`
- Type check: `ty check`

### Cargo (Rust)

- Test: `cargo test`
- Lint: `cargo lint`
- Format: `cargo format`
- Format check: `cargo format-check`
- Type check: `cargo type-check`

## Python Commands (UV)

### Root Project

- Install dependencies: `uv sync`
- Add dependency: `uv add <package>` (or `uv add --dev <package>` for dev deps)
- Remove dependency: `uv remove <package>`
- Run app: `cozyreq` (or `uv run cozyreq`)
- Run tests: `pytest`
- Run single test: `pytest tests/path/to/test_file.py::test_function_name`
- Format check: `ruff format --check`
- Format fix: `ruff format`
- Lint: `ruff check`
- Type check: `ty check`
- Docs: `uv zensical serve` (opens at localhost:8000)

### Apps/API (FastAPI)

- Install dependencies: `uv sync --project apps/api`
- Add dependency: `uv add --project apps/api <package>`
- Run dev server: `fastapi dev src/main.py` (in apps/api directory)

## TypeScript Commands (Bun)

### Apps/Web (Next.js)

- Install dependencies: `bun install` (from root)
- Run dev server: `bun run dev` (in apps/web directory) or `mise run dev:web`
- Build: `bun run build` (in apps/web directory)
- Start production: `bun run start` (in apps/web directory)
- Lint: `bun run lint`
- Format: `bun run fmt`
- Format check: `bun run fmt:check`
- Type check: `bun run type-check`

### Root (Workspace Management)

- Install all deps: `bun install`
- Add workspace dev dependency: Add to root `package.json` devDependencies

## Rust Commands (Cargo)

### Apps/CLI

- Fetch dependencies: `cargo fetch --manifest-path apps/cli/Cargo.toml`
- Build: `cargo build --manifest-path apps/cli/Cargo.toml`
- Build release: `cargo build --release --manifest-path apps/cli/Cargo.toml`
- Run: `cargo run --manifest-path apps/cli/Cargo.toml`
- Run tests: `cargo test`
- Lint: `cargo lint`
- Format: `cargo format`
- Format check: `cargo format-check`
- Type check: `cargo type-check`

## Mise Tasks (Cross-Language)

### Development

- `mise run dev` - Start all services (Supabase + API + web) in parallel
- `mise run dev:web` - Start Next.js only
- `mise run dev:api` - Start FastAPI only
- `mise run dev:cli` - Build and run CLI

### Database

- `mise run db:start` - Start Supabase
- `mise run db:stop` - Stop Supabase
- `mise run db:reset` - Reset Supabase database

### Testing & Quality (Root Level)

- `mise run test` - Run all test suites (bun + pytest + cargo)
- `mise run lint` - Run all linters (oxlint + ruff + clippy)
- `mise run format` - Run all formatters (oxfmt + ruff + rustfmt)

### Setup

- `mise run setup` - Initial project setup

## Code Style

### Python

- Python 3.14+ required
- Indentation: 4 spaces
- Format: Use `ruff format`
- Linting: Follow `ruff check` recommendations
- Type hints: Required, validated with `ty`
- Imports: Standard library first, then third-party, then local (separated by blank lines)
- Use `typing.override` decorator for overridden methods
- Async tests: Use `pytest-asyncio` (asyncio_mode = "auto" is configured)

### TypeScript

- Indentation: 2 spaces
- Format: Use `oxfmt`
- Linting: Use `oxlint`
- Use strict TypeScript configuration
- Prefer functional components in React

### Rust

- Indentation: 4 spaces (default rustfmt)
- Format: Use `cargo fmt`
- Linting: Use `cargo clippy` with `-D warnings`
- Follow Rust naming conventions (snake_case for functions, CamelCase for types)
- Use `?` operator for error handling

### General

- Line endings: LF, UTF-8 encoding, final newline required
- Project structure: See README.md for monorepo layout
- Entry points:
  - Python: `src/cozyreq/cli.py` with `main()` function
  - TypeScript: `apps/web/app/page.tsx` (Next.js)
  - Rust: `apps/cli/src/main.rs` with `main()` function

## Issue Tracking

- This project uses **Linear** for issue tracking
