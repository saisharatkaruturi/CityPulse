# Your City, Your Services — backend

> "Help residents report local issues and find the right municipal service, with better routing and clearer updates."

A backend-first civic issue platform. Residents report problems (potholes, garbage, leaks, drains, streetlights),
find the right municipal service, and track a transparent, database-backed timeline. Officers triage and
resolve work, and administrators configure departments, categories, routing, and service targets.

**All demo data is fictional.** No real municipality is contacted. External integrations are either disabled
or clearly labelled **SIMULATED** mocks.

---

## Quick start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                  # install deps (+ dev tools)
cp .env.example .env                     # optional; defaults work for local dev
uv run python -m app.cli migrate         # create/upgrade the SQLite DB at ./var/ycys.db
uv run python -m app.cli seed            # fictional demo data (repeatable)
uv run uvicorn app.main:app --reload     # API on http://127.0.0.1:8000, docs at /docs
uv run python -m app.cli worker          # background jobs (separate terminal); --once for a single pass
```

| Command | Purpose |
|---|---|
| `python -m app.cli migrate` | `alembic upgrade head` using `DATABASE_URL` |
| `python -m app.cli seed` | Upsert reference data and create demo complaints once. Refuses in production. |
| `python -m app.cli reset-demo --yes` | Drop everything, migrate, and seed. Refuses in production. |
| `python -m app.cli worker [--once]` | Outbox delivery, notification delivery, SLA reminders/escalation, auto-close, external sync, orphan-upload cleanup |
| `ADMIN_PASSWORD=... python -m app.cli create-admin --email you@org` | Bootstrap a real system admin (password from the environment, never argv) |
| `uv run pytest` | Full test suite |
| `uv run ruff check app tests alembic` / `uv run mypy app` | Lint and type checks |

Migrations never run automatically on app startup.

### Demo accounts (development only)

Every account is `<handle>@example.com` with password `DEMO_PASSWORD` (default `demo-password-123`).

| Handle | Role |
|---|---|
| `resident1`, `resident2`, `resident3` | resident |
| `roads.officer1`, `roads.officer2`, `sanitation.officer`, `water.officer`, `drainage.officer`, `lighting.officer` | field officer (team member) |
| `triage.supervisor`, `roads.supervisor`, `sanitation.supervisor`, `water.supervisor`, `drainage.supervisor`, `lighting.supervisor` | supervisor (department-scoped) |
| `muni.admin` | municipal administrator |
| `admin` | system administrator |
| `auditor` | read-only auditor |

The seed creates fictional departments (Triage, Roads, Sanitation, Water Supply, Drainage, Street Lighting),
6 teams, 4 **fictional** grid wards (`demo-w1`…`demo-w4`, not real boundaries), 14 categories (Telugu demo
labels, not reviewed by a native speaker), 6 routing rules, 4 **illustrative** SLA policies, and 7 services.
It also creates 11 complaints across statuses: in progress, resolved with evidence, closed with feedback,
an unmapped category, an uncategorised report, a public duplicate pair, an overdue drain (its `created_at`
is backdated by the seed and labelled as such), rejected, and withdrawn.

---

## Architecture

A modular monolith using FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, and SQLite (PostgreSQL-compatible).

```
app/
  main.py              app factory, middleware (request ID, size limit, security headers, access log), /health, /ready
  cli.py, seed.py      operational commands, demo data
  core/                config (typed, validated), errors (envelope), logging (JSON + redaction),
                       security (argon2, JWT), permissions (RBAC + row scope), ratelimit, time
  db/                  declarative base, UTC datetime type, engine/session
  domain/              PURE rules: workflow state machine, routing decision, priority, SLA math, geo, enums
  models/              persistence (33 tables)
  schemas/             explicit request/response models (request bodies forbid unknown fields)
  services/            use cases: complaints, routing, sla, intelligence, duplicates, media, notifications,
                       outbox, analytics, admin, audit, views (response shaping)
  adapters/            provider interfaces + implementations: classifier, email/SMS, municipal, geocoder, storage
  jobs/worker.py       background jobs
  api/routers/         thin HTTP handlers
