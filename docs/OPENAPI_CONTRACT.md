# Reusable OpenAPI contract gate

AdapterProof owns a bounded adapter around the pinned GitHub implementation at
`schemathesis/schemathesis@40e71c4657c79be08ea772b612a121b0e0ac7142`.
The upstream tool generates and checks cases; AdapterProof owns the portfolio
contract: process isolation, fixed controls, receipt shape, outcome
classification, and GitHub reuse.

Consumers provide one `adapterproof.openapi.json` file. The admitted region is
intentionally narrow:

- a real Uvicorn/TCP boundary and real OpenAPI document;
- a separate tool interpreter and consumer interpreter;
- deterministic `coverage` only, one worker, exact path regex, fixed seed;
- disposable consumer data and a 1–300 second budget;
- NDJSON classification where `FatalError` overrides the CLI's ambiguous exit
  code `1`, and any `NonFatalError` makes the run incomplete rather than a
  product finding;
- suppressed consumer access logs so generated-case volume cannot block the
  service on an undrained subprocess pipe.

`NO_FINDINGS` is the default expected result. A frozen mutation run may declare
`--expect findings`. Budget, startup, and schema-load failures are operational
errors and can never satisfy either expectation.

Unrestricted fuzzing remains outside this contract because Phase 2 showed that
shrinking could exceed the fixed budget. That limitation is visible rather
than silently weakened.
