# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

Python tooling for Lantmäteriet.

## Commands

- `uv run pytest` — run Python tests
- `uv run ruff check .` — lint Python
- `uv run ruff format .` — format Python
- `uv run mypy src tests` — type-check Python in `src/` and `tests/`

## Rules

- Never commit, push, or create branches.
  Leave all changes in the working tree; the user commits.
- Never run destructive commands (`rm -rf`, `git reset --hard`, force-push).
- Do not modify files under `dist/`.
- Never edit `.env` or commit secrets.
- Before finishing a task, run the relevant checks from Commands and report results.

## Conventions

- Python: follow ruff configuration in `pyproject.toml`; format with ruff-format.
- Markdown: lint with markdownlint.
- Keep each sentence on its own line; do not break sentences to fit a line length.
- Pre-commit hooks (ruff, mypy, markdownlint) run on commit —
  run `pre-commit run --all-files` before pushing.
- Do not commit directly to `main`; open a pull request.
- Keep PRs small and focused; describe the change, not the process.
