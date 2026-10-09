[English](README.md) | [简体中文](README_ZH_CN.md)

# Agent OS: A Pluggable Memory System for Any Agent

This repository is a lightweight, platform-agnostic **memory system for AI agents**. It keeps an agent's long-term memory as plain Markdown files inside a Git repository, so the memory outlives any single model, product, or session.

## Why memory

Models keep getting smarter, but intelligence is not what makes an assistant *yours*. A model forgets you the moment its context window resets or the product swaps its backend. The thing that actually compounds — and that no vendor can hand you for free — is **memory about you**: your preferences, your standards, your projects, your way of working. This project makes that memory a standalone artifact you own, keep, and plug into whatever agent comes next.

## Core idea

> Agent = Intelligence + Action + Memory + Proactivity

Intelligence and action are increasingly commoditized. Memory is the only term that grows. This repository is that memory — deliberately minimal, plain text, and decoupled from every model and platform.

## Design

- **Three layers reduced to two.** OpenClaw's memory has an inner core (identity and rules), a middle layer (long-term knowledge), and an outer episodic layer (day-to-day chatter). Because modern agent products let you start a fresh conversation cheaply, the episodic layer is dropped. What remains is a read-only kernel plus a writable long-term store.
- **Memory is scoped by environment.** Every memory carries an `env` tag (`global`, `local`, or `cloud`) so the same repository makes an agent behave correctly whether it runs in a local IDE or a stateless cloud sandbox.
- **Self-evolution via `/learn`.** The agent abstracts a session's learnings into a new memory file, strips project-specific details, and writes it back — to disk locally, or by committing and pushing in the cloud.

## Repository layout

```text
agent-workspace/
├── README.md                   # This file — the front door for newcomers
├── WAKEUP.md                   # The Core Manifesto — read first on every wake-up
├── .memory/                    # The Brain (global knowledge)
│   ├── 00_kernel/              # [READ-ONLY] persona, memory schema, capability discovery
│   ├── preferences/            # [READ/WRITE] user habits & styles
│   ├── principles/             # [READ/WRITE] operating laws
│   ├── entities/               # [READ/WRITE] system-level nouns
│   └── corrections/            # [READ/WRITE] error logs & fixes
└── lab/                        # The Body (execution zone)
    ├── _toolkit/               # [CLOUD-ONLY] sanitized routine tools
    └── <temporary_projects>/   # [READ/WRITE] ephemeral scratchpads
```

## Make it yours

Fork or clone this repository and replace the contents of `.memory/` with your own. The structure stays; the memories become yours. Then wake it up — any agent that can read and write a Git repository can use it.

- The design story: [I Skipped OpenClaw but Stole Its Soul](https://victor42.eth.limo/post-en/personal-memory-system-for-any-agent)
- One-paste cloud bootstrap: [initialization prompt](https://gist.github.com/greenzorro/95768e2096b02f89020fcfcc445472d4)

---

Created by [Victor42](https://victor42.work/) & [Agent Vik](https://github.com/agent-vik/about-me)

---

# For Agent

You are being connected to this **persistent memory repository** for the first time. Follow these steps to clone it and bring the agent to a usable state.

## Prerequisites

- Git installed in the current environment.
- Network access to GitHub (HTTPS).
- A terminal: a local machine (persistent) or a cloud sandbox (stateless).

## One batched human gate

A human must do this once, because only they can authorize it:

- Create a **fine-grained personal access token** scoped to this single repository, with `Contents: Read and write`. Do not request anything broader.

## First-time setup

**Step 1 — Git identity.** Configure it so commits do not fail:

```bash
git config --global user.email "you@example.com"
git config --global user.name "your-agent-name"
```

**Step 2 — Clone.** Use silent, non-interactive mode:

```bash
GIT_TERMINAL_PROMPT=0 git clone https://<your-token>@github.com/<owner>/<repo>.git
```

**Step 3 — Boot.** Enter the repository and load the core manifesto:

```bash
cd <repo>
cat WAKEUP.md
```

## Usage

`WAKEUP.md` is the runtime boot document. On every wake-up, read it and **run the initialization sequence it requires** — loading `.memory/00_kernel/persona.md`, `.memory/00_kernel/memory_schema.md`, and `.memory/00_kernel/capability_discovery.md` — before doing anything else.

After boot, its protocols apply: run the pre-flight memory retrieval before complex tasks, load memories filtered by the current `env` tag, and use `/learn` to persist new global knowledge.

## Verify

After the boot sequence, ask the agent "Who are you, and who am I?". A correctly woken agent answers from memory, not from model defaults.

## Hand off to the human

When the token is in place and the repository is cloned, control returns to the human, who gives the first real task.

## Red lines

- Never commit secrets, tokens, or private credentials into `.memory/`.
- Cloud sandbox: persist memory by committing and pushing. Local machine: write to disk and let the human commit.
- `.memory/00_kernel/` is read-only.