alembic/               versioned migrations
tests/                 177 tests (unit, integration, API, end to end)
```

HTTP handlers parse input, call one service function, and shape output. Business rules live in `domain/` and
`services/`. Routing and workflow logic each exist in exactly one place.

### Data model (main relationships)

`users` ↔ `user_roles` (role + optional department/ward scope) · `auth_sessions` (revocable tokens) ·
`departments` (one or more `is_fallback` triage queues) ↔ `department_ward_coverage` ↔ `wards` ·
`teams` ⟶ department · `officers` ⟶ user, department, team, supervisor ·
`categories` (two levels, synonyms, i18n labels, default priority) ·
`services` ↔ departments, categories (draft/published/unavailable/unpublished) ·
`routing_rules` and `sla_policies` (versioned: `version`, `supersedes_id`, effective dates) ·
`complaints` ⟶ reporter, category (resident-reported and current), ward, department, team, officer, routing rule,
SLA policy (+version), `merged_into_id` · child tables: `complaint_status_history`, `complaint_assignments`,
`complaint_category_changes`, `complaint_priority_changes`, `complaint_comments`, `complaint_internal_notes`,
`complaint_media`, `complaint_links`, `complaint_supporters`, `feedback`, `escalation_history`,
`ai_classifications` · platform: `notifications`, `notification_preferences`, `outbox_events`,
`idempotency_records`, `audit_logs`, `announcements`.

* Primary keys are UUIDs. The public reference (`YCS-XXXXXXXX`, 8 random chars from a 30-symbol alphabet) is
  separate, DB-unique, and retried on collision. It is a tracking label, never an access secret: every read is
  authorised.
* Timestamps are timezone-aware UTC (`UTCDateTime` type). `created_at` is creation time; `updated_at` is the last
  row change; `resolved_at` is the latest time staff marked a case resolved; `closed_at` is closure;
  `due_at` is the SLA resolution target.
* `complaints.version` provides optimistic locking (SQLAlchemy `version_id_col` plus `If-Match`). Stale writes
  return `409 stale_version`.
* History is never cascade-deleted. Departments, officers, categories, rules, and policies are deactivated,
  not deleted.

---

## Roles and permissions

Deny by default. The role→permission matrix and row-scope predicates live in `app/core/permissions.py`, and
scope is applied **inside SQL queries**.

| Capability | resident | field_officer | supervisor | municipal_admin | system_admin | auditor |
|---|---|---|---|---|---|---|
| Create complaint | ✓ | ✓ | ✓ | ✓ | ✓ | |
| Read own reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Read others' complaints | public summary only | assigned + own team | own departments | all | all | all (read-only) |
| Transition / comment / resolve | own: withdraw, reopen, confirm | in scope | in scope | all | all | |
| Assign / reassign / merge / re-prioritise / recategorise | | | own departments | all | all | |
| Internal notes | never | in scope | in scope | all | all | read |
| Analytics | | | own departments | all | all | all |
| CSV export | | | | ✓ | ✓ | ✓ |
| Configure departments, categories, services, rules, SLA, announcements | | | | ✓ | ✓ | |
| Grant/revoke roles, deactivate users, ops outbox | | | | | ✓ | |
| Audit log | | | | | ✓ | ✓ |

A complaint the caller cannot see returns **404**, so its existence isn't confirmed. Status, department,
assignment, priority, timestamps, and reporter are never accepted from residents; request bodies reject
unknown fields.

## Complaint state machine (`app/domain/workflow.py`)

```
submitted ─┬─> under_review ─┬─> assigned ─> in_progress ─> resolved ─> closed
           │                 │      │  ▲          │  ▲          │  ▲       │
           └─> assigned      │      ▼  │          ▼  │          ▼  │       ▼
                             └> awaiting_resident / on_hold      reopened <┘
