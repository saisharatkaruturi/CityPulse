# MASTER BUILD PROMPT FOR CLAUDE CODE

## Your City, Your Services --- Civic Issue Reporting and Municipal Service Routing Platform

**Problem statement:** "Your City, Your Services. Help residents report
local issues and find the right municipal service, with better routing
and clearer updates."

**Primary instruction:** Inspect the existing repository, implement a
real backend, run tests, fix failures, and document the result. This is
backend-first; do not spend time on UI or visual design. Do not merely
produce a plan or snippets. Modify the project itself. Preserve working
code, follow repository instructions, and report honestly what is
implemented, mocked, partial, or deferred.

## Operating rules

-   Read `CLAUDE.md`, `README.md`, `AGENTS.md`, package manifests,
    environment examples, migrations, and tests before editing.
-   Identify the existing stack and reuse it unless it is clearly
    unsuitable.
-   If the repository is empty, choose one coherent stack; preferred
    default is FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL,
    pytest, and typed configuration.
-   If the repository already uses TypeScript, use its existing
    framework and conventions instead of adding a second backend.
-   Prefer a modular monolith over microservices.
-   Create a plan, implement in small vertical slices, test each slice,
    and update documentation.
-   Never fabricate API credentials, official municipal data, real case
    IDs, or claims of real-world delivery.
-   Never claim a municipality received or resolved a complaint unless
    an authorized integration confirms it.
-   Mock optional external providers behind interfaces; clearly label
    mock behavior.
-   AI must be optional assistance, not a dependency for saving or
    tracking complaints.
-   Use database transactions, constraints, server-side authorization,
    validation, idempotency, and audit history for important operations.
-   Keep secrets out of source control, logs, responses, test fixtures,
    and documentation.
-   Never trust client-supplied user IDs, roles, assignment, status,
    timestamps, or privileged fields.
-   Use UTC timestamps internally, pagination on collection endpoints,
    safe error responses, and explicit API schemas.
-   Do not silently swallow exceptions, hardcode analytics, fake
    persistence with in-memory arrays, or return fake success from
    placeholder endpoints.
-   Run migrations, tests, lint/type checks where available, and a smoke
    test before reporting completion.
-   Ask only when a critical choice cannot be safely inferred; otherwise
    choose a reversible documented default.

## Product boundaries

The platform has six core backend engines: complaint management, service
discovery and routing, workflow/SLA, notifications,
intelligence/duplicate detection, and analytics. Residents submit and
track issues; officers triage and resolve them; administrators configure
departments, categories, routing, service targets, and permissions.
Distinguish local receipt, department routing, department
acknowledgement, marked resolution, and independently verified
real-world completion.

## Repository discovery

1.  Inspect repository tree and identify entry points, routers,
    services, models, schemas, settings, migrations, tests, and scripts.
2.  Run baseline tests before changes and record existing failures
    separately from newly introduced failures.
3.  Identify conventions for naming, API prefixes, error responses,
    logging, dependency injection, and formatting.
4.  Do not overwrite existing files blindly; inspect current contents
    and preserve unrelated working behavior.
5.  Create a concise implementation plan based on the actual repository
    and revise it as discoveries occur.
6.  Inspect git status and avoid overwriting user changes; review the
    final diff for accidental unrelated edits.
7.  Do not stop after planning; implement the agreed backend and verify
    the real repository state.

## Architecture and configuration

8.  Separate HTTP handlers, application/use-case services, domain rules,
    persistence, external adapters, background jobs, and tests.
9.  Keep business logic out of controllers and avoid duplicated routing
    or workflow logic.
10. Create typed central configuration with startup validation for
    required settings.
11. Provide `.env.example` with placeholders and descriptions, never
    real credentials.
12. Separate development, test, and production settings; production
    debug mode must be disabled by default.
13. Use explicit production CORS origins, request-size limits, upload
    limits, pagination limits, and external-call timeouts.
14. Make AI, maps, email, SMS, and municipal integrations optional
    through configuration.
15. Provide clear startup errors for invalid required configuration
    without printing secrets.
16. Pin or constrain dependencies according to repository conventions
    and use maintained packages.
17. Do not introduce a message broker, microservices, or complex
    infrastructure without a demonstrated need.

## Database and migrations

18. Use one canonical persistence model with primary keys, foreign keys,
    unique constraints, NOT NULL constraints, and appropriate indexes.
19. Use versioned migrations for all schema changes and verify
    clean-database migration.
20. Make migrations safe for existing data; do not drop or rewrite data
    without a justified migration plan.
21. Use transactions for complaint creation, status transitions,
    assignment changes, audit history, and related required records.
22. Use database constraints as the final protection for uniqueness and
    critical invariants.
23. Use optimistic locking or row locks where concurrent edits could
    overwrite each other.
24. Use UTC-aware timestamps and document timestamp semantics.
25. Prefer archival or soft deletion for records requiring history; do
    not cascade-delete audit evidence.
26. Provide a repeatable seed command and a test database that cannot
    accidentally touch production.
27. Document backup, restore, migration, and data-retention
    expectations.

## Users and authentication

28. Create user identity and profile models with stable IDs and only
    necessary personal data.
29. Support resident and municipal staff identities; support account
    deactivation without breaking historical complaints.
30. Use a mature authentication provider/library where practical.
31. If storing passwords, use modern password hashing; never store
    plaintext passwords.
32. Use secure recovery and verification tokens if those flows are
    implemented.
33. Rate-limit login and recovery; use generic failure messages that do
    not reveal account existence.
34. Validate token issuer, audience, expiry, signature, and revocation
    where relevant.
35. Use secure, HTTP-only, SameSite cookies and CSRF protection when
    applicable to the chosen session design.
36. Never store long-lived secrets in URLs or expose password hashes in
    API responses.
37. Test missing, invalid, expired, revoked, and unauthorized
    credentials.

## Roles and permissions

38. Implement server-side role-based access control plus department/ward
    scope where relevant.
39. Support resident, field officer, department supervisor, municipal
    administrator, system administrator, and read-only auditor roles as
    appropriate.
40. Use deny-by-default access policies and centralized permission
    checks.
41. Residents may access their own private complaints and only
    explicitly public summaries of other complaints.
42. Residents must not change status, department, officer assignment,
    audit timestamps, or privileged fields directly.
43. Field officers may access only assigned cases or their authorized
    team/department scope.
44. Supervisors may assign and reassign cases within their authorized
    scope and inspect overdue work.
45. Only authorized administrators may change categories, departments,
    routing rules, SLA policies, roles, or global settings.
46. Internal notes, private evidence, audit logs, exports, and analytics
    must be protected by explicit permissions.
47. Test IDOR, cross-user access, cross-department access, privilege
    escalation, and direct API calls bypassing the UI.

## Departments and officers

48. Create departments with stable ID, name, code, description, active
    state, public contact fields, and service coverage.
49. Support officers, team membership, supervisor relationships, and
    active/inactive status.
50. Do not assign new work to inactive officers or departments without
    an explicit policy exception.
51. Support assignment to an officer or team queue.
52. Record every assignment and reassignment with actor, old/new owner,
    timestamp, and reason.
53. Require a reason for manual reassignment and preserve the original
    routing decision.
54. Provide an unassigned/triage queue when no responsible team is
    known.
55. Allow department deactivation without deleting historical complaints
    or assignments.
56. Keep internal staff notes private from residents.
57. Test assignment scope, inactive staff, missing teams, and
    unauthorized reassignment.

## Service directory

58. Create a service catalogue with ID, name, summary, detailed
    instructions, department relationships, categories, active state,
    and optional public contact details.
59. Support search by name, description, synonyms, category, and
    optional natural-language query.
60. Store operating hours, eligibility, and required information only
    when verified and maintained.
61. Allow administrators to publish, unpublish, or mark services
    temporarily unavailable.
62. Provide a safe no-match response instead of inventing a service or
    department.
63. Distinguish information services from complaint-reporting services.
64. Store last-reviewed timestamp and service owner where practical.
65. Do not hardcode service catalogue data into route handlers.
66. Do not invent official government eligibility rules, contact
    details, service guarantees, or legal deadlines.
67. Test search, filters, inactive services, no-match behavior, and
    department relationships.

## Categories and taxonomy

68. Create categories and optional subcategories with stable IDs,
    labels, descriptions, synonyms, active state, and optional examples.
69. Map categories to routing rules, default priorities, and SLA
    policies through data/configuration.
70. Allow a category to be disabled without deleting historical records.
71. Validate submitted category IDs and support an explicit
    unknown/other or triage fallback.
72. Keep resident-selected category separate from later staff-corrected
    category where auditability matters.
73. Record who corrected a category, when, why, and whether routing was
    recalculated.
74. Support localizable labels if multilingual support is enabled.
75. Do not let ambiguous keywords route a complaint with unjustified
    certainty.
76. Use consistent taxonomy IDs across database, API, tests, and seed
    data.
77. Test invalid, inactive, ambiguous, parent/child, and unknown
    categories.

## Wards, zones, and location

78. Represent wards/zones and store stable IDs, display names, active
    state, and verified boundary data where available.
79. Never fabricate official ward boundaries; document provenance and
    limitations of geographic data.
80. Validate latitude and longitude ranges and preserve location
    source/accuracy when available.
81. Allow manual location selection when GPS is unavailable or
    inaccurate.
82. Resolve jurisdiction through verified boundaries or configured
    rules, not guessed addresses.
83. Support department coverage by ward, zone, or service boundary.
84. Handle missing coordinates and out-of-area reports with a documented
    fallback.
85. Support nearby issue queries with bounded radius, result count, and
    privacy filtering.
86. Use spatial indexes if PostGIS or another spatial engine is used.
87. Never expose private exact coordinates through public APIs unless
    explicitly approved by policy.

## Complaint model

88. Store internal ID, unique human-readable reference, reporter, title,
    description, category/subcategory, location, visibility, priority,
    status, department, assignment, timestamps, deadline, resolution,
    and optional external case reference.
89. Keep internal primary keys separate from public tracking references.
90. Generate tracking references collision-safely using database-backed
    uniqueness.
91. Never use a predictable sequential reference as the sole anonymous
    access secret.
92. Track created_at, updated_at, resolved_at, closed_at, and due_at
    with defined semantics.
93. Store media references separately from the complaint row.
94. Store source channel, duplicate links, privacy setting, reassignment
    reason, escalation state, and routing decision when useful.
95. Allow anonymous reporting only if policy enables it and provide a
    high-entropy tracking token or equivalent.
96. Define archival, withdrawal, correction, retention, and deletion
    behavior explicitly.
97. Preserve history and the original reporter relationship after merges
    or closure.

## Complaint creation and validation

98. Implement POST complaint creation with explicit request schema and
    server-side authorization.
99. Require a meaningful description or documented minimum fields and
    enforce bounded lengths.
100. Trim safe whitespace and reject empty/whitespace-only descriptions.
101. Validate category, ward, media ownership, visibility, coordinate
     ranges, and all referenced IDs.
102. Do not trust client-supplied reporter IDs, status, assignment,
     priority overrides, timestamps, or audit fields.
103. Set initial status and timestamps server-side and generate the
     tracking reference on the server.
104. Create the complaint and initial status history in one transaction.
105. Return the reference only after persistence succeeds.
106. Support idempotency keys for retryable creation requests and reject
     key reuse with different input.
107. Return field-level validation errors in a consistent safe response
     format.

## Complaint retrieval, search, and edits

108. Implement authorized list and detail endpoints with pagination and
     bounded page size.
109. Support filters for status, category, department, assigned officer,
     priority, ward, date range, and permitted text search.
110. Enforce row-level scope in database queries; never fetch all rows
     and filter only in the frontend.
111. Use explicit response schemas to avoid leaking internal fields.
112. Separate resident-edit schemas from staff-edit schemas.
113. Reject mass assignment of protected fields and reject edits to
     immutable fields.
114. Use stable ordering and appropriate indexes for frequently used
     filters.
115. Support conflict responses when a stale edit would overwrite a
     newer update.
116. Do not expose internal notes, private media, reporter contact
     details, or sensitive audit data to unauthorized callers.
117. Test filter combinations, pagination, empty results, private
     records, and cross-user access.

## Workflow state machine

118. Define allowed statuses and transitions in one central domain
     module.
119. Support a practical MVP flow such as Submitted, Under Review,
     Assigned, In Progress, Awaiting Resident, On Hold, Resolved,
     Closed, Rejected, Withdrawn, and Reopened as needed.
120. Validate every transition server-side and reject arbitrary
     client-supplied status values.
121. Require a reason for rejection, hold, reopening, and sensitive
     correction where policy specifies.
122. Require resolution notes/evidence when configured.
123. Record previous state, new state, actor, timestamp, reason, and
     system/human origin.
124. Write status and history in the same transaction.
125. Define whether resolved and closed are separate states and document
     the rule.
126. Define how SLA clocks behave in hold or awaiting-resident states.
127. Test every allowed transition and representative forbidden
     transitions.

## Assignment and reassignment

128. Provide authorized assignment and reassignment use cases separate
     from general complaint updates.
129. Validate department, team, and officer existence, active state, and
     scope.
130. Require a reason for manual reassignment.
131. Record old and new assignment in assignment history.
132. Preserve initial automatic routing outcome even after manual
     changes.
133. Notify the appropriate staff/resident after a committed meaningful
     change.
134. Prevent repeated reassignment loops and handle unavailable
     officers.
135. Support an unassigned queue when no valid target exists.
136. Ensure assignment changes and history commit atomically.
137. Test unauthorized assignment, inactive target, concurrent
     assignment, and successful reassignment.

## Routing engine

138. Implement deterministic routing in a dedicated service rather than
     HTTP handlers.
139. Route using category/subcategory, verified jurisdiction, service
     coverage, and active department rules.
140. Store rule precedence, active state, effective dates, and
     responsible department in configuration.
141. Define explicit precedence for overlapping or conflicting rules.
142. Record selected rule, routing result, explanation, timestamp, and
     fallback reason.
143. Route unknown or ambiguous cases to triage rather than inventing a
     destination.
144. Support authorized manual reassignment and optional re-evaluation
     after category correction.
145. Prevent routing loops and preserve prior decisions for audit.
146. AI may suggest a category or department but must not override
     jurisdiction or silently decide uncertain cases.
147. Test valid mapping, inactive department, no match, conflicting
     rules, outside jurisdiction, and fallback.

## Priority and urgency

148. Define controlled priority values and keep priority separate from
     status.
149. Calculate default priority using configurable rules such as issue
     type, safety, recurrence, affected population, and waiting time
     where available.
150. Do not declare a critical emergency from a single keyword alone.
151. Allow authorized staff to override priority with a required reason
     and history.
152. Use configured rules to alert staff about critical or high-priority
     issues.
153. Direct immediate danger to verified emergency channels; do not
     imply this app dispatches emergency services.
154. Do not let an AI-only score trigger irreversible high-impact
     actions.
155. Support filtering and sorting by priority.
156. Use illustrative sample rules unless official local policy has been
     verified.
157. Test deterministic scoring, override permission, invalid values,
     and alert policy.

## SLA and escalation

158. Create configurable policies for acknowledgement, assignment,
     review, and resolution targets.
159. Select policy by category, priority, department, and effective date
     where configured.
160. Store policy version used for each complaint's target.
161. Calculate due dates on the server and document
     working-hour/timezone behavior.
162. Support holidays and working calendars only when reliable data is
     configured.
163. Define pause/resume behavior for hold and awaiting-resident states.
164. Schedule approaching-deadline reminders and overdue detection.
165. Escalate to a configured supervisor or queue when policy requires
     it.
166. Make reminder/escalation jobs idempotent and record trigger, actor,
     destination, and timestamp.
167. Never present sample deadlines as official municipal guarantees.

## Notifications

168. Use domain events for complaint submitted, assigned, reassigned,
     status changed, information requested, resolved, reopened, deadline
     approaching, and overdue.
169. Implement in-app notifications as the baseline.
170. Use provider adapters for email, SMS, push, or messaging platforms;
     keep them optional.
171. Store recipient, channel, template, delivery state, attempt count,
     timestamps, and provider reference.
172. Use safe templates and escape untrusted content for the target
     channel.
173. Respect user preferences and applicable consent requirements.
174. Use bounded retries with backoff and avoid duplicate delivery on
     job retries.
175. Never roll back a complaint because notification delivery fails.
176. Do not include private contact details, internal notes, tokens, or
     unnecessary personal data in messages.
177. Test provider-disabled mode, failure, retry, deduplication, read
     state, and ownership.

## Background jobs and reliable events

178. Move notification delivery, image processing, optional AI
     classification, overdue checks, escalation, and expensive analytics
     to background tasks where appropriate.
179. Use a simple worker/scheduler suited to the existing stack; do not
     introduce Kafka without need.
180. Use a transactional outbox or equivalent for important events when
     database commit and event delivery must stay consistent.
181. Store event type, aggregate ID, payload version, minimal payload,
     created time, processing state, attempt count, and sanitized
     failure details.
182. Make event consumers idempotent and jobs safe to run more than
     once.
183. Use bounded retry counts, timeouts, and backoff.
184. Prevent overlapping scheduled runs from creating duplicate
     escalations.
185. Expose failed jobs to authorized operators and document recovery.
186. Ensure a worker restart does not lose committed required work.
187. Test repeated delivery, rollback, worker failure, retry, and
     duplicate processing.

## AI and natural-language service discovery

188. Create a provider-neutral interface for classification and
     natural-language service search.
189. Keep deterministic keyword/synonym matching as the fallback.
190. Validate AI structured output against configured category and
     service IDs.
191. Store suggestion, confidence, provider/model version, and timestamp
     where appropriate.
192. Use a configurable confidence threshold and send uncertain results
     to manual review.
193. Treat model output as untrusted data; guard against prompt
     injection in user text and uploads.
194. Use timeouts, usage limits, and safe retries.
195. Do not require AI credentials for complaint submission or tracking.
196. Send only necessary data to third-party providers and document
     privacy implications.
197. Test provider timeout, malformed output, unknown category, low
     confidence, and disabled-provider behavior.

## Duplicate detection and community support

198. Find candidate duplicates using category, geographic proximity,
     time window, status, and optional text similarity.
199. Bound candidate radius and result count and avoid expensive
     unbounded searches.
200. Show only complaint data the caller is allowed to see.
201. Do not automatically merge based only on text similarity.
202. Allow authorized staff to merge verified duplicates with reason and
     audit history.
203. Prevent merge cycles and preserve each original report and reporter
     relationship.
204. Allow support/vote functionality only if public visibility and
     abuse controls are implemented.
205. Prevent duplicate support from the same account where policy
     forbids it.
206. Do not expose supporter identities.
207. Test nearby matches, distant similar text, different categories,
     unauthorized merge, and repeated support.

## Media and file storage

208. Validate file type by content where feasible, size, upload
     ownership, and allowed formats.
209. Reject executable or disallowed formats and enforce request/file
     size limits.
210. Generate safe storage keys; never use raw client filenames as
     paths.
211. Store metadata separately from complaint records and use private
     storage by default.
212. Check authorization on every file retrieval and use expiring signed
     URLs when appropriate.
213. Scan uploads for malware where feasible and track scan state.
214. Strip EXIF data from public derivatives when necessary.
215. Handle interrupted uploads, orphan cleanup, and expired temporary
     files safely.
216. Do not expose storage credentials or private evidence through
     public complaint APIs.
217. Test oversized files, unsupported content, path traversal,
     ownership, private access, and provider failure.

## Comments, notes, evidence, and feedback

218. Separate resident-visible comments from staff-only internal notes.
219. Validate comment length and prevent author/timestamp spoofing.
220. Allow authorized staff to request more information from a resident.
221. Store resolution notes and evidence separately from ordinary
     comments.
222. Apply file access controls to before/after photos and other
     evidence.
223. Allow feedback only for eligible complaint states and authorized
     reporters.
224. Define a bounded rating scale and prevent duplicate feedback unless
     editing is supported.
225. Allow a reopen request under a documented policy and preserve
     previous resolution history.
226. Moderate public content where community features exist and audit
     moderation actions.
227. Test that private notes and evidence never leak through resident
     endpoints or notifications.

## Analytics and reporting

228. Compute all metrics from persisted records, never hardcoded
     dashboard numbers.
229. Define totals for open, resolved, closed, rejected, withdrawn,
     overdue, and reopened complaints.
230. Calculate average and median resolution time with documented
     start/end events.
231. Define SLA compliance numerator and denominator explicitly.
232. Aggregate by department, category, ward, priority, and date range.
233. Enforce role scope and privacy-safe aggregation in analytics
     queries.
234. Support CSV exports only for authorized users and bounded data
     ranges.
235. Mitigate CSV formula injection for user-controlled strings.
236. Handle empty data and timezone boundaries consistently.
237. Test every metric against known fixtures and document its
     definition.

## Admin configuration

238. Allow authorized admins to manage departments, officers,
     categories, services, wards, routing rules, SLA policies,
     notification templates, languages, and public announcements.
239. Use validation and authorization for every administrative endpoint.
240. Record actor, timestamp, and old/new values for critical policy
     changes.
241. Version routing and SLA rules or preserve enough history to explain
     past decisions.
242. Deactivate referenced records instead of deleting history.
243. Prevent administrators from accidentally removing the only fallback
     queue.
244. Allow safe activation/deactivation of optional modules.
245. Provide a public announcement lifecycle with
     draft/published/expired states if included.
246. Label seed announcements as demo data and do not fabricate official
     notices.
247. Test unauthorized changes, invalid references, and historical
     integrity.

## Security, privacy, and abuse prevention

248. Use parameterized database access and explicit schemas to prevent
     injection and mass assignment.
249. Use TLS in deployed environments, secure authentication settings,
     and least-privilege database credentials.
250. Set rate limits for login, recovery, complaint creation, search,
     uploads, and expensive AI routes.
251. Use safe generic errors and do not expose stack traces in
     production.
252. Redact passwords, tokens, authorization headers, signed URLs, and
     sensitive request bodies from logs.
253. Collect only necessary personal data and document visibility,
     retention, correction, archival, and deletion rules.
254. Do not expose reporter phone/email, private descriptions, exact
     home coordinates, or internal notes publicly.
255. Restrict exports and audit log access and record sensitive bulk
     actions.
256. Follow applicable Indian privacy and data-protection requirements
     without claiming legal compliance absent review.
257. Test IDOR, privilege escalation, cross-department access, upload
     abuse, rate limits, public leakage, and secret exposure.

## Search, map, and geocoding integrations

258. Keep map/geocoding provider code behind an adapter and credentials
     in environment settings.
259. Handle provider timeouts, rate limits, invalid results, ambiguous
     addresses, and missing results.
260. Do not treat reverse geocoding as proof of jurisdiction.
261. Cache only when provider terms and data freshness permit.
262. Allow manual location correction and a no-GPS fallback.
263. Keep public map output privacy-filtered and bounded.
264. Use verified GIS data for boundaries and document data provenance.
265. Do not send private complaint descriptions to map providers
     unnecessarily.
266. Provide mock adapters for tests and clearly label mocked behavior.
267. Test provider-disabled, timeout, invalid response, and out-of-area
     behavior.

## API conventions

268. Use consistent resource naming and API prefixes matching the
     repository.
269. Define request and response schemas for all public endpoints.
270. Use consistent error objects with stable machine-readable codes.
271. Use appropriate HTTP statuses for validation, authentication,
     authorization, conflicts, rate limits, and internal failures.
272. Document every endpoint's permissions, request fields, responses,
     filters, and error cases.
273. Generate or maintain OpenAPI documentation that matches the
     implementation.
274. Use pagination for collections and stable ordering.
275. Use a correlation/request ID in logs and responses where practical.
276. Do not return raw ORM objects or exceptions directly.
277. Test both successful and failed response contracts.

## Operations, deployment, and observability

278. Provide health and, where useful, readiness checks without exposing
     infrastructure secrets.
279. Add structured logs with correlation IDs and safe context.
280. Document local startup, migrations, seeding, workers, tests,
     linting, and API docs.
281. Do not run destructive migrations automatically on every
     application startup.
282. Document production TLS, CORS, secrets, upload storage, backups,
     and recovery.
283. Provide a safe demo reset command that refuses to run in
     production.
284. Run dependency checks where tooling is available.
285. Verify clean database migration and seed repeatability.
286. Keep logs, audit records, and business history conceptually
     separate.
287. Report deployment as successful only if it was actually deployed
     and verified.

## Testing and quality

288. Use unit tests for routing, state transitions, SLA calculations,
     priority rules, and validation.
289. Use integration tests for database transactions, migrations,
     uniqueness, and concurrency-sensitive operations.
290. Use API tests for authentication, response contracts, pagination,
     filters, and authorization.
291. Use fictional test data and mock all external providers.
292. Test that automated tests never send real email/SMS or call live
     municipal systems.
293. Test complaint creation, tracking, assignment, status updates,
     resolution, feedback, and analytics end to end.
294. Test invalid inputs, forbidden transitions, cross-user access,
     duplicate retries, provider failures, and worker retries.
295. Run full tests and lint/type checks and report exact command
     outcomes.
296. Do not skip or weaken tests just to achieve a passing result.
297. Inspect final diff and verify no credentials or unrelated changes
     were introduced.

## Seed data and demo scenarios

298. Seed fictional Roads, Sanitation, Water Supply, Drainage, and
     Street Lighting departments.
299. Seed categories for potholes, garbage, water leakage, blocked
     drains, broken streetlights, and other civic issues.
300. Seed fictional wards or zones and clearly label them as demo data.
301. Seed resident, officer, supervisor, and administrator accounts with
     development-only instructions.
302. Seed complaints across statuses, categories, departments, and
     priorities.
303. Seed an overdue complaint, an unmapped complaint, and a pair of
     potential duplicates.
304. Seed a resolved complaint with fictional resolution notes and
     evidence metadata.
305. Make seed scripts repeatable and safe to run.
306. Prevent demo credentials and reset scripts from being used in
     production.
307. Document all sample data and avoid real personal information.

## External municipal integration

308. Define a provider interface for an external municipal
     case-management API only if authorized integration is in scope.
309. Use documented and authorized APIs; do not scrape portals or bypass
     access controls.
310. Store external case IDs only after a real provider confirms them.
311. Map local and external statuses explicitly and record
     synchronization state.
312. Handle timeout, rejection, retry, partial failure, and
     reconciliation.
313. Distinguish local receipt from external acknowledgement in all
     resident-facing messages.
314. Provide a mock adapter for demo mode and mark all mock results as
     simulated.
315. Protect credentials and do not log provider secrets.
316. Do not claim a real municipality received a report unless
     confirmed.
317. Test mock success, provider rejection, timeout, retry, and
     reconciliation.

## Multilingual, voice, and accessibility support

318. Preserve original text and store translations separately.
319. Support English and Telugu when required by the target users and
     configured resources.
320. Use stable language codes and Unicode-safe database/API behavior.
321. Allow correction of speech-to-text and translation output.
322. Validate audio types and size if voice input is implemented.
323. Delete temporary audio according to documented retention rules.
324. Provide a text-entry fallback when speech recognition fails.
325. Do not require a photo or exact GPS location when inappropriate or
     unavailable.
326. Keep error codes stable so clients can localize messages.
327. Test non-Latin text persistence, search, notifications, and
     serialization.

## Offline support (optional)

328. Treat offline submission as optional and defer it until the online
     lifecycle is correct.
329. Clearly distinguish local draft, queued submission, and
     server-confirmed complaint.
330. Do not issue a real tracking reference before server persistence.
331. Use idempotency when queued reports are retried.
332. Revalidate category, jurisdiction, permissions, and media at
     synchronization time.
333. Handle expired authentication, rejected queued reports, and partial
     upload failures.
334. Define local draft retention and cancellation behavior.
335. Never let offline mode bypass server validation.
336. Test repeated synchronization and stale configuration.
337. Do not claim offline support unless it has been implemented and
     tested.

## Documentation and final report

338. Update README with project purpose, architecture, setup,
     migrations, seeding, startup, tests, and API docs.
339. Document entities and relationships, permissions, state machine,
     routing precedence, fallback, and SLA calculations.
340. Document environment variables, provider setup, and mock mode.
341. Document how to add a category, department, routing rule,
     notification provider, or AI provider.
342. Document retention, privacy assumptions, backup/recovery, and known
     limitations.
343. List files changed, routes added, migrations, tests actually run,
     and their exact outcomes.
344. Separate fully implemented, partially implemented, mocked, and
     deferred functionality.
345. List manual configuration still required and the next three
     highest-value tasks.
346. Never claim tests, integrations, deployment, or external delivery
     succeeded unless verified.
347. Finish only when the core complaint lifecycle is functional and the
     remaining limitations are explicit.

## Database data dictionary

### `users`

-   stable primary key
-   normalized unique email when email login is enabled
-   optional normalized phone
-   display name
-   password hash only if local passwords are used
-   active/deactivated state
-   preferred language
-   created and updated timestamps
-   never expose credentials or hashes

### `roles and user_roles`

-   controlled role names
-   many-to-many user-role mapping if required
-   optional department/ward scope
-   server-enforced permission matrix
-   auditable privilege changes

### `departments`

-   stable ID and unique code
-   name and description
-   active state
-   public contact fields
-   coverage rules
-   optional parent department
-   timestamps
-   historical references preserved after deactivation

### `officers`

-   linked staff user
-   department/team membership
-   active state
-   supervisor relation
-   assignment eligibility
-   no unnecessary sensitive employment data

### `wards`

-   stable ID and name
-   optional code
-   verified boundary geometry if available
-   active state
-   data provenance
-   timestamps
-   no fabricated official boundaries

### `services`

-   name and description
-   department relationships
-   supported categories
-   active/publication state
-   verified instructions/contact/hours
-   last reviewed timestamp

### `categories`

-   name and description
-   optional parent category
-   synonyms
-   active state
-   routing relation
-   priority/SLA relation
-   historical label preservation

### `routing_rules`

-   category and optional geographic match
-   target department/queue
-   precedence
-   effective dates
-   active state
-   created/updated actor
-   version/audit history

### `complaints`

-   internal ID
-   unique public reference
-   reporter ID or allowed anonymous mode
-   title and description
-   category/subcategory
-   coordinates/address/ward
-   visibility
-   priority and status
-   department and assignment
-   due/resolved/closed timestamps
-   version for concurrency
-   optional confirmed external case ID

### `complaint_media`

-   complaint ID
-   uploader ID
-   opaque storage key
-   sanitized filename
-   content type and size
-   media kind
-   visibility
-   scan state
-   upload timestamp
-   optional sanitized public derivative

### `complaint_status_history`

-   complaint ID
-   previous and next status
-   actor
-   reason
-   system/human marker
-   server timestamp
-   immutable to ordinary users

### `complaint_assignments`

-   complaint ID
-   old/new department
-   old/new officer/team
-   actor
-   reason
-   routing rule reference
-   timestamp
-   historical assignment preservation

### `complaint_comments`

-   complaint ID
-   author
-   body
-   visibility
-   timestamps
-   moderation/edit state
-   no client-controlled author identity

### `complaint_internal_notes`

-   complaint ID
-   authorized staff author
-   body
-   timestamp
-   strict staff-only access

### `complaint_links`

-   source and target complaint IDs
-   relationship type
-   merge/duplicate reason
-   actor and timestamp
-   cycle prevention

### `complaint_supporters`

-   complaint ID
-   user or permitted anonymous key
-   timestamp
-   uniqueness policy
-   no public supporter identity

### `sla_policies`

-   category/priority/department scope
-   acknowledgement/assignment/resolution targets
-   calendar and pause rules
-   effective dates
-   version
-   illustrative versus official policy label

### `escalation_history`

-   complaint ID
-   rule and trigger
-   target queue/supervisor
-   actor/system marker
-   timestamp
-   delivery/action result

### `notifications`

-   recipient
-   complaint reference
-   event type
-   channel
-   template version
-   delivery status
-   attempt count
-   provider reference
-   created/sent/read timestamps

### `notification_preferences`

-   user ID
-   channel settings
-   language
-   consent/opt-out state where applicable
-   updated timestamp

### `feedback`

-   complaint ID
-   authorized reporter
-   bounded rating
-   optional text
-   timestamps
-   duplicate feedback policy

### `announcements`

-   title/body
-   audience or ward scope
-   draft/published/expired state
-   publisher
-   publish window
-   audit history
-   demo label if synthetic

### `audit_logs`

-   actor
-   action
-   entity type/ID
-   timestamp
-   reason
-   correlation ID
-   safe before/after summary
-   restricted read access

### `idempotency_records`

-   caller scope
-   key
-   operation
-   request fingerprint
-   safe replay reference
-   created/expiry timestamps
-   unique constraint

### `outbox_events`

-   event type
-   aggregate ID
-   payload version
-   minimal payload
-   processing status
-   attempt count
-   created/processed timestamps
-   sanitized failure detail

### `ai_classifications`

-   complaint/query reference
-   suggested category/department
-   confidence
-   model/provider version
-   timestamp
-   final human-selected value kept separately

## API endpoint contract catalogue

