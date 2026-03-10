# Workflow

## Phase 1: Gather Evidence

Before drafting, inspect:

1. repo `README.md`
2. key docs or demo script
3. live URL
4. demo/video URL
5. package manifests or architecture docs
6. prior Max post examples

If a claim is not grounded in repo, docs, or demo evidence, do not use it.

## Phase 2: Draft

Default output:

- 5 main drafts
- 1 shorter version
- 1 more technical version

For each draft include:

- angle label
- post text
- recommended URL
- one-line why-it-works note

## Phase 3: Ask Before Publish

Before publishing, ask the user to confirm:

- selected draft
- target platforms
- publish now vs schedule
- scheduled time if applicable
- whether to attach existing media or use generated image fallback

No publish without explicit approval.

## Phase 4: Publish Or Schedule

Use `scripts/max_social_publish.py`.

Typical flow:

1. list profiles or accounts if needed
2. resolve profile or account IDs
3. upload local media if needed
4. create the post
5. return the Late response JSON and summarize outcome

## Secrets Rule

- load secrets from env or Doppler
- never print API keys
- never write keys into generated files or command output

## Interactive Mode

Preferred one-command flow:

```bash
python3 scripts/max_social_publish.py \
  --interactive \
  --repo-url https://github.com/owner/repo \
  --live-url https://example.com \
  --demo-url https://loom.com/share/abc
```

Interactive mode should:

1. gather context
2. draft candidate posts
3. ask the user to select one
4. ask for target platforms and publish timing if missing
5. ask for media if missing
6. ask for final approval
7. publish or schedule

Real example:

```bash
GETLATE_DEV_API_KEY_FREE=... \
python3 scripts/max_social_publish.py \
  --content 'Most AI post generators flatten the interesting part...' \
  --platforms x \
  --account x=690248619d65616f16a5c5bc \
  --media-file assets/max-social-publisher-screenshot.png \
  --publish-now
```

## Defaults

- Prefer real demo, live product, or repo URLs over generated media.
- Use generated image fallback only when there is no strong attached media or when the user explicitly wants one.
- Prefer Late API for all supported platforms.
