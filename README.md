# Cozy API

Let AI agents interact with your API.

## Prerequisites

Install the following prerequisites:

- [Rust](https://www.rust-lang.org)
- [mise](https://mise.jdx.dev)

You can easily install the dependencies:

```bash
mise install
npm install
uv sync
```

## Usage

Add a `.env` file with development config:

```
DATABASE_FILE=~/config/dev.cozyapi/data.db
```

Run the application locally:

```bash
mise run dev:app
```

Run MCP server with inspector:

```bash
mise run dev:mcp
```
