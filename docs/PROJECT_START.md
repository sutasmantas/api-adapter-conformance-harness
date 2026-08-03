# AdapterProof project start

## 1. Restart boundary

- repository: `portfolio_demos/adapter_proof`
- baseline branch and commit: local `main` at pinned pytest-httpserver commit
  `44b3c9123cf4861d9ceda34fd5c0077cd53d03b4`
- original implementation branch: `agent/adapter-proof-depth`
- component-reuse branch: `agent/adapter-proof-component-reuse`
- assigned isolated worktree:
  `portfolio_demos/worktrees/adapter_proof_component_audit`
- owner/session: non-Context portfolio stream, depth slice 4
- repositories/worktrees that are read-only: ContextSidecar and all portfolio
  repositories except the packaged DeliveryGuard release read from its clean
  local `main`
- exact next action: record and verify the retrospective component-level
  GitHub audit before re-closing slice 4

Never share an active worktree or switch branches inside an assigned worktree.

## 2. Client outcome and non-duplication

- one client-purchased outcome this project proves: verify a client-owned HTTP
  integration's authentication reference, mapping, idempotency, retry,
  dead-letter, replay, and evidence behavior before live credentials/go-live
- existing portfolio evidence closest to it: Relay's generic outbound adapter
  and DeliveryGuard's reusable delivery lifecycle
- mechanism or deliverable that is genuinely new: declarative adapter manifests
  executed against real local HTTP expectations with a case-level conformance
  report
- why this is better coverage than deepening an existing project: it turns
  reusable delivery behavior into a repeatable integration acceptance process
  without manufacturing named-provider claims

## 3. GitHub foundation comparison

Licensing was deliberately excluded from discovery and selection.

| Candidate | Repository | Activity/version checked | Central behavior reusable for this MRE | Adaptation cost/risk | Decision |
| --- | --- | --- | --- | --- | --- |
| pytest-httpserver | `https://github.com/csernazs/pytest-httpserver` | `44b3c91`, current GitHub `master`, checked 2026-08-01 | real localhost HTTP server, ordered/one-shot expectations, exact request/header/JSON matching, request log, standalone context manager | low: directly exercises DeliveryGuard's real urllib request boundary | selected |
| RESPX | `https://github.com/lundberg/respx` | `57d8c29`, current GitHub `master`, checked 2026-08-01 | HTTPX route matching, side effects, pytest fixture | medium/high: patches HTTPX only and would require changing or bypassing the consumer's actual transport | rejected |
| WireMock | `https://github.com/wiremock/wiremock` | current GitHub `master`, checked 2026-08-01 | rich standalone matching, request verification, delays, faults, stateful behavior | high: Java/standalone runtime and broad feature surface are unnecessary for this bounded Python harness | rejected |

Selected foundation:

- repository URL: `https://github.com/csernazs/pytest-httpserver.git`
- pinned tag/commit: `44b3c9123cf4861d9ceda34fd5c0077cd53d03b4`
- exact code/package/contracts reused: `HTTPServer`, ordered and one-shot
  expectations, JSON/header matchers, response builders, request log, and
  assertion checks
- upstream history/identity preservation: cloned history is retained and the
  source remote is named `upstream`
- why this is faster/safer than starting blank: the harness uses a tested real
  localhost server and exact request matching instead of inventing another mock
  transport

## 4. Component-level GitHub reuse audit

The original repository-foundation comparison did not separately audit all
substantial custom layers. `docs/COMPONENT_REUSE_AUDIT.md` corrects that process
gap before any refit:

| Proposed component | Candidates checked | Decision | Exact boundary |
| --- | --- | --- | --- |
| manifest/schema validation | Pydantic, python-jsonschema | `custom` after measured Pydantic prototype | retain one strict 120-line parser/model; both candidates add glue or a second source of truth without removing domain validation |
| nested mapping | glom, JMESPath | `custom` | retain the 42-line bounded reader/writer because candidates add a broader DSL or solve only reads |
| conformance orchestration/report | Schemathesis, Pact Python, Tavern | `custom` over adopted pytest-httpserver + DeliveryGuard | retain exact receipt/retry/replay orchestration; avoid a second incompatible contract model |

Candidate commits, total integration-cost decisions, and rejected overlap are
recorded in the audit. Discovery and selection did not use licensing.

## 5. Distinct visual direction

Not applicable. AdapterProof is a package/CLI/report artifact with no UI.
Creating a dashboard would duplicate existing portfolio surfaces and add no
integration evidence. If a UI becomes client-required, the full rendered
portfolio comparison gate must be completed first.

## 6. Minimum referenceable evidence contract

| Gate | Observable acceptance evidence | Status |
| --- | --- | --- |
| Central similarity | pytest-httpserver handles real local wire expectations and inspection | PASS |
| Component-level reuse decisions | all substantial custom layers audited; three bounded custom decisions recorded with measured integration cost | PASS |
| Working vertical slice | manifest + canonical event -> mapped request -> DeliveryGuard -> report | PASS |
| No-key deterministic proof | fake providers and referenced test secret only | PASS |
| Invalid input and abuse behavior | malformed manifests/mappings/secret refs and key collisions refuse | PASS |
| Provider/tool failure and retry/refusal/handoff | success, 409, 429, 4xx, 5xx, malformed, dead-letter, replay | PASS |
| Focused mechanism tests | manifest, mapping, wire expectations, report, DeliveryGuard receipts | PASS |
| Clean-checkout quickstart | vendored verified DeliveryGuard wheel + install/test/run/build | PASS |
| Cover-letter claim ledger | generic-integration claims mapped to case evidence | PASS |
| Honest unsupported-claim boundary | no named SaaS, live credential, production, or exactly-once claim | PASS |

## 7. Verification and handback

- static/type/lint command: `python -m ruff check adapterproof
  tests/test_adapterproof.py`, `python -m ruff format --check adapterproof
  tests/test_adapterproof.py`, and `python -m mypy adapterproof` pass
- focused tests: `python -m pytest tests/test_adapterproof.py -q` -> 13
  passed
- retained foundation behavior: 107 core tests passed, 3 skipped; 23 examples
  passed, 1 expected failure
- integration/demo command: `adapterproof run --output
  .evidence/report.json` -> PASS, 2 adapters, 20 cases; repeated report SHA-256
  `07DBC48C4A27F1C11CC6E63DCB1B5F0E3E13D3724B552D93ADE723CE2C9020CF`
- build/package command: `python -m build` and `python -m twine check
  dist/*` pass; Docker image build/run prints PASS
- branch and final commit: `agent/adapter-proof-depth`; exact closure and merge
  commits are recorded in `docs/EXECUTION_CHECKPOINT.md`
- clean state: detached evidence-commit verification passed from a fresh venv;
  generated verification worktree removed
- known boundaries: generic local HTTP fixtures only; see
  `docs/CLAIM_LEDGER.md`
- exact next portfolio action: close slice 4 before starting the LedgerLens
  heterogeneous-document benchmark
