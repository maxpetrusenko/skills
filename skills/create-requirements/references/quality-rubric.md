# Requirements Package Quality Rubric

Score 0-10. Minimum acceptable score: 9.0.

## Dimensions

| Dimension | Points | 9+/10 standard |
| --- | ---: | --- |
| Project grounding | 1.0 | Reads real repo/docs/source/GitHub evidence and names source files. |
| Brainlift | 0.8 | Defines product, users, 9+/10 bar, non-negotiables, anti-patterns, Max-specific constraints. |
| Comparable research | 1.3 | Uses 3-7 current comparable apps/projects with primary-source citations and borrow/avoid decisions. |
| PRD quality | 0.9 | Clear users, jobs, goals, non-goals, metrics, release scope. |
| Presearch quality | 0.9 | Decision matrix, constraints, alternatives, recommended architecture, tradeoffs. |
| Spec quality | 1.3 | Functional/NFR requirements, data/API/auth/trust boundaries, edge cases, acceptance criteria. |
| UI flow quality | 0.9 | Diagrams or wireflows for core journeys, empty states, failure states, admin/debug flows where relevant. |
| AI/eval quality | 0.7 | For AI projects: traces/evals/cost/latency/fallbacks. If non-AI, reallocate to spec depth. |
| Traceability | 0.7 | Requirement IDs map to repo evidence, research influence, acceptance tests, and gaps. |
| PDF/design quality | 0.7 | Visually polished, CollabBoard-style family, project-specific language, no placeholders. |
| Independent review | 0.5 | Uses a separate review/rating pass and records fixes. |
| Verification | 0.3 | Rendered PDF inspected, text checked, JSON validated, commands recorded. |

## Hard Caps

Any missing required artifact is a blocked run, not a capped score.

- No fresh research: max 6.0
- No brainlift: max 6.0
- No citations: max 6.5
- No PRD or no spec: max 7.0
- No presearch/decision matrix: max 7.0
- No UI flows/diagrams: max 7.5
- No traceability JSON: max 8.0
- No independent review artifact: max 8.0
- Deterministic extraction as final doc: max 6.5
- Copied CollabBoard content for another project: max 5.0
- No visual PDF inspection: max 8.0
- Broken PDF rendering, overlapping text, or unreadable tables: max 7.0

## Independent Review Definition

Independent review means a separate reviewer context from the authoring pass. Acceptable forms:

- `rate` invoked after generation without the authoring transcript
- Claude/Codex on another machine or fresh context
- a subagent with only the generated artifacts and rubric

The same agent that authored the package cannot be the only reviewer.

## Required Artifact Checklist

All must exist before a run can pass:

- `brainlift.md`
- `requirements-research.md`
- `requirements-prd.md`
- `requirements-presearch.md`
- `requirements-spec.md`
- `requirements-ui-flows.md`
- `requirements.md`
- `requirements.pdf`
- `requirements-traceability.json`
- `requirements-review.md`

Run `scripts/verify_package.py <package-dir>` before assigning a final score. A nonzero verifier exit blocks delivery.

## Review Output

`requirements-review.md` must include:

```text
Rating:
Verdict:
Independent reviewer:
Reviewer context:
Authoring context:
Artifacts reviewed:
Evidence read:
Comparable sources:
Hard caps checked:
Top fixes applied:
Remaining gaps:
Verification commands:
```

If score is below 9.0, patch and rerun review.
