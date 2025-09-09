Quickstart
---------

Prerequisites:
- Python 3.9+
- syft installed and on PATH (or set `SYFT_EXE`)
- Optional: govulncheck for Go reachability

Install:

```bash
pip install noisecutter
```

Run fast-path on a repo:

```bash
python -m noisecutter sbom --source . --out sbom.cdx.json
python -m noisecutter audit --sbom sbom.cdx.json --out vulns.json
python -m noisecutter reach --lang go --entry ./examples/go-mod-sample/cmd/server --vulns vulns.json --out reach.json
python -m noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.json --out report.sarif
python -m noisecutter policy --sarif report.sarif --level high --fail-on reachable

Multi-entry Go sample:

```bash
cd examples/go-multi-entry
make all_artifacts
# snapshot goldens once
make golden
# verify on subsequent runs
make verify-golden
```
```


