# AdapterProof research decision

Date: 2026-08-05

## Outcome

The systematic evidence gate is `PASS`. Experiment and overall technique-ceiling gates remain `PARTIAL`: A0-A4 are designs, not results.

Fixed real-localhost conformance remains the acceptance truth. A0 is the exact first experiment, followed by Schemathesis/Hypothesis reuse in A1. RESTler, EvoMaster, WuppieFuzz, formal models and security scanners are escalation profiles, not a default tool pile.

## Retained decisions

| Family | Disposition |
| --- | --- |
| fixed exact wire/lifecycle cases | mandatory control |
| common defect/replay/flakiness scorer | A0 |
| Schemathesis + Hypothesis | A1 first generated/stateful candidate |
| OAI Overlay/examples | A1 input augmentation arm |
| RESTler then EvoMaster/WuppieFuzz | A2 only for observed deep-sequence/coverage gaps |
| oasdiff + Pact + runtime replay | A3 complementary evolution gates |
| OWASP security tools | A4 authorized specialist profile |
| TLA+/semantic and metamorphic relations | deferred to critical, reviewable oracle gaps |
| official GraphQL/gRPC/AsyncAPI suites | route only by actual protocol requirement |
| custom generator/diff/mock framework | rejected |

## Exact next controlled work

1. A0 common corpus, reset, finding and mutation-sensitive scorer.
2. A1 adopt Schemathesis rather than write OpenAPI generation logic.
3. A2 only if A1 leaves declared sequence gaps.
4. A3 after generation behavior is reproducible.
5. A4 only inside authorized local/security scope.

No experiment, implementation, polish, merge, push or publication occurred.

## Eleven systematic evidence gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Problem decomposition | PASS | contract through evaluation layers in `TECHNIQUE_TAXONOMY.md` |
| Search protocol | PASS | nine dated iterations |
| Survey coverage | PASS | 2024 systematic survey and 2025-2026 primary work |
| Benchmark coverage | PASS | public corpora plus A0-A4 local seeded design |
| Existing-answer search | PASS | fixed/generated, schema/semantic and protocol questions separated |
| Technique-family saturation | PASS | iterations 7 and 8 added no top-level family |
| Candidate comparison | PASS | `EVIDENCE_MATRIX.csv` |
| Contrary evidence | PASS | incomplete specs, weak oracles, state explosion and flakiness |
| Implementation evidence | PASS | exact pins and reuse map in `GITHUB_IMPLEMENTATION_AUDIT.md` |
| Portfolio fit | PASS | specialized pre-go-live/API evolution evidence; DeliveryGuard is reused rather than duplicated |
| Review status | PASS | all conclusions labelled |

## Claim boundary

Defensible now: exact bounded REST adapter conformance and a systematic pinned plan for generated/stateful, compatibility, security and protocol-specific testing.

Not defensible now: OpenAPI-wide coverage, generated fault discovery, consumer compatibility, OAuth/pagination/security correctness, non-REST conformance, live-provider behavior or production scale.