any open state ─> rejected (staff, reason) | withdrawn (reporter or staff)
```

* Reasons are required for `rejected`, `on_hold`, `awaiting_resident`, `reopened`, and system closure.
* **Resolved ≠ closed.** `resolved` means staff marked the work done, which is *not* independent verification.
  `closed` happens when the reporter confirms (feedback with `confirm_resolved`), staff close it, or the worker
  auto-closes after `AUTO_CLOSE_RESOLVED_AFTER_DAYS` (7) without a reopen.
* A reporter may reopen within `REOPEN_WINDOW_DAYS` (14) of resolution; staff may reopen anytime.
* Staff commenting with `request_information=true` → `awaiting_resident`. The resident's reply automatically
  returns the case to `in_progress` (if an officer is assigned) or `under_review`.
* Merge closes the duplicate with system closure and a link; the reporter keeps access to their original report.
* Status, history row, audit entry, and outbox event are written in **one transaction**.

The resident-facing `progress` object distinguishes **received locally → routed to a department queue →
acknowledged by staff → externally acknowledged (only if a provider confirmed; flagged if simulated) → marked
resolved → confirmed by resident**.

## Routing (`app/domain/routing.py`, `app/services/routing.py`)

1. **Jurisdiction:** a manually selected ward wins (no-GPS fallback). Otherwise coordinates are matched against
   configured ward polygons. A point outside every configured boundary is `out_of_area`. With no boundary data,
   jurisdiction is unknown, not guessed. Reverse geocoding is never used as proof.
2. **Candidates:** active rules within their effective window whose category equals the complaint's category or
   its parent, whose ward matches or is null, whose department is active, and whose department coverage (if
   any) includes the ward.
3. **Precedence:** exact category > parent category, then ward-specific > any ward, then lower `precedence`.
   If the best candidates still disagree on the department, the outcome is `conflicting_rules`.
4. **Fallback:** an unknown or triage category, no match, an inactive department, a conflict, or out of area
   all go to the **triage queue** (`is_fallback` department) with a `reason_code`. A department is never invented.
5. The decision (rule ID, explanation, reason code, jurisdiction method) is stored. `initial_routing` is
   immutable; later reroutes and manual (re)assignments are rows in `complaint_assignments`.
6. A staff category correction re-evaluates routing (`reroute=true`) and records `complaint_category_changes`.

## Priority

Deterministic and illustrative: start from the category default, and raise one level (capped at `high`) when the
resident reports a safety risk on a safety-sensitive category. **`critical` is never automatic.** Only
supervisors/admins can set it, with a reason, recorded in `complaint_priority_changes`. Text keywords never
change priority. `high` and `critical` priorities alert department supervisors. Every suggestion response
carries an emergency notice: this service does not dispatch emergency help (112 in India).

## SLA (`app/domain/sla.py`, `app/services/sla.py`)

* The policy is selected by specificity (category > department > priority > newest), and the complaint
  stores `sla_policy_id` + `sla_policy_version`. Seeded policies are flagged `is_illustrative`. **They are not
  official guarantees.**
* Targets are wall-clock UTC hours from `created_at`. No working-hours or holiday calendar is applied, because
  no verified calendar data exists.
* The clock pauses in `on_hold`/`awaiting_resident`, and the paused time is added to `due_at` on resume. A
  reopened case gets a fresh resolution window.
* Worker: a reminder fires once when less than 20% of the window remains. Overdue → level 1 (department
  supervisors), then level 2 (municipal admins) after a further half-window, never beyond `ESCALATION_MAX_LEVEL`.
  Idempotency comes from a unique key on `(complaint, trigger, level, due_at_snapshot)` plus outbox dedup keys,
  so overlapping runs cannot double-escalate. A notification failure never erases an escalation.

## Notifications and reliable events

* Every state change writes an `outbox_events` row in the same transaction. The worker claims rows with a lease
  (`FOR UPDATE SKIP LOCKED` on PostgreSQL) and fans them out into `notifications`. Each notification has a
  unique `dedup_key = event:recipient:channel`, so replays never duplicate.
* In-app notifications are always on. Email and SMS are opt-in (`PUT /api/users/me/notification-preferences`)
  and go through provider adapters, which are disabled (→ `skipped`) or mock (SIMULATED). Delivery uses
  bounded retries with exponential backoff.
* Templates include only the reference, status label, and routing stage: never descriptions, contact details,
  internal notes, or tokens.
* Failed events are visible to system admins (`GET /api/admin/outbox`) and can be re-queued after the cause is
  fixed.

## AI and service discovery

* `KeywordClassifier` (deterministic synonym/label matching) is the default and the fallback. `MockLLMClassifier`
  is a SIMULATED stand-in. Plug a real model in by implementing `Classifier.classify()` in
  `app/adapters/classifier.py`.
* Output is validated against active category codes, and the confidence must be ≥ `AI_CONFIDENCE_THRESHOLD`
  to be used. Anything else goes to triage. Provider errors fall back to keywords. Suggestions are stored in
  `ai_classifications`.
* AI is never required: with `AI_PROVIDER=disabled`, uncategorised reports still save and route to triage.
* `GET /api/services` searches published/unavailable services by name, synonyms, description, and suggested
  category. With no match it returns `no_match: true` and guidance instead of inventing a service.
* `POST /api/routing/suggest` previews category + department with **no side effects**.

## Duplicates and community support

Candidates are bounded: same or related category, open, unmerged, within `DUPLICATE_RADIUS_M` (bounding-box SQL
prefilter, then haversine), within `DUPLICATE_WINDOW_DAYS`, with at most `DUPLICATE_MAX_RESULTS`, ranked by
distance and text similarity. Residents see only a reference (plus the title if public) for complaints they
can't open. Nothing is auto-merged. Merging requires supervisor/admin scope over both complaints and a reason,
and refuses self-merges, already-merged targets, and chains/cycles. Public `nearby` search returns only public,
open reports, with coordinates rounded to ~100 m. Supporting is limited to one per account, never your own
report, and supporter identities are never exposed.

## Media

`POST /api/media` (multipart) detects JPEG/PNG/WebP by magic bytes and re-encodes with Pillow, which **strips
EXIF/GPS** and rejects malformed images. Size limits apply. Storage keys are random and the client filename is
sanitised for display only. Storage is private, and every download (`GET /api/media/{id}/content`) is
authorised. Upload first, then reference IDs in `media_ids` (report) or `evidence_media_ids` (resolve; staff only).
Uploads left unattached are deleted after `ORPHAN_MEDIA_MAX_AGE_HOURS`. There is **no malware scanner**
(`scan_state=not_scanned`).

## Analytics definitions (`GET /api/admin/analytics`, `/analytics/export.csv`)

The population is complaints with `created_at` in `[date_from, date_to)` UTC (max 366 days), within the
caller's scope (supervisors: their departments).

* `reports_total` counts all reports. `issues_total` excludes reports merged into another one, which avoids
  double counting. All other metrics use issues.
* `open` covers submitted, under_review, assigned, in_progress, awaiting_resident, on_hold, and reopened.
  `overdue_open` is open and `is_overdue`. `reopened` means `reopen_count > 0`.
* `resolution_hours_avg/median` = `resolved_at − created_at`, over issues with `resolved_at` set.
* `sla_compliance` = `sla_met / sla_measured`, where measured means resolved with a `due_at`, and met means
  `resolved_at ≤ due_at`. It is `null` when nothing was measured.
* Breakdowns are by department, category, ward, and priority. The CSV export is audited and prefixes cells
  starting with `= + - @` with `'` to block formula injection.

