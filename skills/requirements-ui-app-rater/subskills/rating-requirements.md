# Requirements coverage (35 pts)

**Rubric weight:** 35/100  
**Parent skill:** `requirements-ui-app-rater`

## When to load

- Building or scoring a requirement matrix
- "Does this satisfy the take-home / brief?"
- Must-have vs nice-to-have disputes
- Government/regulatory lens (also read `../references/government-regulated-apps.md`)

## Matrix (required before scoring)

```text
ID | Requirement quote | Type: must/nice/eval/non-goal | Evidence needed | Weight | Status
```

Rules:

- Deliverables section → must-haves.
- "Would be huge", "if feasible", "out of scope" → nice-to-haves unless deliverables say otherwise.
- Evaluation criteria → scoring dimensions even when not features.
- Never promote nice-to-have to blocker without explicit reason.

## Extraction

1. Read requirement source first (DOCX: `python-docx`, PDF/OCR, Markdown direct).
2. Separate: must-haves, nice-to-haves, non-goals, evaluation criteria.
3. Cross-check README, `docs/requirements*`, trace matrices vs shipped code/commands.

## Consistency checks

- README vs docs vs UI copy vs API/OpenAPI — same supported scope.
- Code/tests support feature docs call unsupported → docs/API blocker.
- Runtime schema ≠ OpenAPI examples → integration readiness down.
- Domain wording by mode/profile (e.g. wine path must not show spirits-only copy).

## Scoring guide

| Band | Signal |
| --- | --- |
| 32–35 | Every must-have Pass with evidence; nice-to-haves scoped; no invented scope |
| 28–31 | Core must-haves Pass; 1–2 Partial with documented limits |
| 22–27 | Core works but matrix gaps or stale trace |
| &lt;22 | Missing must-haves or untested claims |

**10/10:** All must-haves **Pass**; nice-to-haves may be Partial only if brief allows documented limits. Full gate: `../references/take-home-submission-10.md`.

## Evidence

- Matrix rows with file paths, URLs, test names
- Requirement doc quotes (short)
- Screenshot or step proof for demo path

## Government/regulatory add-ons

From `../references/government-regulated-apps.md`:

- Blocking rules cite primary sources
- Draft checks not presented as official approval
- Human review / audit trail where domain requires it
