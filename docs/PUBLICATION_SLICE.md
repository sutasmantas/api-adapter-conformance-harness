# AdapterProof publication slice

Date: 2026-08-03

## Acceptance contract

This slice is presentation over existing execution evidence, not a new test
engine. It passes only when:

- the canonical `adapterproof run` command still generates 20 passing cases;
- the viewer reads that generated JSON without maintaining a second result
  model or hard-coded pass counts;
- each adapter exposes its exact method, path, safe header contract, redacted
  mapped payload, manifest hash, and case receipts;
- the rate-limit recovery, exhausted server failure, duplicate suppression,
  idempotency collision, dead-letter replay, and missing-secret paths remain
  inspectable;
- desktop and mobile browser flows have no clipping, overlap, or horizontal
  page overflow;
- the final upload package contains three 1600x1200 PNGs and one 15–22 second
  MP4, all sourced from the real report;
- canonical Upwork copy keeps the local, generic-adapter, no-OAuth, no-scale,
  and at-least-once boundaries explicit.

Publishing to a user-owned public remote is a separate external action and is
not implied by creating this local branch.

## Reuse and implementation decision

The technical foundation and component audit remain closed at `6dd45c0`.
This publication surface introduces no substantial application subsystem:

| Responsibility | Candidates considered | Decision | Reason |
| --- | --- | --- | --- |
| Report truth | existing generated `conformance-report.json`; new API/model | adopt existing report | A second model would duplicate the test engine and could drift. |
| Read-only browser surface | React/Vite; a copied dashboard; browser-native HTML/CSS/JS | custom browser-native view | The surface is one JSON reader with adapter/case selection. A framework adds install, build, upgrade, and clean-checkout work without removing a responsibility. |
| Local serving | Flask/FastAPI; Python standard-library HTTP server | refit standard-library handler | The viewer needs only static assets plus one report route; a web framework would be larger than the bounded code. |
| Browser capture | portfolio Playwright/Chromium tooling | adopt existing local tooling | Reuse the already-proven capture environment; do not add a runtime dependency to AdapterProof. |

No GitHub search is warranted for the tiny selection/render functions. The
repository-level and component-level audits already cover the actual adapter,
mapping, orchestration, persistence, and test responsibilities. Reopening
those decisions for a read-only view would create the integration work this
portfolio policy is designed to avoid.

## Distinct visual identity

The existing portfolio comparison includes pale editorial covers, dense
evaluation grids, appointment ledgers, call timelines, and pipeline
reconciliation tables. AdapterProof uses a different structural metaphor:

- full-bleed dark protocol lab rather than a pale marketing shell;
- compact vertical adapter switcher and case strip rather than a run sidebar;
- central source-to-wire contract with signal traces rather than a matrix,
  reconciliation table, or incident timeline;
- cyan/acid-lime status language with monospace payload evidence;
- no duplicate PipelineForge reconciliation layout and no DeliveryGuard
  attempt-timeline hero.

The visual identity is frozen before implementation so the publication media
does not require a later structural redesign.
