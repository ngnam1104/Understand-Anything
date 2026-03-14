---
name: understand
description: Analyze a codebase to produce an interactive knowledge graph for understanding architecture, components, and relationships
argument-hint: [options]
---

# /understand

Analyze the current codebase and produce a `knowledge-graph.json` file in `.understand-anything/`.

## Options

- `$ARGUMENTS` may contain:
  - `--full` — Force a full rebuild, ignoring any existing graph
  - A directory path — Scope analysis to a specific subdirectory

## Phase 0 — Pre-flight

1. Determine the project root (current working directory).
2. Get the current git commit hash:
   ```bash
   git rev-parse HEAD
   ```
3. Check if `.understand-anything/knowledge-graph.json` already exists. If it does, read it.
4. Check if `.understand-anything/meta.json` exists. If it does, read it to get `gitCommitHash`.
5. **Decide the analysis path:**
   - If `--full` is in `$ARGUMENTS`, or no existing graph → **Full analysis** (all phases)
   - If existing graph exists → check staleness by running:
     ```bash
     git diff <lastCommitHash>..HEAD --name-only
     ```
   - If no changed files → Report "Graph is up to date" and stop
   - If changed files exist → **Incremental update** (re-analyze only changed files)

## Phase 1 — SCAN (Full analysis only)

Dispatch the **project-scanner** agent:

> Scan this project directory to discover all source files, detect languages and frameworks.
> Project root: `<project-root>`

Collect the result: project name, description, languages, frameworks, file list, complexity estimate.

If >200 files, inform the user and suggest scoping with a subdirectory argument.

## Phase 2 — ANALYZE

### Full analysis

Batch the file list from Phase 1 into groups of **5-10 files each**.

For each batch, dispatch a **file-analyzer** agent **in parallel** (up to 3 concurrent):

> Analyze these source files and produce GraphNode and GraphEdge objects.
> Project: `<projectName>`
> Languages: `<languages>`
> All project files (for import resolution): `<full file path list>`
>
> Files to analyze in this batch:
> 1. `<path>` (<sizeLines> lines)
> 2. `<path>` (<sizeLines> lines)
> ...

Collect all results and merge:
- Combine all `nodes` arrays (deduplicate by `id` — keep the later one if duplicates exist)
- Combine all `edges` arrays (deduplicate by `source+target+type`)

### Incremental update

Use the changed files list from Phase 0. Batch and analyze only those files using file-analyzer agents (same process as above). After collecting results, merge with the existing graph:
- Remove old nodes whose `filePath` matches a changed file
- Remove old edges whose `source` or `target` references a removed node
- Add new nodes and edges from the fresh analysis

## Phase 3 — ASSEMBLE

Merge all file-analyzer results into a single set of nodes and edges.

Validate basic integrity:
- Every edge `source` and `target` references an existing node `id`
- Remove any orphaned edges that reference non-existent nodes
- No duplicate node IDs

## Phase 4 — ARCHITECTURE

Dispatch the **architecture-analyzer** agent:

> Analyze this codebase's structure to identify architectural layers.
> Project: `<projectName>` — `<projectDescription>`
>
> File nodes:
> ```json
> [list of {id, name, filePath, summary, tags} for all file-type nodes]
> ```
>
> Import edges:
> ```json
> [list of edges with type "imports"]
> ```

Collect the layers result.

For **incremental updates**: re-run architecture analysis on the full merged node set (layers may shift when files change).

## Phase 5 — TOUR

Dispatch the **tour-builder** agent:

> Create a guided learning tour for this codebase.
> Project: `<projectName>` — `<projectDescription>`
> Languages: `<languages>`
>
> Nodes (summarized):
> ```json
> [list of {id, name, filePath, summary, type} for key nodes]
> ```
>
> Layers:
> ```json
> [layers from Phase 4]
> ```
>
> Key edges:
> ```json
> [imports and calls edges]
> ```

Collect the tour steps.

## Phase 6 — REVIEW

Assemble the full KnowledgeGraph object:

```json
{
  "version": "1.0.0",
  "project": {
    "name": "<projectName>",
    "languages": ["<languages>"],
    "frameworks": ["<frameworks>"],
    "description": "<projectDescription>",
    "analyzedAt": "<ISO timestamp>",
    "gitCommitHash": "<commit hash>"
  },
  "nodes": [<all nodes>],
  "edges": [<all edges>],
  "layers": [<layers from Phase 4>],
  "tour": [<steps from Phase 5>]
}
```

Dispatch the **graph-reviewer** agent:

> Validate this knowledge graph for completeness and correctness.
>
> ```json
> <full KnowledgeGraph JSON>
> ```

If the reviewer reports `approved: false`:
- Review the issues list
- Fix any fixable issues (remove invalid edges, fill missing fields with defaults)
- If critical issues remain after one fix attempt, save the graph anyway with a warning

## Phase 7 — SAVE

1. Write the knowledge graph to `.understand-anything/knowledge-graph.json`
2. Write metadata to `.understand-anything/meta.json`:
   ```json
   {
     "lastAnalyzedAt": "<ISO timestamp>",
     "gitCommitHash": "<commit hash>",
     "version": "1.0.0",
     "analyzedFiles": <number of files analyzed>
   }
   ```
3. Report a summary to the user:
   - Project name and description
   - Files analyzed / total files
   - Nodes created (by type)
   - Edges created (by type)
   - Layers identified
   - Tour steps generated
   - Any warnings from the reviewer
   - Path to the output file
4. Tell the user how to view the dashboard:
   ```
   To view your codebase dashboard, clone the Understand Anything repo and run:
     pnpm install && pnpm dev:dashboard
   The dashboard auto-detects .understand-anything/knowledge-graph.json from the project root.
   ```

## Error Handling

- If any agent fails, retry **once** with clarified context
- If still fails, skip that phase gracefully and continue with partial results
- Always save partial results — a partial graph is better than no graph
- Report any skipped phases or errors in the final summary

## KnowledgeGraph Schema Reference

### Node Types
- `file` — Source file
- `function` — Function or method
- `class` — Class, interface, or type
- `module` — Logical module or package
- `concept` — Abstract concept or pattern

### Node ID Conventions
- `file:<relative-path>` (e.g., `file:src/index.ts`)
- `func:<relative-path>:<name>` (e.g., `func:src/utils.ts:formatDate`)
- `class:<relative-path>:<name>` (e.g., `class:src/models/User.ts:User`)
- `module:<name>` (e.g., `module:authentication`)
- `concept:<name>` (e.g., `concept:dependency-injection`)

### Edge Types (18 total)
| Category | Types |
|----------|-------|
| Structural | `imports`, `exports`, `contains`, `inherits`, `implements` |
| Behavioral | `calls`, `subscribes`, `publishes`, `middleware` |
| Data flow | `reads_from`, `writes_to`, `transforms`, `validates` |
| Dependencies | `depends_on`, `tested_by`, `configures` |
| Semantic | `related`, `similar_to` |

### Edge Weight Conventions
- `contains`: 1.0
- `inherits`: 0.9
- `implements`: 0.9
- `calls`: 0.8
- `exports`: 0.8
- `imports`: 0.7
- `depends_on`: 0.6
- `tested_by`: 0.5
- Other types: 0.5 default
