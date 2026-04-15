# Security policy

## Supported versions

We release security fixes for the latest development line on `main` and the most recent **tagged** release. Older tags may not receive backports unless a critical issue affects downstream users.

## Reporting a vulnerability

Please report security issues **privately** so we can coordinate a fix before public disclosure.

**Preferred:** use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) for this repository when it is enabled.

**Alternative:** email `team@noisecutter.dev` with a clear subject line (for example `Security: NoiseCutter`) and include:

- A short description of the issue and its impact
- Steps to reproduce or a proof-of-concept, if you can share them safely
- Affected **versions** and **surfaces**: PyPI package, Docker image, GitHub Action workflows, or CLI-only

We aim to acknowledge reports within a few business days and will agree on a disclosure timeline with you.

## Scope

### In scope

- The **NoiseCutter** Python package and CLI (`noisecutter` on PyPI when published from this project)
- **Docker** images published as documented in this repository (for example `ghcr.io/.../noisecutter`)
- **GitHub Actions** workflows defined under `.github/workflows/` in this repository, when they process untrusted input in a way that could affect users of those workflows

### Coordinated / upstream

NoiseCutter orchestrates external tools (for example **Syft**, **govulncheck**) and calls remote services (for example the **OSV** API). Vulnerabilities in those components should be reported to their respective projects unless NoiseCutter is clearly at fault (for example unsafe subprocess invocation, secret leakage, or insecure defaults in our code).

## Safe harbor

We support good-faith security research. Do not access data that is not yours, degrade production services, or perform disruptive testing against third parties without permission.

## PyPI and metadata

Published packages declare a **Security** project URL when built from this repository (see `pyproject.toml` `[project.urls]`). Use that link or this file for coordinated disclosure expectations.
