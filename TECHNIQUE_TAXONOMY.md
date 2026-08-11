# AdapterProof technique taxonomy

Date: 2026-08-05

Status: systematic research dossier; no implementation or experiment is authorized here. Conclusions use `established`, `provisional`, `contested`, or `unknown`.

## Decision boundary

AdapterProof currently validates a declarative HTTP adapter against a real local server with two manifests and twenty deterministic lifecycle cases. It proves exact headers/body/mapping plus DeliveryGuard retry, receipt, dedupe, collision, dead-letter and replay behavior. It does not prove arbitrary OpenAPI support, generated/stateful exploration, consumer compatibility, OAuth, pagination, concurrency/rate limits, signature protocols, non-REST APIs, production traffic or a named provider.

The paid outcome is pre-go-live evidence that an integration behaves correctly at the wire and fails safely. Schema validity, workflow semantics, compatibility, security authorization and performance are separate test-oracle problems.

## Problem decomposition

| Layer | Decision | Serious families | Current boundary |
| --- | --- | --- | --- |
| contract source | describe callable surface | custom manifest; OpenAPI; consumer contract; traffic/examples; protocol schema | custom manifest |
| request construction | produce syntactically and semantically valid requests | fixed fixtures; example/overlay seeding; property generation; mutation; LLM assistance | fixed fixtures |
| state/workflow | order dependent operations and reuse outputs | independent calls; producer-consumer graph; state machine; coverage-guided sequence; formal model | fixed hand-authored lifecycle |
| oracle | decide correctness beyond 2xx/5xx | schema; exact wire; invariants; semantic contracts; metamorphic relations; differential/consumer checks | exact wire and lifecycle |
| evolution | detect provider/consumer breakage | OpenAPI diff; generated SDK compilation; consumer-driven contract; replayed traffic | none |
| auth/security | prove identity, authorization and abuse controls | static auth headers; OAuth flows; multi-principal BOLA/BFLA; injection/security fuzzing | secret header only |
| resilience | rate limits, pagination, retries and malformed behavior | fixed cases; stateful property tests; chaos/network faults | fixed status/timeout cases |
| protocol family | choose protocol-specific conformance | REST/OpenAPI; GraphQL/HTTP; gRPC interop; AsyncAPI/event; webhooks/signatures | REST/HTTP only |
| environment | select realism and determinism | in-process mock; real local server; recorded replay; container system; live sandbox | real local server |
| reproducibility | minimize and replay failures | seed/example; shrinking; sequence replay; generated code; JUnit/SARIF | deterministic named cases |
| evaluation | distinguish activity from value | endpoint/status coverage; valid-operation rate; unique reproducible faults; semantic/authorization detection; flakiness | case pass/fail |

## Technique families and operating regions

### Fixed deterministic conformance — `established control`

Exact hand-written cases remain the best acceptance oracle for a known client integration and policy-critical edge cases. They are auditable and stable but cannot discover unknown combinations or long sequences.

### OpenAPI schema/property generation — `established family`

Schemathesis builds on Hypothesis to generate, shrink and reproduce OpenAPI/GraphQL cases and stateful workflows. It is the closest Python fit and should be the first generated-test candidate. Specification quality bounds results: recent fault-injection work shows coverage can remain high while request/response quality collapses.

### Example/Overlay augmentation — `provisional but strong fit`

OpenAPI descriptions often omit valid semantic values and inter-parameter constraints. OAI Overlay 1.1 provides a standard, separate augmentation document; 2026 industrial EvoMaster work reports improved black-box input viability. Use it to seed examples without forking the provider spec, while still testing the base spec for drift.

### Stateful dependency fuzzing — `established family`, `tool-dependent`

RESTler infers producer-consumer dependencies and explores request sequences; EvoMaster adds search and white-box support; WuppieFuzz adds LibAFL coverage guidance. These can reach deeper states than independent calls, but runtime, language, setup and flakiness differ. They follow—not replace—the fixed acceptance and Schemathesis control.

### Formal model/executable semantic contracts — `provisional specialist`

IcePick/Glacier uses a TLA+ state model and executable semantic contracts to address sequence coverage and weak status-code oracles. This can suit a small critical state machine, but model construction and state explosion make it inappropriate as the default adapter path.

