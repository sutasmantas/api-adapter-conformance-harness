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
    raise RuntimeError("Unknown command.")
