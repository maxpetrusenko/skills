# Spawning Judges

## Capability Contract

Council requires these runtime capabilities. Map them to whatever your agent harness provides.

**For concrete tool call examples per backend, read the matching shared reference:**
- Claude Native Teams → `skills/shared/references/backend-claude-teams.md`
- Codex Sub-Agents / CLI → `skills/shared/references/backend-codex-subagents.md`
- Background Tasks → `skills/shared/references/backend-background-tasks.md`
- Inline → `skills/shared/references/backend-inline.md`

| Capability | Required for | What it does |
|------------|-------------|-------------|
| **Spawn parallel subagent** | All modes except `--quick` | Create N judges that run concurrently, each with a prompt |
| **Agent-to-agent messaging** | `--debate` only | Send a message to a running judge (for R2 verdict exchange) |
| **Graceful shutdown** | Cleanup | Terminate judges after consolidation |
| **Shared filesystem** | All modes | Judges write output files to `.agents/council/` |

If **spawn** is unavailable, degrade to `--quick` (inline single-agent).
If **messaging** is unavailable, `--debate` degrades to single-round review.

## Spawning Flow

### Phase 1: Spawn Judges in Parallel

For each judge (N = 2 default, 3 with `--deep`):

1. Spawn a subagent with the judge prompt (see `agent-prompts.md`)
2. Each judge receives the full context packet as its prompt
3. Track the mapping: `judge-{N}` → agent handle (for messaging and cleanup)

All judges spawn in parallel. Do not wait for one before spawning the next.

### Phase 2: Wait for Completion

Judges write output files, then send a MINIMAL completion signal:

```json
{
  "type": "verdict",
  "verdict": "PASS | WARN | FAIL",
  "confidence": "HIGH | MEDIUM | LOW",
  "file": ".agents/council/YYYY-MM-DD-<target>-judge-1.md"
}
```

Wait for all judges to signal (up to `COUNCIL_TIMEOUT`, default 120s). If a judge times out, proceed with N-1 and note in report.

### Phase 3: Debate R2 (if `--debate`)

After R1 completes, send each judge a message containing:
- Verdict summaries of OTHER judges (verdict + confidence + file path only)
- Instructions to read other judges' files for full reasoning
- The debate protocol (see `agent-prompts.md`)

CONTEXT BUDGET: Send only verdict summaries, NOT full JSON findings. Judges read files for detail.

Wait up to `COUNCIL_R2_TIMEOUT` (default 90s). If a judge doesn't respond, use their R1 verdict.

### Phase 4: Consolidation

Lead reads each judge's output file (one at a time), extracts JSON verdict, synthesizes final report. No separate agent — consolidation runs inline.

### Phase 5: Cleanup

Shut down all judges via runtime's shutdown mechanism. Cleanup MUST succeed even on partial failures:

1. Request graceful shutdown for each judge
2. Wait up to 30s for acknowledgment
3. If any judge doesn't respond, log warning, proceed anyway
4. Always run cleanup — lingering agents pollute future sessions

## Codex CLI Judges (--mixed mode)

For cross-vendor consensus, run Codex CLI processes alongside runtime-native judges:

```bash
# With structured output (preferred)
codex exec -s read-only -C "$(pwd)" --output-schema skills/council/schemas/verdict.json -o .agents/council/codex-{N}.json "{PACKET}"

# Fallback (if --output-schema unsupported)
codex exec --full-auto -C "$(pwd)" -o .agents/council/codex-{N}.md "{PACKET}"
```

Uses the user's default Codex model. Only pass `-m` if `COUNCIL_CODEX_MODEL` is explicitly set.

Flag order: `-s`/`--full-auto` → `-C` → `--output-schema` → `-o` → prompt (add `-m` before `-C` only if overriding model).

**Valid flags:** `--full-auto`, `-s`, `-m`, `-C`, `--output-schema`, `-o`, `--add-dir`
**Invalid flags:** `-q` (doesn't exist), `--quiet` (doesn't exist)

Codex CLI processes run as background shell commands — this is fine (they're separate OS processes, not agent background tasks).

## Timeout Configuration

| Timeout | Default | Description |
|---------|---------|-------------|
| Judge timeout | 120s | Max time for judge to complete (per round) |
| Shutdown grace period | 30s | Time to wait for shutdown acknowledgment |
| R2 debate timeout | 90s | Max time for R2 after sending debate messages |

## Model Selection

| Vendor | Default | Override |
|--------|---------|----------|
| Claude | sonnet | `--claude-model=opus` |
| Codex | (user's default) | `--codex-model=<model>` or `COUNCIL_CODEX_MODEL` env var |

## Output Collection

All council outputs go to `.agents/council/`:

```bash
mkdir -p .agents/council

# Judge output (R1)
.agents/council/YYYY-MM-DD-<target>-judge-1.md
.agents/council/YYYY-MM-DD-<target>-judge-error-paths.md

# Judge output (R2, when --debate)
.agents/council/YYYY-MM-DD-<target>-judge-1-r2.md

# Codex CLI output (--mixed)
.agents/council/YYYY-MM-DD-<target>-codex-1.json   # with --output-schema
.agents/council/YYYY-MM-DD-<target>-codex-1.md      # fallback

# Final consolidated report
.agents/council/YYYY-MM-DD-<target>-report.md
```

## Judge Naming

Convention: `council-YYYYMMDD-<target>` for the team/session name.

Judge names: `judge-{N}` for independent judges, `judge-{perspective}` when using presets (e.g., `judge-error-paths`, `judge-feasibility`).
