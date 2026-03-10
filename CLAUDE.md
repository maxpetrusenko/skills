# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **local skills registry** — 500+ Agent Skills stored centrally and installed into project-local agent directories as needed. Skills are specialized knowledge modules that extend AI capabilities through structured `SKILL.md` files, following the [Agent Skills specification](https://agentskills.io).

**Key concept**: Skills provide expert knowledge ("knowledge delta") that Claude doesn't already possess. A good skill focuses on decision trees, trade-offs, edge cases, and domain-specific frameworks — not basic concepts or tutorials.

**Registry pattern**: Keep skills here, load them per-task via `scripts/load-skills.sh`. This avoids bloating every project with unused skills.

## Architecture

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Core skill definition with YAML frontmatter (keep <500 lines)
├── README.md         # Human-facing documentation
├── references/       # Extended docs loaded on-demand
├── scripts/          # Implementation code (Python/Node.js)
├── lib/              # Shared utilities
├── templates/        # Code templates
├── assets/           # Static files
├── package.json      # Node.js dependencies (if applicable)
└── requirements.txt  # Python dependencies (if applicable)
```

### Skill Types by Content Pattern

| Type | Lines | Focus | Example |
|------|-------|-------|---------|
| **Mindset** | ~50 | Core philosophy, mental models | skill-judge |
| **Navigation** | ~30 | How to explore a codebase | codebase-navigation |
| **Philosophy** | ~150 | Design principles, trade-offs | functional-programming |
| **Process** | ~200 | Step-by-step workflows | git-workflow |
| **Tool** | ~300 | Complete tool reference | playwright-skill |

### Installation Paths

Skills can be installed in multiple locations. When working with skills, resolve `$SKILL_DIR` dynamically:

- Plugin system: `~/.claude/plugins/marketplaces/*/skills/<skill-name>`
- Manual global: `~/.claude/skills/<skill-name>`
- Project-specific: `<project>/.codex/skills/`, `.claude/skills/`, `.cursor/skills/`, `.agents/skills/`

## Loading Skills into Projects

This registry provides `scripts/load-skills.sh` and `scripts/clear-skills.sh` for per-project skill management.

### Regular Workflow (Recommended)

1. Read requirements first (`docs/requirements.md`, `docs/PRESEARCH.md`, PRD).
2. Define domains in manifest with:
   - `@domains: <domain1>, <domain2>, ...`
3. Build project manifests (`skills.must.txt`, `skills.good.txt`, resolved `skills.task.txt`).
4. Maintain `skills.lock.json` with pinned skill sources/revisions.
5. Keep workflow helpers when needed:
   - `deep-research` for pre-search/research-driven work
   - `linear-cli` for Linear-integrated execution
6. Gemini selection:
   - use `gemini` for workflow guidance
   - include `gemini-api-dev` only when implementing Gemini API code
7. Run clear then load sequentially with explicit manifest, lockfile, and project-local codex path.

### Manifest-Based Loading (Recommended)

Create a manifest in your target project:

```bash
# In target project
mkdir -p .agents
cat > .agents/skills.task.txt <<'EOF'
@domains: app, backend, testing
react-best-practices
e2e-testing
systematic-debugging
EOF
```

Then load from registry:

```bash
/Users/maxpetrusenko/Desktop/Projects/skills/scripts/load-skills.sh \
  --project /path/to/target-project \
  --skills-repo /Users/maxpetrusenko/Desktop/Projects/skills \
  --codex-home /path/to/target-project/.codex \
  --manifest /path/to/target-project/.agents/skills.task.txt \
  --lockfile /path/to/target-project/.agents/skills.lock.json \
  --require-lock \
  --strict-manifest \
  --require-domain-coverage \
  --ensure-gitignore
```

### Direct Skill Loading

Load specific skills (ignores manifest; use for ad-hoc local work, not automation/CI):

```bash
scripts/load-skills.sh --project /path/to/project react-best-practices playwright-skill
```

### Agent Targets

Skills install to multiple agent targets:

| Target | Destination |
|--------|-------------|
| `codex` | `<project>/.codex/skills/` (default) |
| `claude` | `<project>/.claude/skills/` |
| `cursor` | `<project>/.cursor/skills/` |
| `agents` | `<project>/.agents/skills/` |

Load to multiple targets:

```bash
scripts/load-skills.sh \
  --project /path/to/app \
  --targets codex,claude,cursor \
  --codex-home /path/to/app/.codex \
  --manifest /path/to/app/.agents/skills.task.txt \
  --lockfile /path/to/app/.agents/skills.lock.json \
  --require-lock \
  --strict-manifest \
  --require-domain-coverage \
  --ensure-gitignore
```

### Clearing Skills

```bash
# Clear from manifest
scripts/clear-skills.sh --project /path/to/project

# Clear specific skills
scripts/clear-skills.sh --project /path/to/project react-best-practices

# Remove all from target
scripts/clear-skills.sh --project /path/to/project --targets codex --all --yes
```

## External Skill Sources

Additional skill repositories referenced in `.agents/AGENTS.md`:

| Repository | Focus |
|------------|-------|
| [anthropics/skills](https://github.com/anthropics/skills) | Official Anthropic skills |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | Vercel-maintained skills |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React/Web UI skills |
| [vercel-labs/next-skills](https://github.com/vercel-labs/next-skills) | Next.js-specific skills |
| [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills) | LangChain integration |
| [numman-ali/openskills](https://github.com/numman-ali/openskills) | Cross-tool skill installer |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Curated list |
| [skills.sh](https://skills.sh) | Skill package manager/registry |

Use these for:
- **Canonical examples**: anthropics/skills
- **React/Web UI work**: vercel-labs/agent-skills, next-skills
- **Cross-tool reuse**: OpenSkills for shared AGENTS.md setups
- **Discovery**: awesome-claude-skills for curated catalog

## Working with Skills

### Creating a New Skill

1. Create directory: `mkdir skills/<skill-name>`
2. Add `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: One-line summary of what this skill provides
   risk: low | medium | high | unknown
   source: official | community
   ---
   ```
3. Focus content on **expert-only knowledge** — what Claude genuinely doesn't know
4. Keep SKILL.md under 500 lines; move extended content to `references/`

### Skill Evaluation Criteria

Use **skill-judge** to evaluate skill quality across dimensions:
- **Knowledge Delta** (most important): Does it provide expert knowledge not in training data?
- **Structure**: Proper YAML frontmatter, clear sections
- **Completeness**: Covers key concepts without redundancy
- **Actionability**: Provides specific guidance, not just theory

Run evaluation: `/skill-judge evaluate <skill-path>`

### Common Skill Commands

Each skill defines its own commands via `SKILL.md`. Examples:

- `/nblm ask <question>` — Query Google NotebookLM (nblm skill)
- `/playwright <url>` — Browser automation (playwright-skill)
- `/skill-judge evaluate` — Evaluate skill quality

## Development Patterns

### Node.js Skills (e.g., playwright-skill)

```bash
cd $SKILL_DIR
npm install          # Install dependencies
npm run setup        # One-time setup (browsers, etc.)
node run.js <script> # Execute script
```

### Python Skills (e.g., nblm)

```bash
cd $SKILL_DIR
python scripts/run.py <module> <command>  # Auto-creates .venv
# Or manually:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Important: Use Wrapper Scripts

Many Python skills (like nblm) provide a `run.py` wrapper that:
- Automatically creates `.venv` if missing
- Installs Python and Node.js dependencies
- Handles environment setup

**Always use the wrapper** — running scripts directly may fail without the virtual environment.

## Key Skills Reference

| Skill | Purpose | Key Feature |
|-------|---------|-------------|
| **skill-judge** | Evaluate skill quality | Knowledge delta scoring |
| **playwright-skill** | Browser automation | Auto-detects dev servers |
| **nblm** | Google NotebookLM integration | Source-grounded answers |
| **plugin-forge** | Build Claude Code plugins | Plugin development toolkit |
| **react-email** | HTML email with React | Email development |

## What Claude Already Knows (Skip These Skills)

**Don't load skills for topics Claude has in training data**. These provide minimal knowledge delta:

| Category | Already Know Well |
|----------|-------------------|
| **Languages** | JavaScript/TypeScript, Python, Go, Rust, Java, C#, PHP, Swift fundamentals |
| **Web Basics** | HTML, CSS, DOM, fetch, HTTP, cookies, storage |
| **Frameworks** | React, Vue, Angular, Next.js basics (hooks, components, props) |
| **Backend** | Express, FastAPI, Django basics (routing, middleware) |
| **Databases** | SQL fundamentals, basic ORMs, CRUD patterns |
| **DevOps** | Git (clone, commit, branch, merge, rebase), Docker basics |
| **Testing** | Jest, pytest, testing concepts (unit/integration/E2E) |
| **Tools** | npm, yarn, pnpm, pip, curl, grep, find, sed |
| **Concepts** | REST, GraphQL, JSON, async/await, promises, OOP, FP basics |
| **Security** | OWASP top 10, XSS, SQL injection, auth basics (JWT, sessions) |

**Load skills for**: Domain-specific workflows, non-obvious trade-offs, edge cases from experience, tool-specific advanced patterns, private/internal APIs.

## Design Philosophy

**The Core Formula**: `Good Skill = Expert-only Knowledge − What Claude Already Knows`

Skills are **not tutorials**. They're knowledge externalization mechanisms that extend Claude's capabilities without retraining. Edit a Markdown file, save, and behavior changes instantly.

### Three Types of Knowledge in Skills

| Type | Definition | Treatment |
|------|------------|-----------|
| **Expert** | Claude genuinely doesn't know | Must keep — core value |
| **Activation** | Claude knows but may not think of | Keep if brief — reminder |
| **Redundant** | Claude definitely knows | Delete — token waste |

## Notes

- This is a **local registry**, not a monorepo — each skill is independent
- No central build/test system — skills manage their own dependencies
- The `data/` directory within skills typically contains sensitive auth data — never commit
- Skills support progressive disclosure: metadata first, core content, then references
- After loading skills, restart agent tools to pick up changes
- Use `--symlink` flag with load-skills.sh for development (faster updates)
