---
paths:
  - "**/*.rb"
  - "**/*.erb"
  - "app/**"
  - "config/**"
  - "db/**"
  - "Gemfile"
---

# Security

Day-to-day secure-coding rules for every Rails project. These are the habits
that prevent the common vulnerabilities during development.

> For a full, evidence-backed audit against **OWASP ASVS 4.0.3 (Level 2)** —
> chapter by chapter with findings and a rollup — use the
> [`owasp-asvs-security`](../skills/owasp-asvs-security) skill. This file
> is the everyday coding baseline; that skill is the periodic deep review.

## Input & mass assignment

- **Strong parameters everywhere.** Whitelist with `params.require(...).permit(...)`.
  Never `permit!`, never pass raw `params` to `create`/`update`.
- Validate and coerce untrusted input at the boundary; don't trust client data.

## SQL injection

- Use parameterized queries and hash conditions:
  `where(email: params[:email])`. Never interpolate params into a SQL string.
- If you must write raw SQL, use bind parameters (`where("age > ?", n)`), never
  `"age > #{n}"`.

## XSS & output encoding

- Rails escapes by default — keep it that way. Only `raw` / `html_safe` on
  content you built and trust; run user content through `sanitize` with an
  allowlist.
- Never build HTML by string concatenation with user data.

## Authentication & sessions

- Use a vetted solution (Devise, Rails 8 built-in auth, or `has_secure_password`)
  — don't roll your own password hashing.
- Cookies: `httponly`, `secure`, `same_site: :lax` (or stricter). Reset the
  session on login/logout (`reset_session`) to prevent fixation.
- Enforce strong password storage (bcrypt/argon2); support MFA where it matters.

## Authorization

- Enforce access control on **every** action — never rely on hidden UI.
- Use Pundit or CanCanCan; scope every query to the current user
  (`current_user.projects.find(...)`), never `Project.find(params[:id])` for
  user-owned data (prevents IDOR).

## CSRF & headers

- Keep `protect_from_forgery` / Rails' default CSRF protection on for HTML forms.
- Force TLS in production (`config.force_ssl = true`).
- Set security headers (CSP, `X-Content-Type-Options`, `X-Frame-Options` /
  frame-ancestors, HSTS). Consider the `secure_headers` gem.

## Secrets & config

- No secrets in the repo. Use Rails credentials or a secrets manager; keep
  `.env` out of git.
- Rotate credentials on exposure; scope API keys least-privilege.
- Different secrets per environment.

## Dependencies & scanning (run in CI)

- **Brakeman** — static analysis for Rails vulnerabilities.
- **bundler-audit** — flags gems with known CVEs.
- **Dependabot / `bundle outdated`** — keep dependencies patched.
- Fail the build on new high-severity findings.

## Data protection & logging

- Filter sensitive params from logs (`config.filter_parameters`): passwords,
  tokens, PII, card data.
- Encrypt sensitive columns at rest (Active Record Encryption) where warranted.
- Never log credentials, tokens, or full PII.

## File uploads & external requests

- Validate upload content type and size; store outside the web root / on object
  storage; never trust the filename.
- Guard against SSRF: validate and allowlist outbound URLs; don't fetch
  user-supplied URLs blindly.
