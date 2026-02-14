# SYSTEM MEMORY SCHEMA & `/learn` PROTOCOL

> **CORE DIRECTIVE:** > You are reading the memory schema of this Agent OS. Whenever you extract a new learning, preference, or rule, you MUST format it exactly as specified in this document before saving it to the `.memory/` directory.

## 1. The `/learn` Protocol (Memory Extraction)
When the User commands `/learn` (or explicitly asks you to remember something global), you must execute this sequence:

**Step 0: Scope Audit (CRITICAL)**
- **Load Boundary**: Before identifying insights, you MUST read `.memory/principles/scope_isolation.md`.
- **Verify Eligibility**: Explicitly ask yourself: "Is this global or local?" If it belongs to a project's `notes.md`, DO NOT proceed with /learn.

1. **Identify**: Extract the core insights from the current conversation.
2. **Filter**: Discard all project-specific data (e.g., local variables). Keep ONLY global, reusable knowledge.
3. **Sanitize Paths**: **CRITICAL STEP.** Scan content for absolute paths. Replace them with abstract variables defined in `routine/utils/path.py` (see Section 5).
4. **Format**: Draft a `.md` file using the strict YAML Frontmatter defined below.
5. **Route**: Save the file to the correct subfolder inside `.memory/`.
6. **Persist (Environment Logic)**:
   * **IF `env: cloud`**: Execute `git add`, `git commit -m "chore(memory): add [type] - [desc]"`, and `git push origin main`.
   * **IF `env: local`**: Write the file to disk ONLY. Do NOT execute git commands automatically. Notify the User to review.
---

## 2. YAML Frontmatter Standard
EVERY file you write to `.memory/` (except inside `00_kernel/`) MUST begin with this exact YAML frontmatter structure. No exceptions.

```yaml
---
id: "mem-{YYYYMMDD}-{random_4_chars}"
type: "{strictly_one_of_the_4_types_below}"
env: "{global|cloud|local}"
confidence: "{high|medium|low}"
tags: ["tag1", "tag2"]
---
```

* **`id`**: Must be unique. E.g., `mem-20260211-a8x9`.
* **`env`**: Execution environment scope.
  * `global`: Universal principles (e.g., Python coding style, MECE thinking, Persona).
  * `cloud`: Ephemeral sandbox-specific (e.g., relative paths, no root, git config for stateless nodes).
  * `local`: Physical machine-specific (e.g., MacOS paths, AppleScript, heavy tools).
* **`confidence`**:
  * `high`: Explicitly stated by the User.
  * `medium`: Extracted/inferred by you from successful executions.
  * `low`: Unverified hypotheses or temporary fixes.

## 3. The 4 Global Types & Directory Mapping

You must classify the memory into exactly ONE of the following types and save it to its corresponding folder.

### Type 1: `preference`

* **Definition**: The User's cross-project habits, analytical frameworks, and aesthetic standards.
* **Target Folder**: `.memory/preferences/`
* **Example**: "User strictly requires MECE frameworks before coding," "User prefers Python type hints."

### Type 2: `principle`

* **Definition**: Global operating laws, physical constraints of this sandbox, or workflow rules.
* **Target Folder**: `.memory/principles/`
* **Example**: "Always use GIT_TERMINAL_PROMPT=0 when cloning/pushing to prevent terminal block."

### Type 3: `entity`

* **Definition**: System-level nouns, architectural concepts, or agent definitions. NEVER project-level variables.
* **Target Folder**: `.memory/entities/`
* **Example**: "agent-workspace (The persistent memory monorepo)", "Agent实例 (The compute node)".

### Type 4: `correction`

* **Definition**: Fatal system-level errors you made and the definitive solution provided by the User.
* **Target Folder**: `.memory/corrections/`
* **Example**: "Do not attempt to write SSH private keys to disk due to HARD_BLOCKED_SECRET_FILE. Use HTTPS PAT instead."

## 4. Body Content Formatting

* **Keep it MECE**: Mutually Exclusive, Collectively Exhaustive.
* **Be Concise**: Use bullet points. Do not write chatty introductions or conclusions. Treat it like a database record.

## 5. Path Abstraction Standards (Cross-Platform Portability)

To ensure memories work across Windows, Linux, and MacOS, you are **STRICTLY FORBIDDEN** from writing hardcoded absolute paths in memory content.

**The Mapping Rule:**

Refer to the User's infrastructure (`routine/utils/path.py`) and use these variables instead of raw paths:

- `PATH_DOWNLOADS`: Instead of `/Users/{user}/Downloads` or `D:\Downloads`
- `BASE_PATH_CODING`: Instead of `/Users/{user}/.../coding`
- `BASE_PATH_CODING/agent-workspace`: Instead of absolute path to this repo
- `BASE_PATH_CODING/projects`: Instead of absolute path to projects folder
- `BASE_PATH_CODING/routine`: Instead of absolute path to routine folder

**Example:**

- ❌ Bad: "The dataset is in `/Users/victor/Downloads/temp`"
- ✅ Good: "The dataset is in `PATH_DOWNLOADS/temp`"
