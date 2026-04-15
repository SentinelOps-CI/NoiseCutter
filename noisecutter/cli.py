from __future__ import annotations

from pathlib import Path

import click
import typer
from rich import print

from .cache import Cache
from .config import load_config
from .core.fuse import fuse_to_sarif, write_summary_txt
from .core.policy import FailOn, PolicyLevel, evaluate_policy
from .exit_codes import INVALID_INPUT, POLICY_FAILURE, TOOL_FAILURE
from .integrations.go.govulncheck_adapter import compute_reachability_go
from .integrations.osv_adapter import audit_osv
from .integrations.syft_adapter import generate_sbom
from .logging_utils import setup_logging
from .utils import write_json_deterministic

app = typer.Typer(help=("NoiseCutter — prove what’s exploitable; ignore the rest."))


@app.callback()
def main_opts(
    ctx: typer.Context,
    log_level: str | None = typer.Option(
        None,
        "--log-level",
        help="error|warn|info|debug|trace",
    ),
    config_repo: Path | None = typer.Option(
        None,
        "--repo",
        help="Repo root for config discovery",
    ),
    strict_repro: bool | None = typer.Option(
        None,
        help=("Deterministic outputs; also honors NOISECUTTER_STRICT_REPRO"),
    ),
) -> None:
    setup_logging(log_level)
    cfg = load_config(config_repo)
    if strict_repro is not None:
        cfg.strict_repro = strict_repro
    ctx.obj = {"config": cfg, "cache": Cache(Path(cfg.cache_dir))}


@app.command()
def sbom(
    source: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Path to source repo",
    ),
    image: str | None = typer.Option(
        None,
        help="Container image ref (name@digest)",
    ),
    out: Path = typer.Option(
        Path("sbom.cdx.json"),
        help="Output CycloneDX SBOM path",
    ),
) -> None:
    """Generate CycloneDX SBOM using syft."""
    try:
        doc = generate_sbom(
            source_path=source,
            image_ref=image,
            cache=click.get_current_context().obj.get("cache"),
        )
    except RuntimeError as exc:
        print(f"[red]SBOM generation failed:[/red] {exc}. Install syft and try again.")
        raise typer.Exit(code=TOOL_FAILURE)
    write_json_deterministic(out, doc)
    print(f"[green]SBOM written:[/green] {out}")


@app.command()
def audit(
    sbom: Path = typer.Option(
        ...,
        exists=True,
        help="Input CycloneDX SBOM",
    ),
    out: Path = typer.Option(
        Path("vulns.json"),
        help="Output vulnerabilities JSON",
    ),
) -> None:
    """Enrich SBOM components with OSV advisories."""
    res = audit_osv(
        sbom_path=sbom,
        cache=click.get_current_context().obj.get("cache"),
    )
    write_json_deterministic(out, res)
    print(f"[green]Vulns written:[/green] {out}")


@app.command()
def reach(
    lang: str = typer.Option(..., help="Language (e.g., go)"),
    entry: Path = typer.Option(..., exists=True, help="Entry point (e.g., ./cmd/server)"),
    vulns: Path = typer.Option(..., exists=True, help="Vulnerabilities JSON"),
    coverage: Path | None = typer.Option(None, exists=True, help="Optional coverage file"),
    out: Path = typer.Option(Path("reach.json"), help="Output reachability JSON"),
) -> None:
    """Determine reachability for advisories."""
    if lang.lower() == "go":
        try:
            res = compute_reachability_go(
                entry_path=entry,
                vulns_json=vulns,
                coverage_path=coverage,
                cache=click.get_current_context().obj.get("cache"),
            )
        except RuntimeError as exc:
            print(f"[red]Reachability failed:[/red] {exc}. Install govulncheck and try again.")
            raise typer.Exit(code=TOOL_FAILURE)
    else:
        print("[red]Language not supported yet[/red]")
        raise typer.Exit(code=INVALID_INPUT)
    write_json_deterministic(out, res)
    print(f"[green]Reachability written:[/green] {out}")


@app.command()
def fuse(
    sbom: Path = typer.Option(..., exists=True),
    vulns: Path = typer.Option(..., exists=True),
    reach: Path = typer.Option(..., exists=True),
    out: Path = typer.Option(Path("report.sarif")),
) -> None:
    """Fuse SBOM+Vulns+Reachability into SARIF."""
    sarif_doc = fuse_to_sarif(
        sbom_path=sbom,
        vulns_path=vulns,
        reach_path=reach,
    )
    write_json_deterministic(out, sarif_doc)
    summary = out.with_suffix(".summary.txt")
    write_summary_txt(sarif_doc, summary)
    print(f"[green]SARIF written:[/green] {out}")
    print(f"[green]Summary written:[/green] {summary}")


@app.command()
def policy(
    sarif: Path = typer.Option(..., exists=True),
    level: PolicyLevel = typer.Option(PolicyLevel.high, case_sensitive=False),
    fail_on: FailOn = typer.Option(
        FailOn.reachable,
        case_sensitive=False,
        help="Fail criteria",
    ),
) -> None:
    """Evaluate policy and exit non-zero on violation."""
    violations = evaluate_policy(
        sarif_path=sarif,
        min_level=level,
        fail_on=fail_on,
    )
    if violations:
        size = len(violations)
        print(f"[red]Policy violations: {size}[/red]")
        for v in violations:
            rule_id = v["ruleId"]
            level_str = v.get("level")
            reachable_str = v.get("properties", {}).get("reachable")
            print(f" - {rule_id} {level_str} reachable={reachable_str}")
        raise typer.Exit(code=POLICY_FAILURE)
    print("[green]Policy passed[/green]")


cache_app = typer.Typer(help="Cache management")


@cache_app.command("warm")
def cache_warm(
    ctx: typer.Context,
    source: Path = typer.Option(Path("."), exists=True, dir_okay=True, file_okay=False),
    entries: str | None = typer.Option(None, help="Comma-separated entry points for reach"),
) -> None:
    # cfg exists for future advanced warming logic
    _ = ctx.obj["config"]
    # Placeholder: implement warming via integrations later
    entries_str = entries or ""
    prefix = "[green]Cache warmed for source:[/green] "
    prefix += f"{source} "
    msg = f"{prefix}entries={entries_str}"
    print(msg)


@cache_app.command("stats")
def cache_stats(ctx: typer.Context) -> None:
    cache = ctx.obj["cache"]
    s = cache.stats()
    print(f"entries={s['entries']} bytes={s['bytes']}")


@cache_app.command("clear")
def cache_clear(ctx: typer.Context) -> None:
    cache = ctx.obj["cache"]
    cache.clear()
    print("[green]Cache cleared[/green]")


app.add_typer(cache_app, name="cache")


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
