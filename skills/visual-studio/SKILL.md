---
name: visual-studio
description: Umbrella for every visual and film job. Routes a request to the right sub-skill (explainer image, architecture diagram, chart, post media, storyboard, HyperFrames video, reverse a reference video, AI video direction) and runs one shared director pass and one review gate on the result. Use for "make an image/diagram/chart/video for this", "storyboard", "director", "explain this visually", "visual explainer", "post media", or when unsure which visual skill applies.
version: 0.1.0
metadata:
  hermes:
    tags: [visual, video, image, diagram, director, storyboard, hyperframes, explainer]
---

# visual-studio

One front door for visuals. It does not replace anything. It picks the sub-skill, runs the director pass, applies the house rules and the review gate. Sub-skills keep their own SKILL.md and stay where they are.

Details live in `references/`:
- `references/inventory.md`: every visual or video skill, path, host, in use or not
- `references/director-pass.md`: the pass in full, with the templates
- `references/house-rules.md`: shared rules and how conflicts between skills resolve
- `references/review-gate.md`: two-second test, Opus rubric, commands
- `references/render-owners.md`: which tool renders what, and where to run it
- `references/experiment-2026-11-18.md`: director plus HyperFrames against explainer-visuals, with scores

## 1. Route first

Find the row, load the sub-skill, then run section 2 on whatever it produces.

| Request | Go to | Renders with |
| --- | --- | --- |
| A reply needs a picture, or "should this have one" (before/after, state key, timing range, log compare, layers) | `explainer-visuals` (decides image or NO_IMAGE first) | earshot templates or HyperFrames stills (section 4) |
| Architecture or system diagram from code or a description | `eraser-diagrams` for layout, `mermaid-diagrams` for flow, sequence, ER | Mermaid or Eraser, then restyle to the house rules |
| Chart, plot, dashboard, numbers | `data-visualization` (Python) or the `dataviz` skill; story shape from `data-storytelling` | matplotlib, plotly, or HyperFrames `types/data.md` for motion |
| Media for an X or LinkedIn post (video, still, explainer) | `post-media` (`post.json`), brief and scorecard from Hermes `post-video-director` | HyperFrames |
| Storyboard before animating | `hyperframes/references/storyboard.md` and `story.md`, `spec.md` | HyperFrames snapshot stills |
| Any video, launch film, explainer, kinetic type, vertical clip | `hyperframes` (then `hyperframes-cli`, `hyperframes-registry`, `media-use`) | HyperFrames |
| Rebuild or copy a reference video | `reverse-any-video` | HyperFrames |
| Direction for AI-generated footage (shot list, camera, performance, pacing) | Hermes `director-prompts`, then `ai-video-production`; two-body dance shots `duo-motion-direction` | Seedance, Veo, via Hermes lanes |
| Narrated story over stills | Hermes `narrated-story-video` | HyperFrames |
| Type, colour, spacing, tokens | `visual-design-foundations` | none, it feeds the others |
| Download a source video | `video-downloader` | yt-dlp |
| Several of the above | split the job, route each part, run one director pass over the whole | |

Hermes-owned skills live on maxiclaw under `~/.hermes/skills/` (`content-publishing/post-video-director`, `media/director-prompts`, `media/ai-video-production`, `media/narrated-story-video`, `duo-motion-direction`). Read them there, do not copy them.

Which one is "the director"? Max's phrase maps to two things. For posts it is Hermes `post-video-director` (idea, medium, world, shots, reviewer). For any film it is the HyperFrames flow `story.md` then `spec.md` then `storyboard.md`. For AI footage it is `director-prompts`. Section 2 is the common core of all three.

## 2. The director pass (every output goes through it)

Write these five lines before anything renders. Four sentences is fine. Skip none, even for a still.

1. **Intent.** What the viewer believes or does afterwards, one sentence. If you cannot write it, there is no image (`NO_IMAGE`).
2. **Key frame.** The single frame that carries the intent. Describe it as a picture, not a list of facts. A still is its key frame. A clip is a key frame plus the path to it.
3. **First look.** What the eye lands on first, named as an object ("the green 9", "the short green marker"), not a topic.
4. **Two-second test, planned.** Hide headline, subhead, captions and footer. Say what a viewer can still point at. If the answer is "nothing", redraw the composition before drawing anything else.
5. **Motion verdict.** Does motion earn its place? Yes only when the mechanism arrives over time (a digit appearing, a race, a fill). A static comparison stays a still. Default no.

