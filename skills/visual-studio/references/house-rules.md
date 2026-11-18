# House rules and conflicts

## Rules (from Max's standing rules and the existing skills)
Light theme, real typeface, committed palette, no purple on light paper, no badges or chips, no emoji, no dashes in copy, exact numbers once at their mark, illustrative data labelled, phone first. Sources: AGENTS.md UI section, explainer-visuals composition rules, post-media validation, post-video-director.

## Conflicts found and how they resolve

| Conflict | Where | Resolution |
| --- | --- | --- |
| Dark architecture diagrams | Hermes `architecture-diagram` template (dark SVG), `post-video-director` tool table | Use for layout only. Final output is light. |
| 1920x1080 default | `hyperframes` ("a new video is 1920x1080") | Feed media is 1080x1350 (`post-media`). Wide 1920x1080 only for landscape asks. |
| Inter and system sans on boards | `hyperframes/references/storyboard.md` ("Inter or the system sans-serif") | Boards are working files. Anything shipped uses a bundled real face. |
| Dark paper | `post-media` rejects it, `hyperframes` types/music and 3D may use dark | House rule wins for Max's outputs. Music and 3D films are the one place a dark ground can be argued, and only when Max asks. |
| Raster image generation | `explainer-visuals` allows it for concept art, needs a subscription route | Never for exact values, timings or logs. No paid API keys. |
| Tool owner for stills | earshot templates, HyperFrames snapshot, Playwright, matplotlib | Earshot for replies, HyperFrames for posts and anything with motion, Playwright for captured UI, Python for data charts |
| Remotion | repo `remotion*` skills | Superseded by HyperFrames (Max 2026-11-11). Keep only for existing Remotion source (`remotion-to-hyperframes`). |
| Two direction notes | `post-video-director` and `post-visual-direction` | Prefer `post-video-director` (newer, has gate scripts). Do not merge without Max. |
| Illustrative wording | explainer-visuals eyebrow rule vs post copy | Eyebrow carries "ILLUSTRATIVE DATA". Footer states the scope or limit. |
