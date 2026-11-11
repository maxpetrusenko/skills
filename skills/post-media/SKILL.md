---
name: post-media
description: Make post media with HyperFrames, Max's default generator for every post video, still image and explainer. Use for any request to make media for a post, launch, explainer, an X or LinkedIn video, or "make a video/image for this". Renders 1080x1350, 1080x1920, 1920x1080 video and 1080x1350 / 1600x900 PNG stills from a post.json.
---

# post-media

HyperFrames (HTML to video) behind a `post.json`. Light mode, real font, real proof assets, one hook, 2 to 4 beats, an end card. Reference: earshot's `video/`.

## CLI

```bash
post-media new <slug> [--from post.json]        # scaffold ~/Desktop/Projects/media/<slug>/ (post.json + assets/)
post-media render <slug> [--formats feed,story,wide]   # check, render, ffprobe, 3 frames per format
post-media stills <slug> [--formats still-feed,still-wide]  # PNG 1080x1350 and 1600x900
```

Formats: `feed` 1080x1350 (X, LinkedIn), `story` 1080x1920, `wide` 1920x1080. Dimension strings work too. Output: `<project>/out/<slug>-WxH.mp4`, `out/frames/<fmt>-{1,2,3}.png`, `out/report.json`, `stills/<slug>-WxH.png`. Never commit the mp4s.

Binary: `~/Desktop/Projects/skills/skills/post-media/bin/post-media.mjs` (symlinked to `~/.local/bin/post-media`). First run does `npm install` in `template/`.

## Steps

1. Gather real assets first: screenshots, recordings, a memo mp3. Put them in `<project>/assets/`. Placeholders are the last resort; never fake UI that the product does not have (the screenshot must show what the beat claims).
2. Pick the template: `post.example.json` is the default (terminal beat, phone beats, end card). Use `terminal` for CLI moments, `image(s)` with `frame` `phone` or `card` for screens, text only for a statement beat. Two images side by side with `label`s give a before/after.
3. Write the scenes in `post.json`. Run the unslop skill on every on-screen line first. Hook is one line, beats are short, the end card is name plus URL.
4. `post-media new <slug> --from <file>` (or edit the scaffolded `post.json`), then `post-media render <slug>`. For image-only posts run `post-media stills <slug>`.
5. Verify: render already runs `hyperframes check`, ffprobe (size, duration vs expected) and extracts 3 frames. Open the frames and read them at phone size: text legible, nothing clipped, no placeholder look. Fix and re-render.
6. Hand off the absolute paths of the mp4/PNG, the frames and `report.json`. Social drafts need media attached: this is that media.

## post.json

```json
{
  "hook": "One line.",
  "hookSub": "optional",
  "beats": [
    { "text": "Headline", "sub": "optional", "dur": 3.6,
      "image": "assets/shot.png", "frame": "phone|card",
      "images": [{ "src": "assets/a.png", "label": "Before" }, { "src": "assets/b.png", "label": "After" }],
      "terminal": { "title": "claude", "lines": ["> cmd", "output", "Listen: https://..."], "highlight": 2 },
      "audio": "assets/clip.mp3" }
  ],
  "end": { "name": "name", "tag": "optional", "url": "github.com/you/repo" },
  "voiceover": "assets/voice.mp3",
  "palette": { "paper": "#faf7f2", "ink": "#1b1b18", "accent": "#1f6f5c" },
  "font": { "display": "newsreader", "body": "source-sans-3", "mono": "ibm-plex-mono" },
  "pace": { "hook": 2.6, "beat": 3.6, "end": 3.2 },
  "formats": ["1080x1350"],
  "still": { "headline": "optional, default hook", "image": "assets/shot.png", "frame": "phone", "footer": "url" }
}
```

- Beats: 1 to 4. Per beat use `image`, `images`, `terminal` or none. Asset paths resolve from the project dir (`~` and absolute allowed). A beat with `audio` stretches to fit the clip. `voiceover` stretches the whole film to cover the track.
- Fonts bundled: newsreader, fraunces, source-sans-3, dm-sans, ibm-plex-mono. Inter, Roboto, Arial are rejected.
- Validation errors (build stops): dark paper, purple accent on light paper, banned fonts, emoji, en/em dashes, missing hook or end. Warnings: AI-tell words (unslop).
- Motion budget: hook rule draw plus one media rise and slow scroll per beat. Do not add more.

## Render contract (HyperFrames)

Generated compositions follow the `hyperframes` skill: timed `.clip` elements, one paused GSAP timeline registered on `window.__timelines["main"]`, no network, no `Date.now`, bundled-font `@font-face` from `assets/fonts/`, relative `assets/` paths. Do not hand-edit `build/`; edit `post.json` or `template/src/compose.mjs`. Grades, music, TTS and avatar clips: `media-use` (free local tools first; HeyGen sign-in only if a HeyGen model is explicitly needed). Voiceover for free: `npx hyperframes tts` (Kokoro on device), then set `voiceover`.

## Mac mini install note (not installed from here)

Rule 3b: skills never live under `~/Desktop` on the mini. On maxiclaw: clone the skills repo to `~/Projects/skills`, then `ln -s ~/Projects/skills/skills/post-media ~/.claude/skills/post-media` and `ln -s ~/Projects/skills/skills/post-media/bin/post-media.mjs ~/.local/bin/post-media`. Set `POST_MEDIA_HOME=~/Projects/media` so projects stay off Desktop. Needs Node 22+, ffmpeg, Chrome (`npx hyperframes browser ensure`).
