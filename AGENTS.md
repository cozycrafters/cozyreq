# Agent Guidelines for CozyReq

## Setup
- Install dependencies: `mise install && uv sync`
- Add new dependencies: `uv add <package>` (or `uv add --dev <package>` for dev dependencies)
- Python version: 3.13+

## Build/Lint/Test Commands
- Format check: `uv run ruff format --check`
- Format code: `uv run ruff format`
- Lint: `uv run ruff check`
- Lint with auto-fix: `uv run ruff check --fix`
- Type check: `uv run pyright`
- Run all tests: `uv run pytest`
- Run single test: `uv run pytest path/to/test_file.py::test_function_name`

## Code Style
- **Indentation**: 4 spaces for Python, 2 spaces for other files (per .editorconfig)
- **Line endings**: LF only
- **Formatting**: Use Ruff (enforced in CI)
- **Type hints**: Required - Pyright type checking is enabled
- **Imports**: Follow PEP 8 ordering (stdlib, third-party, local)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Use for public APIs and complex functions
- **Error handling**: Prefer specific exceptions over bare except clauses
- **Dependencies**: Managed via uv, specified in pyproject.toml
- **Charset**: UTF-8 with final newline in all files

## Workflow
- All changes must pass: ruff format check, ruff check, pyright, and pytest
- CI runs these checks automatically on PRs to main branch
- Fix linting issues with `uv run ruff check --fix` before committing
