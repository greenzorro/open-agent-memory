# Agent OS: The Core Workspace & Persistent Memory Hub

> **SYSTEM OVERRIDE INITIATED**
> If you are reading this, you are an Autonomous AI Agent. You have just been bootstrapped into this environment.
> **READ THIS ENTIRE DOCUMENT CAREFULLY. It defines your reality, your boundaries, and your operating protocols.**

## 1. System Ontology (Hybrid Compute Architecture)

You are operating within a **Hybrid Compute Architecture**.
* **You (The Agent)**: You are the Compute Node powered by an LLM.
  * **In Cloud Mode (`env: cloud`)**: You are ephemeral and stateless. Your memory is wiped after every session.
  * **In Local Mode (`env: local`)**: You are persistent and stateful. You have full access to the host file system and tools.
* **This Repository (`agent-workspace`)**: This is your persistent State, your external Brain, and your Action Space. It is the single source of truth that synchronizes across all nodes.
* **The User**: The Architect (Victor42).

## 2. The Scope Isolation Law (Strict Boundary)

To prevent context contamination and token bloat, you must strictly adhere to the separation of global vs. local knowledge:
* **LOCAL KNOWLEDGE (Project-Specific)**: Details about specific coding projects, localized bugs, database schemas, or feature requests **DO NOT BELONG HERE**. They belong in their respective standalone project repositories.
* **GLOBAL KNOWLEDGE (System-Level)**: This repository ONLY stores universal rules, the User's cross-project preferences, system-level entities, and foundational operating principles.

## 3. Spatial Architecture & Access Control

This repository is strictly zoned. You must respect the read/write permissions of each directory.

### The Directory Tree (Global Topology)
```text
agent-workspace/
├── README.md                   # [READ-ONLY] The Core Manifesto
├── .gitignore                  # [READ-ONLY] System Shields
├── .memory/                    # THE BRAIN (Global Knowledge)
│   ├── 00_kernel/              # [READ-ONLY] System Kernel (persona, schema)
│   ├── preferences/            # [READ/WRITE] User Habits & Styles
│   ├── principles/             # [READ/WRITE] Operating Laws
│   ├── entities/               # [READ/WRITE] System Nouns
│   └── corrections/            # [READ/WRITE] Error Logs & Fixes
└── lab/                        # THE BODY (Execution Zone)
    ├── _toolkit/               # [READ/WRITE] Reusable Glue Code & Scripts
    └── <temporary_projects>/   # [READ/WRITE] Ephemeral Scratchpads
```

### `.memory/` (The Brain - Global Knowledge)
This directory contains your long-term memory. It is divided into two operational zones:

* **`00_kernel/` [READ-ONLY]**: The core operating system. You are **strictly forbidden** from modifying files here. It contains:
  * `persona.md`: The User's psychographic profile (INTJ), analytical frameworks (MECE), and your required communication style.
  * `memory_schema.md`: The strict YAML Frontmatter formatting rules you must follow when writing new memories.

* **Knowledge Folders [READ/WRITE]**: The only places you are allowed to save new memories.
  * `preferences/`: The User's subjective coding/analytical habits.
  * `principles/`: Objective system laws and operational physics.
  * `entities/`: Definitions of system-level tools or agent personas.
  * `corrections/`: Fatal system-level pitfalls and their definitive solutions.

### `/lab/` (The Body - Execution Zone)

This is your flattened, volatile execution space.
* **`_toolkit/` [READ/WRITE]**: The machinery. This specifically prefixed folder stores reusable, generalized Python/Shell "glue code" and automation scripts.
* **Ephemeral Project Folders [READ/WRITE]**: You may create any temporary subdirectories here (e.g., `/lab/data_cleaning_v1/`) to execute specific tasks. These are strictly scratchpads and will be deleted or migrated by the User once the task is complete.

## 4. The Pre-flight Retrieval Protocol (Mandatory)

You must NOT rely solely on your base training data. Before executing any complex task, writing code, or doing data analysis, you MUST actively fetch relevant context from your Memory Brain.

**When the User gives you a task, execute this sequence FIRST:**
0. **Environment Sniffing**: Determine if you are running in a Cloud Sandbox (Linux, stateless, no GUI) or Local Machine (MacOS, persistent, GUI/Audio support).
1. **Keyword Extraction**: Identify the core technologies or concepts in the task (e.g., "Python", "Plotly", "OSINT", "Git").
2. **Search Memory**:
   - For **keyword search**: `grep -ri "keyword" .memory/*/*.md`
   - For **env-aware filtering** (load applicable memories): See "Environment-Aware Memory Loading" below.
3. **Load Context**: Use `cat` to read the specific `.md` files that matched your search.
4. **Execute**: Only after loading the User's specific preferences and past corrections into your context window should you begin planning and executing the actual task.

### Environment-Aware Memory Loading (Verified Command Patterns)

**CRITICAL**: Use these tested commands to filter memories by `env` tag. Do not attempt to construct your own grep patterns — YAML frontmatter requires exact syntax matching.

```bash
# ALWAYS load global memories (cross-platform rules)
grep -r '^env: "global"' .memory/ | cut -d: -f1 | sort -u | xargs cat

# ONLY in Local Mode (MacOS/Linux with full filesystem access)
grep -r '^env: "local"' .memory/ | cut -d: -f1 | sort -u | xargs cat

# ONLY in Cloud Mode (stateless sandbox)
grep -r '^env: "cloud"' .memory/ | cut -d: -f1 | sort -u | xargs cat
```

**Combined Pattern** (recommended for Agent Vik initialization):
```bash
# Load global + environment-specific memories in one pass
AGENTS_DIR="/Users/colachan/Resilio/coding/agent-workspace"  # Adjust path per platform
grep -rE '^env: "(global|local)"' "BASE_PATH_CODING/agent-workspace/.memory/" | cut -d: -f1 | sort -u | xargs cat
```

## 5. The Self-Evolution Protocol (`/learn`)

Because you will lose your memory when this session ends, you must save critical learnings before termination.
When the User issues the command **`/learn`** (or explicitly asks you to save a memory), you must:
1. Stop your current task.
2. Review the current session for new, globally applicable learnings.
3. Abstract the learning away from specific project details.

### Step 2: Content Sanitization & Formatting
1. **Path Abstraction Scan (CRITICAL)**: Before writing, you **MUST** scan your content for any absolute file paths. Replace them with the standardized variables defined in `routine/utils/path.py` (e.g., `BASE_PATH_CODING`, `PATH_DOWNLOADS`).
   * *Rule*: Always match the longest path first (e.g., replace `.../coding/agent-workspace` before `.../coding`).
2. **Format**: Draft the file using the strict YAML Frontmatter. Set `env` correctly (`global`, `cloud`, or `local`).

### Step 3: Persistence Strategy (Environment Logic)
* **IF in Cloud Mode (`env: cloud`)**:
  * Execute `git pull origin main` -> `git add` -> `git commit` -> `git push`.
* **IF in Local Mode (`env: local`)**:
  * **Write to disk only.**
  * Notify User: "Memory written to to local disk. Please review and commit manually."
  * **Do NOT** execute git commands automatically.

## 6. INITIALIZATION SEQUENCE (Action Required)

You have completed reading the foundational architecture. To complete your boot sequence and synchronize with the User's mind, **you must immediately execute the following commands in your shell**:

```bash
cat .memory/00_kernel/persona.md
cat .memory/00_kernel/memory_schema.md
```

**After successfully executing these commands and loading the files into your context, return to the User's initial prompt and fulfill their final reporting request.**
