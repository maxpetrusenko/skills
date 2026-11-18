# Experiment: director pass plus HyperFrames against explainer-visuals

Date 2026-11-18. Question: does the director and video route make better explainer images than the current explainer-visuals route?

## Setup
- Fixtures (earshot `test/fixtures/explain/`): gate-threshold, orca-timeline, perf-illustrative. Reply text is the ground truth for every image.
- Arm A: the explainer-visuals renders from the last earshot round (390 px wide at 2x, 780 px).
- Arm B: director pass (`DIRECTOR.md`), one HyperFrames scene per fixture, 1080x1350, light theme, Fraunces, DM Sans, IBM Plex Mono. Still taken at the hold frame, plus a 4.8 to 5.6 s clip.
- Same scorer for both: earshot `explain-score.ts`, gate 1 on the bare image, then `claude -p --model opus`, 8 of 10 bar, same reference PNGs.
- Arm B got three rounds at most (A's earshot loop also ran three). Round 2 and 3 fixes came from the scorer's notes.

## Scores (overall, out of 10)

| Fixture | A: explainer-visuals | B round 1 | B round 2 | B round 3 (final) |
| --- | --- | --- | --- | --- |
| gate-threshold | 6 (7 in the earlier earshot round) | FAIL gate 1, shows "needs 0.55" after "prints three decimals" | 7 | 8 |
| orca-timeline | 8 | 7 | 8 | 8 |
| perf-illustrative | 7 | 7 | 8 | 8 |

Gate 1 (two-second test): A passed 3 of 3. B passed 2 of 3 in round 1, 3 of 3 afterwards.
Round 3 was run only for gate-threshold. Orca-timeline and perf-illustrative final scores are round 2.

## Verdict
Director plus HyperFrames scored higher or equal on all three, by 2, 0 and 1 points after iteration. That is inside the plus or minus one noise seen between runs of the same image, and three fixtures is a small sample. Honest reading: slightly better, not proven.

What produced the gain was the director pass, not video:
- Show the bug state next to the fix (orca-timeline red outline on the wrong grey bar). The judge had marked A down for never drawing the bug.
- Drop marks that imply data the reply did not give (the fading waveform in perf-illustrative that the judge read as playback time).
- Name the first look and test it bare (the green 9, the green bar, the short marker).

What did not help:
- HyperFrames as a still renderer. Equal quality to the earshot templates. It cost more setup: layout by hand, bare variant by hand, no exact-string code path.
- Motion. The gate-threshold clip (digits typing in, the 9 landing) and the perf race are the only two where motion shows the mechanism. Orca-timeline is a colour change and a still carries it.

What B had that A did not: a larger canvas (1080x1350 against 780 px wide) with more room, which helped density scores. Not a controlled variable.

What A has that B lacks: it is automated. Earshot generates exact strings and numbers from code and gates them. B's numbers were typed by hand.

Recommendation: keep explainer-visuals as the generator for reply images. Use the director lines as a required pre-step (bug state shown, no implied data, named first look). Use HyperFrames for stills and clips only when the reply is a post, or when motion shows a mechanism.

## Files
`~/Desktop/Projects/media/visual-studio-experiment/`
- `arm-a-explainer-visuals/*.png`
- `arm-b-director-hyperframes/*.png`, `*-bare.png`, `*.mp4`
- `scores/A.json`, `B.json` (round 1), `B2.json`, `B3.json`
- `source/DIRECTOR.md`, `build.mjs` (final), `build.r1.mjs`

## Caveats
- Clip frames were spot-checked at one mid moment (gate-threshold at 2.0 s). The other clips were checked by `ffprobe` size and duration only. Frame extraction on pro was blocked by the fleet load guard.
- A was not re-rendered. It is the final earshot render, scored again today.
