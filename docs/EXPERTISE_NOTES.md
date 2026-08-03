# Validate an adapter contract before claiming a live integration

### Client trigger

- Job wording or deliverable that makes this relevant: API/webhook integration,
  CRM/calendar/messaging connector, mapping validation, retries, idempotency,
  dead-letter handling, or pre-go-live acceptance testing
- How often it appeared in the measured corpus or proposal log: CRM 16.3%,
  messaging 13.5%, calendar 12.4%, and automation platforms 12.2% in the depth
  plan's measured corpus
- Existing project/component that can be reused: AdapterProof manifests and
  runner with the packaged DeliveryGuard lifecycle

### Failure symptom or unanswered choice

A connector can appear complete after one mocked 2xx while still sending the
wrong shape or headers, retrying permanent failures, duplicating side effects,
persisting secrets, or offering no replay evidence.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Patch the HTTP client and assert one call | very fast unit test | bypasses the real transport and rarely proves lifecycle state or receipts |
| Stand up a large provider simulator | rich faults and protocols | unnecessary runtime and provider maintenance before demand is known |
| Real local HTTP expectations plus a declarative manifest | exact wire proof while remaining credential-free and reusable | generic proof does not establish named-provider compatibility |

### Controlled comparison

- Representative cases or fixtures: two structurally different generic
  adapter manifests and one canonical lead-like event
- Frozen development/held-out split, when relevant: not applicable; this is a
  deterministic conformance contract
- Metrics and decision thresholds chosen before the run: every exact header and
  mapped payload matches; all 20 case results pass; receipt sequences equal the
  expected sequences; secrets are absent from SQLite evidence
- Runtime, hardware, model/provider version, cost assumptions, and date:
  Python 3.13.5 on Windows, Python 3.12 container, pytest-httpserver 1.1.5,
  DeliveryGuard 0.1.0 from `850cfd`, 2026-08-03, no paid provider
- What is deliberately outside the comparison: named SaaS schemas, OAuth,
  signature verification, provider sandboxes, concurrency, throughput, and UI

### Result

Both manifests passed ten cases each: success, already-applied, rate-limit
recovery, exhausted server failure, permanent rejection, malformed success,
duplicate suppression, changed-payload collision refusal, dead-letter replay,
and missing-secret refusal. The focused suite passed 13 tests. Retained
pytest-httpserver behavior passed 107 core tests and 23 examples, with 3 skips
and 1 expected failure. Package metadata and Docker execution passed.

### Decision rule

Start from AdapterProof when the client's adapter can be expressed as a bounded
JSON mapping and generic HTTP outcome contract. Add a named adapter only after
repeated job demand or a live client supplies the provider contract and
acceptance criteria.

### Delivery control

Freeze the canonical event, manifest, expected wire request, outcome sequence,
and report schema together. A changed payload under the same idempotency key
must refuse before transport, and a retry/replay claim must name its exact
receipt sequence.

### Reuse boundary

- Reusable without client data: manifest parser, dot-path mapper, scenario
  runner, generic fixtures, report schema, and DeliveryGuard integration
- Requires client data, credentials, environment, or acceptance criteria:
  actual provider schema, endpoint trust policy, auth flow, mappings, retry
  headers, and success/replay acceptance rules
- Unsupported claim that must not appear in a proposal: named-provider or
  production integration based only on these local generic fixtures

### Proposal-safe insight

I verify adapters at the wire and lifecycle boundaries before using live
credentials: exact mapped JSON and headers are checked alongside retry stop,
dedupe, collision, dead-letter, replay, receipt, and secret-persistence rules.

### Evidence

- Code: `adapterproof/manifest.py`, `adapterproof/mapping.py`,
  `adapterproof/runner.py`
- Tests: `tests/test_adapterproof.py` plus retained pytest-httpserver tests
- Raw comparison artifact: `docs/evidence/conformance-report.json`
- Foundation decision: `docs/PROJECT_START.md`, `THIRD_PARTY_REUSE.md`
- Reproduction command: `adapterproof run --output .evidence/report.json`

### Interview follow-up

- Likely technical question: Does this prove a Salesforce or Slack integration?
- Short answer: No. It proves the reusable HTTP adapter and delivery contracts;
  a named provider still needs its current schema, auth flow, and fixtures.
- Deeper evidence to open if challenged: exact request expectations, mapped
  payloads, receipt sequences, collision refusal, and redacted report artifact
