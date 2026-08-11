# AdapterProof benchmark design

Date: 2026-08-05

Status: design only. No generated, stateful, compatibility or security experiment was run.

## Questions closed by external evidence

| Question | Closed decision |
| --- | --- |
| Are fixed cases obsolete once fuzzing is added? | no; exact business/wire acceptance and discovery serve different failure classes |
| Does an OpenAPI-valid response prove workflow semantics? | no; behavioral oracles and state predicates are separate |
| Is an OpenAPI document sufficient to generate valid deep tests? | often no; examples, dependencies and semantic constraints materially affect results |
| Does one schema diff prove consumer compatibility? | no; combine spec rules, consumer usage and runtime acceptance |
| Can REST tooling establish GraphQL/gRPC/event conformance? | no; use official protocol-specific suites |

## Common corpus and scorer

- Public: stratified APIs from the EvoMaster/SBFT and APIs.guru corpora, plus OWASP crAPI only in an isolated authorized environment.
- Local: 12 deterministic FastAPI services with 60 operations and seeded defects in mapping, required/optional fields, producer-consumer dependencies, pagination, rate limits, OAuth expiry/refresh, signatures, BOLA/BFLA, concurrency and provider evolution.
- Each defect has an exact oracle and a clean sibling. State is reset by namespace/snapshot; every finding stores tool/version/config/seed/minimized sequence/request-response digest and reproducibility count.
- Metrics: operation/status/schema coverage, valid-operation rate, unique reproducible defects by class, semantic/security precision and recall, time-to-first/last unique defect, flaky rate, generated-suite size, replay success, CPU/RAM and setup/operator minutes.

## A0 — corpus/scorer reconciliation (exact first experiment)

Map the current twenty cases and public-tool outputs to one finding contract. Inject one duplicate finding, one flaky response, one wrong semantic result and one unreachable operation; the scorer must identify each. PASS requires 100% exact seeded-defect classification, stable service resets and unchanged current conformance results.

Budget: local CPU/containers, four hours, no live external APIs.

## A1 — fixed versus generated OpenAPI tests

Compare the current fixed suite, Schemathesis examples, Schemathesis generated independent calls and stateful workflows. Run base OpenAPI alone versus reviewed Overlay/example augmentation. Freeze 15/30/60-minute budgets and five repetitions.

Promote Schemathesis if it preserves all fixed gates and finds at least one held-out defect class not covered by fixed cases with at least 95% replay success, under 10% flaky findings and a 15-minute CI profile. Overlay is retained only if valid-operation rate or unique semantic defects improve materially without hiding a base-spec defect.

## A2 — deeper sequence escalation

Run only if A1 misses seeded dependencies of length 3+. Compare RESTler first; add EvoMaster or WuppieFuzz only when its feedback mode matches an observed gap. Keep service/reset/budget identical. A tool must add at least two reproducible held-out deep-state defects or 10 points of state/operation coverage beyond A1 within a one-hour budget to justify its runtime. Generated request count alone is not a win.

## A3 — evolution and consumer compatibility

Create 24 provider changes: operation/field removal, requiredness/type/enum/auth changes, additive fields/operations and runtime semantic changes without schema change. Compare oasdiff, Pact Python consumer contracts, generated SDK compile/smoke and AdapterProof runtime replay.

Hard gate: every change relied on by the frozen consumer must be caught by at least one release gate; false blocks on additive unused changes are reported. The decision artifact explains which layer caught each change—no aggregate “compatibility score.”

## A4 — auth, rate, pagination, signatures and security (conditional)

Add explicit OAuth token lifecycle, cursor/link pagination, rate-limit recovery, raw-body signature/key rotation and two-principal authorization profiles. Reuse OWASP/EvoMaster security oracles only in the authorized fixture. Hard-fail unauthorized effect/data access; report false positives, lockout/rate side effects and replayability. This profile cannot be run against an unapproved provider sandbox.

## Protocol route

GraphQL uses the `graphql-http` audit plus project policy cases; gRPC uses the official interop suite; event APIs use AsyncAPI plus broker-specific behavior. A separate protocol profile is admitted only by an actual client requirement and never contributes to a generic REST claim.

## Stopping rules

- Stop after A1 if fixed + Schemathesis covers every seeded class and deeper tools add no unique defect.
- Stop a tool after two consecutive budget tiers add no reproducible unique defect.
- Re-run every candidate failure at least three times after reset; quarantine flakiness instead of counting it.
- Keep generation and oracle contributions separate.
- Prefer importing tool-native repro output over writing a new generator or minimizer.

