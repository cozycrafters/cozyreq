# Agent Guidelines for CozyReq

## Build & Test Commands
- **Dev**: `bun run dev` (Vite only) or `bun run tauri dev` (full Tauri app)
- **Build**: `bun run build` (frontend), `cargo build --manifest-path src-tauri/Cargo.toml` (Rust)
- **Test**: `bun test` (frontend), `cargo test --manifest-path src-tauri/Cargo.toml` (all Rust tests)
- **Single Test**: `bun test -t "test name"` (frontend), `cargo test test_name --manifest-path src-tauri/Cargo.toml` (Rust)
- **Lint**: `cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings`, `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`
- **Format**: `cargo fmt --manifest-path src-tauri/Cargo.toml`

## Code Style

### TypeScript/SolidJS
- Use **SolidJS** primitives (`createSignal`, `createEffect`, etc.) - no React hooks
- **Strict mode** enabled: all types required, no implicit `any`, no unused vars/params
- Import order: external deps, Tauri API (`@tauri-apps/*`), local modules, CSS/assets
- Use `invoke()` from `@tauri-apps/api/core` for Rust backend calls
- JSX: preserve mode with `jsxImportSource: "solid-js"`, use TailwindCSS for styling
- Testing: Vitest with `@solidjs/testing-library`, use `render()` and `getByRole()`

### Rust
- **Edition 2021**, stable toolchain with `rustfmt` and `clippy` components
- Use `#[tauri::command]` for functions exposed to frontend
- Format with `rustfmt`, lint with `clippy` (zero warnings policy)
- Error handling: use `Result<T, E>` with `.expect()` and descriptive messages
- Naming: `snake_case` for functions/vars, `PascalCase` for types/structs