---

## API

Interactive docs are at `/docs` (disabled in production). Every error has the same shape:

```json
{"error": {"code": "stable_machine_code", "message": "...", "details": [{"field": "...", "issue": "..."}], "request_id": "..."}}
```

Status codes: 401 for unauthenticated/expired/revoked, 403 for not permitted, 404 for not found or not visible,
409 for invalid state/stale version/duplicate, 413 for too large, 422 for validation errors, 429 for rate
limiting. Collections are paginated (`page`, `page_size` ≤ 100) with stable ordering. `X-Request-ID` is
echoed on every response and appears in logs.

| Method & path | Who | Notes |
|---|---|---|
| `POST /api/auth/register` · `/login` · `/logout` | public / any | Rate-limited; generic login failures; logout revokes the server-side session |
| `GET/PATCH /api/users/me`, `GET/PUT /api/users/me/notification-preferences` | any | Email/roles not editable |
| `POST /api/complaints` | any | `Idempotency-Key` header supported; returns 201 (or 200 replay) |
| `GET /api/complaints` | any | Filters: status (multi), category, department, officer, priority, ward, created range, `q`, overdue, unassigned, mine; sort by created/updated/priority/due |
| `GET /api/complaints/{id}` | in scope | Resident or staff view; real timeline; `ETag` = version |
| `PATCH /api/complaints/{id}` | reporter / staff | Reporter: title/description/visibility before pickup. Staff: category/priority/visibility + reason. `If-Match` |
| `POST /api/complaints/{id}/transitions` | in scope | Generic validated transition |
| `POST …/withdraw` · `/assign` · `/reassign` · `/resolve` · `/close` · `/reopen` | see matrix | Dedicated use cases |
| `GET/POST …/comments`, `GET/POST …/notes` | scope / staff | Notes are staff-only |
| `GET …/media`, `GET …/possible-duplicates`, `POST …/merge` | scope / managers | |
| `POST …/feedback`, `POST/DELETE …/support` | reporter / residents | |
| `GET /api/complaints/nearby`, `GET /api/complaints/public/{reference}` | any | Public-safe summaries |
| `POST /api/media`, `GET /api/media/{id}/content` | any / authorised | |
| `GET /api/services`, `GET /api/categories`, `GET /api/wards`, `POST /api/routing/suggest`, `GET /api/announcements` | any | |
| `GET /api/notifications`, `PATCH /api/notifications/{id}/read` | owner | |
| `GET /api/admin/analytics`, `/analytics/export.csv` | analytics roles | |
| `GET/POST/PATCH /api/admin/departments`, `teams`, `officers`, `categories`, `services`, `wards` | admins (lists also supervisors) | Audited |
| `GET/POST/PATCH /api/admin/routing-rules`, `sla-policies` | admins | PATCH creates a new version |
| `POST /api/admin/users/{id}/roles` · `/roles/revoke` · `/activation` | system admin | The last system admin is protected |
| `POST /api/admin/announcements`, `…/{id}/state` | admins | draft → published → expired |
| `GET /api/admin/audit-logs`, `GET /api/admin/outbox`, `POST …/outbox/{id}/retry` | auditor/system admin | |
| `GET /health`, `GET /ready` | public | Liveness / DB readiness, no infrastructure details |

