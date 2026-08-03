"""Execute frozen wire-level conformance scenarios and return case evidence."""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from deliveryguard.executor import DeliveryExecutor, RetryPolicy
from deliveryguard.identifiers import canonical_json, make_idempotency_key
from deliveryguard.redaction import DEFAULT_REDACTED_FIELDS, redact
from deliveryguard.store import DeliveryStore, IdempotencyConflict
from pytest_httpserver import HTTPServer

from adapterproof.adapter import ManifestAdapter
from adapterproof.mapping import map_event

if TYPE_CHECKING:
    from collections.abc import Iterator

    from deliveryguard.models import ActionRecord

    from adapterproof.manifest import AdapterManifest


@dataclass(frozen=True)
class CaseResult:
    case: str
    expected_state: str
    actual_state: str
    expected_receipt_classifications: list[str]
    receipt_classifications: list[str]
    expected_requests: int
    actual_requests: int
    passed: bool
    detail: str


@dataclass(frozen=True)
class ConformanceReport:
    adapter_id: str
    manifest_hash: str
    wire_contract: dict[str, Any]
    mapped_payload: dict[str, Any]
    cases: list[CaseResult]
    secret_value_persisted: bool
    gate: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "manifest_hash": self.manifest_hash,
            "wire_contract": self.wire_contract,
            "mapped_payload": self.mapped_payload,
            "cases": [asdict(case) for case in self.cases],
            "secret_value_persisted": self.secret_value_persisted,
            "gate": self.gate,
        }


def _manifest_hash(manifest: AdapterManifest) -> str:
    normalized = asdict(manifest)
    normalized["redacted_fields"] = sorted(manifest.redacted_fields)
    return hashlib.sha256(canonical_json(normalized).encode()).hexdigest()


def _wire_contract(manifest: AdapterManifest) -> dict[str, Any]:
    """Describe the exercised request without exposing generated secrets."""
    return {
        "method": "POST",
        "endpoint_path": manifest.endpoint_path,
        "headers": [
            {
                "name": manifest.auth_header,
                "value": f"{manifest.auth_prefix}<resolved from {manifest.secret_ref}>",
                "source": manifest.secret_ref,
            },
            {
                "name": manifest.idempotency_header,
                "value": "<generated per case>",
                "source": "DeliveryGuard idempotency key",
            },
            {
                "name": manifest.correlation_header,
                "value": "<generated per case>",
                "source": "AdapterProof correlation ID",
            },
            {
                "name": "Content-Type",
                "value": "application/json",
                "source": "constant",
            },
        ],
    }


@contextmanager
def _environment_secret(name: str, value: str) -> Iterator[None]:
    previous = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


@contextmanager
def _quiet_http_logs() -> Iterator[None]:
    logger = logging.getLogger("werkzeug")
    previous = logger.level
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(previous)


def _result(
    *,
    name: str,
    expected_state: str,
    action: ActionRecord,
    store: DeliveryStore,
    expected_classifications: list[str],
    expected_requests: int,
    actual_requests: int,
    assertion_error: str = "",
) -> CaseResult:
    classifications = [item.classification.value for item in store.attempts(action.id)]
    passed = (
        action.state.value == expected_state
        and classifications == expected_classifications
        and actual_requests == expected_requests
        and not assertion_error
    )
    detail = assertion_error or "wire expectations, state, and receipt count matched"
    return CaseResult(
        case=name,
        expected_state=expected_state,
        actual_state=action.state.value,
        expected_receipt_classifications=expected_classifications,
        receipt_classifications=classifications,
        expected_requests=expected_requests,
        actual_requests=actual_requests,
        passed=passed,
        detail=detail,
    )


