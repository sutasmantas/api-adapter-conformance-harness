from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

import pytest

from adapterproof.cli import FIXTURE_ROOT, main, run_default_suite
from adapterproof.manifest import ManifestError, load_manifest, parse_manifest
from adapterproof.mapping import MappingContractError, map_event
from adapterproof.viewer_server import create_viewer_server


def manifests() -> list[Path]:
    return sorted((FIXTURE_ROOT / "adapters").glob("*.json"))


def event() -> dict[str, object]:
    return json.loads((FIXTURE_ROOT / "canonical_event.json").read_text(encoding="utf-8"))


def test_record_mapping_is_exact_and_does_not_leak_unmapped_fields() -> None:
    manifest = load_manifest(FIXTURE_ROOT / "adapters" / "record_sink.json")
    assert map_event(manifest, event()) == {
        "source_event_id": "evt-20260801-001",
        "record": {
            "external_id": "lead-0042",
            "contact": {"email": "buyer@example.test"},
            "stage": "qualified",
            "source": "adapterproof",
        },
    }


def test_notification_mapping_uses_different_shape_and_auth_contract() -> None:
    manifest = load_manifest(FIXTURE_ROOT / "adapters" / "notification_sink.json")
    assert manifest.auth_header == "Authorization"
    assert manifest.auth_prefix == "Bearer "
    assert map_event(manifest, event()) == {
        "metadata": {
            "event_id": "evt-20260801-001",
            "event_type": "lead.qualified",
            "subject_id": "lead-0042",
        },
        "message": {
            "text": "Please schedule a technical discovery call.",
            "channel": "operations",
        },
    }


def test_missing_required_source_refuses_before_transport() -> None:
    manifest = load_manifest(FIXTURE_ROOT / "adapters" / "record_sink.json")
    with pytest.raises(MappingContractError, match=r"lead\.email"):
        map_event(manifest, {"event_id": "evt-1", "lead": {"id": "lead-1", "stage": "new"}})


@pytest.mark.parametrize(
    "mutation",
    [
        {"unexpected": True},
        {"adapter_id": "Bad ID"},
        {"endpoint_path": "relative"},
        {"idempotency_header": "bad\nheader"},
        {"auth": {"secret_ref": "literal:secret", "header": "Authorization", "prefix": ""}},
        {"mapping": {"event_id": "same", "lead.id": "same"}},
    ],
)
def test_invalid_manifest_contracts_refuse(mutation: dict[str, object]) -> None:
    value = json.loads((FIXTURE_ROOT / "adapters" / "record_sink.json").read_text(encoding="utf-8"))
    value.update(mutation)
    with pytest.raises(ManifestError):
        parse_manifest(value)


def test_default_suite_passes_all_wire_and_delivery_cases(tmp_path: Path) -> None:
    report = run_default_suite(tmp_path / "databases")
    assert report["gate"] == "PASS"
    assert report["deliveryguard"] == "0.1.0"
    assert report["foundation"] == "pytest-httpserver 1.1.5"
    assert len(report["adapters"]) == 2
    cases = [case for adapter in report["adapters"] for case in adapter["cases"]]
    assert len(cases) == 20
    assert all(case["passed"] for case in cases)
    assert {case["case"] for case in cases} == {
        "success",
        "already_applied",
        "rate_limit_then_success",
        "server_error_exhausted",
        "client_rejected",
        "malformed_success",
        "duplicate",
        "idempotency_collision",
        "dead_letter_replay",
        "missing_secret",
    }
    assert all(not adapter["secret_value_persisted"] for adapter in report["adapters"])
    assert report["adapters"][0]["mapped_payload"]["message"]["text"] == "[REDACTED]"
    assert report["adapters"][1]["mapped_payload"]["record"]["contact"]["email"] == "[REDACTED]"
    record_contract = report["adapters"][1]["wire_contract"]
    assert record_contract["method"] == "POST"
    assert record_contract["endpoint_path"] == "/v1/records"
    assert [header["name"] for header in record_contract["headers"]] == [
        "X-API-Key",
        "X-Idempotency-Key",
        "X-Correlation-ID",
        "Content-Type",
    ]
    assert "ADAPTERPROOF_RECORD_TOKEN" in record_contract["headers"][0]["value"]


def test_receipt_sequences_prove_retry_stop_and_replay(tmp_path: Path) -> None:
    report = run_default_suite(tmp_path / "databases")
    cases = {case["case"]: case for case in report["adapters"][0]["cases"]}
    assert cases["rate_limit_then_success"]["receipt_classifications"] == [
        "rate_limit",
        "success",
    ]
    assert cases["server_error_exhausted"]["receipt_classifications"] == [
        "server_error",
        "server_error",
    ]
    assert cases["client_rejected"]["receipt_classifications"] == ["client_error"]
    assert cases["dead_letter_replay"]["receipt_classifications"] == [
        "client_error",
        "success",
    ]
    assert cases["missing_secret"]["actual_requests"] == 0


def test_cli_writes_report_and_is_repeatable_on_same_database(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    database_dir = tmp_path / "databases"
    arguments = ["run", "--database-dir", str(database_dir), "--output", str(output)]
    assert main(arguments) == 0
    first = json.loads(output.read_text(encoding="utf-8"))
    assert main(arguments) == 0
    second = json.loads(output.read_text(encoding="utf-8"))
    assert first == second


def test_vendored_deliveryguard_wheel_matches_recorded_hash() -> None:
    root = Path(__file__).parents[1]
    wheel = root / "vendor" / "deliveryguard-0.1.0-py3-none-any.whl"
    expected = (root / "vendor" / "deliveryguard-0.1.0.sha256").read_text(encoding="utf-8").split()[0]
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == expected


def test_viewer_serves_the_generated_report_and_static_surface(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(run_default_suite(tmp_path / "databases")), encoding="utf-8")
    server = create_viewer_server(report_path, port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        with urlopen(f"http://{host}:{port}/api/report") as response:
            served_report = json.load(response)
            assert response.headers["Cache-Control"] == "no-store"
        assert served_report["gate"] == "PASS"
        assert sum(len(adapter["cases"]) for adapter in served_report["adapters"]) == 20
        with urlopen(f"http://{host}:{port}/") as response:
            page = response.read().decode()
        assert "AdapterProof protocol lab" in page
        assert 'id="adapter-switcher"' in page
        with urlopen(f"http://{host}:{port}/publication.html?frame=proof") as response:
            publication_page = response.read().decode()
        assert "429 rate limit" in publication_page
        assert "503 server failure" in publication_page
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
