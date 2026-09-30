---
name: handdraw-style-prompter
description: Turn a 001–274 hand-drawn style number and image theme into bilingual prompts, using model capability data to decide when core traits and a numbered reference image are required.
---

# Hand-drawn Style Prompter

This is the install entrypoint for the complete hand-drawn style package.
The package root contains the `images/` gallery and numbered reference assets;
the operational contract is [skills/handdraw-style-prompter/SKILL.md](skills/handdraw-style-prompter/SKILL.md).

Before handling a request, read that Skill file completely. Resolve every
gallery and reference-image path from this installed package root. Install this
repository at path `.` so the `images/` directory and the nested Skill are
kept together.

## Request routing index

When the user asks to illustrate an article, plan article illustrations, choose
insertion points, or write prompts for article images, read and invoke
[article-illustration-planner](skills/article-illustration-planner/SKILL.md)
before handling the request. Use the hand-drawn style rules in
[handdraw-style-prompter](skills/handdraw-style-prompter/SKILL.md) for style-number
resolution and prompt construction.