### Metamorphic testing — `provisional specialist`

Metamorphic relations compare outputs when a definitive answer is unavailable. Recent ARMeta evidence suggests complementarity, not replacement. Use only where a stable domain relation can be reviewed; do not let an LLM-generated relation become its own oracle.

### Compatibility and consumer-driven contracts — `established distinct families`

oasdiff detects documented OpenAPI breaking changes; Pact verifies the subset a consumer actually uses. A schema diff cannot prove runtime behavior, and a consumer contract cannot find unused-provider regressions. Use both where provider evolution and real consumer assumptions matter.

### Mocking and replay — `established support family`

Prism and WireMock provide spec-driven mocks/stubs and fault behavior. They accelerate consumer development but are not evidence that the real provider conforms. AdapterProof's real-localhost wire path remains the final pre-go-live control.

### Security-specific API testing — `established separate oracle family`

OWASP guidance and current ASTF/EvoMaster work cover multi-principal object/function authorization, injection and abuse. Security tests require authorized identities and explicit policy predicates; generic 5xx fuzzing cannot infer BOLA/BFLA correctness.

### Flakiness detection and replay — `established evaluation need`

A 2026 study inspected nearly 3,000 failures across 36 APIs and showed REST fuzzing flakiness is material. Re-run/minimize failures, reset state, distinguish nondeterminism from unique faults, and never count repeated flaky failures as discoveries.

### Protocol-specific conformance — `established specialized profiles`

GraphQL-over-HTTP has an official audit suite, gRPC has an interop suite, and AsyncAPI describes event APIs. Do not force these through a REST manifest; reuse the protocol's own maintained conformance surface when a client request requires it.

## Search protocol

- Search date: 2026-08-05.
- Sources: the 2024 server-side web-fuzzing survey, primary tool papers and 2025-2026 comparative studies, official OpenAPI/Overlay/GraphQL/gRPC/AsyncAPI/OWASP material, maintained GitHub repositories and current issue metadata.
- Included negative evidence: incomplete specs, low valid-request rates, weak status-code oracles, state explosion and flaky failures.
- Excluded: tool-list blogs, popularity rankings, live unauthorized scanning and all license research/ranking.

| Iteration | Query family | New decision-relevant family |
| ---: | --- | --- |
| 0 | systematic REST API fuzzing survey | generation, feedback, state/dependency taxonomy |
| 1 | QuickREST, Morest, RESTler, Schemathesis, EvoMaster | property/stateful/search tool regions |
| 2 | consumer contracts and OpenAPI breaking changes | Pact and spec-diff evolution family |
| 3 | protocol conformance | GraphQL/gRPC/AsyncAPI specialist routes |
| 4 | 2025-2026 coverage-guided and incomplete-spec testing | WuppieFuzz and Overlay/example augmentation |
| 5 | executable semantic contracts/model checking | formal-model oracle family |
| 6 | metamorphic and flakiness testing | metamorphic oracle; failure disambiguation |
| 7 | concurrency/performance/security expansion | no top-level family; refined security/performance strata |
| 8 | current OWASP/competition implementations | no top-level family; added maintained implementations inside existing families |

Iterations 7 and 8 added no top-level family after semantic/metamorphic oracles were included. Saturation is `PASS` for the dated scope.

## Primary anchors

- [Server-side web application fuzzing survey](https://arxiv.org/abs/2406.03208)
- [QuickREST](https://arxiv.org/abs/1912.09686)
- [Morest](https://arxiv.org/abs/2204.12148)
- [OpenAPI fault injection](https://arxiv.org/abs/2607.12101)
- [OAI Overlay for REST fuzzing](https://arxiv.org/abs/2607.04325)
- [REST fuzzing flakiness](https://arxiv.org/abs/2603.28452)
- [IcePick/Glacier](https://arxiv.org/abs/2604.08633)
- [ARMeta](https://arxiv.org/abs/2605.28321)
- [OpenAPI and Overlay specifications](https://spec.openapis.org/)
- [OWASP API Security](https://owasp.org/API-Security/)

