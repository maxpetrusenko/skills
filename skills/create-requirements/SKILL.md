---
name: create-requirements
description: Research-led requirements generator for local Mac and GitHub projects. Use when Max asks to create, refresh, or grade requirements.pdf; generate a 9+/10 requirements package; build spec, PRD, presearch, UI flows, diagrams, acceptance criteria, and source traceability from project evidence plus fresh comparable-product research.
---

# Create Requirements

## Contract

Create a 9+/10 requirements package, not a deterministic extraction.

The helper script is only an evidence collector. Final outputs must be synthesized by the agent using project docs, codebase evidence, GitHub state, fresh comparable-product research, and the related local skills listed below.

Do not call the generated PDF complete until the package includes:

- `brainlift.md`
- `requirements-research.md`
- `requirements-prd.md`
- `requirements-presearch.md`
- `requirements-spec.md`
- `requirements-ui-flows.md`
- `requirements-traceability.json`
- `requirements.md`
- `requirements.pdf`
- `requirements-review.md`

There is no quick mode for this skill. If any required artifact cannot be produced, stop and mark the run blocked instead of delivering a partial package.

## Required Skill Stack

Use these skills in order:

1. `deep-research` or web research: comparable apps, competitors, official docs, patterns.
2. `presearch-pipeline`: doc plan, multi-doc research, architecture/presearch orchestration.
3. `visual-presearch-workflow`: visual diagrams, UI flow mockups, system maps.
4. `rate`: final rating gate.
5. `requirements-ui-app-rater`: app/take-home requirement quality where relevant.
6. `llm-evaluation`: AI feature evals, traces, observability, model quality.
7. `pdf`: render and visually inspect the final PDF.

If a listed skill is missing, manually perform the same step and note the missing skill in `requirements-review.md`. Do not skip the step.

## Workflow

### 1. Intake

Resolve target project and output folder.

Read, at minimum:

- `AGENTS.md`, `CLAUDE.md`, `docs/requirements*`, `docs/PRD*`, `docs/PRESEARCH*`, `docs/TASKS*`, `README*`
- relevant source files for core flows
- GitHub metadata, issues, PRs, releases when available

Then run the evidence collector:

```bash
python3 "$SKILL_DIR/scripts/create_requirements.py" \
  --projects-root "$PROJECT" \
  --no-github \
  --output "$OUT/requirements-audit.pdf" \
  --output-mode audit
```

Use the JSON/Markdown output as evidence, not as the final requirements document.

The helper script must never write `requirements.pdf`, `requirements.md`, or `requirements.json`. Those final artifacts are agent-authored only.

### 2. Brainlift

Create `brainlift.md` before research synthesis.

It must explain:

- product definition in plain English
- target users and jobs-to-be-done
- what 9+/10 looks like
- non-negotiable constraints
- anti-patterns and bad versions to avoid
- Max-specific constraints, taste, safety boundaries, and approval rules
- initial unknowns to resolve through research

The brainlift is a required artifact and a hard blocker for final delivery.

### 3. Fresh Research

Research 3-7 comparable products or projects before writing requirements.

Prefer official/current sources:

- product docs and help centers
- developer docs
- public API docs
- public demos/screenshots
- credible GitHub repos and architecture docs

For each comparable, capture:

- product name and source URL
- relevant feature patterns
- UI flow patterns
- data model or API implications
- quality bar to match or exceed
- what to borrow
- what to avoid

If the project domain is unclear, infer it from the repo, then research that domain. Do not reuse CollabBoard examples for unrelated projects.

Research must cover these angles:

- product competitors and adjacent products
- UX/workflow patterns
- technical architecture
- data model and API design
- security, policy, privacy, platform, and legal constraints where relevant
- AI/eval/observability patterns where relevant
- proof, demo, submission, or deployment expectations

### 4. Generate Required Docs

Create the package as a coherent doc set:

