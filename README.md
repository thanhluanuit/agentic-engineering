# agent-skills

AI agent skills and rules for software engineering workflows.

A **skill** is a self-contained package (instructions + scripts + data) that an
agent like Claude Code discovers and runs on demand. Drop one into a project and
the agent knows *when* to use it and *how* to run it.

A **rule** is a markdown instruction file the agent reads automatically — either
every session or only when it opens a matching file — to keep coding conventions
consistent without being asked.

## Structure

```
agent-skills/
├── CLAUDE.md                           # project instructions, loaded every session
└── .claude/
    ├── rules/                          # Rails engineering rules (auto-loaded)
    │   ├── principles.md               # always-on
    │   ├── technical_stack.md          # always-on (per-project template)
    │   ├── code_style.md               # loads on Ruby/Rails/frontend files
    │   ├── performance.md              # loads on models, jobs, migrations
    │   └── security.md                 # loads on app/config/db code
    └── skills/
        ├── owasp-asvs-security         # audit code against OWASP ASVS 4.0.3
        └── skill-creator               # scaffold, evaluate, and optimize new skills
```

| Skill | What it does |
|---|---|
| [`owasp‑asvs‑security`](.claude/skills/owasp-asvs-security) | Audits your code against OWASP ASVS 4.0.3 (Level 2), citing evidence for every finding. |
| [`skill-creator`](.claude/skills/skill-creator) | Scaffolds, refines, and optimizes skills, with evals to benchmark what works. |


---

## Rules

The [`.claude/rules/`](.claude/rules/) directory holds engineering conventions
that apply to every Rails project. They follow
[Claude Code's rules mechanism](https://code.claude.com/docs/en/memory): the
agent loads them into context on its own, so your code stays consistent without
you restating the standards each session. **Always-on** rules load every session
as baseline context; **path-scoped** rules carry `paths:` frontmatter and load
only when the agent opens a matching file, so they cost nothing until relevant.

| Rule | Loads | Covers |
|---|---|---|
| [`principles.md`](.claude/rules/principles.md) | Always-on | Core engineering values — the Rails Way, small reversible changes, fail loudly. Wins when a style rule conflicts. |
| [`technical_stack.md`](.claude/rules/technical_stack.md) | Always-on | Per-project stack template (Ruby/Rails versions, DB, jobs, frontend) to fill in and keep current. |
| [`code_style.md`](.claude/rules/code_style.md) | `*.rb`, `*.erb`, `app/**` | Ruby + Rails + frontend style; the conventions RuboCop and ERB Lint can't enforce on their own. |
| [`performance.md`](.claude/rules/performance.md) | models, jobs, migrations | N+1 queries, indexing, caching, background jobs, and safe migrations on live databases. |
| [`security.md`](.claude/rules/security.md) | `app/**`, `config/**`, `db/**` | Everyday secure-coding baseline; points to `owasp-asvs-security` for the periodic deep audit. |

Rules are guidance the agent *reads*, not configuration it *enforces*. For
guaranteed behavior use [hooks](https://code.claude.com/docs/en/hooks) or
[permissions](https://code.claude.com/docs/en/permissions).

**Using them in your own project** — copy `.claude/rules/` (and optionally
`CLAUDE.md`) into any Rails repo, then fill in `technical_stack.md`. The agent
picks them up automatically on the next session.


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
