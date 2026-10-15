# Why the workflow uses source code and rendered evidence

The workflow follows one practical loop: write a deterministic scene, render
stable views, inspect the pixels, check structured facts, and revise the source.
The useful part is the observation channel, not a particular agent connector.

## Blender supports the batch model directly

Blender documents background execution, factory startup, Python error exit
codes, command ordering, and still-image animation output. The repository uses
those native interfaces instead of controlling the GUI.

- [Blender command-line arguments](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)
- [Blender command-line rendering](https://docs.blender.org/manual/en/5.2/advanced/command_line/render.html)
- [Blender Python scripting tips](https://docs.blender.org/api/5.2/info_tips_and_tricks.html)
- [Blender operator context pitfalls](https://docs.blender.org/api/5.2/info_gotchas_operators.html)
- [Blender animation output guidance](https://docs.blender.org/manual/en/5.2/render/output/animation.html)

Blender recommends still-image sequences for animation output. A frame sequence
survives a partial render and lets the encoder change without rerendering the
scene.

## Pixels and structured checks catch different errors

A valid scene graph cannot prove that a label is readable. A convincing image
cannot prove that a hidden count or final owner is correct. The runtime therefore
writes both rendered frames and a JSON manifest.

SceneCraft uses a related code, render, critique, and revise loop. SimWorlds
adds deterministic runtime inspection because images alone cannot validate a
dynamic mechanism.

- [SceneCraft paper](https://arxiv.org/abs/2403.01248)
- [SimWorlds paper](https://arxiv.org/abs/2607.01766)

## CraftBot provides a useful evaluation precedent

CraftBot stores Blender models as versioned Python, renders stable diagnostic
views, checks geometry numerically, and exports downstream review data. This
repository reuses the method, not CraftBot code: keep source inspectable, keep
evaluation views stable, and combine visual review with machine checks.

CraftBot was reviewed at commit
`2acd0c79d8caaa1ecf822e3eb83a43de2afd6b63`. Its license is MIT.

- [CraftBot repository](https://github.com/lukapiskorec/craftbot/tree/2acd0c79d8caaa1ecf822e3eb83a43de2afd6b63)
- [CraftBot license](https://github.com/lukapiskorec/craftbot/blob/2acd0c79d8caaa1ecf822e3eb83a43de2afd6b63/LICENSE)
- [CraftBot render views](https://github.com/lukapiskorec/craftbot/blob/2acd0c79d8caaa1ecf822e3eb83a43de2afd6b63/tools/render_views.py)
- [CraftBot verification workflow](https://github.com/lukapiskorec/craftbot/blob/2acd0c79d8caaa1ecf822e3eb83a43de2afd6b63/skills/verifying-models/SKILL.md)

## Direct `bpy` is the smaller interface for empty scenes

An MCP bridge helps when an agent must inspect a large artist-owned `.blend`,
preserve a live interactive session, or query unfamiliar state. It adds little
when one Python file can rebuild an empty scene in seconds. A direct process has
fewer states to leak, a reviewable source file, and an explicit lifetime.

The official Blender Lab MCP server and community servers can execute generated
Python with the Blender process's operating-system permissions. Use an isolated
machine or account for untrusted input.

- [Blender Lab MCP server](https://www.blender.org/lab/mcp-server/)
- [Blender license](https://www.blender.org/about/license/)
