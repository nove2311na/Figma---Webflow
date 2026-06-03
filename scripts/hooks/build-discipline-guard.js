#!/usr/bin/env node
/**
 * MAS Build Discipline Guard — PreToolUse hook for Bash tool.
 *
 * Enforces D-1 from agentic/policies/build-discipline.md:
 *   "Write→Bash, never multi-line `python -c`"
 *
 * Reads Claude Code hook JSON from stdin:
 *   {tool_name, tool_input: {command}, ...}
 *
 * Detects `python -c` invocations that contain embedded newlines (raw `\n` in
 * the command string OR escaped \n in a quoted python code block). Blocks
 * with exit code 2 and writes a clear D-1 message to stderr.
 *
 * Allows:
 *   - python (no -c)
 *   - python -c "single line; with semicolons" (no newlines, no embedded \n)
 *   - python scripts/anything.py
 *   - any other command
 *
 * Exit codes (Claude Code PreToolUse contract):
 *   0 = allow
 *   2 = block (stderr is shown to user as the reason)
 */
'use strict';

const fs = require('fs');

let raw = '';
try {
  raw = fs.readFileSync(0, 'utf8');
} catch (err) {
  process.exit(0);
}

let payload = {};
try {
  payload = JSON.parse(raw);
} catch (err) {
  process.exit(0);
}

if (payload.tool_name !== 'Bash') {
  process.exit(0);
}

const command = (payload.tool_input && payload.tool_input.command) || '';
if (typeof command !== 'string' || command.length === 0) {
  process.exit(0);
}

const pyCRegex = /\bpython(?:3)?(?:\s+-c|\s+--c)\b/;
if (!pyCRegex.test(command)) {
  process.exit(0);
}

const hasRawNewline = command.includes('\n');
const hasEscapedNewline = /python[^"]*"[^"]*\\n[^"]*"/.test(command) || /python[^']*'[^']*\\n[^']*'/.test(command);
const hasHeredoc = /<<\s*['"]?python['"]?/.test(command);

if (hasRawNewline || hasEscapedNewline || hasHeredoc) {
  const reason = [
    '[MAS Build Discipline D-1] Blocked: multi-line `python -c` detected.',
    '',
    'Command contained an embedded newline inside `python -c` code, which',
    'Windows bash mangles (causes SyntaxError: EOL while scanning string).',
    '',
    'Required pattern (D-1): use the Write tool to save a .py file, then run it.',
    '  1. Write tool -> save scripts/<descriptive_name>.py',
    '  2. Bash: python scripts/<descriptive_name>.py',
    '',
    'Single-line `python -c` with semicolons IS allowed. Multi-line is not.',
    'See agentic/policies/build-discipline.md (D-1) for full rationale.',
  ].join('\n');
  process.stderr.write(reason + '\n');
  process.exit(2);
}

process.exit(0);
