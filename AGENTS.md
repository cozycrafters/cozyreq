# Agent Instructions

## Commands
- **Build**: `cargo build`
- **Lint**: `cargo clippy -- -D warnings`
- **Format**: `cargo fmt`
- **Test**: `cargo test` (Single: `cargo test <test_name>`)

## Code Style
- **Conventions**: Follow standard Rust 2021 edition idioms.
- **Formatting**: Strictly adhere to `rustfmt`.
- **Linting**: Ensure code passes `clippy` with no warnings.
- **Imports**: Group imports by crate; std first, then external, then internal.
- **Error Handling**: Use `Result` and `?` operator. Avoid `unwrap()` unless in tests.
- **Naming**: `snake_case` for variables/functions, `CamelCase` for types/traits.
