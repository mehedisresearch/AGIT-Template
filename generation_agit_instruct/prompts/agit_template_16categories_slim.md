# Generic Agent Instruction Template (AGIT)

Repository-agnostic template. Fill facts from the target repository only.

## Project overview / purpose

- State what the project does in 2–4 sentences for an agent that has never seen the repo.
- Name the primary users (contributors, SDK consumers, operators) and the main workflows.
- Point to the canonical docs entry (README, docs site) without inventing product claims.
- Prefer facts that appear in the repository README over marketing language.

## Repository structure

- Summarize the top-level layout: apps/, packages/, src/, docs/, tests/, scripts/, .github/.
- Say where agents should look first for application code vs libraries vs tooling.
- Call out monorepo workspace roots if present (pnpm-workspace, cargo workspace, solutions).
- Keep paths accurate to this repository; do not invent folders.

## Build / run / install

- Document the package manager and install command used by this repo (npm/pnpm/yarn/pip/uv/cargo/dotnet/…).
- Give the exact local build and run commands from README, Makefiles, or package scripts.
- Note toolchain prerequisites (language version, Node/.NET/Python, Docker) only if evidenced.
- Prefer copy-pasteable shell blocks; do not invent solution names or scripts that are not in the tree.

## Test / CI commands

- Document how to run unit, integration, and lint checks locally.
- Reference the CI system and what must be green before merge (GitHub Actions, Azure DevOps, …).
- Include filters or package-scoped test commands when the repo uses them.
- Do not invent coverage thresholds or workflow names that are not in `.github/workflows` or docs.

## Code style / formatting

- Name the formatter/linter stack (eslint, prettier, ruff, black, editorconfig, dotnet format, …).
- State naming and formatting rules that contributors must follow.
- Point to config files (`.eslintrc`, `pyproject.toml`, `.editorconfig`) rather than restating every rule.
- Prefer “run the project formatter” over invented style guides.

## Architecture / design constraints

- Describe major layers/modules and allowed dependency directions.
- State non-negotiable design rules (no cross-layer imports, prefer composition, keep APIs stable).
- Reference architecture docs or ADRs when they exist.
- Avoid generic SOLID boilerplate that is not enforced in this repo.

## Domain models / key abstractions

- Define the core domain types/entities agents will touch.
- Explain how data flows between those abstractions.
- Point to canonical model packages or schema locations.
- Do not invent entities that do not appear in the codebase.

## API / interface contracts

- Document public APIs, CLI entrypoints, or RPC/HTTP contracts agents must respect.
- Note versioning / compatibility expectations for public surfaces.
- Point to OpenAPI, proto, or typed interface directories when present.
- Avoid fabricating endpoints or method signatures.

## Do / Don't rules

### Do
- Follow existing patterns in neighboring code before inventing new ones.
- Run the project’s lint/tests before submitting changes.
- Keep diffs focused; update docs/instruction files when behavior changes.
- Prefer shared utilities over copy-pasted logic.

### Don't
- Do not commit secrets, credentials, or `.env` files.
- Do not bypass CI checks or disable failing tests without discussion.
- Do not introduce a second package manager or build system.
- Do not add large unrelated refactors to bugfix PRs.

## Git / PR / commit conventions

- Follow the repository’s branch naming and PR template.
- Use the commit style this project already uses (conventional commits if configured).
- Keep PRs reviewable; link issues when applicable.
- Do not invent a commit format that conflicts with existing history or bots.

## Tooling-specific agent config

- Describe how this instruction file relates to sibling formats (AGENTS.md, CLAUDE.md, Copilot, Cursor rules).
- Note any agent permissions, MCP tools, or skill files that must be loaded first.
- Prefer repo-local agent config over generic assistant advice.

## Examples / few-shot snippets

- Provide short, real examples of preferred command invocations or API usage from this repo.
- Use fenced code blocks matching the project’s language.
- Examples must be runnable or clearly illustrative — not placeholder `foo/bar` samples.

## Security / secrets

- Never commit API keys, tokens, private keys, or customer data.
- Load secrets from the project’s approved mechanism (env vars, secret manager, CI secrets).
- Do not log credentials; redact sensitive fields in traces.
- Follow security docs or CODEOWNERS for auth-related changes.

## Performance

- Avoid unnecessary work on hot paths; measure before micro-optimizing.
- Respect existing caching, batching, and pagination patterns.
- Do not add unbounded loops over large collections without limits.
- Call out known performance constraints documented in the repo.

## Ownership / contacts

- Point to CODEOWNERS, maintainers list, or team contacts if present.
- Say where to ask questions ( Discussions, Discord, Slack, issues ).
- Do not invent email addresses or owner names.

## Maintenance / when to update

- Update this instruction file when build/test commands, structure, or policies change.
- Remove stale commands after toolchain migrations.
- Keep sibling instruction formats in sync when the same policy applies to all agents.
