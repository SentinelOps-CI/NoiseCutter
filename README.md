<p align="center">
  <img src="docs/assets/noisecutter-hero.svg" alt="NoiseCutter hero" width="820" />
</p>

NoiseCutter - Prove what’s exploitable; ignore the rest
======================================================

Mission: Cut vuln noise to near-zero by proving which CVEs are actually callable from your app’s entry points, using open CLIs, reproducible SBOMs, and CI-first workflows.

Quickstart
----------

Install:

```bash
pip install noisecutter
```

Windows note: If the console shim misbehaves, prefer `python -m noisecutter`.

Fast path (repo SBOM → audit → reach → SARIF → policy):

```bash
python -m noisecutter sbom --source . --out sbom.cdx.json
python -m noisecutter audit --sbom sbom.cdx.json --out vulns.json
python -m noisecutter reach --lang go --entry ./examples/go-mod-sample/cmd/server \
  --vulns vulns.json --out reach.json
python -m noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.json --out report.sarif
python -m noisecutter policy --sarif report.sarif --level high --fail-on reachable
```

Go recipe prerequisites:
- Go toolchain installed
- `govulncheck` installed: `go install golang.org/x/vuln/cmd/govulncheck@latest`
- In example module, run once: `cd examples/go-mod-sample && go mod tidy`

Windows specifics:
- Ensure `syft` is on PATH or set `SYFT_EXE=C:\path\to\syft.exe`
- If you hit encoding issues, set `set PYTHONIOENCODING=utf-8` and `chcp 65001`

Reproducibility
---------------

Deterministic outputs (golden-friendly):
- Set `NOISECUTTER_STRICT_REPRO=1` and optionally `SOURCE_DATE_EPOCH`.
- Pin tool versions (see `tool-versions.json`).

Multi-entry Go sample
---------------------

```bash
cd examples/go-multi-entry
make all_artifacts   # sbom -> audit -> reach(server,worker) -> fuse
# First time to capture goldens
make golden
# Later to verify
make verify-golden
```

Config and logging
------------------

- Global flags: `--log-level`, `--repo`, `--strict-repro`
- Config file: `.noisecutter.yaml` supports sbom/audit/reach/fuse/policy, cache, concurrency, timeouts
- Logging: env `NOISECUTTER_LOGGING_CONFIG`, `NOISECUTTER_LOG_FILE`, `NOISECUTTER_LOG_JSON`

CI usage
--------

See `ci/pr-fastpath.yml` for a PR fast-path. Recommended steps:
- Generate SBOM with syft
- Audit with OSV
- Reachability with language-native tooling (e.g., govulncheck for Go)
- Fuse to SARIF and upload
- Enforce policy: fail only on reachable HIGH/CRITICAL

Docs
----

- `docs/QUICKSTART.md`: step-by-step setup
- `docs/WHY_REACHABILITY.md`: concepts and rationale
- `docs/THREAT_MODEL.md`: risks and mitigations
- `docs/EXCEPTION_PLAYBOOK.md`: policy exceptions
- `docs/TROUBLESHOOTING.md`: syft/govulncheck and Windows tips

License: Apache-2.0


