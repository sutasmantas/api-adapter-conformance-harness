"""AdapterProof command line interface."""

from __future__ import annotations

import argparse
import json
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from adapterproof.manifest import load_manifest
from adapterproof.openapi import expectation_exit_code, run_openapi_contract
from adapterproof.runner import run_conformance
from adapterproof.viewer_server import create_viewer_server

FIXTURE_ROOT = Path(__file__).parent / "fixtures"


def run_default_suite(database_dir: Path) -> dict[str, Any]:
    event = json.loads((FIXTURE_ROOT / "canonical_event.json").read_text(encoding="utf-8"))
    reports = []
    for manifest_path in sorted((FIXTURE_ROOT / "adapters").glob("*.json")):
        manifest = load_manifest(manifest_path)
        report = run_conformance(
            manifest,
            event,
            database_dir / f"{manifest.adapter_id}.sqlite3",
        )
        reports.append(report.to_dict())
    passed = bool(reports) and all(report["gate"] == "PASS" for report in reports)
    return {
        "gate": "PASS" if passed else "FAIL",
        "foundation": f"pytest-httpserver {version('pytest-httpserver')}",
        "deliveryguard": version("deliveryguard"),
        "adapters": reports,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="adapterproof")
    command = result.add_subparsers(dest="command", required=True)
    run = command.add_parser("run", help="run the frozen generic adapter suite")
    run.add_argument("--database-dir", type=Path, default=Path(".evidence/databases"))
    run.add_argument("--output", type=Path)
    view = command.add_parser("view", help="serve a generated conformance report")
    view.add_argument("--report", type=Path, default=Path("docs/evidence/conformance-report.json"))
    view.add_argument("--host", default="127.0.0.1")
    view.add_argument("--port", type=int, default=8767)
    openapi = command.add_parser(
        "openapi",
        help="run a bounded schema-derived API contract in an isolated tool environment",
    )
    openapi.add_argument("--config", type=Path, required=True)
    openapi.add_argument("--consumer-python", type=Path, required=True)
    openapi.add_argument("--report-dir", type=Path, default=Path(".evidence/openapi"))
    openapi.add_argument(
        "--expect",
        choices=("no-findings", "findings"),
        default="no-findings",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "run":
        report = run_default_suite(arguments.database_dir)
        serialized = json.dumps(report, indent=2, sort_keys=True)
        print(serialized)
        if arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(f"{serialized}\n", encoding="utf-8")
        return 0 if report["gate"] == "PASS" else 1
    if arguments.command == "view":
        server = create_viewer_server(arguments.report, host=arguments.host, port=arguments.port)
        print(f"AdapterProof report viewer: http://{arguments.host}:{arguments.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    if arguments.command == "openapi":
        receipt = run_openapi_contract(
            arguments.config,
            arguments.consumer_python,
            arguments.report_dir,
        )
        summary = {
            key: receipt[key]
            for key in (
                "consumer_id",
                "elapsed_seconds",
                "schemathesis_exit",
                "result_class",
                "report",
                "report_sha256",
            )
        }
        # A failure summary that omits why it failed forces the reader into the
        # artifact. Surface the cause inline when there is one.
        if receipt.get("start_error"):
            summary["start_error"] = receipt["start_error"]
        print(json.dumps(summary, indent=2))
        return expectation_exit_code(receipt["result_class"], arguments.expect)
    raise RuntimeError("Unknown command.")
