# AdapterProof component-level GitHub reuse audit — 2026-08-03

## Why this exists

The initial AdapterProof start gate compared repository foundations and adopted
pytest-httpserver, but it did not separately search GitHub before implementing
the manifest, mapping, and conformance-runner layers. This retrospective audit
closes that process defect before slice 5. Licensing was not researched,
filtered, compared, or ranked.

Decision rule: adopt or refit when a component removes a complete
responsibility with bounded glue and testable behavior. Keep a bounded custom
component when candidates solve a materially different problem, replace only a
tiny function, or add more runtime, glue, testing, and upgrade surface than
they remove. Do not combine overlapping tools merely to increase reuse.

## Component decisions

| Proposed component | GitHub candidates and checked pins | Decision | Exact reused surface or custom boundary | Total integration-cost evidence |
| --- | --- | --- | --- | --- |
| Strict manifest/schema validation | Pydantic `v2.13.4` / `cf67d4b3193c3fe43ede18612ed62785eee11382`; python-jsonschema `v4.26.0` / `a7277432b0f7bcd0551f6e589d30457017125df4` | **Custom after measured prototype** | retain the frozen dataclass plus one strict parser containing AdapterProof's exact JSON, header, path, environment-reference, default, and collision contract | A Pydantic prototype increased the module from 120 to 135 logical lines and introduced 108 new integration lines to replace 78 parser lines; domain validators still remained, plus a compiled runtime dependency and upgrade gate. jsonschema would require both a schema and a conversion/model layer, creating two sources of truth. Neither removes enough responsibility to justify the glue. |
| Bounded nested JSON mapping | glom `30b477ab65560914a38f331614947d0894701044`; JMESPath Python `2812594e69d43098ef60f81f4efc404c071b0418` | **Custom** | retain `mapping.py`: safe dot-path reads, deterministic nested writes, deep-copy isolation, missing-source refusal, and target-collision refusal | Current implementation is 42 logical lines. JMESPath provides source querying but not safe target construction, so it would leave most code plus a new expression language. glom can transform and read/write nested data but exposes a much broader spec surface and new exception/upgrade behavior. Either adds more integration and test surface than this deliberately restricted mapper. |
| Delivery lifecycle conformance orchestration and report | Schemathesis `97545f28106171c800ed258f970b9170a957d62d`; Pact Python `0027fc196b59f1d663056df6102497439710e05a`; Tavern `c629c67cc644a493a6d6435310d17e46e7020613`; already-adopted pytest-httpserver `44b3c9123cf4861d9ceda34fd5c0077cd53d03b4` | **Custom orchestration over adopted components** | retain the explicit ten-case runner/report while continuing to reuse pytest-httpserver for real wire expectations and DeliveryGuard for idempotency, outcome classification, receipts, dead-letter, and replay | Schemathesis is OpenAPI/GraphQL property testing, Pact is consumer-provider contract generation/verification, and Tavern introduces a YAML REST-test model. None exposes DeliveryGuard action/receipt lifecycle assertions. Adopting one would require a second schema/contract DSL plus adapters back into the same custom state/report logic. That is integration and upgrade burden without removing the central runner responsibility. |
| Report serialization and CLI plumbing | standard library dataclasses/JSON/argparse; no separate substantial component | **Custom/trivial** | deterministic dictionary/JSON serialization and one `run` command | The behavior is small and already supplied by the Python standard library. A reporting or CLI framework would add dependency surface without removing meaningful logic. |

## Prototype result and implementation scope

The Pydantic option was prototyped only after the audit commit. It made the
implementation larger and did not eliminate the domain-specific validators, so
the uncommitted prototype was discarded. No product implementation change is
required by this audit.

No Pydantic, python-jsonschema, glom, JMESPath, Schemathesis, Pact, Tavern, or
additional reporting/CLI framework will be integrated. That restraint is part
of avoiding integration hell, not a failure to reuse. AdapterProof continues
to reuse pytest-httpserver for the real HTTP contract and DeliveryGuard for the
delivery lifecycle—the two components that each remove a complete
responsibility.

## Upgrade boundary

- The three deliberately custom layers remain bounded by focused tests. Reopen
  validation if manifest variants multiply enough that duplicated manual shape
  logic appears; reopen mapping for arrays/conditionals/transforms; reopen the
  runner for an OpenAPI provider contract, cross-team provider verification,
  or a materially different report transport.
- Any future candidate must reduce total custom responsibility after glue, not
  merely replace local lines with framework-specific validators or adapters.
