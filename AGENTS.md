# AGENTS.md

This file provides guidance to AI coding agents when working in this repository.
It is aligned with `CLAUDE.md`, with stricter execution guidance for cross-agent consistency.


# Goal

Store skills locally ( most used)
Download skills from sources belo to agent's project folder ( per task or per PRD or requiremtns). Load enough skills to solve the problem  

## Details

How to actually use this for your agents
If you want a concrete starting plan for coding + general agentic work:

For Claude‑centric or multi‑agent setups

Install anthropics/skills first; use it as canonical examples and as a high‑quality catalog you can actually reuse or fork.

If you’re using LangChain Deep Agents, wire in LangChain Skills directories for research/observer subagents and keep Claude/Anthropic skills as external packages.

For editor‑ and IDE‑driven coding agents (Claude Code, Cursor, Copilot, Codex, Windsurf, etc.)

Use skills.sh + vercel-labs/skills as your package manager and registry.

Install vercel-labs/agent-skills (React/Web UI) and vercel-labs/next-skills (Next.js) into your coding agent for immediate gains on perf, accessibility, and architecture.

For product‑specific workflows and internal tools

If your product docs are on Mintlify, customize the auto‑generated skill.md and keep it in your repo so all agents know how to use your API/UI correctly.
​

For cross‑tool reuse (Claude Code + Cursor + others), consider OpenSkills to install anthropics/skills and other packages into a shared AGENTS.md‑based setup.
​

## allowlisted source
https://github.com/affaan-m/everything-claude-code (ECC - 67 skills, 40 commands, 29 agents)
https://github.com/numman-ali/openskills
https://github.com/travisvn/awesome-claude-skills
https://github.com/anthropics/skills
https://github.com/vercel-labs/agent-skills
https://github.com/vercel-labs/skills
https://github.com/vercel-labs/next-skills
www.Skills.sh
https://github.com/langchain-ai/langchain-skills
??
https://github.com/OpenLinkSoftware/ai-agent-skills




## Repository Purpose

This repository is a catalog of **500 local agent skills**.  
Each skill is an independent module rooted at `<skill-name>/SKILL.md`, usually with optional `references/`, `scripts/`, `assets/`, and templates.

Core concept: a good skill should add **knowledge delta** (expert trade-offs, edge cases, decision criteria), not generic tutorials.

## Quick Facts

- Skill count: `500` (`find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l`)
- Root model docs: `CLAUDE.md`, `AGENTS.md`
- Each skill is self-contained; there is no monorepo-wide build/test contract

## Standard Skill Layout

```text
skill-name/
├── SKILL.md          # Required, primary instructions
├── README.md         # Optional, human-facing docs
├── references/       # Optional, load on demand
├── scripts/          # Optional, executable helpers
├── templates/        # Optional, reusable templates
├── assets/           # Optional, static assets
├── lib/              # Optional, shared helpers
├── package.json      # Optional, Node.js deps
└── requirements.txt  # Optional, Python deps
```

## Agent Operating Protocol

1. Discover first:
   - Read target skill `SKILL.md` before touching `references/`.
   - Load only the minimum files needed for the current task.
2. Prefer existing tooling:
   - If `scripts/` exists, run or patch scripts instead of re-implementing logic in chat.
   - If templates/assets exist, reuse them.
3. Keep changes local and minimal:
   - Do not refactor unrelated skills.
   - Do not introduce cross-skill coupling unless explicitly asked.
4. Verify behavior:
   - Run the smallest meaningful validation (script invocation, lint, smoke test).
   - Report what was verified and what was not.
5. Protect sensitive data:
   - Never commit secrets or auth artifacts (commonly under `data/`, `.env`, or local caches).
6. Keep agent runtime folders out of git:
   - Ensure target project `.gitignore` includes:
     - `.claude/`
     - `.codex/`
     - `.agents/`

## Skill Selection Rules

Use a skill when the task matches a skill domain or the user names a skill explicitly.

Prioritize skills that provide:
- domain-specific workflows,
- non-obvious implementation trade-offs,
- advanced tool behavior and failure modes.

Avoid loading skills for baseline knowledge already in model memory (language basics, framework fundamentals, simple CRUD).

## Quality Bar for New or Updated Skills

A skill is high quality when it has:
- Clear scope and one-sentence purpose in `SKILL.md`
- Explicit decision rules ("if/then" guidance)
- Practical edge cases and failure handling
- Concrete commands/examples that are directly executable
- Progressive disclosure (short core + targeted references)
- Low redundancy with common baseline knowledge

## Practical Commands

### Required Protocol (Project-Local Loading)