---

## Configuration

See `.env.example` for every variable with descriptions. Highlights:

* `ENVIRONMENT=production` requires a `JWT_SECRET` of at least 32 characters, `DEBUG=false`, and explicit CORS
  origins. It also disables `/docs` and refuses seed/reset. Configuration errors name the setting but never
  print its value.
* `DATABASE_URL`: SQLite by default. For PostgreSQL, run `uv sync --extra postgres` and use
  `postgresql+psycopg://…`. (The PostgreSQL path has not been run in this environment; see limitations.)
* Providers: `AI_PROVIDER` (keyword|mock|disabled), `EMAIL_PROVIDER`, `SMS_PROVIDER`, `MUNICIPAL_INTEGRATION`,
  `GEOCODING_PROVIDER` (disabled|mock).

### Extending

* **Category:** `POST /api/admin/categories` (two levels max, stable `code` like `roads.speedbreaker`), then a
  routing rule and optionally an SLA policy. Add `labels_i18n` for translations.
* **Department:** `POST /api/admin/departments` (+ `covered_ward_ids` to restrict coverage), teams via
  `/api/admin/teams`, officers via `/api/admin/officers`, supervisors via role grants with `department_id`.
* **Routing rule:** `POST /api/admin/routing-rules`. Changing it via `PATCH` versions it, and old complaints keep
  pointing at the version that routed them.
* **Notification provider:** implement `MessageProvider.send()` in `app/adapters/providers.py`, wire it into
  `get_providers()`, and add a config value. Raise `ProviderUnavailable` for retryable errors and
  `ProviderRejected` for permanent ones.
* **AI provider:** implement `Classifier` in `app/adapters/classifier.py` and register it in `build_classifier`.
  Send only the description. Output is validated and thresholded automatically.
* **Municipal integration:** implement `MunicipalCaseProvider.submit_case()`. External IDs are stored only after
  confirmation. Only use documented, authorised APIs, never scraping.

---

## Privacy, retention, and operations

* Personal data is limited to email, display name, optional phone, and language. Reporter contact details are
  never in public responses, notifications, or CSV exports (the CSV has references, not reporters). Exact
  coordinates are visible only to the reporter and in-scope staff; public views round them to ~100 m.
* Logs are JSON with request IDs and redaction of passwords, tokens, `Authorization` headers, and JWTs. Logs,
  `audit_logs` (who changed what policy/assignment), and business history tables are kept separate.
* **Retention (proposed defaults, not yet automated):** complaints and history are kept indefinitely for
  accountability. Unattached uploads are deleted after 24 h (automated). Idempotency keys expire after 24 h.
  Account deactivation preserves historical complaints. Deletion/anonymisation on request is **not
  implemented**. Indian data-protection obligations (DPDP Act 2023) need legal review; **no compliance is
  claimed**.
* **Backups:** SQLite: stop writes and copy `var/ycys.db` plus `var/media/` (or use `sqlite3 .backup`).
  PostgreSQL: `pg_dump` plus the media volume. Restore by putting the files back, then running `migrate`.
  Test restores regularly.
