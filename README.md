# AdapterProof

AdapterProof verifies a client-owned HTTP integration before live credentials
or go-live. A declarative manifest maps a canonical event into the provider
payload and defines referenced authentication, idempotency, and correlation
headers. The harness then sends real localhost HTTP requests through
DeliveryGuard and records a case-level conformance report.

The frozen suite covers two deliberately generic adapter shapes—record and
notification sinks—not named SaaS products. Each runs success, already-applied,
rate-limit recovery, exhausted server failure, permanent rejection, malformed
success, duplicate delivery, changed-payload idempotency collision refusal,
dead-letter replay, and missing-secret cases.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install vendor\deliveryguard-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest tests\test_adapterproof.py -q
.\.venv\Scripts\adapterproof.exe run --output .evidence\report.json
```

The command must print `"gate": "PASS"` for both manifests. It can be rerun
against the same database directory without reusing an action because each
verification execution is separately scoped.

## Read-only report viewer

Generate the report, then open the local protocol-lab surface:

```powershell
.\.venv\Scripts\adapterproof.exe run --output docs\evidence\conformance-report.json
.\.venv\Scripts\adapterproof.exe view --report docs\evidence\conformance-report.json
```

Visit `http://127.0.0.1:8767`. The viewer reads the generated report directly;
it does not run a second test path or hard-code the pass count. It shows the
safe request-header contract, redacted mapped payload, manifest identity, and
receipt sequence for each frozen case.

## Portfolio evidence

The local `final_upload/` package contains three 1600×1200 report-driven PNGs
and a 20.76-second H.264 walkthrough. `docs/PUBLICATION_EVIDENCE.md` records
the exact generation, browser, media, and claim gates. These files do not imply
deployment or a public repository; both remain separate publication actions.

## Manifest boundary

The manifest supports:

- one HTTP endpoint path;
- an `env:` secret reference, header, and prefix;
- idempotency and correlation header names;
- bounded timeout;
- source-to-target dot-path mappings and JSON constants;
- required source paths and additional redacted field names.

It deliberately does not embed secret values, execute arbitrary transforms,
or claim compatibility with a provider merely because the generic HTTP cases
pass. Named CRM, calendar, messaging, or automation adapters still require a
live/repeated job trigger and provider-specific fixtures.

## Evidence boundaries

AdapterProof proves local contract behavior, not production availability,
throughput, distributed exactly-once effects, OAuth flows, webhook signature
verification, or a named SaaS integration. Endpoint allowlisting and private
network controls remain consuming-application responsibilities.
