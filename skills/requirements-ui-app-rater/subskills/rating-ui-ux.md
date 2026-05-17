# UI/UX + reviewer workflow (20 pts)

**Rubric weight:** 20/100  
**Parent skill:** `requirements-ui-app-rater`

## When to load

- "Score the UI", "UX audit", "visual QA"
- UI-only slice of a full rating
- After requirements matrix exists (terminology must match brief)

## Live UI protocol

1. Open hosted URL or local app.
2. **5-second test:** What does it do? Primary action obvious? Domain language correct?
3. Happy path with realistic sample data from the brief.
4. Viewports: at least one narrow/mobile + one desktop unless brief says desktop-only.
5. States: loading, empty, error, partial success, done.
6. Post-action panels: evidence/checks visible — not clipped by fixed height or hidden overflow.
7. Console/network on critical actions.

## UI judgment rules

Good UI for requirements-driven apps:

- Starts with the user's job, not a generic marketing hero.
- Primary action without hunting; domain language from the brief.
- System state visible; **evidence, not just scores**.
- Human judgment controls explicit where review/approval matters.
- No fake dashboards, generic AI sparkle, duplicate nav/chrome.
- Max default: **light mode** unless project/domain requires dark.

## Scoring guide

| Band | Signal |
| --- | --- |
| 18–20 | Obvious main path, low cognitive load, responsive, useful errors, no AI slop |
| 14–17 | Usable; P1 polish (spacing, hierarchy, mobile nits) |
| 10–13 | Works but needs explanation; hidden primary task |
| &lt;10 | Misleading chrome, wrong domain language, evidence hidden |

**Caps (parent applies):** UI hides primary task → max **80** even if backend works. Major a11y blockers in core flow (public-sector) → max **75**.

## Findings format

```text
UI findings
- P0: blocks submission or misleads reviewer
- P1: hurts score, fix if time
- P2: polish
```

## Evidence

- Screenshot paths + viewport size
- Steps to reproduce each P0/P1
- Before/after if comparing local vs hosted

## Web calibration (bounded)

- WCAG 2.2 for a11y issues
- Nielsen heuristics for interaction
- Lighthouse as **evidence**, not the rubric

Do not replace product judgment with Lighthouse alone.
