# Agent Guidelines for CozyReq

## Build/Test/Lint Commands
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

## Code Style
- Python 3.14+ required
- Indentation: 4 spaces for Python, 2 spaces for other files (see .editorconfig)
- Line endings: LF, UTF-8 encoding, final newline required
- Format: Use `ruff format` for automatic formatting
- Linting: Follow `ruff check` recommendations
- Type hints: Required, validated with `ty`
- Imports: Standard library first, then third-party, then local (separated by blank lines)
- Use `typing.override` decorator for overridden methods
- Project structure: Source code in `src/cozyreq/`, tests in `tests/`
- Entry point: `src/cozyreq/cli.py` with `main()` function
- Async tests: Use `pytest-asyncio` (asyncio_mode = "auto" is configured)
