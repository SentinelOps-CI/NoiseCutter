Troubleshooting
---------------

Syft not found
--------------

Symptom: `RuntimeError: syft not found`.

Fix:
- Install syft and ensure it is on PATH; or
- Set `SYFT_EXE` to the absolute syft path; or
- Place `syft(.exe)` in `./bin/`.

govulncheck errors
------------------

1) No go.mod found
- Ensure the entry path is under a Go module (`go.mod`).
- The adapter auto-detects the module root; run from the repo or provide a path inside the module.

2) Missing go.sum entries
- Run `go mod tidy` inside the module once.

3) Package pattern not in std
- We pass relative package paths (e.g., `./cmd/server`). Ensure the entry exists under the module.

Windows encoding noise
----------------------

If you see `UnicodeDecodeError` in the console when chaining commands:
- Set `set PYTHONIOENCODING=utf-8` and `chcp 65001`, then re-run.

Editable install not picked up
------------------------------

Symptom: `No module named noisecutter` when running `make` on Windows.

Fix:
- Use an explicit interpreter in Make: `make PYTHON="py -3" ...`
- Or reinstall editable: `py -3 -m pip install -e .`
- Confirm path: `py -3 -c "import noisecutter,inspect;print(inspect.getfile(noisecutter))"` should point to your repo.

OSV severity parsing error
--------------------------

If you hit a `ValueError` on CVSS strings, upgrade to the latest `noisecutter` or reinstall from source (`pip install -e .`).

Shim vs module execution
------------------------

If `noisecutter` shim fails on Windows, use `python -m noisecutter` instead.


