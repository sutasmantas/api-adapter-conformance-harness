# AdapterProof execution checkpoint — 2026-08-03

## OpenAPI toolbox slice — 2026-08-06

- implementation branch/worktree: `agent/toolbox-api-verification` at
  `portfolio_demos/worktrees/adapter_proof_api_toolbox`;
- public-snapshot branch/worktree: `agent/openapi-publication-snapshot` at
  `portfolio_demos/worktrees/adapterproof_openapi_publication`;
- clean base: `c70186d5308242b4e63b597aa55b9b08445f8d67`
- scope: make AdapterProof the reusable owner of the bounded Schemathesis
  contract already proven by the portfolio-level Phase 2 experiment;
- security-specific work: postponed to the final toolbox backlog;
- license research: excluded by user direction.

Current gate: **PUBLICATION_SNAPSHOT_READY_HOSTED_REUSE_PENDING**.

| Gate | Evidence | Status |
| --- | --- | --- |
| bounded contract/config validation | `adapterproof/openapi.py`; fuzzing, unknown fields, invalid paths, ports and budgets rejected | PASS |
| result semantics | `FatalError` overrides ambiguous exit `1`; budget and expectation exit codes differ | PASS |
| reusable CLI and workflow | `adapterproof openapi`; `.github/workflows/openapi-contract.yml` | PASS |
| focused static/test gate | Ruff, format, strict mypy; 24 tests | PASS |
| real Ledger consumer | commit `1bf1b65285ac46e90aebd210c9691631d7d35a7a`; 8/8 cases, `NO_FINDINGS`, receipt summary | PASS |
| real Relay consumer and discovered-contract regression | commit `ac292e158a52bdddbaa32bcf13e8297fb21f3b6b`; 77/77 cases, `NO_FINDINGS`; boolean/integral-number boundary regressed | PASS |
| package and retained regression | build/Twine pass; 24 focused, 107 retained + 3 skipped, 23 examples + 1 expected failure | PASS |
| hosted cross-repository reuse | provider and consumer workflows have not executed from their remotes | PENDING |

Exact next action: publish the current tip of
`agent/openapi-publication-snapshot` first, verify its provider workflow, then
publish the Ledger Lens and Relay snapshot branches that pin that immutable
tip. Preserve both consumer GitHub run URLs. Local cross-project reuse is
proven; hosted cross-repository reuse must not be claimed yet.

First real-consumer mutation: Relay's generated-case volume filled the captured
Uvicorn access-log pipe and produced `NonFatalError` network timeouts, which the
first classifier mislabeled as findings from exit code `1`. The corrected
runner suppresses access logs and classifies any `NonFatalError` as `RUN_ERROR`.
Both consumers must pin the public snapshot containing the correction, not the
foundation-only commit `2728d8d`.

## Restart boundary

- repository: `portfolio_demos/adapter_proof`
- local integration branch: `main` at component-audit merge
  `27455c99cc7fe44b3fbbe8f8040c48435f942c59`
- completed implementation branch: `agent/adapter-proof-depth`
- foundation commit: `44b3c9123cf4861d9ceda34fd5c0077cd53d03b4`
- project-start commit: `ddb567559eb8d69f0e52b5b611915f3b57a6a906`
- application commit: `f58c465eb12b4d0bd539ff178a89d73d874a4fd5`
- evidence commit: `17cf68b561da0aceb8896618bec026694f0f631e`
- closure commit: `28af38c3202d337a393d2c6f02c369d58808005d`
- original integration-checkpoint commit:
  `27da9f4fbd3481c1ffcb35005532f4aeaa0b50a1`
- final component-audit checkpoint: this file's commit
- assigned worktree: `portfolio_demos/worktrees/adapter_proof_depth`
- publication worktree:
  `portfolio_demos/worktrees/adapterproof_publication`
- publication branch: `agent/adapterproof-publication`
- publication baseline:
  `6dd45c0271ee41354b5019fa34824d52c3a3f768`
- publication contract commit: `ecd1bcc`
- report-viewer commit: `0097d23`
- local publication-package commit: `e0310b3`
- ContextSidecar: excluded and untouched

## Publication gate — 2026-08-03

