Go multi-entry sample
=======================

This sample has **two entry points** with different reachability characteristics:

- **`cmd/server`** — HTTP server (`/health`, `/noop`, `/do-risky`)
- **`cmd/worker`** — background-style entry that may exercise different code paths

It is used by CI ([`.github/workflows/pr.yml`](../../.github/workflows/pr.yml)) to build SBOM → audit → reach → fuse outputs and **verify golden files** under `testdata/golden/`.

**Release checklist:** `testdata/golden/` must contain the full set of baseline JSON/SARIF/summary files (not only `.keep`). On Linux or macOS, with Syft and govulncheck installed, run `make golden` once and commit the generated files so `make verify-golden` passes in CI.

Prerequisites
-------------

- Same as the root project: **Python**, **Syft**, **Go**, **govulncheck** (see [`tool-versions.json`](../../tool-versions.json))
- **GNU Make** (Linux/macOS; GitHub Actions uses this sample on ubuntu-latest and macos-latest)

Quickstart
----------

```bash
cd examples/go-multi-entry
make all_artifacts    # sbom -> audit -> reach(server,worker) -> fuse
```

Capture or verify goldens (maintainers):

```bash
make golden          # refresh testdata/golden from current outputs
make verify-golden   # diff against committed goldens
```

Policy example (server report)
------------------------------

```bash
python -m noisecutter policy --sarif report.server.sarif --level high --fail-on reachable
```

Optional: run the HTTP server locally
---------------------------------------

```bash
go run ./cmd/server
```

Then exercise routes (for example `curl` against `/health` or `/do-risky`). This is optional for the NoiseCutter pipeline; the reach step uses **govulncheck** against the entry package, not runtime traffic.

More documentation: [docs/QUICKSTART.md](../../docs/QUICKSTART.md), [docs/INTEGRATIONS.md](../../docs/INTEGRATIONS.md).
