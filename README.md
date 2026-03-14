# Understand Anything

An open-source tool that combines LLM intelligence with static analysis to help anyone understand any codebase — from junior developers to product managers.

## Current Status

**Phase 4 complete.** The core analysis engine, web dashboard, and Claude Code skills are all functional. The project includes a multi-agent `/understand` command, fuzzy and semantic search, schema validation, staleness detection, layer auto-detection, guided learning tours, and an interactive chat interface.

## Features

### Phase 1 — Foundation
- **Knowledge Graph** — Automatically maps your codebase into an interactive graph of files, functions, classes, and their relationships
- **Multi-Panel Dashboard** — Graph view, code viewer, chat, and learn panels in a workspace layout
- **Natural Language Search** — Search your codebase with plain English: "which parts handle authentication?"
- **Tree-sitter Analysis** — Accurate structural analysis for TypeScript, JavaScript (more languages coming)
- **LLM-Powered Summaries** — Every node gets a plain-English description of what it does and why

### Phase 2 — Intelligence
- **Fuzzy Search** — Fast, typo-tolerant search across all graph nodes via Fuse.js (SearchEngine in core)
- **Schema Validation** — Zod-based runtime validation when loading knowledge graphs, with detailed error messages
- **Staleness Detection** — Detects changed files via git diff and incrementally merges graph updates
- **Layer Auto-Detection** — Heuristic-based layer grouping (API, Service, Data, UI, Utility) with LLM refinement
- **`/understand-chat` Skill** — Ask questions about your codebase directly in the terminal via Claude Code
- **Dashboard Chat Panel** — Context-aware Q&A integrated into the web dashboard (Claude API)
- **Dagre Auto-Layout** — Automatic hierarchical graph layout for clean visualization
- **Layer Visualization** — Color-coded layer grouping with collapsible groups and a legend panel

### Phase 3 — Learning
- **Guided Tours** — Auto-generated step-by-step walkthroughs of codebase architecture (Kahn's algorithm)
- **Language Lessons** — 12 concept patterns explained in context (generics, closures, decorators, etc.)
- **Persona Selector** — Adaptive UI for junior devs, non-technical stakeholders, and AI-assisted developers
- **Learn Panel** — Interactive tour mode with graph highlighting in the dashboard

### Phase 4 — Skills & Ecosystem
- **`/understand` Command** — Multi-agent pipeline that analyzes a codebase end-to-end and produces `knowledge-graph.json`
- **`/understand-diff` Skill** — Analyze git diffs against the knowledge graph for impact and risk assessment
- **`/understand-explain` Skill** — Deep-dive explanations of any file, function, or module
- **`/understand-onboard` Skill** — Generate team onboarding guides from the knowledge graph
- **Plugin Registry** — Community analyzer plugins with auto-discovery
- **Semantic Search** — Embedding-based vector search with cosine similarity

## Quick Start

### 1. Analyze any codebase (via Claude Code)

```bash
# Install the plugin
claude --plugin-dir /path/to/Understand-Anything/packages/skill

# In any project, run:
/understand
```

This produces `.understand-anything/knowledge-graph.json` in your project.

### 2. View the dashboard

```bash
# Clone this repo and install
git clone https://github.com/Lum1104/Understand-Anything.git
cd Understand-Anything
pnpm install

# Start the dashboard (auto-detects .understand-anything/ from your project)
pnpm dev:dashboard
```

The dashboard dev server automatically looks for `.understand-anything/knowledge-graph.json` in the project root — no manual copying needed.

### 3. Use other skill commands

```bash
# Ask questions about the codebase
/understand-chat How does authentication work in this project?

# Analyze impact of current changes
/understand-diff

# Deep-dive into a specific file
/understand-explain src/auth/login.ts

# Generate an onboarding guide
/understand-onboard
```

## Plugin Installation

The skill commands work in any project via Claude Code:

```bash
# Option 1: Load for current session
claude --plugin-dir /path/to/Understand-Anything/packages/skill

# Option 2: Add to .claude/settings.json for persistent use
# (in the project where you cloned Understand-Anything)
```

```json
{
  "enabledPlugins": {
    "understand-anything": {}
  }
}
```

## Commands

| Command | Description |
|---------|-------------|
| `pnpm install` | Install all dependencies |
| `pnpm --filter @understand-anything/core build` | Build the core package |
| `pnpm --filter @understand-anything/core test` | Run core tests |
| `pnpm --filter @understand-anything/skill build` | Build the skill package |
| `pnpm --filter @understand-anything/skill test` | Run skill tests |
| `pnpm --filter @understand-anything/dashboard build` | Build the dashboard |
| `pnpm dev:dashboard` | Start dashboard dev server |

## Multi-Agent Architecture

The `/understand` command orchestrates 5 specialized agents in a 7-phase pipeline:

| Agent | Model | Role |
|-------|-------|------|
| `project-scanner` | Haiku | Discover files, detect languages and frameworks |
| `file-analyzer` | Sonnet | Extract functions, classes, imports; produce graph nodes/edges |
| `architecture-analyzer` | Sonnet | Identify architectural layers (API, Service, Data, UI, etc.) |
| `tour-builder` | Sonnet | Generate guided learning tours |
| `graph-reviewer` | Haiku | Validate graph completeness and referential integrity |

File analyzers run in parallel (up to 3 concurrent) for speed. Supports incremental updates — only re-analyzes files that changed since the last run.

## Project Structure

```
packages/
  core/        — Analysis engine: types, persistence, tree-sitter, search, schema, staleness, layers, tours
  dashboard/   — React + TypeScript web dashboard with chat, learn, and persona panels
  skill/
    agents/    — Specialized AI agents (scanner, analyzer, architect, tour-builder, reviewer)
    skills/    — Claude Code skills (/understand, /understand-chat, /understand-diff, etc.)
```

## Tech Stack

- TypeScript, pnpm workspaces
- React 18, Vite, TailwindCSS
- React Flow (graph visualization)
- Monaco Editor (code viewer)
- Zustand (state management)
- tree-sitter (static analysis)
- Fuse.js (fuzzy search)
- Zod (schema validation)
- Dagre (graph layout)

## License

MIT
