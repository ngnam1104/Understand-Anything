# Understand Anything

An open-source tool that combines LLM intelligence with static analysis to help anyone understand any codebase — from junior developers to product managers.

## Features

- **Knowledge Graph** — Automatically maps your codebase into an interactive graph of files, functions, classes, and their relationships
- **Multi-Panel Dashboard** — Graph view, code viewer, chat, and learn panels in a workspace layout
- **Natural Language Search** — Search your codebase with plain English: "which parts handle authentication?"
- **Tree-sitter Analysis** — Accurate structural analysis for TypeScript, JavaScript (more languages coming)
- **LLM-Powered Summaries** — Every node gets a plain-English description of what it does and why

## Quick Start

```bash
# Install dependencies
pnpm install

# Build the core package
pnpm --filter @understand-anything/core build

# Start the dashboard dev server
pnpm dev:dashboard
```

## Project Structure

```
packages/
  core/        — Analysis engine: types, persistence, tree-sitter, LLM prompts
  dashboard/   — React + TypeScript web dashboard
  skill/       — Claude Code skill (coming soon)
```

## Tech Stack

- TypeScript, pnpm workspaces
- React 18, Vite, TailwindCSS
- React Flow (graph visualization)
- Monaco Editor (code viewer)
- Zustand (state management)
- tree-sitter (static analysis)

## License

MIT
