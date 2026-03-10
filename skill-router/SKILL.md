---
name: skill-router
description: "Loads when the user asks to load new skills for the repo. Also use when the user mentions 'load skill', makes a PRD, working on a new problem. checking project requirements."
metadata:
  short-description: Offline skill loader
---

# Skill Router

Purpose: keep context small by selecting and loading only relevant skills per task.

## Offline Library

- Path: `/Users/maxpetrusenko/Desktop/Projects/skills/`
- Skill files: paths listed in that index (expected `.../SKILL.md`)

## Required Workflow

1. Read only `/Users/maxpetrusenko/Desktop/Projects/skills/index.md`.
2. Select the minimum set of skills that fully covers task needs (balanced; no hard cap).
3. Copy selected skill folders to project repo to .agents or ./claude folder so they will be loaded in context every time.
4. Start work and report:
   - `Skills loaded now: ...`
   - `Potential skills later: ...`

## Selection Method

1. Extract task intent signals (domain, action, constraints).
2. Match against index keywords and choose the highest-coverage skill first.
3. Add additional skills only when they cover missing capability.
4. Stop adding when coverage is complete; avoid redundant overlap.

## Constraints

- Never enumerate all skills in the library.
- Never paste full skill docs into chat.
- If there is no clear match, ask for one clarifying keyword.
- Skills are sourced from `/Users/maxpetrusenko/Desktop/Projects/skills`.
- For newly added skills, run security checks before first regular use.
