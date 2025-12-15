# Agent Guidelines for CozyReq

## Build/Test Commands
- **Build**: `cargo build`
- **Run**: `cargo run`
- **Test all**: `cargo test`
- **Test single**: `cargo test test_name`
- **Format**: `cargo fmt`
- **Lint**: `cargo clippy -- -D warnings`
- **Format check**: `cargo fmt -- --check`
- **Add dependency**: `cargo add <crate>` (optionally specify version with `@version`)
- **Remove dependency**: `cargo remove <crate>`

## Code Style
- **Edition**: Rust 2024
- **Formatting**: Use `cargo fmt` (standard rustfmt rules)
- **Imports**: Group by std → external crates → crate modules; alphabetical order
- **Types**: Explicit types in struct fields, inference OK in local variables
- **Naming**: snake_case (functions/vars), PascalCase (types/enums), SCREAMING_SNAKE_CASE (constants)
- **Error handling**: Use `color_eyre::Result<T>` for fallible functions; propagate with `?`
- **Documentation**: Doc comments (`///`) for public items, explain "why" not "what"
- **Testing**: Place tests in `#[cfg(test)] mod tests` within same file; name tests descriptively

## Project Structure
- Workspace with crates in `crates/` directory
- Main binary in `crates/cozyreq/src/main.rs`
- TUI logic in `crates/cozyreq/src/tui.rs`
