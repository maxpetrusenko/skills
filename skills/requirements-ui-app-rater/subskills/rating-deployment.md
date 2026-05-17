# Deployment + delivery (10 pts)

**Rubric weight:** 10/100  
**Parent skill:** `requirements-ui-app-rater`

## When to load

- "Is deploy ready?", hosted URL check, prod vs repo
- Take-home requires live prototype URL

## Discovery order (if URL missing)

1. README/docs: vercel, netlify, pages, coolify, fly, custom domain
2. `.env.example`, deploy configs, package metadata
3. Manager hosting maps: `/Users/maxpetrusenko/Desktop/Projects/manager` (when appropriate)

**Rule:** Grade **hosted behavior** when deliverable requires deployment. Local-only success does not replace broken production.

## Checks

- [ ] Hosted URL loads; core flow works on **production**
- [ ] `curl` or fetch `/api/health` (or documented health) matches repo expectations
- [ ] No secrets in client bundle, logs, or README
- [ ] Production build healthy; demo data or one-click demo path (&lt;60s)
- [ ] Env vars documented; dev/prod parity explained
- [ ] Redeploy if API/tracing/docs changed since last deploy

## Scoring guide

| Band | Signal |
| --- | --- |
| 9–10 | URL works, demo fast, env clear, prod matches repo |
| 7–8 | URL works; minor env/doc gaps |
| 5–6 | URL flaky or demo hard to find |
| &lt;5 | Required URL missing or broken |

**Caps:** No deployed URL when required → max **80**. Core flow local-only, prod broken → max **70**. Missing repo/README when required → max **75**. Exposed secret → max **60** (lower if exploitable). Prod stale vs repo → max **94**.

## Evidence

- Live URL
- Health response snippet (redact secrets)
- Deploy platform + last-known good commit if inferable
- Demo steps timed on hosted URL
