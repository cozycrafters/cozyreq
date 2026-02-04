# Agent Guidelines for CozyReq

This is a **monorepo** with three workspaces:
- **Python (UV)**: Root project + `apps/api/`
- **TypeScript (Bun)**: `apps/web/`
- **Rust (Cargo)**: `apps/cli/`

## Python Commands (UV)

### Root Project
- Install dependencies: `uv sync`
- Add dependency: `uv add <package>` (or `uv add --dev <package>` for dev deps)
- Remove dependency: `uv remove <package>`
- Run app: `cozyreq` (or `uv run cozyreq`)
- Run tests: `uv run pytest`
- Run single test: `uv run pytest tests/path/to/test_file.py::test_function_name`
- Format check: `uv run ruff format --check`
- Format fix: `uv run ruff format`
- Lint: `uv run ruff check`
- Type check: `uv run ty check`
- Docs: `uv zensical serve` (opens at localhost:8000)

### Apps/API (FastAPI)
- Install dependencies: `uv sync --project apps/api`
- Add dependency: `uv add --project apps/api <package>`
- Run dev server: `uv run --project apps/api uvicorn src.main:app --reload --port 8000`
- Run tests: `uv run --project apps/api pytest`
- Format check: `uv run --project apps/api ruff format --check`
- Format fix: `uv run --project apps/api ruff format`
- Lint: `uv run --project apps/api ruff check`
- Type check: `uv run --project apps/api ty check`

## TypeScript Commands (Bun)

### Apps/Web (Next.js)
- Install dependencies: `bun install` (from root)
- Run dev server: `bun run --cwd apps/web dev` or `mise run dev:web`
- Build: `bun run --cwd apps/web build`
- Start production: `bun run --cwd apps/web start`
- Lint (oxlint): `bun run --cwd apps/web lint`
- Format (oxfmt): `bun run --cwd apps/web format`
- Type check: `bun run --cwd apps/web type-check`

### Root (Workspace Management)
- Install all deps: `bun install`
- Add workspace dev dependency: Add to root `package.json` devDependencies

## Rust Commands (Cargo)

### Apps/CLI
- Fetch dependencies: `cargo fetch --manifest-path apps/cli/Cargo.toml`
- Build: `cargo build --manifest-path apps/cli/Cargo.toml`
- Build release: `cargo build --release --manifest-path apps/cli/Cargo.toml`
- Run: `cargo run --manifest-path apps/cli/Cargo.toml`
- Run tests: `cargo test --manifest-path apps/cli/Cargo.toml`
- Lint (clippy): `cargo clippy --manifest-path apps/cli/Cargo.toml -- -D warnings`
- Format: `cargo fmt --manifest-path apps/cli/Cargo.toml`
- Check formatting: `cargo fmt --manifest-path apps/cli/Cargo.toml -- --check`

## Mise Tasks (Cross-Language)

### Development
- `mise run dev` - Start all services (Supabase + FastAPI + Next.js)
- `mise run dev:web` - Start Next.js only
- `mise run dev:api` - Start FastAPI only
- `mise run dev:cli` - Build and run CLI

### Database
- `mise run db:start` - Start Supabase
- `mise run db:stop` - Stop Supabase
- `mise run db:reset` - Reset Supabase database
- `mise run db:migrate` - Run Supabase migrations

### Testing
- `mise run test` - Run all test suites
- `mise run test:web` - Run Next.js tests
- `mise run test:api` - Run FastAPI tests
- `mise run test:cli` - Run Rust CLI tests

### Quality
- `mise run lint` - Run all linters (oxlint, ruff, clippy)
- `mise run format` - Run all formatters (oxfmt, ruff format, rustfmt)

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
