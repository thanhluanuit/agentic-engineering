---
paths:
  - "spec/**"
  - "test/**"
---

# Testing

Testing is enforced by the runner (RSpec or Minitest — see
[`technical_stack.md`](technical_stack.md) for which one this project uses)
and coverage tooling; these rules capture the conventions the runner can't
enforce.

## Coverage & intent

- Every change ships with a test that fails without it — a suite that only
  documents happy paths misses regressions before a user does.
- Test behavior, not implementation. Assert on the public interface (return
  value, state change, response) — not on private methods or instance
  variables. A test that breaks on refactor without a real behavior change is
  a maintenance cost, not a safety net.
- Don't write a test for framework behavior you didn't write — a bare
  `validates :email, presence: true` doesn't need its own spec proving Rails'
  validation works. Test validations that carry real conditional or custom
  logic.

## Test types

- **Model specs** for business logic: scopes, custom validations, callbacks,
  instance/class methods — not a dumping ground for controller-level
  assertions.
- **Request specs over controller specs** — a request spec exercises routing,
  params, authentication, and the real response in one pass; controller specs
  are legacy and Rails no longer generates them by default.
- **System specs** (Capybara) sparingly, for the critical user flows only —
  they're the slowest and most flake-prone layer. Don't chase feature-complete
  coverage there; that's what the faster layers are for.
- Security-relevant paths need their own coverage, not just the happy path —
  see [`security.md`](security.md)'s authorization-testing note (assert a
  non-owner gets `403`/`404`) and, for any change touching queries,
  [`performance.md`](performance.md)'s query-count assertion pattern
  (`assert_queries`) to lock in an N+1 fix.

## Data & isolation

- **Factories over fixtures** for new test data (if the project uses
  FactoryBot — see `technical_stack.md`). Keep factories minimal: only the
  attributes required to be valid; model variations as traits, not new
  factories.
- Avoid factory callbacks and associations that silently create more records
  than the test needs — they slow the suite and hide what a test actually
  depends on.
- Each example must be independent: no shared mutable state across examples,
  no reliance on run order. Keep random-order execution on (RSpec's default)
  — it's what surfaces order-dependent bugs before CI does.
- Never call a real third-party API in a test — stub outbound HTTP with
  WebMock/VCR. Never `sleep` to wait on async behavior; use the job adapter's
  test helpers (`perform_enqueued_jobs`) or poll with a timeout.
- Freeze or travel time (`freeze_time` / `travel_to`) for anything
  time-sensitive instead of stubbing `Time.now`/`Date.today` directly —
  matches the zone-aware `Time.current` convention in
  [`code_style.md`](code_style.md).

## Structure & maintenance

- One behavior per example; keep `describe`/`context` nesting shallow enough
  to read as a sentence. A context you can't name in one phrase is testing too
  much at once.
- Reach for `shared_examples` only after the same behavior is genuinely
  duplicated across specs — the "duplicate twice before abstracting" rule
  from [`principles.md`](principles.md) applies here too; a shared example
  built too early usually ends up parameterized past readability.
- A flaky test is a bug, not noise — fix it or explicitly quarantine it
  (skip, tagged and tracked), never leave it randomly red in CI where it
  trains reviewers to ignore failures.

## Speed

- Push slow setup (large fixture graphs, full-stack system specs) to the
  minimum layer that actually needs it — model and request specs should
  dominate the suite by count, system specs the minority.
- Run tests in parallel (Rails' built-in test parallelization, or
  `parallel_tests`) once the suite is slow enough to matter — don't add it
  speculatively before it does.