The local client-readable package is complete, but the controlling publication
gate is not closed because no user-owned public remote exists. Do not begin
DeliveryGuard from this checkpoint.

| Gate | Evidence | Status |
| --- | --- | --- |
| Clean restart | exact `6dd45c0` baseline; named branch; isolated worktree; canonical `main` stayed clean | PASS |
| Real source data | viewer and all media read the generated report; repeated report SHA-256 `D413DDC4…A0E07` | PASS |
| One bought outcome | cover leads with verifying an API adapter before go-live | PASS |
| Distinct visual identity | dark protocol lab with wire map and case rail; no PipelineForge reconciliation table or DeliveryGuard incident timeline | PASS |
| Upload package | three PNGs and one MP4 under `final_upload/` | PASS |
| Image quality | each PNG is 1600×1200; automated bounds check and manual inspection passed | PASS |
| Video quality | H.264/yuv420p, 1600×1200, 20.76 seconds; five representative frames inspected | PASS |
| Canonical copy | 58-character title, 64-character role, 527-character description, five skills, exact media order and claim boundary in the central copy source | PASS |
| Repository proof | publication commit `80c1ef4` is verified on the user-owned public repository `https://github.com/sutasmantas/api-adapter-conformance-harness`; local publication merge `c2dea03` is ready to push | PASS |
| Final validation | 144 passed, 3 skipped, 1 expected failure on clean Linux; Ruff, format, strict mypy, package/Twine, Docker, desktop/mobile browser and media checks pass; public source proof is present | PASS |

Detailed commands, media metadata and claim limits are recorded in
`docs/PUBLICATION_EVIDENCE.md`.

## Exit gate

| Gate | Evidence | Status |
| --- | --- | --- |
| GitHub-first foundation | pytest-httpserver history retained at `44b3c91`; RESPX and WireMock compared before implementation; licensing excluded | PASS |
| Component-level GitHub audit | manifest, mapping, runner, and report/CLI layers separately compared; measured `custom` decisions avoid higher-cost glue while pytest-httpserver and DeliveryGuard remove complete responsibilities | PASS |
| Central foundation behavior | direct `HTTPServer`, ordered expectations, exact headers/JSON, request log, and assertion checks | PASS |
| Functional vertical slice | canonical event + manifest -> mapped real localhost request -> DeliveryGuard -> case report | PASS |
| Mapping and auth boundary | two structurally different generic manifests; exact mapping/header tests; secrets referenced from environment | PASS |
| Failure lifecycle | 20 cases cover success, 409, 429 recovery, 503 exhaustion, 422, malformed response, duplicate, collision, dead-letter replay, and missing secret | PASS |
| Durable/redacted evidence | DeliveryGuard receipt sequences match exactly; fixture secret absent from SQLite; contact/message values redacted in report | PASS |
| Focused verification | 13 AdapterProof tests pass | PASS |
| Retained foundation regression | 107 core passed, 3 skipped; 23 examples passed, 1 expected failure | PASS |
| Static verification | Ruff lint/format and strict mypy pass | PASS |
| Package verification | wheel/sdist build and Twine checks pass; wheel contains only AdapterProof plus metadata | PASS |
| Container verification | clean image build and run prints PASS for two adapters | PASS |
| Clean-checkout verification | detached `17cf68b` fresh install/lint/type/test/build/Twine/report/Docker checks pass; checkout clean | PASS |
| Claim boundary | `docs/CLAIM_LEDGER.md` prohibits named-provider, OAuth, production, scale, exactly-once, deployment, and client-outcome claims | PASS |

## Verification commands and results

- `python -m ruff check adapterproof tests/test_adapterproof.py` -> pass
- `python -m ruff format --check adapterproof tests/test_adapterproof.py` ->
  8 files already formatted
- `python -m mypy adapterproof` -> no issues in 7 source files
- `python -m pytest tests/test_adapterproof.py -q` -> 13 passed
- retained core suite with a 15-second per-test guard -> 107 passed, 3
  skipped
- retained examples with a 15-second per-test guard -> 23 passed, 1 xfailed
- `adapterproof run ...` twice -> PASS, 2 adapters, 20 cases, identical
  SHA-256 `07DBC48C...C9020CF`
