---
paths:
  - "**/*.rb"
  - "**/*.erb"
  - "**/*.rake"
  - "app/**"
  - "lib/**"
  - "config/**"
  - "Gemfile"
---

# Code Style Guide (Ruby + Rails + Frontend)

Style is enforced by tooling first. Run **RuboCop** (`rubocop-rails`,
`rubocop-performance`) and **ERB Lint**; the rules below capture the intent and
the things linters can't catch. When in doubt, match the surrounding file.

## Ruby

- **Two-space indent**, no tabs. Max line length ~100–120 (match the project's
  RuboCop config).
- Use `frozen_string_literal: true` magic comment on new files.
- Prefer `&&`/`||` over `and`/`or` (different precedence — `and`/`or` cause bugs).
- Guard clauses over nested conditionals:
  ```ruby
  return unless user.active?
  # happy path here
  ```
- Prefer `each`, `map`, `select`, `reduce` over manual loops. No mutation inside
  a `map`.
- Use keyword arguments for methods with more than one argument or any boolean.
- Small methods (aim < 10 lines) with a single responsibility. Extract private
  methods freely.
- Use `%i[]` / `%w[]` for symbol and word arrays.
- String interpolation over concatenation; double quotes by project convention.

## Rails

- **Naming**: models singular (`User`), tables plural (`users`), controllers
  plural (`UsersController`). Follow it exactly — Rails relies on it.
- **Query in the model, not the view or controller.** Expose named scopes:
  ```ruby
  scope :active, -> { where(archived_at: nil) }
  ```
- **Always guard against N+1**: use `includes`/`preload`/`eager_load`. See
  [`performance.md`](performance.md).
- **Strong parameters** in every controller — never `permit!`. See
  [`security.md`](security.md).
- **Enums** for status-like columns; back them with a DB default and constraint.
- **Callbacks sparingly** — they create hidden coupling and slow tests. Prefer
  explicit service calls for anything with side effects (emails, jobs, external
  APIs).
- **Migrations**: one concern per migration, reversible, with the right indexes.
  Add `NOT NULL` and foreign keys at the DB level.
- **Time**: always `Time.current` / `Date.current` (zone-aware), never
  `Time.now`.
- **Money**: integer cents or a dedicated type — never floats.
- **I18n**: user-facing strings go through `t(...)`, not hard-coded.

## Frontend (Hotwire / ERB / JS)

- **Prefer server-rendered HTML + Hotwire** (Turbo Frames/Streams, Stimulus)
  before reaching for a SPA framework.
- **No logic in ERB** beyond simple presentation. Extract to helpers,
  presenters, or ViewComponents. Never run queries in a view.
- **Escape by default.** Only use `raw`/`html_safe` on content you constructed
  and trust; sanitize anything user-derived. See [`security.md`](security.md).
- **Stimulus controllers** are small and focused; name data attributes by intent
  (`data-controller`, `data-action`, `data-*-target`).
- **JavaScript**: no inline `<script>` handlers; use `const`/`let` (never `var`);
  keep DOM lookups scoped to the Stimulus controller's element.
- **CSS**: follow the project's system (Tailwind utility-first, or BEM for custom
  CSS). No inline styles for anything reusable.
- **Accessibility**: semantic elements, `alt` text, labels tied to inputs,
  keyboard-navigable interactions.

## Comments & docs

- Comment the *why*, not the *what*. Delete commented-out code — git remembers.
- A public method with non-obvious behavior gets a one-line doc comment.
- Match the file's existing comment density; don't over-annotate.
