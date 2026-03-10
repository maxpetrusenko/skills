# Agent Skills

[![Skills](https://img.shields.io/badge/skills-1300%2B-blue)](https://github.com/maxpetrusenko/skills)
[![Targets](https://img.shields.io/badge/targets-codex%20%7C%20claude%20%7C%20cursor%20%7C%20agents-black)](./AGENTS.md)

Curated local skill registry for Codex, Claude Code, Cursor, and other coding agents.

This repo packages 1,300+ reusable skills with project-local install scripts, manifest support, and a safer workflow for loading only the skills a project actually needs.

Add this to the target project's main `AGENTS.md` or `CLAUDE.md`:

```md
Skills: once requirements are clear, load related skills from `/Users/maxpetrusenko/Desktop/Projects/skills/AGENTS.md`.
If requirements are not clear yet, ask the user which skill or domain is needed first.
```

## Why This Repo

- Large local catalog of practical agent skills
- Project-local installs instead of global tool drift
- Manifest-based loading for repeatable setups
- Works across `codex`, `claude`, `cursor`, and `.agents`
- Built for real coding workflows, not generic prompt dumps

## Installation

Clone the registry:

```bash
git clone https://github.com/maxpetrusenko/skills.git
cd skills
```

## Quick Start

Install a few skills into a target project:

```bash
mkdir -p /absolute/path/to/target-project/.agents

cat > /absolute/path/to/target-project/.agents/skills.task.txt <<'EOF'
# Example task manifest
react-dev
responsive-design
e2e-testing
systematic-debugging
EOF

./scripts/load-skills.sh \
  --project /absolute/path/to/target-project \
  --skills-repo "$(pwd)" \
  --codex-home /absolute/path/to/target-project/.codex \
  --targets codex,agents \
  --manifest /absolute/path/to/target-project/.agents/skills.task.txt \
  --force
```

After loading, restart the agent session in the target project so it picks up the installed skills.

## How To Use It

### 1. Create a task manifest

Put the exact skills needed for the current project in:

- `.agents/skills.must.txt`
- `.agents/skills.good.txt`
- `.agents/skills.task.txt`

Minimal example:

```txt
@domains: frontend, testing, debugging
react-dev
responsive-design
e2e-testing
systematic-debugging
verification-before-completion
```

### 2. Load skills into the target project

```bash
./scripts/load-skills.sh \
  --project /absolute/path/to/target-project \
  --skills-repo "$(pwd)" \
  --codex-home /absolute/path/to/target-project/.codex \
  --targets codex,claude,cursor,agents \
  --manifest /absolute/path/to/target-project/.agents/skills.task.txt \
  --lockfile /absolute/path/to/target-project/.agents/skills.lock.json \
  --strict-manifest \
  --require-lock \
  --require-domain-coverage \
  --ensure-gitignore \
  --force
```

### 3. Clear old installs when the manifest changes

```bash
./scripts/clear-skills.sh \
  --project /absolute/path/to/target-project \
  --codex-home /absolute/path/to/target-project/.codex \
  --targets codex,claude,cursor,agents \
  --all \
  --yes
```

## What's Included

- API and backend skills
- Frontend, design, and accessibility skills
- Testing, debugging, and verification skills
- Security, deployment, and CI/CD skills
- Product, planning, and documentation workflows
- Many vendor and integration-specific skills

Every skill lives under `skills/` and is usually rooted at:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── README.md
    ├── references/
    ├── scripts/
    ├── templates/
    └── assets/
```

## Supported Targets

- `codex` -> `<project>/.codex/skills`
- `claude` -> `<project>/.claude/skills`
- `cursor` -> `<project>/.cursor/skills`
- `agents` -> `<project>/.agents/skills`

## Repo Structure

```text
repo-root/
├── skills/<skill-name>/SKILL.md
├── scripts/load-skills.sh
├── scripts/clear-skills.sh
├── AGENTS.md
└── CLAUDE.md
```

## Supply Chain Notes

- Prefer allowlisted sources before vendoring external skills
- Review `SKILL.md`, `scripts/`, and dependency files before loading outside code
- Pin external sources to a commit SHA in the target project lockfile
- Use project-local installs to avoid leaking skills across unrelated repos

## Resources

- Main operating guide: [AGENTS.md](./AGENTS.md)
- Model/runtime notes: [CLAUDE.md](./CLAUDE.md)
- Loader script: [`scripts/load-skills.sh`](./scripts/load-skills.sh)
- Clear script: [`scripts/clear-skills.sh`](./scripts/clear-skills.sh)

## License

No OSS license has been added yet.
