# Principles

The non-negotiable engineering values for every Rails project. When a specific
style rule and a principle conflict, the principle wins.

## The Rails Way first

- Prefer built-in Rails idioms over custom abstractions. Reach for a gem or a
  service object only when the framework genuinely doesn't cover the case.
- Convention over configuration. Follow Rails' naming and directory conventions
  so the code is predictable to any Rails developer.

## Fat models, skinny controllers — but not obese models

- Controllers orchestrate: authenticate, authorize, call one domain method,
  render. No business logic.
- Push behavior into models, but when a model grows past its single
  responsibility, extract concerns, POROs, or service objects — don't let it
  become a god object.
- Views contain no logic beyond presentation. Use helpers, presenters, or
  ViewComponents.

## Explicit over clever

- Optimize for the reader. Code is read far more than it's written.
- Name things for intent, not implementation. A method name should let a reader
  skip its body.
- Avoid metaprogramming unless it removes real, repeated boilerplate and stays
  greppable.

## Small, reversible changes

- Prefer many small PRs over one large one. Each PR does one thing.
- Every change is covered by a test that would fail without it.
- Migrations are reversible (`change` or paired `up`/`down`) and safe to run on
  a live database (see [`performance.md`](performance.md)).

## Fail loudly, recover deliberately

- Don't rescue `Exception` or swallow errors. Rescue the narrowest class you can
  handle, and let the rest surface to error tracking.
- Validate at the boundary (params, model validations, DB constraints) rather
  than trusting callers.

## Security and correctness are not optional

- Never trade a security control for convenience. See [`security.md`](security.md).
- Data integrity lives in the database (foreign keys, `NOT NULL`, unique
  indexes), not only in model validations.

## Leave it better

- Boy-scout rule: touch a file, tidy what you reasonably can within the PR's
  scope — without turning a bugfix into a refactor.
