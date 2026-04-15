Integrations
============

This page summarizes how NoiseCutter fits into CI/CD and how to wire external systems safely.

GitHub Actions (continuous integration)
---------------------------------------

**[`ci.yml`](../.github/workflows/ci.yml)** (pull requests and pushes to `main`, plus manual `workflow_dispatch`):

- Matrix: Python **3.9, 3.11, 3.12, 3.13**
- **`uv sync --frozen --extra dev`** then **ruff** (lint + format check), **mypy**, **pytest** with coverage
- **[typos](https://github.com/crate-ci/typos)** spell check (config: [`_typos.toml`](../_typos.toml))
- **[pip-audit](https://pypi.org/project/pip-audit/)** on an exported locked dependency list (`uv export` with `--no-emit-project`)

**[`pr.yml`](../.github/workflows/pr.yml)** (PR fast path):

- **Ubuntu / macOS:** installs Syft via [`scripts/install-syft.sh`](../scripts/install-syft.sh), pins **govulncheck** per `tool-versions.json`, runs `examples/go-multi-entry` **make** targets and **verify-golden**
- **Windows:** Python test suite (no GNU `make` in that job)
- Uploads SARIF from the Go sample on Linux for PR annotations

**[`codeql.yml`](../.github/workflows/codeql.yml)** — CodeQL analysis for Python on `main` and PRs (scheduled weekly as well).

**[`dependency-review.yml`](../.github/workflows/dependency-review.yml)** — [Dependency review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review) on pull requests (requires a usable dependency graph in GitHub for your manifests).

GitHub Actions (release)
------------------------

See **[`release.yml`](../.github/workflows/release.yml)**. On **version tags** it:

- Builds the wheel and sdist with **`uv build`**
- **[Artifact attestations](https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds)** for `dist/*` (public repos; verify with `gh attestation verify`, see GitHub CLI docs)
- Publishes to **PyPI** using [trusted publishing (OIDC)](https://docs.pypi.org/trusted-publishers/)
- Builds and pushes a **Docker** image to **GHCR** using `GITHUB_TOKEN`

Repository automation
---------------------

- **[`dependabot.yml`](../.github/dependabot.yml)** — **uv** lockfile updates at the repo root plus grouped **GitHub Actions** updates (see [Contributing](../CONTRIBUTING.md) for the workflow index).

GitLab CI (example)
-------------------

Install Syft using a **checksum-verified** release asset (see `scripts/install-syft.sh` in this repo), or the equivalent inline steps below. Do not pipe remote install scripts into `sh`.

```yaml
stages: [fastpath]

fastpath:
  image: python:3.12
  stage: fastpath
  before_script:
    - pip install noisecutter
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      set -eux
      SYFT_VERSION=1.16.0
      BASE="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}"
      curl -fsSL "${BASE}/syft_${SYFT_VERSION}_checksums.txt" -o /tmp/syft.sum
      curl -fsSL "${BASE}/syft_${SYFT_VERSION}_linux_amd64.tar.gz" -o /tmp/syft.tgz
      EXPECTED="$(awk -v a="syft_${SYFT_VERSION}_linux_amd64.tar.gz" '$2==a {print $1; exit}' /tmp/syft.sum)"
      echo "${EXPECTED}  /tmp/syft.tgz" | sha256sum -c -
      tar -xzf /tmp/syft.tgz -C /usr/local/bin syft
  script:
    - cd examples/go-multi-entry
    - make all_artifacts
    - make verify-golden
  artifacts:
    when: always
    paths:
      - examples/go-multi-entry/report.*.sarif
```

Jenkins (example)
-----------------

Declarative pipeline snippet (ensure `bin/` stays on `PATH` for later stages, for example via `environment { PATH = "$WORKSPACE/bin:$PATH" }`):

```groovy
pipeline {
  agent any
  environment {
    PATH = "$WORKSPACE/bin:$PATH"
  }
  stages {
    stage('Setup') {
      steps {
        sh '''
          set -eux
          pip install noisecutter
          SYFT_VERSION=1.16.0
          BASE="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}"
          mkdir -p bin
          curl -fsSL "${BASE}/syft_${SYFT_VERSION}_checksums.txt" -o syft.sum
          curl -fsSL "${BASE}/syft_${SYFT_VERSION}_linux_amd64.tar.gz" -o syft.tgz
          EXPECTED="$(awk -v a="syft_${SYFT_VERSION}_linux_amd64.tar.gz" '$2==a {print $1; exit}' syft.sum)"
          echo "${EXPECTED}  syft.tgz" | sha256sum -c -
          tar -xzf syft.tgz -C bin syft
          export PATH="$PWD/bin:$PATH"
        '''
      }
    }
    stage('Fastpath') {
      steps {
        dir('examples/go-multi-entry') {
          sh 'make all_artifacts'
          sh 'make verify-golden'
        }
      }
    }
    stage('Publish SARIF') {
      steps {
        archiveArtifacts artifacts: 'examples/go-multi-entry/report.*.sarif', fingerprint: true
      }
    }
  }
}
```
