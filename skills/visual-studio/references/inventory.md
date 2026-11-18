# Inventory (2026-11-18)

Checked by listing each directory and reading each SKILL.md. "Use" is evidence-based where noted, otherwise "unverified". pro = this MacBook, mini = maxiclaw.

## Visual and video skills

| Skill | Path | What it does | Where | Use |
| --- | --- | --- | --- | --- |
| explainer-visuals | pro `~/.claude/skills/`, mini `~/.claude/skills/`, repo `skills/explainer-visuals` (uncommitted until the PR) | Decides image or NO_IMAGE for an agent reply, four methods, composition rules, two-second test, Opus rubric | pro, mini | in use (earshot explainer, PR #15) |
| hyperframes | pro `~/.claude/skills/`, `~/.hermes/skills/`; mini `~/.hermes/skills/` | HTML to video contract, work loop, `story.md`, `spec.md`, `storyboard.md`, types for launch, explainer, music, data, vertical, 3D, character | pro, mini | in use (post-media, earshot video) |
| hyperframes-cli | same | CLI by job: init, check, snapshot, render, publish | pro, mini | in use |
| hyperframes-registry | same | About 450 ready blocks (transitions, titles, captions, charts) | pro, mini | in use |
| media-use | pro `~/.claude/skills/`, `~/.hermes/skills/`; mini `~/.hermes/skills/` | Music, SFX, images, icons, voice, avatar, cutouts, grades | pro, mini | in use |
| reverse-any-video | same | Rebuild a video as an editable HyperFrames project, checked frame by frame | pro, mini | unverified (HyperFrames Pro feature) |
| post-media | repo `skills/post-media`, pro symlink `~/.claude/skills/post-media` | `post.json` to HyperFrames feed, story, wide video and stills; bundled fonts; validation | pro | in use (earshot demo video) |
| duo-motion-direction | pro and mini `~/.hermes/skills/` | Prompt grammar and QC for two-body AI dance video (Seedance, Veo) | pro, mini | in use by Hermes lanes (unverified recent) |
| director-prompts | pro and mini `~/.hermes/skills/media/director-prompts` | Four vocabularies for AI video prompts: angle, movement, performance, story; look block rule | pro, mini | unverified |
| ai-video-production | pro and mini `~/.hermes/skills/media/ai-video-production` | Provider choice, realism and uncanny-valley doctrine, probes | pro, mini | unverified |
| narrated-story-video | pro and mini `~/.hermes/skills/media/narrated-story-video` | First-person story in a cloned voice over stills, called by post-video-director | pro, mini | in use by Hermes X lane |
| post-video-director | pro and mini `~/.hermes/skills/content-publishing/post-video-director` | Picks one idea, medium, visual world, shot list, reviewer; scorecard 28 of 40; visual ledger | pro, mini | in use (X daily, live copy on mini) |
| post-visual-direction | pro `~/.hermes/skills/content-publishing/post-visual-direction` | Visual that matches a post's claim (older direction note, 195 lines) | pro | unverified, overlaps post-video-director |
| diagramming | pro and mini `~/.hermes/skills/diagramming` | Category stub (Excalidraw) | pro, mini | stub only |
| eraser-diagrams | repo `skills/eraser-diagrams` | Architecture diagrams from code or description | repo | unverified |
| mermaid-diagrams | repo `skills/mermaid-diagrams` | Mermaid syntax guide | repo | unverified |
| data-visualization | repo `skills/data-visualization` | matplotlib, seaborn, plotly charts | repo | unverified |
| data-storytelling | repo `skills/data-storytelling` | Narrative structure for analytics | repo | unverified |
| visual-design-foundations | repo `skills/visual-design-foundations` | Type, colour, spacing, iconography principles | repo | unverified |
| video-downloader | repo `skills/video-downloader` | yt-dlp downloads | repo | unverified |
| remotion, remotion-render, remotion-best-practices | repo `skills/` | Remotion video (superseded by HyperFrames for Max's posts) | repo | superseded |
| canvas-design, baoyu-cover-image, imagen, html-to-image-automation | repo `skills/` | Raster art, cover images, image generation | repo | unverified, outside this umbrella's first pass |
| dataviz, artifact-diagramming | Claude built-in skills | Chart and diagram guidance for artifacts | built in | available |

## Not found on either host
No skill is named `visual-studio`, `director`, or `video-director`. `hermes skills search director` returned only unrelated hub entries (director-readiness-advisor, directory skills, a clawhub "Director Beat Split"). `gbrain search "director skill"` and `"video director"` returned conversation logs only.

## Gaps
- mini `~/.claude/skills` holds only explainer-visuals. HyperFrames skills there live under `~/.hermes/skills`.
- Two overlapping Hermes direction notes (`post-visual-direction`, `post-video-director`). Not merged here. Open question for Max.
- Nothing owns "architecture diagram in the house style". Eraser and Mermaid defaults are not light theme with a chosen face. House rules apply on top.
