"""Bounded dot-path mapping from canonical events to provider payloads."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from adapterproof.manifest import AdapterManifest


class MappingContractError(ValueError):
    pass


def _read_path(source: Mapping[str, Any], path: str) -> Any:
    current: Any = source
    for segment in path.split("."):
        if not isinstance(current, Mapping) or segment not in current:
            raise MappingContractError(f"Required source field is missing: {path}.")
        current = current[segment]
    return copy.deepcopy(current)


def _write_path(target: dict[str, Any], path: str, value: Any) -> None:
    segments = path.split(".")
    current = target
    for segment in segments[:-1]:
        existing = current.get(segment)
        if existing is None:
            child: dict[str, Any] = {}
            current[segment] = child
            current = child
        elif isinstance(existing, dict):
            current = existing
        else:
            raise MappingContractError(f"Mapping target conflicts at: {path}.")
    leaf = segments[-1]
    if leaf in current:
        raise MappingContractError(f"Mapping target was written twice: {path}.")
    current[leaf] = copy.deepcopy(value)


def map_event(manifest: AdapterManifest, event: Mapping[str, Any]) -> dict[str, Any]:
    for required in manifest.required_source_paths:
        _read_path(event, required)
    result: dict[str, Any] = {}
    for source, target in manifest.mapping.items():
        _write_path(result, target, _read_path(event, source))
    for target, value in manifest.constants.items():
        _write_path(result, target, value)
    return result
