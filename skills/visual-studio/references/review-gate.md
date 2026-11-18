# Review gate

Two gates, in order. Same gate for every image whatever tool made it.

## Gate 1: two-second test (hard)
Produce the bare image: eyebrow, headline, subhead, captions and footer hidden with `visibility:hidden` so layout stays. Small labels and values stay. A judge sees only that and answers: can a viewer point at what changed, or at which state is which, in two seconds?

Fail when the eye has no single place to go, the compared things look alike, the meaning needs the hidden text, a value is printed twice as a value label (axis ticks do not count), or a mark does not match the source.

A fail means change the composition. Not the prompt, not the colours.

In HyperFrames, build the composition with a `.bare` class on the root that hides `.chrome`, and snapshot both.

## Gate 2: Opus rubric
Eight areas, 1 to 10: realism, legibility, density, journey, metrics, how, clarity, style. Overall 8 or higher for every image. The source text is ground truth: anything invented or paraphrased where the source gives exact text is a serious fault.

Scorer: earshot `scripts/explain-score.ts` (branch `feat/explainer-references` until merged). It reads `<name>.png`, `<name>-bare.png` and `<name>.input.txt` (the source text) from one folder, runs gate 1 on the bare image, then gate 2.

```
cd ~/Desktop/Projects/earshot
pnpm tsx scripts/explain-score.ts <dir> --json > scores.json     # exits 1 on a gate 1 fail
```

It runs `claude -p --model opus` on the subscription session, API keys stripped. Exit 2 means that session is not usable. Run it on pro or uniclaw (see `render-owners.md`). Three images take a few minutes.

## Rules
- Report per image. Never average.
- Scores move plus or minus one between runs of the same image (the same gate-threshold image scored 6 here and 7 in an earlier round). Treat a one point gap as noise.
- Two failed rounds means no image, or a named blocker.
- Video adds: snapshot three moments, read them at phone size, `ffprobe` size and duration, confirm the hold frame is the key frame.
