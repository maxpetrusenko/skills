---
name: explainer-visuals
description: Make or review a visual explainer image for an agent reply: a before/after, a state key, a timing comparison, a layered architecture, or a decision to make no image at all. Use for "visual explainer", "explain image", "earshot image", "before/after visual", "what changed picture", "make a diagram of this reply", or when judging whether an explainer image is good enough to ship.
---

# explainer-visuals

One reply in, zero to three phone-sized images out. The picture must make the change visible before anyone reads a word. A picture that reads like a formatted summary has failed, even when every fact in it is right.

Code that does this in earshot: `src/explain-*.ts`, prompt `prompts/visual-explainer.v4.txt` plus `prompts/visual-explainer-format.v4.txt`, scorer `scripts/explain-score.ts`. The rules below and the prompt are one rule set; `test/explain-refs.test.ts` fails if they drift.

Details live in `references/`:
- `references/methods.md`: the four methods, how to run each
- `references/composition.md`: composition rules with the reasons
- `references/review-gates.md`: two-second test, then the rubric
- `references/references.md`: reference images, their input text, Max's ratings and critique, good and bad pairs

## 1. Image or NO_IMAGE

Decide first. Most replies get no image.

| Reply | Answer |
| --- | --- |
| "Lint, typecheck, build and tests all pass (343 tests)." | NO_IMAGE. A status line is a sentence. |
| A status update, a test, lint or build result, a one-line fix with nothing to see, an answer to a question | NO_IMAGE |
| A value that looked wrong but was right, or a wrong value now fixed | image: log comparison |
| Two states a user could not tell apart (waiting vs playing, grey vs green) | image: state key |
| Numbers from the reply: wait, size, speed | image: range on one axis |
| A recommendation or design with named layers | image: layered architecture |
| A visible interface change (new button, new row) | image: capture and annotate |
| Something that changes over time with no stated timings | storyboard stills, then HyperFrames |

When unsure, no image. A status-only reply must never get one.

## 2. Pick the method

| Method | Use for | Never for |
| --- | --- | --- |
| Capture and annotate | UI fixes: a real element screenshot, tightly cropped, one outline | anything that has no screen |
| Render from data | perf numbers and log values: exact strings and numbers come from code, the model only sets emphasis | concept art |
| Storyboard stills, then HyperFrames | anything that changes over time | static comparisons |
| Raster image generation with a separate composition reference and a separate style reference | concept or hero images with no literal screen | the player, timings, logs, any exact value |

Raster generation needs a subscription route (for example Codex OAuth image generation). No paid API keys. If no route exists, skip it and say so. See `references/methods.md`.

## 3. Composition rules (these scored; the first draft did not)

1. One close-up. One concept per image, at most three images per reply.
2. Show the state in the same slot. Waiting and playing are the same player bar with different contents, one above the other. The eye compares contents, not frames.
3. The state is visible before the label is read: a dashed line against a green waveform needs no caption.
4. Show each number once, at the mark it describes. Never again in a chip, caption or footer.
5. Marks match the evidence:
   - a dot is a value
   - a bracket is a range
   - no time axis, no lanes and no durations unless the reply gives timings
   - no axis, no durations, no invented average, no stage breakdown otherwise
6. Exact strings stay exact. Log values are copied character for character in mono. Both lines share one column grid; only the digits that differ are highlighted, and the code computes the highlight.
7. Illustrative data says so in the eyebrow ("EARSHOT / ILLUSTRATIVE DATA").
8. Light theme, a real typeface, AA contrast, no purple, no badges, no emoji, no dark mode.
9. Phone first, about 390 px. The layout still works at 1280.
10. No lone metric card, no numbered footer lines repeating the captions, no empty whitespace.

Text parts: eyebrow `PROJECT / KIND`, a declarative headline under nine words that states the conclusion, a one-line subhead, an optional one-line footer that states the scope or limit.

When the numbers are the wait until something appears in the player, merge the two: the track is the player bar, dashed while waiting, a waveform once available, and the bracket sits where it becomes available. Merge only when the timing evidence describes that same player behavior. Keep a gate log separate.

## 4. Review gates, in this order

1. Two-second test. Render with the headline, subhead, captions and footer hidden. Can someone point at what changed in two seconds? If not, change the composition. Do not touch the prompt first.
2. Then the Opus rubric: eight areas, every image 8/10 or higher to ship, graded against the reference PNGs. A timeline or state key is graded on whether its states and timing make sense, not on whether it looks like a screenshot.

Run both with `pnpm tsx scripts/explain-score.ts <dir> --min 8`. The demo script writes the bare screenshot next to each image (`*-bare.png`) and the scorer runs the two-second test first, as a hard gate. See `references/review-gates.md`.

## 5. Run it in earshot

```
pnpm tsx scripts/explain-demo.ts --shots          # live model over test/fixtures/explain/*.json, 390 and 1280 px
pnpm tsx scripts/explain-preview.ts spec.json out --shots   # a saved spec, no LLM
pnpm tsx scripts/explain-score.ts <shots dir> --min 8
```

Heavy work (renders, Playwright, scoring) runs on maxiclaw (`ssh mini`, `~/Projects/earshot`).

## 6. Types the code accepts

`log_compare`, `state_key`, `range_chart` (with `player: true` for wait-until-available), `architecture` (layered only, real names, an icon on every node, one flow direction), `ui_before_after`. Code-level sequence diagrams and boxes joined by lines are rejected.
