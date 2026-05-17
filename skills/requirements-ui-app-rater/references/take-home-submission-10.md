# Take-Home 10/10 Submission Gate

Read when the user asks for **10/10**, **submission-ready**, or **grade this before send**. Run **after** implementation; this is a pass/fail gate plus rubric floor, not a build plan.

**Subskills:** orchestration in `../subskills/rating-submission-10.md`; per-dimension detail in `rating-requirements`, `rating-engineering`, `rating-deployment`, `rating-qa`, `rating-ui-ux`, `rating-product-judgment`.

## Score rule

**100/100 only if every must-have is Pass with evidence and no cap applies.** Nice-to-haves may be Partial if documented. Peer features (mock COLA queue, ZIP manifest, two-layer UI) are **not** must-haves unless the brief says so.

## Condensed gate (run in order)

### A. Automated gates (block if any fail)

```bash
npm run test && npm run lint && npm run build
npm run test:e2e          # required for UI take-homes with a browser flow
npx -y react-doctor --full --offline --json --no-respect-inline-disables   # React/Next only
curl -fsS <DEPLOYED_URL>/api/health    # when brief requires live URL
```

- React Doctor: **0 errors**, score **≥ 90** (or document false positives).
- E2E must cover **primary happy path** (not only “page loads”).
- **Prod must match repo** — redeploy if `/api/health`, env, or tracing changed.

### B. Must-have matrix (35/35)

Build from `docs/requirements.md` or the assignment DOCX. Every **must-have** row = **Pass** + file/URL evidence.

| Brief item (typical TTB label take-home) | Pass when |
| --- | --- |
| Deployed working prototype | Live URL loads; core action works without secrets |
| Repo + README | Clone, `npm install`, `cp .env.example`, `npm run dev`; deliverables table |
| README brief docs | **Approach**, **tools**, **assumptions**, **limitations/trade-offs** — not buried in ADRs only |
| Core verify flow | All listed fields checked (brand, class, ABV, net, bottler, import origin, gov warning) |
| Gov warning | Exact text + `GOVERNMENT WARNING:` caps; **document** font/placement limits |
| Human judgment | Reviewer can approve/reject; no silent auto-denial |
| ~5 seconds | `docs/SPEED_EVIDENCE.md` or fresh timed run on demo fixture (typical under 5s wall on happy path) |
| Clean UI + errors | Obvious primary action; demo path under 60s; basic error states tested |
| Standalone / no COLAs API | No real COLAs integration; mock queue optional |
| Cloud/security | Limitations in README; no persistence of uploads by default |
| Sample labels | Fixtures path documented; **Demo** or equivalent one-click path |

**Partial allowed only** where the brief explicitly allows documenting limits (e.g. font size, wine/beer depth “if feasible”).

### C. README & docs (attention to requirements)

- [ ] **Requirements matrix** in README (summary) + `docs/REQUIREMENTS_TRACE.md` (full trace).
- [ ] **Before/after** (or flow) screenshots as JPEG/PNG in `docs/assets/`.
- [ ] Live URL in README matches deployed app.
- [ ] `.env.example` matches code (no dead LangSmith if removed; tracing doc matches Braintrust/Langfuse/etc.).
- [ ] OpenAPI/API.md agrees with routes and response shapes.
- [ ] Peer comparison optional — do **not** treat missing peer extras as failures.

### D. Government / regulatory lens (TTB-style)

- [ ] **Blind extraction** — model does not receive application facts at extract time.
- [ ] **Deterministic rules** decide pass/fail/review; UI shows **application vs label evidence** per row.
- [ ] **Fail closed** on garbage OCR, multi-bottle shelf photos, invented boilerplate.
- [ ] **CFR/source refs** on checks when feasible (or assignment cites).
- [ ] Limitations explicit: not legal approval, no COLAs, no font metrics, no audit persistence.

### E. Engineering cleanliness (15/15)

- [ ] No source file over ~500 LOC without split (big `rules.ts` caps Engineering).
- [ ] ADRs or `docs/decisions/` for approach (extract → rules → human).
- [ ] Tests on rules, API routes, imports — not only UI smoke.
- [ ] **AI tracing**: Braintrust, LangSmith, or equivalent documented in `.env.example` + README if model calls exist.

### F. Live test (do not skip)

1. Open deployed URL (not local-only if brief requires deploy).
2. Run assignment **example fields** or **Demo pass** fixture.
3. Confirm comparison table shows **expected vs observed**.
4. Check console for errors; narrow viewport spot-check.
5. Regenerate README screenshots if UI changed: `npm run screenshots:readme` (if script exists).

## Rubric floor for 10/10

| Dimension | Target |
| --- | ---: |
| Requirements coverage | **35/35** |
| UI/UX + workflow | **18–20/20** |
| Correctness + reliability | **14–15/15** |
| Engineering quality | **14–15/15** |
| Deployment/delivery | **10/10** |
| Product judgment | **4–5/5** |

## Caps that prevent 10/10 (fix before submit)

| Issue | Max score |
| --- | ---: |
| Deployed URL broken | 70–80 |
| Core flow broken | 60 |
| No E2E on UI take-home | 93 |
| React Doctor errors | 85 |
| Prod ≠ repo (stale health/API) | 94 |
| README/trace stale vs shipped code | 94 |
| Regulated app: draft = official approval | 70 |
| AI compare: garbage OCR passes as evidence | 70 |

## alcohol-label-verifier canonical paths

Use when rating `alcohol-label-verifier` / LabelCheck:

| Artifact | Path |
| --- | --- |
| Requirement source | `docs/requirements.md` |
| Full trace | `docs/REQUIREMENTS_TRACE.md` |
| Speed | `docs/SPEED_EVIDENCE.md` |
| Fixtures (Faheem dataset) | `public/evals/fixtures/spirits-generated-canonical/` |
| Live | `https://cola.maxpetrusenko.com` |
| Screenshots | `docs/assets/reviewer-before-input.jpg`, `reviewer-after-verification.jpg` |

**Not required for 10:** mock COLA queue, ZIP+manifest batch, Layer 1/2 split UI, persisted audit trail.
