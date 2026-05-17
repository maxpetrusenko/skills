# Engineering quality + code cleanliness (15 pts)

**Rubric weight:** 15/100  
**Parent skill:** `requirements-ui-app-rater`

## When to load

- "Code cleanliness", "engineering score", "React Doctor", "is the repo maintainable?"
- Pre-submit gate: lint/test/build
- Not a substitute for requirements or live UI testing

## Gates (run smallest meaningful set)

```bash
npm run test
npm run test:e2e
npm run lint
npm run build
```

Adjust for stack. Record exact command + output if skipped or failed.

## React/Next (when applicable)

```bash
npx -y react-doctor --full --offline --json --no-respect-inline-disables
```

- **Errors** → blockers until fixed or out-of-scope justified.
- Score **&lt;90** → usually cap Engineering at **12/15**; **&lt;80** → **9/15**.
- Score **100** does not mean app is 100 — other dimensions still apply.

**Caps:** React Doctor errors → max **85**. Score &lt;90 → max **92**. Cannot run React Doctor + no equivalent → max **94**.

## Code cleanliness checklist

- Architecture matches domain (e.g. blind extract → rules → human disposition).
- Tests on **rules + API** paths that matter for submission.
- Files **&gt;~500 LOC** without split/justify → cleanliness ding (e.g. monolithic `rules.ts`).
- Sensible dependencies; validation on API boundaries.
- Git hygiene: unrelated diffs, huge generated assets, untracked submission junk → note explicitly.
- README: setup, env, assumptions, limitations, test commands.

## AI observability (when model calls exist)

Default: **Braintrust, LangSmith, or equivalent**.

- `.env.example` documents tracing keys; README says how to verify (`/api/health` or docs).
- Traces: metadata (provider, model, status), not raw secrets/images.
- Prefixed env vars OK if docs say which wins; README lists **one** canonical set.
- **No trace story** → parent cap **88** (lower if evals central to brief).
- **Prod health stale vs repo** (removed deps, wrong flags) → cap **94** until redeploy.

## Documentation parity

- Requirements docs separate must/nice/non-goals/eval criteria.
- Trace/README commands match what CI and code actually run.

## Scoring guide

| Band | Signal |
| --- | --- |
| 14–15 | Green gates, React Doctor ≥90, tests meaningful, maintainable modules |
| 11–13 | Solid with warnings or one fat file justified |
| 8–10 | Tests thin or gates flaky; hygiene issues |
| &lt;8 | No tests, broken build, secrets in repo |

## Evidence

- Command outputs (pass/fail snippets)
- React Doctor JSON summary: score, errorCount, warningCount
- File paths for architecture/tests/ADRs
- LOC note for files over ceiling

Companion: `vercel-react-best-practices`, `code-review-analysis`.