* **Production:** terminate TLS at a reverse proxy, run the API with multiple workers, and run exactly one
  `worker` process (or several with PostgreSQL row locking). Use a least-privilege DB user, keep secrets in a
  secret manager, and put `MEDIA_ROOT` on a private persistent volume. Rate limits are per process, so use a
  shared store before scaling out.

---

## Status: implemented vs partial vs mocked vs deferred

**Fully implemented and tested**
- Registration, login, logout with revocable server-side sessions; argon2 hashing; JWT issuer/audience/expiry
  checks; generic login errors; rate limits.
- RBAC + department/team/assignment row scope enforced in SQL; IDOR, cross-department, and escalation tests.
- Departments, teams, officers, wards (polygon jurisdiction), categories (two levels, i18n labels), service
  directory with publication states.
- Complaint creation with validation, server-side fields, collision-safe references, idempotency keys,
  transactional history + outbox.
- Central state machine, assignment/reassignment with reasons and history, optimistic locking, comments vs
  internal notes, information requests, resolution notes/evidence, feedback, reopen window, withdrawal,
  auto-close.
- Deterministic routing with precedence, coverage, effective dates, conflict detection, triage fallback,
  rerouting after category correction, and preserved initial decision.
- Priority rules with an audited staff override; SLA selection, pause/resume, reminders, overdue escalation
  (idempotent).
- In-app notifications via a transactional outbox with retries, leases, dedup, and an ops view.
- Duplicate candidates, audited merge with cycle prevention, public nearby search, support votes.
- Analytics and audited CSV export computed from records, with formula-injection protection.
- Admin configuration with an audit log; versioned routing rules and SLA policies; protection for the fallback
  queue and the last admin.
- Media uploads with content sniffing, EXIF stripping, size limits, and authorised download.
- Request IDs, structured redacted logs, security headers, body-size limit, health/readiness, startup config
  validation.

**Mocked (SIMULATED, labelled in data and responses)**
- Email and SMS delivery (`MockMessageProvider`), the municipal case system (`MockMunicipalProvider`, IDs
  prefixed `SIMULATED-`), reverse geocoding (`MockGeocoder`), and the external LLM classifier
  (`MockLLMClassifier`).

**Partial**
- Multilingual: Unicode storage/search and localised category labels work. Translations of complaint text are
  not stored separately (the original text and language are preserved).
- Rate limiting is in-process only.
- Comment moderation has an `is_hidden` flag and permission, but no moderation endpoint yet.
- Reminders cover the resolution target. The acknowledgement target is computed and exposed but not escalated.

**Deferred / not implemented**
- Real email, SMS, push, map, LLM, or municipal integrations (no credentials were provided or invented).
- Anonymous reporting (disabled by policy; it would need high-entropy tracking tokens).
- Voice input, offline sync, malware scanning, holiday/working-hour calendars, password reset flow,
  data-subject deletion/anonymisation, PostGIS spatial indexes.

## Verification performed

* `uv run pytest`: **177 passed** (unit: workflow transitions, routing, priority, SLA, geo, classifier;
  integration and API: lifecycle, validation, idempotency, permissions/IDOR, privacy leaks, duplicates/merge,
  worker retries/dedup/escalation/external sync, admin versioning, analytics fixtures, CSV, media, config,
  logging redaction, migrations, seed repeatability).
* `uv run ruff check app tests alembic`: all checks passed. `uv run mypy app`: no issues in 61 files.
* Clean-database `alembic upgrade head` → `check` (no model drift) → `downgrade base` → `upgrade head`.
* Seed run twice (the second creates nothing). Reset and seed refuse in production.
* Live smoke test against `uvicorn`: login → service search → routing suggestion → create → assign →
  resolve → timeline; other residents get 404 and unauthenticated calls get 401; then a worker pass.
* **Not verified:** PostgreSQL (no credentials available), any real external provider, and deployment.

## Next three highest-value tasks

1. Run the suite against PostgreSQL in CI, and add PostGIS or at least a spatial index for ward lookup and
   nearby search.
2. Implement a real notification provider (email first) and a password reset flow, plus a moderation endpoint
   for public comments.
3. Move rate limiting and the worker schedule to shared infrastructure (Redis or Postgres advisory locks) and
   add acknowledgement-target escalation with working-hour calendars once verified data exists.