Follow this protocol for every target project:

1. Detect stack first from project files (`pyproject.toml`, `requirements.txt`, `package.json`, `go.mod`, etc.).
2. Ensure `.gitignore` in the target project excludes `.claude/`, `.codex/`, and `.agents/`.
3. If those entries are missing, add them before loading skills.
4. Update only `<project>/.agents/skills.task.txt` with stack-matching skills.
5. Use `clear-skills.sh` before reloading if previously installed skills are wrong.
6. Run clear then load sequentially (never in parallel) to avoid race conditions.
7. Load from `--manifest <project>/.agents/skills.task.txt` only.
8. Do not pass positional skill args when using manifests.
9. Size the selection to requirements coverage: include all skills needed to satisfy project requirements, no fixed cap.
10. If stack-skill mismatch is found, stop and rewrite the manifest first.
11. For `codex` target, force project-local path via `--codex-home <project>/.codex` to avoid accidental global installs in `~/.codex/skills`.
12. In automation/CI, enable strict mode flags: `--strict-manifest --require-domain-coverage --ensure-gitignore`.
13. In automation/CI, require lockfile enforcement: `--require-lock --lockfile <project>/.agents/skills.lock.json`.

### Regular Selection Steps (Use For Any Project)

1. Read project requirements docs first (for example: `docs/requirements.md`, `docs/PRESEARCH.md`).
2. Write declared domains at top of task manifest:
   - `@domains: <domain1>, <domain2>, ...`
3. Build `skills.must.txt` and `skills.good.txt`, then resolve `skills.task.txt`.
4. Keep planning/research helpers when project workflow needs them:
   - `deep-research` for pre-search/research tasks
   - `linear-cli` when task tracking in Linear is part of workflow
5. Gemini rule:
   - Use `gemini` for workflow-level guidance
   - Add `gemini-api-dev` only when implementing Gemini API endpoints in code
6. Clear old installs, then load sequentially using explicit `--manifest`, `--lockfile`, and project-local `--codex-home`.
7. If declared domains are uncovered, either add matching skills or record explicit gaps and proceed with official docs.

### Requirements-Driven Skill Tiers

Use two tiers derived from project requirements:

- `must-have`: skills required to ship core scope (MVP blockers).
- `good-to-have`: skills that improve quality, speed, or operations, but are not blockers.

Manifest files in target project:

- `<project>/.agents/skills.must.txt`
- `<project>/.agents/skills.good.txt`
- `<project>/.agents/skills.task.txt` (resolved final set to load)
- `<project>/.agents/skills.lock.json` (pinned supply chain source of truth)

Resolution rules:

1. Start from requirements and map each requirement to at least one skill.
2. Put blockers in `skills.must.txt`; optional improvements in `skills.good.txt`.
3. Build `skills.task.txt` as:
   - all `must-have` skills
   - plus `good-to-have` skills only when they support current phase/time budget
4. Keep one line per skill, comments allowed with `#`.
5. Load only from explicit `--manifest <project>/.agents/skills.task.txt`.
6. In CI, require all task skills to be present in `skills.lock.json`.

Lockfile minimum schema:

```json
{
  "skills": [
    { "name": "rag-implementation", "source": "local", "rev": "", "allowScripts": false },
    { "name": "example-external-skill", "source": "github", "rev": "0123456789abcdef0123456789abcdef01234567", "allowScripts": false }
  ]
}
```

Rules:
- `skills[].name` is required.
- For non-local `source`, `rev` must be a full 40-char commit SHA.
- `skills.task.txt` entries must be pinned in `skills.lock.json` when `--require-lock` is used.

### External Skill Intake (Security Gate)

When skills are downloaded from the internet, apply this gate before loading:

1. Source trust:
   - Prefer allowlisted sources (official or approved org repos).
   - Pin repo to commit SHA or release tag (no floating `main`).
2. Static review:
   - Read `SKILL.md` fully.
   - Inspect `scripts/`, `package.json`, `requirements.txt`, and install hooks.
   - Reject skills with unclear network/execution behavior.
3. Execution safety:
   - Do not run external scripts automatically.
   - First load docs-only usage; enable scripts only after explicit review.
4. Data safety:
   - No secret handling inside skill artifacts.
   - Never commit external skill caches or runtime folders.
5. Approval:
   - Record accepted source URL + pinned revision in project notes.

### External Skills via Skills.sh

Use Skills.sh for discovery and testing only, not as the primary project loader.

Workflow:

1. Search:
   - `npx skills search <query>`
2. Test in sandbox:
   - `npx skills add <skill> --sandbox`
