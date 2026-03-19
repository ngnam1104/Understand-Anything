# Installing Understand-Anything for OpenClaw

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lum1104/Understand-Anything.git ~/.openclaw/understand-anything
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.openclaw/skills
   ln -s ~/.openclaw/understand-anything/understand-anything-plugin/skills ~/.openclaw/skills/understand-anything
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\skills"
   cmd /c mklink /J "$env:USERPROFILE\.openclaw\skills\understand-anything" "$env:USERPROFILE\.openclaw\understand-anything\understand-anything-plugin\skills"
   ```

3. **Restart OpenClaw** to discover the skills.

## Usage

- `@understand` — Analyze the current codebase
- `@understand-chat` — Ask questions about the knowledge graph
- `@understand-dashboard` — Launch the interactive dashboard

## Updating

```bash
cd ~/.openclaw/understand-anything && git pull
```

## Uninstalling

```bash
rm ~/.openclaw/skills/understand-anything
rm -rf ~/.openclaw/understand-anything
```
