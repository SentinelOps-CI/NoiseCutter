Contributing
============

Thanks for your interest in contributing to NoiseCutter.

Getting started
---------------

1. Fork and clone this repository.
2. Create a virtual environment and install development dependencies:

   ```bash
   pip install -e ".[dev]"
   # or (recommended, matches CI):
   uv sync --extra dev
   pre-commit install
   ```

3. Verify the CLI:

   ```bash
   python -m noisecutter --help
   # with uv:
   uv run noisecutter --help
   ```

Code style
----------

- **Python:** [ruff](https://docs.astral.sh/ruff/) (lint + format), [mypy](https://mypy-lang.org/) (strict). Run `pre-commit run --all-files` before pushing.
- **Spelling:** CI runs [typos](https://github.com/crate-ci/typos) using [`_typos.toml`](_typos.toml). Install the `typos` CLI locally if you want the same check before push.
- **Editor defaults:** [`.editorconfig`](.editorconfig) (indentation, line endings).
- Keep functions focused; add docstrings for public APIs.

Testing
-------

- Run the full suite with coverage:

  ```bash
  uv run pytest tests/ --cov=noisecutter
  ```

- Add **golden** expectations under [`tests/golden/`](tests/golden/) for stable SARIF or JSON outputs.
- Add small **fixtures** under [`tests/fixtures/`](tests/fixtures/) for SBOM, vuln, and reach inputs.

CI workflows
------------

Workflows live in [`.github/workflows/`](.github/workflows/).

| File | Triggers | Purpose |
| ---- | -------- | ------- |
| [`ci.yml`](.github/workflows/ci.yml) | PR/push `main`, `workflow_dispatch` | Python **3.9–3.13**: ruff, mypy, pytest + coverage, typos, pip-audit (locked export) |
| [`pr.yml`](.github/workflows/pr.yml) | PR `main` | Go multi-entry **make** + golden verify (Linux/macOS); Windows pytest smoke |
| [`release.yml`](.github/workflows/release.yml) | Tags `v*.*.*`, `workflow_dispatch` | `uv build`, artifact attestations, PyPI OIDC, GHCR, GitHub Release |
| [`codeql.yml`](.github/workflows/codeql.yml) | PR/push `main`, weekly | CodeQL (Python) |
| [`dependency-review.yml`](.github/workflows/dependency-review.yml) | PR `main` | Dependency review (requires dependency graph where available) |

[Dependabot](.github/dependabot.yml) uses the **uv** ecosystem at the repository root for **`uv.lock`**, plus grouped GitHub Actions updates.

Documentation
-------------

When you change behavior, flags, defaults, or CI:

- Update [README.md](README.md) if user-facing overview changes.
- Update [docs/QUICKSTART.md](docs/QUICKSTART.md) or [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) as appropriate.
- Update [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) if GitHub Actions or third-party CI examples change.
- Summarize user-visible changes in the GitHub release notes when you cut a release.

Security
--------

- Avoid `shell=True`; validate and escape user-controlled paths and inputs.
- Record external tool versions in SARIF where applicable (`tool.driver`).
- Report security issues per [SECURITY.md](SECURITY.md) (private disclosure).

License
-------

By contributing, you agree that your contributions are licensed under Apache-2.0.
