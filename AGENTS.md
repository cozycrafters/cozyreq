# Agent Guidelines for CozyReq

## Build & Test Commands
- **Dev**: `bun run dev` (Vite only) or `bun run tauri dev` (full Tauri app)
- **Build**: `bun run build` (frontend), `cargo build --manifest-path src-tauri/Cargo.toml` (Rust)
- **Test**: `bun test` (frontend), `cargo test --manifest-path src-tauri/Cargo.toml` (Rust), `uv run pytest` (Python)
- **Single Test**: `bun test -t "test name"` (frontend), `cargo test test_name --manifest-path src-tauri/Cargo.toml` (Rust), `uv run pytest -k test_name` (Python)
- **Lint**: `cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings`, `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`, `uv run ruff check`, `uv run pyright`
- **Format**: `cargo fmt --manifest-path src-tauri/Cargo.toml`, `uv run ruff format`

## Code Style

### TypeScript/SolidJS
- Use **SolidJS** primitives (`createSignal`, `createEffect`, etc.) - no React hooks
- **Strict mode** enabled: all types required, no implicit `any`, no unused vars/params
- Import order: external deps, Tauri API (`@tauri-apps/*`), local modules, CSS/assets
- Use `invoke()` from `@tauri-apps/api/core` for Rust backend calls
- JSX: preserve mode with `jsxImportSource: "solid-js"`, use TailwindCSS + DaisyUI for styling
- Testing: Vitest with `@solidjs/testing-library`, use `render()` and `getByRole()`

### Rust
- **Edition 2024**, stable toolchain with `rustfmt` and `clippy` components
- Use `#[tauri::command]` for functions exposed to frontend
- Format with `rustfmt`, lint with `clippy` (zero warnings policy)
- Error handling: use `Result<T, E>` with `.expect()` and descriptive messages
- Naming: `snake_case` for functions/vars, `PascalCase` for types/structs

### Python
- **Python 3.13+** with `uv` for dependency management (workspace with `packages/` members)
- Format with `ruff format`, lint with `ruff check`, type-check with `pyright`
- Testing: pytest with `uv run pytest`, use descriptive test names with `test_` prefix
- Type hints required for all function signatures
- Naming: `snake_case` for functions/vars/modules, `PascalCase` for classes
