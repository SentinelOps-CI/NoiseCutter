SHELL := /bin/bash

.PHONY: all build test clean help sbom audit reach-server reach-worker fuse-server fuse-worker policy-server policy-worker all_artifacts verify-golden golden

BUILD_DIR := ./bin
CMD_DIRS := $(wildcard cmd/*)

all: all_artifacts

build: $(CMD_DIRS)
	@mkdir -p $(BUILD_DIR)
	@for dir in $^; do \
		name=$$(basename $$dir); \
		echo "Building $$name..."; \
		go build -o $(BUILD_DIR)/$$name $$dir; \
	done

test:
	go test ./...

clean:
	rm -rf $(BUILD_DIR) sbom.cdx.json vulns.json reach.server.json reach.worker.json report.server.sarif report.worker.sarif report.server.summary.txt report.worker.summary.txt

sbom:
	syft . -o cyclonedx-json > sbom.cdx.json

audit:
	python -m noisecutter audit --sbom sbom.cdx.json --out vulns.json

reach-server:
	python -m noisecutter reach --lang go --entry ./cmd/server --vulns vulns.json --out reach.server.json || true

reach-worker:
	python -m noisecutter reach --lang go --entry ./cmd/worker --vulns vulns.json --out reach.worker.json || true

fuse-server:
	python -m noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.server.json --out report.server.sarif

fuse-worker:
	python -m noisecutter fuse --sbom sbom.cdx.json --vulns vulns.json --reach reach.worker.json --out report.worker.sarif

policy-server:
	python -m noisecutter policy --sarif report.server.sarif --level high --fail-on reachable || true

policy-worker:
	python -m noisecutter policy --sarif report.worker.sarif --level high --fail-on reachable || true

all_artifacts: sbom audit reach-server reach-worker fuse-server fuse-worker

golden: all_artifacts
	mkdir -p testdata/golden
	cp sbom.cdx.json testdata/golden/
	cp vulns.json testdata/golden/
	cp reach.server.json testdata/golden/
	cp reach.worker.json testdata/golden/
	cp report.server.sarif testdata/golden/
	cp report.worker.sarif testdata/golden/
	cp report.server.summary.txt testdata/golden/
	cp report.worker.summary.txt testdata/golden/

verify-golden: all_artifacts
	diff -u testdata/golden/sbom.cdx.json sbom.cdx.json
	diff -u testdata/golden/vulns.json vulns.json
	diff -u testdata/golden/reach.server.json reach.server.json
	diff -u testdata/golden/reach.worker.json reach.worker.json
	diff -u testdata/golden/report.server.sarif report.server.sarif
	diff -u testdata/golden/report.worker.sarif report.worker.sarif
	diff -u testdata/golden/report.server.summary.txt report.server.summary.txt
	diff -u testdata/golden/report.worker.summary.txt report.worker.summary.txt

help:
	@echo "Targets: build, test, clean, sbom, audit, reach-server, reach-worker, fuse-server, fuse-worker, policy-server, policy-worker, all"


