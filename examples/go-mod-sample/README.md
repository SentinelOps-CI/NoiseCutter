Go sample (single entry)
=========================

This example is a **minimal Go module** with an HTTP entry point under `cmd/server`. Use it to try the NoiseCutter pipeline end-to-end: SBOM, OSV audit, **govulncheck** reachability, SARIF fuse, and policy.

Prerequisites
-------------

- Go toolchain and this repo’s **NoiseCutter** CLI installed (`pip` or `uv`; see root [README.md](../../README.md))
- **Syft** on `PATH` (or `SYFT_EXE` on Windows)
- **govulncheck** pinned per [`tool-versions.json`](../../tool-versions.json), for example:

  ```bash
  go install golang.org/x/vuln/cmd/govulncheck@v1.2.0
  ```

Setup
-----

```bash
cd examples/go-mod-sample
go mod tidy
```

Typical commands
----------------

From the **NoiseCutter repository root** (paths match the main [README.md](../../README.md) quickstart):

```bash
noisecutter sbom --source . --out sbom.cdx.json
noisecutter audit --sbom sbom.cdx.json --out vulns.json
noisecutter reach --lang go --entry ./examples/go-mod-sample/cmd/server --vulns vulns.json --out reach.json
noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.json --out report.sarif
noisecutter policy --sarif report.sarif --level high --fail-on reachable
```

If you run from **inside** `examples/go-mod-sample`, adjust `--source` and file paths accordingly.

See also [docs/TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) for govulncheck and Windows notes.
