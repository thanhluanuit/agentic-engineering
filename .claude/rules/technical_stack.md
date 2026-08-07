# Technical Stack

> **Template.** Stack details are per-project. Fill in the blanks below when you
> drop this folder into a Rails app, and keep it current.
>
> - **Lockfiles win.** If this file and `Gemfile.lock` / `package.json` ever
>   disagree, trust the lockfile and fix this file — don't act on stale info here.
> - **Unfilled means undocumented, not zero.** A field still showing
>   `<placeholder>` text has not been recorded — read `Gemfile.lock`,
>   `.ruby-version`, or the relevant config directly rather than guessing or
>   repeating the placeholder back as if it were a real value.

## Runtime

- **Ruby**: `<x.y.z>` (pin in `.ruby-version` and `Gemfile`)
- **Rails**: `<x.y.z>` (patch matters for CVE/version-gated checks)
- **Package manager**: Bundler `<version>`

## Data

- **Primary database**: `<PostgreSQL x / MySQL x>`
- **Cache / sessions**: `<Redis / Memcached / Solid Cache>`
- **Background jobs**: `<Sidekiq / GoodJob / Solid Queue>` on `<Redis / DB>`
  (Sidekiq → Redis; GoodJob/Solid Queue → DB — keep the pairing valid)
- **Search**: `<none / Elasticsearch / pg_search>`

## Application

- **Authentication**: `<Devise / Rails 8 built-in auth / has_secure_password>`
- **Authorization**: `<Pundit / CanCanCan>`
- **Multi-tenancy**: `<none / row-scoped / schema-per-tenant / other>` — if
  tenanted, cross-tenant isolation is usually the highest real security risk;
  say so explicitly here so it isn't missed.

## Frontend

- **Rendering**: `<Hotwire (Turbo + Stimulus) / ViewComponent / React via Inertia>`
- **Asset pipeline**: `<Propshaft / Sprockets / jsbundling + esbuild>`
- **CSS**: `<Tailwind / Sass / vanilla>`

## Testing & quality

- **Test framework**: `<RSpec / Minitest>`
- **Factories / fixtures**: `<FactoryBot / fixtures>`
- **Linters**: RuboCop (with `rubocop-rails`, `rubocop-performance`), ERB Lint
- **Security scanners**: Brakeman, bundler-audit (see [`security.md`](security.md))

## Infrastructure

- **Deploy**: `<Kamal / Heroku / Fly.io / K8s>`
- **CI**: `<GitHub Actions / GitLab CI>`
- **Ruby app server**: Puma (note here if something else, e.g. `<Unicorn / Passenger>`)
- **Env / secrets**: Rails credentials or `<Vault / SSM>` — never committed `.env`
- **Error tracking / APM**: `<Sentry / Honeybadger / Datadog / Skylight / none>`

## Conventions for keeping this file honest

- Bump the versions here in the same PR that bumps them in `Gemfile.lock`.
- If a listed tool is removed, remove it here too — a stale stack doc is worse
  than none.
