"""Strict declarative contract for an HTTP delivery adapter."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ADAPTER_ID = re.compile(r"^[a-z][a-z0-9_]{2,47}$")
HEADER_NAME = re.compile(r"^[A-Za-z0-9!#$%&'*+.^_`|~-]{1,128}$")
PATH_SEGMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")
ALLOWED_KEYS = {
    "adapter_id",
    "endpoint_path",
    "auth",
    "idempotency_header",
    "correlation_header",
    "timeout_seconds",
    "mapping",
    "constants",
    "required_source_paths",
    "redacted_fields",
}


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class AdapterManifest:
    adapter_id: str
    endpoint_path: str
    secret_ref: str
    auth_header: str
    auth_prefix: str
    idempotency_header: str
    correlation_header: str
    timeout_seconds: float
    mapping: dict[str, str]
    constants: dict[str, Any]
    required_source_paths: tuple[str, ...]
    redacted_fields: frozenset[str]


def _path(value: str, label: str) -> str:
    segments = value.split(".")
    if not segments or any(not PATH_SEGMENT.fullmatch(part) for part in segments):
        raise ManifestError(f"{label} must be a dot-separated safe field path.")
    return value


def _header(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEADER_NAME.fullmatch(value):
        raise ManifestError(f"{label} must be a valid HTTP header name.")
    return value


def parse_manifest(value: Any) -> AdapterManifest:
    if not isinstance(value, dict):
        raise ManifestError("Adapter manifest must be a JSON object.")
    unknown = set(value) - ALLOWED_KEYS
    if unknown:
        raise ManifestError(f"Unknown manifest fields: {', '.join(sorted(unknown))}.")
    adapter_id = value.get("adapter_id")
    if not isinstance(adapter_id, str) or not ADAPTER_ID.fullmatch(adapter_id):
        raise ManifestError("adapter_id must be 3-48 lowercase letters, digits, or underscores.")
    endpoint_path = value.get("endpoint_path")
    if (
        not isinstance(endpoint_path, str)
        or not endpoint_path.startswith("/")
        or "//" in endpoint_path
        or "?" in endpoint_path
        or "#" in endpoint_path
    ):
        raise ManifestError("endpoint_path must be an absolute path without query or fragment.")
    auth = value.get("auth")
    if not isinstance(auth, dict) or set(auth) != {"secret_ref", "header", "prefix"}:
        raise ManifestError("auth must contain exactly secret_ref, header, and prefix.")
    secret_ref = auth["secret_ref"]
    if not isinstance(secret_ref, str) or not secret_ref.startswith("env:"):
        raise ManifestError("auth.secret_ref must use an env: reference.")
    auth_prefix = auth["prefix"]
    if not isinstance(auth_prefix, str) or "\r" in auth_prefix or "\n" in auth_prefix:
        raise ManifestError("auth.prefix must be a single-line string.")
    timeout = value.get("timeout_seconds", 10.0)
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 120:
        raise ManifestError("timeout_seconds must be greater than zero and no more than 120.")
    mapping = value.get("mapping")
    if not isinstance(mapping, dict) or not mapping:
        raise ManifestError("mapping must contain at least one source-to-target path.")
    normalized_mapping: dict[str, str] = {}
    for source, target in mapping.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise ManifestError("mapping paths must be strings.")
        normalized_mapping[_path(source, "mapping source")] = _path(target, "mapping target")
    if len(set(normalized_mapping.values())) != len(normalized_mapping):
        raise ManifestError("Two source paths cannot write the same mapping target.")
    constants = value.get("constants", {})
    if not isinstance(constants, dict):
        raise ManifestError("constants must be a JSON object.")
    normalized_constants = {_path(str(key), "constant target"): item for key, item in constants.items()}
    if set(normalized_constants) & set(normalized_mapping.values()):
        raise ManifestError("A constant and mapping cannot write the same target.")
    required = value.get("required_source_paths", list(normalized_mapping))
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise ManifestError("required_source_paths must be a list of field paths.")
    normalized_required = tuple(_path(item, "required source") for item in required)
    redacted = value.get("redacted_fields", [])
    if not isinstance(redacted, list) or not all(isinstance(item, str) for item in redacted):
        raise ManifestError("redacted_fields must be a list of field names.")
    return AdapterManifest(
        adapter_id=adapter_id,
        endpoint_path=endpoint_path,
        secret_ref=secret_ref,
        auth_header=_header(auth["header"], "auth.header"),
        auth_prefix=auth_prefix,
        idempotency_header=_header(value.get("idempotency_header"), "idempotency_header"),
        correlation_header=_header(value.get("correlation_header"), "correlation_header"),
        timeout_seconds=float(timeout),
        mapping=normalized_mapping,
        constants=normalized_constants,
        required_source_paths=normalized_required,
        redacted_fields=frozenset(redacted),
    )


def load_manifest(path: str | Path) -> AdapterManifest:
    source = Path(path)
    try:
        return parse_manifest(json.loads(source.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Manifest is not valid JSON: {exc.msg}.") from None
