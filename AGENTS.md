# AGENTS.md

Adapter for any agent that doesn't have Claude Code's auto-loading memory
mechanism and instead reads a root `AGENTS.md` — **Codex CLI**, **Devin**,
and others following the same convention. Claude Code reads
[`.claude/rules/`](.claude/rules/) and [`.claude/skills/`](.claude/skills/)
natively and needs nothing from this file.

`.claude/rules/*.md` is the single, agent-neutral source of truth for
engineering conventions in this template — plain markdown, no Claude-specific
syntax in the body. This file just tells a non-Claude agent which of those
files to read and when, since it has no auto-loading mechanism of its own.

## Rules — read these

| Rule file | When to read it | Covers |
|---|---|---|
| [`.claude/rules/principles.md`](.claude/rules/principles.md) | Always | Core engineering values — Convention over Configuration, DRY, SOLID in Rails terms. Wins when a style rule conflicts. |
| [`.claude/rules/technical_stack.md`](.claude/rules/technical_stack.md) | Always | Per-project stack (Ruby/Rails versions, DB, jobs, frontend) — a template with blanks, filled in per consumer repo. |
| [`.claude/rules/code_style.md`](.claude/rules/code_style.md) | Editing `*.rb`, `*.erb`, `*.rake`, `app/**`, `lib/**`, `config/**`, `Gemfile`, `Rakefile` | Ruby + Rails + frontend style conventions. |
| [`.claude/rules/performance.md`](.claude/rules/performance.md) | Editing `*.rb`, `app/views/**`, `config/**` | N+1 queries, indexing, caching, background jobs, safe migrations. |
| [`.claude/rules/security.md`](.claude/rules/security.md) | Editing `*.rb`, `*.erb`, `app/**`, `config/**`, `db/**`, `Gemfile` | Everyday secure-coding baseline. |
| [`.claude/rules/testing.md`](.claude/rules/testing.md) | Editing `spec/**`, `test/**` | RSpec/Minitest conventions — test types, factories, isolation, flaky-test hygiene. |

When a rule conflicts with `principles.md`, `principles.md` wins.

## Skills — Claude Code only, run by hand

The `.claude/skills/*` packages (`owasp-asvs-security`, `owasp-top-10-reviewer`,
`performance-auditor`, `code-reviewer`, `skill-creator`) rely on Claude Code's
description-based auto-discovery to decide *when* to trigger. That mechanism
doesn't exist outside Claude Code — Codex CLI, Devin, or any other agent
reading this file — so they won't fire automatically here.

Their `scripts/` are plain Python and Bash, runnable by hand from any agent or
terminal — invoke them directly against the target repo root, e.g.:

```bash
python3 /path/to/.claude/skills/owasp-asvs-security/scripts/track_audit.py init 2025-07-28 all
python3 /path/to/.claude/skills/performance-auditor/scripts/checkpoint.py status 2025-07-28
```

Read the skill's own `SKILL.md` (and `README.md`, where present) for the full
procedure before running its scripts — the workflow, output locations, and
finding schema are documented there, not here.

## Keeping this file current

When a rule file is added, renamed, or rescoped, update the table above in
the same change, alongside `README.md`'s rule table — this file is the only
thing that points any non-Claude agent at `.claude/rules/`, and a stale
pointer here is worse than none.

Windsurf is explicitly out of scope — no adapter is maintained for it.
