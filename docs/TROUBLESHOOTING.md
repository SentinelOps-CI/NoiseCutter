Troubleshooting
===============

Syft not found
--------------

**Symptom:** `RuntimeError: syft not found`.

**Fix:**

- Install [Syft](https://github.com/anchore/syft) and ensure it is on `PATH`, **or**
- Set `SYFT_EXE` to the absolute path to the `syft` binary (common on Windows), **or**
- Place `syft` or `syft.exe` in `./bin/` under the current working directory.

Prefer a **checksum-verified** install using [`scripts/install-syft.sh`](../scripts/install-syft.sh) (Unix/macOS) or [`scripts/install-syft.ps1`](../scripts/install-syft.ps1) (Windows). Versions are pinned in [`tool-versions.json`](../tool-versions.json).

govulncheck errors
------------------

1. **No `go.mod` found**  
   Ensure the `--entry` path sits under a Go module. The adapter walks up to find `go.mod`.

2. **Missing `go.sum` entries**  
   Run `go mod tidy` inside the module once.

3. **Package path invalid**  
   Use paths that exist under the module (for example `./cmd/server`).

4. **Version drift**  
   Install the govulncheck version recommended in `tool-versions.json` (for example `go install golang.org/x/vuln/cmd/govulncheck@v1.2.0`).

Windows encoding
----------------

If you see `UnicodeDecodeError` in the console:

- Set `PYTHONIOENCODING=utf-8` and `chcp 65001`, then re-run.

Editable install not picked up
------------------------------

**Symptom:** `No module named noisecutter` when running `make` on Windows.

**Fix:**

- Point Make at your interpreter: `make PYTHON="py -3"` where supported, **or**
- Reinstall editable: `py -3 -m pip install -e .`
- Confirm: `py -3 -c "import noisecutter, inspect; print(inspect.getfile(noisecutter))"` should resolve to your clone.

OSV API and audit step
-----------------------

- The OSV client uses **httpx** with retries on transient HTTP errors and network failures. Persistent failures usually indicate network policy (firewall/proxy) blocking `https://api.osv.dev/`.
- If severity parsing errors appear on unusual OSV payloads, update to the latest `noisecutter` or install from source (`pip install -e .` / `uv sync --extra dev`).

Shim vs module execution
--------------------------

If the `noisecutter` console script fails on Windows, use:

```bash
python -m noisecutter
```

CI vs local differences
-----------------------

- CI uses **`uv sync --frozen --extra dev`** so lockfile and dev tools match. If local runs diverge, regenerate the lockfile with `uv lock` after dependency changes.
- Spell check: install [typos](https://github.com/crate-ci/typos) or rely on the `typos` step in GitHub Actions.

Dependency / supply-chain checks
--------------------------------

- **`pip-audit`** runs in CI against an exported locked requirement list. To reproduce locally:

  ```bash
  uv export --frozen --no-dev --no-hashes --no-emit-project -o /tmp/req.txt
  uvx pip-audit -r /tmp/req.txt --strict
  ```
