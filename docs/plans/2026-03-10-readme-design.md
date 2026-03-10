# Public README Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a visitor-facing root README that explains what this repo is, how to install skills from it, and how to use the project-local loader workflow.

**Architecture:** Keep the README hybrid. Top section should read like a public package README for GitHub visitors. Middle section should use real commands from `scripts/load-skills.sh` and `scripts/clear-skills.sh`. Bottom section should explain manifests, targets, and the repo structure without turning into internal-only docs.

**Tech Stack:** Markdown, shell scripts, GitHub repository docs

---

### Task 1: Add the design note

**Files:**
- Create: `docs/plans/2026-03-10-readme-design.md`

**Step 1: Write the design note**

Document the README goal, section order, and what visitor actions it must support.

**Step 2: Verify the note exists**

Run: `test -f docs/plans/2026-03-10-readme-design.md && echo ok`
Expected: `ok`

### Task 2: Add the root README

**Files:**
- Create: `README.md`
- Reference: `scripts/load-skills.sh`
- Reference: `scripts/clear-skills.sh`
- Reference: `AGENTS.md`

**Step 1: Write the README**

Include:
- title and one-line pitch
- why this repo exists
- installation via `git clone`
- quick start with `scripts/load-skills.sh`
- example manifest flow
- supported targets
- repo structure
- safety note for external skills
- resources and license status

**Step 2: Keep examples executable**

Only include commands supported by the current shell scripts.

### Task 3: Verify content

**Files:**
- Modify: `README.md`

**Step 1: Read back the README**

Run: `sed -n '1,260p' README.md`
Expected: sections render cleanly and commands are readable.

**Step 2: Verify the documented commands**

Run: `bash scripts/load-skills.sh --help`
Expected: help output includes documented flags like `--project`, `--manifest`, `--targets`, and `--codex-home`.

Run: `bash scripts/clear-skills.sh --help`
Expected: help output includes documented flags like `--project`, `--targets`, and `--all`.

### Task 4: Publish for review

**Files:**
- Modify: `README.md`

**Step 1: Commit**

```bash
git add README.md docs/plans/2026-03-10-readme-design.md
git commit -m "docs: add public repo README"
```

**Step 2: Push**

```bash
git push origin main
```
