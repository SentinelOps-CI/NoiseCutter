SHELL := /bin/bash

.PHONY: sbom audit reach fuse policy

sbom:
	syft . -o cyclonedx-json > sbom.cdx.json

audit:
	noisecutter audit --sbom sbom.cdx.json --out vulns.json

reach:
	noisecutter reach --lang go --entry ./cmd/server --vulns vulns.json --out reach.json || true

fuse:
	noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.json --out report.sarif

policy:
	noisecutter policy --sarif report.sarif --level high --fail-on reachable || true


