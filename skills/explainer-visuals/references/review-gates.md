# Review gates

Run them in this order. Do not skip to the rubric.

## Gate 1: two-second test (hard gate)

Render the image with the eyebrow, headline, subhead, captions and footer hidden (CSS `visibility:hidden`, layout kept). Small labels and values stay. A judge sees only that version and answers: from the composition alone, can a viewer point at what changed, or at which state is which, within two seconds?

Fail when:
- the eye has no single place to go
- the two compared things look the same
- the meaning needs the hidden text
- a number appears twice
- an axis, bar or mark does not match what the reply says

A fail means change the composition (same slot, bigger mark, one highlight), not the prompt. Only after the composition passes does tuning the prompt make sense.

Implementation: `scripts/explain-demo.ts --shots` writes `<name>-bare.png` beside each screenshot and an `.input.txt` with the reply. `scripts/explain-score.ts` runs the two-second test on the bare image first; a fail scores 0 and the exit code is 1.

## Gate 2: Opus 8/10 rubric

`claude -p --model opus` opens the reference PNGs (the style bar) and the image, with the reply as ground truth. Eight areas scored 1 to 10: realism, legibility, density, journey (does the headline state the conclusion), metrics (exact, honest, illustrative labeled, no axis without timings), how, clarity, style (match to the reference, light palette). Overall must be 8 or higher for every image.

Grading rules:
- Timelines and state keys are graded on whether the states and timing make sense for the reply, not on whether they look like screenshots.
- Anything invented, paraphrased where the reply gives exact text, or contradicting the reply is a serious fault.
- A status-only reply must have produced NO_IMAGE; there is nothing to score.

## Approval

The image set is approved only when every image passes gate 1 and scores 8 or higher in gate 2. Report which images pass and which do not; do not average.
