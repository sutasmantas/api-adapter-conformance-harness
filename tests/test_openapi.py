from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from adapterproof.openapi import (
    OpenAPIContractError,
    classify_result,
    expectation_exit_code,
    load_contract,
    ndjson_event_types,
)

if TYPE_CHECKING:
    from pathlib import Path


def valid_contract() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "consumer_id": "example",
        "app": "example.main:app",
        "app_dir": ".",
        "port": 8873,
        "health_path": "/api/health",
        "schema_path": "/openapi.json",
        "data_env": {"EXAMPLE_DATA_DIR": ".evidence/data"},
        "include_path_regex": "^/api/health$",
        "phases": "coverage",
        "max_examples": 1,
        "seed": 20260806,
        "run_timeout_seconds": 30,
    }


def write_contract(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "adapterproof.openapi.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_contract_resolves_paths_and_freezes_bounded_controls(tmp_path: Path) -> None:
    contract = load_contract(write_contract(tmp_path, valid_contract()))
    assert contract.app_dir == tmp_path
    assert contract.data_env["EXAMPLE_DATA_DIR"] == tmp_path / ".evidence" / "data"
    assert contract.phases == "coverage"
    assert contract.max_examples == 1
    assert contract.health_url == "http://127.0.0.1:8873/api/health"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("phases", "fuzzing"),
        ("max_examples", 0),
        ("run_timeout_seconds", 301),
        ("port", False),
        ("health_path", "api/health"),
    ],
)
def test_contract_rejects_values_outside_trial_region(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    payload = valid_contract()
    payload[field] = value
    with pytest.raises(OpenAPIContractError):
        load_contract(write_contract(tmp_path, payload))


def test_contract_rejects_unknown_fields(tmp_path: Path) -> None:
    payload = valid_contract()
    payload["global_score"] = 99
    with pytest.raises(OpenAPIContractError, match=r"extra=.*global_score"):
        load_contract(write_contract(tmp_path, payload))


def test_fatal_event_overrides_ambiguous_exit_one() -> None:
    assert classify_result(None, 1, ["FatalError"]) == "SCHEMA_LOAD_FAILURE"
    assert classify_result(None, 1, ["NonFatalError"]) == "RUN_ERROR"
    assert classify_result(None, 1, ["ScenarioFinished"]) == "FINDINGS"


def test_budget_and_expectation_exit_codes_are_distinct() -> None:
    assert classify_result("TimeoutExpired: 30 seconds", None, []) == "BUDGET_KILLED"
    assert expectation_exit_code("BUDGET_KILLED", "no-findings") == 2
    assert expectation_exit_code("RUN_ERROR", "findings") == 2
    assert expectation_exit_code("FINDINGS", "no-findings") == 1
    assert expectation_exit_code("FINDINGS", "findings") == 0


def test_ndjson_parser_ignores_partial_lines(tmp_path: Path) -> None:
    report = tmp_path / "report.ndjson"
    report.write_text(
        '{"Initialize": {}}\nnot-json\n{"ScenarioFinished": {}}\n',
        encoding="utf-8",
    )
    assert ndjson_event_types(report) == ["Initialize", "ScenarioFinished"]
