# Requirement And Completion Signals

## Requirement Source Files

Prefer files whose names indicate product intent:

- `docs/requirements*.md`, `requirements*.md`, `REQUIREMENTS*.md`
- `docs/prd*.md`, `PRD*.md`, `product-requirements*.md`
- `spec*.md`, `brief*.md`, `assignment*.md`
- `docs/tasks*.md`, `TODO.md`, `PLAN.md`, `PRESEARCH.md`
- `README.md` and `CHANGELOG.md` only after stronger sources

Ignore dependency manifests named `requirements.txt` unless the user asks for environment requirements.

## Requirement Line Signals

Keep lines with:

- Checkbox tasks: `- [ ]`, `- [x]`
- Modal verbs: `must`, `should`, `need`, `requires`, `shall`
- Product markers: `acceptance`, `criteria`, `user story`, `feature`, `constraint`, `non-goal`
- Release markers: `ship`, `launch`, `done`, `complete`, `deployed`

## Completion Signals

Completed:

- `CHANGELOG.md` release entries
- Git tags or GitHub releases
- `shipped`, `complete`, `completed`, `done`, `launched`, `deployed`
- Mostly checked task lists in requirement docs

Active:

- Unchecked task lists dominate
- `WIP`, `blocked`, `in progress`, `TODO`, `backlog`

Unknown:

- Requirements found but no completion marker
- GitHub metadata only, no readable requirement docs