- `brainlift.md`: product brief, target user, 9+/10 bar, constraints, anti-patterns.
- `requirements-research.md`: comparable-product research, citations, borrow/avoid decisions.
- `requirements-prd.md`: users, jobs, product goals, non-goals, feature scope, success metrics.
- `requirements-presearch.md`: constraints, options, decision matrix, architecture direction.
- `requirements-spec.md`: functional requirements, non-functional requirements, data model, APIs, auth/trust boundaries, acceptance criteria.
- `requirements-ui-flows.md`: Mermaid diagrams and/or visual wireflow sections for core user flows, failure states, admin/debug states, and AI/eval flows where relevant.
- `requirements.md`: submission-ready synthesized requirements document.
- `requirements.pdf`: rendered final version of `requirements.md`, visually modeled after the CollabBoard requirements style but filled with project-specific content.
- `requirements-traceability.json`: requirement IDs mapped to source evidence, research influence, acceptance tests, and gaps.
- `requirements-review.md`: final rating, quality gate results, known gaps, and verification commands.

### 5. Document Shape

`requirements.md` and `requirements.pdf` must use this structure unless the project clearly requires a better one:

Use `templates/requirements-package.md` as the authoritative section/header skeleton. If you intentionally change a header, update `scripts/verify_package.py` in the same run.

1. Title and subtitle.
2. Background and product thesis.
3. Comparable-product research summary.
4. Project overview and deadlines/milestones if relevant.
5. MVP requirements.
6. Core product requirements.
7. UI flows and user journeys.
8. Technical architecture.
9. Data model and API requirements.
10. AI/evaluation requirements when the project uses AI.
11. Security, privacy, auth, and trust boundaries.
12. Performance and reliability targets.
13. Acceptance criteria and test plan.
14. Submission/deployment requirements.
15. Traceability appendix.

Use project-specific language. Never leave generic placeholders like "Generated Product Requirements" in final output.

### 6. Quality Gate

Run the rubric in `references/quality-rubric.md`.

Minimum acceptable score: 9.0/10.

Hard blockers:

- no fresh comparable-product research
- no brainlift
- no citations/sources
- no PRD
- no spec
- no presearch/decision matrix
- no UI flow diagrams
- no acceptance criteria
- no traceability map
- no visual PDF render inspection
- no independent review/rating artifact
- generic extracted text pretending to be requirements
- copied CollabBoard text for a non-CollabBoard project

If score is below 9, patch the package and rerun the review. Do not hand off a sub-9 package unless Max explicitly asks to stop.

Independent review means a separate reviewer context from the authoring pass: `rate` invoked fresh, Claude/Codex on another machine or fresh context, or a subagent given only the generated artifacts and rubric. The same agent that authored the package cannot be the only reviewer.

## Resources

| File | Purpose |
| --- | --- |
| `scripts/create_requirements.py` | Evidence/audit collector. Not the final generator. |
| `scripts/verify_package.py` | Hard gate for required artifacts, traceability shape, banned placeholders, review score, and PDF presence. |
| `references/signals.md` | Requirement-source and completion-signal rules. |
| `references/research-led-workflow.md` | Detailed research/synthesis process. |
| `references/quality-rubric.md` | 9+/10 scoring gate. |
| `references/traceability-schema.json` | Required traceability JSON shape. |
| `templates/requirements-package.md` | Markdown skeleton for final requirements. |
| `templates/requirements-review.md` | Required independent review format. |

## Verification

Before final response:

- Render `requirements.pdf` to PNG with `pdftoppm`.
- Inspect page 1 and at least one inner page visually.
- Run `pdftotext requirements.pdf -` and confirm no placeholders or unrelated project names.
- Run `scripts/verify_package.py "$OUT"` and block delivery on nonzero exit. This verifies required artifacts, final-doc sections, traceability IDs, independent-review metadata, banned placeholders, and PDF text.
- Record all commands and score in `requirements-review.md`.
