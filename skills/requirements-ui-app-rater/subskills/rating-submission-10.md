# 10/10 submission gate (post-code)

**Parent skill:** `requirements-ui-app-rater`  
**Full checklist:** `../references/take-home-submission-10.md`

## When to load

Triggers: "10/10", "submission ready", "take-home ready", "grade before I submit", "pass all requirements".

Run **after implementation**. Run **all category subskills** (or full parent orchestration), then apply this gate.

## Orchestration order

1. `rating-requirements.md` — matrix; every must-have **Pass**
2. `rating-engineering.md` — gates green
3. `rating-deployment.md` — hosted = repo; health `curl`
4. `rating-qa.md` — happy path + edges + speed proof if required
5. `rating-ui-ux.md` — demo &lt;60s on **hosted** URL; screenshots in README
6. `rating-product-judgment.md` — trade-offs documented

## Condensed pass/fail (all required for 100/100)

1. **Gates:** `test`, `lint`, `build`, `test:e2e`; React Doctor ≥90, 0 errors (React/Next).
2. **Must-haves:** all **Pass** in matrix (nice-to-haves may be Partial if brief allows documented limits).
3. **README:** live URL, setup, approach/tools/assumptions/limitations, matrix summary, before/after screenshots.
4. **Deploy = repo:** redeploy if health/API/tracing changed; verify live health.
5. **Live demo &lt;60s** on hosted URL (assignment example or one-click demo).
6. **Speed proof** when brief implies it (~5s): doc or fresh timed run on primary fixture.
7. **Regulated lens** (if TTB/compliance): blind extract → rules → human disposition; limitations documented.
8. **Engineering:** ADRs/decisions, tests on rules+API, no unjustified &gt;~500 LOC files, tracing in `.env.example`.
9. **Peer extras** (mock COLA queue, ZIP batch, etc.) — **do not fail** unless in the brief.

## Verdict

- **100/100** only if no rubric caps in `../references/default-rubric.md` and Requirements = **35/35**.
- Otherwise report capped score + explicit blockers to clear.

## Output

Use parent `templates/rating-report.md` or standard report format; lead with:

```text
10/10 gate: PASS | FAIL
Blockers: ...
```