- `python -m build` and `python -m twine check dist/*` -> pass
- `docker build ...` and `docker run --rm ...` -> PASS

The original retained `tests/test_release.py` is excluded: its four tests
hard-code the upstream `pytest-httpserver` distribution name and exact file
inventory. AdapterProof replaces that package identity, so its own build,
wheel-content, Twine, fresh-install, and Docker checks are the applicable
release gate.

## Commits

- `ddb567559eb8d69f0e52b5b611915f3b57a6a906` — compare and pin the
  GitHub foundation and freeze the evidence contract
- `f58c465eb12b4d0bd539ff178a89d73d874a4fd5` — implement the adapter
  conformance package, fixtures, tests, CI, and Docker path
- `17cf68b561da0aceb8896618bec026694f0f631e` — record the deterministic
  report, expertise note, and claim limits
- `28af38c3202d337a393d2c6f02c369d58808005d` — close every slice gate
- `de4a28e64e58013efec8ea14a09c01238b242f28` — merge the verified branch
  into local `main`
- `80b5f1208cfce9a6eac33f1959465034e0c1868a` — record the retrospective
  component-level GitHub audit before prototyping a refit
- `281d1e459ce62604b491a99315090c27ee632b67` — record measured reuse
  decisions after discarding the higher-cost Pydantic prototype
- `f140b8272e89a74b747331ff83a2d3ce43d80769` — close the component-level
  audit gate
- `27455c99cc7fe44b3fbbe8f8040c48435f942c59` — merge the component-level
  audit into local `main`
- `80c1ef46d25bcfaed9ca9b4d0dd1dafe77ab19a0` — close the publication
  package and every local media/verification gate
- `c2dea0305206a02c9c74dd8e36a4dc161cb05ad8` — merge the verified
  publication branch into local `main`

## Remaining limitations

- The fixtures represent generic record and notification sinks, not any named
  CRM, calendar, messaging, or automation provider.
- Authentication covers environment-referenced static secrets; OAuth, token
  refresh, and webhook signatures are not implemented.
- The proof is local and deterministic. There is no remote, deployment,
  production traffic, uptime, throughput, concurrency, or client-outcome
  evidence.
- Delivery semantics remain at-least-once and depend on the destination
  honoring the idempotency key; distributed exactly-once effects are not
  claimed.
- Endpoint allowlisting and private-network/SSRF controls remain consuming
  application responsibilities.
- The manifest intentionally supports bounded dot-path JSON mapping, not
  arbitrary transforms or provider-specific retry headers.
- Manifest validation, nested mapping, lifecycle orchestration, and report/CLI
  glue remain portfolio-owned bounded code after the candidate and integration-
  cost audit in `docs/COMPONENT_REUSE_AUDIT.md`; reopen only when the stated
  requirement triggers appear.
- The publication viewer is a bounded read-only rendering of the real report;
  no hosted validation service, named SaaS breadth, or product dashboard is
  claimed.

## Exact next action

Push the merged `main` checkpoint to the verified user-owned public remote,
promote AdapterProof from `publication-ready-local` to `active` in the central
evidence registry, and update the cross-portfolio checkpoint. AdapterProof's
publication gate is all `PASS`; after those bookkeeping updates the separate
DeliveryGuard publication branch may begin. Keep the borrowed foundation only
as `upstream`.
# Technique-dossier checkpoint — 2026-08-05

- Branch: `agent/adapter-proof-technique-dossier`
- Clean base: `main` at `c70186d5308242b4e63b597aa55b9b08445f8d67`
- Dossier commit: `45ad035`
- Systematic evidence gate: `PASS` (all eleven gates in
  `RESEARCH_DECISION.md`).
- Experiment/technique-ceiling gate: `PARTIAL`; A0-A4 are designs only.
- Verification: `python -m ruff check adapterproof
  tests/test_adapterproof.py` and `python -m pytest -q
  tests/test_adapterproof.py` -> 14 passed.
- Remaining limitations: no OpenAPI generation/stateful result, compatibility
  result, OAuth/pagination/security profile, non-REST conformance, live
  provider evidence or production scale.
- Exact next action: A0 common corpus/reset/finding scorer, then A1 fixed
  control versus adopted Schemathesis/Hypothesis. Do not write a custom
  generator before that component experiment.
