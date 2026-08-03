# Third-party reuse

AdapterProof retains the Git history of
[pytest-httpserver](https://github.com/csernazs/pytest-httpserver), pinned at
`44b3c9123cf4861d9ceda34fd5c0077cd53d03b4`. Its real localhost server,
request matchers, ordered/one-shot expectations, response builders, request
log, and assertion checks are the central test mechanism.

AdapterProof also consumes the packaged DeliveryGuard 0.1.0 wheel built from
clean local `main` commit `850cfdafc545a40fdbaff4a8a577499a436888b5`.
The wheel is stored under `vendor/` with a SHA-256 checksum so detached
verification and CI do not depend on an unpublished remote.

The `adapterproof/` manifest, mapper, scenario runner, report schema, fixtures,
tests, CLI, documentation, and claim limits are portfolio-owned additions.
Foundation selection was technical; license was not researched or compared.
