---
id: "mem-20260819-n2en"
type: "principle"
env: "global"
confidence: "high"
tags: ["中译英", "翻译成英文", "英文化", "native English", "本地化改写", "CN to EN"]
---

# Native CN to EN

Use when the task is primarily Chinese-to-English rendering or English-side polishing from Chinese source text, including requests for 中译英, 翻译成英文, 英文化, native English, 本地化改写, CN to EN, or Chinese to English.

Do not use it for:

- English copywriting from scratch with no Chinese source
- explanation-heavy bilingual tutoring unless the user explicitly asks for commentary
- localization workflows that require glossary, terminology QA, or multi-file asset handling

Local and cloud personas use this memory. Do not depend on whether the host installed a same-named skill.

Turn Chinese source text into two English outputs:

1. 翻译
2. 本地化改写

Keep the source tone. If the Chinese is casual, keep it casual. If it is sharp, restrained, or conversational, preserve that level of force instead of flattening it into generic written English.

## Output target

Pick the output target from the runtime and the user's request.

| Situation | Output target |
|---|---|
| The user gives a specific file path and the runtime can write files locally | Write the result to that file |
| The user gives no file path | Output in the current conversation |
| The runtime is a cloud agent and the user did not explicitly ask for a file artifact | Prefer output in the current conversation |

If writing to a file, write the final output content itself, not an extra report about what you did.

## Core pattern

Always do exactly two passes over the same source text:

1. Produce the 翻译 version by translating every human-readable passage into concise, natural English in the source's register. Establish one request-local rendering for each recurring domain term. Render Chinese proper nouns with an established English name or a consistent supported romanization. Preserve proper nouns and product names already written in their established Latin-script form.
2. Produce the 本地化改写 version by editing the complete 翻译 version for idiomatic phrasing, economy, consistent terminology, and full source coverage. Do not expand or explain beyond the source.

Do not add explanation unless the user explicitly asks for it.

## Required output shape

When outputting in chat, the answer must contain:

1. the label `第1步翻译：`
2. one fenced `text` code block containing only the 翻译 version
3. the label `第2步本地化改写：`
4. one fenced `text` code block containing only the 本地化改写 version

Outside those two code blocks, include no explanation, no bullets, no source text, and no extra notes unless the user explicitly asks for them.

Use this exact shape:

第1步翻译：

```text
翻译内容写在这里。
```

第2步本地化改写：

```text
本地化改写内容写在这里。
```

When writing to a file, write the same content shape into the target file unless the user explicitly asks for another file format.

## Output rules

- Render every human-readable part of the source.
- Preserve meaning before elegance, then improve idiomatic quality in pass two.
- Avoid Chinglish.
- Avoid needless expansion.
- Do not expand or explain beyond the source.
- Keep one consistent rendering for each recurring domain term within the same request.
- Use an established English name for Chinese proper nouns when one exists; otherwise use a consistent supported romanization.
- Preserve proper nouns and product names already written in Latin script.
- Preserve rhetorical force, implied subject, and compression when English can carry them naturally.
- If the source is colloquial, do not over-formalize it.
- If the source is terse, do not pad it.
- If a literal rendering sounds unnatural, prefer the native phrasing that preserves intent.
- Ensure full source coverage. Do not omit a substantive sentence, clause, or term just because a shorter English phrasing reads better.

## Quick reference

| Need | Action |
|---|---|
| User pasted Chinese text into chat | Return both steps in chat |
| User selected text from a file | Process that exact text; return in chat unless a file target was requested |
| User provided a destination path | Write the two-block result to that file |
| User is using a cloud agent without a destination path | Return in chat |

## Common mistakes

- Returning only one version instead of both steps
- Adding commentary, notes, or back-translation when the user asked for output only
- Making pass two freer but not more accurate
- Letting recurring terms drift across the same response
- Translating proper nouns inconsistently or rewriting names already in Latin script
- Smoothing away the original tone
- Omitting a substantive sentence, clause, or term in the name of fluency
- Dumping the full output into chat after writing the requested file, unless the user also asked to see it in chat

## Minimal example

Source:

```text
这不是做不做的问题，而是现在做会不会把系统提前拖进复杂度泥潭。
```

Output:

第1步翻译：

```text
This is not about whether to do it, but whether doing it now would drag the system into a swamp of complexity too early.
```

第2步本地化改写：

```text
This isn't about whether we should do it. It's about whether doing it now would pull the system into unnecessary complexity too early.
```
