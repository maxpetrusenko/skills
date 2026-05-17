# Default App Rating Rubric

Use the assignment's own rubric when present. If none exists, use this 100-point fallback.

| Dimension | Points | Definition |
| --- | ---: | --- |
| Requirements coverage | 35 | Must-haves implemented, nice-to-haves scoped, examples from brief work, no invented scope. |
| UI/UX + reviewer workflow | 20 | Primary path obvious, low cognitive load, domain language, responsive, accessible, useful error/loading/empty states. |
| Functional correctness + reliability | 15 | Happy path and edge paths work, no crashes, no console noise, speed acceptable, fallback behavior sane. |
| Engineering quality | 15 | Clean architecture, tests, validation, security basics, README/setup, maintainable code, sensible dependencies. |
| Deployment/delivery | 10 | Hosted URL works when required, env documented, production build healthy, demo data present, no secret/log leaks. |
| Creative product judgment | 5 | Memorable product decision, domain nuance, thoughtful simplification, useful trade-offs. |

## Caps

- App does not load: max 45.
- No working core flow: max 60.
- Deployed URL required but broken while local works: max 70.
- No deployed URL when explicitly required: max 80.
- Missing repo/README when explicitly required: max 75.
- Major secret/security leak: max 60.
- Dangerous authoritative AI judgment in regulated domain: max 70.
- AI/OCR comparison app presents hallucinated, default, or garbage extracted fields as passing evidence: max 70, lower if the domain is regulated and the UI looks authoritative.
- Primary task hidden/unclear: max 80.
- No requirements source: max 70 unless heuristic-only review requested.

## Verdict Bands

- 90-100: Strong / ship / submit.
- 80-89: Good, fix gaps if time allows.
- 70-79: Plausible but risky.
- 60-69: Weak prototype.
- 45-59: Demo-fragile.
- <45: Not ready.