def run_conformance(
    manifest: AdapterManifest,
    event: dict[str, Any],
    database_path: str | Path,
) -> ConformanceReport:
    database = Path(database_path)
    database.parent.mkdir(parents=True, exist_ok=True)
    store = DeliveryStore(database)
    mapped = map_event(manifest, event)
    run_id = uuid.uuid4().hex
    environment_name = manifest.secret_ref.removeprefix("env:")
    fixture_secret = f"fixture-only-{manifest.adapter_id}-secret"
    cases: list[CaseResult] = []

    with (
        _environment_secret(environment_name, fixture_secret),
        _quiet_http_logs(),
        HTTPServer(host="127.0.0.1") as server,
    ):
        adapter = ManifestAdapter(manifest, server.url_for(manifest.endpoint_path))
        executor = DeliveryExecutor(
            store,
            adapter,
            policy=RetryPolicy(max_attempts=2),
            sleeper=lambda _: None,
        )

        def identifiers(name: str) -> tuple[str, str]:
            key = make_idempotency_key(
                "adapterproof",
                {"adapter": manifest.adapter_id, "case": name, "event": event, "run": run_id},
            )
            return key, f"adapterproof-{name}-{run_id[:12]}"

        def expect(name: str, statuses: list[int | str]) -> tuple[str, str]:
            key, correlation = identifiers(name)
            headers = {
                manifest.auth_header: f"{manifest.auth_prefix}{fixture_secret}",
                manifest.idempotency_header: key,
                manifest.correlation_header: correlation,
                "Content-Type": "application/json",
            }
            for status in statuses:
                handler = server.expect_ordered_request(
                    manifest.endpoint_path,
                    method="POST",
                    headers=headers,
                    json=mapped,
                )
                if status == "malformed":
                    handler.respond_with_data("not-json", status=200, content_type="application/json")
                else:
                    handler.respond_with_json({"receipt": f"{name}-{status}"}, status=int(status))
            return key, correlation

        def execute(
            name: str,
            statuses: list[int | str],
            expected_state: str,
            expected_classifications: list[str],
        ) -> None:
            server.clear()
            key, correlation = expect(name, statuses)
            assertion_error = ""
            with server.wait(timeout=2):
                action = executor.deliver(
                    idempotency_key=key,
                    destination=manifest.adapter_id,
                    payload=event,
                    correlation_id=correlation,
                )
            try:
                server.check()
            except AssertionError as exc:
                assertion_error = str(exc)
            cases.append(
                _result(
                    name=name,
                    expected_state=expected_state,
                    action=action,
                    store=store,
                    expected_classifications=expected_classifications,
                    expected_requests=len(statuses),
                    actual_requests=len(server.log),
                    assertion_error=assertion_error,
                )
            )

        execute("success", [202], "delivered", ["success"])
        execute("already_applied", [409], "already_applied", ["already_applied"])
        execute(
            "rate_limit_then_success",
            [429, 202],
            "delivered",
            ["rate_limit", "success"],
        )
        execute(
            "server_error_exhausted",
            [503, 503],
            "dead_letter",
            ["server_error", "server_error"],
        )
        execute("client_rejected", [422], "dead_letter", ["client_error"])
        execute(
            "malformed_success",
            ["malformed"],
            "dead_letter",
            ["malformed_response"],
        )

        server.clear()
        duplicate_key, duplicate_correlation = expect("duplicate", [202])
        with server.wait(timeout=2):
            first = executor.deliver(
                idempotency_key=duplicate_key,
                destination=manifest.adapter_id,
                payload=event,
                correlation_id=duplicate_correlation,
            )
            second = executor.deliver(
                idempotency_key=duplicate_key,
                destination=manifest.adapter_id,
                payload=event,
                correlation_id="ignored-duplicate-correlation",
            )
        duplicate_error = "" if first.id == second.id else "duplicate returned a different action"
        try:
            server.check()
        except AssertionError as exc:
            duplicate_error = str(exc)
        cases.append(
            _result(
                name="duplicate",
                expected_state="delivered",
                action=second,
                store=store,
                expected_classifications=["success"],
                expected_requests=1,
                actual_requests=len(server.log),
                assertion_error=duplicate_error,
            )
        )

        server.clear()
        collision_key, collision_correlation = expect("collision", [202])
        with server.wait(timeout=2):
            collision_action = executor.deliver(
                idempotency_key=collision_key,
                destination=manifest.adapter_id,
                payload=event,
                correlation_id=collision_correlation,
            )
        collision_refused = False
        try:
            executor.deliver(
                idempotency_key=collision_key,
                destination=manifest.adapter_id,
                payload=event | {"event_id": "changed-event"},
                correlation_id=collision_correlation,
            )
        except IdempotencyConflict:
            collision_refused = True
        collision_receipts = [item.classification.value for item in store.attempts(collision_action.id)]
        collision_passed = collision_refused and len(server.log) == 1 and collision_receipts == ["success"]
        cases.append(
            CaseResult(
                case="idempotency_collision",
                expected_state="collision_refused",
                actual_state=("collision_refused" if collision_refused else "collision_accepted"),
                expected_receipt_classifications=["success"],
                receipt_classifications=collision_receipts,
                expected_requests=1,
                actual_requests=len(server.log),
                passed=collision_passed,
                detail=(
                    "changed payload refused before transport"
                    if collision_passed
                    else "idempotency collision contract failed"
                ),
            )
        )

        server.clear()
        replay_key, replay_correlation = expect("replay", [422, 202])
        with server.wait(timeout=2):
            dead = executor.deliver(
                idempotency_key=replay_key,
                destination=manifest.adapter_id,
                payload=event,
                correlation_id=replay_correlation,
            )
            replayed = executor.replay(
                dead.id,
                payload=event,
                correlation_id=replay_correlation,
            )
        replay_error = "" if dead.state.value == "dead_letter" and replayed.cycle == 2 else "replay lifecycle mismatch"
        try:
            server.check()
        except AssertionError as exc:
            replay_error = str(exc)
        cases.append(
            _result(
                name="dead_letter_replay",
                expected_state="delivered",
                action=replayed,
                store=store,
                expected_classifications=["client_error", "success"],
                expected_requests=2,
                actual_requests=len(server.log),
                assertion_error=replay_error,
            )
        )

        server.clear()
        missing_key, missing_correlation = identifiers("missing_secret")
        os.environ.pop(environment_name, None)
        missing = executor.deliver(
            idempotency_key=missing_key,
            destination=manifest.adapter_id,
            payload=event,
            correlation_id=missing_correlation,
        )
        cases.append(
            _result(
                name="missing_secret",
                expected_state="dead_letter",
                action=missing,
                store=store,
                expected_classifications=["configuration_error"],
                expected_requests=0,
                actual_requests=len(server.log),
            )
        )

    persisted = fixture_secret in database.read_bytes().decode("utf-8", errors="ignore")
    passed = all(case.passed for case in cases) and not persisted
    return ConformanceReport(
        adapter_id=manifest.adapter_id,
        manifest_hash=_manifest_hash(manifest),
        wire_contract=_wire_contract(manifest),
        mapped_payload=redact(mapped, DEFAULT_REDACTED_FIELDS | manifest.redacted_fields),
        cases=cases,
        secret_value_persisted=persisted,
        gate="PASS" if passed else "FAIL",
    )
