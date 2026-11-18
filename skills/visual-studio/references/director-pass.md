# Director pass

Read when a visual or film is about to be made. The five lines in SKILL.md section 2 are the whole contract. This file holds the templates and what each line borrows from existing skills.

## Source of each line
- Intent: HyperFrames `story.md` section 1 ("the one thing"), post-video-director step 2 ("one idea, one sighting").
- Key frame and first look: post-video-director "the one thing a viewer should see", explainer-visuals composition rule 1 (one close-up).
- Two-second test: explainer-visuals `review-gates.md` gate 1.
- Motion verdict: post-video-director step 3 (medium choice, stop at the first yes), HyperFrames `spec.md` ("something new every 2 to 4 s" applies to films, not to cards).

## Template (copy into the work folder as DIRECTOR.md)

```
SOURCE:   the exact text or data the visual must obey (paste it)
INTENT:   one sentence
KEY FRAME: the picture, with the one highlighted thing
FIRST LOOK: the object the eye lands on
BARE TEST: what stays pointable with the headline, subhead, captions, footer hidden
MARKS:    each mark and the evidence behind it (dot = value, bracket = range)
NOT SHOWN: what the source did not give, so it stays off the picture
MOTION:   yes or no, and the mechanism that arrives over time
BEATS:    (clips only) time, what lands, hero move
```

## Clips
- 3 to 5 seconds. One hero move per beat. Hold the key frame for the last second so a paused frame reads as a finished poster.
- Motion is a function of timeline time. HyperFrames contract: paused GSAP timeline on `window.__timelines`, no `Date.now`, no random, no network.
- A sweep or race that maps to a data axis must map linearly, or it implies the wrong thing.
- Typing or revealing a digit, filling a bar, a cursor crossing an axis earn motion. Colour swaps do not.

## Films over about 15 seconds
Do not shortcut. HyperFrames `story.md` (three storylines, the person picks), `spec.md` (every adjective becomes a number), `storyboard.md` (stills the person approves), then render. Run the director lines first as the front page of `SPEC.md`.

## AI footage
Add Hermes `director-prompts`: locked look block, one camera move per shot, angle named before action, emotion as behaviour, durations sum to the clip. Two bodies touching: `duo-motion-direction` before spending a generation.

## Posts
Hermes `post-video-director` runs the scorecard (28 of 40) and the visual ledger before any render. This pass sits inside its step 2 and step 5.
