---
name: vscode-extension
description: Conventions for the user's TypeScript/React projects, especially VS Code extensions (extension host + React webviews + language client) — layout, build, testing, and how to verify a change. Use when working on vscode-pharo or another VS Code extension or React/TS frontend.
---

# VS Code extension (TypeScript + React)

Read the project's `package.json` scripts and `CLAUDE.md` first; they win over
this file.

## Shape

- **Extension host** (`src/extension.ts`, Node): commands, language client,
  tree views. Nothing React here.
- **Webviews** (React, bundled separately): talk to the host only through typed
  `postMessage` contracts; define the message types once, shared by both sides,
  and validate incoming messages (zod or a type guard).
- **Language features** come from the language server (PLS for Pharo). New
  protocol features go server-side; the extension stays a thin client.
- `contributes` in `package.json` is API: commands, settings and views need an
  entry there and an `activationEvents` path.

## Verify

Cheapest that proves the change, in order:

1. `npx tsc --noEmit` (allowlisted)
2. `npx vitest run <files>` (allowlisted) for pure logic
3. The project's bundling script (esbuild/webpack/vite) when imports or the
   webview change
4. `@vscode/test-electron` / extension tests only when activation or commands
   change

Use the `run` skill to launch the Extension Development Host when the user wants
to see it.

## Code

- Strict TypeScript, no `any`; pure logic out of React components with a test next to it.
- Small components, one per file; hooks for state and messaging.
- Dispose everything registered (`context.subscriptions.push(...)`).
- Node version deprecations in CI (`actions/setup-node`) are their own PR.