3. Review before adoption:
   - Read `SKILL.md`
   - Inspect `scripts/`, `package.json`, `requirements.txt`
4. Vendor into local registry:
   - Copy approved skill into `/Users/maxpetrusenko/Desktop/Projects/skills/`
   - Pin source to commit SHA or release tag in project notes
5. Load into projects only with local scripts:
   - `scripts/load-skills.sh` with explicit `--manifest`, `--strict-manifest`, and project-local `--codex-home`

Rule:
- Do not load Skills.sh packages directly into project agent folders for production work.

### Gap Closure Workflow (When Registry Lacks Needed Skills)

If requirements reference technologies without matching local skills:

1. Mark each gap explicitly in project notes (e.g., `firebase`, `konva`, `llamaindex`, `qdrant`).
2. For immediate delivery, proceed with trusted official docs plus nearest local skills.
3. For repeatability, create a focused local skill in this registry for each high-impact gap.
4. Keep gap skills narrow and practical (commands, failure modes, decision rules).
5. Add new gap skills to future manifests only after review.

Important behavior:
- If `--manifest` is omitted, `load-skills.sh` may merge both:
  - `<project>/.agents/skills.core.txt`
  - `<project>/.agents/skills.task.txt`
- To avoid unexpected skills, always pass `--manifest` explicitly.
- If `--codex-home` is omitted, codex path defaults to `<project>/.codex`; still pass it explicitly in automation for safety.

Replace wrong skills, then reload from a single manifest:

```bash
# Ensure agent runtime folders are not committed
cat >> /absolute/path/to/target-project/.gitignore <<'EOF'
.claude/
.codex/
.agents/
EOF

/Users/maxpetrusenko/Desktop/Projects/skills/scripts/clear-skills.sh \
  --project /absolute/path/to/target-project \
  --codex-home /absolute/path/to/target-project/.codex \
  --targets codex,agents --all --yes

# Run after clear completes (sequential execution)
/Users/maxpetrusenko/Desktop/Projects/skills/scripts/load-skills.sh \
  --project /absolute/path/to/target-project \
  --skills-repo /Users/maxpetrusenko/Desktop/Projects/skills \
  --codex-home /absolute/path/to/target-project/.codex \
  --targets codex,agents \
  --manifest /absolute/path/to/target-project/.agents/skills.task.txt \
  --lockfile /absolute/path/to/target-project/.agents/skills.lock.json \
  --require-lock \
  --strict-manifest \
  --require-domain-coverage \
  --ensure-gitignore \
  --force
```

Create tiered manifests and resolve final task manifest:

```bash
cat > /absolute/path/to/target-project/.agents/skills.must.txt <<'EOF'
# Core blockers only
rag-implementation
fastapi-python
python-testing-patterns
EOF

cat > /absolute/path/to/target-project/.agents/skills.good.txt <<'EOF'
# Optional quality/ops improvements
python-observability
logging-best-practices
error-handling-patterns
EOF

cat /absolute/path/to/target-project/.agents/skills.must.txt \
    /absolute/path/to/target-project/.agents/skills.good.txt \
  | awk 'NF && $1 !~ /^#/' \
  | awk '!seen[$0]++' \
  > /absolute/path/to/target-project/.agents/skills.task.txt
```

Load skills into another project:

```bash
/Users/maxpetrusenko/Desktop/Projects/skills/scripts/load-skills.sh \
  --project /absolute/path/to/target-project \
  --skills-repo /Users/maxpetrusenko/Desktop/Projects/skills \
  --manifest /absolute/path/to/target-project/.agents/skills.task.txt
```

Load to multiple agent targets in that project:

```bash
/Users/maxpetrusenko/Desktop/Projects/skills/scripts/load-skills.sh \
  --project /absolute/path/to/target-project \
  --skills-repo /Users/maxpetrusenko/Desktop/Projects/skills \
  --targets codex,claude,cursor,agents \
  --manifest /absolute/path/to/target-project/.agents/skills.task.txt
```

Notes:
- Default target is `codex` -> `<project>/.codex/skills`.
- Explicit `--manifest` is required for deterministic loading.
- Restart the agent session in the target project after loading.

Discover skills:

```bash
find . -mindepth 2 -maxdepth 2 -name SKILL.md | sort
```

Count skills:

```bash
find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
```

Inspect one skill quickly:

```bash
sed -n '1,220p' <skill-name>/SKILL.md
find <skill-name> -maxdepth 2 -type f | sort
```

## Notes

- Treat this repo as a **skill registry**, not a single application.
- Prefer additive edits over destructive rewrites.
- Keep `SKILL.md` concise; move depth into `references/` when needed.
