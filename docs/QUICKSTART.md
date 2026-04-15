Quickstart
==========

Prerequisites
-------------

- **Python** 3.9 through 3.13 (see `requires-python` in `pyproject.toml`).
- **Syft** on `PATH`, or set `SYFT_EXE` to the binary. Prefer a [checksum-verified install](../scripts/install-syft.sh) (see `tool-versions.json` for the pinned Syft version).
- **Optional (Go reachability):** `govulncheck` — install with a pinned tag, for example:

  ```bash
  go install golang.org/x/vuln/cmd/govulncheck@v1.2.0
  ```

  See `tool-versions.json` for the recommended version.

Install NoiseCutter
-------------------

Using pip:

```bash
pip install noisecutter
```

Using uv (matches CI and `uv.lock`):

```bash
uv sync --extra dev
# CLI: uv run noisecutter --help
```

Run the fast path on a repository
----------------------------------

From the NoiseCutter repo root (or your project root with the CLI on `PATH`):

```bash
python -m noisecutter sbom --source . --out sbom.cdx.json
python -m noisecutter audit --sbom sbom.cdx.json --out vulns.json
python -m noisecutter reach --lang go --entry ./examples/go-mod-sample/cmd/server --vulns vulns.json --out reach.json
python -m noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.json --out report.sarif
python -m noisecutter policy --sarif report.sarif --level high --fail-on reachable
```

Multi-entry Go sample
---------------------

```bash
cd examples/go-multi-entry
make all_artifacts
# Capture golden outputs once (for maintainers / CI fixtures)
make golden
# Verify later
make verify-golden
```

Reproducibility
---------------

- Set `NOISECUTTER_STRICT_REPRO=1` (and optionally `SOURCE_DATE_EPOCH`) for deterministic JSON where supported.
- Pin external tools using `tool-versions.json` and the same tags in CI.

Further reading
---------------

- [INTEGRATIONS.md](INTEGRATIONS.md) — GitHub Actions, GitLab, Jenkins
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Syft, govulncheck, Windows, OSV
- [WHY_REACHABILITY.md](WHY_REACHABILITY.md) — concepts
- [THREAT_MODEL.md](THREAT_MODEL.md) — risks and mitigations
- [EXCEPTION_PLAYBOOK.md](EXCEPTION_PLAYBOOK.md) — policy exceptions
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — development setup and tests
- [../SECURITY.md](../SECURITY.md) — vulnerability reporting
