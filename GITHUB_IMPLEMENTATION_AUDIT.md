# AdapterProof GitHub implementation audit

Date: 2026-08-05

Purpose: adopt maintained generation, compatibility and protocol components before writing substantial test logic. Licenses are intentionally ignored; fitness, health, observed limitations and integration cost control adoption.

## Current seams

- `manifest.py` parses the bounded adapter contract.
- `mapping.py` resolves canonical-event fields.
- `adapter.py` builds the exact outbound request.
- `runner.py` executes cases and records lifecycle evidence.

Generated tools should emit through or compare against those seams. The fixed runner remains the final exact acceptance layer.

## Repository comparison

| Repository and inspected pin | Health | Reusable component | Boundary/defect risk | Decision |
| --- | --- | --- | --- | --- |
| [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis) `e8ac447` | active 2026-08-04; 10 open issues | OpenAPI/GraphQL generation, shrinking, stateful workflows and repro | valid requests depend on spec/examples and state reset | first generated-test integration; do not rebuild OpenAPI strategies |
| [microsoft/restler-fuzzer](https://github.com/microsoft/restler-fuzzer) `6d984de` | active 2026-06-10; 298 open issues | dependency inference, sequence exploration, replay | .NET/Docker and longer workflow; first examples/dependencies can constrain exploration | escalation only after A1 sequence gap |
| [WebFuzzing/EvoMaster](https://github.com/WebFuzzing/EvoMaster) `56a22a0` | active 2026-08-04; 46 open issues | black/white-box search, security oracles, generated tests | JVM/driver/run-time/flakiness burden | deep/security escalation, not default |
| [TNO-S3/WuppieFuzz](https://github.com/TNO-S3/WuppieFuzz) `b6e4ec2` | active 2026-08-03; 33 open issues | coverage-guided LibAFL stateful fuzzer | young tool, Rust/instrumentation integration | reference/benchmark candidate only |
| [pact-foundation/pact-python](https://github.com/pact-foundation/pact-python) `7d4c025` | active 2026-08-05; 18 open issues | consumer contract generation/provider verification | only proves expressed consumer interactions | A3 consumer-usage profile |
| [oasdiff/oasdiff](https://github.com/oasdiff/oasdiff) `fb8babb` | active 2026-08-03; 35 open issues | OpenAPI 3.0/3.1 change/breaking rules | spec diff cannot prove runtime compatibility | A3 schema-evolution gate beside Pact/runtime replay |
| [stoplightio/prism](https://github.com/stoplightio/prism) `82b4aa5` | active 2026-08-04; 147 open issues | OpenAPI mock/validation | mock can agree with the same defective spec | development convenience only |
| [wiremock/wiremock](https://github.com/wiremock/wiremock) `109b55e` | active 2026-08-05; 497 open issues | programmable HTTP state/fault server | Java service is disproportionate to current pytest-httpserver needs | do not replace current local server without a missing fault case |
| [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis) `5b20755` | active 2026-08-05; 43 open issues | strategies, shrinking, state machines | direct OpenAPI strategy code would duplicate Schemathesis | use through Schemathesis; direct only for manifest/mapping invariants |
| [OAI/OpenAPI-Specification](https://github.com/OAI/OpenAPI-Specification) `5423da4` and [Overlay](https://github.com/OAI/Overlay-Specification) `2b27df8` | active | normative schemas and separate augmentation format | tool support differs across 3.0/3.1/3.2 and overlay versions | pin supported spec/version matrix and validate fixtures |
| [graphql/graphql-http](https://github.com/graphql/graphql-http) `08b4ed2` | not archived; last push 2025-10; 11 issues | official GraphQL-over-HTTP audit suite | protocol-specific | reuse if GraphQL enters scope; never emulate through REST mapping |
| [asyncapi/spec](https://github.com/asyncapi/spec) `5648e62` | active 2026-07-30; 43 issues | event/API specification | description is not broker/runtime conformance | protocol-specific future profile |
| [OWASP/crAPI](https://github.com/OWASP/crAPI) `73d309c` and [ASTF](https://github.com/OWASP/www-project-api-security-testing-framework) `61ec39c` | active; intentionally vulnerable corpus + young test tool | authorized security fixtures and multi-principal checks | findings/oracles require review; never run against unauthorized live APIs | reuse corpus/profile only when A4 security is in scope |
| [APIs-guru/openapi-directory](https://github.com/APIs-guru/openapi-directory) `f04b8d0` | active but 1,700 issues | diverse public OpenAPI corpus | specs and live services drift; not acceptance truth | stratified parser/generator robustness corpus only |

## Reuse map before custom logic

| Need | First reuse source | Thin AdapterProof ownership |
| --- | --- | --- |
| OpenAPI generation/shrinking | Schemathesis/Hypothesis | canonical-event and exact lifecycle adapter; reset/reconciliation |
| semantic valid inputs | OAI Overlay/examples | reviewed seed file and base-spec drift check |
| deeper sequences | RESTler, then EvoMaster if needed | shared corpus/scorer/replay import |
| breaking-change detection | oasdiff | supported version policy and client/runtime acceptance |
| consumer assumptions | Pact Python | map real consumer interactions to exact provider verification |
| security | OWASP corpus/ASTF or EvoMaster oracle | authorized principals, business policy predicates and confirmation |
| non-REST | official protocol conformance suite | only project-specific policy/lifecycle wrapper |

## Explicit non-adoptions

- Do not write an OpenAPI strategy engine, shrinker, sequence dependency engine or contract diff from scratch.
- Do not run RESTler, EvoMaster and WuppieFuzz together before Schemathesis establishes the remaining gap.
- Do not count unique status codes, repeated flaky failures or raw 5xx volume as integration correctness.
- Do not let a mock generated from the same spec prove the real provider.
- Do not claim a spec diff or Pact contract alone proves backward compatibility.
- Do not scan any live API without explicit authorization and isolated test identities.

## Minimal integration checks

1. Preserve all current exact request/lifecycle cases and report generated tests separately.
2. Pin OpenAPI/JSON Schema versions and include circular refs, oneOf/anyOf, nullable, formats and malformed specs.
3. Reset or namespace state per generated example; replay every finding from a seed/minimal sequence.
4. Count reproducible unique semantic/security failures, not request volume.
5. Run multi-principal authorization cases only with explicit expected policy.
6. Keep every optional generator/protocol profile removable without changing fixed manifest behavior.

