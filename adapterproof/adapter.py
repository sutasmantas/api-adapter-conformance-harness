"""Manifest-driven adapter that delegates reliability to DeliveryGuard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from deliveryguard.adapter import ProviderConfig, WebhookAdapter
from deliveryguard.redaction import DEFAULT_REDACTED_FIELDS

from adapterproof.mapping import map_event

if TYPE_CHECKING:
    from collections.abc import Mapping

    from deliveryguard.models import DeliveryResult

    from adapterproof.manifest import AdapterManifest


class ManifestAdapter:
    def __init__(self, manifest: AdapterManifest, endpoint_url: str) -> None:
        self.manifest = manifest
        self._delegate = WebhookAdapter(
            ProviderConfig(
                endpoint_url,
                secret_ref=manifest.secret_ref,
                secret_header=manifest.auth_header,
                secret_prefix=manifest.auth_prefix,
                idempotency_header=manifest.idempotency_header,
                correlation_header=manifest.correlation_header,
                timeout_seconds=manifest.timeout_seconds,
                redacted_fields=DEFAULT_REDACTED_FIELDS | manifest.redacted_fields,
            )
        )

    def send(
        self,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        correlation_id: str,
    ) -> DeliveryResult:
        return self._delegate.send(
            map_event(self.manifest, payload),
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
        )
