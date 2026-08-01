# agent-skills

AI agent skills for software engineering workflows.

A skill is a self-contained package (instructions + scripts + data) that an
agent like Claude Code discovers and runs on demand. Drop one into a project and
the agent knows *when* to use it and *how* to run it.

## Structure

```
agent-skills/
└── .claude/
    └── skills/
        ├── owasp-asvs-security   # audit code against OWASP ASVS 4.0.3
        └── skill-creator         # scaffold, evaluate, and optimize new skills
```

| Skill | What it does                                                                                                                                   |
|---|------------------------------------------------------------------------------------------------------------------------------------------------|
| [`owasp-asvs-security`](.claude/skills/owasp-asvs-security) | Audits your code against OWASP ASVS 4.0.3 (Level 2) and produces evidence-backed findings plus a rollup — without changing the code it audits. |
| [`skill-creator`](.claude/skills/skill-creator) | Helps you build, refine, and benchmark new skills.                                                                                             |


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
