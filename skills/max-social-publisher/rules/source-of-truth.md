# Source Of Truth

## Canonical References

Use these as the publish reference, in this order:

1. Official Late repo: `https://github.com/getlate-dev/late-api`
2. Official docs: `https://docs.getlate.dev`
3. Official LLM docs dump: `https://docs.getlate.dev/llms-full.txt`

This skill should be checked against upstream before changing publishing behavior.

## Current Verified Upstream

- repo: `getlate-dev/late-api`
- verified commit: `6ce8796cf0b7daca755b144e60c7acebe90afa2a`
- commit date: `2026-01-23`

## Update Rule

Before editing this skill's Late behavior:

1. inspect upstream `SKILL.md`
2. inspect relevant upstream rules
3. inspect `docs.getlate.dev/llms-full.txt` for current request fields
4. update this skill only if upstream behavior changed

## Why

Late is the publishing backend. Drift here means bad publishes, wrong payloads, or broken scheduling.
