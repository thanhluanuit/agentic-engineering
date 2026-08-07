# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not a Rails application** — it's a distributable package of Claude Code
configuration (rules + skills) for Rails engineering workflows. Consumers copy
`.claude/rules/` and/or individual `.claude/skills/*` directories into their own
Rails projects. There is no app to build, no test suite to run at the repo root,
and no runtime dependencies beyond Python 3 (used by the skills' bundled scripts).

Work here means: editing rule markdown, editing/creating skills, running a
skill's own scripts against a *target* repo (never this one), and running each
skill's eval/benchmark tooling.

## Repository structure

```
AGENTS.md              # thin adapter for non-Claude agents (Codex CLI, Devin, and other AGENTS.md-reading agents) — see below
.claude/
├── rules/            # Rails engineering rules, auto-loaded by Claude Code
│   ├── principles.md         # always-on — wins when a style rule conflicts
│   ├── technical_stack.md    # always-on — per-project template, fill in per consumer repo
│   ├── code_style.md         # loads on *.rb, *.erb, *.rake, app/**, lib/**, config/**, Gemfile
│   ├── performance.md        # loads on *.rb, app/views/**, config/**
│   ├── security.md           # loads on app/**, config/**, db/**
│   └── testing.md            # loads on spec/**, test/**
└── skills/
    ├── owasp-asvs-security    # ASVS 4.0.3 L2 audit — periodic deep sweep
    ├── owasp-top-10-reviewer  # OWASP Top 10:2025 review — PR gate or repo sweep
    ├── performance-auditor    # N+1s, indexing, caching, jobs, scaling limits
    ├── code-reviewer          # correctness + reuse/simplification review — PR or diff
    └── skill-creator          # scaffold, eval, and optimize skills (meta-skill)
```

## Multi-agent support

This repo is meant to be reused by more than Claude Code. `.claude/rules/*.md`
is the single agent-neutral source of truth for engineering conventions —
plain markdown, no Claude-specific syntax in the body. Two consumption paths
exist on top of it:

- **Claude Code** reads `.claude/rules/` and `.claude/skills/` natively via
  its memory and skill-discovery mechanisms — no adapter needed.
- **Any other agent** — Codex CLI, Devin, and others that follow the open
  AGENTS.md convention — has no equivalent auto-loading, so root
  [`AGENTS.md`](AGENTS.md) is a thin adapter: it lists every rule file and
  when to read it, and documents that the `.claude/skills/*` packages are
  Claude-only automation (their `scripts/` are still runnable by hand from
  any agent).

Windsurf is explicitly out of scope — no adapter is maintained for it.

**When adding, renaming, or rescoping a rule file**, update `AGENTS.md`'s
table in the same change — that file only points at `.claude/rules/`, and a
stale pointer there is worse than none. Skills stay Claude-only by design
(their auto-discovery mechanism doesn't exist in any non-Claude agent, Codex
CLI and Devin included); don't try to give them native triggering in another
agent's format — document the manual `scripts/` runbook path instead, per
`AGENTS.md`.

## Rules: how they work

Rules are markdown files Claude Code loads automatically per
[the memory mechanism](https://code.claude.com/docs/en/memory) — they are read
guidance, not enforced configuration (use hooks/permissions for guarantees).

- **Always-on** (`principles.md`, `technical_stack.md`): no `paths:` frontmatter,
  loaded every session.
- **Path-scoped**: carry a `paths:` glob list in frontmatter and only load when
  Claude opens a matching file — see the header of `code_style.md`,
  `performance.md`, `security.md`, `testing.md` for their exact globs.
- **`technical_stack.md` is a template with blanks** (`<x.y.z>` placeholders) —
  it is meant to be filled in per consumer repo, not here. Don't treat the blanks
  as a bug.
- When editing a rule, keep the frontmatter `paths:` list accurate — that's the
  only thing that determines when it loads.
- `principles.md` is the tie-breaker: when a specific style rule (in
  `code_style.md`, `performance.md`, `security.md`, `testing.md`) conflicts
  with a principle, the principle wins.

## Skills: how they work

Each skill directory follows the standard shape: `SKILL.md` (frontmatter +
instructions, the only thing always in context), plus `scripts/` (executable,
don't need to be read to run), `references/` (loaded on demand), `data/` (JSON
loaded selectively, never whole), `assets/` (output templates), and `evals/`
(test/benchmark harness for the skill itself).

Three of the five skills (`owasp-asvs-security`, `owasp-top-10-reviewer`,
`performance-auditor`) are **read-only reviewers**: they audit a target Rails
repo and write only under a scoped output directory in *that* repo
(`asvs-audit/`, `owasp-review-<date>.md`, `performance-review-report/`
respectively) — they never modify application code. When working on these
skills, preserve that guarantee; it's the thing that makes the audit trustworthy.
`code-reviewer` is the one exception: it's a code-quality reviewer, not a
security/performance auditor, so it's allowed to edit application code — but
only via its explicit `--fix` flag, never by default. Don't loosen that gate
either; the default must stay read-only.

Each skill's scripts assume the working directory is the **target repo root**,
not this repo — invoke them by full/absolute path to the skill's `scripts/`
directory, e.g.:

```bash
python3 /path/to/.claude/skills/owasp-asvs-security/scripts/track_audit.py init 2025-07-28 all
python3 /path/to/.claude/skills/performance-auditor/scripts/checkpoint.py status 2025-07-28
```

### Editing an existing skill

Read the skill's own `README.md` and `SKILL.md` first — each documents its
procedure, finding schema, and requirements in full. Key invariants to preserve
across all three reviewer skills:
- **Evidence or it didn't happen** — every verdict/finding cites a `file:line`,
  tool output, or observed config; uncertain → `NEEDS_REVIEW` /
  `needs-measurement`, never an inflated verdict.
- **Findings have a fixed required-field schema** (see each skill's SKILL.md),
  and their `checkpoint.py`/`track_audit.py add-finding` scripts reject a
  finding missing any field — don't loosen that.
- Checkpointed skills (`owasp-asvs-security`, `performance-auditor`) resume by
  `<run-date>` in strict ISO `YYYY-MM-DD` form — any other format silently
  breaks the prior-run diff.

### Creating or improving a skill: use skill-creator

`skill-creator` is the meta-skill for this repo — invoke it (don't hand-roll a
new skill from scratch) whenever asked to create a new skill, edit an existing
one, or benchmark one. It drives: draft `SKILL.md` → write `evals/evals.json`
test prompts → spawn with-skill and baseline subagent runs in parallel →
aggregate via `python -m scripts.aggregate_benchmark <workspace>/iteration-N
--skill-name <name>` (run from the `skill-creator` directory) → review via
`eval-viewer/generate_review.py` → iterate on user feedback → optionally
optimize the SKILL.md `description` field via `scripts/run_loop.py` (the
primary triggering signal) → package with `scripts/package_skill.py`.
Full procedure is in `.claude/skills/skill-creator/SKILL.md` — read it before
starting rather than reconstructing the loop from memory.

### Benchmarking `owasp-top-10-reviewer`

That skill has a standalone recall benchmark against OWASP RailsGoat (planted
vulnerabilities as ground truth): see
`.claude/skills/owasp-top-10-reviewer/evals/benchmark.md`. Score with
`python3 scripts/score_benchmark.py --expected evals/railsgoat-expected.json --detected results.json`
run from the skill's directory. It measures *strong-tier recall* only (classic
injection/mass-assignment/IDOR/CVE/open-redirect classes) — never report it as
overall coverage.

## Conventions when adding content here

- New rule files need `paths:` frontmatter unless genuinely always-on; update
  the table in `README.md` **and** the rule table in `AGENTS.md` to match —
  Claude Code picks the new file up automatically, but any other agent
  (Codex CLI, Devin, etc.) only finds it through `AGENTS.md`'s explicit
  pointer.
- New skills need a `SKILL.md` with `name` + `description` frontmatter (the
  `description` is the entire triggering mechanism — be specific and a little
  "pushy" about when to use it, per skill-creator's guidance), then a row added
  to `README.md`. A standalone README (workflow, outputs, requirements) is the
  default for a skill with scripts/checkpointed state to document (see the
  three reviewer skills); skip it when `SKILL.md` alone is self-contained
  (e.g. `code-reviewer`).
- Don't add app-level tooling (Gemfile, package.json, CI config) — this repo
  intentionally has none; it's config to be consumed by other repos, not an app
  itself.
