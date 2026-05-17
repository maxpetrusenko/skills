# Government / Regulated App Lens

Use this reference when rating apps for government, public-sector, regulated submissions, compliance review, permits, benefits, tax, licensing, legal-adjacent workflows, or agency-style evidence review.

## Core Judgment

Rate the app as a decision-support system unless the brief explicitly grants official decision authority.

The key question is not "does it look modern?" It is:

> Can a real reviewer or applicant trust what happened, trace it to sources, correct it, and hand it off?

## Extra Requirement Matrix Fields

Add these columns to the normal requirement matrix:

```text
Authority source | Evidence shown? | Human override? | Audit/export? | Harm if wrong
```

Use primary sources for rules:

- official agency pages
- CFR/statute/regulation text
- official forms, checklists, manuals, policy docs
- assignment source docs

Avoid using blog posts or competitor copy as rule authority unless they are only product calibration.

## Rating Checks

Authority and source truth:

- Blocking checks cite a primary source or the assignment requirement.
- Exact statutory text is compared exactly when the law requires exact wording.
- The app separates source facts, extracted evidence, rule results, and human disposition.
- The app does not convert uncertain extraction into clean pass/fail.
- The app calls itself a reviewer assistant unless official authority is explicitly in scope.

Evidence and audit:

- Every fail/review finding shows expected value, observed value, source/reference, rationale, and next step.
- Export includes input facts, file names, extraction output, rule checks, timestamps/version if available, and final reviewer disposition.
- Batch flows preserve row-to-file pairing and partial failure state.
- Human override/review decisions are explicit and explainable.

Safety and harm:

- The app fails closed for ambiguous identity, target, eligibility, or compliance evidence.
- It distinguishes "missing from uploaded evidence" from "not present anywhere."
- It avoids defaulting common boilerplate or standard values into evidence.
- It handles stale or changed regulations as a known maintenance risk.

Accessibility and public-sector UX:

- Core flow is keyboard reachable and screen-reader plausible.
- Error messages are plain language and actionable.
- Required fields, file limits, and supported formats are clear before submission.
- Mobile/narrow viewport works when the target user could plausibly use it.
- Visual style is restrained, task-first, and avoids decorative complexity that obscures the workflow.

Privacy, security, and deployment:

- Sensitive documents/images are not logged or retained accidentally.
- `.env.example` and docs name required keys without exposing secrets.
- Local/dev/prod run paths are equivalent; no prod-only hidden steps.
- Side-effecting actions use sandbox/test tenants or require explicit approval.
- Data retention and export boundaries are documented when real user data is plausible.

## Government App Caps

Apply these after the normal score:

- No primary-source basis for required legal/compliance checks: max 80.
- Presents advisory output as official approval/denial without authority: max 70.
- No evidence trail for a blocking result: max 82.
- Missing human review/override in a high-stakes decision workflow: max 75.
- Major accessibility blocker in the primary flow: max 75.
- Stores or logs sensitive applicant/compliance data unsafely: max 60.
- Cannot reproduce the same behavior locally/dev as deployed: max 80.

## Good Signs

- Rule engine is deterministic and test-covered.
- AI/OCR/model layer extracts evidence only.
- User can inspect evidence before disposition.
- Batch review handles many records without losing pairing.
- Docs name limitations honestly.
- Tests include edge cases from official requirements and realistic bad inputs.

## Common Failure Modes

- "AI approved" language.
- Vague citations like "TTB rules" without section/source.
- Exact legal text normalized for case/punctuation when exactness matters.
- No distinction between missing fact, unreadable evidence, and true mismatch.
- Pretty dashboard hiding the actual review queue.
- No export or handoff artifact.
- Sample-only rules pretending to be full regulatory coverage.
