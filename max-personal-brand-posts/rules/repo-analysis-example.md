# Repo Analysis Example

Worked example for: `maxpetrusenko/mvp-1-collab-board`

## Grounded Inputs

Source: GitHub README and package manifests fetched on 2026-03-10.

- Repo: `https://github.com/maxpetrusenko/mvp-1-collab-board`
- Live app: `https://mvp-1-collab-board.web.app/b/mvp-demo-board`
- Demo video: `https://www.loom.com/share/b2016cdf9d4a4b4e96fec12253fec0d9`
- Core promise: realtime collaborative whiteboard MVP
- Stack: React, Vite, TypeScript, Konva, Yjs, Firebase, Playwright
- Multiplayer proof: cursor sync, object sync, presence awareness
- AI angle: prompt-to-diagram / AI command path in product docs

## High-Signal Proof Points

- realtime multi-user board, not static mock UI
- canvas + sync stack implies real interaction complexity
- Firebase + Yjs + Konva is specific enough to signal engineering depth
- live deployment + public repo + loom demo = strong proof bundle

## Weak Angles

- generic "AI whiteboard"
- long feature list
- vague collaboration claims
- saying "cool project" or "excited to share"

## Strong Angles

### Outcome-first

People want the board to keep up with thinking, not slow it down.

### Workflow compression

Prompt instead of dragging boxes for 20 minutes.

### Technical proof

Realtime cursors, object sync, canvas editing, deployed live.

## Example Extraction

Bad:

```text
Built an AI-powered collaborative whiteboard with React, Firebase, Yjs, Konva, authentication, presence, sync, and tests.
```

Why bad:
- reads like a resume bullet
- no user outcome
- no tension

Better:

```text
Your whiteboard should keep up with the conversation.

CollabBoard turns a prompt into a diagram, then lets a team edit it live together.

Built with React + Konva + Yjs + Firebase.

Demo:
https://www.loom.com/share/b2016cdf9d4a4b4e96fec12253fec0d9
```

Why better:
- outcome first
- product legible
- technical proof for insiders
- clean demo CTA
