Contributing
------------

Thanks for your interest in contributing to NoiseCutter.

Getting started
---------------

1) Fork and clone.
2) Create a virtualenv and install dev deps:

```bash
pip install -e .[dev]
pre-commit install
```

3) Verify CLI works locally:

```bash
python -m noisecutter --help
```

Code style
----------

- Python: ruff, black, mypy (strict). Run `pre-commit run -a`.
- Keep functions small, add docstrings for public APIs.

Testing
-------

- Add snapshot tests for converters and SARIF.
- Provide small fixtures for SBOM, OSV, and reachability.

Security
--------

- Avoid shell=True; validate/escape user inputs.
- Record external tool versions in SARIF `tool.driver`.

License
-------

By contributing, you agree that your contributions are licensed under Apache-2.0.