Then, by output type:
- Still: key frame, build, gate.
- Clip over about 3 seconds: add a storyboard, one line per beat with a time, one hero move per beat (`references/director-pass.md`).
- Film over about 15 seconds: use the full HyperFrames flow (`story.md`: three storylines, one pick, then `spec.md`). The pass above is the front page of that.
- AI footage: the pass plus `director-prompts` blocks (look locked, one move per shot, durations sum).

What the pass changed in the experiment: it added the missing evidence (show the bug state, not only the fix), it removed marks that implied data the reply never gave, and it fixed the first look. It did not make the render look better by itself. See `references/experiment-2026-11-18.md`.

## 3. House rules (shared)

Apply to every sub-skill output. Conflicts and how they resolve are in `references/house-rules.md`.

- Light theme only. No dark mode, no dark void backgrounds, no glow.
- A real typeface, not Inter, Roboto, Arial or system defaults. HyperFrames bundles Fraunces, DM Sans, Newsreader, Source Sans 3, IBM Plex Mono. Mono for any exact value.
- A committed palette in CSS variables. One accent that carries the point. No purple on light paper.
- No badges, count chips, status pills, emoji, or helper captions that restate the picture.
- Exact numbers and strings come from the source text, copied character for character. A number appears once, at the mark it describes. Illustrative data says so in the eyebrow.
- No axis, duration, average or stage breakdown the source did not give.
- Real things from their source (screens, logos). Draw only what has none. Never fake UI.
- Text rules: unslop every on-screen line first. No dashes in on-screen copy.
- Phone first. Check at about 390 px wide. Key text at least 28 px on a 1080 canvas.
- Headline states the conclusion in under nine words. Eyebrow is `PROJECT / KIND`.

## 4. Pick the render path

| Output | Tool | Notes |
| --- | --- | --- |
| Earshot reply image (log, state key, range, layers) | earshot `explain-*` templates | exact strings and numbers come from code |
| Any still outside earshot | HyperFrames `snapshot --at <t>` on a one-scene composition | 1080x1350 for feed, 1600x900 for link cards |
| Clip | HyperFrames `render --quality looks` (draft), `standard` or `high` (final) | `check --json` first |
| Chart | matplotlib/plotly PNG, or HyperFrames when it moves | one data module drives every number |
| Diagram | Mermaid or Eraser output restyled, or HyperFrames HTML | no boxes joined by lines for architecture; layered stack, icon per node |
| Captured UI | Playwright element screenshot, one outline | `explainer-visuals` capture method |

Never render on maxiclaw when its disk is under about 2 GB free. Check `df -h ~` first. See `references/render-owners.md`.

## 5. Review gate (every output)

Run in this order and do not skip to the rubric.

1. **Two-second test.** Render the bare version (chrome hidden, layout kept). Ask a judge, or yourself with a stopwatch, what the eye lands on and whether the change or state is pointable. A fail changes the composition, not the prompt.
2. **Opus rubric.** `claude -p --model opus`, eight areas, every image 8 of 10 or better to ship. The command is in `references/review-gate.md`. Judge against reference images and against the source text as ground truth.
3. **Fix named defects, run once more, stop.** After two rounds that fail, ship no image or say what blocks it. Do not average scores. Report per image.
4. Video adds a frame check: snapshot 3 moments, read them at phone size, `ffprobe` size and duration.

Scores vary by plus or minus one between runs of the same image. A single 7 against an 8 is not a difference. Compare across several fixtures.

## 6. Hand-off

Report the absolute paths of the PNG or MP4, the bare frame, the director lines, the gate result per image, and what was not run. Social drafts need media attached, so a post image or clip is delivered with its draft. Do not commit MP4s.

## 7. What not to do

- Do not copy sub-skill content into this one. Link to it.
- Do not edit upstream-managed skills (`hyperframes*`, `media-use`, `reverse-any-video`). The CLI updates overwrite them.
- Do not start a render before the director lines exist.
- Do not use video because a skill exists for it. Section 2, line 5.
