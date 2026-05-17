# Functional correctness + reliability (15 pts)

**Rubric weight:** 15/100  
**Parent skill:** `requirements-ui-app-rater`

## When to load

- "QA rate", "edge cases", "does it work?", reliability
- Pair with `rating-ui-ux` for browser steps; this subskill owns **correctness + edge matrix**

## Edge-case discovery (before final score)

Search (bounded, current sources):

- `<domain> app common edge cases`
- `<domain> OCR/image edge cases` (if visual inputs)
- Official docs + competitor patterns

Matrix:

```text
Edge case | Source/context | Expected behavior | Current handling | Rating impact | Fix/docs
```

Classify each: **blocker** | **prototype expected** | **nice-to-have** | **documented limitation**.

Test highest-risk **3+** when feasible. Do not punish prototype for every edge case — punish obvious/prompt-implied gaps that mislead evaluators.

## Live test paths (minimum)

1. Happy path with requirement examples / fixtures.
2. Missing/invalid input.
3. Slow/loading.
4. Bad file/network/API.
5. Empty state.
6. Domain-specific: poor images, multi-object, partial/covered content, ambiguous target.

## AI/OCR apps (if applicable)

- Each pass/fail row grounded in **visible or extracted evidence** for that field.
- Garbage OCR (`C`, one-char), empty strings → must not pass brand/class/ABV/address checks.
- Default boilerplate (750 mL, standard warning) → must not pass if not visible.
- Multi-product images → fail or block isolation, not random label match.
- Extractor uncertainty vs deterministic rules → disclose; no clean approval on conflict.

## Speed + degraded behavior

- If brief implies ~5s or similar: timed run or `SPEED_EVIDENCE`-style doc.
- Fallback/degraded paths must fail safely with clear UX.

## E2E expectation

- At least one browser E2E smoke on primary flow (Playwright default for Next unless repo standardizes Cypress).
- Map E2E to requirement IDs, not only "page loads".
- Local E2E without CI → parent cap **96** unless reason documented.

## Scoring guide

| Band | Signal |
| --- | --- |
| 14–15 | Happy path + edge matrix solid; no console noise; speed OK |
| 11–13 | Core reliable; 1–2 edge gaps documented |
| 8–10 | Fragile on common edges; console errors |
| &lt;8 | Core example fails or unsafe AI presentation |

**Caps:** No working core flow → max **60**. App won't load → max **45**. AI hallucination as authoritative compliance/legal/medical → max **70** (lower if dangerous).

## Evidence

```text
Test evidence
- URL/local command:
- Browser steps:
- Console/network:
- E2E command + result:
- Edge matrix rows tested:
```

Companion: `qa-test-planner` for regression cases from requirement rows; `verification-before-completion` before claiming Pass.