### `POST /api/auth/register` --- Register resident where local registration is enabled

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/auth/login` --- Authenticate

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/auth/logout` --- End session or revoke relevant credentials

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/users/me` --- Get current user's safe profile

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `PATCH /api/users/me` --- Update permitted profile fields

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints` --- Create complaint

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/complaints` --- List authorized complaints with pagination and filters

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/complaints/{id}` --- Get authorized complaint detail

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `PATCH /api/complaints/{id}` --- Update allowed fields using role-specific schema

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/withdraw` --- Withdraw where policy permits

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/assign` --- Assign to officer/team

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/reassign` --- Reassign with reason and history

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/transitions` --- Apply validated workflow transition

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/resolve` --- Record resolution and evidence

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/close` --- Close according to workflow rules

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/reopen` --- Request or perform reopening

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/comments` --- Add permitted comment

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/complaints/{id}/possible-duplicates` --- Find safe duplicate candidates

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/merge` --- Merge verified duplicates with audit history

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/complaints/{id}/feedback` --- Submit eligible feedback

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/services` --- Search/browse active service directory

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/categories` --- List active categories

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/routing/suggest` --- Suggest a route without side effects

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/wards` --- List supported geographic areas

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/complaints/nearby` --- Find public-safe nearby issues

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/notifications` --- List current user's notifications

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `PATCH /api/notifications/{id}/read` --- Mark own notification read

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/admin/analytics` --- Return role-scoped metrics from real records

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/admin/departments` --- List departments within permission scope

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/admin/departments` --- Create department

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `PATCH /api/admin/departments/{id}` --- Update department with audit

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/admin/routing-rules` --- List routing configuration

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/admin/routing-rules` --- Create validated routing rule

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `PATCH /api/admin/routing-rules/{id}` --- Update/version routing rule

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /api/admin/sla-policies` --- List SLA policies

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `POST /api/admin/sla-policies` --- Create validated SLA policy

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

### `GET /health` --- Minimal health status

-   Define typed request and response schemas and document all fields.
-   Enforce authentication and server-side authorization appropriate to
    this route.
-   Validate inputs, references, state, and ownership before modifying
    data.
-   Return consistent safe errors and appropriate HTTP status codes.
-   Add positive, negative, authorization, and failure-path tests.
-   Update OpenAPI documentation and avoid fake success responses.

## End-to-end workflow acceptance scenarios

### Resident report lifecycle

-   [ ] Resident submits description, category suggestion, optional
    location, and optional media.
-   [ ] API validates request and permissions, creates complaint and
    initial status history transactionally, and returns a tracking
    reference after persistence.
-   [ ] Routing selects a configured department or fallback queue and
    records its decision.
-   [ ] Notification event is queued only after the database commit.
-   [ ] Authorized officer views and assigns the complaint.
-   [ ] Officer transitions it to in progress and the system records
    actor, reason, and timestamp.
-   [ ] Officer records resolution notes and evidence and marks the case
    resolved.
-   [ ] Resident retrieves actual status history and can submit feedback
    or request reopening if policy allows.
-   [ ] Analytics reflect the real persisted records.
-   [ ] Automated tests verify the complete flow and all relevant
    permission boundaries.

### Unknown route

-   [ ] An unknown category is accepted if basic report validation
    passes.
-   [ ] The routing engine does not invent a department.
-   [ ] The complaint enters a triage queue or explicit unassigned
    state.
-   [ ] The resident receives a tracking reference.
-   [ ] An authorized officer corrects category/department and the
    change is audited.
-   [ ] Routing is reevaluated under configured rules.
-   [ ] Tests prove the fallback works without AI credentials.

### Duplicate report

-   [ ] System searches bounded nearby open complaints with matching or
    related categories.
-   [ ] Candidate output excludes private reporter data.
-   [ ] Resident can continue with a distinct report or support a
    permitted public issue.
-   [ ] Authorized staff can merge a verified duplicate with a reason.
-   [ ] Merge preserves original records and audit history and prevents
    cycles.
-   [ ] Analytics avoid double-counting where the definition requires
    underlying issues rather than reports.

### Overdue case

-   [ ] Configured SLA creates a due date on the server.
-   [ ] Scheduled worker detects approaching deadline and queues at most
    one reminder per policy window.
-   [ ] Overdue worker records the overdue condition and applies
    configured escalation.
-   [ ] Escalation target is validated and history is recorded.
-   [ ] Notification failure does not erase the escalation.
-   [ ] Repeated worker execution does not duplicate events.

### External provider outage

-   [ ] Local complaint persistence succeeds without external provider
    availability.
-   [ ] Outbox/queue stores pending optional work.
-   [ ] Timeout/rejection is recorded with sanitized diagnostics.
-   [ ] Retry is bounded and idempotent.
-   [ ] External case ID is stored only after confirmed provider
    response.
-   [ ] Resident wording distinguishes local receipt from external
    acknowledgement.

## Expanded implementation directives

### Directive 0001 --- Repository discovery

-   Implement this requirement in the actual repository: Inspect
    repository tree and identify entry points, routers, services,
    models, schemas, settings, migrations, tests, and scripts.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Inspect repository tree and identify entry points, routers,
    services, models, schemas, settings, migrations, tests, and scripts.
-   Persist all required data and audit events consistently for: Inspect
    repository tree and identify entry points, routers, services,
    models, schemas, settings, migrations, tests, and scripts.
-   Add at least one positive test and one relevant negative/failure
    test for: Inspect repository tree and identify entry points,
    routers, services, models, schemas, settings, migrations, tests, and
    scripts.
-   Document configuration, behavior, limitations, and manual setup for:
    Inspect repository tree and identify entry points, routers,
    services, models, schemas, settings, migrations, tests, and scripts.

### Directive 0002 --- Repository discovery

-   Implement this requirement in the actual repository: Run baseline
    tests before changes and record existing failures separately from
    newly introduced failures.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Run baseline tests before changes and record existing failures
    separately from newly introduced failures.
-   Persist all required data and audit events consistently for: Run
    baseline tests before changes and record existing failures
    separately from newly introduced failures.
-   Add at least one positive test and one relevant negative/failure
    test for: Run baseline tests before changes and record existing
    failures separately from newly introduced failures.
-   Document configuration, behavior, limitations, and manual setup for:
    Run baseline tests before changes and record existing failures
    separately from newly introduced failures.

### Directive 0003 --- Repository discovery

-   Implement this requirement in the actual repository: Identify
    conventions for naming, API prefixes, error responses, logging,
    dependency injection, and formatting.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Identify conventions for naming, API prefixes, error responses,
    logging, dependency injection, and formatting.
-   Persist all required data and audit events consistently for:
    Identify conventions for naming, API prefixes, error responses,
    logging, dependency injection, and formatting.
-   Add at least one positive test and one relevant negative/failure
    test for: Identify conventions for naming, API prefixes, error
    responses, logging, dependency injection, and formatting.
-   Document configuration, behavior, limitations, and manual setup for:
    Identify conventions for naming, API prefixes, error responses,
    logging, dependency injection, and formatting.

### Directive 0004 --- Repository discovery

-   Implement this requirement in the actual repository: Do not
    overwrite existing files blindly; inspect current contents and
    preserve unrelated working behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not overwrite existing files blindly; inspect current
    contents and preserve unrelated working behavior.
-   Persist all required data and audit events consistently for: Do not
    overwrite existing files blindly; inspect current contents and
    preserve unrelated working behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not overwrite existing files blindly; inspect current
    contents and preserve unrelated working behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not overwrite existing files blindly; inspect current contents
    and preserve unrelated working behavior.

### Directive 0005 --- Repository discovery

-   Implement this requirement in the actual repository: Create a
    concise implementation plan based on the actual repository and
    revise it as discoveries occur.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create a concise implementation plan based on the actual
    repository and revise it as discoveries occur.
-   Persist all required data and audit events consistently for: Create
    a concise implementation plan based on the actual repository and
    revise it as discoveries occur.
-   Add at least one positive test and one relevant negative/failure
    test for: Create a concise implementation plan based on the actual
    repository and revise it as discoveries occur.
-   Document configuration, behavior, limitations, and manual setup for:
    Create a concise implementation plan based on the actual repository
    and revise it as discoveries occur.

### Directive 0006 --- Repository discovery

-   Implement this requirement in the actual repository: Inspect git
    status and avoid overwriting user changes; review the final diff for
    accidental unrelated edits.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Inspect git status and avoid overwriting user changes; review
    the final diff for accidental unrelated edits.
-   Persist all required data and audit events consistently for: Inspect
    git status and avoid overwriting user changes; review the final diff
    for accidental unrelated edits.
-   Add at least one positive test and one relevant negative/failure
    test for: Inspect git status and avoid overwriting user changes;
    review the final diff for accidental unrelated edits.
-   Document configuration, behavior, limitations, and manual setup for:
    Inspect git status and avoid overwriting user changes; review the
    final diff for accidental unrelated edits.

### Directive 0007 --- Repository discovery

-   Implement this requirement in the actual repository: Do not stop
    after planning; implement the agreed backend and verify the real
    repository state.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not stop after planning; implement the agreed backend and
    verify the real repository state.
-   Persist all required data and audit events consistently for: Do not
    stop after planning; implement the agreed backend and verify the
    real repository state.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not stop after planning; implement the agreed backend
    and verify the real repository state.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not stop after planning; implement the agreed backend and verify
    the real repository state.

### Directive 0008 --- Architecture and configuration

-   Implement this requirement in the actual repository: Separate HTTP
    handlers, application/use-case services, domain rules, persistence,
    external adapters, background jobs, and tests.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Separate HTTP handlers, application/use-case services, domain
    rules, persistence, external adapters, background jobs, and tests.
-   Persist all required data and audit events consistently for:
    Separate HTTP handlers, application/use-case services, domain rules,
    persistence, external adapters, background jobs, and tests.
-   Add at least one positive test and one relevant negative/failure
    test for: Separate HTTP handlers, application/use-case services,
    domain rules, persistence, external adapters, background jobs, and
    tests.
-   Document configuration, behavior, limitations, and manual setup for:
    Separate HTTP handlers, application/use-case services, domain rules,
    persistence, external adapters, background jobs, and tests.

### Directive 0009 --- Architecture and configuration

-   Implement this requirement in the actual repository: Keep business
    logic out of controllers and avoid duplicated routing or workflow
    logic.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep business logic out of controllers and avoid duplicated
    routing or workflow logic.
-   Persist all required data and audit events consistently for: Keep
    business logic out of controllers and avoid duplicated routing or
    workflow logic.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep business logic out of controllers and avoid
    duplicated routing or workflow logic.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep business logic out of controllers and avoid duplicated routing
    or workflow logic.

### Directive 0010 --- Architecture and configuration

-   Implement this requirement in the actual repository: Create typed
    central configuration with startup validation for required settings.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create typed central configuration with startup validation for
    required settings.
-   Persist all required data and audit events consistently for: Create
    typed central configuration with startup validation for required
    settings.
-   Add at least one positive test and one relevant negative/failure
    test for: Create typed central configuration with startup validation
    for required settings.
-   Document configuration, behavior, limitations, and manual setup for:
    Create typed central configuration with startup validation for
    required settings.

### Directive 0011 --- Architecture and configuration

-   Implement this requirement in the actual repository: Provide
    `.env.example` with placeholders and descriptions, never real
    credentials.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide `.env.example` with placeholders and descriptions, never
    real credentials.
-   Persist all required data and audit events consistently for: Provide
    `.env.example` with placeholders and descriptions, never real
    credentials.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide `.env.example` with placeholders and descriptions,
    never real credentials.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide `.env.example` with placeholders and descriptions, never
    real credentials.

### Directive 0012 --- Architecture and configuration

-   Implement this requirement in the actual repository: Separate
    development, test, and production settings; production debug mode
    must be disabled by default.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Separate development, test, and production settings; production
    debug mode must be disabled by default.
-   Persist all required data and audit events consistently for:
    Separate development, test, and production settings; production
    debug mode must be disabled by default.
-   Add at least one positive test and one relevant negative/failure
    test for: Separate development, test, and production settings;
    production debug mode must be disabled by default.
-   Document configuration, behavior, limitations, and manual setup for:
    Separate development, test, and production settings; production
    debug mode must be disabled by default.

### Directive 0013 --- Architecture and configuration

-   Implement this requirement in the actual repository: Use explicit
    production CORS origins, request-size limits, upload limits,
    pagination limits, and external-call timeouts.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use explicit production CORS origins, request-size limits,
    upload limits, pagination limits, and external-call timeouts.
-   Persist all required data and audit events consistently for: Use
    explicit production CORS origins, request-size limits, upload
    limits, pagination limits, and external-call timeouts.
-   Add at least one positive test and one relevant negative/failure
    test for: Use explicit production CORS origins, request-size limits,
    upload limits, pagination limits, and external-call timeouts.
-   Document configuration, behavior, limitations, and manual setup for:
    Use explicit production CORS origins, request-size limits, upload
    limits, pagination limits, and external-call timeouts.

### Directive 0014 --- Architecture and configuration

-   Implement this requirement in the actual repository: Make AI, maps,
    email, SMS, and municipal integrations optional through
    configuration.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Make AI, maps, email, SMS, and municipal integrations optional
    through configuration.
-   Persist all required data and audit events consistently for: Make
    AI, maps, email, SMS, and municipal integrations optional through
    configuration.
-   Add at least one positive test and one relevant negative/failure
    test for: Make AI, maps, email, SMS, and municipal integrations
    optional through configuration.
-   Document configuration, behavior, limitations, and manual setup for:
    Make AI, maps, email, SMS, and municipal integrations optional
    through configuration.

### Directive 0015 --- Architecture and configuration

-   Implement this requirement in the actual repository: Provide clear
    startup errors for invalid required configuration without printing
    secrets.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide clear startup errors for invalid required configuration
    without printing secrets.
-   Persist all required data and audit events consistently for: Provide
    clear startup errors for invalid required configuration without
    printing secrets.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide clear startup errors for invalid required
    configuration without printing secrets.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide clear startup errors for invalid required configuration
    without printing secrets.

### Directive 0016 --- Architecture and configuration

-   Implement this requirement in the actual repository: Pin or
    constrain dependencies according to repository conventions and use
    maintained packages.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Pin or constrain dependencies according to repository
    conventions and use maintained packages.
-   Persist all required data and audit events consistently for: Pin or
    constrain dependencies according to repository conventions and use
    maintained packages.
-   Add at least one positive test and one relevant negative/failure
    test for: Pin or constrain dependencies according to repository
    conventions and use maintained packages.
-   Document configuration, behavior, limitations, and manual setup for:
    Pin or constrain dependencies according to repository conventions
    and use maintained packages.

### Directive 0017 --- Architecture and configuration

-   Implement this requirement in the actual repository: Do not
    introduce a message broker, microservices, or complex infrastructure
    without a demonstrated need.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not introduce a message broker, microservices, or complex
    infrastructure without a demonstrated need.
-   Persist all required data and audit events consistently for: Do not
    introduce a message broker, microservices, or complex infrastructure
    without a demonstrated need.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not introduce a message broker, microservices, or
    complex infrastructure without a demonstrated need.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not introduce a message broker, microservices, or complex
    infrastructure without a demonstrated need.

### Directive 0018 --- Database and migrations

-   Implement this requirement in the actual repository: Use one
    canonical persistence model with primary keys, foreign keys, unique
    constraints, NOT NULL constraints, and appropriate indexes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use one canonical persistence model with primary keys, foreign
    keys, unique constraints, NOT NULL constraints, and appropriate
    indexes.
-   Persist all required data and audit events consistently for: Use one
    canonical persistence model with primary keys, foreign keys, unique
    constraints, NOT NULL constraints, and appropriate indexes.
-   Add at least one positive test and one relevant negative/failure
    test for: Use one canonical persistence model with primary keys,
    foreign keys, unique constraints, NOT NULL constraints, and
    appropriate indexes.
-   Document configuration, behavior, limitations, and manual setup for:
    Use one canonical persistence model with primary keys, foreign keys,
    unique constraints, NOT NULL constraints, and appropriate indexes.

### Directive 0019 --- Database and migrations

-   Implement this requirement in the actual repository: Use versioned
    migrations for all schema changes and verify clean-database
    migration.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use versioned migrations for all schema changes and verify
    clean-database migration.
-   Persist all required data and audit events consistently for: Use
    versioned migrations for all schema changes and verify
    clean-database migration.
-   Add at least one positive test and one relevant negative/failure
    test for: Use versioned migrations for all schema changes and verify
    clean-database migration.
-   Document configuration, behavior, limitations, and manual setup for:
    Use versioned migrations for all schema changes and verify
    clean-database migration.

### Directive 0020 --- Database and migrations

-   Implement this requirement in the actual repository: Make migrations
    safe for existing data; do not drop or rewrite data without a
    justified migration plan.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Make migrations safe for existing data; do not drop or rewrite
    data without a justified migration plan.
-   Persist all required data and audit events consistently for: Make
    migrations safe for existing data; do not drop or rewrite data
    without a justified migration plan.
-   Add at least one positive test and one relevant negative/failure
    test for: Make migrations safe for existing data; do not drop or
    rewrite data without a justified migration plan.
-   Document configuration, behavior, limitations, and manual setup for:
    Make migrations safe for existing data; do not drop or rewrite data
    without a justified migration plan.

### Directive 0021 --- Database and migrations

-   Implement this requirement in the actual repository: Use
    transactions for complaint creation, status transitions, assignment
    changes, audit history, and related required records.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use transactions for complaint creation, status transitions,
    assignment changes, audit history, and related required records.
-   Persist all required data and audit events consistently for: Use
    transactions for complaint creation, status transitions, assignment
    changes, audit history, and related required records.
-   Add at least one positive test and one relevant negative/failure
    test for: Use transactions for complaint creation, status
    transitions, assignment changes, audit history, and related required
    records.
-   Document configuration, behavior, limitations, and manual setup for:
    Use transactions for complaint creation, status transitions,
    assignment changes, audit history, and related required records.

### Directive 0022 --- Database and migrations

-   Implement this requirement in the actual repository: Use database
    constraints as the final protection for uniqueness and critical
    invariants.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use database constraints as the final protection for uniqueness
    and critical invariants.
-   Persist all required data and audit events consistently for: Use
    database constraints as the final protection for uniqueness and
    critical invariants.
-   Add at least one positive test and one relevant negative/failure
    test for: Use database constraints as the final protection for
    uniqueness and critical invariants.
-   Document configuration, behavior, limitations, and manual setup for:
    Use database constraints as the final protection for uniqueness and
    critical invariants.

### Directive 0023 --- Database and migrations

-   Implement this requirement in the actual repository: Use optimistic
    locking or row locks where concurrent edits could overwrite each
    other.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use optimistic locking or row locks where concurrent edits could
    overwrite each other.
-   Persist all required data and audit events consistently for: Use
    optimistic locking or row locks where concurrent edits could
    overwrite each other.
-   Add at least one positive test and one relevant negative/failure
    test for: Use optimistic locking or row locks where concurrent edits
    could overwrite each other.
-   Document configuration, behavior, limitations, and manual setup for:
    Use optimistic locking or row locks where concurrent edits could
    overwrite each other.

### Directive 0024 --- Database and migrations

-   Implement this requirement in the actual repository: Use UTC-aware
    timestamps and document timestamp semantics.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use UTC-aware timestamps and document timestamp semantics.
-   Persist all required data and audit events consistently for: Use
    UTC-aware timestamps and document timestamp semantics.
-   Add at least one positive test and one relevant negative/failure
    test for: Use UTC-aware timestamps and document timestamp semantics.
-   Document configuration, behavior, limitations, and manual setup for:
    Use UTC-aware timestamps and document timestamp semantics.

### Directive 0025 --- Database and migrations

-   Implement this requirement in the actual repository: Prefer archival
    or soft deletion for records requiring history; do not
    cascade-delete audit evidence.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prefer archival or soft deletion for records requiring history;
    do not cascade-delete audit evidence.
-   Persist all required data and audit events consistently for: Prefer
    archival or soft deletion for records requiring history; do not
    cascade-delete audit evidence.
-   Add at least one positive test and one relevant negative/failure
    test for: Prefer archival or soft deletion for records requiring
    history; do not cascade-delete audit evidence.
-   Document configuration, behavior, limitations, and manual setup for:
    Prefer archival or soft deletion for records requiring history; do
    not cascade-delete audit evidence.

### Directive 0026 --- Database and migrations

-   Implement this requirement in the actual repository: Provide a
    repeatable seed command and a test database that cannot accidentally
    touch production.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a repeatable seed command and a test database that
    cannot accidentally touch production.
-   Persist all required data and audit events consistently for: Provide
    a repeatable seed command and a test database that cannot
    accidentally touch production.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a repeatable seed command and a test database that
    cannot accidentally touch production.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a repeatable seed command and a test database that cannot
    accidentally touch production.

### Directive 0027 --- Database and migrations

-   Implement this requirement in the actual repository: Document
    backup, restore, migration, and data-retention expectations.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document backup, restore, migration, and data-retention
    expectations.
-   Persist all required data and audit events consistently for:
    Document backup, restore, migration, and data-retention
    expectations.
-   Add at least one positive test and one relevant negative/failure
    test for: Document backup, restore, migration, and data-retention
    expectations.
-   Document configuration, behavior, limitations, and manual setup for:
    Document backup, restore, migration, and data-retention
    expectations.

### Directive 0028 --- Users and authentication

-   Implement this requirement in the actual repository: Create user
    identity and profile models with stable IDs and only necessary
    personal data.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create user identity and profile models with stable IDs and only
    necessary personal data.
-   Persist all required data and audit events consistently for: Create
    user identity and profile models with stable IDs and only necessary
    personal data.
-   Add at least one positive test and one relevant negative/failure
    test for: Create user identity and profile models with stable IDs
    and only necessary personal data.
-   Document configuration, behavior, limitations, and manual setup for:
    Create user identity and profile models with stable IDs and only
    necessary personal data.

### Directive 0029 --- Users and authentication

-   Implement this requirement in the actual repository: Support
    resident and municipal staff identities; support account
    deactivation without breaking historical complaints.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support resident and municipal staff identities; support account
    deactivation without breaking historical complaints.
-   Persist all required data and audit events consistently for: Support
    resident and municipal staff identities; support account
    deactivation without breaking historical complaints.
-   Add at least one positive test and one relevant negative/failure
    test for: Support resident and municipal staff identities; support
    account deactivation without breaking historical complaints.
-   Document configuration, behavior, limitations, and manual setup for:
    Support resident and municipal staff identities; support account
    deactivation without breaking historical complaints.

### Directive 0030 --- Users and authentication

-   Implement this requirement in the actual repository: Use a mature
    authentication provider/library where practical.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use a mature authentication provider/library where practical.
-   Persist all required data and audit events consistently for: Use a
    mature authentication provider/library where practical.
-   Add at least one positive test and one relevant negative/failure
    test for: Use a mature authentication provider/library where
    practical.
-   Document configuration, behavior, limitations, and manual setup for:
    Use a mature authentication provider/library where practical.

### Directive 0031 --- Users and authentication

-   Implement this requirement in the actual repository: If storing
    passwords, use modern password hashing; never store plaintext
    passwords.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: If storing passwords, use modern password hashing; never store
    plaintext passwords.
-   Persist all required data and audit events consistently for: If
    storing passwords, use modern password hashing; never store
    plaintext passwords.
-   Add at least one positive test and one relevant negative/failure
    test for: If storing passwords, use modern password hashing; never
    store plaintext passwords.
-   Document configuration, behavior, limitations, and manual setup for:
    If storing passwords, use modern password hashing; never store
    plaintext passwords.

### Directive 0032 --- Users and authentication

-   Implement this requirement in the actual repository: Use secure
    recovery and verification tokens if those flows are implemented.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use secure recovery and verification tokens if those flows are
    implemented.
-   Persist all required data and audit events consistently for: Use
    secure recovery and verification tokens if those flows are
    implemented.
-   Add at least one positive test and one relevant negative/failure
    test for: Use secure recovery and verification tokens if those flows
    are implemented.
-   Document configuration, behavior, limitations, and manual setup for:
    Use secure recovery and verification tokens if those flows are
    implemented.

### Directive 0033 --- Users and authentication

-   Implement this requirement in the actual repository: Rate-limit
    login and recovery; use generic failure messages that do not reveal
    account existence.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Rate-limit login and recovery; use generic failure messages that
    do not reveal account existence.
-   Persist all required data and audit events consistently for:
    Rate-limit login and recovery; use generic failure messages that do
    not reveal account existence.
-   Add at least one positive test and one relevant negative/failure
    test for: Rate-limit login and recovery; use generic failure
    messages that do not reveal account existence.
-   Document configuration, behavior, limitations, and manual setup for:
    Rate-limit login and recovery; use generic failure messages that do
    not reveal account existence.

### Directive 0034 --- Users and authentication

-   Implement this requirement in the actual repository: Validate token
    issuer, audience, expiry, signature, and revocation where relevant.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate token issuer, audience, expiry, signature, and
    revocation where relevant.
-   Persist all required data and audit events consistently for:
    Validate token issuer, audience, expiry, signature, and revocation
    where relevant.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate token issuer, audience, expiry, signature, and
    revocation where relevant.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate token issuer, audience, expiry, signature, and revocation
    where relevant.

### Directive 0035 --- Users and authentication

-   Implement this requirement in the actual repository: Use secure,
    HTTP-only, SameSite cookies and CSRF protection when applicable to
    the chosen session design.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use secure, HTTP-only, SameSite cookies and CSRF protection when
    applicable to the chosen session design.
-   Persist all required data and audit events consistently for: Use
    secure, HTTP-only, SameSite cookies and CSRF protection when
    applicable to the chosen session design.
-   Add at least one positive test and one relevant negative/failure
    test for: Use secure, HTTP-only, SameSite cookies and CSRF
    protection when applicable to the chosen session design.
-   Document configuration, behavior, limitations, and manual setup for:
    Use secure, HTTP-only, SameSite cookies and CSRF protection when
    applicable to the chosen session design.

### Directive 0036 --- Users and authentication

-   Implement this requirement in the actual repository: Never store
    long-lived secrets in URLs or expose password hashes in API
    responses.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never store long-lived secrets in URLs or expose password hashes
    in API responses.
-   Persist all required data and audit events consistently for: Never
    store long-lived secrets in URLs or expose password hashes in API
    responses.
-   Add at least one positive test and one relevant negative/failure
    test for: Never store long-lived secrets in URLs or expose password
    hashes in API responses.
-   Document configuration, behavior, limitations, and manual setup for:
    Never store long-lived secrets in URLs or expose password hashes in
    API responses.

### Directive 0037 --- Users and authentication

-   Implement this requirement in the actual repository: Test missing,
    invalid, expired, revoked, and unauthorized credentials.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test missing, invalid, expired, revoked, and unauthorized
    credentials.
-   Persist all required data and audit events consistently for: Test
    missing, invalid, expired, revoked, and unauthorized credentials.
-   Add at least one positive test and one relevant negative/failure
    test for: Test missing, invalid, expired, revoked, and unauthorized
    credentials.
-   Document configuration, behavior, limitations, and manual setup for:
    Test missing, invalid, expired, revoked, and unauthorized
    credentials.

### Directive 0038 --- Roles and permissions

-   Implement this requirement in the actual repository: Implement
    server-side role-based access control plus department/ward scope
    where relevant.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Implement server-side role-based access control plus
    department/ward scope where relevant.
-   Persist all required data and audit events consistently for:
    Implement server-side role-based access control plus department/ward
    scope where relevant.
-   Add at least one positive test and one relevant negative/failure
    test for: Implement server-side role-based access control plus
    department/ward scope where relevant.
-   Document configuration, behavior, limitations, and manual setup for:
    Implement server-side role-based access control plus department/ward
    scope where relevant.

### Directive 0039 --- Roles and permissions

-   Implement this requirement in the actual repository: Support
    resident, field officer, department supervisor, municipal
    administrator, system administrator, and read-only auditor roles as
    appropriate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support resident, field officer, department supervisor,
    municipal administrator, system administrator, and read-only auditor
    roles as appropriate.
-   Persist all required data and audit events consistently for: Support
    resident, field officer, department supervisor, municipal
    administrator, system administrator, and read-only auditor roles as
    appropriate.
-   Add at least one positive test and one relevant negative/failure
    test for: Support resident, field officer, department supervisor,
    municipal administrator, system administrator, and read-only auditor
    roles as appropriate.
-   Document configuration, behavior, limitations, and manual setup for:
    Support resident, field officer, department supervisor, municipal
    administrator, system administrator, and read-only auditor roles as
    appropriate.

### Directive 0040 --- Roles and permissions

-   Implement this requirement in the actual repository: Use
    deny-by-default access policies and centralized permission checks.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use deny-by-default access policies and centralized permission
    checks.
-   Persist all required data and audit events consistently for: Use
    deny-by-default access policies and centralized permission checks.
-   Add at least one positive test and one relevant negative/failure
    test for: Use deny-by-default access policies and centralized
    permission checks.
-   Document configuration, behavior, limitations, and manual setup for:
    Use deny-by-default access policies and centralized permission
    checks.

### Directive 0041 --- Roles and permissions

-   Implement this requirement in the actual repository: Residents may
    access their own private complaints and only explicitly public
    summaries of other complaints.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Residents may access their own private complaints and only
    explicitly public summaries of other complaints.
-   Persist all required data and audit events consistently for:
    Residents may access their own private complaints and only
    explicitly public summaries of other complaints.
-   Add at least one positive test and one relevant negative/failure
    test for: Residents may access their own private complaints and only
    explicitly public summaries of other complaints.
-   Document configuration, behavior, limitations, and manual setup for:
    Residents may access their own private complaints and only
    explicitly public summaries of other complaints.

### Directive 0042 --- Roles and permissions

-   Implement this requirement in the actual repository: Residents must
    not change status, department, officer assignment, audit timestamps,
    or privileged fields directly.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Residents must not change status, department, officer
    assignment, audit timestamps, or privileged fields directly.
-   Persist all required data and audit events consistently for:
    Residents must not change status, department, officer assignment,
    audit timestamps, or privileged fields directly.
-   Add at least one positive test and one relevant negative/failure
    test for: Residents must not change status, department, officer
    assignment, audit timestamps, or privileged fields directly.
-   Document configuration, behavior, limitations, and manual setup for:
    Residents must not change status, department, officer assignment,
    audit timestamps, or privileged fields directly.

### Directive 0043 --- Roles and permissions

-   Implement this requirement in the actual repository: Field officers
    may access only assigned cases or their authorized team/department
    scope.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Field officers may access only assigned cases or their
    authorized team/department scope.
-   Persist all required data and audit events consistently for: Field
    officers may access only assigned cases or their authorized
    team/department scope.
-   Add at least one positive test and one relevant negative/failure
    test for: Field officers may access only assigned cases or their
    authorized team/department scope.
-   Document configuration, behavior, limitations, and manual setup for:
    Field officers may access only assigned cases or their authorized
    team/department scope.

### Directive 0044 --- Roles and permissions

-   Implement this requirement in the actual repository: Supervisors may
    assign and reassign cases within their authorized scope and inspect
    overdue work.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Supervisors may assign and reassign cases within their
    authorized scope and inspect overdue work.
-   Persist all required data and audit events consistently for:
    Supervisors may assign and reassign cases within their authorized
    scope and inspect overdue work.
-   Add at least one positive test and one relevant negative/failure
    test for: Supervisors may assign and reassign cases within their
    authorized scope and inspect overdue work.
-   Document configuration, behavior, limitations, and manual setup for:
    Supervisors may assign and reassign cases within their authorized
    scope and inspect overdue work.

### Directive 0045 --- Roles and permissions

-   Implement this requirement in the actual repository: Only authorized
    administrators may change categories, departments, routing rules,
    SLA policies, roles, or global settings.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Only authorized administrators may change categories,
    departments, routing rules, SLA policies, roles, or global settings.
-   Persist all required data and audit events consistently for: Only
    authorized administrators may change categories, departments,
    routing rules, SLA policies, roles, or global settings.
-   Add at least one positive test and one relevant negative/failure
    test for: Only authorized administrators may change categories,
    departments, routing rules, SLA policies, roles, or global settings.
-   Document configuration, behavior, limitations, and manual setup for:
    Only authorized administrators may change categories, departments,
    routing rules, SLA policies, roles, or global settings.

### Directive 0046 --- Roles and permissions

-   Implement this requirement in the actual repository: Internal notes,
    private evidence, audit logs, exports, and analytics must be
    protected by explicit permissions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Internal notes, private evidence, audit logs, exports, and
    analytics must be protected by explicit permissions.
-   Persist all required data and audit events consistently for:
    Internal notes, private evidence, audit logs, exports, and analytics
    must be protected by explicit permissions.
-   Add at least one positive test and one relevant negative/failure
    test for: Internal notes, private evidence, audit logs, exports, and
    analytics must be protected by explicit permissions.
-   Document configuration, behavior, limitations, and manual setup for:
    Internal notes, private evidence, audit logs, exports, and analytics
    must be protected by explicit permissions.

### Directive 0047 --- Roles and permissions

-   Implement this requirement in the actual repository: Test IDOR,
    cross-user access, cross-department access, privilege escalation,
    and direct API calls bypassing the UI.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test IDOR, cross-user access, cross-department access, privilege
    escalation, and direct API calls bypassing the UI.
-   Persist all required data and audit events consistently for: Test
    IDOR, cross-user access, cross-department access, privilege
    escalation, and direct API calls bypassing the UI.
-   Add at least one positive test and one relevant negative/failure
    test for: Test IDOR, cross-user access, cross-department access,
    privilege escalation, and direct API calls bypassing the UI.
-   Document configuration, behavior, limitations, and manual setup for:
    Test IDOR, cross-user access, cross-department access, privilege
    escalation, and direct API calls bypassing the UI.

### Directive 0048 --- Departments and officers

-   Implement this requirement in the actual repository: Create
    departments with stable ID, name, code, description, active state,
    public contact fields, and service coverage.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create departments with stable ID, name, code, description,
    active state, public contact fields, and service coverage.
-   Persist all required data and audit events consistently for: Create
    departments with stable ID, name, code, description, active state,
    public contact fields, and service coverage.
-   Add at least one positive test and one relevant negative/failure
    test for: Create departments with stable ID, name, code,
    description, active state, public contact fields, and service
    coverage.
-   Document configuration, behavior, limitations, and manual setup for:
    Create departments with stable ID, name, code, description, active
    state, public contact fields, and service coverage.

### Directive 0049 --- Departments and officers

-   Implement this requirement in the actual repository: Support
    officers, team membership, supervisor relationships, and
    active/inactive status.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support officers, team membership, supervisor relationships, and
    active/inactive status.
-   Persist all required data and audit events consistently for: Support
    officers, team membership, supervisor relationships, and
    active/inactive status.
-   Add at least one positive test and one relevant negative/failure
    test for: Support officers, team membership, supervisor
    relationships, and active/inactive status.
-   Document configuration, behavior, limitations, and manual setup for:
    Support officers, team membership, supervisor relationships, and
    active/inactive status.

### Directive 0050 --- Departments and officers

-   Implement this requirement in the actual repository: Do not assign
    new work to inactive officers or departments without an explicit
    policy exception.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not assign new work to inactive officers or departments
    without an explicit policy exception.
-   Persist all required data and audit events consistently for: Do not
    assign new work to inactive officers or departments without an
    explicit policy exception.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not assign new work to inactive officers or departments
    without an explicit policy exception.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not assign new work to inactive officers or departments without
    an explicit policy exception.

### Directive 0051 --- Departments and officers

-   Implement this requirement in the actual repository: Support
    assignment to an officer or team queue.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support assignment to an officer or team queue.
-   Persist all required data and audit events consistently for: Support
    assignment to an officer or team queue.
-   Add at least one positive test and one relevant negative/failure
    test for: Support assignment to an officer or team queue.
-   Document configuration, behavior, limitations, and manual setup for:
    Support assignment to an officer or team queue.

### Directive 0052 --- Departments and officers

-   Implement this requirement in the actual repository: Record every
    assignment and reassignment with actor, old/new owner, timestamp,
    and reason.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record every assignment and reassignment with actor, old/new
    owner, timestamp, and reason.
-   Persist all required data and audit events consistently for: Record
    every assignment and reassignment with actor, old/new owner,
    timestamp, and reason.
-   Add at least one positive test and one relevant negative/failure
    test for: Record every assignment and reassignment with actor,
    old/new owner, timestamp, and reason.
-   Document configuration, behavior, limitations, and manual setup for:
    Record every assignment and reassignment with actor, old/new owner,
    timestamp, and reason.

### Directive 0053 --- Departments and officers

-   Implement this requirement in the actual repository: Require a
    reason for manual reassignment and preserve the original routing
    decision.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Require a reason for manual reassignment and preserve the
    original routing decision.
-   Persist all required data and audit events consistently for: Require
    a reason for manual reassignment and preserve the original routing
    decision.
-   Add at least one positive test and one relevant negative/failure
    test for: Require a reason for manual reassignment and preserve the
    original routing decision.
-   Document configuration, behavior, limitations, and manual setup for:
    Require a reason for manual reassignment and preserve the original
    routing decision.

### Directive 0054 --- Departments and officers

-   Implement this requirement in the actual repository: Provide an
    unassigned/triage queue when no responsible team is known.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide an unassigned/triage queue when no responsible team is
    known.
-   Persist all required data and audit events consistently for: Provide
    an unassigned/triage queue when no responsible team is known.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide an unassigned/triage queue when no responsible
    team is known.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide an unassigned/triage queue when no responsible team is
    known.

### Directive 0055 --- Departments and officers

-   Implement this requirement in the actual repository: Allow
    department deactivation without deleting historical complaints or
    assignments.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow department deactivation without deleting historical
    complaints or assignments.
-   Persist all required data and audit events consistently for: Allow
    department deactivation without deleting historical complaints or
    assignments.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow department deactivation without deleting historical
    complaints or assignments.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow department deactivation without deleting historical complaints
    or assignments.

### Directive 0056 --- Departments and officers

-   Implement this requirement in the actual repository: Keep internal
    staff notes private from residents.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep internal staff notes private from residents.
-   Persist all required data and audit events consistently for: Keep
    internal staff notes private from residents.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep internal staff notes private from residents.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep internal staff notes private from residents.

### Directive 0057 --- Departments and officers

-   Implement this requirement in the actual repository: Test assignment
    scope, inactive staff, missing teams, and unauthorized reassignment.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test assignment scope, inactive staff, missing teams, and
    unauthorized reassignment.
-   Persist all required data and audit events consistently for: Test
    assignment scope, inactive staff, missing teams, and unauthorized
    reassignment.
-   Add at least one positive test and one relevant negative/failure
    test for: Test assignment scope, inactive staff, missing teams, and
    unauthorized reassignment.
-   Document configuration, behavior, limitations, and manual setup for:
    Test assignment scope, inactive staff, missing teams, and
    unauthorized reassignment.

### Directive 0058 --- Service directory

-   Implement this requirement in the actual repository: Create a
    service catalogue with ID, name, summary, detailed instructions,
    department relationships, categories, active state, and optional
    public contact details.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create a service catalogue with ID, name, summary, detailed
    instructions, department relationships, categories, active state,
    and optional public contact details.
-   Persist all required data and audit events consistently for: Create
    a service catalogue with ID, name, summary, detailed instructions,
    department relationships, categories, active state, and optional
    public contact details.
-   Add at least one positive test and one relevant negative/failure
    test for: Create a service catalogue with ID, name, summary,
    detailed instructions, department relationships, categories, active
    state, and optional public contact details.
-   Document configuration, behavior, limitations, and manual setup for:
    Create a service catalogue with ID, name, summary, detailed
    instructions, department relationships, categories, active state,
    and optional public contact details.

### Directive 0059 --- Service directory

-   Implement this requirement in the actual repository: Support search
    by name, description, synonyms, category, and optional
    natural-language query.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support search by name, description, synonyms, category, and
    optional natural-language query.
-   Persist all required data and audit events consistently for: Support
    search by name, description, synonyms, category, and optional
    natural-language query.
-   Add at least one positive test and one relevant negative/failure
    test for: Support search by name, description, synonyms, category,
    and optional natural-language query.
-   Document configuration, behavior, limitations, and manual setup for:
    Support search by name, description, synonyms, category, and
    optional natural-language query.

### Directive 0060 --- Service directory

-   Implement this requirement in the actual repository: Store operating
    hours, eligibility, and required information only when verified and
    maintained.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store operating hours, eligibility, and required information
    only when verified and maintained.
-   Persist all required data and audit events consistently for: Store
    operating hours, eligibility, and required information only when
    verified and maintained.
-   Add at least one positive test and one relevant negative/failure
    test for: Store operating hours, eligibility, and required
    information only when verified and maintained.
-   Document configuration, behavior, limitations, and manual setup for:
    Store operating hours, eligibility, and required information only
    when verified and maintained.

### Directive 0061 --- Service directory

-   Implement this requirement in the actual repository: Allow
    administrators to publish, unpublish, or mark services temporarily
    unavailable.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow administrators to publish, unpublish, or mark services
    temporarily unavailable.
-   Persist all required data and audit events consistently for: Allow
    administrators to publish, unpublish, or mark services temporarily
    unavailable.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow administrators to publish, unpublish, or mark
    services temporarily unavailable.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow administrators to publish, unpublish, or mark services
    temporarily unavailable.

### Directive 0062 --- Service directory

-   Implement this requirement in the actual repository: Provide a safe
    no-match response instead of inventing a service or department.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a safe no-match response instead of inventing a service
    or department.
-   Persist all required data and audit events consistently for: Provide
    a safe no-match response instead of inventing a service or
    department.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a safe no-match response instead of inventing a
    service or department.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a safe no-match response instead of inventing a service or
    department.

### Directive 0063 --- Service directory

-   Implement this requirement in the actual repository: Distinguish
    information services from complaint-reporting services.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Distinguish information services from complaint-reporting
    services.
-   Persist all required data and audit events consistently for:
    Distinguish information services from complaint-reporting services.
-   Add at least one positive test and one relevant negative/failure
    test for: Distinguish information services from complaint-reporting
    services.
-   Document configuration, behavior, limitations, and manual setup for:
    Distinguish information services from complaint-reporting services.

### Directive 0064 --- Service directory

-   Implement this requirement in the actual repository: Store
    last-reviewed timestamp and service owner where practical.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store last-reviewed timestamp and service owner where practical.
-   Persist all required data and audit events consistently for: Store
    last-reviewed timestamp and service owner where practical.
-   Add at least one positive test and one relevant negative/failure
    test for: Store last-reviewed timestamp and service owner where
    practical.
-   Document configuration, behavior, limitations, and manual setup for:
    Store last-reviewed timestamp and service owner where practical.

### Directive 0065 --- Service directory

-   Implement this requirement in the actual repository: Do not hardcode
    service catalogue data into route handlers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not hardcode service catalogue data into route handlers.
-   Persist all required data and audit events consistently for: Do not
    hardcode service catalogue data into route handlers.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not hardcode service catalogue data into route
    handlers.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not hardcode service catalogue data into route handlers.

### Directive 0066 --- Service directory

-   Implement this requirement in the actual repository: Do not invent
    official government eligibility rules, contact details, service
    guarantees, or legal deadlines.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not invent official government eligibility rules, contact
    details, service guarantees, or legal deadlines.
-   Persist all required data and audit events consistently for: Do not
    invent official government eligibility rules, contact details,
    service guarantees, or legal deadlines.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not invent official government eligibility rules,
    contact details, service guarantees, or legal deadlines.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not invent official government eligibility rules, contact
    details, service guarantees, or legal deadlines.

### Directive 0067 --- Service directory

-   Implement this requirement in the actual repository: Test search,
    filters, inactive services, no-match behavior, and department
    relationships.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test search, filters, inactive services, no-match behavior, and
    department relationships.
-   Persist all required data and audit events consistently for: Test
    search, filters, inactive services, no-match behavior, and
    department relationships.
-   Add at least one positive test and one relevant negative/failure
    test for: Test search, filters, inactive services, no-match
    behavior, and department relationships.
-   Document configuration, behavior, limitations, and manual setup for:
    Test search, filters, inactive services, no-match behavior, and
    department relationships.

### Directive 0068 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Create
    categories and optional subcategories with stable IDs, labels,
    descriptions, synonyms, active state, and optional examples.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create categories and optional subcategories with stable IDs,
    labels, descriptions, synonyms, active state, and optional examples.
-   Persist all required data and audit events consistently for: Create
    categories and optional subcategories with stable IDs, labels,
    descriptions, synonyms, active state, and optional examples.
-   Add at least one positive test and one relevant negative/failure
    test for: Create categories and optional subcategories with stable
    IDs, labels, descriptions, synonyms, active state, and optional
    examples.
-   Document configuration, behavior, limitations, and manual setup for:
    Create categories and optional subcategories with stable IDs,
    labels, descriptions, synonyms, active state, and optional examples.

### Directive 0069 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Map categories
    to routing rules, default priorities, and SLA policies through
    data/configuration.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Map categories to routing rules, default priorities, and SLA
    policies through data/configuration.
-   Persist all required data and audit events consistently for: Map
    categories to routing rules, default priorities, and SLA policies
    through data/configuration.
-   Add at least one positive test and one relevant negative/failure
    test for: Map categories to routing rules, default priorities, and
    SLA policies through data/configuration.
-   Document configuration, behavior, limitations, and manual setup for:
    Map categories to routing rules, default priorities, and SLA
    policies through data/configuration.

### Directive 0070 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Allow a
    category to be disabled without deleting historical records.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow a category to be disabled without deleting historical
    records.
-   Persist all required data and audit events consistently for: Allow a
    category to be disabled without deleting historical records.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow a category to be disabled without deleting
    historical records.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow a category to be disabled without deleting historical records.

### Directive 0071 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Validate
    submitted category IDs and support an explicit unknown/other or
    triage fallback.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate submitted category IDs and support an explicit
    unknown/other or triage fallback.
-   Persist all required data and audit events consistently for:
    Validate submitted category IDs and support an explicit
    unknown/other or triage fallback.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate submitted category IDs and support an explicit
    unknown/other or triage fallback.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate submitted category IDs and support an explicit
    unknown/other or triage fallback.

### Directive 0072 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Keep
    resident-selected category separate from later staff-corrected
    category where auditability matters.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep resident-selected category separate from later
    staff-corrected category where auditability matters.
-   Persist all required data and audit events consistently for: Keep
    resident-selected category separate from later staff-corrected
    category where auditability matters.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep resident-selected category separate from later
    staff-corrected category where auditability matters.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep resident-selected category separate from later staff-corrected
    category where auditability matters.

### Directive 0073 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Record who
    corrected a category, when, why, and whether routing was
    recalculated.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record who corrected a category, when, why, and whether routing
    was recalculated.
-   Persist all required data and audit events consistently for: Record
    who corrected a category, when, why, and whether routing was
    recalculated.
-   Add at least one positive test and one relevant negative/failure
    test for: Record who corrected a category, when, why, and whether
    routing was recalculated.
-   Document configuration, behavior, limitations, and manual setup for:
    Record who corrected a category, when, why, and whether routing was
    recalculated.

### Directive 0074 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Support
    localizable labels if multilingual support is enabled.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support localizable labels if multilingual support is enabled.
-   Persist all required data and audit events consistently for: Support
    localizable labels if multilingual support is enabled.
-   Add at least one positive test and one relevant negative/failure
    test for: Support localizable labels if multilingual support is
    enabled.
-   Document configuration, behavior, limitations, and manual setup for:
    Support localizable labels if multilingual support is enabled.

### Directive 0075 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Do not let
    ambiguous keywords route a complaint with unjustified certainty.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not let ambiguous keywords route a complaint with unjustified
    certainty.
-   Persist all required data and audit events consistently for: Do not
    let ambiguous keywords route a complaint with unjustified certainty.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not let ambiguous keywords route a complaint with
    unjustified certainty.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not let ambiguous keywords route a complaint with unjustified
    certainty.

### Directive 0076 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Use consistent
    taxonomy IDs across database, API, tests, and seed data.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use consistent taxonomy IDs across database, API, tests, and
    seed data.
-   Persist all required data and audit events consistently for: Use
    consistent taxonomy IDs across database, API, tests, and seed data.
-   Add at least one positive test and one relevant negative/failure
    test for: Use consistent taxonomy IDs across database, API, tests,
    and seed data.
-   Document configuration, behavior, limitations, and manual setup for:
    Use consistent taxonomy IDs across database, API, tests, and seed
    data.

### Directive 0077 --- Categories and taxonomy

-   Implement this requirement in the actual repository: Test invalid,
    inactive, ambiguous, parent/child, and unknown categories.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test invalid, inactive, ambiguous, parent/child, and unknown
    categories.
-   Persist all required data and audit events consistently for: Test
    invalid, inactive, ambiguous, parent/child, and unknown categories.
-   Add at least one positive test and one relevant negative/failure
    test for: Test invalid, inactive, ambiguous, parent/child, and
    unknown categories.
-   Document configuration, behavior, limitations, and manual setup for:
    Test invalid, inactive, ambiguous, parent/child, and unknown
    categories.

### Directive 0078 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Represent
    wards/zones and store stable IDs, display names, active state, and
    verified boundary data where available.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Represent wards/zones and store stable IDs, display names,
    active state, and verified boundary data where available.
-   Persist all required data and audit events consistently for:
    Represent wards/zones and store stable IDs, display names, active
    state, and verified boundary data where available.
-   Add at least one positive test and one relevant negative/failure
    test for: Represent wards/zones and store stable IDs, display names,
    active state, and verified boundary data where available.
-   Document configuration, behavior, limitations, and manual setup for:
    Represent wards/zones and store stable IDs, display names, active
    state, and verified boundary data where available.

### Directive 0079 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Never fabricate
    official ward boundaries; document provenance and limitations of
    geographic data.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never fabricate official ward boundaries; document provenance
    and limitations of geographic data.
-   Persist all required data and audit events consistently for: Never
    fabricate official ward boundaries; document provenance and
    limitations of geographic data.
-   Add at least one positive test and one relevant negative/failure
    test for: Never fabricate official ward boundaries; document
    provenance and limitations of geographic data.
-   Document configuration, behavior, limitations, and manual setup for:
    Never fabricate official ward boundaries; document provenance and
    limitations of geographic data.

### Directive 0080 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Validate
    latitude and longitude ranges and preserve location source/accuracy
    when available.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate latitude and longitude ranges and preserve location
    source/accuracy when available.
-   Persist all required data and audit events consistently for:
    Validate latitude and longitude ranges and preserve location
    source/accuracy when available.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate latitude and longitude ranges and preserve
    location source/accuracy when available.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate latitude and longitude ranges and preserve location
    source/accuracy when available.

### Directive 0081 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Allow manual
    location selection when GPS is unavailable or inaccurate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow manual location selection when GPS is unavailable or
    inaccurate.
-   Persist all required data and audit events consistently for: Allow
    manual location selection when GPS is unavailable or inaccurate.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow manual location selection when GPS is unavailable or
    inaccurate.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow manual location selection when GPS is unavailable or
    inaccurate.

### Directive 0082 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Resolve
    jurisdiction through verified boundaries or configured rules, not
    guessed addresses.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Resolve jurisdiction through verified boundaries or configured
    rules, not guessed addresses.
-   Persist all required data and audit events consistently for: Resolve
    jurisdiction through verified boundaries or configured rules, not
    guessed addresses.
-   Add at least one positive test and one relevant negative/failure
    test for: Resolve jurisdiction through verified boundaries or
    configured rules, not guessed addresses.
-   Document configuration, behavior, limitations, and manual setup for:
    Resolve jurisdiction through verified boundaries or configured
    rules, not guessed addresses.

### Directive 0083 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Support
    department coverage by ward, zone, or service boundary.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support department coverage by ward, zone, or service boundary.
-   Persist all required data and audit events consistently for: Support
    department coverage by ward, zone, or service boundary.
-   Add at least one positive test and one relevant negative/failure
    test for: Support department coverage by ward, zone, or service
    boundary.
-   Document configuration, behavior, limitations, and manual setup for:
    Support department coverage by ward, zone, or service boundary.

### Directive 0084 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Handle missing
    coordinates and out-of-area reports with a documented fallback.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle missing coordinates and out-of-area reports with a
    documented fallback.
-   Persist all required data and audit events consistently for: Handle
    missing coordinates and out-of-area reports with a documented
    fallback.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle missing coordinates and out-of-area reports with a
    documented fallback.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle missing coordinates and out-of-area reports with a documented
    fallback.

### Directive 0085 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Support nearby
    issue queries with bounded radius, result count, and privacy
    filtering.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support nearby issue queries with bounded radius, result count,
    and privacy filtering.
-   Persist all required data and audit events consistently for: Support
    nearby issue queries with bounded radius, result count, and privacy
    filtering.
-   Add at least one positive test and one relevant negative/failure
    test for: Support nearby issue queries with bounded radius, result
    count, and privacy filtering.
-   Document configuration, behavior, limitations, and manual setup for:
    Support nearby issue queries with bounded radius, result count, and
    privacy filtering.

### Directive 0086 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Use spatial
    indexes if PostGIS or another spatial engine is used.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use spatial indexes if PostGIS or another spatial engine is
    used.
-   Persist all required data and audit events consistently for: Use
    spatial indexes if PostGIS or another spatial engine is used.
-   Add at least one positive test and one relevant negative/failure
    test for: Use spatial indexes if PostGIS or another spatial engine
    is used.
-   Document configuration, behavior, limitations, and manual setup for:
    Use spatial indexes if PostGIS or another spatial engine is used.

### Directive 0087 --- Wards, zones, and location

-   Implement this requirement in the actual repository: Never expose
    private exact coordinates through public APIs unless explicitly
    approved by policy.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never expose private exact coordinates through public APIs
    unless explicitly approved by policy.
-   Persist all required data and audit events consistently for: Never
    expose private exact coordinates through public APIs unless
    explicitly approved by policy.
-   Add at least one positive test and one relevant negative/failure
    test for: Never expose private exact coordinates through public APIs
    unless explicitly approved by policy.
-   Document configuration, behavior, limitations, and manual setup for:
    Never expose private exact coordinates through public APIs unless
    explicitly approved by policy.

### Directive 0088 --- Complaint model

-   Implement this requirement in the actual repository: Store internal
    ID, unique human-readable reference, reporter, title, description,
    category/subcategory, location, visibility, priority, status,
    department, assignment, timestamps, deadline, resolution, and
    optional external case reference.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store internal ID, unique human-readable reference, reporter,
    title, description, category/subcategory, location, visibility,
    priority, status, department, assignment, timestamps, deadline,
    resolution, and optional external case reference.
-   Persist all required data and audit events consistently for: Store
    internal ID, unique human-readable reference, reporter, title,
    description, category/subcategory, location, visibility, priority,
    status, department, assignment, timestamps, deadline, resolution,
    and optional external case reference.
-   Add at least one positive test and one relevant negative/failure
    test for: Store internal ID, unique human-readable reference,
    reporter, title, description, category/subcategory, location,
    visibility, priority, status, department, assignment, timestamps,
    deadline, resolution, and optional external case reference.
-   Document configuration, behavior, limitations, and manual setup for:
    Store internal ID, unique human-readable reference, reporter, title,
    description, category/subcategory, location, visibility, priority,
    status, department, assignment, timestamps, deadline, resolution,
    and optional external case reference.

### Directive 0089 --- Complaint model

-   Implement this requirement in the actual repository: Keep internal
    primary keys separate from public tracking references.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep internal primary keys separate from public tracking
    references.
-   Persist all required data and audit events consistently for: Keep
    internal primary keys separate from public tracking references.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep internal primary keys separate from public tracking
    references.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep internal primary keys separate from public tracking references.

### Directive 0090 --- Complaint model

-   Implement this requirement in the actual repository: Generate
    tracking references collision-safely using database-backed
    uniqueness.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Generate tracking references collision-safely using
    database-backed uniqueness.
-   Persist all required data and audit events consistently for:
    Generate tracking references collision-safely using database-backed
    uniqueness.
-   Add at least one positive test and one relevant negative/failure
    test for: Generate tracking references collision-safely using
    database-backed uniqueness.
-   Document configuration, behavior, limitations, and manual setup for:
    Generate tracking references collision-safely using database-backed
    uniqueness.

### Directive 0091 --- Complaint model

-   Implement this requirement in the actual repository: Never use a
    predictable sequential reference as the sole anonymous access
    secret.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never use a predictable sequential reference as the sole
    anonymous access secret.
-   Persist all required data and audit events consistently for: Never
    use a predictable sequential reference as the sole anonymous access
    secret.
-   Add at least one positive test and one relevant negative/failure
    test for: Never use a predictable sequential reference as the sole
    anonymous access secret.
-   Document configuration, behavior, limitations, and manual setup for:
    Never use a predictable sequential reference as the sole anonymous
    access secret.

### Directive 0092 --- Complaint model

-   Implement this requirement in the actual repository: Track
    created_at, updated_at, resolved_at, closed_at, and due_at with
    defined semantics.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Track created_at, updated_at, resolved_at, closed_at, and due_at
    with defined semantics.
-   Persist all required data and audit events consistently for: Track
    created_at, updated_at, resolved_at, closed_at, and due_at with
    defined semantics.
-   Add at least one positive test and one relevant negative/failure
    test for: Track created_at, updated_at, resolved_at, closed_at, and
    due_at with defined semantics.
-   Document configuration, behavior, limitations, and manual setup for:
    Track created_at, updated_at, resolved_at, closed_at, and due_at
    with defined semantics.

### Directive 0093 --- Complaint model

-   Implement this requirement in the actual repository: Store media
    references separately from the complaint row.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store media references separately from the complaint row.
-   Persist all required data and audit events consistently for: Store
    media references separately from the complaint row.
-   Add at least one positive test and one relevant negative/failure
    test for: Store media references separately from the complaint row.
-   Document configuration, behavior, limitations, and manual setup for:
    Store media references separately from the complaint row.

### Directive 0094 --- Complaint model

-   Implement this requirement in the actual repository: Store source
    channel, duplicate links, privacy setting, reassignment reason,
    escalation state, and routing decision when useful.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store source channel, duplicate links, privacy setting,
    reassignment reason, escalation state, and routing decision when
    useful.
-   Persist all required data and audit events consistently for: Store
    source channel, duplicate links, privacy setting, reassignment
    reason, escalation state, and routing decision when useful.
-   Add at least one positive test and one relevant negative/failure
    test for: Store source channel, duplicate links, privacy setting,
    reassignment reason, escalation state, and routing decision when
    useful.
-   Document configuration, behavior, limitations, and manual setup for:
    Store source channel, duplicate links, privacy setting, reassignment
    reason, escalation state, and routing decision when useful.

### Directive 0095 --- Complaint model

-   Implement this requirement in the actual repository: Allow anonymous
    reporting only if policy enables it and provide a high-entropy
    tracking token or equivalent.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow anonymous reporting only if policy enables it and provide
    a high-entropy tracking token or equivalent.
-   Persist all required data and audit events consistently for: Allow
    anonymous reporting only if policy enables it and provide a
    high-entropy tracking token or equivalent.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow anonymous reporting only if policy enables it and
    provide a high-entropy tracking token or equivalent.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow anonymous reporting only if policy enables it and provide a
    high-entropy tracking token or equivalent.

### Directive 0096 --- Complaint model

-   Implement this requirement in the actual repository: Define
    archival, withdrawal, correction, retention, and deletion behavior
    explicitly.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define archival, withdrawal, correction, retention, and deletion
    behavior explicitly.
-   Persist all required data and audit events consistently for: Define
    archival, withdrawal, correction, retention, and deletion behavior
    explicitly.
-   Add at least one positive test and one relevant negative/failure
    test for: Define archival, withdrawal, correction, retention, and
    deletion behavior explicitly.
-   Document configuration, behavior, limitations, and manual setup for:
    Define archival, withdrawal, correction, retention, and deletion
    behavior explicitly.

### Directive 0097 --- Complaint model

-   Implement this requirement in the actual repository: Preserve
    history and the original reporter relationship after merges or
    closure.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Preserve history and the original reporter relationship after
    merges or closure.
-   Persist all required data and audit events consistently for:
    Preserve history and the original reporter relationship after merges
    or closure.
-   Add at least one positive test and one relevant negative/failure
    test for: Preserve history and the original reporter relationship
    after merges or closure.
-   Document configuration, behavior, limitations, and manual setup for:
    Preserve history and the original reporter relationship after merges
    or closure.

### Directive 0098 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Implement POST
    complaint creation with explicit request schema and server-side
    authorization.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Implement POST complaint creation with explicit request schema
    and server-side authorization.
-   Persist all required data and audit events consistently for:
    Implement POST complaint creation with explicit request schema and
    server-side authorization.
-   Add at least one positive test and one relevant negative/failure
    test for: Implement POST complaint creation with explicit request
    schema and server-side authorization.
-   Document configuration, behavior, limitations, and manual setup for:
    Implement POST complaint creation with explicit request schema and
    server-side authorization.

### Directive 0099 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Require a
    meaningful description or documented minimum fields and enforce
    bounded lengths.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Require a meaningful description or documented minimum fields
    and enforce bounded lengths.
-   Persist all required data and audit events consistently for: Require
    a meaningful description or documented minimum fields and enforce
    bounded lengths.
-   Add at least one positive test and one relevant negative/failure
    test for: Require a meaningful description or documented minimum
    fields and enforce bounded lengths.
-   Document configuration, behavior, limitations, and manual setup for:
    Require a meaningful description or documented minimum fields and
    enforce bounded lengths.

### Directive 0100 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Trim safe
    whitespace and reject empty/whitespace-only descriptions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Trim safe whitespace and reject empty/whitespace-only
    descriptions.
-   Persist all required data and audit events consistently for: Trim
    safe whitespace and reject empty/whitespace-only descriptions.
-   Add at least one positive test and one relevant negative/failure
    test for: Trim safe whitespace and reject empty/whitespace-only
    descriptions.
-   Document configuration, behavior, limitations, and manual setup for:
    Trim safe whitespace and reject empty/whitespace-only descriptions.

### Directive 0101 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Validate
    category, ward, media ownership, visibility, coordinate ranges, and
    all referenced IDs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate category, ward, media ownership, visibility, coordinate
    ranges, and all referenced IDs.
-   Persist all required data and audit events consistently for:
    Validate category, ward, media ownership, visibility, coordinate
    ranges, and all referenced IDs.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate category, ward, media ownership, visibility,
    coordinate ranges, and all referenced IDs.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate category, ward, media ownership, visibility, coordinate
    ranges, and all referenced IDs.

### Directive 0102 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Do not trust
    client-supplied reporter IDs, status, assignment, priority
    overrides, timestamps, or audit fields.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not trust client-supplied reporter IDs, status, assignment,
    priority overrides, timestamps, or audit fields.
-   Persist all required data and audit events consistently for: Do not
    trust client-supplied reporter IDs, status, assignment, priority
    overrides, timestamps, or audit fields.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not trust client-supplied reporter IDs, status,
    assignment, priority overrides, timestamps, or audit fields.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not trust client-supplied reporter IDs, status, assignment,
    priority overrides, timestamps, or audit fields.

### Directive 0103 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Set initial
    status and timestamps server-side and generate the tracking
    reference on the server.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Set initial status and timestamps server-side and generate the
    tracking reference on the server.
-   Persist all required data and audit events consistently for: Set
    initial status and timestamps server-side and generate the tracking
    reference on the server.
-   Add at least one positive test and one relevant negative/failure
    test for: Set initial status and timestamps server-side and generate
    the tracking reference on the server.
-   Document configuration, behavior, limitations, and manual setup for:
    Set initial status and timestamps server-side and generate the
    tracking reference on the server.

### Directive 0104 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Create the
    complaint and initial status history in one transaction.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create the complaint and initial status history in one
    transaction.
-   Persist all required data and audit events consistently for: Create
    the complaint and initial status history in one transaction.
-   Add at least one positive test and one relevant negative/failure
    test for: Create the complaint and initial status history in one
    transaction.
-   Document configuration, behavior, limitations, and manual setup for:
    Create the complaint and initial status history in one transaction.

### Directive 0105 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Return the
    reference only after persistence succeeds.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Return the reference only after persistence succeeds.
-   Persist all required data and audit events consistently for: Return
    the reference only after persistence succeeds.
-   Add at least one positive test and one relevant negative/failure
    test for: Return the reference only after persistence succeeds.
-   Document configuration, behavior, limitations, and manual setup for:
    Return the reference only after persistence succeeds.

### Directive 0106 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Support
    idempotency keys for retryable creation requests and reject key
    reuse with different input.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support idempotency keys for retryable creation requests and
    reject key reuse with different input.
-   Persist all required data and audit events consistently for: Support
    idempotency keys for retryable creation requests and reject key
    reuse with different input.
-   Add at least one positive test and one relevant negative/failure
    test for: Support idempotency keys for retryable creation requests
    and reject key reuse with different input.
-   Document configuration, behavior, limitations, and manual setup for:
    Support idempotency keys for retryable creation requests and reject
    key reuse with different input.

### Directive 0107 --- Complaint creation and validation

-   Implement this requirement in the actual repository: Return
    field-level validation errors in a consistent safe response format.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Return field-level validation errors in a consistent safe
    response format.
-   Persist all required data and audit events consistently for: Return
    field-level validation errors in a consistent safe response format.
-   Add at least one positive test and one relevant negative/failure
    test for: Return field-level validation errors in a consistent safe
    response format.
-   Document configuration, behavior, limitations, and manual setup for:
    Return field-level validation errors in a consistent safe response
    format.

### Directive 0108 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Implement
    authorized list and detail endpoints with pagination and bounded
    page size.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Implement authorized list and detail endpoints with pagination
    and bounded page size.
-   Persist all required data and audit events consistently for:
    Implement authorized list and detail endpoints with pagination and
    bounded page size.
-   Add at least one positive test and one relevant negative/failure
    test for: Implement authorized list and detail endpoints with
    pagination and bounded page size.
-   Document configuration, behavior, limitations, and manual setup for:
    Implement authorized list and detail endpoints with pagination and
    bounded page size.

### Directive 0109 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Support filters
    for status, category, department, assigned officer, priority, ward,
    date range, and permitted text search.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support filters for status, category, department, assigned
    officer, priority, ward, date range, and permitted text search.
-   Persist all required data and audit events consistently for: Support
    filters for status, category, department, assigned officer,
    priority, ward, date range, and permitted text search.
-   Add at least one positive test and one relevant negative/failure
    test for: Support filters for status, category, department, assigned
    officer, priority, ward, date range, and permitted text search.
-   Document configuration, behavior, limitations, and manual setup for:
    Support filters for status, category, department, assigned officer,
    priority, ward, date range, and permitted text search.

### Directive 0110 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Enforce
    row-level scope in database queries; never fetch all rows and filter
    only in the frontend.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Enforce row-level scope in database queries; never fetch all
    rows and filter only in the frontend.
-   Persist all required data and audit events consistently for: Enforce
    row-level scope in database queries; never fetch all rows and filter
    only in the frontend.
-   Add at least one positive test and one relevant negative/failure
    test for: Enforce row-level scope in database queries; never fetch
    all rows and filter only in the frontend.
-   Document configuration, behavior, limitations, and manual setup for:
    Enforce row-level scope in database queries; never fetch all rows
    and filter only in the frontend.

### Directive 0111 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Use explicit
    response schemas to avoid leaking internal fields.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use explicit response schemas to avoid leaking internal fields.
-   Persist all required data and audit events consistently for: Use
    explicit response schemas to avoid leaking internal fields.
-   Add at least one positive test and one relevant negative/failure
    test for: Use explicit response schemas to avoid leaking internal
    fields.
-   Document configuration, behavior, limitations, and manual setup for:
    Use explicit response schemas to avoid leaking internal fields.

### Directive 0112 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Separate
    resident-edit schemas from staff-edit schemas.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Separate resident-edit schemas from staff-edit schemas.
-   Persist all required data and audit events consistently for:
    Separate resident-edit schemas from staff-edit schemas.
-   Add at least one positive test and one relevant negative/failure
    test for: Separate resident-edit schemas from staff-edit schemas.
-   Document configuration, behavior, limitations, and manual setup for:
    Separate resident-edit schemas from staff-edit schemas.

### Directive 0113 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Reject mass
    assignment of protected fields and reject edits to immutable fields.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Reject mass assignment of protected fields and reject edits to
    immutable fields.
-   Persist all required data and audit events consistently for: Reject
    mass assignment of protected fields and reject edits to immutable
    fields.
-   Add at least one positive test and one relevant negative/failure
    test for: Reject mass assignment of protected fields and reject
    edits to immutable fields.
-   Document configuration, behavior, limitations, and manual setup for:
    Reject mass assignment of protected fields and reject edits to
    immutable fields.

### Directive 0114 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Use stable
    ordering and appropriate indexes for frequently used filters.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use stable ordering and appropriate indexes for frequently used
    filters.
-   Persist all required data and audit events consistently for: Use
    stable ordering and appropriate indexes for frequently used filters.
-   Add at least one positive test and one relevant negative/failure
    test for: Use stable ordering and appropriate indexes for frequently
    used filters.
-   Document configuration, behavior, limitations, and manual setup for:
    Use stable ordering and appropriate indexes for frequently used
    filters.

### Directive 0115 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Support
    conflict responses when a stale edit would overwrite a newer update.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support conflict responses when a stale edit would overwrite a
    newer update.
-   Persist all required data and audit events consistently for: Support
    conflict responses when a stale edit would overwrite a newer update.
-   Add at least one positive test and one relevant negative/failure
    test for: Support conflict responses when a stale edit would
    overwrite a newer update.
-   Document configuration, behavior, limitations, and manual setup for:
    Support conflict responses when a stale edit would overwrite a newer
    update.

### Directive 0116 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Do not expose
    internal notes, private media, reporter contact details, or
    sensitive audit data to unauthorized callers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not expose internal notes, private media, reporter contact
    details, or sensitive audit data to unauthorized callers.
-   Persist all required data and audit events consistently for: Do not
    expose internal notes, private media, reporter contact details, or
    sensitive audit data to unauthorized callers.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not expose internal notes, private media, reporter
    contact details, or sensitive audit data to unauthorized callers.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not expose internal notes, private media, reporter contact
    details, or sensitive audit data to unauthorized callers.

### Directive 0117 --- Complaint retrieval, search, and edits

-   Implement this requirement in the actual repository: Test filter
    combinations, pagination, empty results, private records, and
    cross-user access.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test filter combinations, pagination, empty results, private
    records, and cross-user access.
-   Persist all required data and audit events consistently for: Test
    filter combinations, pagination, empty results, private records, and
    cross-user access.
-   Add at least one positive test and one relevant negative/failure
    test for: Test filter combinations, pagination, empty results,
    private records, and cross-user access.
-   Document configuration, behavior, limitations, and manual setup for:
    Test filter combinations, pagination, empty results, private
    records, and cross-user access.

### Directive 0118 --- Workflow state machine

-   Implement this requirement in the actual repository: Define allowed
    statuses and transitions in one central domain module.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define allowed statuses and transitions in one central domain
    module.
-   Persist all required data and audit events consistently for: Define
    allowed statuses and transitions in one central domain module.
-   Add at least one positive test and one relevant negative/failure
    test for: Define allowed statuses and transitions in one central
    domain module.
-   Document configuration, behavior, limitations, and manual setup for:
    Define allowed statuses and transitions in one central domain
    module.

### Directive 0119 --- Workflow state machine

-   Implement this requirement in the actual repository: Support a
    practical MVP flow such as Submitted, Under Review, Assigned, In
    Progress, Awaiting Resident, On Hold, Resolved, Closed, Rejected,
    Withdrawn, and Reopened as needed.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support a practical MVP flow such as Submitted, Under Review,
    Assigned, In Progress, Awaiting Resident, On Hold, Resolved, Closed,
    Rejected, Withdrawn, and Reopened as needed.
-   Persist all required data and audit events consistently for: Support
    a practical MVP flow such as Submitted, Under Review, Assigned, In
    Progress, Awaiting Resident, On Hold, Resolved, Closed, Rejected,
    Withdrawn, and Reopened as needed.
-   Add at least one positive test and one relevant negative/failure
    test for: Support a practical MVP flow such as Submitted, Under
    Review, Assigned, In Progress, Awaiting Resident, On Hold, Resolved,
    Closed, Rejected, Withdrawn, and Reopened as needed.
-   Document configuration, behavior, limitations, and manual setup for:
    Support a practical MVP flow such as Submitted, Under Review,
    Assigned, In Progress, Awaiting Resident, On Hold, Resolved, Closed,
    Rejected, Withdrawn, and Reopened as needed.

### Directive 0120 --- Workflow state machine

-   Implement this requirement in the actual repository: Validate every
    transition server-side and reject arbitrary client-supplied status
    values.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate every transition server-side and reject arbitrary
    client-supplied status values.
-   Persist all required data and audit events consistently for:
    Validate every transition server-side and reject arbitrary
    client-supplied status values.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate every transition server-side and reject arbitrary
    client-supplied status values.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate every transition server-side and reject arbitrary
    client-supplied status values.

### Directive 0121 --- Workflow state machine

-   Implement this requirement in the actual repository: Require a
    reason for rejection, hold, reopening, and sensitive correction
    where policy specifies.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Require a reason for rejection, hold, reopening, and sensitive
    correction where policy specifies.
-   Persist all required data and audit events consistently for: Require
    a reason for rejection, hold, reopening, and sensitive correction
    where policy specifies.
-   Add at least one positive test and one relevant negative/failure
    test for: Require a reason for rejection, hold, reopening, and
    sensitive correction where policy specifies.
-   Document configuration, behavior, limitations, and manual setup for:
    Require a reason for rejection, hold, reopening, and sensitive
    correction where policy specifies.

### Directive 0122 --- Workflow state machine

-   Implement this requirement in the actual repository: Require
    resolution notes/evidence when configured.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Require resolution notes/evidence when configured.
-   Persist all required data and audit events consistently for: Require
    resolution notes/evidence when configured.
-   Add at least one positive test and one relevant negative/failure
    test for: Require resolution notes/evidence when configured.
-   Document configuration, behavior, limitations, and manual setup for:
    Require resolution notes/evidence when configured.

### Directive 0123 --- Workflow state machine

-   Implement this requirement in the actual repository: Record previous
    state, new state, actor, timestamp, reason, and system/human origin.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record previous state, new state, actor, timestamp, reason, and
    system/human origin.
-   Persist all required data and audit events consistently for: Record
    previous state, new state, actor, timestamp, reason, and
    system/human origin.
-   Add at least one positive test and one relevant negative/failure
    test for: Record previous state, new state, actor, timestamp,
    reason, and system/human origin.
-   Document configuration, behavior, limitations, and manual setup for:
    Record previous state, new state, actor, timestamp, reason, and
    system/human origin.

### Directive 0124 --- Workflow state machine

-   Implement this requirement in the actual repository: Write status
    and history in the same transaction.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Write status and history in the same transaction.
-   Persist all required data and audit events consistently for: Write
    status and history in the same transaction.
-   Add at least one positive test and one relevant negative/failure
    test for: Write status and history in the same transaction.
-   Document configuration, behavior, limitations, and manual setup for:
    Write status and history in the same transaction.

### Directive 0125 --- Workflow state machine

-   Implement this requirement in the actual repository: Define whether
    resolved and closed are separate states and document the rule.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define whether resolved and closed are separate states and
    document the rule.
-   Persist all required data and audit events consistently for: Define
    whether resolved and closed are separate states and document the
    rule.
-   Add at least one positive test and one relevant negative/failure
    test for: Define whether resolved and closed are separate states and
    document the rule.
-   Document configuration, behavior, limitations, and manual setup for:
    Define whether resolved and closed are separate states and document
    the rule.

### Directive 0126 --- Workflow state machine

-   Implement this requirement in the actual repository: Define how SLA
    clocks behave in hold or awaiting-resident states.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define how SLA clocks behave in hold or awaiting-resident
    states.
-   Persist all required data and audit events consistently for: Define
    how SLA clocks behave in hold or awaiting-resident states.
-   Add at least one positive test and one relevant negative/failure
    test for: Define how SLA clocks behave in hold or awaiting-resident
    states.
-   Document configuration, behavior, limitations, and manual setup for:
    Define how SLA clocks behave in hold or awaiting-resident states.

### Directive 0127 --- Workflow state machine

-   Implement this requirement in the actual repository: Test every
    allowed transition and representative forbidden transitions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test every allowed transition and representative forbidden
    transitions.
-   Persist all required data and audit events consistently for: Test
    every allowed transition and representative forbidden transitions.
-   Add at least one positive test and one relevant negative/failure
    test for: Test every allowed transition and representative forbidden
    transitions.
-   Document configuration, behavior, limitations, and manual setup for:
    Test every allowed transition and representative forbidden
    transitions.

### Directive 0128 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Provide
    authorized assignment and reassignment use cases separate from
    general complaint updates.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide authorized assignment and reassignment use cases
    separate from general complaint updates.
-   Persist all required data and audit events consistently for: Provide
    authorized assignment and reassignment use cases separate from
    general complaint updates.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide authorized assignment and reassignment use cases
    separate from general complaint updates.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide authorized assignment and reassignment use cases separate
    from general complaint updates.

### Directive 0129 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Validate
    department, team, and officer existence, active state, and scope.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate department, team, and officer existence, active state,
    and scope.
-   Persist all required data and audit events consistently for:
    Validate department, team, and officer existence, active state, and
    scope.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate department, team, and officer existence, active
    state, and scope.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate department, team, and officer existence, active state, and
    scope.

### Directive 0130 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Require a
    reason for manual reassignment.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Require a reason for manual reassignment.
-   Persist all required data and audit events consistently for: Require
    a reason for manual reassignment.
-   Add at least one positive test and one relevant negative/failure
    test for: Require a reason for manual reassignment.
-   Document configuration, behavior, limitations, and manual setup for:
    Require a reason for manual reassignment.

### Directive 0131 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Record old and
    new assignment in assignment history.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record old and new assignment in assignment history.
-   Persist all required data and audit events consistently for: Record
    old and new assignment in assignment history.
-   Add at least one positive test and one relevant negative/failure
    test for: Record old and new assignment in assignment history.
-   Document configuration, behavior, limitations, and manual setup for:
    Record old and new assignment in assignment history.

### Directive 0132 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Preserve
    initial automatic routing outcome even after manual changes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Preserve initial automatic routing outcome even after manual
    changes.
-   Persist all required data and audit events consistently for:
    Preserve initial automatic routing outcome even after manual
    changes.
-   Add at least one positive test and one relevant negative/failure
    test for: Preserve initial automatic routing outcome even after
    manual changes.
-   Document configuration, behavior, limitations, and manual setup for:
    Preserve initial automatic routing outcome even after manual
    changes.

### Directive 0133 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Notify the
    appropriate staff/resident after a committed meaningful change.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Notify the appropriate staff/resident after a committed
    meaningful change.
-   Persist all required data and audit events consistently for: Notify
    the appropriate staff/resident after a committed meaningful change.
-   Add at least one positive test and one relevant negative/failure
    test for: Notify the appropriate staff/resident after a committed
    meaningful change.
-   Document configuration, behavior, limitations, and manual setup for:
    Notify the appropriate staff/resident after a committed meaningful
    change.

### Directive 0134 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Prevent
    repeated reassignment loops and handle unavailable officers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent repeated reassignment loops and handle unavailable
    officers.
-   Persist all required data and audit events consistently for: Prevent
    repeated reassignment loops and handle unavailable officers.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent repeated reassignment loops and handle unavailable
    officers.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent repeated reassignment loops and handle unavailable officers.

### Directive 0135 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Support an
    unassigned queue when no valid target exists.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support an unassigned queue when no valid target exists.
-   Persist all required data and audit events consistently for: Support
    an unassigned queue when no valid target exists.
-   Add at least one positive test and one relevant negative/failure
    test for: Support an unassigned queue when no valid target exists.
-   Document configuration, behavior, limitations, and manual setup for:
    Support an unassigned queue when no valid target exists.

### Directive 0136 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Ensure
    assignment changes and history commit atomically.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Ensure assignment changes and history commit atomically.
-   Persist all required data and audit events consistently for: Ensure
    assignment changes and history commit atomically.
-   Add at least one positive test and one relevant negative/failure
    test for: Ensure assignment changes and history commit atomically.
-   Document configuration, behavior, limitations, and manual setup for:
    Ensure assignment changes and history commit atomically.

### Directive 0137 --- Assignment and reassignment

-   Implement this requirement in the actual repository: Test
    unauthorized assignment, inactive target, concurrent assignment, and
    successful reassignment.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test unauthorized assignment, inactive target, concurrent
    assignment, and successful reassignment.
-   Persist all required data and audit events consistently for: Test
    unauthorized assignment, inactive target, concurrent assignment, and
    successful reassignment.
-   Add at least one positive test and one relevant negative/failure
    test for: Test unauthorized assignment, inactive target, concurrent
    assignment, and successful reassignment.
-   Document configuration, behavior, limitations, and manual setup for:
    Test unauthorized assignment, inactive target, concurrent
    assignment, and successful reassignment.

### Directive 0138 --- Routing engine

-   Implement this requirement in the actual repository: Implement
    deterministic routing in a dedicated service rather than HTTP
    handlers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Implement deterministic routing in a dedicated service rather
    than HTTP handlers.
-   Persist all required data and audit events consistently for:
    Implement deterministic routing in a dedicated service rather than
    HTTP handlers.
-   Add at least one positive test and one relevant negative/failure
    test for: Implement deterministic routing in a dedicated service
    rather than HTTP handlers.
-   Document configuration, behavior, limitations, and manual setup for:
    Implement deterministic routing in a dedicated service rather than
    HTTP handlers.

### Directive 0139 --- Routing engine

-   Implement this requirement in the actual repository: Route using
    category/subcategory, verified jurisdiction, service coverage, and
    active department rules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Route using category/subcategory, verified jurisdiction, service
    coverage, and active department rules.
-   Persist all required data and audit events consistently for: Route
    using category/subcategory, verified jurisdiction, service coverage,
    and active department rules.
-   Add at least one positive test and one relevant negative/failure
    test for: Route using category/subcategory, verified jurisdiction,
    service coverage, and active department rules.
-   Document configuration, behavior, limitations, and manual setup for:
    Route using category/subcategory, verified jurisdiction, service
    coverage, and active department rules.

### Directive 0140 --- Routing engine

-   Implement this requirement in the actual repository: Store rule
    precedence, active state, effective dates, and responsible
    department in configuration.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store rule precedence, active state, effective dates, and
    responsible department in configuration.
-   Persist all required data and audit events consistently for: Store
    rule precedence, active state, effective dates, and responsible
    department in configuration.
-   Add at least one positive test and one relevant negative/failure
    test for: Store rule precedence, active state, effective dates, and
    responsible department in configuration.
-   Document configuration, behavior, limitations, and manual setup for:
    Store rule precedence, active state, effective dates, and
    responsible department in configuration.

### Directive 0141 --- Routing engine

-   Implement this requirement in the actual repository: Define explicit
    precedence for overlapping or conflicting rules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define explicit precedence for overlapping or conflicting rules.
-   Persist all required data and audit events consistently for: Define
    explicit precedence for overlapping or conflicting rules.
-   Add at least one positive test and one relevant negative/failure
    test for: Define explicit precedence for overlapping or conflicting
    rules.
-   Document configuration, behavior, limitations, and manual setup for:
    Define explicit precedence for overlapping or conflicting rules.

### Directive 0142 --- Routing engine

-   Implement this requirement in the actual repository: Record selected
    rule, routing result, explanation, timestamp, and fallback reason.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record selected rule, routing result, explanation, timestamp,
    and fallback reason.
-   Persist all required data and audit events consistently for: Record
    selected rule, routing result, explanation, timestamp, and fallback
    reason.
-   Add at least one positive test and one relevant negative/failure
    test for: Record selected rule, routing result, explanation,
    timestamp, and fallback reason.
-   Document configuration, behavior, limitations, and manual setup for:
    Record selected rule, routing result, explanation, timestamp, and
    fallback reason.

### Directive 0143 --- Routing engine

-   Implement this requirement in the actual repository: Route unknown
    or ambiguous cases to triage rather than inventing a destination.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Route unknown or ambiguous cases to triage rather than inventing
    a destination.
-   Persist all required data and audit events consistently for: Route
    unknown or ambiguous cases to triage rather than inventing a
    destination.
-   Add at least one positive test and one relevant negative/failure
    test for: Route unknown or ambiguous cases to triage rather than
    inventing a destination.
-   Document configuration, behavior, limitations, and manual setup for:
    Route unknown or ambiguous cases to triage rather than inventing a
    destination.

### Directive 0144 --- Routing engine

-   Implement this requirement in the actual repository: Support
    authorized manual reassignment and optional re-evaluation after
    category correction.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support authorized manual reassignment and optional
    re-evaluation after category correction.
-   Persist all required data and audit events consistently for: Support
    authorized manual reassignment and optional re-evaluation after
    category correction.
-   Add at least one positive test and one relevant negative/failure
    test for: Support authorized manual reassignment and optional
    re-evaluation after category correction.
-   Document configuration, behavior, limitations, and manual setup for:
    Support authorized manual reassignment and optional re-evaluation
    after category correction.

### Directive 0145 --- Routing engine

-   Implement this requirement in the actual repository: Prevent routing
    loops and preserve prior decisions for audit.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent routing loops and preserve prior decisions for audit.
-   Persist all required data and audit events consistently for: Prevent
    routing loops and preserve prior decisions for audit.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent routing loops and preserve prior decisions for
    audit.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent routing loops and preserve prior decisions for audit.

### Directive 0146 --- Routing engine

-   Implement this requirement in the actual repository: AI may suggest
    a category or department but must not override jurisdiction or
    silently decide uncertain cases.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: AI may suggest a category or department but must not override
    jurisdiction or silently decide uncertain cases.
-   Persist all required data and audit events consistently for: AI may
    suggest a category or department but must not override jurisdiction
    or silently decide uncertain cases.
-   Add at least one positive test and one relevant negative/failure
    test for: AI may suggest a category or department but must not
    override jurisdiction or silently decide uncertain cases.
-   Document configuration, behavior, limitations, and manual setup for:
    AI may suggest a category or department but must not override
    jurisdiction or silently decide uncertain cases.

### Directive 0147 --- Routing engine

-   Implement this requirement in the actual repository: Test valid
    mapping, inactive department, no match, conflicting rules, outside
    jurisdiction, and fallback.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test valid mapping, inactive department, no match, conflicting
    rules, outside jurisdiction, and fallback.
-   Persist all required data and audit events consistently for: Test
    valid mapping, inactive department, no match, conflicting rules,
    outside jurisdiction, and fallback.
-   Add at least one positive test and one relevant negative/failure
    test for: Test valid mapping, inactive department, no match,
    conflicting rules, outside jurisdiction, and fallback.
-   Document configuration, behavior, limitations, and manual setup for:
    Test valid mapping, inactive department, no match, conflicting
    rules, outside jurisdiction, and fallback.

### Directive 0148 --- Priority and urgency

-   Implement this requirement in the actual repository: Define
    controlled priority values and keep priority separate from status.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define controlled priority values and keep priority separate
    from status.
-   Persist all required data and audit events consistently for: Define
    controlled priority values and keep priority separate from status.
-   Add at least one positive test and one relevant negative/failure
    test for: Define controlled priority values and keep priority
    separate from status.
-   Document configuration, behavior, limitations, and manual setup for:
    Define controlled priority values and keep priority separate from
    status.

### Directive 0149 --- Priority and urgency

-   Implement this requirement in the actual repository: Calculate
    default priority using configurable rules such as issue type,
    safety, recurrence, affected population, and waiting time where
    available.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Calculate default priority using configurable rules such as
    issue type, safety, recurrence, affected population, and waiting
    time where available.
-   Persist all required data and audit events consistently for:
    Calculate default priority using configurable rules such as issue
    type, safety, recurrence, affected population, and waiting time
    where available.
-   Add at least one positive test and one relevant negative/failure
    test for: Calculate default priority using configurable rules such
    as issue type, safety, recurrence, affected population, and waiting
    time where available.
-   Document configuration, behavior, limitations, and manual setup for:
    Calculate default priority using configurable rules such as issue
    type, safety, recurrence, affected population, and waiting time
    where available.

### Directive 0150 --- Priority and urgency

-   Implement this requirement in the actual repository: Do not declare
    a critical emergency from a single keyword alone.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not declare a critical emergency from a single keyword alone.
-   Persist all required data and audit events consistently for: Do not
    declare a critical emergency from a single keyword alone.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not declare a critical emergency from a single keyword
    alone.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not declare a critical emergency from a single keyword alone.

### Directive 0151 --- Priority and urgency

-   Implement this requirement in the actual repository: Allow
    authorized staff to override priority with a required reason and
    history.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow authorized staff to override priority with a required
    reason and history.
-   Persist all required data and audit events consistently for: Allow
    authorized staff to override priority with a required reason and
    history.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow authorized staff to override priority with a
    required reason and history.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow authorized staff to override priority with a required reason
    and history.

### Directive 0152 --- Priority and urgency

-   Implement this requirement in the actual repository: Use configured
    rules to alert staff about critical or high-priority issues.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use configured rules to alert staff about critical or
    high-priority issues.
-   Persist all required data and audit events consistently for: Use
    configured rules to alert staff about critical or high-priority
    issues.
-   Add at least one positive test and one relevant negative/failure
    test for: Use configured rules to alert staff about critical or
    high-priority issues.
-   Document configuration, behavior, limitations, and manual setup for:
    Use configured rules to alert staff about critical or high-priority
    issues.

### Directive 0153 --- Priority and urgency

-   Implement this requirement in the actual repository: Direct
    immediate danger to verified emergency channels; do not imply this
    app dispatches emergency services.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Direct immediate danger to verified emergency channels; do not
    imply this app dispatches emergency services.
-   Persist all required data and audit events consistently for: Direct
    immediate danger to verified emergency channels; do not imply this
    app dispatches emergency services.
-   Add at least one positive test and one relevant negative/failure
    test for: Direct immediate danger to verified emergency channels; do
    not imply this app dispatches emergency services.
-   Document configuration, behavior, limitations, and manual setup for:
    Direct immediate danger to verified emergency channels; do not imply
    this app dispatches emergency services.

### Directive 0154 --- Priority and urgency

-   Implement this requirement in the actual repository: Do not let an
    AI-only score trigger irreversible high-impact actions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not let an AI-only score trigger irreversible high-impact
    actions.
-   Persist all required data and audit events consistently for: Do not
    let an AI-only score trigger irreversible high-impact actions.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not let an AI-only score trigger irreversible
    high-impact actions.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not let an AI-only score trigger irreversible high-impact
    actions.

### Directive 0155 --- Priority and urgency

-   Implement this requirement in the actual repository: Support
    filtering and sorting by priority.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support filtering and sorting by priority.
-   Persist all required data and audit events consistently for: Support
    filtering and sorting by priority.
-   Add at least one positive test and one relevant negative/failure
    test for: Support filtering and sorting by priority.
-   Document configuration, behavior, limitations, and manual setup for:
    Support filtering and sorting by priority.

### Directive 0156 --- Priority and urgency

-   Implement this requirement in the actual repository: Use
    illustrative sample rules unless official local policy has been
    verified.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use illustrative sample rules unless official local policy has
    been verified.
-   Persist all required data and audit events consistently for: Use
    illustrative sample rules unless official local policy has been
    verified.
-   Add at least one positive test and one relevant negative/failure
    test for: Use illustrative sample rules unless official local policy
    has been verified.
-   Document configuration, behavior, limitations, and manual setup for:
    Use illustrative sample rules unless official local policy has been
    verified.

### Directive 0157 --- Priority and urgency

-   Implement this requirement in the actual repository: Test
    deterministic scoring, override permission, invalid values, and
    alert policy.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test deterministic scoring, override permission, invalid values,
    and alert policy.
-   Persist all required data and audit events consistently for: Test
    deterministic scoring, override permission, invalid values, and
    alert policy.
-   Add at least one positive test and one relevant negative/failure
    test for: Test deterministic scoring, override permission, invalid
    values, and alert policy.
-   Document configuration, behavior, limitations, and manual setup for:
    Test deterministic scoring, override permission, invalid values, and
    alert policy.

### Directive 0158 --- SLA and escalation

-   Implement this requirement in the actual repository: Create
    configurable policies for acknowledgement, assignment, review, and
    resolution targets.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create configurable policies for acknowledgement, assignment,
    review, and resolution targets.
-   Persist all required data and audit events consistently for: Create
    configurable policies for acknowledgement, assignment, review, and
    resolution targets.
-   Add at least one positive test and one relevant negative/failure
    test for: Create configurable policies for acknowledgement,
    assignment, review, and resolution targets.
-   Document configuration, behavior, limitations, and manual setup for:
    Create configurable policies for acknowledgement, assignment,
    review, and resolution targets.

### Directive 0159 --- SLA and escalation

-   Implement this requirement in the actual repository: Select policy
    by category, priority, department, and effective date where
    configured.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Select policy by category, priority, department, and effective
    date where configured.
-   Persist all required data and audit events consistently for: Select
    policy by category, priority, department, and effective date where
    configured.
-   Add at least one positive test and one relevant negative/failure
    test for: Select policy by category, priority, department, and
    effective date where configured.
-   Document configuration, behavior, limitations, and manual setup for:
    Select policy by category, priority, department, and effective date
    where configured.

### Directive 0160 --- SLA and escalation

-   Implement this requirement in the actual repository: Store policy
    version used for each complaint's target.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store policy version used for each complaint's target.
-   Persist all required data and audit events consistently for: Store
    policy version used for each complaint's target.
-   Add at least one positive test and one relevant negative/failure
    test for: Store policy version used for each complaint's target.
-   Document configuration, behavior, limitations, and manual setup for:
    Store policy version used for each complaint's target.

### Directive 0161 --- SLA and escalation

-   Implement this requirement in the actual repository: Calculate due
    dates on the server and document working-hour/timezone behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Calculate due dates on the server and document
    working-hour/timezone behavior.
-   Persist all required data and audit events consistently for:
    Calculate due dates on the server and document working-hour/timezone
    behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Calculate due dates on the server and document
    working-hour/timezone behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Calculate due dates on the server and document working-hour/timezone
    behavior.

### Directive 0162 --- SLA and escalation

-   Implement this requirement in the actual repository: Support
    holidays and working calendars only when reliable data is
    configured.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support holidays and working calendars only when reliable data
    is configured.
-   Persist all required data and audit events consistently for: Support
    holidays and working calendars only when reliable data is
    configured.
-   Add at least one positive test and one relevant negative/failure
    test for: Support holidays and working calendars only when reliable
    data is configured.
-   Document configuration, behavior, limitations, and manual setup for:
    Support holidays and working calendars only when reliable data is
    configured.

### Directive 0163 --- SLA and escalation

-   Implement this requirement in the actual repository: Define
    pause/resume behavior for hold and awaiting-resident states.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define pause/resume behavior for hold and awaiting-resident
    states.
-   Persist all required data and audit events consistently for: Define
    pause/resume behavior for hold and awaiting-resident states.
-   Add at least one positive test and one relevant negative/failure
    test for: Define pause/resume behavior for hold and
    awaiting-resident states.
-   Document configuration, behavior, limitations, and manual setup for:
    Define pause/resume behavior for hold and awaiting-resident states.

### Directive 0164 --- SLA and escalation

-   Implement this requirement in the actual repository: Schedule
    approaching-deadline reminders and overdue detection.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Schedule approaching-deadline reminders and overdue detection.
-   Persist all required data and audit events consistently for:
    Schedule approaching-deadline reminders and overdue detection.
-   Add at least one positive test and one relevant negative/failure
    test for: Schedule approaching-deadline reminders and overdue
    detection.
-   Document configuration, behavior, limitations, and manual setup for:
    Schedule approaching-deadline reminders and overdue detection.

### Directive 0165 --- SLA and escalation

-   Implement this requirement in the actual repository: Escalate to a
    configured supervisor or queue when policy requires it.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Escalate to a configured supervisor or queue when policy
    requires it.
-   Persist all required data and audit events consistently for:
    Escalate to a configured supervisor or queue when policy requires
    it.
-   Add at least one positive test and one relevant negative/failure
    test for: Escalate to a configured supervisor or queue when policy
    requires it.
-   Document configuration, behavior, limitations, and manual setup for:
    Escalate to a configured supervisor or queue when policy requires
    it.

### Directive 0166 --- SLA and escalation

-   Implement this requirement in the actual repository: Make
    reminder/escalation jobs idempotent and record trigger, actor,
    destination, and timestamp.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Make reminder/escalation jobs idempotent and record trigger,
    actor, destination, and timestamp.
-   Persist all required data and audit events consistently for: Make
    reminder/escalation jobs idempotent and record trigger, actor,
    destination, and timestamp.
-   Add at least one positive test and one relevant negative/failure
    test for: Make reminder/escalation jobs idempotent and record
    trigger, actor, destination, and timestamp.
-   Document configuration, behavior, limitations, and manual setup for:
    Make reminder/escalation jobs idempotent and record trigger, actor,
    destination, and timestamp.

### Directive 0167 --- SLA and escalation

-   Implement this requirement in the actual repository: Never present
    sample deadlines as official municipal guarantees.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never present sample deadlines as official municipal guarantees.
-   Persist all required data and audit events consistently for: Never
    present sample deadlines as official municipal guarantees.
-   Add at least one positive test and one relevant negative/failure
    test for: Never present sample deadlines as official municipal
    guarantees.
-   Document configuration, behavior, limitations, and manual setup for:
    Never present sample deadlines as official municipal guarantees.

### Directive 0168 --- Notifications

-   Implement this requirement in the actual repository: Use domain
    events for complaint submitted, assigned, reassigned, status
    changed, information requested, resolved, reopened, deadline
    approaching, and overdue.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use domain events for complaint submitted, assigned, reassigned,
    status changed, information requested, resolved, reopened, deadline
    approaching, and overdue.
-   Persist all required data and audit events consistently for: Use
    domain events for complaint submitted, assigned, reassigned, status
    changed, information requested, resolved, reopened, deadline
    approaching, and overdue.
-   Add at least one positive test and one relevant negative/failure
    test for: Use domain events for complaint submitted, assigned,
    reassigned, status changed, information requested, resolved,
    reopened, deadline approaching, and overdue.
-   Document configuration, behavior, limitations, and manual setup for:
    Use domain events for complaint submitted, assigned, reassigned,
    status changed, information requested, resolved, reopened, deadline
    approaching, and overdue.

### Directive 0169 --- Notifications

-   Implement this requirement in the actual repository: Implement
    in-app notifications as the baseline.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Implement in-app notifications as the baseline.
-   Persist all required data and audit events consistently for:
    Implement in-app notifications as the baseline.
-   Add at least one positive test and one relevant negative/failure
    test for: Implement in-app notifications as the baseline.
-   Document configuration, behavior, limitations, and manual setup for:
    Implement in-app notifications as the baseline.

### Directive 0170 --- Notifications

-   Implement this requirement in the actual repository: Use provider
    adapters for email, SMS, push, or messaging platforms; keep them
    optional.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use provider adapters for email, SMS, push, or messaging
    platforms; keep them optional.
-   Persist all required data and audit events consistently for: Use
    provider adapters for email, SMS, push, or messaging platforms; keep
    them optional.
-   Add at least one positive test and one relevant negative/failure
    test for: Use provider adapters for email, SMS, push, or messaging
    platforms; keep them optional.
-   Document configuration, behavior, limitations, and manual setup for:
    Use provider adapters for email, SMS, push, or messaging platforms;
    keep them optional.

### Directive 0171 --- Notifications

-   Implement this requirement in the actual repository: Store
    recipient, channel, template, delivery state, attempt count,
    timestamps, and provider reference.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store recipient, channel, template, delivery state, attempt
    count, timestamps, and provider reference.
-   Persist all required data and audit events consistently for: Store
    recipient, channel, template, delivery state, attempt count,
    timestamps, and provider reference.
-   Add at least one positive test and one relevant negative/failure
    test for: Store recipient, channel, template, delivery state,
    attempt count, timestamps, and provider reference.
-   Document configuration, behavior, limitations, and manual setup for:
    Store recipient, channel, template, delivery state, attempt count,
    timestamps, and provider reference.

### Directive 0172 --- Notifications

-   Implement this requirement in the actual repository: Use safe
    templates and escape untrusted content for the target channel.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use safe templates and escape untrusted content for the target
    channel.
-   Persist all required data and audit events consistently for: Use
    safe templates and escape untrusted content for the target channel.
-   Add at least one positive test and one relevant negative/failure
    test for: Use safe templates and escape untrusted content for the
    target channel.
-   Document configuration, behavior, limitations, and manual setup for:
    Use safe templates and escape untrusted content for the target
    channel.

### Directive 0173 --- Notifications

-   Implement this requirement in the actual repository: Respect user
    preferences and applicable consent requirements.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Respect user preferences and applicable consent requirements.
-   Persist all required data and audit events consistently for: Respect
    user preferences and applicable consent requirements.
-   Add at least one positive test and one relevant negative/failure
    test for: Respect user preferences and applicable consent
    requirements.
-   Document configuration, behavior, limitations, and manual setup for:
    Respect user preferences and applicable consent requirements.

### Directive 0174 --- Notifications

-   Implement this requirement in the actual repository: Use bounded
    retries with backoff and avoid duplicate delivery on job retries.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use bounded retries with backoff and avoid duplicate delivery on
    job retries.
-   Persist all required data and audit events consistently for: Use
    bounded retries with backoff and avoid duplicate delivery on job
    retries.
-   Add at least one positive test and one relevant negative/failure
    test for: Use bounded retries with backoff and avoid duplicate
    delivery on job retries.
-   Document configuration, behavior, limitations, and manual setup for:
    Use bounded retries with backoff and avoid duplicate delivery on job
    retries.

### Directive 0175 --- Notifications

-   Implement this requirement in the actual repository: Never roll back
    a complaint because notification delivery fails.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never roll back a complaint because notification delivery fails.
-   Persist all required data and audit events consistently for: Never
    roll back a complaint because notification delivery fails.
-   Add at least one positive test and one relevant negative/failure
    test for: Never roll back a complaint because notification delivery
    fails.
-   Document configuration, behavior, limitations, and manual setup for:
    Never roll back a complaint because notification delivery fails.

### Directive 0176 --- Notifications

-   Implement this requirement in the actual repository: Do not include
    private contact details, internal notes, tokens, or unnecessary
    personal data in messages.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not include private contact details, internal notes, tokens,
    or unnecessary personal data in messages.
-   Persist all required data and audit events consistently for: Do not
    include private contact details, internal notes, tokens, or
    unnecessary personal data in messages.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not include private contact details, internal notes,
    tokens, or unnecessary personal data in messages.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not include private contact details, internal notes, tokens, or
    unnecessary personal data in messages.

### Directive 0177 --- Notifications

-   Implement this requirement in the actual repository: Test
    provider-disabled mode, failure, retry, deduplication, read state,
    and ownership.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test provider-disabled mode, failure, retry, deduplication, read
    state, and ownership.
-   Persist all required data and audit events consistently for: Test
    provider-disabled mode, failure, retry, deduplication, read state,
    and ownership.
-   Add at least one positive test and one relevant negative/failure
    test for: Test provider-disabled mode, failure, retry,
    deduplication, read state, and ownership.
-   Document configuration, behavior, limitations, and manual setup for:
    Test provider-disabled mode, failure, retry, deduplication, read
    state, and ownership.

### Directive 0178 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Move
    notification delivery, image processing, optional AI classification,
    overdue checks, escalation, and expensive analytics to background
    tasks where appropriate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Move notification delivery, image processing, optional AI
    classification, overdue checks, escalation, and expensive analytics
    to background tasks where appropriate.
-   Persist all required data and audit events consistently for: Move
    notification delivery, image processing, optional AI classification,
    overdue checks, escalation, and expensive analytics to background
    tasks where appropriate.
-   Add at least one positive test and one relevant negative/failure
    test for: Move notification delivery, image processing, optional AI
    classification, overdue checks, escalation, and expensive analytics
    to background tasks where appropriate.
-   Document configuration, behavior, limitations, and manual setup for:
    Move notification delivery, image processing, optional AI
    classification, overdue checks, escalation, and expensive analytics
    to background tasks where appropriate.

### Directive 0179 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Use a simple
    worker/scheduler suited to the existing stack; do not introduce
    Kafka without need.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use a simple worker/scheduler suited to the existing stack; do
    not introduce Kafka without need.
-   Persist all required data and audit events consistently for: Use a
    simple worker/scheduler suited to the existing stack; do not
    introduce Kafka without need.
-   Add at least one positive test and one relevant negative/failure
    test for: Use a simple worker/scheduler suited to the existing
    stack; do not introduce Kafka without need.
-   Document configuration, behavior, limitations, and manual setup for:
    Use a simple worker/scheduler suited to the existing stack; do not
    introduce Kafka without need.

### Directive 0180 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Use a
    transactional outbox or equivalent for important events when
    database commit and event delivery must stay consistent.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use a transactional outbox or equivalent for important events
    when database commit and event delivery must stay consistent.
-   Persist all required data and audit events consistently for: Use a
    transactional outbox or equivalent for important events when
    database commit and event delivery must stay consistent.
-   Add at least one positive test and one relevant negative/failure
    test for: Use a transactional outbox or equivalent for important
    events when database commit and event delivery must stay consistent.
-   Document configuration, behavior, limitations, and manual setup for:
    Use a transactional outbox or equivalent for important events when
    database commit and event delivery must stay consistent.

### Directive 0181 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Store event
    type, aggregate ID, payload version, minimal payload, created time,
    processing state, attempt count, and sanitized failure details.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store event type, aggregate ID, payload version, minimal
    payload, created time, processing state, attempt count, and
    sanitized failure details.
-   Persist all required data and audit events consistently for: Store
    event type, aggregate ID, payload version, minimal payload, created
    time, processing state, attempt count, and sanitized failure
    details.
-   Add at least one positive test and one relevant negative/failure
    test for: Store event type, aggregate ID, payload version, minimal
    payload, created time, processing state, attempt count, and
    sanitized failure details.
-   Document configuration, behavior, limitations, and manual setup for:
    Store event type, aggregate ID, payload version, minimal payload,
    created time, processing state, attempt count, and sanitized failure
    details.

### Directive 0182 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Make event
    consumers idempotent and jobs safe to run more than once.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Make event consumers idempotent and jobs safe to run more than
    once.
-   Persist all required data and audit events consistently for: Make
    event consumers idempotent and jobs safe to run more than once.
-   Add at least one positive test and one relevant negative/failure
    test for: Make event consumers idempotent and jobs safe to run more
    than once.
-   Document configuration, behavior, limitations, and manual setup for:
    Make event consumers idempotent and jobs safe to run more than once.

### Directive 0183 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Use bounded
    retry counts, timeouts, and backoff.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use bounded retry counts, timeouts, and backoff.
-   Persist all required data and audit events consistently for: Use
    bounded retry counts, timeouts, and backoff.
-   Add at least one positive test and one relevant negative/failure
    test for: Use bounded retry counts, timeouts, and backoff.
-   Document configuration, behavior, limitations, and manual setup for:
    Use bounded retry counts, timeouts, and backoff.

### Directive 0184 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Prevent
    overlapping scheduled runs from creating duplicate escalations.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent overlapping scheduled runs from creating duplicate
    escalations.
-   Persist all required data and audit events consistently for: Prevent
    overlapping scheduled runs from creating duplicate escalations.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent overlapping scheduled runs from creating duplicate
    escalations.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent overlapping scheduled runs from creating duplicate
    escalations.

### Directive 0185 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Expose failed
    jobs to authorized operators and document recovery.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Expose failed jobs to authorized operators and document
    recovery.
-   Persist all required data and audit events consistently for: Expose
    failed jobs to authorized operators and document recovery.
-   Add at least one positive test and one relevant negative/failure
    test for: Expose failed jobs to authorized operators and document
    recovery.
-   Document configuration, behavior, limitations, and manual setup for:
    Expose failed jobs to authorized operators and document recovery.

### Directive 0186 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Ensure a worker
    restart does not lose committed required work.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Ensure a worker restart does not lose committed required work.
-   Persist all required data and audit events consistently for: Ensure
    a worker restart does not lose committed required work.
-   Add at least one positive test and one relevant negative/failure
    test for: Ensure a worker restart does not lose committed required
    work.
-   Document configuration, behavior, limitations, and manual setup for:
    Ensure a worker restart does not lose committed required work.

### Directive 0187 --- Background jobs and reliable events

-   Implement this requirement in the actual repository: Test repeated
    delivery, rollback, worker failure, retry, and duplicate processing.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test repeated delivery, rollback, worker failure, retry, and
    duplicate processing.
-   Persist all required data and audit events consistently for: Test
    repeated delivery, rollback, worker failure, retry, and duplicate
    processing.
-   Add at least one positive test and one relevant negative/failure
    test for: Test repeated delivery, rollback, worker failure, retry,
    and duplicate processing.
-   Document configuration, behavior, limitations, and manual setup for:
    Test repeated delivery, rollback, worker failure, retry, and
    duplicate processing.

### Directive 0188 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Create a
    provider-neutral interface for classification and natural-language
    service search.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create a provider-neutral interface for classification and
    natural-language service search.
-   Persist all required data and audit events consistently for: Create
    a provider-neutral interface for classification and natural-language
    service search.
-   Add at least one positive test and one relevant negative/failure
    test for: Create a provider-neutral interface for classification and
    natural-language service search.
-   Document configuration, behavior, limitations, and manual setup for:
    Create a provider-neutral interface for classification and
    natural-language service search.

### Directive 0189 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Keep
    deterministic keyword/synonym matching as the fallback.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep deterministic keyword/synonym matching as the fallback.
-   Persist all required data and audit events consistently for: Keep
    deterministic keyword/synonym matching as the fallback.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep deterministic keyword/synonym matching as the
    fallback.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep deterministic keyword/synonym matching as the fallback.

### Directive 0190 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Validate AI
    structured output against configured category and service IDs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate AI structured output against configured category and
    service IDs.
-   Persist all required data and audit events consistently for:
    Validate AI structured output against configured category and
    service IDs.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate AI structured output against configured category
    and service IDs.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate AI structured output against configured category and
    service IDs.

### Directive 0191 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Store
    suggestion, confidence, provider/model version, and timestamp where
    appropriate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store suggestion, confidence, provider/model version, and
    timestamp where appropriate.
-   Persist all required data and audit events consistently for: Store
    suggestion, confidence, provider/model version, and timestamp where
    appropriate.
-   Add at least one positive test and one relevant negative/failure
    test for: Store suggestion, confidence, provider/model version, and
    timestamp where appropriate.
-   Document configuration, behavior, limitations, and manual setup for:
    Store suggestion, confidence, provider/model version, and timestamp
    where appropriate.

### Directive 0192 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Use a
    configurable confidence threshold and send uncertain results to
    manual review.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use a configurable confidence threshold and send uncertain
    results to manual review.
-   Persist all required data and audit events consistently for: Use a
    configurable confidence threshold and send uncertain results to
    manual review.
-   Add at least one positive test and one relevant negative/failure
    test for: Use a configurable confidence threshold and send uncertain
    results to manual review.
-   Document configuration, behavior, limitations, and manual setup for:
    Use a configurable confidence threshold and send uncertain results
    to manual review.

### Directive 0193 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Treat model
    output as untrusted data; guard against prompt injection in user
    text and uploads.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Treat model output as untrusted data; guard against prompt
    injection in user text and uploads.
-   Persist all required data and audit events consistently for: Treat
    model output as untrusted data; guard against prompt injection in
    user text and uploads.
-   Add at least one positive test and one relevant negative/failure
    test for: Treat model output as untrusted data; guard against prompt
    injection in user text and uploads.
-   Document configuration, behavior, limitations, and manual setup for:
    Treat model output as untrusted data; guard against prompt injection
    in user text and uploads.

### Directive 0194 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Use timeouts,
    usage limits, and safe retries.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use timeouts, usage limits, and safe retries.
-   Persist all required data and audit events consistently for: Use
    timeouts, usage limits, and safe retries.
-   Add at least one positive test and one relevant negative/failure
    test for: Use timeouts, usage limits, and safe retries.
-   Document configuration, behavior, limitations, and manual setup for:
    Use timeouts, usage limits, and safe retries.

### Directive 0195 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Do not require
    AI credentials for complaint submission or tracking.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not require AI credentials for complaint submission or
    tracking.
-   Persist all required data and audit events consistently for: Do not
    require AI credentials for complaint submission or tracking.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not require AI credentials for complaint submission or
    tracking.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not require AI credentials for complaint submission or tracking.

### Directive 0196 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Send only
    necessary data to third-party providers and document privacy
    implications.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Send only necessary data to third-party providers and document
    privacy implications.
-   Persist all required data and audit events consistently for: Send
    only necessary data to third-party providers and document privacy
    implications.
-   Add at least one positive test and one relevant negative/failure
    test for: Send only necessary data to third-party providers and
    document privacy implications.
-   Document configuration, behavior, limitations, and manual setup for:
    Send only necessary data to third-party providers and document
    privacy implications.

### Directive 0197 --- AI and natural-language service discovery

-   Implement this requirement in the actual repository: Test provider
    timeout, malformed output, unknown category, low confidence, and
    disabled-provider behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test provider timeout, malformed output, unknown category, low
    confidence, and disabled-provider behavior.
-   Persist all required data and audit events consistently for: Test
    provider timeout, malformed output, unknown category, low
    confidence, and disabled-provider behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Test provider timeout, malformed output, unknown category,
    low confidence, and disabled-provider behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Test provider timeout, malformed output, unknown category, low
    confidence, and disabled-provider behavior.

### Directive 0198 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Find candidate
    duplicates using category, geographic proximity, time window,
    status, and optional text similarity.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Find candidate duplicates using category, geographic proximity,
    time window, status, and optional text similarity.
-   Persist all required data and audit events consistently for: Find
    candidate duplicates using category, geographic proximity, time
    window, status, and optional text similarity.
-   Add at least one positive test and one relevant negative/failure
    test for: Find candidate duplicates using category, geographic
    proximity, time window, status, and optional text similarity.
-   Document configuration, behavior, limitations, and manual setup for:
    Find candidate duplicates using category, geographic proximity, time
    window, status, and optional text similarity.

### Directive 0199 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Bound candidate
    radius and result count and avoid expensive unbounded searches.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Bound candidate radius and result count and avoid expensive
    unbounded searches.
-   Persist all required data and audit events consistently for: Bound
    candidate radius and result count and avoid expensive unbounded
    searches.
-   Add at least one positive test and one relevant negative/failure
    test for: Bound candidate radius and result count and avoid
    expensive unbounded searches.
-   Document configuration, behavior, limitations, and manual setup for:
    Bound candidate radius and result count and avoid expensive
    unbounded searches.

### Directive 0200 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Show only
    complaint data the caller is allowed to see.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Show only complaint data the caller is allowed to see.
-   Persist all required data and audit events consistently for: Show
    only complaint data the caller is allowed to see.
-   Add at least one positive test and one relevant negative/failure
    test for: Show only complaint data the caller is allowed to see.
-   Document configuration, behavior, limitations, and manual setup for:
    Show only complaint data the caller is allowed to see.

### Directive 0201 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Do not
    automatically merge based only on text similarity.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not automatically merge based only on text similarity.
-   Persist all required data and audit events consistently for: Do not
    automatically merge based only on text similarity.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not automatically merge based only on text similarity.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not automatically merge based only on text similarity.

### Directive 0202 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Allow
    authorized staff to merge verified duplicates with reason and audit
    history.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow authorized staff to merge verified duplicates with reason
    and audit history.
-   Persist all required data and audit events consistently for: Allow
    authorized staff to merge verified duplicates with reason and audit
    history.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow authorized staff to merge verified duplicates with
    reason and audit history.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow authorized staff to merge verified duplicates with reason and
    audit history.

### Directive 0203 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Prevent merge
    cycles and preserve each original report and reporter relationship.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent merge cycles and preserve each original report and
    reporter relationship.
-   Persist all required data and audit events consistently for: Prevent
    merge cycles and preserve each original report and reporter
    relationship.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent merge cycles and preserve each original report and
    reporter relationship.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent merge cycles and preserve each original report and reporter
    relationship.

### Directive 0204 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Allow
    support/vote functionality only if public visibility and abuse
    controls are implemented.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow support/vote functionality only if public visibility and
    abuse controls are implemented.
-   Persist all required data and audit events consistently for: Allow
    support/vote functionality only if public visibility and abuse
    controls are implemented.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow support/vote functionality only if public visibility
    and abuse controls are implemented.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow support/vote functionality only if public visibility and abuse
    controls are implemented.

### Directive 0205 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Prevent
    duplicate support from the same account where policy forbids it.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent duplicate support from the same account where policy
    forbids it.
-   Persist all required data and audit events consistently for: Prevent
    duplicate support from the same account where policy forbids it.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent duplicate support from the same account where
    policy forbids it.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent duplicate support from the same account where policy forbids
    it.

### Directive 0206 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Do not expose
    supporter identities.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not expose supporter identities.
-   Persist all required data and audit events consistently for: Do not
    expose supporter identities.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not expose supporter identities.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not expose supporter identities.

### Directive 0207 --- Duplicate detection and community support

-   Implement this requirement in the actual repository: Test nearby
    matches, distant similar text, different categories, unauthorized
    merge, and repeated support.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test nearby matches, distant similar text, different categories,
    unauthorized merge, and repeated support.
-   Persist all required data and audit events consistently for: Test
    nearby matches, distant similar text, different categories,
    unauthorized merge, and repeated support.
-   Add at least one positive test and one relevant negative/failure
    test for: Test nearby matches, distant similar text, different
    categories, unauthorized merge, and repeated support.
-   Document configuration, behavior, limitations, and manual setup for:
    Test nearby matches, distant similar text, different categories,
    unauthorized merge, and repeated support.

### Directive 0208 --- Media and file storage

-   Implement this requirement in the actual repository: Validate file
    type by content where feasible, size, upload ownership, and allowed
    formats.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate file type by content where feasible, size, upload
    ownership, and allowed formats.
-   Persist all required data and audit events consistently for:
    Validate file type by content where feasible, size, upload
    ownership, and allowed formats.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate file type by content where feasible, size, upload
    ownership, and allowed formats.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate file type by content where feasible, size, upload
    ownership, and allowed formats.

### Directive 0209 --- Media and file storage

-   Implement this requirement in the actual repository: Reject
    executable or disallowed formats and enforce request/file size
    limits.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Reject executable or disallowed formats and enforce request/file
    size limits.
-   Persist all required data and audit events consistently for: Reject
    executable or disallowed formats and enforce request/file size
    limits.
-   Add at least one positive test and one relevant negative/failure
    test for: Reject executable or disallowed formats and enforce
    request/file size limits.
-   Document configuration, behavior, limitations, and manual setup for:
    Reject executable or disallowed formats and enforce request/file
    size limits.

### Directive 0210 --- Media and file storage

-   Implement this requirement in the actual repository: Generate safe
    storage keys; never use raw client filenames as paths.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Generate safe storage keys; never use raw client filenames as
    paths.
-   Persist all required data and audit events consistently for:
    Generate safe storage keys; never use raw client filenames as paths.
-   Add at least one positive test and one relevant negative/failure
    test for: Generate safe storage keys; never use raw client filenames
    as paths.
-   Document configuration, behavior, limitations, and manual setup for:
    Generate safe storage keys; never use raw client filenames as paths.

### Directive 0211 --- Media and file storage

-   Implement this requirement in the actual repository: Store metadata
    separately from complaint records and use private storage by
    default.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store metadata separately from complaint records and use private
    storage by default.
-   Persist all required data and audit events consistently for: Store
    metadata separately from complaint records and use private storage
    by default.
-   Add at least one positive test and one relevant negative/failure
    test for: Store metadata separately from complaint records and use
    private storage by default.
-   Document configuration, behavior, limitations, and manual setup for:
    Store metadata separately from complaint records and use private
    storage by default.

### Directive 0212 --- Media and file storage

-   Implement this requirement in the actual repository: Check
    authorization on every file retrieval and use expiring signed URLs
    when appropriate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Check authorization on every file retrieval and use expiring
    signed URLs when appropriate.
-   Persist all required data and audit events consistently for: Check
    authorization on every file retrieval and use expiring signed URLs
    when appropriate.
-   Add at least one positive test and one relevant negative/failure
    test for: Check authorization on every file retrieval and use
    expiring signed URLs when appropriate.
-   Document configuration, behavior, limitations, and manual setup for:
    Check authorization on every file retrieval and use expiring signed
    URLs when appropriate.

### Directive 0213 --- Media and file storage

-   Implement this requirement in the actual repository: Scan uploads
    for malware where feasible and track scan state.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Scan uploads for malware where feasible and track scan state.
-   Persist all required data and audit events consistently for: Scan
    uploads for malware where feasible and track scan state.
-   Add at least one positive test and one relevant negative/failure
    test for: Scan uploads for malware where feasible and track scan
    state.
-   Document configuration, behavior, limitations, and manual setup for:
    Scan uploads for malware where feasible and track scan state.

### Directive 0214 --- Media and file storage

-   Implement this requirement in the actual repository: Strip EXIF data
    from public derivatives when necessary.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Strip EXIF data from public derivatives when necessary.
-   Persist all required data and audit events consistently for: Strip
    EXIF data from public derivatives when necessary.
-   Add at least one positive test and one relevant negative/failure
    test for: Strip EXIF data from public derivatives when necessary.
-   Document configuration, behavior, limitations, and manual setup for:
    Strip EXIF data from public derivatives when necessary.

### Directive 0215 --- Media and file storage

-   Implement this requirement in the actual repository: Handle
    interrupted uploads, orphan cleanup, and expired temporary files
    safely.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle interrupted uploads, orphan cleanup, and expired
    temporary files safely.
-   Persist all required data and audit events consistently for: Handle
    interrupted uploads, orphan cleanup, and expired temporary files
    safely.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle interrupted uploads, orphan cleanup, and expired
    temporary files safely.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle interrupted uploads, orphan cleanup, and expired temporary
    files safely.

### Directive 0216 --- Media and file storage

-   Implement this requirement in the actual repository: Do not expose
    storage credentials or private evidence through public complaint
    APIs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not expose storage credentials or private evidence through
    public complaint APIs.
-   Persist all required data and audit events consistently for: Do not
    expose storage credentials or private evidence through public
    complaint APIs.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not expose storage credentials or private evidence
    through public complaint APIs.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not expose storage credentials or private evidence through public
    complaint APIs.

### Directive 0217 --- Media and file storage

-   Implement this requirement in the actual repository: Test oversized
    files, unsupported content, path traversal, ownership, private
    access, and provider failure.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test oversized files, unsupported content, path traversal,
    ownership, private access, and provider failure.
-   Persist all required data and audit events consistently for: Test
    oversized files, unsupported content, path traversal, ownership,
    private access, and provider failure.
-   Add at least one positive test and one relevant negative/failure
    test for: Test oversized files, unsupported content, path traversal,
    ownership, private access, and provider failure.
-   Document configuration, behavior, limitations, and manual setup for:
    Test oversized files, unsupported content, path traversal,
    ownership, private access, and provider failure.

### Directive 0218 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Separate
    resident-visible comments from staff-only internal notes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Separate resident-visible comments from staff-only internal
    notes.
-   Persist all required data and audit events consistently for:
    Separate resident-visible comments from staff-only internal notes.
-   Add at least one positive test and one relevant negative/failure
    test for: Separate resident-visible comments from staff-only
    internal notes.
-   Document configuration, behavior, limitations, and manual setup for:
    Separate resident-visible comments from staff-only internal notes.

### Directive 0219 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Validate
    comment length and prevent author/timestamp spoofing.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate comment length and prevent author/timestamp spoofing.
-   Persist all required data and audit events consistently for:
    Validate comment length and prevent author/timestamp spoofing.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate comment length and prevent author/timestamp
    spoofing.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate comment length and prevent author/timestamp spoofing.

### Directive 0220 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Allow
    authorized staff to request more information from a resident.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow authorized staff to request more information from a
    resident.
-   Persist all required data and audit events consistently for: Allow
    authorized staff to request more information from a resident.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow authorized staff to request more information from a
    resident.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow authorized staff to request more information from a resident.

### Directive 0221 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Store
    resolution notes and evidence separately from ordinary comments.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store resolution notes and evidence separately from ordinary
    comments.
-   Persist all required data and audit events consistently for: Store
    resolution notes and evidence separately from ordinary comments.
-   Add at least one positive test and one relevant negative/failure
    test for: Store resolution notes and evidence separately from
    ordinary comments.
-   Document configuration, behavior, limitations, and manual setup for:
    Store resolution notes and evidence separately from ordinary
    comments.

### Directive 0222 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Apply file
    access controls to before/after photos and other evidence.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Apply file access controls to before/after photos and other
    evidence.
-   Persist all required data and audit events consistently for: Apply
    file access controls to before/after photos and other evidence.
-   Add at least one positive test and one relevant negative/failure
    test for: Apply file access controls to before/after photos and
    other evidence.
-   Document configuration, behavior, limitations, and manual setup for:
    Apply file access controls to before/after photos and other
    evidence.

### Directive 0223 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Allow feedback
    only for eligible complaint states and authorized reporters.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow feedback only for eligible complaint states and authorized
    reporters.
-   Persist all required data and audit events consistently for: Allow
    feedback only for eligible complaint states and authorized
    reporters.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow feedback only for eligible complaint states and
    authorized reporters.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow feedback only for eligible complaint states and authorized
    reporters.

### Directive 0224 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Define a
    bounded rating scale and prevent duplicate feedback unless editing
    is supported.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define a bounded rating scale and prevent duplicate feedback
    unless editing is supported.
-   Persist all required data and audit events consistently for: Define
    a bounded rating scale and prevent duplicate feedback unless editing
    is supported.
-   Add at least one positive test and one relevant negative/failure
    test for: Define a bounded rating scale and prevent duplicate
    feedback unless editing is supported.
-   Document configuration, behavior, limitations, and manual setup for:
    Define a bounded rating scale and prevent duplicate feedback unless
    editing is supported.

### Directive 0225 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Allow a reopen
    request under a documented policy and preserve previous resolution
    history.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow a reopen request under a documented policy and preserve
    previous resolution history.
-   Persist all required data and audit events consistently for: Allow a
    reopen request under a documented policy and preserve previous
    resolution history.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow a reopen request under a documented policy and
    preserve previous resolution history.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow a reopen request under a documented policy and preserve
    previous resolution history.

### Directive 0226 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Moderate public
    content where community features exist and audit moderation actions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Moderate public content where community features exist and audit
    moderation actions.
-   Persist all required data and audit events consistently for:
    Moderate public content where community features exist and audit
    moderation actions.
-   Add at least one positive test and one relevant negative/failure
    test for: Moderate public content where community features exist and
    audit moderation actions.
-   Document configuration, behavior, limitations, and manual setup for:
    Moderate public content where community features exist and audit
    moderation actions.

### Directive 0227 --- Comments, notes, evidence, and feedback

-   Implement this requirement in the actual repository: Test that
    private notes and evidence never leak through resident endpoints or
    notifications.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test that private notes and evidence never leak through resident
    endpoints or notifications.
-   Persist all required data and audit events consistently for: Test
    that private notes and evidence never leak through resident
    endpoints or notifications.
-   Add at least one positive test and one relevant negative/failure
    test for: Test that private notes and evidence never leak through
    resident endpoints or notifications.
-   Document configuration, behavior, limitations, and manual setup for:
    Test that private notes and evidence never leak through resident
    endpoints or notifications.

### Directive 0228 --- Analytics and reporting

-   Implement this requirement in the actual repository: Compute all
    metrics from persisted records, never hardcoded dashboard numbers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Compute all metrics from persisted records, never hardcoded
    dashboard numbers.
-   Persist all required data and audit events consistently for: Compute
    all metrics from persisted records, never hardcoded dashboard
    numbers.
-   Add at least one positive test and one relevant negative/failure
    test for: Compute all metrics from persisted records, never
    hardcoded dashboard numbers.
-   Document configuration, behavior, limitations, and manual setup for:
    Compute all metrics from persisted records, never hardcoded
    dashboard numbers.

### Directive 0229 --- Analytics and reporting

-   Implement this requirement in the actual repository: Define totals
    for open, resolved, closed, rejected, withdrawn, overdue, and
    reopened complaints.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define totals for open, resolved, closed, rejected, withdrawn,
    overdue, and reopened complaints.
-   Persist all required data and audit events consistently for: Define
    totals for open, resolved, closed, rejected, withdrawn, overdue, and
    reopened complaints.
-   Add at least one positive test and one relevant negative/failure
    test for: Define totals for open, resolved, closed, rejected,
    withdrawn, overdue, and reopened complaints.
-   Document configuration, behavior, limitations, and manual setup for:
    Define totals for open, resolved, closed, rejected, withdrawn,
    overdue, and reopened complaints.

### Directive 0230 --- Analytics and reporting

-   Implement this requirement in the actual repository: Calculate
    average and median resolution time with documented start/end events.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Calculate average and median resolution time with documented
    start/end events.
-   Persist all required data and audit events consistently for:
    Calculate average and median resolution time with documented
    start/end events.
-   Add at least one positive test and one relevant negative/failure
    test for: Calculate average and median resolution time with
    documented start/end events.
-   Document configuration, behavior, limitations, and manual setup for:
    Calculate average and median resolution time with documented
    start/end events.

### Directive 0231 --- Analytics and reporting

-   Implement this requirement in the actual repository: Define SLA
    compliance numerator and denominator explicitly.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define SLA compliance numerator and denominator explicitly.
-   Persist all required data and audit events consistently for: Define
    SLA compliance numerator and denominator explicitly.
-   Add at least one positive test and one relevant negative/failure
    test for: Define SLA compliance numerator and denominator
    explicitly.
-   Document configuration, behavior, limitations, and manual setup for:
    Define SLA compliance numerator and denominator explicitly.

### Directive 0232 --- Analytics and reporting

-   Implement this requirement in the actual repository: Aggregate by
    department, category, ward, priority, and date range.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Aggregate by department, category, ward, priority, and date
    range.
-   Persist all required data and audit events consistently for:
    Aggregate by department, category, ward, priority, and date range.
-   Add at least one positive test and one relevant negative/failure
    test for: Aggregate by department, category, ward, priority, and
    date range.
-   Document configuration, behavior, limitations, and manual setup for:
    Aggregate by department, category, ward, priority, and date range.

### Directive 0233 --- Analytics and reporting

-   Implement this requirement in the actual repository: Enforce role
    scope and privacy-safe aggregation in analytics queries.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Enforce role scope and privacy-safe aggregation in analytics
    queries.
-   Persist all required data and audit events consistently for: Enforce
    role scope and privacy-safe aggregation in analytics queries.
-   Add at least one positive test and one relevant negative/failure
    test for: Enforce role scope and privacy-safe aggregation in
    analytics queries.
-   Document configuration, behavior, limitations, and manual setup for:
    Enforce role scope and privacy-safe aggregation in analytics
    queries.

### Directive 0234 --- Analytics and reporting

-   Implement this requirement in the actual repository: Support CSV
    exports only for authorized users and bounded data ranges.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support CSV exports only for authorized users and bounded data
    ranges.
-   Persist all required data and audit events consistently for: Support
    CSV exports only for authorized users and bounded data ranges.
-   Add at least one positive test and one relevant negative/failure
    test for: Support CSV exports only for authorized users and bounded
    data ranges.
-   Document configuration, behavior, limitations, and manual setup for:
    Support CSV exports only for authorized users and bounded data
    ranges.

### Directive 0235 --- Analytics and reporting

-   Implement this requirement in the actual repository: Mitigate CSV
    formula injection for user-controlled strings.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Mitigate CSV formula injection for user-controlled strings.
-   Persist all required data and audit events consistently for:
    Mitigate CSV formula injection for user-controlled strings.
-   Add at least one positive test and one relevant negative/failure
    test for: Mitigate CSV formula injection for user-controlled
    strings.
-   Document configuration, behavior, limitations, and manual setup for:
    Mitigate CSV formula injection for user-controlled strings.

### Directive 0236 --- Analytics and reporting

-   Implement this requirement in the actual repository: Handle empty
    data and timezone boundaries consistently.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle empty data and timezone boundaries consistently.
-   Persist all required data and audit events consistently for: Handle
    empty data and timezone boundaries consistently.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle empty data and timezone boundaries consistently.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle empty data and timezone boundaries consistently.

### Directive 0237 --- Analytics and reporting

-   Implement this requirement in the actual repository: Test every
    metric against known fixtures and document its definition.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test every metric against known fixtures and document its
    definition.
-   Persist all required data and audit events consistently for: Test
    every metric against known fixtures and document its definition.
-   Add at least one positive test and one relevant negative/failure
    test for: Test every metric against known fixtures and document its
    definition.
-   Document configuration, behavior, limitations, and manual setup for:
    Test every metric against known fixtures and document its
    definition.

### Directive 0238 --- Admin configuration

-   Implement this requirement in the actual repository: Allow
    authorized admins to manage departments, officers, categories,
    services, wards, routing rules, SLA policies, notification
    templates, languages, and public announcements.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow authorized admins to manage departments, officers,
    categories, services, wards, routing rules, SLA policies,
    notification templates, languages, and public announcements.
-   Persist all required data and audit events consistently for: Allow
    authorized admins to manage departments, officers, categories,
    services, wards, routing rules, SLA policies, notification
    templates, languages, and public announcements.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow authorized admins to manage departments, officers,
    categories, services, wards, routing rules, SLA policies,
    notification templates, languages, and public announcements.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow authorized admins to manage departments, officers, categories,
    services, wards, routing rules, SLA policies, notification
    templates, languages, and public announcements.

### Directive 0239 --- Admin configuration

-   Implement this requirement in the actual repository: Use validation
    and authorization for every administrative endpoint.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use validation and authorization for every administrative
    endpoint.
-   Persist all required data and audit events consistently for: Use
    validation and authorization for every administrative endpoint.
-   Add at least one positive test and one relevant negative/failure
    test for: Use validation and authorization for every administrative
    endpoint.
-   Document configuration, behavior, limitations, and manual setup for:
    Use validation and authorization for every administrative endpoint.

### Directive 0240 --- Admin configuration

-   Implement this requirement in the actual repository: Record actor,
    timestamp, and old/new values for critical policy changes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record actor, timestamp, and old/new values for critical policy
    changes.
-   Persist all required data and audit events consistently for: Record
    actor, timestamp, and old/new values for critical policy changes.
-   Add at least one positive test and one relevant negative/failure
    test for: Record actor, timestamp, and old/new values for critical
    policy changes.
-   Document configuration, behavior, limitations, and manual setup for:
    Record actor, timestamp, and old/new values for critical policy
    changes.

### Directive 0241 --- Admin configuration

-   Implement this requirement in the actual repository: Version routing
    and SLA rules or preserve enough history to explain past decisions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Version routing and SLA rules or preserve enough history to
    explain past decisions.
-   Persist all required data and audit events consistently for: Version
    routing and SLA rules or preserve enough history to explain past
    decisions.
-   Add at least one positive test and one relevant negative/failure
    test for: Version routing and SLA rules or preserve enough history
    to explain past decisions.
-   Document configuration, behavior, limitations, and manual setup for:
    Version routing and SLA rules or preserve enough history to explain
    past decisions.

### Directive 0242 --- Admin configuration

-   Implement this requirement in the actual repository: Deactivate
    referenced records instead of deleting history.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Deactivate referenced records instead of deleting history.
-   Persist all required data and audit events consistently for:
    Deactivate referenced records instead of deleting history.
-   Add at least one positive test and one relevant negative/failure
    test for: Deactivate referenced records instead of deleting history.
-   Document configuration, behavior, limitations, and manual setup for:
    Deactivate referenced records instead of deleting history.

### Directive 0243 --- Admin configuration

-   Implement this requirement in the actual repository: Prevent
    administrators from accidentally removing the only fallback queue.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent administrators from accidentally removing the only
    fallback queue.
-   Persist all required data and audit events consistently for: Prevent
    administrators from accidentally removing the only fallback queue.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent administrators from accidentally removing the only
    fallback queue.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent administrators from accidentally removing the only fallback
    queue.

### Directive 0244 --- Admin configuration

-   Implement this requirement in the actual repository: Allow safe
    activation/deactivation of optional modules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow safe activation/deactivation of optional modules.
-   Persist all required data and audit events consistently for: Allow
    safe activation/deactivation of optional modules.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow safe activation/deactivation of optional modules.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow safe activation/deactivation of optional modules.

### Directive 0245 --- Admin configuration

-   Implement this requirement in the actual repository: Provide a
    public announcement lifecycle with draft/published/expired states if
    included.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a public announcement lifecycle with
    draft/published/expired states if included.
-   Persist all required data and audit events consistently for: Provide
    a public announcement lifecycle with draft/published/expired states
    if included.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a public announcement lifecycle with
    draft/published/expired states if included.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a public announcement lifecycle with draft/published/expired
    states if included.

### Directive 0246 --- Admin configuration

-   Implement this requirement in the actual repository: Label seed
    announcements as demo data and do not fabricate official notices.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Label seed announcements as demo data and do not fabricate
    official notices.
-   Persist all required data and audit events consistently for: Label
    seed announcements as demo data and do not fabricate official
    notices.
-   Add at least one positive test and one relevant negative/failure
    test for: Label seed announcements as demo data and do not fabricate
    official notices.
-   Document configuration, behavior, limitations, and manual setup for:
    Label seed announcements as demo data and do not fabricate official
    notices.

### Directive 0247 --- Admin configuration

-   Implement this requirement in the actual repository: Test
    unauthorized changes, invalid references, and historical integrity.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test unauthorized changes, invalid references, and historical
    integrity.
-   Persist all required data and audit events consistently for: Test
    unauthorized changes, invalid references, and historical integrity.
-   Add at least one positive test and one relevant negative/failure
    test for: Test unauthorized changes, invalid references, and
    historical integrity.
-   Document configuration, behavior, limitations, and manual setup for:
    Test unauthorized changes, invalid references, and historical
    integrity.

### Directive 0248 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Use
    parameterized database access and explicit schemas to prevent
    injection and mass assignment.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use parameterized database access and explicit schemas to
    prevent injection and mass assignment.
-   Persist all required data and audit events consistently for: Use
    parameterized database access and explicit schemas to prevent
    injection and mass assignment.
-   Add at least one positive test and one relevant negative/failure
    test for: Use parameterized database access and explicit schemas to
    prevent injection and mass assignment.
-   Document configuration, behavior, limitations, and manual setup for:
    Use parameterized database access and explicit schemas to prevent
    injection and mass assignment.

### Directive 0249 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Use TLS in
    deployed environments, secure authentication settings, and
    least-privilege database credentials.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use TLS in deployed environments, secure authentication
    settings, and least-privilege database credentials.
-   Persist all required data and audit events consistently for: Use TLS
    in deployed environments, secure authentication settings, and
    least-privilege database credentials.
-   Add at least one positive test and one relevant negative/failure
    test for: Use TLS in deployed environments, secure authentication
    settings, and least-privilege database credentials.
-   Document configuration, behavior, limitations, and manual setup for:
    Use TLS in deployed environments, secure authentication settings,
    and least-privilege database credentials.

### Directive 0250 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Set rate limits
    for login, recovery, complaint creation, search, uploads, and
    expensive AI routes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Set rate limits for login, recovery, complaint creation, search,
    uploads, and expensive AI routes.
-   Persist all required data and audit events consistently for: Set
    rate limits for login, recovery, complaint creation, search,
    uploads, and expensive AI routes.
-   Add at least one positive test and one relevant negative/failure
    test for: Set rate limits for login, recovery, complaint creation,
    search, uploads, and expensive AI routes.
-   Document configuration, behavior, limitations, and manual setup for:
    Set rate limits for login, recovery, complaint creation, search,
    uploads, and expensive AI routes.

### Directive 0251 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Use safe
    generic errors and do not expose stack traces in production.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use safe generic errors and do not expose stack traces in
    production.
-   Persist all required data and audit events consistently for: Use
    safe generic errors and do not expose stack traces in production.
-   Add at least one positive test and one relevant negative/failure
    test for: Use safe generic errors and do not expose stack traces in
    production.
-   Document configuration, behavior, limitations, and manual setup for:
    Use safe generic errors and do not expose stack traces in
    production.

### Directive 0252 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Redact
    passwords, tokens, authorization headers, signed URLs, and sensitive
    request bodies from logs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Redact passwords, tokens, authorization headers, signed URLs,
    and sensitive request bodies from logs.
-   Persist all required data and audit events consistently for: Redact
    passwords, tokens, authorization headers, signed URLs, and sensitive
    request bodies from logs.
-   Add at least one positive test and one relevant negative/failure
    test for: Redact passwords, tokens, authorization headers, signed
    URLs, and sensitive request bodies from logs.
-   Document configuration, behavior, limitations, and manual setup for:
    Redact passwords, tokens, authorization headers, signed URLs, and
    sensitive request bodies from logs.

### Directive 0253 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Collect only
    necessary personal data and document visibility, retention,
    correction, archival, and deletion rules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Collect only necessary personal data and document visibility,
    retention, correction, archival, and deletion rules.
-   Persist all required data and audit events consistently for: Collect
    only necessary personal data and document visibility, retention,
    correction, archival, and deletion rules.
-   Add at least one positive test and one relevant negative/failure
    test for: Collect only necessary personal data and document
    visibility, retention, correction, archival, and deletion rules.
-   Document configuration, behavior, limitations, and manual setup for:
    Collect only necessary personal data and document visibility,
    retention, correction, archival, and deletion rules.

### Directive 0254 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Do not expose
    reporter phone/email, private descriptions, exact home coordinates,
    or internal notes publicly.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not expose reporter phone/email, private descriptions, exact
    home coordinates, or internal notes publicly.
-   Persist all required data and audit events consistently for: Do not
    expose reporter phone/email, private descriptions, exact home
    coordinates, or internal notes publicly.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not expose reporter phone/email, private descriptions,
    exact home coordinates, or internal notes publicly.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not expose reporter phone/email, private descriptions, exact home
    coordinates, or internal notes publicly.

### Directive 0255 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Restrict
    exports and audit log access and record sensitive bulk actions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Restrict exports and audit log access and record sensitive bulk
    actions.
-   Persist all required data and audit events consistently for:
    Restrict exports and audit log access and record sensitive bulk
    actions.
-   Add at least one positive test and one relevant negative/failure
    test for: Restrict exports and audit log access and record sensitive
    bulk actions.
-   Document configuration, behavior, limitations, and manual setup for:
    Restrict exports and audit log access and record sensitive bulk
    actions.

### Directive 0256 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Follow
    applicable Indian privacy and data-protection requirements without
    claiming legal compliance absent review.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Follow applicable Indian privacy and data-protection
    requirements without claiming legal compliance absent review.
-   Persist all required data and audit events consistently for: Follow
    applicable Indian privacy and data-protection requirements without
    claiming legal compliance absent review.
-   Add at least one positive test and one relevant negative/failure
    test for: Follow applicable Indian privacy and data-protection
    requirements without claiming legal compliance absent review.
-   Document configuration, behavior, limitations, and manual setup for:
    Follow applicable Indian privacy and data-protection requirements
    without claiming legal compliance absent review.

### Directive 0257 --- Security, privacy, and abuse prevention

-   Implement this requirement in the actual repository: Test IDOR,
    privilege escalation, cross-department access, upload abuse, rate
    limits, public leakage, and secret exposure.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test IDOR, privilege escalation, cross-department access, upload
    abuse, rate limits, public leakage, and secret exposure.
-   Persist all required data and audit events consistently for: Test
    IDOR, privilege escalation, cross-department access, upload abuse,
    rate limits, public leakage, and secret exposure.
-   Add at least one positive test and one relevant negative/failure
    test for: Test IDOR, privilege escalation, cross-department access,
    upload abuse, rate limits, public leakage, and secret exposure.
-   Document configuration, behavior, limitations, and manual setup for:
    Test IDOR, privilege escalation, cross-department access, upload
    abuse, rate limits, public leakage, and secret exposure.

### Directive 0258 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Keep
    map/geocoding provider code behind an adapter and credentials in
    environment settings.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep map/geocoding provider code behind an adapter and
    credentials in environment settings.
-   Persist all required data and audit events consistently for: Keep
    map/geocoding provider code behind an adapter and credentials in
    environment settings.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep map/geocoding provider code behind an adapter and
    credentials in environment settings.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep map/geocoding provider code behind an adapter and credentials
    in environment settings.

### Directive 0259 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Handle provider
    timeouts, rate limits, invalid results, ambiguous addresses, and
    missing results.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle provider timeouts, rate limits, invalid results,
    ambiguous addresses, and missing results.
-   Persist all required data and audit events consistently for: Handle
    provider timeouts, rate limits, invalid results, ambiguous
    addresses, and missing results.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle provider timeouts, rate limits, invalid results,
    ambiguous addresses, and missing results.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle provider timeouts, rate limits, invalid results, ambiguous
    addresses, and missing results.

### Directive 0260 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Do not treat
    reverse geocoding as proof of jurisdiction.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not treat reverse geocoding as proof of jurisdiction.
-   Persist all required data and audit events consistently for: Do not
    treat reverse geocoding as proof of jurisdiction.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not treat reverse geocoding as proof of jurisdiction.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not treat reverse geocoding as proof of jurisdiction.

### Directive 0261 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Cache only when
    provider terms and data freshness permit.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Cache only when provider terms and data freshness permit.
-   Persist all required data and audit events consistently for: Cache
    only when provider terms and data freshness permit.
-   Add at least one positive test and one relevant negative/failure
    test for: Cache only when provider terms and data freshness permit.
-   Document configuration, behavior, limitations, and manual setup for:
    Cache only when provider terms and data freshness permit.

### Directive 0262 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Allow manual
    location correction and a no-GPS fallback.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow manual location correction and a no-GPS fallback.
-   Persist all required data and audit events consistently for: Allow
    manual location correction and a no-GPS fallback.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow manual location correction and a no-GPS fallback.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow manual location correction and a no-GPS fallback.

### Directive 0263 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Keep public map
    output privacy-filtered and bounded.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep public map output privacy-filtered and bounded.
-   Persist all required data and audit events consistently for: Keep
    public map output privacy-filtered and bounded.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep public map output privacy-filtered and bounded.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep public map output privacy-filtered and bounded.

### Directive 0264 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Use verified
    GIS data for boundaries and document data provenance.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use verified GIS data for boundaries and document data
    provenance.
-   Persist all required data and audit events consistently for: Use
    verified GIS data for boundaries and document data provenance.
-   Add at least one positive test and one relevant negative/failure
    test for: Use verified GIS data for boundaries and document data
    provenance.
-   Document configuration, behavior, limitations, and manual setup for:
    Use verified GIS data for boundaries and document data provenance.

### Directive 0265 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Do not send
    private complaint descriptions to map providers unnecessarily.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not send private complaint descriptions to map providers
    unnecessarily.
-   Persist all required data and audit events consistently for: Do not
    send private complaint descriptions to map providers unnecessarily.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not send private complaint descriptions to map
    providers unnecessarily.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not send private complaint descriptions to map providers
    unnecessarily.

### Directive 0266 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Provide mock
    adapters for tests and clearly label mocked behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide mock adapters for tests and clearly label mocked
    behavior.
-   Persist all required data and audit events consistently for: Provide
    mock adapters for tests and clearly label mocked behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide mock adapters for tests and clearly label mocked
    behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide mock adapters for tests and clearly label mocked behavior.

### Directive 0267 --- Search, map, and geocoding integrations

-   Implement this requirement in the actual repository: Test
    provider-disabled, timeout, invalid response, and out-of-area
    behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test provider-disabled, timeout, invalid response, and
    out-of-area behavior.
-   Persist all required data and audit events consistently for: Test
    provider-disabled, timeout, invalid response, and out-of-area
    behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Test provider-disabled, timeout, invalid response, and
    out-of-area behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Test provider-disabled, timeout, invalid response, and out-of-area
    behavior.

### Directive 0268 --- API conventions

-   Implement this requirement in the actual repository: Use consistent
    resource naming and API prefixes matching the repository.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use consistent resource naming and API prefixes matching the
    repository.
-   Persist all required data and audit events consistently for: Use
    consistent resource naming and API prefixes matching the repository.
-   Add at least one positive test and one relevant negative/failure
    test for: Use consistent resource naming and API prefixes matching
    the repository.
-   Document configuration, behavior, limitations, and manual setup for:
    Use consistent resource naming and API prefixes matching the
    repository.

### Directive 0269 --- API conventions

-   Implement this requirement in the actual repository: Define request
    and response schemas for all public endpoints.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define request and response schemas for all public endpoints.
-   Persist all required data and audit events consistently for: Define
    request and response schemas for all public endpoints.
-   Add at least one positive test and one relevant negative/failure
    test for: Define request and response schemas for all public
    endpoints.
-   Document configuration, behavior, limitations, and manual setup for:
    Define request and response schemas for all public endpoints.

### Directive 0270 --- API conventions

-   Implement this requirement in the actual repository: Use consistent
    error objects with stable machine-readable codes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use consistent error objects with stable machine-readable codes.
-   Persist all required data and audit events consistently for: Use
    consistent error objects with stable machine-readable codes.
-   Add at least one positive test and one relevant negative/failure
    test for: Use consistent error objects with stable machine-readable
    codes.
-   Document configuration, behavior, limitations, and manual setup for:
    Use consistent error objects with stable machine-readable codes.

### Directive 0271 --- API conventions

-   Implement this requirement in the actual repository: Use appropriate
    HTTP statuses for validation, authentication, authorization,
    conflicts, rate limits, and internal failures.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use appropriate HTTP statuses for validation, authentication,
    authorization, conflicts, rate limits, and internal failures.
-   Persist all required data and audit events consistently for: Use
    appropriate HTTP statuses for validation, authentication,
    authorization, conflicts, rate limits, and internal failures.
-   Add at least one positive test and one relevant negative/failure
    test for: Use appropriate HTTP statuses for validation,
    authentication, authorization, conflicts, rate limits, and internal
    failures.
-   Document configuration, behavior, limitations, and manual setup for:
    Use appropriate HTTP statuses for validation, authentication,
    authorization, conflicts, rate limits, and internal failures.

### Directive 0272 --- API conventions

-   Implement this requirement in the actual repository: Document every
    endpoint's permissions, request fields, responses, filters, and
    error cases.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document every endpoint's permissions, request fields,
    responses, filters, and error cases.
-   Persist all required data and audit events consistently for:
    Document every endpoint's permissions, request fields, responses,
    filters, and error cases.
-   Add at least one positive test and one relevant negative/failure
    test for: Document every endpoint's permissions, request fields,
    responses, filters, and error cases.
-   Document configuration, behavior, limitations, and manual setup for:
    Document every endpoint's permissions, request fields, responses,
    filters, and error cases.

### Directive 0273 --- API conventions

-   Implement this requirement in the actual repository: Generate or
    maintain OpenAPI documentation that matches the implementation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Generate or maintain OpenAPI documentation that matches the
    implementation.
-   Persist all required data and audit events consistently for:
    Generate or maintain OpenAPI documentation that matches the
    implementation.
-   Add at least one positive test and one relevant negative/failure
    test for: Generate or maintain OpenAPI documentation that matches
    the implementation.
-   Document configuration, behavior, limitations, and manual setup for:
    Generate or maintain OpenAPI documentation that matches the
    implementation.

### Directive 0274 --- API conventions

-   Implement this requirement in the actual repository: Use pagination
    for collections and stable ordering.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use pagination for collections and stable ordering.
-   Persist all required data and audit events consistently for: Use
    pagination for collections and stable ordering.
-   Add at least one positive test and one relevant negative/failure
    test for: Use pagination for collections and stable ordering.
-   Document configuration, behavior, limitations, and manual setup for:
    Use pagination for collections and stable ordering.

### Directive 0275 --- API conventions

-   Implement this requirement in the actual repository: Use a
    correlation/request ID in logs and responses where practical.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use a correlation/request ID in logs and responses where
    practical.
-   Persist all required data and audit events consistently for: Use a
    correlation/request ID in logs and responses where practical.
-   Add at least one positive test and one relevant negative/failure
    test for: Use a correlation/request ID in logs and responses where
    practical.
-   Document configuration, behavior, limitations, and manual setup for:
    Use a correlation/request ID in logs and responses where practical.

### Directive 0276 --- API conventions

-   Implement this requirement in the actual repository: Do not return
    raw ORM objects or exceptions directly.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not return raw ORM objects or exceptions directly.
-   Persist all required data and audit events consistently for: Do not
    return raw ORM objects or exceptions directly.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not return raw ORM objects or exceptions directly.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not return raw ORM objects or exceptions directly.

### Directive 0277 --- API conventions

-   Implement this requirement in the actual repository: Test both
    successful and failed response contracts.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test both successful and failed response contracts.
-   Persist all required data and audit events consistently for: Test
    both successful and failed response contracts.
-   Add at least one positive test and one relevant negative/failure
    test for: Test both successful and failed response contracts.
-   Document configuration, behavior, limitations, and manual setup for:
    Test both successful and failed response contracts.

### Directive 0278 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Provide health
    and, where useful, readiness checks without exposing infrastructure
    secrets.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide health and, where useful, readiness checks without
    exposing infrastructure secrets.
-   Persist all required data and audit events consistently for: Provide
    health and, where useful, readiness checks without exposing
    infrastructure secrets.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide health and, where useful, readiness checks without
    exposing infrastructure secrets.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide health and, where useful, readiness checks without exposing
    infrastructure secrets.

### Directive 0279 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Add structured
    logs with correlation IDs and safe context.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Add structured logs with correlation IDs and safe context.
-   Persist all required data and audit events consistently for: Add
    structured logs with correlation IDs and safe context.
-   Add at least one positive test and one relevant negative/failure
    test for: Add structured logs with correlation IDs and safe context.
-   Document configuration, behavior, limitations, and manual setup for:
    Add structured logs with correlation IDs and safe context.

### Directive 0280 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Document local
    startup, migrations, seeding, workers, tests, linting, and API docs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document local startup, migrations, seeding, workers, tests,
    linting, and API docs.
-   Persist all required data and audit events consistently for:
    Document local startup, migrations, seeding, workers, tests,
    linting, and API docs.
-   Add at least one positive test and one relevant negative/failure
    test for: Document local startup, migrations, seeding, workers,
    tests, linting, and API docs.
-   Document configuration, behavior, limitations, and manual setup for:
    Document local startup, migrations, seeding, workers, tests,
    linting, and API docs.

### Directive 0281 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Do not run
    destructive migrations automatically on every application startup.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not run destructive migrations automatically on every
    application startup.
-   Persist all required data and audit events consistently for: Do not
    run destructive migrations automatically on every application
    startup.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not run destructive migrations automatically on every
    application startup.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not run destructive migrations automatically on every application
    startup.

### Directive 0282 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Document
    production TLS, CORS, secrets, upload storage, backups, and
    recovery.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document production TLS, CORS, secrets, upload storage, backups,
    and recovery.
-   Persist all required data and audit events consistently for:
    Document production TLS, CORS, secrets, upload storage, backups, and
    recovery.
-   Add at least one positive test and one relevant negative/failure
    test for: Document production TLS, CORS, secrets, upload storage,
    backups, and recovery.
-   Document configuration, behavior, limitations, and manual setup for:
    Document production TLS, CORS, secrets, upload storage, backups, and
    recovery.

### Directive 0283 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Provide a safe
    demo reset command that refuses to run in production.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a safe demo reset command that refuses to run in
    production.
-   Persist all required data and audit events consistently for: Provide
    a safe demo reset command that refuses to run in production.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a safe demo reset command that refuses to run in
    production.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a safe demo reset command that refuses to run in production.

### Directive 0284 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Run dependency
    checks where tooling is available.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Run dependency checks where tooling is available.
-   Persist all required data and audit events consistently for: Run
    dependency checks where tooling is available.
-   Add at least one positive test and one relevant negative/failure
    test for: Run dependency checks where tooling is available.
-   Document configuration, behavior, limitations, and manual setup for:
    Run dependency checks where tooling is available.

### Directive 0285 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Verify clean
    database migration and seed repeatability.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Verify clean database migration and seed repeatability.
-   Persist all required data and audit events consistently for: Verify
    clean database migration and seed repeatability.
-   Add at least one positive test and one relevant negative/failure
    test for: Verify clean database migration and seed repeatability.
-   Document configuration, behavior, limitations, and manual setup for:
    Verify clean database migration and seed repeatability.

### Directive 0286 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Keep logs,
    audit records, and business history conceptually separate.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep logs, audit records, and business history conceptually
    separate.
-   Persist all required data and audit events consistently for: Keep
    logs, audit records, and business history conceptually separate.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep logs, audit records, and business history
    conceptually separate.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep logs, audit records, and business history conceptually
    separate.

### Directive 0287 --- Operations, deployment, and observability

-   Implement this requirement in the actual repository: Report
    deployment as successful only if it was actually deployed and
    verified.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Report deployment as successful only if it was actually deployed
    and verified.
-   Persist all required data and audit events consistently for: Report
    deployment as successful only if it was actually deployed and
    verified.
-   Add at least one positive test and one relevant negative/failure
    test for: Report deployment as successful only if it was actually
    deployed and verified.
-   Document configuration, behavior, limitations, and manual setup for:
    Report deployment as successful only if it was actually deployed and
    verified.

### Directive 0288 --- Testing and quality

-   Implement this requirement in the actual repository: Use unit tests
    for routing, state transitions, SLA calculations, priority rules,
    and validation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use unit tests for routing, state transitions, SLA calculations,
    priority rules, and validation.
-   Persist all required data and audit events consistently for: Use
    unit tests for routing, state transitions, SLA calculations,
    priority rules, and validation.
-   Add at least one positive test and one relevant negative/failure
    test for: Use unit tests for routing, state transitions, SLA
    calculations, priority rules, and validation.
-   Document configuration, behavior, limitations, and manual setup for:
    Use unit tests for routing, state transitions, SLA calculations,
    priority rules, and validation.

### Directive 0289 --- Testing and quality

-   Implement this requirement in the actual repository: Use integration
    tests for database transactions, migrations, uniqueness, and
    concurrency-sensitive operations.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use integration tests for database transactions, migrations,
    uniqueness, and concurrency-sensitive operations.
-   Persist all required data and audit events consistently for: Use
    integration tests for database transactions, migrations, uniqueness,
    and concurrency-sensitive operations.
-   Add at least one positive test and one relevant negative/failure
    test for: Use integration tests for database transactions,
    migrations, uniqueness, and concurrency-sensitive operations.
-   Document configuration, behavior, limitations, and manual setup for:
    Use integration tests for database transactions, migrations,
    uniqueness, and concurrency-sensitive operations.

### Directive 0290 --- Testing and quality

-   Implement this requirement in the actual repository: Use API tests
    for authentication, response contracts, pagination, filters, and
    authorization.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use API tests for authentication, response contracts,
    pagination, filters, and authorization.
-   Persist all required data and audit events consistently for: Use API
    tests for authentication, response contracts, pagination, filters,
    and authorization.
-   Add at least one positive test and one relevant negative/failure
    test for: Use API tests for authentication, response contracts,
    pagination, filters, and authorization.
-   Document configuration, behavior, limitations, and manual setup for:
    Use API tests for authentication, response contracts, pagination,
    filters, and authorization.

### Directive 0291 --- Testing and quality

-   Implement this requirement in the actual repository: Use fictional
    test data and mock all external providers.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use fictional test data and mock all external providers.
-   Persist all required data and audit events consistently for: Use
    fictional test data and mock all external providers.
-   Add at least one positive test and one relevant negative/failure
    test for: Use fictional test data and mock all external providers.
-   Document configuration, behavior, limitations, and manual setup for:
    Use fictional test data and mock all external providers.

### Directive 0292 --- Testing and quality

-   Implement this requirement in the actual repository: Test that
    automated tests never send real email/SMS or call live municipal
    systems.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test that automated tests never send real email/SMS or call live
    municipal systems.
-   Persist all required data and audit events consistently for: Test
    that automated tests never send real email/SMS or call live
    municipal systems.
-   Add at least one positive test and one relevant negative/failure
    test for: Test that automated tests never send real email/SMS or
    call live municipal systems.
-   Document configuration, behavior, limitations, and manual setup for:
    Test that automated tests never send real email/SMS or call live
    municipal systems.

### Directive 0293 --- Testing and quality

-   Implement this requirement in the actual repository: Test complaint
    creation, tracking, assignment, status updates, resolution,
    feedback, and analytics end to end.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test complaint creation, tracking, assignment, status updates,
    resolution, feedback, and analytics end to end.
-   Persist all required data and audit events consistently for: Test
    complaint creation, tracking, assignment, status updates,
    resolution, feedback, and analytics end to end.
-   Add at least one positive test and one relevant negative/failure
    test for: Test complaint creation, tracking, assignment, status
    updates, resolution, feedback, and analytics end to end.
-   Document configuration, behavior, limitations, and manual setup for:
    Test complaint creation, tracking, assignment, status updates,
    resolution, feedback, and analytics end to end.

### Directive 0294 --- Testing and quality

-   Implement this requirement in the actual repository: Test invalid
    inputs, forbidden transitions, cross-user access, duplicate retries,
    provider failures, and worker retries.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test invalid inputs, forbidden transitions, cross-user access,
    duplicate retries, provider failures, and worker retries.
-   Persist all required data and audit events consistently for: Test
    invalid inputs, forbidden transitions, cross-user access, duplicate
    retries, provider failures, and worker retries.
-   Add at least one positive test and one relevant negative/failure
    test for: Test invalid inputs, forbidden transitions, cross-user
    access, duplicate retries, provider failures, and worker retries.
-   Document configuration, behavior, limitations, and manual setup for:
    Test invalid inputs, forbidden transitions, cross-user access,
    duplicate retries, provider failures, and worker retries.

### Directive 0295 --- Testing and quality

-   Implement this requirement in the actual repository: Run full tests
    and lint/type checks and report exact command outcomes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Run full tests and lint/type checks and report exact command
    outcomes.
-   Persist all required data and audit events consistently for: Run
    full tests and lint/type checks and report exact command outcomes.
-   Add at least one positive test and one relevant negative/failure
    test for: Run full tests and lint/type checks and report exact
    command outcomes.
-   Document configuration, behavior, limitations, and manual setup for:
    Run full tests and lint/type checks and report exact command
    outcomes.

### Directive 0296 --- Testing and quality

-   Implement this requirement in the actual repository: Do not skip or
    weaken tests just to achieve a passing result.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not skip or weaken tests just to achieve a passing result.
-   Persist all required data and audit events consistently for: Do not
    skip or weaken tests just to achieve a passing result.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not skip or weaken tests just to achieve a passing
    result.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not skip or weaken tests just to achieve a passing result.

### Directive 0297 --- Testing and quality

-   Implement this requirement in the actual repository: Inspect final
    diff and verify no credentials or unrelated changes were introduced.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Inspect final diff and verify no credentials or unrelated
    changes were introduced.
-   Persist all required data and audit events consistently for: Inspect
    final diff and verify no credentials or unrelated changes were
    introduced.
-   Add at least one positive test and one relevant negative/failure
    test for: Inspect final diff and verify no credentials or unrelated
    changes were introduced.
-   Document configuration, behavior, limitations, and manual setup for:
    Inspect final diff and verify no credentials or unrelated changes
    were introduced.

### Directive 0298 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed fictional
    Roads, Sanitation, Water Supply, Drainage, and Street Lighting
    departments.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed fictional Roads, Sanitation, Water Supply, Drainage, and
    Street Lighting departments.
-   Persist all required data and audit events consistently for: Seed
    fictional Roads, Sanitation, Water Supply, Drainage, and Street
    Lighting departments.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed fictional Roads, Sanitation, Water Supply, Drainage,
    and Street Lighting departments.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed fictional Roads, Sanitation, Water Supply, Drainage, and Street
    Lighting departments.

### Directive 0299 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed categories
    for potholes, garbage, water leakage, blocked drains, broken
    streetlights, and other civic issues.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed categories for potholes, garbage, water leakage, blocked
    drains, broken streetlights, and other civic issues.
-   Persist all required data and audit events consistently for: Seed
    categories for potholes, garbage, water leakage, blocked drains,
    broken streetlights, and other civic issues.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed categories for potholes, garbage, water leakage,
    blocked drains, broken streetlights, and other civic issues.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed categories for potholes, garbage, water leakage, blocked
    drains, broken streetlights, and other civic issues.

### Directive 0300 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed fictional
    wards or zones and clearly label them as demo data.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed fictional wards or zones and clearly label them as demo
    data.
-   Persist all required data and audit events consistently for: Seed
    fictional wards or zones and clearly label them as demo data.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed fictional wards or zones and clearly label them as
    demo data.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed fictional wards or zones and clearly label them as demo data.

### Directive 0301 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed resident,
    officer, supervisor, and administrator accounts with
    development-only instructions.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed resident, officer, supervisor, and administrator accounts
    with development-only instructions.
-   Persist all required data and audit events consistently for: Seed
    resident, officer, supervisor, and administrator accounts with
    development-only instructions.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed resident, officer, supervisor, and administrator
    accounts with development-only instructions.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed resident, officer, supervisor, and administrator accounts with
    development-only instructions.

### Directive 0302 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed complaints
    across statuses, categories, departments, and priorities.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed complaints across statuses, categories, departments, and
    priorities.
-   Persist all required data and audit events consistently for: Seed
    complaints across statuses, categories, departments, and priorities.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed complaints across statuses, categories, departments,
    and priorities.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed complaints across statuses, categories, departments, and
    priorities.

### Directive 0303 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed an overdue
    complaint, an unmapped complaint, and a pair of potential
    duplicates.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed an overdue complaint, an unmapped complaint, and a pair of
    potential duplicates.
-   Persist all required data and audit events consistently for: Seed an
    overdue complaint, an unmapped complaint, and a pair of potential
    duplicates.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed an overdue complaint, an unmapped complaint, and a
    pair of potential duplicates.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed an overdue complaint, an unmapped complaint, and a pair of
    potential duplicates.

### Directive 0304 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Seed a resolved
    complaint with fictional resolution notes and evidence metadata.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Seed a resolved complaint with fictional resolution notes and
    evidence metadata.
-   Persist all required data and audit events consistently for: Seed a
    resolved complaint with fictional resolution notes and evidence
    metadata.
-   Add at least one positive test and one relevant negative/failure
    test for: Seed a resolved complaint with fictional resolution notes
    and evidence metadata.
-   Document configuration, behavior, limitations, and manual setup for:
    Seed a resolved complaint with fictional resolution notes and
    evidence metadata.

### Directive 0305 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Make seed
    scripts repeatable and safe to run.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Make seed scripts repeatable and safe to run.
-   Persist all required data and audit events consistently for: Make
    seed scripts repeatable and safe to run.
-   Add at least one positive test and one relevant negative/failure
    test for: Make seed scripts repeatable and safe to run.
-   Document configuration, behavior, limitations, and manual setup for:
    Make seed scripts repeatable and safe to run.

### Directive 0306 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Prevent demo
    credentials and reset scripts from being used in production.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Prevent demo credentials and reset scripts from being used in
    production.
-   Persist all required data and audit events consistently for: Prevent
    demo credentials and reset scripts from being used in production.
-   Add at least one positive test and one relevant negative/failure
    test for: Prevent demo credentials and reset scripts from being used
    in production.
-   Document configuration, behavior, limitations, and manual setup for:
    Prevent demo credentials and reset scripts from being used in
    production.

### Directive 0307 --- Seed data and demo scenarios

-   Implement this requirement in the actual repository: Document all
    sample data and avoid real personal information.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document all sample data and avoid real personal information.
-   Persist all required data and audit events consistently for:
    Document all sample data and avoid real personal information.
-   Add at least one positive test and one relevant negative/failure
    test for: Document all sample data and avoid real personal
    information.
-   Document configuration, behavior, limitations, and manual setup for:
    Document all sample data and avoid real personal information.

### Directive 0308 --- External municipal integration

-   Implement this requirement in the actual repository: Define a
    provider interface for an external municipal case-management API
    only if authorized integration is in scope.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define a provider interface for an external municipal
    case-management API only if authorized integration is in scope.
-   Persist all required data and audit events consistently for: Define
    a provider interface for an external municipal case-management API
    only if authorized integration is in scope.
-   Add at least one positive test and one relevant negative/failure
    test for: Define a provider interface for an external municipal
    case-management API only if authorized integration is in scope.
-   Document configuration, behavior, limitations, and manual setup for:
    Define a provider interface for an external municipal
    case-management API only if authorized integration is in scope.

### Directive 0309 --- External municipal integration

-   Implement this requirement in the actual repository: Use documented
    and authorized APIs; do not scrape portals or bypass access
    controls.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use documented and authorized APIs; do not scrape portals or
    bypass access controls.
-   Persist all required data and audit events consistently for: Use
    documented and authorized APIs; do not scrape portals or bypass
    access controls.
-   Add at least one positive test and one relevant negative/failure
    test for: Use documented and authorized APIs; do not scrape portals
    or bypass access controls.
-   Document configuration, behavior, limitations, and manual setup for:
    Use documented and authorized APIs; do not scrape portals or bypass
    access controls.

### Directive 0310 --- External municipal integration

-   Implement this requirement in the actual repository: Store external
    case IDs only after a real provider confirms them.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Store external case IDs only after a real provider confirms
    them.
-   Persist all required data and audit events consistently for: Store
    external case IDs only after a real provider confirms them.
-   Add at least one positive test and one relevant negative/failure
    test for: Store external case IDs only after a real provider
    confirms them.
-   Document configuration, behavior, limitations, and manual setup for:
    Store external case IDs only after a real provider confirms them.

### Directive 0311 --- External municipal integration

-   Implement this requirement in the actual repository: Map local and
    external statuses explicitly and record synchronization state.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Map local and external statuses explicitly and record
    synchronization state.
-   Persist all required data and audit events consistently for: Map
    local and external statuses explicitly and record synchronization
    state.
-   Add at least one positive test and one relevant negative/failure
    test for: Map local and external statuses explicitly and record
    synchronization state.
-   Document configuration, behavior, limitations, and manual setup for:
    Map local and external statuses explicitly and record
    synchronization state.

### Directive 0312 --- External municipal integration

-   Implement this requirement in the actual repository: Handle timeout,
    rejection, retry, partial failure, and reconciliation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle timeout, rejection, retry, partial failure, and
    reconciliation.
-   Persist all required data and audit events consistently for: Handle
    timeout, rejection, retry, partial failure, and reconciliation.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle timeout, rejection, retry, partial failure, and
    reconciliation.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle timeout, rejection, retry, partial failure, and
    reconciliation.

### Directive 0313 --- External municipal integration

-   Implement this requirement in the actual repository: Distinguish
    local receipt from external acknowledgement in all resident-facing
    messages.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Distinguish local receipt from external acknowledgement in all
    resident-facing messages.
-   Persist all required data and audit events consistently for:
    Distinguish local receipt from external acknowledgement in all
    resident-facing messages.
-   Add at least one positive test and one relevant negative/failure
    test for: Distinguish local receipt from external acknowledgement in
    all resident-facing messages.
-   Document configuration, behavior, limitations, and manual setup for:
    Distinguish local receipt from external acknowledgement in all
    resident-facing messages.

### Directive 0314 --- External municipal integration

-   Implement this requirement in the actual repository: Provide a mock
    adapter for demo mode and mark all mock results as simulated.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a mock adapter for demo mode and mark all mock results
    as simulated.
-   Persist all required data and audit events consistently for: Provide
    a mock adapter for demo mode and mark all mock results as simulated.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a mock adapter for demo mode and mark all mock
    results as simulated.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a mock adapter for demo mode and mark all mock results as
    simulated.

### Directive 0315 --- External municipal integration

-   Implement this requirement in the actual repository: Protect
    credentials and do not log provider secrets.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Protect credentials and do not log provider secrets.
-   Persist all required data and audit events consistently for: Protect
    credentials and do not log provider secrets.
-   Add at least one positive test and one relevant negative/failure
    test for: Protect credentials and do not log provider secrets.
-   Document configuration, behavior, limitations, and manual setup for:
    Protect credentials and do not log provider secrets.

### Directive 0316 --- External municipal integration

-   Implement this requirement in the actual repository: Do not claim a
    real municipality received a report unless confirmed.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not claim a real municipality received a report unless
    confirmed.
-   Persist all required data and audit events consistently for: Do not
    claim a real municipality received a report unless confirmed.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not claim a real municipality received a report unless
    confirmed.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not claim a real municipality received a report unless confirmed.

### Directive 0317 --- External municipal integration

-   Implement this requirement in the actual repository: Test mock
    success, provider rejection, timeout, retry, and reconciliation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test mock success, provider rejection, timeout, retry, and
    reconciliation.
-   Persist all required data and audit events consistently for: Test
    mock success, provider rejection, timeout, retry, and
    reconciliation.
-   Add at least one positive test and one relevant negative/failure
    test for: Test mock success, provider rejection, timeout, retry, and
    reconciliation.
-   Document configuration, behavior, limitations, and manual setup for:
    Test mock success, provider rejection, timeout, retry, and
    reconciliation.

### Directive 0318 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Preserve
    original text and store translations separately.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Preserve original text and store translations separately.
-   Persist all required data and audit events consistently for:
    Preserve original text and store translations separately.
-   Add at least one positive test and one relevant negative/failure
    test for: Preserve original text and store translations separately.
-   Document configuration, behavior, limitations, and manual setup for:
    Preserve original text and store translations separately.

### Directive 0319 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Support English
    and Telugu when required by the target users and configured
    resources.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Support English and Telugu when required by the target users and
    configured resources.
-   Persist all required data and audit events consistently for: Support
    English and Telugu when required by the target users and configured
    resources.
-   Add at least one positive test and one relevant negative/failure
    test for: Support English and Telugu when required by the target
    users and configured resources.
-   Document configuration, behavior, limitations, and manual setup for:
    Support English and Telugu when required by the target users and
    configured resources.

### Directive 0320 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Use stable
    language codes and Unicode-safe database/API behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use stable language codes and Unicode-safe database/API
    behavior.
-   Persist all required data and audit events consistently for: Use
    stable language codes and Unicode-safe database/API behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Use stable language codes and Unicode-safe database/API
    behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Use stable language codes and Unicode-safe database/API behavior.

### Directive 0321 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Allow
    correction of speech-to-text and translation output.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Allow correction of speech-to-text and translation output.
-   Persist all required data and audit events consistently for: Allow
    correction of speech-to-text and translation output.
-   Add at least one positive test and one relevant negative/failure
    test for: Allow correction of speech-to-text and translation output.
-   Document configuration, behavior, limitations, and manual setup for:
    Allow correction of speech-to-text and translation output.

### Directive 0322 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Validate audio
    types and size if voice input is implemented.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Validate audio types and size if voice input is implemented.
-   Persist all required data and audit events consistently for:
    Validate audio types and size if voice input is implemented.
-   Add at least one positive test and one relevant negative/failure
    test for: Validate audio types and size if voice input is
    implemented.
-   Document configuration, behavior, limitations, and manual setup for:
    Validate audio types and size if voice input is implemented.

### Directive 0323 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Delete
    temporary audio according to documented retention rules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Delete temporary audio according to documented retention rules.
-   Persist all required data and audit events consistently for: Delete
    temporary audio according to documented retention rules.
-   Add at least one positive test and one relevant negative/failure
    test for: Delete temporary audio according to documented retention
    rules.
-   Document configuration, behavior, limitations, and manual setup for:
    Delete temporary audio according to documented retention rules.

### Directive 0324 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Provide a
    text-entry fallback when speech recognition fails.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Provide a text-entry fallback when speech recognition fails.
-   Persist all required data and audit events consistently for: Provide
    a text-entry fallback when speech recognition fails.
-   Add at least one positive test and one relevant negative/failure
    test for: Provide a text-entry fallback when speech recognition
    fails.
-   Document configuration, behavior, limitations, and manual setup for:
    Provide a text-entry fallback when speech recognition fails.

### Directive 0325 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Do not require
    a photo or exact GPS location when inappropriate or unavailable.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not require a photo or exact GPS location when inappropriate
    or unavailable.
-   Persist all required data and audit events consistently for: Do not
    require a photo or exact GPS location when inappropriate or
    unavailable.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not require a photo or exact GPS location when
    inappropriate or unavailable.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not require a photo or exact GPS location when inappropriate or
    unavailable.

### Directive 0326 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Keep error
    codes stable so clients can localize messages.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Keep error codes stable so clients can localize messages.
-   Persist all required data and audit events consistently for: Keep
    error codes stable so clients can localize messages.
-   Add at least one positive test and one relevant negative/failure
    test for: Keep error codes stable so clients can localize messages.
-   Document configuration, behavior, limitations, and manual setup for:
    Keep error codes stable so clients can localize messages.

### Directive 0327 --- Multilingual, voice, and accessibility support

-   Implement this requirement in the actual repository: Test non-Latin
    text persistence, search, notifications, and serialization.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test non-Latin text persistence, search, notifications, and
    serialization.
-   Persist all required data and audit events consistently for: Test
    non-Latin text persistence, search, notifications, and
    serialization.
-   Add at least one positive test and one relevant negative/failure
    test for: Test non-Latin text persistence, search, notifications,
    and serialization.
-   Document configuration, behavior, limitations, and manual setup for:
    Test non-Latin text persistence, search, notifications, and
    serialization.

### Directive 0328 --- Offline support (optional)

-   Implement this requirement in the actual repository: Treat offline
    submission as optional and defer it until the online lifecycle is
    correct.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Treat offline submission as optional and defer it until the
    online lifecycle is correct.
-   Persist all required data and audit events consistently for: Treat
    offline submission as optional and defer it until the online
    lifecycle is correct.
-   Add at least one positive test and one relevant negative/failure
    test for: Treat offline submission as optional and defer it until
    the online lifecycle is correct.
-   Document configuration, behavior, limitations, and manual setup for:
    Treat offline submission as optional and defer it until the online
    lifecycle is correct.

### Directive 0329 --- Offline support (optional)

-   Implement this requirement in the actual repository: Clearly
    distinguish local draft, queued submission, and server-confirmed
    complaint.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Clearly distinguish local draft, queued submission, and
    server-confirmed complaint.
-   Persist all required data and audit events consistently for: Clearly
    distinguish local draft, queued submission, and server-confirmed
    complaint.
-   Add at least one positive test and one relevant negative/failure
    test for: Clearly distinguish local draft, queued submission, and
    server-confirmed complaint.
-   Document configuration, behavior, limitations, and manual setup for:
    Clearly distinguish local draft, queued submission, and
    server-confirmed complaint.

### Directive 0330 --- Offline support (optional)

-   Implement this requirement in the actual repository: Do not issue a
    real tracking reference before server persistence.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not issue a real tracking reference before server
    persistence.
-   Persist all required data and audit events consistently for: Do not
    issue a real tracking reference before server persistence.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not issue a real tracking reference before server
    persistence.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not issue a real tracking reference before server persistence.

### Directive 0331 --- Offline support (optional)

-   Implement this requirement in the actual repository: Use idempotency
    when queued reports are retried.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Use idempotency when queued reports are retried.
-   Persist all required data and audit events consistently for: Use
    idempotency when queued reports are retried.
-   Add at least one positive test and one relevant negative/failure
    test for: Use idempotency when queued reports are retried.
-   Document configuration, behavior, limitations, and manual setup for:
    Use idempotency when queued reports are retried.

### Directive 0332 --- Offline support (optional)

-   Implement this requirement in the actual repository: Revalidate
    category, jurisdiction, permissions, and media at synchronization
    time.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Revalidate category, jurisdiction, permissions, and media at
    synchronization time.
-   Persist all required data and audit events consistently for:
    Revalidate category, jurisdiction, permissions, and media at
    synchronization time.
-   Add at least one positive test and one relevant negative/failure
    test for: Revalidate category, jurisdiction, permissions, and media
    at synchronization time.
-   Document configuration, behavior, limitations, and manual setup for:
    Revalidate category, jurisdiction, permissions, and media at
    synchronization time.

### Directive 0333 --- Offline support (optional)

-   Implement this requirement in the actual repository: Handle expired
    authentication, rejected queued reports, and partial upload
    failures.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Handle expired authentication, rejected queued reports, and
    partial upload failures.
-   Persist all required data and audit events consistently for: Handle
    expired authentication, rejected queued reports, and partial upload
    failures.
-   Add at least one positive test and one relevant negative/failure
    test for: Handle expired authentication, rejected queued reports,
    and partial upload failures.
-   Document configuration, behavior, limitations, and manual setup for:
    Handle expired authentication, rejected queued reports, and partial
    upload failures.

### Directive 0334 --- Offline support (optional)

-   Implement this requirement in the actual repository: Define local
    draft retention and cancellation behavior.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Define local draft retention and cancellation behavior.
-   Persist all required data and audit events consistently for: Define
    local draft retention and cancellation behavior.
-   Add at least one positive test and one relevant negative/failure
    test for: Define local draft retention and cancellation behavior.
-   Document configuration, behavior, limitations, and manual setup for:
    Define local draft retention and cancellation behavior.

### Directive 0335 --- Offline support (optional)

-   Implement this requirement in the actual repository: Never let
    offline mode bypass server validation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never let offline mode bypass server validation.
-   Persist all required data and audit events consistently for: Never
    let offline mode bypass server validation.
-   Add at least one positive test and one relevant negative/failure
    test for: Never let offline mode bypass server validation.
-   Document configuration, behavior, limitations, and manual setup for:
    Never let offline mode bypass server validation.

### Directive 0336 --- Offline support (optional)

-   Implement this requirement in the actual repository: Test repeated
    synchronization and stale configuration.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Test repeated synchronization and stale configuration.
-   Persist all required data and audit events consistently for: Test
    repeated synchronization and stale configuration.
-   Add at least one positive test and one relevant negative/failure
    test for: Test repeated synchronization and stale configuration.
-   Document configuration, behavior, limitations, and manual setup for:
    Test repeated synchronization and stale configuration.

### Directive 0337 --- Offline support (optional)

-   Implement this requirement in the actual repository: Do not claim
    offline support unless it has been implemented and tested.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Do not claim offline support unless it has been implemented and
    tested.
-   Persist all required data and audit events consistently for: Do not
    claim offline support unless it has been implemented and tested.
-   Add at least one positive test and one relevant negative/failure
    test for: Do not claim offline support unless it has been
    implemented and tested.
-   Document configuration, behavior, limitations, and manual setup for:
    Do not claim offline support unless it has been implemented and
    tested.

### Directive 0338 --- Documentation and final report

-   Implement this requirement in the actual repository: Update README
    with project purpose, architecture, setup, migrations, seeding,
    startup, tests, and API docs.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Update README with project purpose, architecture, setup,
    migrations, seeding, startup, tests, and API docs.
-   Persist all required data and audit events consistently for: Update
    README with project purpose, architecture, setup, migrations,
    seeding, startup, tests, and API docs.
-   Add at least one positive test and one relevant negative/failure
    test for: Update README with project purpose, architecture, setup,
    migrations, seeding, startup, tests, and API docs.
-   Document configuration, behavior, limitations, and manual setup for:
    Update README with project purpose, architecture, setup, migrations,
    seeding, startup, tests, and API docs.

### Directive 0339 --- Documentation and final report

-   Implement this requirement in the actual repository: Document
    entities and relationships, permissions, state machine, routing
    precedence, fallback, and SLA calculations.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document entities and relationships, permissions, state machine,
    routing precedence, fallback, and SLA calculations.
-   Persist all required data and audit events consistently for:
    Document entities and relationships, permissions, state machine,
    routing precedence, fallback, and SLA calculations.
-   Add at least one positive test and one relevant negative/failure
    test for: Document entities and relationships, permissions, state
    machine, routing precedence, fallback, and SLA calculations.
-   Document configuration, behavior, limitations, and manual setup for:
    Document entities and relationships, permissions, state machine,
    routing precedence, fallback, and SLA calculations.

### Directive 0340 --- Documentation and final report

-   Implement this requirement in the actual repository: Document
    environment variables, provider setup, and mock mode.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document environment variables, provider setup, and mock mode.
-   Persist all required data and audit events consistently for:
    Document environment variables, provider setup, and mock mode.
-   Add at least one positive test and one relevant negative/failure
    test for: Document environment variables, provider setup, and mock
    mode.
-   Document configuration, behavior, limitations, and manual setup for:
    Document environment variables, provider setup, and mock mode.

### Directive 0341 --- Documentation and final report

-   Implement this requirement in the actual repository: Document how to
    add a category, department, routing rule, notification provider, or
    AI provider.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document how to add a category, department, routing rule,
    notification provider, or AI provider.
-   Persist all required data and audit events consistently for:
    Document how to add a category, department, routing rule,
    notification provider, or AI provider.
-   Add at least one positive test and one relevant negative/failure
    test for: Document how to add a category, department, routing rule,
    notification provider, or AI provider.
-   Document configuration, behavior, limitations, and manual setup for:
    Document how to add a category, department, routing rule,
    notification provider, or AI provider.

### Directive 0342 --- Documentation and final report

-   Implement this requirement in the actual repository: Document
    retention, privacy assumptions, backup/recovery, and known
    limitations.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Document retention, privacy assumptions, backup/recovery, and
    known limitations.
-   Persist all required data and audit events consistently for:
    Document retention, privacy assumptions, backup/recovery, and known
    limitations.
-   Add at least one positive test and one relevant negative/failure
    test for: Document retention, privacy assumptions, backup/recovery,
    and known limitations.
-   Document configuration, behavior, limitations, and manual setup for:
    Document retention, privacy assumptions, backup/recovery, and known
    limitations.

### Directive 0343 --- Documentation and final report

-   Implement this requirement in the actual repository: List files
    changed, routes added, migrations, tests actually run, and their
    exact outcomes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List files changed, routes added, migrations, tests actually
    run, and their exact outcomes.
-   Persist all required data and audit events consistently for: List
    files changed, routes added, migrations, tests actually run, and
    their exact outcomes.
-   Add at least one positive test and one relevant negative/failure
    test for: List files changed, routes added, migrations, tests
    actually run, and their exact outcomes.
-   Document configuration, behavior, limitations, and manual setup for:
    List files changed, routes added, migrations, tests actually run,
    and their exact outcomes.

### Directive 0344 --- Documentation and final report

-   Implement this requirement in the actual repository: Separate fully
    implemented, partially implemented, mocked, and deferred
    functionality.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Separate fully implemented, partially implemented, mocked, and
    deferred functionality.
-   Persist all required data and audit events consistently for:
    Separate fully implemented, partially implemented, mocked, and
    deferred functionality.
-   Add at least one positive test and one relevant negative/failure
    test for: Separate fully implemented, partially implemented, mocked,
    and deferred functionality.
-   Document configuration, behavior, limitations, and manual setup for:
    Separate fully implemented, partially implemented, mocked, and
    deferred functionality.

### Directive 0345 --- Documentation and final report

-   Implement this requirement in the actual repository: List manual
    configuration still required and the next three highest-value tasks.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List manual configuration still required and the next three
    highest-value tasks.
-   Persist all required data and audit events consistently for: List
    manual configuration still required and the next three highest-value
    tasks.
-   Add at least one positive test and one relevant negative/failure
    test for: List manual configuration still required and the next
    three highest-value tasks.
-   Document configuration, behavior, limitations, and manual setup for:
    List manual configuration still required and the next three
    highest-value tasks.

### Directive 0346 --- Documentation and final report

-   Implement this requirement in the actual repository: Never claim
    tests, integrations, deployment, or external delivery succeeded
    unless verified.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Never claim tests, integrations, deployment, or external
    delivery succeeded unless verified.
-   Persist all required data and audit events consistently for: Never
    claim tests, integrations, deployment, or external delivery
    succeeded unless verified.
-   Add at least one positive test and one relevant negative/failure
    test for: Never claim tests, integrations, deployment, or external
    delivery succeeded unless verified.
-   Document configuration, behavior, limitations, and manual setup for:
    Never claim tests, integrations, deployment, or external delivery
    succeeded unless verified.

### Directive 0347 --- Documentation and final report

-   Implement this requirement in the actual repository: Finish only
    when the core complaint lifecycle is functional and the remaining
    limitations are explicit.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Finish only when the core complaint lifecycle is functional and
    the remaining limitations are explicit.
-   Persist all required data and audit events consistently for: Finish
    only when the core complaint lifecycle is functional and the
    remaining limitations are explicit.
-   Add at least one positive test and one relevant negative/failure
    test for: Finish only when the core complaint lifecycle is
    functional and the remaining limitations are explicit.
-   Document configuration, behavior, limitations, and manual setup for:
    Finish only when the core complaint lifecycle is functional and the
    remaining limitations are explicit.

### Directive 0348 --- Data model `users`

-   Implement this requirement in the actual repository: stable primary
    key
-   Validate the inputs, permissions, state, and failure modes relevant
    to: stable primary key
-   Persist all required data and audit events consistently for: stable
    primary key
-   Add at least one positive test and one relevant negative/failure
    test for: stable primary key
-   Document configuration, behavior, limitations, and manual setup for:
    stable primary key

### Directive 0349 --- Data model `users`

-   Implement this requirement in the actual repository: normalized
    unique email when email login is enabled
-   Validate the inputs, permissions, state, and failure modes relevant
    to: normalized unique email when email login is enabled
-   Persist all required data and audit events consistently for:
    normalized unique email when email login is enabled
-   Add at least one positive test and one relevant negative/failure
    test for: normalized unique email when email login is enabled
-   Document configuration, behavior, limitations, and manual setup for:
    normalized unique email when email login is enabled

### Directive 0350 --- Data model `users`

-   Implement this requirement in the actual repository: optional
    normalized phone
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional normalized phone
-   Persist all required data and audit events consistently for:
    optional normalized phone
-   Add at least one positive test and one relevant negative/failure
    test for: optional normalized phone
-   Document configuration, behavior, limitations, and manual setup for:
    optional normalized phone

### Directive 0351 --- Data model `users`

-   Implement this requirement in the actual repository: display name
-   Validate the inputs, permissions, state, and failure modes relevant
    to: display name
-   Persist all required data and audit events consistently for: display
    name
-   Add at least one positive test and one relevant negative/failure
    test for: display name
-   Document configuration, behavior, limitations, and manual setup for:
    display name

### Directive 0352 --- Data model `users`

-   Implement this requirement in the actual repository: password hash
    only if local passwords are used
-   Validate the inputs, permissions, state, and failure modes relevant
    to: password hash only if local passwords are used
-   Persist all required data and audit events consistently for:
    password hash only if local passwords are used
-   Add at least one positive test and one relevant negative/failure
    test for: password hash only if local passwords are used
-   Document configuration, behavior, limitations, and manual setup for:
    password hash only if local passwords are used

### Directive 0353 --- Data model `users`

-   Implement this requirement in the actual repository:
    active/deactivated state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active/deactivated state
-   Persist all required data and audit events consistently for:
    active/deactivated state
-   Add at least one positive test and one relevant negative/failure
    test for: active/deactivated state
-   Document configuration, behavior, limitations, and manual setup for:
    active/deactivated state

### Directive 0354 --- Data model `users`

-   Implement this requirement in the actual repository: preferred
    language
-   Validate the inputs, permissions, state, and failure modes relevant
    to: preferred language
-   Persist all required data and audit events consistently for:
    preferred language
-   Add at least one positive test and one relevant negative/failure
    test for: preferred language
-   Document configuration, behavior, limitations, and manual setup for:
    preferred language

### Directive 0355 --- Data model `users`

-   Implement this requirement in the actual repository: created and
    updated timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: created and updated timestamps
-   Persist all required data and audit events consistently for: created
    and updated timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: created and updated timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    created and updated timestamps

### Directive 0356 --- Data model `users`

-   Implement this requirement in the actual repository: never expose
    credentials or hashes
-   Validate the inputs, permissions, state, and failure modes relevant
    to: never expose credentials or hashes
-   Persist all required data and audit events consistently for: never
    expose credentials or hashes
-   Add at least one positive test and one relevant negative/failure
    test for: never expose credentials or hashes
-   Document configuration, behavior, limitations, and manual setup for:
    never expose credentials or hashes

### Directive 0357 --- Data model `roles and user_roles`

-   Implement this requirement in the actual repository: controlled role
    names
-   Validate the inputs, permissions, state, and failure modes relevant
    to: controlled role names
-   Persist all required data and audit events consistently for:
    controlled role names
-   Add at least one positive test and one relevant negative/failure
    test for: controlled role names
-   Document configuration, behavior, limitations, and manual setup for:
    controlled role names

### Directive 0358 --- Data model `roles and user_roles`

-   Implement this requirement in the actual repository: many-to-many
    user-role mapping if required
-   Validate the inputs, permissions, state, and failure modes relevant
    to: many-to-many user-role mapping if required
-   Persist all required data and audit events consistently for:
    many-to-many user-role mapping if required
-   Add at least one positive test and one relevant negative/failure
    test for: many-to-many user-role mapping if required
-   Document configuration, behavior, limitations, and manual setup for:
    many-to-many user-role mapping if required

### Directive 0359 --- Data model `roles and user_roles`

-   Implement this requirement in the actual repository: optional
    department/ward scope
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional department/ward scope
-   Persist all required data and audit events consistently for:
    optional department/ward scope
-   Add at least one positive test and one relevant negative/failure
    test for: optional department/ward scope
-   Document configuration, behavior, limitations, and manual setup for:
    optional department/ward scope

### Directive 0360 --- Data model `roles and user_roles`

-   Implement this requirement in the actual repository: server-enforced
    permission matrix
-   Validate the inputs, permissions, state, and failure modes relevant
    to: server-enforced permission matrix
-   Persist all required data and audit events consistently for:
    server-enforced permission matrix
-   Add at least one positive test and one relevant negative/failure
    test for: server-enforced permission matrix
-   Document configuration, behavior, limitations, and manual setup for:
    server-enforced permission matrix

### Directive 0361 --- Data model `roles and user_roles`

-   Implement this requirement in the actual repository: auditable
    privilege changes
-   Validate the inputs, permissions, state, and failure modes relevant
    to: auditable privilege changes
-   Persist all required data and audit events consistently for:
    auditable privilege changes
-   Add at least one positive test and one relevant negative/failure
    test for: auditable privilege changes
-   Document configuration, behavior, limitations, and manual setup for:
    auditable privilege changes

### Directive 0362 --- Data model `departments`

-   Implement this requirement in the actual repository: stable ID and
    unique code
-   Validate the inputs, permissions, state, and failure modes relevant
    to: stable ID and unique code
-   Persist all required data and audit events consistently for: stable
    ID and unique code
-   Add at least one positive test and one relevant negative/failure
    test for: stable ID and unique code
-   Document configuration, behavior, limitations, and manual setup for:
    stable ID and unique code

### Directive 0363 --- Data model `departments`

-   Implement this requirement in the actual repository: name and
    description
-   Validate the inputs, permissions, state, and failure modes relevant
    to: name and description
-   Persist all required data and audit events consistently for: name
    and description
-   Add at least one positive test and one relevant negative/failure
    test for: name and description
-   Document configuration, behavior, limitations, and manual setup for:
    name and description

### Directive 0364 --- Data model `departments`

-   Implement this requirement in the actual repository: active state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active state
-   Persist all required data and audit events consistently for: active
    state
-   Add at least one positive test and one relevant negative/failure
    test for: active state
-   Document configuration, behavior, limitations, and manual setup for:
    active state

### Directive 0365 --- Data model `departments`

-   Implement this requirement in the actual repository: public contact
    fields
-   Validate the inputs, permissions, state, and failure modes relevant
    to: public contact fields
-   Persist all required data and audit events consistently for: public
    contact fields
-   Add at least one positive test and one relevant negative/failure
    test for: public contact fields
-   Document configuration, behavior, limitations, and manual setup for:
    public contact fields

### Directive 0366 --- Data model `departments`

-   Implement this requirement in the actual repository: coverage rules
-   Validate the inputs, permissions, state, and failure modes relevant
    to: coverage rules
-   Persist all required data and audit events consistently for:
    coverage rules
-   Add at least one positive test and one relevant negative/failure
    test for: coverage rules
-   Document configuration, behavior, limitations, and manual setup for:
    coverage rules

### Directive 0367 --- Data model `departments`

-   Implement this requirement in the actual repository: optional parent
    department
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional parent department
-   Persist all required data and audit events consistently for:
    optional parent department
-   Add at least one positive test and one relevant negative/failure
    test for: optional parent department
-   Document configuration, behavior, limitations, and manual setup for:
    optional parent department

### Directive 0368 --- Data model `departments`

-   Implement this requirement in the actual repository: timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamps
-   Persist all required data and audit events consistently for:
    timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    timestamps

### Directive 0369 --- Data model `departments`

-   Implement this requirement in the actual repository: historical
    references preserved after deactivation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: historical references preserved after deactivation
-   Persist all required data and audit events consistently for:
    historical references preserved after deactivation
-   Add at least one positive test and one relevant negative/failure
    test for: historical references preserved after deactivation
-   Document configuration, behavior, limitations, and manual setup for:
    historical references preserved after deactivation

### Directive 0370 --- Data model `officers`

-   Implement this requirement in the actual repository: linked staff
    user
-   Validate the inputs, permissions, state, and failure modes relevant
    to: linked staff user
-   Persist all required data and audit events consistently for: linked
    staff user
-   Add at least one positive test and one relevant negative/failure
    test for: linked staff user
-   Document configuration, behavior, limitations, and manual setup for:
    linked staff user

### Directive 0371 --- Data model `officers`

-   Implement this requirement in the actual repository: department/team
    membership
-   Validate the inputs, permissions, state, and failure modes relevant
    to: department/team membership
-   Persist all required data and audit events consistently for:
    department/team membership
-   Add at least one positive test and one relevant negative/failure
    test for: department/team membership
-   Document configuration, behavior, limitations, and manual setup for:
    department/team membership

### Directive 0372 --- Data model `officers`

-   Implement this requirement in the actual repository: active state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active state
-   Persist all required data and audit events consistently for: active
    state
-   Add at least one positive test and one relevant negative/failure
    test for: active state
-   Document configuration, behavior, limitations, and manual setup for:
    active state

### Directive 0373 --- Data model `officers`

-   Implement this requirement in the actual repository: supervisor
    relation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: supervisor relation
-   Persist all required data and audit events consistently for:
    supervisor relation
-   Add at least one positive test and one relevant negative/failure
    test for: supervisor relation
-   Document configuration, behavior, limitations, and manual setup for:
    supervisor relation

### Directive 0374 --- Data model `officers`

-   Implement this requirement in the actual repository: assignment
    eligibility
-   Validate the inputs, permissions, state, and failure modes relevant
    to: assignment eligibility
-   Persist all required data and audit events consistently for:
    assignment eligibility
-   Add at least one positive test and one relevant negative/failure
    test for: assignment eligibility
-   Document configuration, behavior, limitations, and manual setup for:
    assignment eligibility

### Directive 0375 --- Data model `officers`

-   Implement this requirement in the actual repository: no unnecessary
    sensitive employment data
-   Validate the inputs, permissions, state, and failure modes relevant
    to: no unnecessary sensitive employment data
-   Persist all required data and audit events consistently for: no
    unnecessary sensitive employment data
-   Add at least one positive test and one relevant negative/failure
    test for: no unnecessary sensitive employment data
-   Document configuration, behavior, limitations, and manual setup for:
    no unnecessary sensitive employment data

### Directive 0376 --- Data model `wards`

-   Implement this requirement in the actual repository: stable ID and
    name
-   Validate the inputs, permissions, state, and failure modes relevant
    to: stable ID and name
-   Persist all required data and audit events consistently for: stable
    ID and name
-   Add at least one positive test and one relevant negative/failure
    test for: stable ID and name
-   Document configuration, behavior, limitations, and manual setup for:
    stable ID and name

### Directive 0377 --- Data model `wards`

-   Implement this requirement in the actual repository: optional code
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional code
-   Persist all required data and audit events consistently for:
    optional code
-   Add at least one positive test and one relevant negative/failure
    test for: optional code
-   Document configuration, behavior, limitations, and manual setup for:
    optional code

### Directive 0378 --- Data model `wards`

-   Implement this requirement in the actual repository: verified
    boundary geometry if available
-   Validate the inputs, permissions, state, and failure modes relevant
    to: verified boundary geometry if available
-   Persist all required data and audit events consistently for:
    verified boundary geometry if available
-   Add at least one positive test and one relevant negative/failure
    test for: verified boundary geometry if available
-   Document configuration, behavior, limitations, and manual setup for:
    verified boundary geometry if available

### Directive 0379 --- Data model `wards`

-   Implement this requirement in the actual repository: active state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active state
-   Persist all required data and audit events consistently for: active
    state
-   Add at least one positive test and one relevant negative/failure
    test for: active state
-   Document configuration, behavior, limitations, and manual setup for:
    active state

### Directive 0380 --- Data model `wards`

-   Implement this requirement in the actual repository: data provenance
-   Validate the inputs, permissions, state, and failure modes relevant
    to: data provenance
-   Persist all required data and audit events consistently for: data
    provenance
-   Add at least one positive test and one relevant negative/failure
    test for: data provenance
-   Document configuration, behavior, limitations, and manual setup for:
    data provenance

### Directive 0381 --- Data model `wards`

-   Implement this requirement in the actual repository: timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamps
-   Persist all required data and audit events consistently for:
    timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    timestamps

### Directive 0382 --- Data model `wards`

-   Implement this requirement in the actual repository: no fabricated
    official boundaries
-   Validate the inputs, permissions, state, and failure modes relevant
    to: no fabricated official boundaries
-   Persist all required data and audit events consistently for: no
    fabricated official boundaries
-   Add at least one positive test and one relevant negative/failure
    test for: no fabricated official boundaries
-   Document configuration, behavior, limitations, and manual setup for:
    no fabricated official boundaries

### Directive 0383 --- Data model `services`

-   Implement this requirement in the actual repository: name and
    description
-   Validate the inputs, permissions, state, and failure modes relevant
    to: name and description
-   Persist all required data and audit events consistently for: name
    and description
-   Add at least one positive test and one relevant negative/failure
    test for: name and description
-   Document configuration, behavior, limitations, and manual setup for:
    name and description

### Directive 0384 --- Data model `services`

-   Implement this requirement in the actual repository: department
    relationships
-   Validate the inputs, permissions, state, and failure modes relevant
    to: department relationships
-   Persist all required data and audit events consistently for:
    department relationships
-   Add at least one positive test and one relevant negative/failure
    test for: department relationships
-   Document configuration, behavior, limitations, and manual setup for:
    department relationships

### Directive 0385 --- Data model `services`

-   Implement this requirement in the actual repository: supported
    categories
-   Validate the inputs, permissions, state, and failure modes relevant
    to: supported categories
-   Persist all required data and audit events consistently for:
    supported categories
-   Add at least one positive test and one relevant negative/failure
    test for: supported categories
-   Document configuration, behavior, limitations, and manual setup for:
    supported categories

### Directive 0386 --- Data model `services`

-   Implement this requirement in the actual repository:
    active/publication state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active/publication state
-   Persist all required data and audit events consistently for:
    active/publication state
-   Add at least one positive test and one relevant negative/failure
    test for: active/publication state
-   Document configuration, behavior, limitations, and manual setup for:
    active/publication state

### Directive 0387 --- Data model `services`

-   Implement this requirement in the actual repository: verified
    instructions/contact/hours
-   Validate the inputs, permissions, state, and failure modes relevant
    to: verified instructions/contact/hours
-   Persist all required data and audit events consistently for:
    verified instructions/contact/hours
-   Add at least one positive test and one relevant negative/failure
    test for: verified instructions/contact/hours
-   Document configuration, behavior, limitations, and manual setup for:
    verified instructions/contact/hours

### Directive 0388 --- Data model `services`

-   Implement this requirement in the actual repository: last reviewed
    timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: last reviewed timestamp
-   Persist all required data and audit events consistently for: last
    reviewed timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: last reviewed timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    last reviewed timestamp

### Directive 0389 --- Data model `categories`

-   Implement this requirement in the actual repository: name and
    description
-   Validate the inputs, permissions, state, and failure modes relevant
    to: name and description
-   Persist all required data and audit events consistently for: name
    and description
-   Add at least one positive test and one relevant negative/failure
    test for: name and description
-   Document configuration, behavior, limitations, and manual setup for:
    name and description

### Directive 0390 --- Data model `categories`

-   Implement this requirement in the actual repository: optional parent
    category
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional parent category
-   Persist all required data and audit events consistently for:
    optional parent category
-   Add at least one positive test and one relevant negative/failure
    test for: optional parent category
-   Document configuration, behavior, limitations, and manual setup for:
    optional parent category

### Directive 0391 --- Data model `categories`

-   Implement this requirement in the actual repository: synonyms
-   Validate the inputs, permissions, state, and failure modes relevant
    to: synonyms
-   Persist all required data and audit events consistently for:
    synonyms
-   Add at least one positive test and one relevant negative/failure
    test for: synonyms
-   Document configuration, behavior, limitations, and manual setup for:
    synonyms

### Directive 0392 --- Data model `categories`

-   Implement this requirement in the actual repository: active state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active state
-   Persist all required data and audit events consistently for: active
    state
-   Add at least one positive test and one relevant negative/failure
    test for: active state
-   Document configuration, behavior, limitations, and manual setup for:
    active state

### Directive 0393 --- Data model `categories`

-   Implement this requirement in the actual repository: routing
    relation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: routing relation
-   Persist all required data and audit events consistently for: routing
    relation
-   Add at least one positive test and one relevant negative/failure
    test for: routing relation
-   Document configuration, behavior, limitations, and manual setup for:
    routing relation

### Directive 0394 --- Data model `categories`

-   Implement this requirement in the actual repository: priority/SLA
    relation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: priority/SLA relation
-   Persist all required data and audit events consistently for:
    priority/SLA relation
-   Add at least one positive test and one relevant negative/failure
    test for: priority/SLA relation
-   Document configuration, behavior, limitations, and manual setup for:
    priority/SLA relation

### Directive 0395 --- Data model `categories`

-   Implement this requirement in the actual repository: historical
    label preservation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: historical label preservation
-   Persist all required data and audit events consistently for:
    historical label preservation
-   Add at least one positive test and one relevant negative/failure
    test for: historical label preservation
-   Document configuration, behavior, limitations, and manual setup for:
    historical label preservation

### Directive 0396 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: category and
    optional geographic match
-   Validate the inputs, permissions, state, and failure modes relevant
    to: category and optional geographic match
-   Persist all required data and audit events consistently for:
    category and optional geographic match
-   Add at least one positive test and one relevant negative/failure
    test for: category and optional geographic match
-   Document configuration, behavior, limitations, and manual setup for:
    category and optional geographic match

### Directive 0397 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: target
    department/queue
-   Validate the inputs, permissions, state, and failure modes relevant
    to: target department/queue
-   Persist all required data and audit events consistently for: target
    department/queue
-   Add at least one positive test and one relevant negative/failure
    test for: target department/queue
-   Document configuration, behavior, limitations, and manual setup for:
    target department/queue

### Directive 0398 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: precedence
-   Validate the inputs, permissions, state, and failure modes relevant
    to: precedence
-   Persist all required data and audit events consistently for:
    precedence
-   Add at least one positive test and one relevant negative/failure
    test for: precedence
-   Document configuration, behavior, limitations, and manual setup for:
    precedence

### Directive 0399 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: effective dates
-   Validate the inputs, permissions, state, and failure modes relevant
    to: effective dates
-   Persist all required data and audit events consistently for:
    effective dates
-   Add at least one positive test and one relevant negative/failure
    test for: effective dates
-   Document configuration, behavior, limitations, and manual setup for:
    effective dates

### Directive 0400 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: active state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: active state
-   Persist all required data and audit events consistently for: active
    state
-   Add at least one positive test and one relevant negative/failure
    test for: active state
-   Document configuration, behavior, limitations, and manual setup for:
    active state

### Directive 0401 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: created/updated
    actor
-   Validate the inputs, permissions, state, and failure modes relevant
    to: created/updated actor
-   Persist all required data and audit events consistently for:
    created/updated actor
-   Add at least one positive test and one relevant negative/failure
    test for: created/updated actor
-   Document configuration, behavior, limitations, and manual setup for:
    created/updated actor

### Directive 0402 --- Data model `routing_rules`

-   Implement this requirement in the actual repository: version/audit
    history
-   Validate the inputs, permissions, state, and failure modes relevant
    to: version/audit history
-   Persist all required data and audit events consistently for:
    version/audit history
-   Add at least one positive test and one relevant negative/failure
    test for: version/audit history
-   Document configuration, behavior, limitations, and manual setup for:
    version/audit history

### Directive 0403 --- Data model `complaints`

-   Implement this requirement in the actual repository: internal ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: internal ID
-   Persist all required data and audit events consistently for:
    internal ID
-   Add at least one positive test and one relevant negative/failure
    test for: internal ID
-   Document configuration, behavior, limitations, and manual setup for:
    internal ID

### Directive 0404 --- Data model `complaints`

-   Implement this requirement in the actual repository: unique public
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: unique public reference
-   Persist all required data and audit events consistently for: unique
    public reference
-   Add at least one positive test and one relevant negative/failure
    test for: unique public reference
-   Document configuration, behavior, limitations, and manual setup for:
    unique public reference

### Directive 0405 --- Data model `complaints`

-   Implement this requirement in the actual repository: reporter ID or
    allowed anonymous mode
-   Validate the inputs, permissions, state, and failure modes relevant
    to: reporter ID or allowed anonymous mode
-   Persist all required data and audit events consistently for:
    reporter ID or allowed anonymous mode
-   Add at least one positive test and one relevant negative/failure
    test for: reporter ID or allowed anonymous mode
-   Document configuration, behavior, limitations, and manual setup for:
    reporter ID or allowed anonymous mode

### Directive 0406 --- Data model `complaints`

-   Implement this requirement in the actual repository: title and
    description
-   Validate the inputs, permissions, state, and failure modes relevant
    to: title and description
-   Persist all required data and audit events consistently for: title
    and description
-   Add at least one positive test and one relevant negative/failure
    test for: title and description
-   Document configuration, behavior, limitations, and manual setup for:
    title and description

### Directive 0407 --- Data model `complaints`

-   Implement this requirement in the actual repository:
    category/subcategory
-   Validate the inputs, permissions, state, and failure modes relevant
    to: category/subcategory
-   Persist all required data and audit events consistently for:
    category/subcategory
-   Add at least one positive test and one relevant negative/failure
    test for: category/subcategory
-   Document configuration, behavior, limitations, and manual setup for:
    category/subcategory

### Directive 0408 --- Data model `complaints`

-   Implement this requirement in the actual repository:
    coordinates/address/ward
-   Validate the inputs, permissions, state, and failure modes relevant
    to: coordinates/address/ward
-   Persist all required data and audit events consistently for:
    coordinates/address/ward
-   Add at least one positive test and one relevant negative/failure
    test for: coordinates/address/ward
-   Document configuration, behavior, limitations, and manual setup for:
    coordinates/address/ward

### Directive 0409 --- Data model `complaints`

-   Implement this requirement in the actual repository: visibility
-   Validate the inputs, permissions, state, and failure modes relevant
    to: visibility
-   Persist all required data and audit events consistently for:
    visibility
-   Add at least one positive test and one relevant negative/failure
    test for: visibility
-   Document configuration, behavior, limitations, and manual setup for:
    visibility

### Directive 0410 --- Data model `complaints`

-   Implement this requirement in the actual repository: priority and
    status
-   Validate the inputs, permissions, state, and failure modes relevant
    to: priority and status
-   Persist all required data and audit events consistently for:
    priority and status
-   Add at least one positive test and one relevant negative/failure
    test for: priority and status
-   Document configuration, behavior, limitations, and manual setup for:
    priority and status

### Directive 0411 --- Data model `complaints`

-   Implement this requirement in the actual repository: department and
    assignment
-   Validate the inputs, permissions, state, and failure modes relevant
    to: department and assignment
-   Persist all required data and audit events consistently for:
    department and assignment
-   Add at least one positive test and one relevant negative/failure
    test for: department and assignment
-   Document configuration, behavior, limitations, and manual setup for:
    department and assignment

### Directive 0412 --- Data model `complaints`

-   Implement this requirement in the actual repository:
    due/resolved/closed timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: due/resolved/closed timestamps
-   Persist all required data and audit events consistently for:
    due/resolved/closed timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: due/resolved/closed timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    due/resolved/closed timestamps

### Directive 0413 --- Data model `complaints`

-   Implement this requirement in the actual repository: version for
    concurrency
-   Validate the inputs, permissions, state, and failure modes relevant
    to: version for concurrency
-   Persist all required data and audit events consistently for: version
    for concurrency
-   Add at least one positive test and one relevant negative/failure
    test for: version for concurrency
-   Document configuration, behavior, limitations, and manual setup for:
    version for concurrency

### Directive 0414 --- Data model `complaints`

-   Implement this requirement in the actual repository: optional
    confirmed external case ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional confirmed external case ID
-   Persist all required data and audit events consistently for:
    optional confirmed external case ID
-   Add at least one positive test and one relevant negative/failure
    test for: optional confirmed external case ID
-   Document configuration, behavior, limitations, and manual setup for:
    optional confirmed external case ID

### Directive 0415 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0416 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: uploader ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: uploader ID
-   Persist all required data and audit events consistently for:
    uploader ID
-   Add at least one positive test and one relevant negative/failure
    test for: uploader ID
-   Document configuration, behavior, limitations, and manual setup for:
    uploader ID

### Directive 0417 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: opaque storage
    key
-   Validate the inputs, permissions, state, and failure modes relevant
    to: opaque storage key
-   Persist all required data and audit events consistently for: opaque
    storage key
-   Add at least one positive test and one relevant negative/failure
    test for: opaque storage key
-   Document configuration, behavior, limitations, and manual setup for:
    opaque storage key

### Directive 0418 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: sanitized
    filename
-   Validate the inputs, permissions, state, and failure modes relevant
    to: sanitized filename
-   Persist all required data and audit events consistently for:
    sanitized filename
-   Add at least one positive test and one relevant negative/failure
    test for: sanitized filename
-   Document configuration, behavior, limitations, and manual setup for:
    sanitized filename

### Directive 0419 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: content type
    and size
-   Validate the inputs, permissions, state, and failure modes relevant
    to: content type and size
-   Persist all required data and audit events consistently for: content
    type and size
-   Add at least one positive test and one relevant negative/failure
    test for: content type and size
-   Document configuration, behavior, limitations, and manual setup for:
    content type and size

### Directive 0420 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: media kind
-   Validate the inputs, permissions, state, and failure modes relevant
    to: media kind
-   Persist all required data and audit events consistently for: media
    kind
-   Add at least one positive test and one relevant negative/failure
    test for: media kind
-   Document configuration, behavior, limitations, and manual setup for:
    media kind

### Directive 0421 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: visibility
-   Validate the inputs, permissions, state, and failure modes relevant
    to: visibility
-   Persist all required data and audit events consistently for:
    visibility
-   Add at least one positive test and one relevant negative/failure
    test for: visibility
-   Document configuration, behavior, limitations, and manual setup for:
    visibility

### Directive 0422 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: scan state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: scan state
-   Persist all required data and audit events consistently for: scan
    state
-   Add at least one positive test and one relevant negative/failure
    test for: scan state
-   Document configuration, behavior, limitations, and manual setup for:
    scan state

### Directive 0423 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: upload
    timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: upload timestamp
-   Persist all required data and audit events consistently for: upload
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: upload timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    upload timestamp

### Directive 0424 --- Data model `complaint_media`

-   Implement this requirement in the actual repository: optional
    sanitized public derivative
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional sanitized public derivative
-   Persist all required data and audit events consistently for:
    optional sanitized public derivative
-   Add at least one positive test and one relevant negative/failure
    test for: optional sanitized public derivative
-   Document configuration, behavior, limitations, and manual setup for:
    optional sanitized public derivative

### Directive 0425 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0426 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: previous and
    next status
-   Validate the inputs, permissions, state, and failure modes relevant
    to: previous and next status
-   Persist all required data and audit events consistently for:
    previous and next status
-   Add at least one positive test and one relevant negative/failure
    test for: previous and next status
-   Document configuration, behavior, limitations, and manual setup for:
    previous and next status

### Directive 0427 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: actor
-   Validate the inputs, permissions, state, and failure modes relevant
    to: actor
-   Persist all required data and audit events consistently for: actor
-   Add at least one positive test and one relevant negative/failure
    test for: actor
-   Document configuration, behavior, limitations, and manual setup for:
    actor

### Directive 0428 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: reason
-   Validate the inputs, permissions, state, and failure modes relevant
    to: reason
-   Persist all required data and audit events consistently for: reason
-   Add at least one positive test and one relevant negative/failure
    test for: reason
-   Document configuration, behavior, limitations, and manual setup for:
    reason

### Directive 0429 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: system/human
    marker
-   Validate the inputs, permissions, state, and failure modes relevant
    to: system/human marker
-   Persist all required data and audit events consistently for:
    system/human marker
-   Add at least one positive test and one relevant negative/failure
    test for: system/human marker
-   Document configuration, behavior, limitations, and manual setup for:
    system/human marker

### Directive 0430 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: server
    timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: server timestamp
-   Persist all required data and audit events consistently for: server
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: server timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    server timestamp

### Directive 0431 --- Data model `complaint_status_history`

-   Implement this requirement in the actual repository: immutable to
    ordinary users
-   Validate the inputs, permissions, state, and failure modes relevant
    to: immutable to ordinary users
-   Persist all required data and audit events consistently for:
    immutable to ordinary users
-   Add at least one positive test and one relevant negative/failure
    test for: immutable to ordinary users
-   Document configuration, behavior, limitations, and manual setup for:
    immutable to ordinary users

### Directive 0432 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0433 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: old/new
    department
-   Validate the inputs, permissions, state, and failure modes relevant
    to: old/new department
-   Persist all required data and audit events consistently for: old/new
    department
-   Add at least one positive test and one relevant negative/failure
    test for: old/new department
-   Document configuration, behavior, limitations, and manual setup for:
    old/new department

### Directive 0434 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: old/new
    officer/team
-   Validate the inputs, permissions, state, and failure modes relevant
    to: old/new officer/team
-   Persist all required data and audit events consistently for: old/new
    officer/team
-   Add at least one positive test and one relevant negative/failure
    test for: old/new officer/team
-   Document configuration, behavior, limitations, and manual setup for:
    old/new officer/team

### Directive 0435 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: actor
-   Validate the inputs, permissions, state, and failure modes relevant
    to: actor
-   Persist all required data and audit events consistently for: actor
-   Add at least one positive test and one relevant negative/failure
    test for: actor
-   Document configuration, behavior, limitations, and manual setup for:
    actor

### Directive 0436 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: reason
-   Validate the inputs, permissions, state, and failure modes relevant
    to: reason
-   Persist all required data and audit events consistently for: reason
-   Add at least one positive test and one relevant negative/failure
    test for: reason
-   Document configuration, behavior, limitations, and manual setup for:
    reason

### Directive 0437 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: routing rule
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: routing rule reference
-   Persist all required data and audit events consistently for: routing
    rule reference
-   Add at least one positive test and one relevant negative/failure
    test for: routing rule reference
-   Document configuration, behavior, limitations, and manual setup for:
    routing rule reference

### Directive 0438 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0439 --- Data model `complaint_assignments`

-   Implement this requirement in the actual repository: historical
    assignment preservation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: historical assignment preservation
-   Persist all required data and audit events consistently for:
    historical assignment preservation
-   Add at least one positive test and one relevant negative/failure
    test for: historical assignment preservation
-   Document configuration, behavior, limitations, and manual setup for:
    historical assignment preservation

### Directive 0440 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0441 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: author
-   Validate the inputs, permissions, state, and failure modes relevant
    to: author
-   Persist all required data and audit events consistently for: author
-   Add at least one positive test and one relevant negative/failure
    test for: author
-   Document configuration, behavior, limitations, and manual setup for:
    author

### Directive 0442 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: body
-   Validate the inputs, permissions, state, and failure modes relevant
    to: body
-   Persist all required data and audit events consistently for: body
-   Add at least one positive test and one relevant negative/failure
    test for: body
-   Document configuration, behavior, limitations, and manual setup for:
    body

### Directive 0443 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: visibility
-   Validate the inputs, permissions, state, and failure modes relevant
    to: visibility
-   Persist all required data and audit events consistently for:
    visibility
-   Add at least one positive test and one relevant negative/failure
    test for: visibility
-   Document configuration, behavior, limitations, and manual setup for:
    visibility

### Directive 0444 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamps
-   Persist all required data and audit events consistently for:
    timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    timestamps

### Directive 0445 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: moderation/edit
    state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: moderation/edit state
-   Persist all required data and audit events consistently for:
    moderation/edit state
-   Add at least one positive test and one relevant negative/failure
    test for: moderation/edit state
-   Document configuration, behavior, limitations, and manual setup for:
    moderation/edit state

### Directive 0446 --- Data model `complaint_comments`

-   Implement this requirement in the actual repository: no
    client-controlled author identity
-   Validate the inputs, permissions, state, and failure modes relevant
    to: no client-controlled author identity
-   Persist all required data and audit events consistently for: no
    client-controlled author identity
-   Add at least one positive test and one relevant negative/failure
    test for: no client-controlled author identity
-   Document configuration, behavior, limitations, and manual setup for:
    no client-controlled author identity

### Directive 0447 --- Data model `complaint_internal_notes`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0448 --- Data model `complaint_internal_notes`

-   Implement this requirement in the actual repository: authorized
    staff author
-   Validate the inputs, permissions, state, and failure modes relevant
    to: authorized staff author
-   Persist all required data and audit events consistently for:
    authorized staff author
-   Add at least one positive test and one relevant negative/failure
    test for: authorized staff author
-   Document configuration, behavior, limitations, and manual setup for:
    authorized staff author

### Directive 0449 --- Data model `complaint_internal_notes`

-   Implement this requirement in the actual repository: body
-   Validate the inputs, permissions, state, and failure modes relevant
    to: body
-   Persist all required data and audit events consistently for: body
-   Add at least one positive test and one relevant negative/failure
    test for: body
-   Document configuration, behavior, limitations, and manual setup for:
    body

### Directive 0450 --- Data model `complaint_internal_notes`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0451 --- Data model `complaint_internal_notes`

-   Implement this requirement in the actual repository: strict
    staff-only access
-   Validate the inputs, permissions, state, and failure modes relevant
    to: strict staff-only access
-   Persist all required data and audit events consistently for: strict
    staff-only access
-   Add at least one positive test and one relevant negative/failure
    test for: strict staff-only access
-   Document configuration, behavior, limitations, and manual setup for:
    strict staff-only access

### Directive 0452 --- Data model `complaint_links`

-   Implement this requirement in the actual repository: source and
    target complaint IDs
-   Validate the inputs, permissions, state, and failure modes relevant
    to: source and target complaint IDs
-   Persist all required data and audit events consistently for: source
    and target complaint IDs
-   Add at least one positive test and one relevant negative/failure
    test for: source and target complaint IDs
-   Document configuration, behavior, limitations, and manual setup for:
    source and target complaint IDs

### Directive 0453 --- Data model `complaint_links`

-   Implement this requirement in the actual repository: relationship
    type
-   Validate the inputs, permissions, state, and failure modes relevant
    to: relationship type
-   Persist all required data and audit events consistently for:
    relationship type
-   Add at least one positive test and one relevant negative/failure
    test for: relationship type
-   Document configuration, behavior, limitations, and manual setup for:
    relationship type

### Directive 0454 --- Data model `complaint_links`

-   Implement this requirement in the actual repository: merge/duplicate
    reason
-   Validate the inputs, permissions, state, and failure modes relevant
    to: merge/duplicate reason
-   Persist all required data and audit events consistently for:
    merge/duplicate reason
-   Add at least one positive test and one relevant negative/failure
    test for: merge/duplicate reason
-   Document configuration, behavior, limitations, and manual setup for:
    merge/duplicate reason

### Directive 0455 --- Data model `complaint_links`

-   Implement this requirement in the actual repository: actor and
    timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: actor and timestamp
-   Persist all required data and audit events consistently for: actor
    and timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: actor and timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    actor and timestamp

### Directive 0456 --- Data model `complaint_links`

-   Implement this requirement in the actual repository: cycle
    prevention
-   Validate the inputs, permissions, state, and failure modes relevant
    to: cycle prevention
-   Persist all required data and audit events consistently for: cycle
    prevention
-   Add at least one positive test and one relevant negative/failure
    test for: cycle prevention
-   Document configuration, behavior, limitations, and manual setup for:
    cycle prevention

### Directive 0457 --- Data model `complaint_supporters`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0458 --- Data model `complaint_supporters`

-   Implement this requirement in the actual repository: user or
    permitted anonymous key
-   Validate the inputs, permissions, state, and failure modes relevant
    to: user or permitted anonymous key
-   Persist all required data and audit events consistently for: user or
    permitted anonymous key
-   Add at least one positive test and one relevant negative/failure
    test for: user or permitted anonymous key
-   Document configuration, behavior, limitations, and manual setup for:
    user or permitted anonymous key

### Directive 0459 --- Data model `complaint_supporters`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0460 --- Data model `complaint_supporters`

-   Implement this requirement in the actual repository: uniqueness
    policy
-   Validate the inputs, permissions, state, and failure modes relevant
    to: uniqueness policy
-   Persist all required data and audit events consistently for:
    uniqueness policy
-   Add at least one positive test and one relevant negative/failure
    test for: uniqueness policy
-   Document configuration, behavior, limitations, and manual setup for:
    uniqueness policy

### Directive 0461 --- Data model `complaint_supporters`

-   Implement this requirement in the actual repository: no public
    supporter identity
-   Validate the inputs, permissions, state, and failure modes relevant
    to: no public supporter identity
-   Persist all required data and audit events consistently for: no
    public supporter identity
-   Add at least one positive test and one relevant negative/failure
    test for: no public supporter identity
-   Document configuration, behavior, limitations, and manual setup for:
    no public supporter identity

### Directive 0462 --- Data model `sla_policies`

-   Implement this requirement in the actual repository:
    category/priority/department scope
-   Validate the inputs, permissions, state, and failure modes relevant
    to: category/priority/department scope
-   Persist all required data and audit events consistently for:
    category/priority/department scope
-   Add at least one positive test and one relevant negative/failure
    test for: category/priority/department scope
-   Document configuration, behavior, limitations, and manual setup for:
    category/priority/department scope

### Directive 0463 --- Data model `sla_policies`

-   Implement this requirement in the actual repository:
    acknowledgement/assignment/resolution targets
-   Validate the inputs, permissions, state, and failure modes relevant
    to: acknowledgement/assignment/resolution targets
-   Persist all required data and audit events consistently for:
    acknowledgement/assignment/resolution targets
-   Add at least one positive test and one relevant negative/failure
    test for: acknowledgement/assignment/resolution targets
-   Document configuration, behavior, limitations, and manual setup for:
    acknowledgement/assignment/resolution targets

### Directive 0464 --- Data model `sla_policies`

-   Implement this requirement in the actual repository: calendar and
    pause rules
-   Validate the inputs, permissions, state, and failure modes relevant
    to: calendar and pause rules
-   Persist all required data and audit events consistently for:
    calendar and pause rules
-   Add at least one positive test and one relevant negative/failure
    test for: calendar and pause rules
-   Document configuration, behavior, limitations, and manual setup for:
    calendar and pause rules

### Directive 0465 --- Data model `sla_policies`

-   Implement this requirement in the actual repository: effective dates
-   Validate the inputs, permissions, state, and failure modes relevant
    to: effective dates
-   Persist all required data and audit events consistently for:
    effective dates
-   Add at least one positive test and one relevant negative/failure
    test for: effective dates
-   Document configuration, behavior, limitations, and manual setup for:
    effective dates

### Directive 0466 --- Data model `sla_policies`

-   Implement this requirement in the actual repository: version
-   Validate the inputs, permissions, state, and failure modes relevant
    to: version
-   Persist all required data and audit events consistently for: version
-   Add at least one positive test and one relevant negative/failure
    test for: version
-   Document configuration, behavior, limitations, and manual setup for:
    version

### Directive 0467 --- Data model `sla_policies`

-   Implement this requirement in the actual repository: illustrative
    versus official policy label
-   Validate the inputs, permissions, state, and failure modes relevant
    to: illustrative versus official policy label
-   Persist all required data and audit events consistently for:
    illustrative versus official policy label
-   Add at least one positive test and one relevant negative/failure
    test for: illustrative versus official policy label
-   Document configuration, behavior, limitations, and manual setup for:
    illustrative versus official policy label

### Directive 0468 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0469 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: rule and
    trigger
-   Validate the inputs, permissions, state, and failure modes relevant
    to: rule and trigger
-   Persist all required data and audit events consistently for: rule
    and trigger
-   Add at least one positive test and one relevant negative/failure
    test for: rule and trigger
-   Document configuration, behavior, limitations, and manual setup for:
    rule and trigger

### Directive 0470 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: target
    queue/supervisor
-   Validate the inputs, permissions, state, and failure modes relevant
    to: target queue/supervisor
-   Persist all required data and audit events consistently for: target
    queue/supervisor
-   Add at least one positive test and one relevant negative/failure
    test for: target queue/supervisor
-   Document configuration, behavior, limitations, and manual setup for:
    target queue/supervisor

### Directive 0471 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: actor/system
    marker
-   Validate the inputs, permissions, state, and failure modes relevant
    to: actor/system marker
-   Persist all required data and audit events consistently for:
    actor/system marker
-   Add at least one positive test and one relevant negative/failure
    test for: actor/system marker
-   Document configuration, behavior, limitations, and manual setup for:
    actor/system marker

### Directive 0472 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0473 --- Data model `escalation_history`

-   Implement this requirement in the actual repository: delivery/action
    result
-   Validate the inputs, permissions, state, and failure modes relevant
    to: delivery/action result
-   Persist all required data and audit events consistently for:
    delivery/action result
-   Add at least one positive test and one relevant negative/failure
    test for: delivery/action result
-   Document configuration, behavior, limitations, and manual setup for:
    delivery/action result

### Directive 0474 --- Data model `notifications`

-   Implement this requirement in the actual repository: recipient
-   Validate the inputs, permissions, state, and failure modes relevant
    to: recipient
-   Persist all required data and audit events consistently for:
    recipient
-   Add at least one positive test and one relevant negative/failure
    test for: recipient
-   Document configuration, behavior, limitations, and manual setup for:
    recipient

### Directive 0475 --- Data model `notifications`

-   Implement this requirement in the actual repository: complaint
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint reference
-   Persist all required data and audit events consistently for:
    complaint reference
-   Add at least one positive test and one relevant negative/failure
    test for: complaint reference
-   Document configuration, behavior, limitations, and manual setup for:
    complaint reference

### Directive 0476 --- Data model `notifications`

-   Implement this requirement in the actual repository: event type
-   Validate the inputs, permissions, state, and failure modes relevant
    to: event type
-   Persist all required data and audit events consistently for: event
    type
-   Add at least one positive test and one relevant negative/failure
    test for: event type
-   Document configuration, behavior, limitations, and manual setup for:
    event type

### Directive 0477 --- Data model `notifications`

-   Implement this requirement in the actual repository: channel
-   Validate the inputs, permissions, state, and failure modes relevant
    to: channel
-   Persist all required data and audit events consistently for: channel
-   Add at least one positive test and one relevant negative/failure
    test for: channel
-   Document configuration, behavior, limitations, and manual setup for:
    channel

### Directive 0478 --- Data model `notifications`

-   Implement this requirement in the actual repository: template
    version
-   Validate the inputs, permissions, state, and failure modes relevant
    to: template version
-   Persist all required data and audit events consistently for:
    template version
-   Add at least one positive test and one relevant negative/failure
    test for: template version
-   Document configuration, behavior, limitations, and manual setup for:
    template version

### Directive 0479 --- Data model `notifications`

-   Implement this requirement in the actual repository: delivery status
-   Validate the inputs, permissions, state, and failure modes relevant
    to: delivery status
-   Persist all required data and audit events consistently for:
    delivery status
-   Add at least one positive test and one relevant negative/failure
    test for: delivery status
-   Document configuration, behavior, limitations, and manual setup for:
    delivery status

### Directive 0480 --- Data model `notifications`

-   Implement this requirement in the actual repository: attempt count
-   Validate the inputs, permissions, state, and failure modes relevant
    to: attempt count
-   Persist all required data and audit events consistently for: attempt
    count
-   Add at least one positive test and one relevant negative/failure
    test for: attempt count
-   Document configuration, behavior, limitations, and manual setup for:
    attempt count

### Directive 0481 --- Data model `notifications`

-   Implement this requirement in the actual repository: provider
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: provider reference
-   Persist all required data and audit events consistently for:
    provider reference
-   Add at least one positive test and one relevant negative/failure
    test for: provider reference
-   Document configuration, behavior, limitations, and manual setup for:
    provider reference

### Directive 0482 --- Data model `notifications`

-   Implement this requirement in the actual repository:
    created/sent/read timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: created/sent/read timestamps
-   Persist all required data and audit events consistently for:
    created/sent/read timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: created/sent/read timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    created/sent/read timestamps

### Directive 0483 --- Data model `notification_preferences`

-   Implement this requirement in the actual repository: user ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: user ID
-   Persist all required data and audit events consistently for: user ID
-   Add at least one positive test and one relevant negative/failure
    test for: user ID
-   Document configuration, behavior, limitations, and manual setup for:
    user ID

### Directive 0484 --- Data model `notification_preferences`

-   Implement this requirement in the actual repository: channel
    settings
-   Validate the inputs, permissions, state, and failure modes relevant
    to: channel settings
-   Persist all required data and audit events consistently for: channel
    settings
-   Add at least one positive test and one relevant negative/failure
    test for: channel settings
-   Document configuration, behavior, limitations, and manual setup for:
    channel settings

### Directive 0485 --- Data model `notification_preferences`

-   Implement this requirement in the actual repository: language
-   Validate the inputs, permissions, state, and failure modes relevant
    to: language
-   Persist all required data and audit events consistently for:
    language
-   Add at least one positive test and one relevant negative/failure
    test for: language
-   Document configuration, behavior, limitations, and manual setup for:
    language

### Directive 0486 --- Data model `notification_preferences`

-   Implement this requirement in the actual repository: consent/opt-out
    state where applicable
-   Validate the inputs, permissions, state, and failure modes relevant
    to: consent/opt-out state where applicable
-   Persist all required data and audit events consistently for:
    consent/opt-out state where applicable
-   Add at least one positive test and one relevant negative/failure
    test for: consent/opt-out state where applicable
-   Document configuration, behavior, limitations, and manual setup for:
    consent/opt-out state where applicable

### Directive 0487 --- Data model `notification_preferences`

-   Implement this requirement in the actual repository: updated
    timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: updated timestamp
-   Persist all required data and audit events consistently for: updated
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: updated timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    updated timestamp

### Directive 0488 --- Data model `feedback`

-   Implement this requirement in the actual repository: complaint ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint ID
-   Persist all required data and audit events consistently for:
    complaint ID
-   Add at least one positive test and one relevant negative/failure
    test for: complaint ID
-   Document configuration, behavior, limitations, and manual setup for:
    complaint ID

### Directive 0489 --- Data model `feedback`

-   Implement this requirement in the actual repository: authorized
    reporter
-   Validate the inputs, permissions, state, and failure modes relevant
    to: authorized reporter
-   Persist all required data and audit events consistently for:
    authorized reporter
-   Add at least one positive test and one relevant negative/failure
    test for: authorized reporter
-   Document configuration, behavior, limitations, and manual setup for:
    authorized reporter

### Directive 0490 --- Data model `feedback`

-   Implement this requirement in the actual repository: bounded rating
-   Validate the inputs, permissions, state, and failure modes relevant
    to: bounded rating
-   Persist all required data and audit events consistently for: bounded
    rating
-   Add at least one positive test and one relevant negative/failure
    test for: bounded rating
-   Document configuration, behavior, limitations, and manual setup for:
    bounded rating

### Directive 0491 --- Data model `feedback`

-   Implement this requirement in the actual repository: optional text
-   Validate the inputs, permissions, state, and failure modes relevant
    to: optional text
-   Persist all required data and audit events consistently for:
    optional text
-   Add at least one positive test and one relevant negative/failure
    test for: optional text
-   Document configuration, behavior, limitations, and manual setup for:
    optional text

### Directive 0492 --- Data model `feedback`

-   Implement this requirement in the actual repository: timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamps
-   Persist all required data and audit events consistently for:
    timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    timestamps

### Directive 0493 --- Data model `feedback`

-   Implement this requirement in the actual repository: duplicate
    feedback policy
-   Validate the inputs, permissions, state, and failure modes relevant
    to: duplicate feedback policy
-   Persist all required data and audit events consistently for:
    duplicate feedback policy
-   Add at least one positive test and one relevant negative/failure
    test for: duplicate feedback policy
-   Document configuration, behavior, limitations, and manual setup for:
    duplicate feedback policy

### Directive 0494 --- Data model `announcements`

-   Implement this requirement in the actual repository: title/body
-   Validate the inputs, permissions, state, and failure modes relevant
    to: title/body
-   Persist all required data and audit events consistently for:
    title/body
-   Add at least one positive test and one relevant negative/failure
    test for: title/body
-   Document configuration, behavior, limitations, and manual setup for:
    title/body

### Directive 0495 --- Data model `announcements`

-   Implement this requirement in the actual repository: audience or
    ward scope
-   Validate the inputs, permissions, state, and failure modes relevant
    to: audience or ward scope
-   Persist all required data and audit events consistently for:
    audience or ward scope
-   Add at least one positive test and one relevant negative/failure
    test for: audience or ward scope
-   Document configuration, behavior, limitations, and manual setup for:
    audience or ward scope

### Directive 0496 --- Data model `announcements`

-   Implement this requirement in the actual repository:
    draft/published/expired state
-   Validate the inputs, permissions, state, and failure modes relevant
    to: draft/published/expired state
-   Persist all required data and audit events consistently for:
    draft/published/expired state
-   Add at least one positive test and one relevant negative/failure
    test for: draft/published/expired state
-   Document configuration, behavior, limitations, and manual setup for:
    draft/published/expired state

### Directive 0497 --- Data model `announcements`

-   Implement this requirement in the actual repository: publisher
-   Validate the inputs, permissions, state, and failure modes relevant
    to: publisher
-   Persist all required data and audit events consistently for:
    publisher
-   Add at least one positive test and one relevant negative/failure
    test for: publisher
-   Document configuration, behavior, limitations, and manual setup for:
    publisher

### Directive 0498 --- Data model `announcements`

-   Implement this requirement in the actual repository: publish window
-   Validate the inputs, permissions, state, and failure modes relevant
    to: publish window
-   Persist all required data and audit events consistently for: publish
    window
-   Add at least one positive test and one relevant negative/failure
    test for: publish window
-   Document configuration, behavior, limitations, and manual setup for:
    publish window

### Directive 0499 --- Data model `announcements`

-   Implement this requirement in the actual repository: audit history
-   Validate the inputs, permissions, state, and failure modes relevant
    to: audit history
-   Persist all required data and audit events consistently for: audit
    history
-   Add at least one positive test and one relevant negative/failure
    test for: audit history
-   Document configuration, behavior, limitations, and manual setup for:
    audit history

### Directive 0500 --- Data model `announcements`

-   Implement this requirement in the actual repository: demo label if
    synthetic
-   Validate the inputs, permissions, state, and failure modes relevant
    to: demo label if synthetic
-   Persist all required data and audit events consistently for: demo
    label if synthetic
-   Add at least one positive test and one relevant negative/failure
    test for: demo label if synthetic
-   Document configuration, behavior, limitations, and manual setup for:
    demo label if synthetic

### Directive 0501 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: actor
-   Validate the inputs, permissions, state, and failure modes relevant
    to: actor
-   Persist all required data and audit events consistently for: actor
-   Add at least one positive test and one relevant negative/failure
    test for: actor
-   Document configuration, behavior, limitations, and manual setup for:
    actor

### Directive 0502 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: action
-   Validate the inputs, permissions, state, and failure modes relevant
    to: action
-   Persist all required data and audit events consistently for: action
-   Add at least one positive test and one relevant negative/failure
    test for: action
-   Document configuration, behavior, limitations, and manual setup for:
    action

### Directive 0503 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: entity type/ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: entity type/ID
-   Persist all required data and audit events consistently for: entity
    type/ID
-   Add at least one positive test and one relevant negative/failure
    test for: entity type/ID
-   Document configuration, behavior, limitations, and manual setup for:
    entity type/ID

### Directive 0504 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0505 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: reason
-   Validate the inputs, permissions, state, and failure modes relevant
    to: reason
-   Persist all required data and audit events consistently for: reason
-   Add at least one positive test and one relevant negative/failure
    test for: reason
-   Document configuration, behavior, limitations, and manual setup for:
    reason

### Directive 0506 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: correlation ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: correlation ID
-   Persist all required data and audit events consistently for:
    correlation ID
-   Add at least one positive test and one relevant negative/failure
    test for: correlation ID
-   Document configuration, behavior, limitations, and manual setup for:
    correlation ID

### Directive 0507 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: safe
    before/after summary
-   Validate the inputs, permissions, state, and failure modes relevant
    to: safe before/after summary
-   Persist all required data and audit events consistently for: safe
    before/after summary
-   Add at least one positive test and one relevant negative/failure
    test for: safe before/after summary
-   Document configuration, behavior, limitations, and manual setup for:
    safe before/after summary

### Directive 0508 --- Data model `audit_logs`

-   Implement this requirement in the actual repository: restricted read
    access
-   Validate the inputs, permissions, state, and failure modes relevant
    to: restricted read access
-   Persist all required data and audit events consistently for:
    restricted read access
-   Add at least one positive test and one relevant negative/failure
    test for: restricted read access
-   Document configuration, behavior, limitations, and manual setup for:
    restricted read access

### Directive 0509 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: caller scope
-   Validate the inputs, permissions, state, and failure modes relevant
    to: caller scope
-   Persist all required data and audit events consistently for: caller
    scope
-   Add at least one positive test and one relevant negative/failure
    test for: caller scope
-   Document configuration, behavior, limitations, and manual setup for:
    caller scope

### Directive 0510 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: key
-   Validate the inputs, permissions, state, and failure modes relevant
    to: key
-   Persist all required data and audit events consistently for: key
-   Add at least one positive test and one relevant negative/failure
    test for: key
-   Document configuration, behavior, limitations, and manual setup for:
    key

### Directive 0511 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: operation
-   Validate the inputs, permissions, state, and failure modes relevant
    to: operation
-   Persist all required data and audit events consistently for:
    operation
-   Add at least one positive test and one relevant negative/failure
    test for: operation
-   Document configuration, behavior, limitations, and manual setup for:
    operation

### Directive 0512 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: request
    fingerprint
-   Validate the inputs, permissions, state, and failure modes relevant
    to: request fingerprint
-   Persist all required data and audit events consistently for: request
    fingerprint
-   Add at least one positive test and one relevant negative/failure
    test for: request fingerprint
-   Document configuration, behavior, limitations, and manual setup for:
    request fingerprint

### Directive 0513 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: safe replay
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: safe replay reference
-   Persist all required data and audit events consistently for: safe
    replay reference
-   Add at least one positive test and one relevant negative/failure
    test for: safe replay reference
-   Document configuration, behavior, limitations, and manual setup for:
    safe replay reference

### Directive 0514 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: created/expiry
    timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: created/expiry timestamps
-   Persist all required data and audit events consistently for:
    created/expiry timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: created/expiry timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    created/expiry timestamps

### Directive 0515 --- Data model `idempotency_records`

-   Implement this requirement in the actual repository: unique
    constraint
-   Validate the inputs, permissions, state, and failure modes relevant
    to: unique constraint
-   Persist all required data and audit events consistently for: unique
    constraint
-   Add at least one positive test and one relevant negative/failure
    test for: unique constraint
-   Document configuration, behavior, limitations, and manual setup for:
    unique constraint

### Directive 0516 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: event type
-   Validate the inputs, permissions, state, and failure modes relevant
    to: event type
-   Persist all required data and audit events consistently for: event
    type
-   Add at least one positive test and one relevant negative/failure
    test for: event type
-   Document configuration, behavior, limitations, and manual setup for:
    event type

### Directive 0517 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: aggregate ID
-   Validate the inputs, permissions, state, and failure modes relevant
    to: aggregate ID
-   Persist all required data and audit events consistently for:
    aggregate ID
-   Add at least one positive test and one relevant negative/failure
    test for: aggregate ID
-   Document configuration, behavior, limitations, and manual setup for:
    aggregate ID

### Directive 0518 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: payload version
-   Validate the inputs, permissions, state, and failure modes relevant
    to: payload version
-   Persist all required data and audit events consistently for: payload
    version
-   Add at least one positive test and one relevant negative/failure
    test for: payload version
-   Document configuration, behavior, limitations, and manual setup for:
    payload version

### Directive 0519 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: minimal payload
-   Validate the inputs, permissions, state, and failure modes relevant
    to: minimal payload
-   Persist all required data and audit events consistently for: minimal
    payload
-   Add at least one positive test and one relevant negative/failure
    test for: minimal payload
-   Document configuration, behavior, limitations, and manual setup for:
    minimal payload

### Directive 0520 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: processing
    status
-   Validate the inputs, permissions, state, and failure modes relevant
    to: processing status
-   Persist all required data and audit events consistently for:
    processing status
-   Add at least one positive test and one relevant negative/failure
    test for: processing status
-   Document configuration, behavior, limitations, and manual setup for:
    processing status

### Directive 0521 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: attempt count
-   Validate the inputs, permissions, state, and failure modes relevant
    to: attempt count
-   Persist all required data and audit events consistently for: attempt
    count
-   Add at least one positive test and one relevant negative/failure
    test for: attempt count
-   Document configuration, behavior, limitations, and manual setup for:
    attempt count

### Directive 0522 --- Data model `outbox_events`

-   Implement this requirement in the actual repository:
    created/processed timestamps
-   Validate the inputs, permissions, state, and failure modes relevant
    to: created/processed timestamps
-   Persist all required data and audit events consistently for:
    created/processed timestamps
-   Add at least one positive test and one relevant negative/failure
    test for: created/processed timestamps
-   Document configuration, behavior, limitations, and manual setup for:
    created/processed timestamps

### Directive 0523 --- Data model `outbox_events`

-   Implement this requirement in the actual repository: sanitized
    failure detail
-   Validate the inputs, permissions, state, and failure modes relevant
    to: sanitized failure detail
-   Persist all required data and audit events consistently for:
    sanitized failure detail
-   Add at least one positive test and one relevant negative/failure
    test for: sanitized failure detail
-   Document configuration, behavior, limitations, and manual setup for:
    sanitized failure detail

### Directive 0524 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: complaint/query
    reference
-   Validate the inputs, permissions, state, and failure modes relevant
    to: complaint/query reference
-   Persist all required data and audit events consistently for:
    complaint/query reference
-   Add at least one positive test and one relevant negative/failure
    test for: complaint/query reference
-   Document configuration, behavior, limitations, and manual setup for:
    complaint/query reference

### Directive 0525 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: suggested
    category/department
-   Validate the inputs, permissions, state, and failure modes relevant
    to: suggested category/department
-   Persist all required data and audit events consistently for:
    suggested category/department
-   Add at least one positive test and one relevant negative/failure
    test for: suggested category/department
-   Document configuration, behavior, limitations, and manual setup for:
    suggested category/department

### Directive 0526 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: confidence
-   Validate the inputs, permissions, state, and failure modes relevant
    to: confidence
-   Persist all required data and audit events consistently for:
    confidence
-   Add at least one positive test and one relevant negative/failure
    test for: confidence
-   Document configuration, behavior, limitations, and manual setup for:
    confidence

### Directive 0527 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: model/provider
    version
-   Validate the inputs, permissions, state, and failure modes relevant
    to: model/provider version
-   Persist all required data and audit events consistently for:
    model/provider version
-   Add at least one positive test and one relevant negative/failure
    test for: model/provider version
-   Document configuration, behavior, limitations, and manual setup for:
    model/provider version

### Directive 0528 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: timestamp
-   Validate the inputs, permissions, state, and failure modes relevant
    to: timestamp
-   Persist all required data and audit events consistently for:
    timestamp
-   Add at least one positive test and one relevant negative/failure
    test for: timestamp
-   Document configuration, behavior, limitations, and manual setup for:
    timestamp

### Directive 0529 --- Data model `ai_classifications`

-   Implement this requirement in the actual repository: final
    human-selected value kept separately
-   Validate the inputs, permissions, state, and failure modes relevant
    to: final human-selected value kept separately
-   Persist all required data and audit events consistently for: final
    human-selected value kept separately
-   Add at least one positive test and one relevant negative/failure
    test for: final human-selected value kept separately
-   Document configuration, behavior, limitations, and manual setup for:
    final human-selected value kept separately

### Directive 0530 --- API POST /api/auth/register

-   Implement this requirement in the actual repository: Register
    resident where local registration is enabled
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Register resident where local registration is enabled
-   Persist all required data and audit events consistently for:
    Register resident where local registration is enabled
-   Add at least one positive test and one relevant negative/failure
    test for: Register resident where local registration is enabled
-   Document configuration, behavior, limitations, and manual setup for:
    Register resident where local registration is enabled

### Directive 0531 --- API POST /api/auth/login

-   Implement this requirement in the actual repository: Authenticate
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Authenticate
-   Persist all required data and audit events consistently for:
    Authenticate
-   Add at least one positive test and one relevant negative/failure
    test for: Authenticate
-   Document configuration, behavior, limitations, and manual setup for:
    Authenticate

### Directive 0532 --- API POST /api/auth/logout

-   Implement this requirement in the actual repository: End session or
    revoke relevant credentials
-   Validate the inputs, permissions, state, and failure modes relevant
    to: End session or revoke relevant credentials
-   Persist all required data and audit events consistently for: End
    session or revoke relevant credentials
-   Add at least one positive test and one relevant negative/failure
    test for: End session or revoke relevant credentials
-   Document configuration, behavior, limitations, and manual setup for:
    End session or revoke relevant credentials

### Directive 0533 --- API GET /api/users/me

-   Implement this requirement in the actual repository: Get current
    user's safe profile
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Get current user's safe profile
-   Persist all required data and audit events consistently for: Get
    current user's safe profile
-   Add at least one positive test and one relevant negative/failure
    test for: Get current user's safe profile
-   Document configuration, behavior, limitations, and manual setup for:
    Get current user's safe profile

### Directive 0534 --- API PATCH /api/users/me

-   Implement this requirement in the actual repository: Update
    permitted profile fields
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Update permitted profile fields
-   Persist all required data and audit events consistently for: Update
    permitted profile fields
-   Add at least one positive test and one relevant negative/failure
    test for: Update permitted profile fields
-   Document configuration, behavior, limitations, and manual setup for:
    Update permitted profile fields

### Directive 0535 --- API POST /api/complaints

-   Implement this requirement in the actual repository: Create
    complaint
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create complaint
-   Persist all required data and audit events consistently for: Create
    complaint
-   Add at least one positive test and one relevant negative/failure
    test for: Create complaint
-   Document configuration, behavior, limitations, and manual setup for:
    Create complaint

### Directive 0536 --- API GET /api/complaints

-   Implement this requirement in the actual repository: List authorized
    complaints with pagination and filters
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List authorized complaints with pagination and filters
-   Persist all required data and audit events consistently for: List
    authorized complaints with pagination and filters
-   Add at least one positive test and one relevant negative/failure
    test for: List authorized complaints with pagination and filters
-   Document configuration, behavior, limitations, and manual setup for:
    List authorized complaints with pagination and filters

### Directive 0537 --- API GET /api/complaints/{id}

-   Implement this requirement in the actual repository: Get authorized
    complaint detail
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Get authorized complaint detail
-   Persist all required data and audit events consistently for: Get
    authorized complaint detail
-   Add at least one positive test and one relevant negative/failure
    test for: Get authorized complaint detail
-   Document configuration, behavior, limitations, and manual setup for:
    Get authorized complaint detail

### Directive 0538 --- API PATCH /api/complaints/{id}

-   Implement this requirement in the actual repository: Update allowed
    fields using role-specific schema
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Update allowed fields using role-specific schema
-   Persist all required data and audit events consistently for: Update
    allowed fields using role-specific schema
-   Add at least one positive test and one relevant negative/failure
    test for: Update allowed fields using role-specific schema
-   Document configuration, behavior, limitations, and manual setup for:
    Update allowed fields using role-specific schema

### Directive 0539 --- API POST /api/complaints/{id}/withdraw

-   Implement this requirement in the actual repository: Withdraw where
    policy permits
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Withdraw where policy permits
-   Persist all required data and audit events consistently for:
    Withdraw where policy permits
-   Add at least one positive test and one relevant negative/failure
    test for: Withdraw where policy permits
-   Document configuration, behavior, limitations, and manual setup for:
    Withdraw where policy permits

### Directive 0540 --- API POST /api/complaints/{id}/assign

-   Implement this requirement in the actual repository: Assign to
    officer/team
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Assign to officer/team
-   Persist all required data and audit events consistently for: Assign
    to officer/team
-   Add at least one positive test and one relevant negative/failure
    test for: Assign to officer/team
-   Document configuration, behavior, limitations, and manual setup for:
    Assign to officer/team

### Directive 0541 --- API POST /api/complaints/{id}/reassign

-   Implement this requirement in the actual repository: Reassign with
    reason and history
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Reassign with reason and history
-   Persist all required data and audit events consistently for:
    Reassign with reason and history
-   Add at least one positive test and one relevant negative/failure
    test for: Reassign with reason and history
-   Document configuration, behavior, limitations, and manual setup for:
    Reassign with reason and history

### Directive 0542 --- API POST /api/complaints/{id}/transitions

-   Implement this requirement in the actual repository: Apply validated
    workflow transition
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Apply validated workflow transition
-   Persist all required data and audit events consistently for: Apply
    validated workflow transition
-   Add at least one positive test and one relevant negative/failure
    test for: Apply validated workflow transition
-   Document configuration, behavior, limitations, and manual setup for:
    Apply validated workflow transition

### Directive 0543 --- API POST /api/complaints/{id}/resolve

-   Implement this requirement in the actual repository: Record
    resolution and evidence
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Record resolution and evidence
-   Persist all required data and audit events consistently for: Record
    resolution and evidence
-   Add at least one positive test and one relevant negative/failure
    test for: Record resolution and evidence
-   Document configuration, behavior, limitations, and manual setup for:
    Record resolution and evidence

### Directive 0544 --- API POST /api/complaints/{id}/close

-   Implement this requirement in the actual repository: Close according
    to workflow rules
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Close according to workflow rules
-   Persist all required data and audit events consistently for: Close
    according to workflow rules
-   Add at least one positive test and one relevant negative/failure
    test for: Close according to workflow rules
-   Document configuration, behavior, limitations, and manual setup for:
    Close according to workflow rules

### Directive 0545 --- API POST /api/complaints/{id}/reopen

-   Implement this requirement in the actual repository: Request or
    perform reopening
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Request or perform reopening
-   Persist all required data and audit events consistently for: Request
    or perform reopening
-   Add at least one positive test and one relevant negative/failure
    test for: Request or perform reopening
-   Document configuration, behavior, limitations, and manual setup for:
    Request or perform reopening

### Directive 0546 --- API POST /api/complaints/{id}/comments

-   Implement this requirement in the actual repository: Add permitted
    comment
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Add permitted comment
-   Persist all required data and audit events consistently for: Add
    permitted comment
-   Add at least one positive test and one relevant negative/failure
    test for: Add permitted comment
-   Document configuration, behavior, limitations, and manual setup for:
    Add permitted comment

### Directive 0547 --- API GET /api/complaints/{id}/possible-duplicates

-   Implement this requirement in the actual repository: Find safe
    duplicate candidates
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Find safe duplicate candidates
-   Persist all required data and audit events consistently for: Find
    safe duplicate candidates
-   Add at least one positive test and one relevant negative/failure
    test for: Find safe duplicate candidates
-   Document configuration, behavior, limitations, and manual setup for:
    Find safe duplicate candidates

### Directive 0548 --- API POST /api/complaints/{id}/merge

-   Implement this requirement in the actual repository: Merge verified
    duplicates with audit history
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Merge verified duplicates with audit history
-   Persist all required data and audit events consistently for: Merge
    verified duplicates with audit history
-   Add at least one positive test and one relevant negative/failure
    test for: Merge verified duplicates with audit history
-   Document configuration, behavior, limitations, and manual setup for:
    Merge verified duplicates with audit history

### Directive 0549 --- API POST /api/complaints/{id}/feedback

-   Implement this requirement in the actual repository: Submit eligible
    feedback
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Submit eligible feedback
-   Persist all required data and audit events consistently for: Submit
    eligible feedback
-   Add at least one positive test and one relevant negative/failure
    test for: Submit eligible feedback
-   Document configuration, behavior, limitations, and manual setup for:
    Submit eligible feedback

### Directive 0550 --- API GET /api/services

-   Implement this requirement in the actual repository: Search/browse
    active service directory
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Search/browse active service directory
-   Persist all required data and audit events consistently for:
    Search/browse active service directory
-   Add at least one positive test and one relevant negative/failure
    test for: Search/browse active service directory
-   Document configuration, behavior, limitations, and manual setup for:
    Search/browse active service directory

### Directive 0551 --- API GET /api/categories

-   Implement this requirement in the actual repository: List active
    categories
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List active categories
-   Persist all required data and audit events consistently for: List
    active categories
-   Add at least one positive test and one relevant negative/failure
    test for: List active categories
-   Document configuration, behavior, limitations, and manual setup for:
    List active categories

### Directive 0552 --- API POST /api/routing/suggest

-   Implement this requirement in the actual repository: Suggest a route
    without side effects
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Suggest a route without side effects
-   Persist all required data and audit events consistently for: Suggest
    a route without side effects
-   Add at least one positive test and one relevant negative/failure
    test for: Suggest a route without side effects
-   Document configuration, behavior, limitations, and manual setup for:
    Suggest a route without side effects

### Directive 0553 --- API GET /api/wards

-   Implement this requirement in the actual repository: List supported
    geographic areas
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List supported geographic areas
-   Persist all required data and audit events consistently for: List
    supported geographic areas
-   Add at least one positive test and one relevant negative/failure
    test for: List supported geographic areas
-   Document configuration, behavior, limitations, and manual setup for:
    List supported geographic areas

### Directive 0554 --- API GET /api/complaints/nearby

-   Implement this requirement in the actual repository: Find
    public-safe nearby issues
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Find public-safe nearby issues
-   Persist all required data and audit events consistently for: Find
    public-safe nearby issues
-   Add at least one positive test and one relevant negative/failure
    test for: Find public-safe nearby issues
-   Document configuration, behavior, limitations, and manual setup for:
    Find public-safe nearby issues

### Directive 0555 --- API GET /api/notifications

-   Implement this requirement in the actual repository: List current
    user's notifications
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List current user's notifications
-   Persist all required data and audit events consistently for: List
    current user's notifications
-   Add at least one positive test and one relevant negative/failure
    test for: List current user's notifications
-   Document configuration, behavior, limitations, and manual setup for:
    List current user's notifications

### Directive 0556 --- API PATCH /api/notifications/{id}/read

-   Implement this requirement in the actual repository: Mark own
    notification read
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Mark own notification read
-   Persist all required data and audit events consistently for: Mark
    own notification read
-   Add at least one positive test and one relevant negative/failure
    test for: Mark own notification read
-   Document configuration, behavior, limitations, and manual setup for:
    Mark own notification read

### Directive 0557 --- API GET /api/admin/analytics

-   Implement this requirement in the actual repository: Return
    role-scoped metrics from real records
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Return role-scoped metrics from real records
-   Persist all required data and audit events consistently for: Return
    role-scoped metrics from real records
-   Add at least one positive test and one relevant negative/failure
    test for: Return role-scoped metrics from real records
-   Document configuration, behavior, limitations, and manual setup for:
    Return role-scoped metrics from real records

### Directive 0558 --- API GET /api/admin/departments

-   Implement this requirement in the actual repository: List
    departments within permission scope
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List departments within permission scope
-   Persist all required data and audit events consistently for: List
    departments within permission scope
-   Add at least one positive test and one relevant negative/failure
    test for: List departments within permission scope
-   Document configuration, behavior, limitations, and manual setup for:
    List departments within permission scope

### Directive 0559 --- API POST /api/admin/departments

-   Implement this requirement in the actual repository: Create
    department
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create department
-   Persist all required data and audit events consistently for: Create
    department
-   Add at least one positive test and one relevant negative/failure
    test for: Create department
-   Document configuration, behavior, limitations, and manual setup for:
    Create department

### Directive 0560 --- API PATCH /api/admin/departments/{id}

-   Implement this requirement in the actual repository: Update
    department with audit
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Update department with audit
-   Persist all required data and audit events consistently for: Update
    department with audit
-   Add at least one positive test and one relevant negative/failure
    test for: Update department with audit
-   Document configuration, behavior, limitations, and manual setup for:
    Update department with audit

### Directive 0561 --- API GET /api/admin/routing-rules

-   Implement this requirement in the actual repository: List routing
    configuration
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List routing configuration
-   Persist all required data and audit events consistently for: List
    routing configuration
-   Add at least one positive test and one relevant negative/failure
    test for: List routing configuration
-   Document configuration, behavior, limitations, and manual setup for:
    List routing configuration

### Directive 0562 --- API POST /api/admin/routing-rules

-   Implement this requirement in the actual repository: Create
    validated routing rule
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create validated routing rule
-   Persist all required data and audit events consistently for: Create
    validated routing rule
-   Add at least one positive test and one relevant negative/failure
    test for: Create validated routing rule
-   Document configuration, behavior, limitations, and manual setup for:
    Create validated routing rule

### Directive 0563 --- API PATCH /api/admin/routing-rules/{id}

-   Implement this requirement in the actual repository: Update/version
    routing rule
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Update/version routing rule
-   Persist all required data and audit events consistently for:
    Update/version routing rule
-   Add at least one positive test and one relevant negative/failure
    test for: Update/version routing rule
-   Document configuration, behavior, limitations, and manual setup for:
    Update/version routing rule

### Directive 0564 --- API GET /api/admin/sla-policies

-   Implement this requirement in the actual repository: List SLA
    policies
-   Validate the inputs, permissions, state, and failure modes relevant
    to: List SLA policies
-   Persist all required data and audit events consistently for: List
    SLA policies
-   Add at least one positive test and one relevant negative/failure
    test for: List SLA policies
-   Document configuration, behavior, limitations, and manual setup for:
    List SLA policies

### Directive 0565 --- API POST /api/admin/sla-policies

-   Implement this requirement in the actual repository: Create
    validated SLA policy
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Create validated SLA policy
-   Persist all required data and audit events consistently for: Create
    validated SLA policy
-   Add at least one positive test and one relevant negative/failure
    test for: Create validated SLA policy
-   Document configuration, behavior, limitations, and manual setup for:
    Create validated SLA policy

### Directive 0566 --- API GET /health

-   Implement this requirement in the actual repository: Minimal health
    status
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Minimal health status
-   Persist all required data and audit events consistently for: Minimal
    health status
-   Add at least one positive test and one relevant negative/failure
    test for: Minimal health status
-   Document configuration, behavior, limitations, and manual setup for:
    Minimal health status

### Directive 0567 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Resident
    submits description, category suggestion, optional location, and
    optional media.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Resident submits description, category suggestion, optional
    location, and optional media.
-   Persist all required data and audit events consistently for:
    Resident submits description, category suggestion, optional
    location, and optional media.
-   Add at least one positive test and one relevant negative/failure
    test for: Resident submits description, category suggestion,
    optional location, and optional media.
-   Document configuration, behavior, limitations, and manual setup for:
    Resident submits description, category suggestion, optional
    location, and optional media.

### Directive 0568 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: API validates
    request and permissions, creates complaint and initial status
    history transactionally, and returns a tracking reference after
    persistence.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: API validates request and permissions, creates complaint and
    initial status history transactionally, and returns a tracking
    reference after persistence.
-   Persist all required data and audit events consistently for: API
    validates request and permissions, creates complaint and initial
    status history transactionally, and returns a tracking reference
    after persistence.
-   Add at least one positive test and one relevant negative/failure
    test for: API validates request and permissions, creates complaint
    and initial status history transactionally, and returns a tracking
    reference after persistence.
-   Document configuration, behavior, limitations, and manual setup for:
    API validates request and permissions, creates complaint and initial
    status history transactionally, and returns a tracking reference
    after persistence.

### Directive 0569 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Routing selects
    a configured department or fallback queue and records its decision.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Routing selects a configured department or fallback queue and
    records its decision.
-   Persist all required data and audit events consistently for: Routing
    selects a configured department or fallback queue and records its
    decision.
-   Add at least one positive test and one relevant negative/failure
    test for: Routing selects a configured department or fallback queue
    and records its decision.
-   Document configuration, behavior, limitations, and manual setup for:
    Routing selects a configured department or fallback queue and
    records its decision.

### Directive 0570 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Notification
    event is queued only after the database commit.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Notification event is queued only after the database commit.
-   Persist all required data and audit events consistently for:
    Notification event is queued only after the database commit.
-   Add at least one positive test and one relevant negative/failure
    test for: Notification event is queued only after the database
    commit.
-   Document configuration, behavior, limitations, and manual setup for:
    Notification event is queued only after the database commit.

### Directive 0571 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Authorized
    officer views and assigns the complaint.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Authorized officer views and assigns the complaint.
-   Persist all required data and audit events consistently for:
    Authorized officer views and assigns the complaint.
-   Add at least one positive test and one relevant negative/failure
    test for: Authorized officer views and assigns the complaint.
-   Document configuration, behavior, limitations, and manual setup for:
    Authorized officer views and assigns the complaint.

### Directive 0572 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Officer
    transitions it to in progress and the system records actor, reason,
    and timestamp.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Officer transitions it to in progress and the system records
    actor, reason, and timestamp.
-   Persist all required data and audit events consistently for: Officer
    transitions it to in progress and the system records actor, reason,
    and timestamp.
-   Add at least one positive test and one relevant negative/failure
    test for: Officer transitions it to in progress and the system
    records actor, reason, and timestamp.
-   Document configuration, behavior, limitations, and manual setup for:
    Officer transitions it to in progress and the system records actor,
    reason, and timestamp.

### Directive 0573 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Officer records
    resolution notes and evidence and marks the case resolved.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Officer records resolution notes and evidence and marks the case
    resolved.
-   Persist all required data and audit events consistently for: Officer
    records resolution notes and evidence and marks the case resolved.
-   Add at least one positive test and one relevant negative/failure
    test for: Officer records resolution notes and evidence and marks
    the case resolved.
-   Document configuration, behavior, limitations, and manual setup for:
    Officer records resolution notes and evidence and marks the case
    resolved.

### Directive 0574 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Resident
    retrieves actual status history and can submit feedback or request
    reopening if policy allows.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Resident retrieves actual status history and can submit feedback
    or request reopening if policy allows.
-   Persist all required data and audit events consistently for:
    Resident retrieves actual status history and can submit feedback or
    request reopening if policy allows.
-   Add at least one positive test and one relevant negative/failure
    test for: Resident retrieves actual status history and can submit
    feedback or request reopening if policy allows.
-   Document configuration, behavior, limitations, and manual setup for:
    Resident retrieves actual status history and can submit feedback or
    request reopening if policy allows.

### Directive 0575 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Analytics
    reflect the real persisted records.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Analytics reflect the real persisted records.
-   Persist all required data and audit events consistently for:
    Analytics reflect the real persisted records.
-   Add at least one positive test and one relevant negative/failure
    test for: Analytics reflect the real persisted records.
-   Document configuration, behavior, limitations, and manual setup for:
    Analytics reflect the real persisted records.

### Directive 0576 --- Workflow Resident report lifecycle

-   Implement this requirement in the actual repository: Automated tests
    verify the complete flow and all relevant permission boundaries.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Automated tests verify the complete flow and all relevant
    permission boundaries.
-   Persist all required data and audit events consistently for:
    Automated tests verify the complete flow and all relevant permission
    boundaries.
-   Add at least one positive test and one relevant negative/failure
    test for: Automated tests verify the complete flow and all relevant
    permission boundaries.
-   Document configuration, behavior, limitations, and manual setup for:
    Automated tests verify the complete flow and all relevant permission
    boundaries.

### Directive 0577 --- Workflow Unknown route

-   Implement this requirement in the actual repository: An unknown
    category is accepted if basic report validation passes.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: An unknown category is accepted if basic report validation
    passes.
-   Persist all required data and audit events consistently for: An
    unknown category is accepted if basic report validation passes.
-   Add at least one positive test and one relevant negative/failure
    test for: An unknown category is accepted if basic report validation
    passes.
-   Document configuration, behavior, limitations, and manual setup for:
    An unknown category is accepted if basic report validation passes.

### Directive 0578 --- Workflow Unknown route

-   Implement this requirement in the actual repository: The routing
    engine does not invent a department.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: The routing engine does not invent a department.
-   Persist all required data and audit events consistently for: The
    routing engine does not invent a department.
-   Add at least one positive test and one relevant negative/failure
    test for: The routing engine does not invent a department.
-   Document configuration, behavior, limitations, and manual setup for:
    The routing engine does not invent a department.

### Directive 0579 --- Workflow Unknown route

-   Implement this requirement in the actual repository: The complaint
    enters a triage queue or explicit unassigned state.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: The complaint enters a triage queue or explicit unassigned
    state.
-   Persist all required data and audit events consistently for: The
    complaint enters a triage queue or explicit unassigned state.
-   Add at least one positive test and one relevant negative/failure
    test for: The complaint enters a triage queue or explicit unassigned
    state.
-   Document configuration, behavior, limitations, and manual setup for:
    The complaint enters a triage queue or explicit unassigned state.

### Directive 0580 --- Workflow Unknown route

-   Implement this requirement in the actual repository: The resident
    receives a tracking reference.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: The resident receives a tracking reference.
-   Persist all required data and audit events consistently for: The
    resident receives a tracking reference.
-   Add at least one positive test and one relevant negative/failure
    test for: The resident receives a tracking reference.
-   Document configuration, behavior, limitations, and manual setup for:
    The resident receives a tracking reference.

### Directive 0581 --- Workflow Unknown route

-   Implement this requirement in the actual repository: An authorized
    officer corrects category/department and the change is audited.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: An authorized officer corrects category/department and the
    change is audited.
-   Persist all required data and audit events consistently for: An
    authorized officer corrects category/department and the change is
    audited.
-   Add at least one positive test and one relevant negative/failure
    test for: An authorized officer corrects category/department and the
    change is audited.
-   Document configuration, behavior, limitations, and manual setup for:
    An authorized officer corrects category/department and the change is
    audited.

### Directive 0582 --- Workflow Unknown route

-   Implement this requirement in the actual repository: Routing is
    reevaluated under configured rules.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Routing is reevaluated under configured rules.
-   Persist all required data and audit events consistently for: Routing
    is reevaluated under configured rules.
-   Add at least one positive test and one relevant negative/failure
    test for: Routing is reevaluated under configured rules.
-   Document configuration, behavior, limitations, and manual setup for:
    Routing is reevaluated under configured rules.

### Directive 0583 --- Workflow Unknown route

-   Implement this requirement in the actual repository: Tests prove the
    fallback works without AI credentials.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Tests prove the fallback works without AI credentials.
-   Persist all required data and audit events consistently for: Tests
    prove the fallback works without AI credentials.
-   Add at least one positive test and one relevant negative/failure
    test for: Tests prove the fallback works without AI credentials.
-   Document configuration, behavior, limitations, and manual setup for:
    Tests prove the fallback works without AI credentials.

### Directive 0584 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: System searches
    bounded nearby open complaints with matching or related categories.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: System searches bounded nearby open complaints with matching or
    related categories.
-   Persist all required data and audit events consistently for: System
    searches bounded nearby open complaints with matching or related
    categories.
-   Add at least one positive test and one relevant negative/failure
    test for: System searches bounded nearby open complaints with
    matching or related categories.
-   Document configuration, behavior, limitations, and manual setup for:
    System searches bounded nearby open complaints with matching or
    related categories.

### Directive 0585 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: Candidate
    output excludes private reporter data.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Candidate output excludes private reporter data.
-   Persist all required data and audit events consistently for:
    Candidate output excludes private reporter data.
-   Add at least one positive test and one relevant negative/failure
    test for: Candidate output excludes private reporter data.
-   Document configuration, behavior, limitations, and manual setup for:
    Candidate output excludes private reporter data.

### Directive 0586 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: Resident can
    continue with a distinct report or support a permitted public issue.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Resident can continue with a distinct report or support a
    permitted public issue.
-   Persist all required data and audit events consistently for:
    Resident can continue with a distinct report or support a permitted
    public issue.
-   Add at least one positive test and one relevant negative/failure
    test for: Resident can continue with a distinct report or support a
    permitted public issue.
-   Document configuration, behavior, limitations, and manual setup for:
    Resident can continue with a distinct report or support a permitted
    public issue.

### Directive 0587 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: Authorized
    staff can merge a verified duplicate with a reason.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Authorized staff can merge a verified duplicate with a reason.
-   Persist all required data and audit events consistently for:
    Authorized staff can merge a verified duplicate with a reason.
-   Add at least one positive test and one relevant negative/failure
    test for: Authorized staff can merge a verified duplicate with a
    reason.
-   Document configuration, behavior, limitations, and manual setup for:
    Authorized staff can merge a verified duplicate with a reason.

### Directive 0588 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: Merge preserves
    original records and audit history and prevents cycles.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Merge preserves original records and audit history and prevents
    cycles.
-   Persist all required data and audit events consistently for: Merge
    preserves original records and audit history and prevents cycles.
-   Add at least one positive test and one relevant negative/failure
    test for: Merge preserves original records and audit history and
    prevents cycles.
-   Document configuration, behavior, limitations, and manual setup for:
    Merge preserves original records and audit history and prevents
    cycles.

### Directive 0589 --- Workflow Duplicate report

-   Implement this requirement in the actual repository: Analytics avoid
    double-counting where the definition requires underlying issues
    rather than reports.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Analytics avoid double-counting where the definition requires
    underlying issues rather than reports.
-   Persist all required data and audit events consistently for:
    Analytics avoid double-counting where the definition requires
    underlying issues rather than reports.
-   Add at least one positive test and one relevant negative/failure
    test for: Analytics avoid double-counting where the definition
    requires underlying issues rather than reports.
-   Document configuration, behavior, limitations, and manual setup for:
    Analytics avoid double-counting where the definition requires
    underlying issues rather than reports.

### Directive 0590 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Configured SLA
    creates a due date on the server.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Configured SLA creates a due date on the server.
-   Persist all required data and audit events consistently for:
    Configured SLA creates a due date on the server.
-   Add at least one positive test and one relevant negative/failure
    test for: Configured SLA creates a due date on the server.
-   Document configuration, behavior, limitations, and manual setup for:
    Configured SLA creates a due date on the server.

### Directive 0591 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Scheduled
    worker detects approaching deadline and queues at most one reminder
    per policy window.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Scheduled worker detects approaching deadline and queues at most
    one reminder per policy window.
-   Persist all required data and audit events consistently for:
    Scheduled worker detects approaching deadline and queues at most one
    reminder per policy window.
-   Add at least one positive test and one relevant negative/failure
    test for: Scheduled worker detects approaching deadline and queues
    at most one reminder per policy window.
-   Document configuration, behavior, limitations, and manual setup for:
    Scheduled worker detects approaching deadline and queues at most one
    reminder per policy window.

### Directive 0592 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Overdue worker
    records the overdue condition and applies configured escalation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Overdue worker records the overdue condition and applies
    configured escalation.
-   Persist all required data and audit events consistently for: Overdue
    worker records the overdue condition and applies configured
    escalation.
-   Add at least one positive test and one relevant negative/failure
    test for: Overdue worker records the overdue condition and applies
    configured escalation.
-   Document configuration, behavior, limitations, and manual setup for:
    Overdue worker records the overdue condition and applies configured
    escalation.

### Directive 0593 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Escalation
    target is validated and history is recorded.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Escalation target is validated and history is recorded.
-   Persist all required data and audit events consistently for:
    Escalation target is validated and history is recorded.
-   Add at least one positive test and one relevant negative/failure
    test for: Escalation target is validated and history is recorded.
-   Document configuration, behavior, limitations, and manual setup for:
    Escalation target is validated and history is recorded.

### Directive 0594 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Notification
    failure does not erase the escalation.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Notification failure does not erase the escalation.
-   Persist all required data and audit events consistently for:
    Notification failure does not erase the escalation.
-   Add at least one positive test and one relevant negative/failure
    test for: Notification failure does not erase the escalation.
-   Document configuration, behavior, limitations, and manual setup for:
    Notification failure does not erase the escalation.

### Directive 0595 --- Workflow Overdue case

-   Implement this requirement in the actual repository: Repeated worker
    execution does not duplicate events.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Repeated worker execution does not duplicate events.
-   Persist all required data and audit events consistently for:
    Repeated worker execution does not duplicate events.
-   Add at least one positive test and one relevant negative/failure
    test for: Repeated worker execution does not duplicate events.
-   Document configuration, behavior, limitations, and manual setup for:
    Repeated worker execution does not duplicate events.

### Directive 0596 --- Workflow External provider outage

-   Implement this requirement in the actual repository: Local complaint
    persistence succeeds without external provider availability.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Local complaint persistence succeeds without external provider
    availability.
-   Persist all required data and audit events consistently for: Local
    complaint persistence succeeds without external provider
    availability.
-   Add at least one positive test and one relevant negative/failure
    test for: Local complaint persistence succeeds without external
    provider availability.
-   Document configuration, behavior, limitations, and manual setup for:
    Local complaint persistence succeeds without external provider
    availability.

### Directive 0597 --- Workflow External provider outage

-   Implement this requirement in the actual repository: Outbox/queue
    stores pending optional work.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Outbox/queue stores pending optional work.
-   Persist all required data and audit events consistently for:
    Outbox/queue stores pending optional work.
-   Add at least one positive test and one relevant negative/failure
    test for: Outbox/queue stores pending optional work.
-   Document configuration, behavior, limitations, and manual setup for:
    Outbox/queue stores pending optional work.

### Directive 0598 --- Workflow External provider outage

-   Implement this requirement in the actual repository:
    Timeout/rejection is recorded with sanitized diagnostics.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Timeout/rejection is recorded with sanitized diagnostics.
-   Persist all required data and audit events consistently for:
    Timeout/rejection is recorded with sanitized diagnostics.
-   Add at least one positive test and one relevant negative/failure
    test for: Timeout/rejection is recorded with sanitized diagnostics.
-   Document configuration, behavior, limitations, and manual setup for:
    Timeout/rejection is recorded with sanitized diagnostics.

### Directive 0599 --- Workflow External provider outage

-   Implement this requirement in the actual repository: Retry is
    bounded and idempotent.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Retry is bounded and idempotent.
-   Persist all required data and audit events consistently for: Retry
    is bounded and idempotent.
-   Add at least one positive test and one relevant negative/failure
    test for: Retry is bounded and idempotent.
-   Document configuration, behavior, limitations, and manual setup for:
    Retry is bounded and idempotent.

### Directive 0600 --- Workflow External provider outage

-   Implement this requirement in the actual repository: External case
    ID is stored only after confirmed provider response.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: External case ID is stored only after confirmed provider
    response.
-   Persist all required data and audit events consistently for:
    External case ID is stored only after confirmed provider response.
-   Add at least one positive test and one relevant negative/failure
    test for: External case ID is stored only after confirmed provider
    response.
-   Document configuration, behavior, limitations, and manual setup for:
    External case ID is stored only after confirmed provider response.

### Directive 0601 --- Workflow External provider outage

-   Implement this requirement in the actual repository: Resident
    wording distinguishes local receipt from external acknowledgement.
-   Validate the inputs, permissions, state, and failure modes relevant
    to: Resident wording distinguishes local receipt from external
    acknowledgement.
-   Persist all required data and audit events consistently for:
    Resident wording distinguishes local receipt from external
    acknowledgement.
-   Add at least one positive test and one relevant negative/failure
    test for: Resident wording distinguishes local receipt from external
    acknowledgement.
-   Document configuration, behavior, limitations, and manual setup for:
    Resident wording distinguishes local receipt from external
    acknowledgement.

## Required implementation order

1.  Inspect repository and report baseline.
2.  Configure application settings, database, migrations, health
    endpoint, and test harness.
3.  Implement identity, roles, authorization, and permission tests.
4.  Implement departments, officers, categories, services, wards, and
    repeatable seed data.
5.  Implement complaint creation, reference generation, validation,
    retrieval, filters, and idempotency.
6.  Implement status machine, status history, assignment history,
    comments, and audit trail.
7.  Implement deterministic routing, jurisdiction checks, and fallback
    queue.
8.  Implement resolution, evidence metadata, feedback, and reopening.
9.  Implement in-app notifications and reliable event handling.
10. Implement SLA deadline calculation, overdue detection, and safe
    escalation.
11. Implement duplicate candidate detection and authorized merge.
12. Implement analytics and authorized reporting from real database
    records.
13. Add optional AI, maps, email/SMS, or external municipal adapters
    only after the core lifecycle works.
14. Harden uploads, privacy, rate limits, logging, and operational
    behavior.
15. Run migrations from a clean database, seed data, full tests,
    lint/type checks, and a smoke test.
16. Fix failures, inspect the final diff, and update README/API
    documentation.
17. Report exact results and clearly identify mocked, partial, deferred,
    and unverified features.

## Final completion criteria

-   A resident can submit a report and receive a unique reference after
    real persistence.
-   A report is routed using configured rules or sent to an explicit
    fallback queue.
-   An authorized officer can assign, update, and resolve the report.
-   Status history and audit records are persisted and
    access-controlled.
-   Residents see the actual status and timeline from the database.
-   Permissions are enforced server-side and negative tests prove they
    work.
-   Notification or AI provider failure cannot lose a complaint.
-   Analytics use real records, not hardcoded values.
-   Migrations, seed scripts, documentation, and tests are repeatable.
-   Mock integrations are labelled as simulated.
-   No real-world municipal delivery or resolution is claimed without
    confirmation.
-   All remaining limitations are documented honestly.

## Final instruction

Build a reliable, secure, maintainable, backend-first civic issue
management system that directly fulfills the problem statement.
Prioritize a complete complaint lifecycle, correct department routing,
transparent updates, and testable permissions over unnecessary
complexity. Implement the repository changes, run the checks, fix
defects, and provide an accurate final implementation report.
