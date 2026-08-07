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

Day-to-day secure-coding rules for every Rails project — the habits that
prevent the common vulnerabilities during development. Self-contained: read
top to bottom for the baseline, no skill required to get value from it.
Prioritized from the [Rails Security
Guide](https://guides.rubyonrails.org/security.html), the [Rails Security
Checklist](https://github.com/eliotsykes/rails-security-checklist), and OWASP
Top 10, in that order where they disagree.

> For a full, evidence-backed audit against **OWASP ASVS 4.0.3 (Level 2)** —
> chapter by chapter with findings and a rollup — use the
> [`owasp-asvs-security`](../skills/owasp-asvs-security) skill. This file
> is the everyday coding baseline; that skill is the periodic deep review.

## Input & mass assignment

- **Strong parameters everywhere.** Whitelist with `params.require(...).permit(...)`.
  Never `permit!`, never pass raw `params` to `create`/`update`.
- Validate and coerce untrusted input at the boundary; don't trust client data,
  hidden fields, or JS-side validation alone — assume every request is
  hand-crafted, not sent by your own form.
- **Prefer allow-lists over blocklists** everywhere you sanitize or validate:
  reject input that doesn't match the expected shape rather than trying to
  strip the bad parts out of it.
- **Anchor regex validators with `\A`/`\z`, never `^`/`$`.** In Ruby, `^`/`$`
  match *line* boundaries, not string boundaries, so `^`/`$` let
  `"good@x.com\nmalicious"` slip past a check that looks airtight. Rails'
  `format:` validator raises if it sees `^`/`$` for exactly this reason.

## SQL injection

- Use parameterized queries and hash conditions: `where(email: params[:email])`.
  Never interpolate params into a SQL string.
- If you must write raw SQL, use bind parameters (`where("age > ?", n)`), never
  `"age > #{n}"`. For fragments assembled outside a model, use
  `sanitize_sql_array` / `sanitize_sql`.
- **A parameterized `LIKE` is still exploitable at the pattern level.**
  `where("name LIKE ?", "%#{q}%")` is SQLi-safe but lets `q` inject `%`/`_`
  wildcards, turning a lookup into a full scan. Wrap the term in
  `sanitize_sql_like(q)` before interpolating it into the pattern.

## XSS & output encoding

- Rails escapes by default — keep it that way. Only `raw` / `html_safe` on
  content you built and trust; run user content through `sanitize` with an
  explicit tag/attribute allowlist.
- Never build HTML by string concatenation with user data.
- For user-authored rich text or Markdown, use an allowlist renderer
  (`Redcarpet::Render::Safe`, not `::HTML`) — never render raw HTML sourced
  from user content.

## Redirects & host safety

- **Never pass user input straight to `redirect_to`.** Allow-list the valid
  destinations rather than trying to regex-validate an arbitrary URL — that's
  a bypass waiting to be found.
- Rails ≥ 7 blocks unsafe `redirect_to(external_url)` by default
  (`raise_on_open_redirects`) — confirm that framework default is actually
  enabled on an upgraded app, and never pass `allow_other_host: true` with
  user-controlled input.
- Keep `ActionDispatch::HostAuthorization` on (`config.hosts`) so a forged
  `Host` header can't be reflected into links, password-reset emails, or
  cache keys.

## Authentication & sessions

- Use a vetted solution (Devise, Rails 8's `authenticate_by` + generator, or
  `has_secure_password`) — don't roll your own password hashing. Use bcrypt's
  (or argon2's) built-in cost/workload factor, and increase it as hardware
  gets faster — put a recurring reminder on this, it's not a one-time setting.
- Cookies: `httponly`, `secure`, `same_site: :lax` (or stricter). Call
  `reset_session` on login **and** logout to prevent session fixation.
- Don't store sensitive or large data in the session — `CookieStore` is
  client-held (encrypted, but still leaves the browser) and capped at 4KB;
  put anything sensitive or sizable in the database, keyed by the session id.
- **Mitigate user enumeration**: login and password-reset responses must not
  reveal whether an account exists ("incorrect username or password", not
  "no such user"). Devise needs `paranoid` mode for this — it isn't automatic.
- **Timing-safe comparison** for tokens/secrets:
  `ActiveSupport::SecurityUtils.secure_compare`, never `token == params[:token]`.
  Look tokens up by an indexed identifier, not by querying the DB with the
  secret itself.
- Rate-limit and lock out: throttle login, password-reset, and OTP endpoints
  (Rails 8's `rate_limit` class macro, or `rack-attack`); lock the account
  after repeated failures; offer MFA for privileged or financial accounts.
- Require the current password to change the password, and re-authentication
  (or at least the current password) to change the account email — and
  notify the user by email when either happens.

## Authorization

- Enforce access control on **every** action — never rely on hidden UI.
  Authentication is not authorization: `authenticate_user!` alone doesn't gate
  per-object access.
- Use Pundit or CanCanCan; scope every query to the current user
  (`current_user.projects.find(params[:id])`), never `Project.find(params[:id])`
  for user-owned data (prevents IDOR).
- **Multi-tenant apps**: scope every query through the tenant, not just the
  user. A `default_scope` alone is not a substitute for explicit scoping at
  each query site — it's silently bypassed by `unscoped`, raw SQL, and joins.
- Cover authorization with tests, not just the happy path: a request spec
  asserting a non-owner gets `403`/`404` catches a missing `authorize` call
  that a feature test for the owner's flow never will.

## CSRF & headers

- Keep `protect_from_forgery with: :exception` on for HTML forms; include
  `csrf_meta_tags` in the layout so Turbo/AJAX requests carry the token.
- Force TLS in production (`config.force_ssl = true`) — this also enables
  HSTS.
- Rails already sends `X-Frame-Options`, `X-Content-Type-Options`, and
  `Referrer-Policy` by default — **Content-Security-Policy is not one of
  them.** Define one in `config/initializers/content_security_policy.rb`, or
  use the `secure_headers` gem if you need finer control.

## Fail closed on errors

- Don't rescue `Exception`, and don't write `rescue nil` / `rescue => e; end`
  around an authentication, authorization, or payment check — a swallowed
  error there means the request silently proceeds as if it had passed.
- On error in a security decision, **deny by default**; rescue the narrowest
  class you can actually handle and let the rest surface to error tracking.
- Wrap multi-step mutations (payments, balance changes, anything with an
  invariant) in a transaction with rollback, and back the invariant with a DB
  constraint, not just an app-level check — a race condition doesn't care
  what your Ruby code assumed.

## Secrets & config

- No secrets in the repo. Use Rails credentials (`bin/rails credentials:edit`)
  or a secrets manager; keep `.env` out of git.
- Rotate credentials on exposure — rotating `secret_key_base` invalidates all
  existing sessions, which is the point. Scope API keys least-privilege.
- Different secrets per environment, including staging/demo — never reuse a
  production secret there. Staging shouldn't hold real user data; scrub or
  synthesize it, and gate the environment behind IP allow-listing or HTTP
  basic auth if it's reachable from the internet.

## Dependencies & scanning (run in CI)

- **Brakeman** — static analysis for Rails vulnerabilities.
- **bundler-audit** — flags gems with known CVEs; keep its advisory DB
  updated (`bundle audit check --update`).
- **Dependabot** / `bundle outdated` — keep dependencies patched. Keep
  non-essential gems in the `development`/`test` group, not production.
- Fail the build on new high-severity findings.

## Data protection & logging

- Filter sensitive params from logs (`config.filter_parameters`): passwords,
  tokens, PII, card data. Rails filters `:passw`, `:secret`, `:token` by
  default — extend the list, don't assume it already covers your domain.
- Log security-relevant events with actor + outcome (login failures,
  authorization denials, privilege changes) so an incident is investigable
  after the fact — a log nobody can query during an incident isn't a control.
- Encrypt sensitive columns at rest (Active Record Encryption) where
  warranted. Never log credentials, tokens, or full PII.

## File uploads & external requests

- Validate upload content type and size; store outside the web root / on
  object storage; never trust the filename — sanitize it or name the file by
  its database id instead.
- Scan uploads for malware before they're served to other users, and process
  images/PDFs in a background job (see [`performance.md`](performance.md)),
  not synchronously on the request path.
- Guard against SSRF: resolve and validate the destination host, not just its
  string form — an allow-listed host that redirects, or that resolves
  differently on a second lookup (DNS rebinding), still reaches an internal
  address. Don't fetch user-supplied URLs blindly.
- **Verify inbound webhook signatures** (Stripe, GitHub, Twilio, etc.) with
  `ActiveSupport::SecurityUtils.secure_compare` against the computed HMAC
  before acting on the payload — an unverified webhook endpoint is an
  unauthenticated write.
