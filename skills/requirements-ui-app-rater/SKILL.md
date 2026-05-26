---
name: requirements-ui-app-rater
description: "Use for rating, judging, or auditing an app/prototype/take-home against requirements, UI/UX, QA/reliability, code cleanliness, deployment, and product judgment"
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [app-review, requirements, ui-ux, take-home, gauntlet, rubric, qa, scoring, government, regulatory, compliance, subskills]
    related_skills: [visual-presearch-workflow, presearch-pipeline, vercel-react-best-practices, verification-before-completion, qa-test-planner, code-review-analysis, ui-ux-pro-max, dogfood]
---

# Requirements + UI App Rater (controller)

## Purpose

Judge an app like a serious reviewer: **requirements first**, working product second, edge cases third, UI fourth, code/deploy fifth. Do not cheerlead. Do not rate from README vibes.

**Category subskills** hold the detailed rubric per dimension. This file is the **orchestrator**: inputs, routing, workflow order, shared caps, report shell.

## Subskill routing

Load only the subskills needed. All live under `subskills/`.

| User intent | Subskill | Points |
| --- | --- | ---: |
| Requirements / matrix / must-have vs nice-to-have | `subskills/rating-requirements.md` | 35 |
| UI / UX / visual QA / workflow | `subskills/rating-ui-ux.md` | 20 |
| QA / edge cases / correctness / E2E / AI-OCR checks | `subskills/rating-qa.md` | 15 |
| Code cleanliness / tests / React Doctor / tracing | `subskills/rating-engineering.md` | 15 |
| Hosted URL / prod vs repo / env / secrets | `subskills/rating-deployment.md` | 10 |
| Trade-offs / Gauntlet calibration / product judgment | `subskills/rating-product-judgment.md` | 5 |
| **10/10 submission ready** (post-code) | `subskills/rating-submission-10.md` | gate |

**Full rating:** run all six category subskills in workflow order below, then aggregate. **Partial rating:** run requested subskills only; say which dimensions were skipped.

**Government/regulatory:** also read `references/government-regulated-apps.md` (layers on requirements + QA subskills).

## When to use

- "rate this app" / "score the UI" / "code cleanliness"
- "does this satisfy the take-home?"
- "10/10" / "submission ready"
- Compare local vs hosted; Gauntlet-ready check

Not for implementation planning alone — need app/repo/doc/URL to inspect.

## Required inputs

Gather without asking when possible:

1. **Requirement source** — DOCX/PDF/MD/brief; extract must/nice/non-goals/eval criteria.
2. **App surface** — repo path, hosted URL, or both (search README/deploy/manager maps if URL missing).
3. **Reviewer lens** — assignment evaluator, not the builder.
4. **Reference set** — calibration only unless brief requires parity.
5. **Edge-case lens** — domain + fixtures; classify blocker vs prototype vs limitation.

## Workflow order (full rating)

1. **Requirements** → `rating-requirements.md` (matrix before testing).
2. **Repo** → `rating-engineering.md` (gates + hygiene).
3. **Deploy** → `rating-deployment.md` (hosted truth).
4. **Live app** → `rating-ui-ux.md` + `rating-qa.md` (browser steps, edges, console).
5. **Product** → `rating-product-judgment.md`.
6. **Caps** → apply table below; write report.
7. If **10/10** asked → `rating-submission-10.md` after step 6.

Bounded web research for domain/edge/UI calibration — see `rating-qa.md` and `rating-ui-ux.md`. Do not drown the report.

## Default 100-point rubric

| Dimension | Pts | Subskill |
| --- | ---: | --- |
| Requirements coverage | 35 | `rating-requirements.md` |
| UI/UX + reviewer workflow | 20 | `rating-ui-ux.md` |
| Functional correctness + reliability | 15 | `rating-qa.md` |
| Engineering quality | 15 | `rating-engineering.md` |
| Deployment/delivery | 10 | `rating-deployment.md` |
| Product judgment | 5 | `rating-product-judgment.md` |

Assignment rubric overrides when present. Detail: `references/default-rubric.md`.

### Caps and blockers (apply after raw scores)

- App does not load: max **45**
- No working core flow: max **60**
- Core flow local-only, required deploy broken: max **70**
- No deployed URL when required: max **80**
- Missing repo/README when required: max **75**
- Major secret leak: max **60**
- AI as authoritative compliance/legal/medical without evidence: max **70**
- No LLM trace story (model calls): max **88**
- Prod/health stale vs repo: max **94**
- React Doctor errors (React/Next): max **85**; score &lt;90: max **92**
- No E2E smoke (UI core flow): max **93**; E2E not in CI: max **96**
- Stale requirements trace/README: max **94**
- Gov app: draft as official decision / no citations / no export: see `rating-requirements.md` + government reference
- UI hides primary task: max **80**
- No requirement source: max **70** (heuristic-only unless user OK)

### Verdict bands

- **90–100:** Strong / submit
- **80–89:** Good; fix gaps if time
- **70–79:** Risky
- **60–69:** Weak prototype
- **45–59:** Demo-fragile
- **&lt;45:** Not ready

## Report format

Use `templates/rating-report.md` or:

```text
Rating: <score>/100 — <verdict>
Subskills run: requirements | ui | qa | engineering | deployment | product | 10-gate

Scorecard
- Requirements: x/35
- UI/UX: x/20
- Correctness/reliability: x/15
- Engineering: x/15
- Deployment: x/10
- Product judgment: x/5

Requirement matrix | Edge-case matrix | UI findings | Test evidence
Missing info | Next fixes (ordered)
```

Keep the rating blunt. Evidence, not vibes.

## References

| File | Use |
| --- | --- |
| `references/take-home-submission-10.md` | Full 10/10 checklist |
| `references/default-rubric.md` | Rubric detail + caps |
| `references/government-regulated-apps.md` | Agency/compliance lens |
| `templates/rating-report.md` | Report skeleton |

## Companion skills

- `verification-before-completion` — before final Pass claims
- `qa-test-planner` — cases from requirement rows
- `vercel-react-best-practices` — React Doctor follow-up
- `code-review-analysis` — security/structure depth
- `presearch-pipeline` — doc plan / iteration loop

## Common pitfalls

1. Rating from docs only — test the app.
2. Treating nice-to-haves as must-haves.
3. Ignoring deployed URL when required.
4. Every edge case as blocker — classify stage.
5. Lighthouse over product judgment.
6. Leaking private Gauntlet/hosting inventory in external reports.

## Verification checklist (controller)

- [ ] Subskills loaded match user request (full vs partial).
- [ ] Requirement matrix before live score (if requirements dimension included).
- [ ] Caps applied after raw dimension scores.
- [ ] 10/10: `rating-submission-10.md` + all must-haves Pass.
- [ ] Report lists evidence paths and skipped dimensions.
