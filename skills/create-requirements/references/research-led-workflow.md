# Research-Led Requirements Workflow

## Principle

Requirements generation is a synthesis task. Evidence extraction is only the input.

The agent must combine:

- repo docs and source evidence
- GitHub issues, PRs, releases, and README claims when available
- brainlift: product definition, users, 9+/10 bar, constraints, anti-patterns
- fresh comparable-product research
- architecture/presearch reasoning
- UI flow modeling
- acceptance criteria and test planning
- final quality review

## Research Tracks

Run all tracks before writing the final document:

1. Comparable products: 3-7 products/apps/projects in the same category.
2. Product UX: onboarding, core workflows, empty/error/success states, collaboration/admin flows.
3. Technical architecture: relevant APIs, state model, data model, auth, sync, deployment, observability.
4. AI/evals: model calls, tool calling, traces, evaluation datasets, failure modes, guardrails.
5. Submission/readiness: what a strong take-home, demo, or project handoff usually proves.

## Mandatory Artifact Order

1. `brainlift.md`
2. `requirements-research.md`
3. `requirements-prd.md`
4. `requirements-presearch.md`
5. `requirements-spec.md`
6. `requirements-ui-flows.md`
7. `requirements-traceability.json`
8. `requirements.md`
9. `requirements.pdf`
10. `requirements-review.md`

Do not skip or merge artifacts. The final PDF may summarize the other files, but the underlying files must exist.

Before writing `requirements-review.md`, run:

```bash
python3 "$SKILL_DIR/scripts/verify_package.py" "$OUT"
```

If the verifier fails, patch the package instead of writing a pass review.

## Comparable Research Output

For every comparable:

```text
Name:
Source:
Why relevant:
Patterns to borrow:
Patterns to avoid:
Requirements implied:
UI flow implications:
Technical implications:
```

Use primary/official sources first. If a source may have changed, verify it live in the current run.

## Synthesis Rules

- Convert research into requirements, not a literature review.
- Each major requirement should have an acceptance criterion.
- Each architecture decision should name rejected alternatives.
- Each UI flow should include happy path, empty state, failure/recovery, and permission/auth state when relevant.
- Each AI requirement should include eval, observability, latency, cost, and fallback behavior.
- Keep CollabBoard as a style/example only. Do not reuse its content for another project.

## Output Quality

The final package should let a competent engineer build the project without asking what the product is, what flows matter, what quality bar applies, or how success will be judged.
