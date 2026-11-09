# scheduler — a shuttle for time-based tasks

One platform cron, not one cron per task. The timetable lives inside `dispatcher-prompt.md`; this directory holds only the shuttle prompt and the node adapter. Task bodies stay where they already live — nothing is copied here.

## The idea

A cron wake-up hands the agent a prompt and no history. Instead of registering one cron per task, register **one** cron at a fixed minute of every hour. The waking session reads a timetable and runs whatever is due. The agent becomes a shuttle: same vehicle, different stops.

Three consequences worth knowing before deploying:

- Adding or moving a task touches one file, not the platform.
- A wake-up with nothing due costs one message and exits.
- A missed wake-up is truly missed; an overlapping one truly runs twice. There is no queue.

## Tasks

| Task | Canonical location | Run by |
|---|---|---|
| Science briefing (daily, 06) | `lab/tasks/science_daily.md` | the shuttle session itself |
| Port cleanup (daily, 07) | `lab/_toolkit/port_cleaner.py` | the shuttle session itself |

Both are executed inside the waking session. No background worker is involved.

## Prerequisites

- A platform whose cron accepts a free-text prompt and wakes a fresh session each time.
- The workspace path is known to the deployment.
- For the science briefing: `lab/_toolkit/utils/keys.json` filled in with a working sender. Port cleanup needs nothing beyond the repo.

## Deploy in three steps

1. Create `env.sh` in this directory. It is gitignored on purpose — node-specific values never belong in the repo.

   ```sh
   NODE="<node name>"
   PROXY_BOOT="<command that brings a proxy up; leave empty if the node has direct egress>"
   PROXY_EXPORT="<export statement for that proxy; leave empty likewise>"
   ```

2. Create the platform cron: expression `11 * * * *`, in the node's own timezone. Prompt = the body of `dispatcher-prompt.md` with `{{WORKSPACE}}` replaced by that node's absolute workspace root.

3. Smoke test: trigger once. Expect read-timetable → run what is due → report. On an hour with nothing due, expect a single alive line.

## Maintenance

- Change the timetable: edit `dispatcher-prompt.md` **and** re-paste the prompt into the platform (two places). The file is canonical; the platform copy is a running instance.
- Change a task's content: edit the canonical location only, listed in the table above. This directory stays untouched.
- Failure semantics: nothing is idempotent by design. If a task ever becomes one where a duplicate run costs money or sends a second message, add an idempotency check to that task alone — never globally.
