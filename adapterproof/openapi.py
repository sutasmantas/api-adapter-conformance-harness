"""Bounded OpenAPI contract execution through a pinned external Schemathesis CLI."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMATHESIS_GIT_PIN = "40e71c4657c79be08ea772b612a121b0e0ac7142"
SCHEMA_VERSION = "1.0.0"
_ENV_NAME = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_EXPECTED_FIELDS = {
    "schema_version",
    "consumer_id",
    "app",
    "app_dir",
    "port",
    "health_path",
    "schema_path",
    "data_env",
    "include_path_regex",
    "phases",
    "max_examples",
    "seed",
    "run_timeout_seconds",
}


class OpenAPIContractError(ValueError):
    """Raised when a consumer contract is malformed or outside the admitted region."""


@dataclass(frozen=True)
class OpenAPIContract:
    """Validated deterministic-coverage contract for one OpenAPI consumer."""

    consumer_id: str
    app: str
    app_dir: Path
    port: int
    health_path: str
    schema_path: str
    data_env: dict[str, Path]
    include_path_regex: str
    phases: str
    max_examples: int
    seed: int
    run_timeout_seconds: int
    source_path: Path

    @property
    def base_url(self) -> str:
        """Return the loopback URL owned by this run."""
        return f"http://127.0.0.1:{self.port}"

    @property
    def health_url(self) -> str:
        """Return the readiness URL."""
        return f"{self.base_url}{self.health_path}"

    @property
    def schema_url(self) -> str:
        """Return the OpenAPI document URL."""
        return f"{self.base_url}{self.schema_path}"


def _require_string(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        message = f"{field} must be a non-empty string"
        raise OpenAPIContractError(message)
    return value


def load_contract(path: Path) -> OpenAPIContract:
    """Load and validate a JSON contract without silently accepting extra policy."""
    source_path = path.resolve()
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        message = "contract must contain one JSON object"
        raise OpenAPIContractError(message)
    missing = sorted(_EXPECTED_FIELDS - set(payload))
    extra = sorted(set(payload) - _EXPECTED_FIELDS)
    if missing or extra:
        message = f"contract fields differ: missing={missing}, extra={extra}"
        raise OpenAPIContractError(message)
    if payload["schema_version"] != SCHEMA_VERSION:
        message = f"unsupported schema_version: {payload['schema_version']}"
        raise OpenAPIContractError(message)
    phases = _require_string(payload, "phases")
    if phases != "coverage":
        message = "only the bounded deterministic coverage phase is admitted"
        raise OpenAPIContractError(message)
    app = _require_string(payload, "app")
    if ":" not in app:
        message = "app must use the module:attribute form"
        raise OpenAPIContractError(message)
    app_dir_value = _require_string(payload, "app_dir")
    app_dir = (source_path.parent / app_dir_value).resolve()
    if not app_dir.is_dir():
        message = f"app_dir does not exist: {app_dir}"
        raise OpenAPIContractError(message)
    port = payload["port"]
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
        message = "port must be an integer from 1 through 65535"
        raise OpenAPIContractError(message)
    max_examples = payload["max_examples"]
    if not isinstance(max_examples, int) or isinstance(max_examples, bool) or not 1 <= max_examples <= 50:
        message = "max_examples must be an integer from 1 through 50"
        raise OpenAPIContractError(message)
    seed = payload["seed"]
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        message = "seed must be a non-negative integer"
        raise OpenAPIContractError(message)
    run_timeout = payload["run_timeout_seconds"]
    if not isinstance(run_timeout, int) or isinstance(run_timeout, bool) or not 1 <= run_timeout <= 300:
        message = "run_timeout_seconds must be an integer from 1 through 300"
        raise OpenAPIContractError(message)
    paths = {}
    for field in ("health_path", "schema_path"):
        value = _require_string(payload, field)
        if not value.startswith("/"):
            message = f"{field} must start with /"
            raise OpenAPIContractError(message)
        paths[field] = value
    data_env_payload = payload["data_env"]
    if not isinstance(data_env_payload, dict) or not data_env_payload:
        message = "data_env must be a non-empty object"
        raise OpenAPIContractError(message)
    data_env: dict[str, Path] = {}
    for name, value in data_env_payload.items():
        if not isinstance(name, str) or not _ENV_NAME.fullmatch(name):
            message = f"invalid data environment name: {name!r}"
            raise OpenAPIContractError(message)
        if not isinstance(value, str) or not value:
            message = f"data environment path must be a string: {name}"
            raise OpenAPIContractError(message)
        data_env[name] = (source_path.parent / value).resolve()
    return OpenAPIContract(
        consumer_id=_require_string(payload, "consumer_id"),
        app=app,
        app_dir=app_dir,
        port=port,
        health_path=paths["health_path"],
        schema_path=paths["schema_path"],
        data_env=data_env,
        include_path_regex=_require_string(payload, "include_path_regex"),
        phases=phases,
        max_examples=max_examples,
        seed=seed,
        run_timeout_seconds=run_timeout,
        source_path=source_path,
    )


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def ndjson_event_types(path: Path | None) -> list[str]:
    """Return the ordered top-level event names from a Schemathesis report."""
    if path is None:
        return []
    event_types: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and event:
                event_types.append(next(iter(event)))
    return event_types


def classify_result(
    start_error: str | None,
    return_code: int | None,
    event_types: list[str],
) -> str:
    """Separate product findings from evaluator and budget failures."""
    if start_error and start_error.startswith("TimeoutExpired:"):
        return "BUDGET_KILLED"
    if start_error:
        return "TOOL_OR_START_FAILURE"
    if "FatalError" in event_types:
        return "SCHEMA_LOAD_FAILURE"
    if "NonFatalError" in event_types:
        return "RUN_ERROR"
    if return_code not in {0, 1}:
        return "TOOL_OR_START_FAILURE"
    return "FINDINGS" if return_code == 1 else "NO_FINDINGS"


def expectation_exit_code(result_class: str, expected: str) -> int:
    """Return zero only when the observed product result matches the declared expectation."""
    expected_result = {"no-findings": "NO_FINDINGS", "findings": "FINDINGS"}[expected]
    if result_class in {
        "BUDGET_KILLED",
        "RUN_ERROR",
        "SCHEMA_LOAD_FAILURE",
        "TOOL_OR_START_FAILURE",
    }:
        return 2
    return 0 if result_class == expected_result else 1


def _wait_until_ready(url: str, process: subprocess.Popen[str], seconds: int = 30) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            message = f"consumer exited before readiness with {process.returncode}"
            raise RuntimeError(message)
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.5)
    message = f"consumer did not become ready: {url}"
    raise TimeoutError(message)


def _schemathesis_executable() -> Path:
    name = "schemathesis.exe" if os.name == "nt" else "schemathesis"
    executable = Path(sys.executable).with_name(name)
    if not executable.is_file():
        message = (
            "Schemathesis is not installed beside the AdapterProof interpreter; "
            f"install Git pin {SCHEMATHESIS_GIT_PIN} in this isolated tool environment"
        )
        raise FileNotFoundError(message)
    return executable


def run_openapi_contract(
    contract_path: Path,
    consumer_python: Path,
    report_dir: Path,
) -> dict[str, Any]:
    """Run one real-service OpenAPI contract and persist a classified receipt."""
    contract = load_contract(contract_path)
    resolved_consumer_python = consumer_python.resolve()
    if not resolved_consumer_python.is_file():
        message = f"consumer Python does not exist: {resolved_consumer_python}"
        raise FileNotFoundError(message)
    executable = _schemathesis_executable()
    resolved_report_dir = report_dir.resolve()
    resolved_report_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    for name, path in contract.data_env.items():
        path.mkdir(parents=True, exist_ok=True)
        environment[name] = str(path)
    uvicorn_command = [
        str(resolved_consumer_python),
        "-m",
        "uvicorn",
        contract.app,
        "--host",
        "127.0.0.1",
        "--port",
        str(contract.port),
        "--app-dir",
        str(contract.app_dir),
        "--log-level",
        "warning",
        "--no-access-log",
    ]
    schemathesis_command = [
        str(executable),
        "run",
        contract.schema_url,
        "--phases",
        contract.phases,
        "--max-examples",
        str(contract.max_examples),
        "--workers",
        "1",
        "--seed",
        str(contract.seed),
        "--report",
        "ndjson",
        "--report-dir",
        str(resolved_report_dir),
        "--no-color",
        "--include-path-regex",
        contract.include_path_regex,
    ]
    started = time.monotonic()
    started_wall = time.time()
    process = subprocess.Popen(
        uvicorn_command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    run: subprocess.CompletedProcess[str] | None = None
    start_error: str | None = None
    try:
        _wait_until_ready(contract.health_url, process)
        run = subprocess.run(
            schemathesis_command,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=contract.run_timeout_seconds,
            check=False,
        )
    except (OSError, RuntimeError, subprocess.TimeoutExpired, TimeoutError) as exc:
        start_error = f"{type(exc).__name__}: {exc}"
    finally:
        process.terminate()
        try:
            consumer_stdout, consumer_stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            consumer_stdout, consumer_stderr = process.communicate(timeout=10)
    reports = sorted(
        (path for path in resolved_report_dir.glob("*.ndjson") if path.stat().st_mtime >= started_wall - 1),
        key=lambda path: path.stat().st_mtime,
    )
    latest = reports[-1] if reports else None
    return_code = run.returncode if run else None
    event_types = ndjson_event_types(latest)
    result_class = classify_result(start_error, return_code, event_types)
    version = subprocess.run(
        [str(executable), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    receipt = {
        "receipt_version": "1.0.0",
        "consumer_id": contract.consumer_id,
        "contract": str(contract.source_path),
        "app": contract.app,
        "consumer_python": str(resolved_consumer_python),
        "schema_url": contract.schema_url,
        "candidate": {
            "source": "https://github.com/schemathesis/schemathesis",
            "git_pin": SCHEMATHESIS_GIT_PIN,
            "reported_version": version.stdout.strip(),
        },
        "controls": {
            "phases": contract.phases,
            "max_examples": contract.max_examples,
            "workers": 1,
            "seed": contract.seed,
            "include_path_regex": contract.include_path_regex,
            "run_timeout_seconds": contract.run_timeout_seconds,
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "schemathesis_exit": return_code,
        "result_class": result_class,
        "report_event_types": event_types,
        "start_error": start_error,
        "report": latest.name if latest else None,
        "report_sha256": _digest(latest) if latest else None,
        "stdout_tail": run.stdout[-8000:] if run else "",
        "stderr_tail": run.stderr[-4000:] if run else "",
        "consumer_stdout_tail": consumer_stdout[-2000:],
        "consumer_stderr_tail": consumer_stderr[-4000:],
    }
    (resolved_report_dir / "run-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt
