# CozyReq

Let AI agents interact with your API.

## Prerequisites

Install the following prerequisites:

- [mise](https://mise.jdx.dev)

You can easily install development environment:

```bash
mise trust
mise install
```

Install dependencies:

```bash
bun install
uv sync --all-packages
```

Start local database:

```bash
supabase start
```

## Development

### Quick Start

Start all services (API + web) in parallel:

```bash
mise run dev
```

## Testing & Quality

All testing and quality commands work from the project root:

```bash
# Run all test suites
mise run test

# Run all linters
mise run lint

# Run all formatters
mise run format
```

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
- `WEB_URL` - Web app URL (default: <http://localhost:3000>)
- `NEXT_PUBLIC_API_URL` - Public API URL for frontend (default: <http://localhost:8000>)
- `NEXT_PUBLIC_SUPABASE_URL` - Public Supabase URL for frontend (from `supabase status`)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Public Supabase key for frontend (from `supabase status`)

To get Supabase values after starting:

```bash
supabase status
```

## Documentation

To run the documentation locally:

```bash
zensical serve
```

Open [localhost:8000](http://localhost:8000) in your browser.
