---
paths:
  - "**/*.rb"
  - "app/models/**"
  - "app/jobs/**"
  - "app/controllers/**"
  - "db/migrate/**"
---

# Performance Optimization

Measure before optimizing. Reach for these rules by default; profile before doing
anything exotic.

## Database is the first place to look

- **Kill N+1 queries.** Use `includes` / `preload` / `eager_load` for associations
  you'll render. Add the [`bullet`](https://github.com/flyerhzm/bullet) gem in
  development to catch them.
- **Index what you query and join.** Every foreign key, every column in a `WHERE`,
  `ORDER BY`, or `JOIN`. Unique indexes back uniqueness validations.
- **Select only what you need**: `select(:id, :name)`, `pluck` for single columns,
  `pick` for a single row. Don't instantiate full AR objects to read one field.
- **Batch large iterations** with `find_each` / `in_batches` — never load a huge
  table into memory with `.all.each`.
- **Avoid queries in loops.** Load the set once, then work in Ruby, or use a
  single aggregate query (`group`, `count`, `sum`).
- **Use `exists?`** instead of `present?`/`any?` when you only need existence.
- **`counter_cache`** for association counts you display often.

## Migrations on live databases

- Adding an index on a large table: use `algorithm: :concurrently` (and
  `disable_ddl_transaction!`).
- Adding a `NOT NULL` column: add nullable + backfill in batches + then enforce.
- Never do heavy backfills inside a schema migration on a big table — use a
  separate data task or job.

## Caching

- **Fragment / Russian-doll caching** for expensive view partials, keyed on the
  record so it expires automatically.
- **`Rails.cache`** for expensive computed values; always set an expiry.
- **HTTP caching** (`fresh_when` / `stale?`) for cacheable controller actions.
- Cache the result, not the bug — never cache around a correctness problem.

## Background work

- Move anything slow or external (email, third-party APIs, image processing,
  bulk writes) into a background job.
- Jobs must be **idempotent** and take **IDs, not serialized objects**, as
  arguments.
- Set sensible retry/backoff; make failures visible in error tracking.

## Application & assets

- Avoid loading giant object graphs into memory; paginate list endpoints.
- Serialize APIs efficiently (`jbuilder` with care, or a fast serializer);
  don't render associations you don't return.
- Precompile and fingerprint assets; serve them via CDN in production.
- Set reasonable Puma worker/thread counts for the host; don't guess in prod.

## Before you optimize

1. Reproduce and **measure** (logs, `rack-mini-profiler`, APM, `EXPLAIN ANALYZE`).
2. Fix the biggest cost first — usually the database.
3. Re-measure to confirm the win. Keep the benchmark in the PR description.
