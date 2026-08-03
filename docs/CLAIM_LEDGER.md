# AdapterProof claim ledger

## Supported now

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Built a credential-free conformance harness for client-owned HTTP adapters | `adapterproof/`, two frozen manifests, CLI report, package and Docker smoke | local generic HTTP contracts, not a hosted validation service |
| Verified referenced authentication, correlation, idempotency, and exact mapped JSON at the wire boundary | pytest-httpserver ordered request expectations and 20 passing case results | environment-secret references and static headers only; no OAuth flow |
| Refused malformed manifests, missing required source fields, missing secrets, and changed-payload idempotency collisions | focused refusal tests and `idempotency_collision`/`missing_secret` report cases | bounded declarative dot-path mapping, not arbitrary provider transforms |
| Proved retry stop rules, dead-letter state, explicit replay, deduplication, and receipt sequences through DeliveryGuard | 429/503/422/malformed/duplicate/replay cases and persisted DeliveryGuard receipts | local SQLite and generic HTTP outcomes; no distributed exactly-once guarantee |
| Used an existing GitHub foundation instead of inventing a mock transport | retained pytest-httpserver history at `44b3c91`, direct `HTTPServer` use, 130 retained tests passed, 3 skipped, 1 expected failure | AdapterProof owns the manifest, mapping, scenario, and report layer |
| Shipped reproducible package, CI, and container paths | vendored checksummed DeliveryGuard wheel, wheel/sdist plus Twine, workflow, Docker PASS | no remote, deployment, uptime, or production traffic claim |

## Proposal-safe wording

> I built a reusable adapter conformance harness that maps a canonical event,
> sends it through a tested delivery lifecycle to exact local HTTP
> expectations, and reports authentication-reference, idempotency, retry,
> dead-letter, replay, and receipt behavior before live credentials are used.

Use AdapterProof when a job asks for API/webhook integration quality,
pre-go-live acceptance evidence, retries, idempotency, or failure handling. Say
"generic HTTP adapter" unless provider-specific fixtures and a repeated/live
job justify a named adapter.

## Unsupported wording

Do not claim:

- Salesforce, HubSpot, Slack, Twilio, calendar, CRM, or other named-provider
  compatibility;
- OAuth, token refresh, webhook signature verification, or live credential
  handling;
- production availability, deployment, throughput, scale, or measured client
  outcomes;
- distributed exactly-once delivery or prevention of duplicate side effects
  without a cooperating destination;
- endpoint allowlisting, private-network blocking, or a complete SSRF defense;
- that passing generic local fixtures proves a provider's current API contract.
