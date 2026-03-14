# Understand Anything

## Project Overview
An open-source tool combining LLM intelligence + static analysis to produce interactive dashboards for understanding codebases.

## Architecture
- **Monorepo** with pnpm workspaces
- **packages/core** — Shared analysis engine (types, persistence, tree-sitter plugin, LLM prompt templates)
- **packages/dashboard** — React + TypeScript web dashboard (React Flow, Monaco Editor, Zustand, TailwindCSS)
- **packages/skill** — Claude Code skill (not yet implemented)

## Key Commands
- `pnpm install` — Install all dependencies
- `pnpm --filter @understand-anything/core build` — Build the core package
- `pnpm --filter @understand-anything/core test` — Run core tests
- `pnpm dev:dashboard` — Start dashboard dev server

## Conventions
- TypeScript strict mode everywhere
- Vitest for testing
- ESM modules (`"type": "module"`)
- Knowledge graph JSON lives in `.understand-anything/` directory of analyzed projects
