# agentic-engineering

AI agent skills and rules for engineering workflows — reusable across
**Claude Code** and any other agent that reads a root **AGENTS.md** file
(Codex CLI and Devin today; the adapter works for any agent following that
same convention).

A **skill** is a self-contained package (instructions + scripts + data) that an
agent like Claude Code discovers and runs on demand. Drop one into a project and
the agent knows *when* to use it and *how* to run it. Skill auto-discovery is
Claude Code-specific — see [Multi-agent support](#multi-agent-support) below
for how other agents use the same skills manually.

A **rule** is a markdown instruction file the agent reads automatically — either
every session or only when it opens a matching file — to keep coding conventions
consistent without being asked. Rule *content* is agent-neutral; only the
auto-loading is Claude-specific.

## Structure

```
agentic-engineering/
├── AGENTS.md                           # thin adapter for any non-Claude agent — points at .claude/rules/
├── .claude/
│   ├── rules/                          # Rails engineering rules (single source of truth)
│   │   ├── principles.md               # always-on
│   │   ├── technical_stack.md          # always-on (per-project template)
│   │   ├── code_style.md               # loads on Ruby/Rails/frontend files
│   │   ├── performance.md              # loads on Ruby files, views, config
│   │   ├── security.md                 # loads on app/config/db code
│   │   └── testing.md                  # loads on spec/test files
│   └── skills/                         # Claude Code-only automation (scripts runnable by hand elsewhere)
│       ├── owasp-asvs-security         # audit code against OWASP ASVS 4.0.3
│       ├── owasp-top-10-reviewer       # review code against OWASP Top 10:2025
│       ├── performance-auditor         # find N+1s, missing indexes, and scaling limits
│       ├── code-reviewer                # correctness + reuse/simplification review of a PR or diff
│       └── skill-creator               # scaffold, evaluate, and optimize new skills
```

| Skill | What it does |
|---|---|
| [`owasp‑asvs‑security`](.claude/skills/owasp-asvs-security) | Audits your code against OWASP ASVS 4.0.3 (Level 2), citing evidence for every finding. |
| [`owasp‑top‑10‑reviewer`](.claude/skills/owasp-top-10-reviewer) | Reviews a GitHub PR or a whole Rails repo against OWASP Top 10:2025 — Brakeman + bundler-audit signal, confirmed in code, plus the inspection pass tools can't do. |
| [`performance‑auditor`](.claude/skills/performance-auditor) | Reviews a Rails + PostgreSQL codebase or PR for performance problems — N+1s, missing indexes, caching, jobs, scaling limits. Measures before it prescribes; every finding ships with a way to verify the win. |
| [`code‑reviewer`](.claude/skills/code-reviewer) | Reviews a PR or diff for correctness bugs and reuse/simplification/efficiency cleanups, checked against the repo's own rules. Effort levels + optional inline PR comments or applied fixes; read-only unless asked. |
| [`skill‑creator`](.claude/skills/skill-creator) | Scaffolds, refines, and optimizes skills, with evals to benchmark what works. |


---

## Multi-agent support

This template isn't Claude Code-only. `.claude/rules/*.md` is the single,
agent-neutral source of truth for engineering conventions; how each agent
consumes it differs:

| Agent | Entry point | Notes |
|---|---|---|
| **Claude Code** | `.claude/rules/`, `.claude/skills/` | Native — rules auto-load by path, skills auto-trigger by description. |
| **Any AGENTS.md-reading agent** (Codex CLI, Devin, and others following the same convention) | [`AGENTS.md`](AGENTS.md) → `.claude/rules/` | No auto-loading of its own — `AGENTS.md` lists every rule file and when to read it. Skills run manually via their `scripts/`. |

Windsurf is explicitly out of scope — no adapter is maintained for it.

**Using this with Codex CLI, Devin, or another AGENTS.md-reading agent** —
copy `.claude/rules/` (and `AGENTS.md`, if your project doesn't already have
one — merge its rule table in if it does) into your project, then fill in
`technical_stack.md`. Skills under `.claude/skills/*` don't auto-trigger
outside Claude Code, but their `scripts/` are plain Python/Bash — invoke them
by hand per `AGENTS.md`'s runbook, or per each skill's own
`SKILL.md`/`README.md`.

---

## Rules

The [`.claude/rules/`](.claude/rules/) directory holds engineering conventions
that apply to every Rails project. They follow
[Claude Code's rules mechanism](https://code.claude.com/docs/en/memory): the
agent loads them into context on its own, so your code stays consistent without
you restating the standards each session.

**Always-on** rules load every session
as baseline context; **path-scoped** rules carry `paths:` frontmatter and load
only when the agent opens a matching file, so they cost nothing until relevant.

| Rule | Loads | Covers |
|---|---|---|
| [`principles.md`](.claude/rules/principles.md) | Always-on | Core engineering values — Convention over Configuration, DRY, and SOLID applied in Rails terms. Wins when a style rule conflicts. |
| [`technical_stack.md`](.claude/rules/technical_stack.md) | Always-on | Per-project stack template (Ruby/Rails versions, DB, jobs, frontend) to fill in and keep current. |
| [`code_style.md`](.claude/rules/code_style.md) | `*.rb`, `*.erb`, `app/**`, `lib/**`, `config/**` | Ruby + Rails + frontend style; the conventions RuboCop and ERB Lint can't enforce on their own. |
| [`performance.md`](.claude/rules/performance.md) | Ruby files, views, config | N+1 queries, indexing, caching, background jobs, and safe migrations on live databases. |
| [`security.md`](.claude/rules/security.md) | `app/**`, `config/**`, `db/**` | Everyday secure-coding baseline; points to `owasp-asvs-security` for the periodic deep audit. |
| [`testing.md`](.claude/rules/testing.md) | `spec/**`, `test/**` | RSpec/Minitest conventions — test types, factories, isolation, flaky-test hygiene. |

Rules are guidance the agent *reads*, not configuration it *enforces*. For
guaranteed behavior use [hooks](https://code.claude.com/docs/en/hooks) or
[permissions](https://code.claude.com/docs/en/permissions).

**Using them in your own project** — copy `.claude/rules/` into any Rails repo,
then fill in `technical_stack.md`. The agent picks them up automatically on the
next session.


---

## owasp-asvs-security

A read-only security audit. Ask your agent for a security review and it walks
your repo against **OWASP ASVS 4.0.3 (Level 2)** — chapter by chapter, citing
evidence for every verdict, and never touching your code.

**Why teams use it**

- **Evidence or it didn't happen** — every verdict cites a `file:line`, tool
  result, or config; when unsure it returns `NEEDS_REVIEW` instead of guessing.
- **Scan, read, or ask** — each requirement is tiered *auto* (scanner),
  *inspect* (read the code), or *manual* (human sign-off).
- **Re-audits get smarter** — each run saves a baseline, so the next one surfaces
  regressions and confirmed fixes instead of starting over.
- **Never edits your code** — the only files it writes are under `asvs-audit/`.

**How to run it**

Just ask — *"run an OWASP ASVS audit"*, *"audit V2 authentication"*, or *"do the
quarterly security review"*. The skill handles the rest: start the run, assess
each section, then render reports and save the baseline.

**What you get** — everything lands under `asvs-audit/` in your repo root:

| Path | Commit? | What |
|---|---|---|
| `asvs-audit/reports/<run-date>/` | yes | the deliverable — one report per chapter + `rollup.html` |
| `asvs-audit/baseline.json` | yes | carry-forward verdicts for the next audit |
| `asvs-audit/state/` | no | transient resume state (gitignore) |

### Sample output — the rollup scorecard

`rollup.html` aggregates the chapters in scope into one leadership-facing view:

> **OWASP ASVS 4.0.3 — Level 2 Audit Rollup**
> Scope: V1, V3, V5, V7, V10 · Run at: 2026-08-01 14:56

| Chapter | Name | Assessed | Findings | Needs Review | Pass/Resolved |
|---|---|:---:|:---:|:---:|:---:|
| V1 | Architecture, Design and Threat Modeling | 38 | 1 | 36 | 1 |
| V3 | Session Management | 18 | 3 | 0 | 15 |
| V5 | Validation, Sanitization and Encoding | 30 | 2 | 5 | 23 |
| V7 | Error Handling and Logging | 12 | 3 | 2 | 7 |
| V10 | Malicious Code | 5 | 2 | 1 | 2 |
| **TOTAL** | | **103** | **11** | **44** | **48** |

- **Assessed** — requirements evaluated.
- **Findings** — failures that need remediation.
- **Needs Review** — items a human must confirm.
- **Pass/Resolved** — passed, or a prior failure now confirmed fixed.

Each chapter links to its detailed report, which leads with the findings to act
on (evidence, remediation, suggested owner) and collapses the passing items.

### Requirements

Python 3 runs the scripts. The reference stack is **Ruby on Rails + PostgreSQL**
(automated checks call [`brakeman`](https://brakemanscanner.org/) and
[`bundler-audit`](https://github.com/rubysec/bundler-audit)). On other stacks
those checks are skipped and the audit continues via code inspection; the HTTP
`headers` and `tls` checks work anywhere. See the
[skill README](.claude/skills/owasp-asvs-security/README.md) for retargeting.

> ASVS requirement text © OWASP Foundation, licensed CC BY-SA 3.0.


---

## owasp-top-10-reviewer

Read-only security review against **OWASP Top 10:2025** — the routine pass at
review time, where ASVS is the periodic deep sweep.

**Modes** — auto-selected from the input.

| Mode | Give it | You get |
|---|---|---|
| PR | a GitHub PR URL | inline comments + summary on the PR; changes requested on any Critical/High |
| Repo | a repo or directory | `owasp-review-<date>.md` |

**How it works** — three passes:

1. **Static** — Brakeman + bundler-audit, mapped to the 2025 categories.
2. **Inspection** — what tools can't see: missing authorization, IDOR, insecure
   design, auth logic flaws, unverified webhooks, fail-open rescues.
3. **Consolidate** — one category per finding, severity as exploitability ×
   impact.

Every tool signal is confirmed in the code before it's reported.

**Requirements** — a Rails project and Python 3. Brakeman + bundler-audit
recommended (`gem install brakeman bundler-audit`); without them it runs
inspection-only. PR mode needs the GitHub MCP server, plus a local checkout of
the branch to run the static tools.

See the [README](.claude/skills/owasp-top-10-reviewer/README.md).


---

## performance-auditor

Performance-only review of a **Rails/ActiveRecord + PostgreSQL** codebase —
scoped so it doesn't collide with a code or security review.

**Measure-first** — locate the bottleneck before prescribing a fix. Static hits
are hypotheses ranked by likely impact, not verdicts; a finding whose reach is
unknown is marked `needs-measurement` instead of a confident Critical.

**Modes**

| Mode | For | What it does |
|---|---|---|
| Review changes | a PR, diff, or branch | flags only what *this change* introduces or worsens |
| Audit codebase | a full sweep | seven categories in impact-per-effort order (`N+1 → Index → Caching → Jobs → Memory → Views → System`); checkpointed, so it resumes and diffs against the last run |
| Diagnose | one slow path | reproduce → isolate → identify → fix → verify → guard |

**Every finding carries eight fields** — `category · location · pattern · impact
· severity · confidence · fix · verify`. `checkpoint.py` rejects one that's
missing any of them: a finding without `verify` is a claim nobody can check.

**Requirements** — Python 3; ripgrep recommended (falls back to `grep`);
ideally a `pg_stat_statements` CSV export from production, which outranks any
grep. Output lands under `performance-review-report/` in the target repo.

See the [README](.claude/skills/performance-auditor/README.md).


---

## code-reviewer

General code-quality review of a **PR or diff** — correctness bugs and
reuse/simplification/efficiency cleanups, checked against the target repo's
own `.claude/rules/*.md` rather than generic taste. It's the skill the
security and performance reviewers point to when they say "leave general
correctness to a code-review skill" — and it returns the favor, flagging
security/performance leads in one line instead of analyzing them.

**Modes**

| Input | Mode |
|---|---|
| GitHub PR URL or number | inline comments + summary via the GitHub MCP server |
| Branch name, or nothing (uncommitted work) | diff against base, or the working-tree diff |

**Effort levels** — `low` / `medium` (default) / `high` / `max`, controlling how
much gets reported (not how carefully the diff is read); reuses whatever level
was last used if none is given.

**Flags** — `--comment` posts findings as inline PR comments; `--fix` applies
them to the working tree. Neither flag: read-only report, the default. Unlike
the three read-only reviewers above, this skill *can* write code — but only on
request, never by default.

**Requirements** — a Ruby on Rails project. PR mode needs the GitHub MCP
server; `--fix` needs a local checkout of the branch under review. See
[`SKILL.md`](.claude/skills/code-reviewer/SKILL.md) for the full workflow.
