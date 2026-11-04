---
name: pharo-mcp
description: Working in a live Pharo image through the Evref-BL/MCP server (mcp__pharo__*, mcp__pharo-pls__*) — picking the right image/server, using dedicated tools over image_evaluate, running tests, and leaving commits to the user's Iceberg. Use for any Pharo/Smalltalk code task, or when setting up a Pharo project's team.
---

# Pharo through MCP

Upstream: [Evref-BL/MCP](https://github.com/Evref-BL/MCP) (in-image server),
[Evref-BL/PLexus](https://github.com/Evref-BL/PLexus) (image lifecycle + MCP
routing), [Evref-BL/pharo-launcher-mcp](https://github.com/Evref-BL/pharo-launcher-mcp).
Upstream ships its own guide and workflow skills:
`npx @evref-bl/pharo-mcp install --host claude` — prefer them for tool details;
this skill only holds the user's conventions on top.

## Which image

- One image = one MCP server = one port. Known so far: `pharo` on 4000 (general),
  `pharo pls` on 4001 (Pharo-LanguageServer image). The project's `.mcp.json`
  says which one belongs to it.
- Use **only** the server of the project's image. For Pharo-LanguageServer work
  that means `mcp__pharo-pls__*`, never `mcp__pharo__*`.
- Server unreachable → ask the user to start the image (`MCP startOnPort: <port>`);
  don't start or replace images yourself unless PLexus manages them.

## Tools, cheapest first

1. Dedicated tools: `class_search`, `class_get`, `method_get`,
   `method_search`, `method_source_search`, `method_reference_search`,
   `method_compile`, `class_create`, `test_run`.
2. `tool_search` → `tool_call` for the rest of the catalog (refactorings,
   critiques, repositories, debugging).
3. `image_evaluate` last — it returns printStrings and invites trial and error.
   Retros showed hundreds of `image_evaluate` calls per session where a
   dedicated tool would do; reach for it only for a one-off expression.

Read a class once with `class_get` rather than method by method.

## Workflow

- Code lives in the image. Don't export Tonel or edit a local clone unless the
  project's CLAUDE.md says so. The user commits and pushes from the image with
  Iceberg: when done, say what's ready (packages, classes) and stop.
- Run the affected tests with `test_run` after each change; report failures as-is.
- Follow existing package/class naming (the tag/protocol conventions in the image).
- Files outside the image (docs, CI) can't go through Iceberg: list them for
  the user instead of writing them to the clone.
