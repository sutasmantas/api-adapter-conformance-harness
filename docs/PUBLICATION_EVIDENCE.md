# AdapterProof publication evidence

Date: 2026-08-03

## Result

The bounded local publication package is complete. The read-only protocol-lab
viewer consumes the generated conformance report, and all four upload assets
are derived from that same report. The public-repository gate remains open.

## Source-of-truth controls

- `adapterproof run` generated two adapters and 20 passing cases.
- Two independent runs produced byte-identical report SHA-256
  `D413DDC4976BC7970F3AAF66A6BE775E162F177F62F4ACBF4E90148E13CA0E07`.
- The report now carries the exercised method, endpoint path, safe header
  contract, manifest identity, redacted mapped body, request count, final
  state, and receipt sequence.
- The viewer serves the report unchanged from `/api/report`; it does not
  maintain a second pass count or result model.
- Generated report text is inserted with `textContent`, not `innerHTML`, so a
  payload or header placeholder cannot become executable markup.

## Functional and static verification

Commands:

```powershell
.\.venv\Scripts\python.exe -m ruff check adapterproof tests/test_adapterproof.py
.\.venv\Scripts\python.exe -m ruff format --check adapterproof tests/test_adapterproof.py
.\.venv\Scripts\python.exe -m mypy adapterproof
.\.venv\Scripts\python.exe -m pytest tests/test_adapterproof.py -q
```

Results at the publication candidate:

- Ruff lint: pass
- Ruff format: pass
- strict mypy: pass across eight source files
- focused suite: 14 passed
- clean Linux regression suite with signal-based 15-second per-test guard:
  144 passed, 3 skipped, 1 expected failure in 25.90 seconds. This includes
  the 14 AdapterProof tests plus the retained foundation and example tests;
  only the obsolete upstream release-identity file is excluded, as before.

Package and container checks:

- wheel and sdist build: pass;
- Twine validation: pass;
- wheel inventory contains all six report/publication viewer assets;
- fresh Docker image build: pass;
- container default run: `PASS`, two adapters, 20 cases.

## Browser verification

The report viewer was exercised in headless Chrome with the existing portfolio
Playwright environment:

- 1440×1000 desktop: adapter switch, idempotency-collision case, exact
  `/v2/notifications` path, `collision refused` state, zero horizontal
  overflow, and no viewport-clipped elements;
- 390×844 mobile: the same interaction and assertions, zero horizontal
  overflow, and no viewport-clipped elements;
- the safe auth text rendered literally as
  `Bearer <resolved from env:ADAPTERPROOF_NOTIFICATION_TOKEN>`.

## Upload package

| File | Evidence | Validation |
| --- | --- | --- |
| `final_upload/01_cover.png` | bought outcome, two adapter shapes, real 20/20 gate | 1600×1200; no clipping |
| `final_upload/02_workflow.png` | canonical event → manifest → exact wire → endpoint expectation → report | 1600×1200; no clipping |
| `final_upload/03_proof.png` | real 429→success beside exhausted 503→dead letter, plus redaction/idempotency boundaries | 1600×1200; no clipping |
| `final_upload/04_adapterproof_walkthrough.mp4` | adapter switch, exact wire, 429 recovery, 503 stop, collision refusal, receipt proof | H.264/yuv420p; 1600×1200; 20.76 seconds |

Representative video frames at 1, 5, 9, 13, and 18 seconds were inspected.
The opening is stable, captions are complete and readable, the interaction
pointer is visible, and the final frame ends on the receipt outcome.

## Claim boundary

The canonical local copy is in
`portfolio_demos/UPWORK_PORTFOLIO_UPLOAD_COPY.md`. It states that the proof uses real
localhost HTTP requests over two generic adapter shapes. It does not claim a
named SaaS integration, OAuth, webhook signatures, production traffic,
throughput, uptime, distributed exactly-once effects, or client outcomes.

## Remaining publication gate

`PARTIAL`: no user-owned public remote is configured, and no validated commit
has been pushed. AdapterProof must remain `publication-ready-local`, not
`active`, in the evidence registry. Do not begin DeliveryGuard until the remote
and registry gates pass, because the controlling plan requires strict
repository order.
