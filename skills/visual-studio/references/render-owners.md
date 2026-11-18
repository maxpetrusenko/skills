# Who renders what, and where

| Job | Owner | Command or entry |
| --- | --- | --- |
| Earshot explainer cards | earshot `src/explain-*.ts`, Playwright | `pnpm tsx scripts/explain-demo.ts --shots` |
| Post video and still from a `post.json` | `post-media` | `post-media render <slug>`, `post-media stills <slug>` |
| Hand-built still or clip | HyperFrames | `hyperframes check --json`, `snapshot --at <t>`, `render --quality looks -o out.mp4` |
| Charts | Python (matplotlib, plotly) or HyperFrames | `data-visualization` |
| Diagrams | Mermaid CLI or Eraser, restyled | `mermaid-diagrams`, `eraser-diagrams` |
| Captured UI | Playwright from the repo | element screenshot, tight crop |
| Reference video rebuild | HyperFrames `reverse` | `reverse-any-video` |
| AI footage | Hermes lanes (Seedance, Veo, Higgsfield, Dreamina) | `ai-video-production` |

## Where to run (checked 2026-11-18)
- maxiclaw: about 1 GB free on a 228 GB disk, 100 percent used. Do not render there. Earshot's docs say heavy work runs on maxiclaw, which no longer holds.
- pro: renders work. The fleet guard denies heavy commands when memory or swap counts as 60 percent or more (swap above half of 1 GB counts as 100). Run one render at a time, then stop.
- uniclaw: 20 GB free, no ffmpeg. HyperFrames needs ffmpeg and Chrome (`npx hyperframes browser ensure`). Install first or stay on pro.
- A scoring run needs only the Claude session, no GPU.

## HyperFrames facts that bit during the experiment
- `snapshot --at 4.4` writes two PNGs, the requested one and an end frame. Use the first.
- Use the CLI from `~/Desktop/Projects/skills/skills/post-media/template/node_modules/.bin/hyperframes` (0.9.33). `npx hyperframes` fails offline.
- Bundled fonts come from `post-media/template/node_modules/@fontsource/*/files/*.woff2`. Copy them into `assets/fonts/` and `@font-face` them.
- `text-wrap: balance` fixes the orphan last word in headlines.
