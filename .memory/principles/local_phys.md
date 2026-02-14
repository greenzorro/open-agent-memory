---
id: "mem-20260212-local-phys"
type: "principle"
env: "local"
confidence: "high"
tags: ["filesystem", "permissions", "retrieval", "local-node"]
---

# Local Host Operating Physics

## 1. File System Access Protocol
- **Absolute Paths Allowed**: You ARE permitted to use absolute paths to navigate the User's verified directories.
- **Safety Boundary**:
  - ✅ **Safe Zone**: `BASE_PATH`, `Downloads/temp`.
  - ⚠️ **Caution Zone**: System configs (`~/.zshrc`, `.env`). Modify ONLY with explicit permission.
  - 🚫 **Restricted Zone**: Root system directories (`/var`, `/usr`, `/etc`).

## 2. Project Retrieval Protocol (Notes Over Readme)
- **First Truth Source**: When entering any project directory, prioritize checking for `notes.md` over `README.md`. 
- **Memo Consistency**: Assume `notes.md` contains the real-time architectural blueprint and technical debt.
- **Project Context**: Always link task execution to the "purpose" defined in the project's notes.

## 3. Persistence & Tooling
- **State Persistence**: Rely on files persisting between sessions. 
- **GUI Awareness**: The host supports GUI, audio, and local browser automation.
