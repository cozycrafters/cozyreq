# CozyReq

Let AI agents interact with your API.

## Prerequisites

Install the following prerequisites:

- [mise](https://mise.jdx.dev)

You can easily install the dependencies:

```bash
mise trust
mise install
mise run setup
```

## Project Structure

This is a **monorepo** with a workspace-based architecture supporting three languages:

```
cozyreq/
├── apps/
│   ├── web/              # Next.js app (TypeScript/Bun)
│   │   ├── package.json
│   │   └── app/          # Next.js app directory
│   ├── api/              # FastAPI app (Python/UV)
│   │   ├── pyproject.toml
│   │   └── src/
│   └── cli/              # Rust CLI (Cargo)
│       ├── Cargo.toml
│       └── src/
├── package.json          # Bun workspace root
├── Cargo.toml            # Cargo workspace root
├── pyproject.toml        # UV workspace root
├── mise.toml             # Task runner configuration
└── supabase/             # Supabase local development
```

### Workspace Management

- **Bun Workspace**: Root `package.json` manages `apps/web`
- **Cargo Workspace**: Root `Cargo.toml` manages `apps/cli`
- **UV Workspace**: Root `pyproject.toml` manages `apps/api`

## Development

### Quick Start

Start all services (Supabase + FastAPI + Next.js) in parallel:

```bash
mise run dev
```

### Individual Services

Start specific services only:

```bash
# Web (Next.js)
mise run dev:web

# API (FastAPI)
mise run dev:api

# CLI (Rust)
mise run dev:cli
```

### Database

Manage Supabase local development:

```bash
# Start Supabase
mise run db:start

# Stop Supabase
mise run db:stop

# Reset database (useful for testing)
mise run db:reset

# Run migrations
mise run db:migrate
```

## Testing & Quality

All testing and quality commands work from the project root:

```bash
# Run all test suites (bun test + uv run test + cargo test)
mise run test

# Run all linters (oxlint + ruff + clippy)
mise run lint

# Run all formatters (oxfmt + ruff format + rustfmt)
mise run format

# Check all formatting
mise run format_check

# Run all type checks (tsc + ty + cargo check)
mise run type_check
```

### Package Manager Commands

You can also run commands directly with each package manager:

**Bun (TypeScript):**
- `bun run test` - Run tests (oxlint)
- `bun run lint` - Run linter
- `bun run format` - Run formatter
- `bun run type-check` - Run type check

**UV (Python):**
- `uv run test` - Run tests (pytest)
- `uv run lint` - Run linter (ruff)
- `uv run format` - Run formatter (ruff)
- `uv run format_check` - Check formatting
- `uv run type_check` - Run type check (ty)

**Cargo (Rust):**
- `cargo test` - Run tests
- `cargo lint` - Run linter (clippy)
- `cargo format` - Run formatter
- `cargo format-check` - Check formatting
- `cargo type-check` - Run type check

## Environment Variables

The following environment variables are required. Values for Supabase can be obtained by running `supabase status` after starting the local development stack.

### Supabase Configuration

- `SUPABASE_URL` - Supabase API URL (from `supabase status`)
- `SUPABASE_ANON_KEY` - Supabase anonymous key (from `supabase status`)
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key (from `supabase status`)

### Authentication

- `JWT_SECRET` - Shared JWT secret for authentication between Web and API

### Service Configuration

- `API_PORT` - FastAPI server port (default: 8000)
- `WEB_URL` - Next.js app URL (default: http://localhost:3000)
- `NEXT_PUBLIC_API_URL` - Public API URL for frontend (default: http://localhost:8000)
- `NEXT_PUBLIC_SUPABASE_URL` - Public Supabase URL for frontend (from `supabase status`)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Public Supabase key for frontend (from `supabase status`)

To get Supabase values after starting:
```bash
supabase status
```

## Setup

Initial project setup:

```bash
mise run setup
```

This will:
1. Install all dependencies (bun, cargo, uv)
2. Initialize Supabase
3. Set up environment files

### Documentation

To run the documentation locally:

```bash
uv zensical serve
```

Open [localhost:8000](http://localhost:8000) in your browser.

## Technology Stack

| Component | Language | Package Manager | Framework |
|-----------|----------|-----------------|-----------|
| Web       | TypeScript | Bun           | Next.js   |
| API       | Python   | UV            | FastAPI   |
| CLI       | Rust     | Cargo         | Clap      |
| Auth      | -        | Supabase      | Magic Link (no sign-up) |
