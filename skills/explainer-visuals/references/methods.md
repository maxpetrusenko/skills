# Methods

Pick by what the picture has to prove. The model decides emphasis (where the eye goes). Code supplies every value.

## 1. Capture and annotate (UI fixes)

Use when the change is something on a screen. Take a Playwright `locator.screenshot` of the real page, rendered in each state, cropped to the one element, with one outline, spotlight or zoom. Do not redraw the app: a redrawn player is a diagram of a player.

```
pnpm tsx scripts/explain-capture.ts <page.html|url> <selector> <out.png> [--outline <selector>] [--pad 12] [--width 390]
```

State change: capture once per state and stack the crops in the same slot (same width, same frame), the changed state outlined. Matched crops beat a legend.

Status in earshot: the script exists and is checked against an earshot page element. The in-page explainer types (`state_key`) draw the player slot from data, because the explain stage runs from reply text and has no running app to capture. Use capture when the app is available to the agent.

## 2. Render from data (perf, logs, ranges)

Use when the reply contains numbers or exact strings. The model returns the strings and numbers it found in the reply; templates draw them.

- `log_compare`: two lines in one close-up, aligned columns, a dotted gap where one line has no digit, a highlight on the digits that differ. The highlight is computed from the two strings.
- `range_chart`: one shared axis from the reply's own unit. A dot is a value, a bracket is a range. `player: true` draws the track as the player bar (dashed waiting, waveform once available) when the numbers are the wait until Original can play.
- No axis, no lanes, no durations unless the reply gives timings. Illustrative values go in the eyebrow.

## 3. Storyboard stills, then HyperFrames (time-varying)

Use when the meaning is a change over time and the reply gives no numbers to put on an axis (a button appearing, a state switching). Write three to five stills (same slot, one state each), check each with the two-second test, then render them as a short HyperFrames video (skills `hyperframes`, `hyperframes-cli`, `post-media`). Light theme, real font, real proof assets.

## 4. Raster image generation (concept or hero only)

Use only for a concept or hero image that has no literal screen. Give the generator two separate references: a composition reference (layout, where the eye goes) and a style reference (palette, type, finish). Never use it for a player, a timing, a log or any exact value; raster text is unreliable and cannot be audited.

Route rule: subscription only (for example Codex OAuth image generation through Hermes or the codex CLI). No paid API keys. If no such route exists, skip raster generation and say so in the report.

Status when this skill was written: no subscription image-generation route was found on maxiclaw (the codex CLI exposes image input, not image output), so raster generation was not tried.
