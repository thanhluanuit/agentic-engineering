# Technical Stack

> **Template.** Stack details are per-project. Fill in the blanks below when you
> drop this folder into a Rails app, and keep it current — the rest of the rules
> assume this file is accurate.

## Runtime

- **Ruby**: `<x.y.z>` (pin in `.ruby-version` and `Gemfile`)
- **Rails**: `<x.y>`
- **Package manager**: Bundler `<version>`

## Data

- **Primary database**: `<PostgreSQL x / MySQL x>`
- **Cache / sessions**: `<Redis / Memcached / Solid Cache>`
- **Background jobs**: `<Sidekiq / GoodJob / Solid Queue>` on `<Redis / DB>`
- **Search**: `<none / Elasticsearch / pg_search>`

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
- **Ruby app server**: `<Puma>`
- **Env / secrets**: Rails credentials or `<Vault / SSM>` — never committed `.env`

## Conventions for keeping this file honest

- Bump the versions here in the same PR that bumps them in `Gemfile.lock`.
- If a listed tool is removed, remove it here too — a stale stack doc is worse
  than none.
