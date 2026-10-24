# CLAUDE CODE MASTER PROMPT

# Your City, Your Services --- Complete Redesign, Bug Fixing, Role-Based UX, Motion Design, and Verification

**Execution instruction:** Implement directly in the existing
repository. This is not a request for a plan, mockup, or new starter
project. Inspect the code, preserve working behavior, implement the
requirements, test them, and report only verified results. **Goal:**
Turn the existing civic-services website into a distinctive, accessible,
responsive, trustworthy, polished application with working role-specific
workflows. **Accuracy rule:** Never invent municipal integrations,
metrics, credentials, service contacts, status events, testimonials, or
successful resolutions. Clearly distinguish platform submission from
municipal receipt, acknowledgement, and resolution.

## 0. Mandatory execution rules

-   Inspect the repository, README, AGENTS.md, package manifests,
    lockfiles, environment examples, route definitions, API client,
    database schema, tests, and current git diff before editing.
-   Identify the real framework, runtime, package manager, styling
    system, authentication system, and existing animation libraries from
    the code rather than guessing.
-   Run baseline lint, type-check, tests, and build when possible;
    record pre-existing failures separately.
-   Create an implementation checklist, then execute it without stopping
    after writing a plan.
-   Edit the existing application rather than building a disconnected
    demo or replacing the project with a starter template.
-   Preserve unrelated user changes and do not reset or overwrite the
    working tree.
-   Do not remove working features unless a requirement explicitly
    requests removal.
-   Do not use fake success states or static buttons that pretend to
    work.
-   Do not rely on CSS hiding as the only authorization mechanism.
-   Enforce permissions through existing route and backend/API
    authorization patterns where available.
-   Use actual data where available; label illustrative data clearly.
-   Keep existing API contracts unless a change is necessary and all
    callers are updated.
-   Use tests for ranking logic, permissions, form behavior, refresh,
    export, and status changes.
-   Use the installed stack and existing conventions; avoid unnecessary
    dependencies.
-   Keep code modular, typed where supported, and maintainable.
-   Use reduced-motion fallbacks for every nonessential animation.
-   Keep all important controls usable with keyboard, touch, and
    assistive technology.
-   Ensure responsive layouts at mobile, tablet, laptop, and desktop
    widths.
-   Do not claim a test passed unless it was actually run and its output
    supports the claim.
-   At completion, list files changed, features implemented, tests run,
    actual results, and remaining blockers.

## 1. Product context and truthfulness

-   Your City, Your Services helps residents report civic issues, find
    relevant services, and track statuses recorded by the platform.
-   Staff roles review cases and may triage, assign, categorize,
    prioritize, or update cases according to their existing permissions.
-   Saving a report in the application does not by itself prove that a
    municipality received, acknowledged, or resolved it.
-   Use distinct wording for submitted, reviewed, assigned, forwarded,
    externally acknowledged, resolved, and verified resolved.
-   Keep core reporting and service discovery usable when optional AI,
    maps, notifications, or integrations are unavailable.
-   AI may assist categorization or duplicate suggestions but must not
    silently override human judgement.
-   Do not describe deterministic keyword matching as machine learning.
-   Do not describe illustrative analytics as live civic statistics.
-   Do not claim municipal partnerships, official endorsement, or
    external delivery without evidence.
-   Keep the experience useful to people outside Telugu-speaking states;
    do not hardcode a regional assumption into universal behavior.

## 2. Repository reconnaissance checklist

-   [ ] AUDIT-001: List the project tree while excluding dependency and
    build folders.
-   [ ] AUDIT-002: Identify frontend entry point and bootstrap.
-   [ ] AUDIT-003: Identify every route and route guard.
-   [ ] AUDIT-004: Identify authentication/session handling.
-   [ ] AUDIT-005: Identify role definitions and permission source of
    truth.
-   [ ] AUDIT-006: Find the current logo and all references to it.
-   [ ] AUDIT-007: Find global styles and design tokens.
-   [ ] AUDIT-008: Find typography, icon, chart, and animation
    dependencies.
-   [ ] AUDIT-009: Find public landing page sections.
-   [ ] AUDIT-010: Find sign-in page and demo-account configuration.
-   [ ] AUDIT-011: Find resident navigation and pages.
-   [ ] AUDIT-012: Find Road Officer navigation and pages.
-   [ ] AUDIT-013: Find Road Supervisor navigation and pages.
-   [ ] AUDIT-014: Find Triage Desk navigation and pages.
-   [ ] AUDIT-015: Find Municipal Admin navigation and pages.
-   [ ] AUDIT-016: Find report creation API and schema.
-   [ ] AUDIT-017: Find issue category enum and validation.
-   [ ] AUDIT-018: Find service directory data and ranking logic.
-   [ ] AUDIT-019: Find notification data fetching and read-state logic.
-   [ ] AUDIT-020: Find queue filters, sorting, pagination, and refresh
    behavior.
-   [ ] AUDIT-021: Find case detail, assignment, category, priority, and
    status mutations.
-   [ ] AUDIT-022: Find possible-duplicate logic and data model.
-   [ ] AUDIT-023: Find analytics formulas and data sources.
-   [ ] AUDIT-024: Find CSV export implementation.
-   [ ] AUDIT-025: Find localization dictionaries and Telugu strings.
-   [ ] AUDIT-026: Find image processing and EXIF/location handling.
-   [ ] AUDIT-027: Find FAQ or questions section.
-   [ ] AUDIT-028: Find Seen Something Broken section.
-   [ ] AUDIT-029: Find Your City animation and photograph section.
-   [ ] AUDIT-030: Find standalone emergency section.
-   [ ] AUDIT-031: Find copyright and demo indicator.
-   [ ] AUDIT-032: Find existing automated tests and scripts.
-   [ ] AUDIT-033: Search for dead links, placeholder handlers, TODOs,
    and console errors.
-   [ ] AUDIT-034: Search for role-specific menu leakage.
-   [ ] AUDIT-035: Search for mock metrics not labelled illustrative.
-   [ ] AUDIT-036: Search for fixed heights that clip Telugu text.
-   [ ] AUDIT-037: Record existing behavior before changing critical
    flows.

## 3. Brand and design system

-   Create a custom civic-tech visual identity that feels elegant,
    distinctive, human, and credible rather than like a generic admin
    template.
-   Use a coherent palette: deep ink/navy, warm white or light grey, one
    controlled civic accent, and semantic success/warning/danger/info
    colors.
-   Centralize colours, spacing, radii, elevation, typography, and
    motion durations in design tokens or the existing token system.
-   Use a refined display typeface for large titles and a highly
    readable UI face for controls and body copy.
-   Ensure fonts support English and Telugu or provide appropriate
    fallbacks.
-   Create a new vector-style logo communicating a city, connected civic
    services, or a helpful pathway.
-   Keep the logo legible at favicon size and on light and dark
    backgrounds.
-   Replace the old logo consistently in header, sign-in, footer,
    favicon, and metadata where applicable.
-   Do not use unreadable novelty typography, unrelated stock logos, or
    inaccurate generated lettering.
-   Use one consistent icon library; do not use emoji as the primary
    icon system.
-   Use cards only when they provide meaningful grouping or interaction.
-   Use whitespace and hierarchy instead of wrapping every item in a
    card.
-   Keep headings, page gutters, content widths, button hierarchy, input
    styling, badges, dialogs, and toasts consistent.
-   Provide visible hover, active, focus, selected, disabled, loading,
    error, and success states.
-   Never communicate status or priority through colour alone.
-   Check contrast and text size at normal desktop zoom and at 200%
    zoom.
-   Use authentic photos only when they improve understanding; prefer
    real screenshots for product flows.
-   Do not use random futuristic city images or glossy AI-generated
    stock visuals as filler.
-   Ensure long content and Telugu strings wrap without clipping.
-   Create a consistent visual language across public pages and
    authenticated staff pages.

## 4. Global motion and 3D rules

-   Use a deliberate motion language with a small set of timings and
    easing curves.
-   Use short transitions for buttons and controls and modest
    transitions for page or panel entry.
-   Use transforms and opacity where possible instead of repeatedly
    animating layout properties.
-   Do not animate every element or keep decorative objects moving
    continuously.
-   Respect prefers-reduced-motion in CSS and JavaScript.
-   For reduced motion, disable parallax, spinning, large scale
    transforms, and nonessential loops.
-   Provide static or simplified fallback visuals if WebGL or 3D
    rendering fails.
-   Lazy-load heavy scenes below the fold.
-   Clean up animation frames, timers, observers, and event listeners on
    unmount.
-   Do not run animation loops when components are off-screen.
-   Do not let canvas or 3D elements capture clicks intended for
    controls.
-   Keep important text as HTML rather than drawing it into canvas.
-   Do not make animations block sign-in, report submission, queue
    review, or CSV export.
-   Do not use 3D charts when a clear 2D chart better supports
    quantitative comparison.
-   Use 3D to communicate depth or relationships, not just to decorate
    every page.
-   Check mobile performance, layout shift, hydration, and
    unsupported-device behavior.
-   Use existing libraries if suitable and add a dependency only when
    justified.
-   Keep the product usable when optional visual assets fail to load.

## 5. Landing page and opening experience

-   [ ] LANDING-001: Redesign the opening page from the structure up; do
    not merely recolor the existing design.
-   [ ] LANDING-002: Create a strong first viewport with a clear
    civic-service promise.
-   [ ] LANDING-003: Use a concise headline explaining reporting and
    service discovery.
-   [ ] LANDING-004: Use supporting copy that does not overclaim
    external municipal delivery.
-   [ ] LANDING-005: Provide a primary CTA to report an issue or begin
    the resident flow.
-   [ ] LANDING-006: Provide a secondary CTA to find a service or
    understand the workflow.
-   [ ] LANDING-007: Use a real product screenshot, labelled mockup, or
    purposeful civic-pathway visual.
-   [ ] LANDING-008: Do not use a generic city photo as the whole design
    concept.
-   [ ] LANDING-009: Use a bespoke city-grid, connected-service-node, or
    civic-map motif where it improves the story.
-   [ ] LANDING-010: Keep CTA visible without requiring a long scroll.
-   [ ] LANDING-011: Use subtle entrance motion without delaying access
    to content.
-   [ ] LANDING-012: Do not hide core text until animation finishes.
-   [ ] LANDING-013: Create a purposeful section rhythm: hero, how it
    works, reportable issues, service discovery, accountability, CTA.
-   [ ] LANDING-014: Remove clutter and repetitive paragraphs.
-   [ ] LANDING-015: Ensure all navigation anchors point to existing
    sections.
-   [ ] LANDING-016: Remove links to sections that are removed later in
    this specification.
-   [ ] LANDING-017: Use neutral Indian urban context without implying
    the product is limited to Telugu states.
-   [ ] LANDING-018: Use responsive art direction for mobile when
    necessary.
-   [ ] LANDING-019: Keep hero text readable over any background.
-   [ ] LANDING-020: Test landing page at narrow mobile and standard
    desktop sizes.

## 6. Sign-in page, logo, and demo account selector

-   [ ] SIGNIN-001: Redesign the sign-in page completely rather than
    applying a cosmetic skin.
-   [ ] SIGNIN-002: Use the new logo and wordmark.
-   [ ] SIGNIN-003: Create a seamless composition with clear form
    hierarchy and restrained custom visuals.
-   [ ] SIGNIN-004: Use elegant motion for entrance, validation, and
    loading feedback.
-   [ ] SIGNIN-005: Keep the form immediately usable and do not wait for
    animation.
-   [ ] SIGNIN-006: Do not display all demo accounts beneath the form.
-   [ ] SIGNIN-007: Create a clearly labelled button such as "Explore
    demo accounts".
-   [ ] SIGNIN-008: Open a dropdown, popover, or dialog when the
    demo-account button is activated.
-   [ ] SIGNIN-009: List all available demo accounts inside that
    controlled surface.
-   [ ] SIGNIN-010: Group demo accounts by Resident, Road Officer, Road
    Supervisor, Triage Desk, and Municipal Admin when those accounts
    exist.
-   [ ] SIGNIN-011: Use role labels and brief descriptions.
-   [ ] SIGNIN-012: Do not automatically sign in merely because the
    dropdown opened.
-   [ ] SIGNIN-013: Use a central demo-account configuration instead of
    duplicating credentials in components.
-   [ ] SIGNIN-014: Do not expose demo passwords in production unless
    explicitly configured for demo mode.
-   [ ] SIGNIN-015: Make demo-only behavior conditional on the existing
    demo configuration.
-   [ ] SIGNIN-016: Never let demo shortcuts bypass server
    authentication or authorization.
-   [ ] SIGNIN-017: Show a clear DEMO label when demo credentials or
    demo sessions are provided.
-   [ ] SIGNIN-018: Keep dropdown/dialog keyboard accessible and close
    it with Escape when appropriate.
-   [ ] SIGNIN-019: Return focus to the trigger when the surface closes.
-   [ ] SIGNIN-020: Prevent the surface from being clipped by its parent
    or viewport.
-   [ ] SIGNIN-021: Use an accessible mobile sheet/dialog if a dropdown
    is cramped.
-   [ ] SIGNIN-022: Validate email and password with useful inline
    messages.
-   [ ] SIGNIN-023: Use correct input types, labels, autocomplete, and
    password visibility behavior.
-   [ ] SIGNIN-024: Prevent duplicate submissions while sign-in is
    pending.
-   [ ] SIGNIN-025: Keep recoverable form values after errors.
-   [ ] SIGNIN-026: Handle network failure with visible feedback.
-   [ ] SIGNIN-027: Do not reveal whether arbitrary emails exist unless
    explicitly intended.
-   [ ] SIGNIN-028: Test each demo account lands in the correct role
    experience.
-   [ ] SIGNIN-029: Test invalid credentials, keyboard flow, and
    reduced-motion mode.
-   [ ] SIGNIN-030: Remove every stale old-logo reference.

## 7. Role-aware navigation

-   Centralize role-aware navigation configuration where practical.
-   Define navigation and action permissions explicitly for each role.
-   Keep resident navigation separate from staff navigation.
-   For Road Officer, Road Supervisor, Triage Desk, and Municipal Admin,
    remove My Reports, Report an Issue, and Find a Service from
    navigation as requested.
-   Remove those resident-only items from sidebars, top navigation,
    mobile menus, and quick-action panels for the specified staff roles.
-   Do not remove resident reporting or service discovery from the
    Resident role.
-   Do not use CSS hiding as the only protection for restricted pages.
-   Validate route permissions and backend/API permissions where
    supported.
-   Handle direct unauthorized URLs safely.
-   Clear or invalidate role-specific caches when users sign out or
    switch demo accounts.
-   Display current role clearly but unobtrusively.
-   Keep sign-out functional and discoverable.
-   Ensure active navigation is clear without relying only on colour.
-   Preserve browser back and forward behavior.
-   Test each role with a clean session.

## 8. Where to go --- service relevance and ranking

-   Change ranking so the service most likely to solve the described
    problem appears first.
-   Do not put unrelated services first because of alphabetical order,
    popularity, or arbitrary featured status.
-   Use a transparent, deterministic strategy based on issue category,
    keywords, service descriptions, accepted issue types, and verified
    jurisdiction data.
-   Keep ranking logic separate from presentation components.
-   Use category and subcategory matches as strong signals.
-   Match terms against service name, description, keywords, and
    accepted issue types.
-   Use jurisdiction only when reliable coverage data exists.
-   Show a short explanation for the best match where possible.
-   Keep plausible alternatives visible when the match is uncertain.
-   Use stable tie-breaking and never random sorting.
-   Show useful suggestions when no service matches.
-   Ensure service discovery remains useful without optional AI.
-   Do not claim AI classification if the code uses keyword rules.
-   Test pothole, garbage, blocked drain, streetlight, and electrical
    queries.
-   Test Telugu and English search terms where translations exist.
-   Test ambiguous queries and no-result states.
-   Do not use unverified geolocation to exclude services.

## 9. Telugu language quality and localization

-   Audit the entire Telugu experience, not only visible landing copy.
-   Review dictionaries, hardcoded labels, placeholders, tooltips,
    validation, notifications, service descriptions, and empty states.
-   Use natural, everyday Telugu rather than literal machine translation
    or unnecessarily bureaucratic language.
-   Keep terminology consistent across public pages, resident workflows,
    notifications, and staff workflows.
-   Use a native Telugu reviewer if available for high-visibility
    phrases.
-   Do not invent official department names without verified source
    data.
-   Use explanatory fallback wording for technical terms without a
    natural equivalent.
-   Ensure language switching updates relevant content without requiring
    re-login.
-   Preserve form values when language changes.
-   Use proper Telugu font fallbacks and test common browsers.
-   Avoid fixed heights that clip Telugu glyphs or multiline labels.
-   Allow buttons and navigation items to expand for longer
    translations.
-   Localize validation and screen-reader labels where feasible.
-   Format dates, numbers, and times according to locale where
    appropriate.
-   Provide a fallback language for missing translations.
-   Never render raw translation keys to end users.
-   Do not infer the user's location from language choice.
-   Make the locale model extensible to additional Indian languages.

## 10. What can you report? and electrical issue taxonomy

-   Redesign the "What can you report?" section with a coherent palette,
    strong hierarchy, and clear selection behavior.
-   Remove awkward colour combinations and use semantic category colours
    consistently.
-   Use cards only when they have a clear action and useful description.
-   Make interactive cards truly clickable and keyboard accessible.
-   Show clear selected and focus states.
-   Do not rely on icons alone; include category names and short
    descriptions.
-   Ensure category selection passes the correct internal identifier to
    the next step.
-   Preserve category selection when navigating back.
-   Add electrical issues as a first-class category or subcategory
    consistent with the data model.
-   Include public-infrastructure examples such as damaged streetlights
    or damaged public electrical fixtures.
-   Use safe wording for exposed wires and electrical hazards; tell
    residents to keep away and contact appropriate emergency services if
    immediate danger exists.
-   Do not provide instructions for residents to repair dangerous
    electrical equipment.
-   Do not imply the platform replaces emergency services.
-   Update frontend validation, backend validation, database
    enum/constraints, and migrations where required.
-   Ensure old reports continue to render.
-   Include electrical issues in report creation, filters, staff queues,
    service matching, analytics, and localization.
-   Do not fabricate a department mapping when reliable mapping data is
    absent.
-   Add tests for electrical issue creation, filtering, and service
    recommendations.

## 11. Image display, location privacy, and geographic neutrality

-   Fix the issue where showing an uploaded image also exposes location
    unexpectedly.
-   Inspect EXIF metadata, geocoding, map labels, image components, and
    location state to identify the source.
-   Display location only when the resident intentionally supplied it or
    there is a clear, disclosed reason.
-   Do not expose EXIF GPS coordinates in public image previews or
    public image URLs.
-   Strip sensitive EXIF metadata from public derivatives where the
    media pipeline supports it.
-   Store original metadata only when necessary, authorized, and
    secured.
-   Separate image preview from the location label.
-   Show the user what location will be attached before submission.
-   Allow correction of inaccurate location before submission.
-   Provide manual location entry if geolocation is denied or
    unavailable.
-   Do not repeatedly request browser location without user action.
-   Explain why location is requested.
-   Do not infer location from language, name, role, or image
    appearance.
-   Do not hardcode Andhra Pradesh or Telangana as universal coverage.
-   Use configurable jurisdiction data for state, district,
    municipality, and ward when supported.
-   Use actual stored location labels; never invent a place name.
-   Label approximate location as approximate.
-   Do not expose exact coordinates publicly by default.
-   Ensure private report locations are not visible to other residents
    without authorization.
-   Test uploads with EXIF metadata, without EXIF metadata, and with no
    location.
-   Test manual location, permission denial, and geolocation timeout.
-   Ensure images remain usable when location is omitted.

## 12. FAQ instead of Questions

-   Rename the existing Questions section to FAQ or Frequently Asked
    Questions.
-   Make clear that the section contains answers to common questions
    rather than a question submission form.
-   Use an accessible accordion/disclosure pattern.
-   Ensure question rows open and close using mouse, keyboard, and
    touch.
-   Expose expanded state correctly to assistive technology.
-   Prevent accordion animation from clipping answers.
-   Include practical questions about reporting, service discovery,
    status, privacy, accounts, and demo limitations.
-   Ensure every answer matches actual application behavior.
-   Do not promise response times or municipal forwarding without
    evidence.
-   Clarify that platform status is not proof of external municipal
    acknowledgement.
-   Link to a contact method only if one actually exists.
-   Do not fabricate an email address or support team.
-   Keep question-submission functionality separate unless actually
    implemented.
-   Localize FAQ questions and answers.
-   Test long Telugu answers and keyboard interaction.

## 13. Seen something broken section

-   Redesign the section as a distinctive and inviting CTA.
-   Use lightweight 3D or dimensional imagery representing a civic
    issue, map pin, street grid, or repair pathway.
-   Prefer CSS/SVG dimensional effects if WebGL is unnecessary.
-   If a 3D library is used, provide a static fallback.
-   Avoid cartoonish destruction or exaggerated damage.
-   Explain that residents can submit a civic issue through the
    platform.
-   Provide a real CTA to the report flow.
-   Use role-appropriate behavior for signed-in staff and
    unauthenticated visitors.
-   Keep CTA above decorative layers and prevent 3D visuals from
    intercepting pointer events.
-   Use restrained hover response only when it works on touch devices
    too.
-   Clamp pointer movement and disable parallax for reduced-motion
    users.
-   Lazy-load the scene if it is below the fold.
-   Test WebGL failure, mobile layout, and reduced-motion mode.

## 14. Your City animation, typography, photographs, and emergency section

-   Redesign the Your City animation completely.
-   Create a bespoke city/service visual that communicates connected
    civic services rather than a generic skyline loop.
-   Use distinctive, elegant typography while retaining readability.
-   Choose typefaces with appropriate English and Telugu fallbacks.
-   Change section colours to match the new design system and maintain
    contrast.
-   Use depth, line work, layered shapes, or restrained parallax only
    when they support the story.
-   Avoid flicker, layout shift, heavy mobile animation, and hydration
    mismatches.
-   Keep headings and body copy readable independently of the animation.
-   Respect reduced-motion preference with a static composition.
-   Remove the photograph section completely.
-   Remove its navigation anchors, empty spacing, imports, and orphaned
    assets after confirming assets are unused elsewhere.
-   Remove the standalone emergency section as requested.
-   Before deleting it, identify safety-critical guidance and preserve
    that guidance contextually in electrical-hazard/report flows.
-   Do not imply the app replaces emergency services.
-   Update public navigation and section order after removals.
-   Test all landing-page anchors after removal.

## 15. Footer, copyright, and demo badge

-   Use the exact footer text "© 2026 Your City, Your Services".
-   Keep year and product name consistent across pages.
-   Highlight DEMO clearly when the environment is actually in demo
    mode.
-   Use a visible badge rather than hiding demo status in tiny text.
-   Do not show the demo badge in real production unless configured as
    demo.
-   Use environment configuration rather than inferring demo mode from a
    username.
-   Ensure footer remains readable on light and dark backgrounds.
-   Ensure footer wraps cleanly on mobile.
-   Ensure footer links work and remove links to removed sections.
-   Test the exact footer and demo label on landing and sign-in pages.

## 16. Resident: Report an Issue page

-   Redesign the page as a guided, polished, low-friction reporting
    workflow.
-   Preserve existing fields, validation rules, API contract, and
    working submission behavior.
-   Use a step indicator only if the flow has meaningful steps.
-   Group category, description, location, and optional images
    logically.
-   Clearly mark required and optional fields.
-   Use concise examples and helper text.
-   Show validation messages beside the relevant field.
-   Validate on client and server where supported.
-   Do not clear the form after recoverable validation errors.
-   Keep file picker accessible even if drag-and-drop is supported.
-   Show image previews with remove and replace controls.
-   Validate file type and size using actual server limits.
-   Show upload progress only if supported by the upload mechanism.
-   Provide retry behavior for upload failure.
-   Prevent unintended location exposure.
-   Allow manual location fallback.
-   Show a review/summary step if it reduces submission mistakes.
-   Prevent duplicate submission while a request is in flight.
-   Show success only after the backend confirms persistence.
-   Show report reference only if returned by the backend.
-   Explain that platform submission does not prove municipal receipt or
    resolution.
-   Link to the saved report only if the application supports it.
-   Keep form keyboard accessible and responsive at 320px.
-   Test valid submission, invalid input, upload failure, no location,
    electrical category, and double submit.

## 17. Resident: Find a Service page

-   Redesign the page as a purposeful discovery tool rather than plain
    text.
-   Provide a clear search field and useful placeholder.
-   Support search by service name, issue type, keywords, and
    description where data exists.
-   Use filters only when they help users narrow results.
-   Rank the best matching service first.
-   Explain the match briefly where possible.
-   Use service cards with title, description, supported issue types,
    and a clear action.
-   Every item that looks clickable must open a real detail view.
-   Use a detail route, accessible modal, or expandable panel consistent
    with existing architecture.
-   Show service name, description, issue types, and verified
    jurisdiction where available.
-   Show contact, hours, and office information only when actual
    reliable data exists.
-   Provide a next action such as reporting an issue only where
    supported.
-   Do not invent phone numbers, email addresses, hours, or service
    targets.
-   Show loading, no-results, and network-error states.
-   Preserve query and filter state when navigating back where
    appropriate.
-   Ensure service details are localized and keyboard accessible.
-   Test pothole query, electrical query, Telugu query, no match,
    open/close details, and service-fetch failure.

## 18. Resident: Notifications page

-   Redesign notifications as a polished activity centre with clear
    hierarchy.
-   Distinguish read and unread state without relying on colour alone.
-   Group by time only if it improves comprehension.
-   Show report reference and status context only when available.
-   Link to the related report only when the user has permission.
-   Implement mark-as-read only if the existing API supports it.
-   Implement mark-all-as-read only if it persists and is authorized.
-   Do not add controls that only change local appearance without
    persisting state.
-   Show empty, loading, and retryable error states.
-   Do not fabricate notifications.
-   Prevent cross-user notification leakage.
-   Ensure refresh fetches current data.
-   Use subtle motion without continuous pulsing.
-   Ensure screen readers can distinguish unread notifications.
-   Test empty, read/unread, navigation, refresh, error, and privacy
    cases.

## 19. Road Officer: queue and case detail

-   Redesign the queue around rapid scanning and operational efficiency.
-   Show actual queue counts only when backed by loaded data.
-   Provide functional status, priority, category, assignment, and date
    filters where supported.
-   Provide search by reference or text where supported.
-   Use a table on wide screens and a readable list/card layout on
    mobile.
-   Show reference, category, priority, location summary, status, and
    age where available.
-   Use text labels with semantic status/priority styling.
-   Keep sort, pagination, and search functional.
-   Show loading skeletons, empty state, error state, and retry control.
-   Make refresh perform an actual data reload, not just a spinner.
-   Preserve filters during refresh and prevent duplicate requests.
-   Show last refreshed time only if known.
-   Open the correct case when a row is selected.
-   Redesign the case header, key actions, resident-submitted details,
    images, location, assignment, and history.
-   Use real backend history; never fabricate events.
-   Provide clear controls for permitted move-forward, assignment,
    category correction, and priority correction actions.
-   Validate actions and show success only after confirmed persistence.
-   Preserve input after recoverable failures.
-   Prevent duplicate submissions and stale case state.
-   Test queue refresh, filters, case opening, role permissions, and
    each permitted mutation.

## 20. Road Supervisor: queue, triage controls, duplicates, analytics

-   Redesign the supervisor queue for triage, reassignment, and
    exception handling.
-   Keep visual consistency with the officer experience while exposing
    supervisor-only actions.
-   Use actual counts, functional filters, stable sorting, and accurate
    loading/error states.
-   Ensure refresh reloads data and preserves filter state.
-   Redesign case details and the Move It On action.
-   Redesign assignment controls and ensure changes persist.
-   Redesign category correction and priority correction controls.
-   Redesign the possible-duplicates section.
-   Distinguish possible duplicates from confirmed duplicates.
-   Show reasons for candidate matches only when supported by data.
-   Never automatically merge reports solely because a similarity score
    is high.
-   Require authorized human confirmation for merge or duplicate
    resolution.
-   Show current value, proposed value, validation, save, and cancel
    controls clearly.
-   Prevent losing meaningful unsaved edits without warning.
-   Validate assignments and allowed status transitions.
-   Use backend audit history where supported; never fabricate it in the
    client.
-   Redesign analytics as a coherent decision-support dashboard.
-   Use real aggregate data or label sample data clearly.
-   Add date-range filters only when the backend supports them and make
    them actually change data.
-   Use readable charts with titles, units, legends, and accessible
    summaries.
-   Redesign "Met the target" with target definition, observed value,
    time period, and calculation.
-   Show not configured or insufficient data instead of falsely claiming
    success.
-   Use restrained 3D/motion accents without obscuring quantitative
    comparisons.
-   Implement working CSV export with accurate headers, escaping, UTF-8,
    safe filename, filters, and permissions.
-   Handle empty export and export failure visibly.
-   Add tests for refresh, assignment, category/priority changes, target
    calculations, and CSV output.

## 21. Triage Desk: queue and case review

-   Redesign the triage queue for reviewing incoming, untriaged,
    incomplete, or potentially duplicate reports where these states
    exist.
-   Show category, priority, summary, location summary, and submission
    time where available.
-   Use actual workflow states rather than inventing status labels.
-   Make filters, sorting, and refresh functional.
-   Preserve filters during refresh.
-   Show useful loading, empty, and error states.
-   Open a redesigned case review view.
-   Redesign move-forward, assignment, category correction, and priority
    correction controls.
-   Show original resident values separately from corrected staff
    values.
-   Persist changes through the real backend.
-   Do not imply external forwarding unless confirmed by a real event.
-   Require human review for ambiguous suggestions.
-   Show duplicate candidates without automatic merge.
-   Keep actions keyboard accessible and permission-aware.
-   Prevent stale selected-case data from affecting another case.
-   Test refresh, filtering, case open, category correction, priority
    correction, assignment, and status updates.

## 22. Municipal Admin: queue, cases, analytics

-   Redesign the admin queue for oversight without overwhelming the
    user.
-   Use actual totals and functional
    status/category/priority/assignment/time filters where supported.
-   Use responsive tables or lists with clear hierarchy.
-   Make every row open the correct case.
-   Ensure refresh actually reloads data and preserves filters.
-   Redesign case header, status, category, priority, assignment,
    move-forward, and correction actions.
-   Enforce admin authorization; do not assume every action is
    permitted.
-   Use backend-derived history only.
-   Require confirmation for consequential actions.
-   Redesign admin analytics with readable charts, accurate metrics, and
    clear time filters.
-   Use real data or label illustrative values prominently.
-   Provide accessible text summaries for key charts where practical.
-   Use motion to clarify patterns, not exaggerate performance.
-   Use 3D only as a restrained accent.
-   Ensure exports respect authorization and privacy.
-   Remove resident-only navigation items from the admin role.
-   Test queue, case detail, assignment, category/priority changes,
    analytics, and export permissions.

## 23. Shared case-detail specification

-   [ ] CASE-001: Put case identity and status first.
-   [ ] CASE-002: Display reference only if it exists.
-   [ ] CASE-003: Display current workflow status.
-   [ ] CASE-004: Display category and priority with text.
-   [ ] CASE-005: Show submitted description readably.
-   [ ] CASE-006: Show uploaded images safely.
-   [ ] CASE-007: Show location according to privacy rules.
-   [ ] CASE-008: Show submission time in locale-aware format.
-   [ ] CASE-009: Show assignment only when available.
-   [ ] CASE-010: Separate resident content from staff metadata.
-   [ ] CASE-011: Use tabs only when content volume justifies them.
-   [ ] CASE-012: Keep primary actions visible without excessive
    scrolling.
-   [ ] CASE-013: Group assignment, forwarding, category, and priority
    actions coherently.
-   [ ] CASE-014: Use current-value and new-value controls for
    corrections.
-   [ ] CASE-015: Show field-level validation.
-   [ ] CASE-016: Prevent unsaved edits from being lost silently.
-   [ ] CASE-017: Confirm irreversible actions.
-   [ ] CASE-018: Use accessible dialog focus management.
-   [ ] CASE-019: Avoid browser alert() when a proper dialog exists.
-   [ ] CASE-020: Show success only after persistence.
-   [ ] CASE-021: Refresh detail data after mutation.
-   [ ] CASE-022: Update queue row after mutation.
-   [ ] CASE-023: Handle stale record conflicts.
-   [ ] CASE-024: Do not overwrite newer server data with stale local
    state.
-   [ ] CASE-025: Use real audit logs only.
-   [ ] CASE-026: Provide loading, not-found, forbidden, and retry
    states.
-   [ ] CASE-027: Ensure all fields work on mobile.
-   [ ] CASE-028: Keep wide tables contained.
-   [ ] CASE-029: Preserve queue filters on back navigation.
-   [ ] CASE-030: Test keyboard and screen-reader landmarks.

## 24. Queue data integrity and refresh

-   [ ] QUEUE-001: Refresh uses the actual data-fetching mechanism.
-   [ ] QUEUE-002: Do not toggle only a local spinner.
-   [ ] QUEUE-003: Prevent concurrent duplicate refresh requests.
-   [ ] QUEUE-004: Cancel or ignore stale responses.
-   [ ] QUEUE-005: Preserve filters, sort, page, and search during
    ordinary refresh.
-   [ ] QUEUE-006: Reset pagination only when a filter makes the page
    invalid.
-   [ ] QUEUE-007: Use stable keys for queue rows.
-   [ ] QUEUE-008: Keep selection attached to the correct case after
    sorting.
-   [ ] QUEUE-009: Do not add unsupported bulk actions.
-   [ ] QUEUE-010: Label counts by their actual scope.
-   [ ] QUEUE-011: Do not confuse system totals with current-user queue
    totals.
-   [ ] QUEUE-012: Use server-side filtering for large datasets where
    supported.
-   [ ] QUEUE-013: Use client-side filtering only for complete
    manageable datasets.
-   [ ] QUEUE-014: Normalize statuses and categories at a clear
    boundary.
-   [ ] QUEUE-015: Handle null fields safely.
-   [ ] QUEUE-016: Handle unknown enum values honestly.
-   [ ] QUEUE-017: Sort dates chronologically.
-   [ ] QUEUE-018: Sort priority using defined priority order.
-   [ ] QUEUE-019: Expose sort state accessibly.
-   [ ] QUEUE-020: Use URL query parameters only if consistent with
    project routing.
-   [ ] QUEUE-021: Update counts after mutation.
-   [ ] QUEUE-022: Preserve previous data with a stale indicator after
    failed refresh when appropriate.
-   [ ] QUEUE-023: Give refresh an accessible name.
-   [ ] QUEUE-024: Do not use a permanent spinning icon.
-   [ ] QUEUE-025: Show last-updated only when timestamp is known.
-   [ ] QUEUE-026: Test timeout and unauthorized response.
-   [ ] QUEUE-027: Test empty queue.
-   [ ] QUEUE-028: Test long descriptions and location labels.
-   [ ] QUEUE-029: Test representative pagination volume.
-   [ ] QUEUE-030: Test electrical category filtering.

## 25. Analytics and "Met the target" correctness

-   Audit every metric source, formula, unit, scope, and time range.
-   Remove or clearly label placeholders.
-   Never invent values to fill an empty chart.
-   Use a clear empty state when no data exists.
-   Ensure selected date range changes the query and all affected
    visualizations.
-   Use consistent units, date formatting, axis labels, legends, and
    semantic colours.
-   Do not rely on colour alone to interpret charts.
-   Provide text summaries or tables for key chart data where practical.
-   Keep animation brief and never imply real-time changes when data is
    static.
-   Explain target, observed value, measurement period, and calculation
    in Met the target.
-   Show not configured when target is absent.
-   Show insufficient data when a calculation cannot be supported.
-   Never mark a target met without actual data and a defined threshold.
-   Calculate time-to-assignment and time-to-resolution from valid
    timestamps.
-   Do not count unresolved cases as resolved.
-   Handle missing timestamps safely.
-   Keep denominators and sample sizes clear for rates.
-   Ensure category totals reconcile with source data where appropriate.
-   Do not double-count cases unintentionally.
-   Apply filters consistently to cards and charts.
-   Ensure analytics data scope respects each role.

## 26. CSV export repair

-   Inspect why the existing export button does not work before
    replacing it.
-   Implement an actual downloadable CSV using the current architecture.
-   Use current filters and time range if that is the intended behavior.
-   Use stable, meaningful column headers.
-   Escape commas, quotes, and line breaks correctly.
-   Preserve Unicode including Telugu text.
-   Use a safe, meaningful filename.
-   Exclude unauthorized or unnecessary private fields.
-   Protect export endpoint/action with role permissions.
-   Handle empty results clearly.
-   Handle export errors with visible feedback.
-   Do not claim success before a file is prepared/downloaded.
-   Use an existing CSV library if already present; avoid needless
    dependencies.
-   Test special characters, quotes, commas, newlines, Unicode, empty
    values, and row counts.
-   Compare exported data with the selected scope.
-   Test export separately for Road Supervisor and Municipal Admin.

## 27. Page-specific 3D/motion direction

### Landing hero

-   Use a dimensional civic map or connected service-node motif.
-   Keep title and CTA readable immediately.
-   Do not imply a live map unless it is live. \### Sign-in
-   Use a restrained logo reveal or geometric depth.
-   Keep the form stationary and usable.
-   Animate validation feedback subtly. \### Report categories
-   Use small dimensional icon treatment or selected-card lift.
-   Do not rotate every card in 3D.
-   Keep keyboard selection obvious. \### Seen something broken
-   Use a lightweight civic issue or map-pin visual.
-   Keep CTA above the scene.
-   Provide static fallback. \### Your City
-   Use bespoke city/service linework and layered depth.
-   Use elegant typography and a new palette.
-   Remove photograph section. \### Report form
-   Animate meaningful step changes only.
-   Keep validation messages stable.
-   Show upload progress only if supported. \### Service directory
-   Use subtle card and detail transitions.
-   Do not hide information behind animation.
-   Keep search results prompt. \### Notifications
-   Use small read/unread transitions.
-   Avoid continuous pulsing.
-   Keep timestamp and status readable. \### Officer queue
-   Use subtle row hover and selected states.
-   Do not use 3D table rows.
-   Prioritize scanning speed. \### Supervisor triage
-   Animate saved assignment/category feedback subtly.
-   Keep duplicate warnings calm and uncertain.
-   Keep action panels stable during save. \### Analytics
-   Use short chart entrance only after data loads.
-   Do not animate values deceptively from zero.
-   Prefer 2D charts for precise comparison.

## 28. Accessibility

-   Use semantic landmarks and one clear primary heading per page.
-   Use buttons for actions and links for navigation.
-   Make every interactive control keyboard reachable.
-   Show visible focus indicators.
-   Use logical focus order.
-   Manage focus in dropdowns, dialogs, drawers, and menus.
-   Return focus to trigger after closing dialogs.
-   Associate validation messages with inputs.
-   Do not use placeholder as the only label.
-   Give icon-only controls accessible names.
-   Provide meaningful alt text for informative images.
-   Use empty alt text for purely decorative imagery.
-   Keep essential text out of canvas.
-   Do not rely on colour alone for status.
-   Check contrast for text, controls, and focus rings.
-   Respect reduced motion.
-   Ensure content reflows at 200% zoom.
-   Prevent horizontal page overflow at narrow widths.
-   Use sufficiently large touch targets.
-   Use accessible table headers.
-   Provide text summaries for charts.
-   Explain recovery from errors.
-   Test Telugu reading order and wrapping.
-   Use plain language.
-   Avoid blaming users in validation messages.
-   Ensure critical workflows work without a mouse.
-   Run available accessibility checks.

## 29. Responsive viewport QA

### Viewport: 320px narrow mobile

-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 375px common
    mobile
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 430px large
    mobile
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 768px tablet
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 1024px laptop
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 1280px desktop
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping. \### Viewport: 1440px large
    desktop
-   No unintended horizontal overflow.
-   Primary action remains visible and clear.
-   Navigation does not overlap content.
-   Forms have readable labels and controls.
-   Dialogs and dropdowns remain within viewport.
-   Tables use responsive layout or controlled scrolling.
-   Charts do not clip labels.
-   3D effects do not block interaction.
-   Footer and demo badge wrap cleanly.
-   Telugu text wraps without clipping.

## 30. API, state, and data integrity

-   Keep API logic separate from presentational components where
    appropriate.
-   Use the existing central API client.
-   Handle credentials according to the existing security model.
-   Never expose server secrets in frontend bundles.
-   Do not swallow API errors silently.
-   Map API failures to useful user-facing messages without stack
    traces.
-   Use typed request/response models if supported.
-   Keep category and status values aligned with backend enums.
-   Handle unknown values safely.
-   Distinguish initial loading from background refresh.
-   Define rollback behavior for optimistic updates.
-   Do not show confirmed success for unconfirmed optimistic mutations.
-   Prevent stale async responses from overwriting current state.
-   Clean up requests on unmount where supported.
-   Respect pagination metadata.
-   Do not use sample arrays for production queue behavior.
-   Separate demo data from real data.
-   Never silently replace failed live data with fabricated data.
-   Create migrations using existing project conventions when schema
    changes are needed.
-   Do not rewrite already-applied migrations without justification.
-   Validate input server-side.
-   Enforce authorization server-side.
-   Apply access rules to report detail and export.
-   Avoid logging sensitive report contents unnecessarily.
-   Validate file uploads server-side where applicable.
-   Keep visible status wording aligned with actual transitions.

## 31. Security and privacy

-   Inspect authentication and authorization before altering role
    navigation.
-   Prevent privilege escalation through query parameters, local
    storage, or frontend state.
-   Validate each privileged mutation on the server.
-   Prevent residents from reading another resident's private report.
-   Ensure staff actions follow current role permissions.
-   Validate and safely serve uploaded files.
-   Escape user-generated content.
-   Protect CSV from spreadsheet formula injection where applicable.
-   Never include credentials in screenshots, logs, tests, or output.
-   Keep demo credentials out of production unless intentionally
    configured.
-   Do not make the demo dropdown a security bypass.
-   Use environment variables for secrets.
-   Do not loosen authentication for visual convenience.
-   Keep errors helpful but do not reveal infrastructure internals.
-   Protect location and image metadata consistently.
-   Do not expose exact coordinates publicly by default.
-   Ensure aggregate analytics do not expose private personal details.
-   Ensure CSV omits fields the role cannot access.
-   Use fictional data in tests.
-   Do not fabricate official municipal endorsement.

## 32. Error and empty-state matrix

### State: Initial page load

-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Background refresh
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Empty
    queue
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Empty
    notifications
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: No
    matching service
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Service
    directory fetch failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Report
    validation failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Report
    network failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Image
    upload failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Unsupported file type
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: File
    too large
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Invalid
    sign-in
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Sign-in
    server unavailable
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Expired
    session
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Unauthorized route
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Forbidden mutation
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Case
    not found
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Stale
    case data
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Assignment failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Category correction failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Priority correction failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Duplicate candidates unavailable
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Analytics has no data
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Analytics API failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Target
    not configured
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Insufficient target data
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: CSV
    empty result
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: CSV
    export failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Geolocation denied
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Geolocation unavailable
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Geocoder unavailable
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: 3D
    unsupported
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State:
    Animation asset failure
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible. \### State: Missing
    translation
-   Display an accurate, plain-language message.
-   Offer recovery where possible.
-   Do not fabricate success or data.
-   Keep the rest of the page usable where possible.

## 33. Automated test plan

### Authentication

-   [ ] TEST-AUTHENTICATION-001: Resident sign-in
-   [ ] TEST-AUTHENTICATION-002: Road Officer sign-in
-   [ ] TEST-AUTHENTICATION-003: Road Supervisor sign-in
-   [ ] TEST-AUTHENTICATION-004: Triage Desk sign-in
-   [ ] TEST-AUTHENTICATION-005: Municipal Admin sign-in
-   [ ] TEST-AUTHENTICATION-006: Invalid sign-in
-   [ ] TEST-AUTHENTICATION-007: Demo dropdown open/close
-   [ ] TEST-AUTHENTICATION-008: Demo account selection
-   [ ] TEST-AUTHENTICATION-009: Sign-out
-   [ ] TEST-AUTHENTICATION-010: Expired session
-   [ ] TEST-AUTHENTICATION-011: Role switch clears stale state \###
    Navigation
-   [ ] TEST-NAVIGATION-001: Resident sees My Reports
-   [ ] TEST-NAVIGATION-002: Resident sees Report an Issue
-   [ ] TEST-NAVIGATION-003: Resident sees Find a Service
-   [ ] TEST-NAVIGATION-004: Officer hides all three resident-only items
-   [ ] TEST-NAVIGATION-005: Supervisor hides all three resident-only
    items
-   [ ] TEST-NAVIGATION-006: Triage hides all three resident-only items
-   [ ] TEST-NAVIGATION-007: Admin hides all three resident-only items
-   [ ] TEST-NAVIGATION-008: Unauthorized direct route blocked
-   [ ] TEST-NAVIGATION-009: Unauthorized API mutation rejected \###
    Reporting
-   [ ] TEST-REPORTING-001: Valid report
-   [ ] TEST-REPORTING-002: Missing required field
-   [ ] TEST-REPORTING-003: Electrical issue
-   [ ] TEST-REPORTING-004: Optional image
-   [ ] TEST-REPORTING-005: Upload failure
-   [ ] TEST-REPORTING-006: Duplicate submission prevention
-   [ ] TEST-REPORTING-007: Optional location
-   [ ] TEST-REPORTING-008: Success waits for server confirmation
-   [ ] TEST-REPORTING-009: Reference shown only if returned \###
    Services
-   [ ] TEST-SERVICES-001: Pothole match ranks first
-   [ ] TEST-SERVICES-002: Electrical match ranks first when configured
-   [ ] TEST-SERVICES-003: Search by service name
-   [ ] TEST-SERVICES-004: Search by keyword
-   [ ] TEST-SERVICES-005: No result
-   [ ] TEST-SERVICES-006: Open service details
-   [ ] TEST-SERVICES-007: Accurate service details
-   [ ] TEST-SERVICES-008: Back navigation
-   [ ] TEST-SERVICES-009: Telugu search where available
-   [ ] TEST-SERVICES-010: Network error \### Notifications
-   [ ] TEST-NOTIFICATIONS-001: Empty state
-   [ ] TEST-NOTIFICATIONS-002: Read/unread state
-   [ ] TEST-NOTIFICATIONS-003: Read action persists when supported
-   [ ] TEST-NOTIFICATIONS-004: Open linked report
-   [ ] TEST-NOTIFICATIONS-005: Refresh reloads data
-   [ ] TEST-NOTIFICATIONS-006: Error state
-   [ ] TEST-NOTIFICATIONS-007: Cross-user privacy \### Queue and case
-   [ ] TEST-QUEUE-AND-CASE-001: Queue load
-   [ ] TEST-QUEUE-AND-CASE-002: Refresh reloads data
-   [ ] TEST-QUEUE-AND-CASE-003: Refresh preserves filters
-   [ ] TEST-QUEUE-AND-CASE-004: Queue error
-   [ ] TEST-QUEUE-AND-CASE-005: Queue empty
-   [ ] TEST-QUEUE-AND-CASE-006: Correct case opens
-   [ ] TEST-QUEUE-AND-CASE-007: Assignment persists
-   [ ] TEST-QUEUE-AND-CASE-008: Category correction persists
-   [ ] TEST-QUEUE-AND-CASE-009: Priority correction persists
-   [ ] TEST-QUEUE-AND-CASE-010: Status transition validates
-   [ ] TEST-QUEUE-AND-CASE-011: Possible duplicates do not auto-merge
-   [ ] TEST-QUEUE-AND-CASE-012: History is backend-derived
-   [ ] TEST-QUEUE-AND-CASE-013: Forbidden action blocked
-   [ ] TEST-QUEUE-AND-CASE-014: Queue updates after mutation
-   [ ] TEST-QUEUE-AND-CASE-015: Stale response rejected \### Analytics
    and CSV
-   [ ] TEST-ANALYTICS-AND-CSV-001: Data source or illustrative label
-   [ ] TEST-ANALYTICS-AND-CSV-002: Date range changes query
-   [ ] TEST-ANALYTICS-AND-CSV-003: Formula tested
-   [ ] TEST-ANALYTICS-AND-CSV-004: Missing target state
-   [ ] TEST-ANALYTICS-AND-CSV-005: Insufficient data state
-   [ ] TEST-ANALYTICS-AND-CSV-006: CSV download
-   [ ] TEST-ANALYTICS-AND-CSV-007: Correct headers
-   [ ] TEST-ANALYTICS-AND-CSV-008: Special characters escaped
-   [ ] TEST-ANALYTICS-AND-CSV-009: Unicode preserved
-   [ ] TEST-ANALYTICS-AND-CSV-010: Filters applied
-   [ ] TEST-ANALYTICS-AND-CSV-011: Role permissions enforced
-   [ ] TEST-ANALYTICS-AND-CSV-012: Empty export
-   [ ] TEST-ANALYTICS-AND-CSV-013: Visible export failure \###
    Accessibility
-   [ ] TEST-ACCESSIBILITY-001: Telugu wraps
-   [ ] TEST-ACCESSIBILITY-002: Missing translation fallback
-   [ ] TEST-ACCESSIBILITY-003: Keyboard sign-in
-   [ ] TEST-ACCESSIBILITY-004: Keyboard dropdown
-   [ ] TEST-ACCESSIBILITY-005: Keyboard FAQ
-   [ ] TEST-ACCESSIBILITY-006: Keyboard service detail
-   [ ] TEST-ACCESSIBILITY-007: Reduced-motion mode
-   [ ] TEST-ACCESSIBILITY-008: Visible focus
-   [ ] TEST-ACCESSIBILITY-009: Errors announced
-   [ ] TEST-ACCESSIBILITY-010: 320px layout

## 34. Manual QA by role

### Resident

-   [ ] RESIDENT-QA-01: Open clean session
-   [ ] RESIDENT-QA-02: Sign in with correct demo account
-   [ ] RESIDENT-QA-03: Verify role identity
-   [ ] RESIDENT-QA-04: Inspect role-specific navigation
-   [ ] RESIDENT-QA-05: Verify forbidden resident-only items are absent
    for staff
-   [ ] RESIDENT-QA-06: Open role home page
-   [ ] RESIDENT-QA-07: Inspect desktop layout
-   [ ] RESIDENT-QA-08: Inspect mobile layout
-   [ ] RESIDENT-QA-09: Trigger refresh and verify network/data update
-   [ ] RESIDENT-QA-10: Open a case if permitted
-   [ ] RESIDENT-QA-11: Verify correct case details
-   [ ] RESIDENT-QA-12: Perform an authorized change
-   [ ] RESIDENT-QA-13: Confirm success only after persistence
-   [ ] RESIDENT-QA-14: Inspect failure feedback
-   [ ] RESIDENT-QA-15: Return to queue and verify updated row
-   [ ] RESIDENT-QA-16: Check keyboard focus
-   [ ] RESIDENT-QA-17: Check reduced-motion mode
-   [ ] RESIDENT-QA-18: Sign out and verify protected data is hidden
    \### Road Officer
-   [ ] ROAD-OFFICER-QA-01: Open clean session
-   [ ] ROAD-OFFICER-QA-02: Sign in with correct demo account
-   [ ] ROAD-OFFICER-QA-03: Verify role identity
-   [ ] ROAD-OFFICER-QA-04: Inspect role-specific navigation
-   [ ] ROAD-OFFICER-QA-05: Verify forbidden resident-only items are
    absent for staff
-   [ ] ROAD-OFFICER-QA-06: Open role home page
-   [ ] ROAD-OFFICER-QA-07: Inspect desktop layout
-   [ ] ROAD-OFFICER-QA-08: Inspect mobile layout
-   [ ] ROAD-OFFICER-QA-09: Trigger refresh and verify network/data
    update
-   [ ] ROAD-OFFICER-QA-10: Open a case if permitted
-   [ ] ROAD-OFFICER-QA-11: Verify correct case details
-   [ ] ROAD-OFFICER-QA-12: Perform an authorized change
-   [ ] ROAD-OFFICER-QA-13: Confirm success only after persistence
-   [ ] ROAD-OFFICER-QA-14: Inspect failure feedback
-   [ ] ROAD-OFFICER-QA-15: Return to queue and verify updated row
-   [ ] ROAD-OFFICER-QA-16: Check keyboard focus
-   [ ] ROAD-OFFICER-QA-17: Check reduced-motion mode
-   [ ] ROAD-OFFICER-QA-18: Sign out and verify protected data is hidden
    \### Road Supervisor
-   [ ] ROAD-SUPERVISOR-QA-01: Open clean session
-   [ ] ROAD-SUPERVISOR-QA-02: Sign in with correct demo account
-   [ ] ROAD-SUPERVISOR-QA-03: Verify role identity
-   [ ] ROAD-SUPERVISOR-QA-04: Inspect role-specific navigation
-   [ ] ROAD-SUPERVISOR-QA-05: Verify forbidden resident-only items are
    absent for staff
-   [ ] ROAD-SUPERVISOR-QA-06: Open role home page
-   [ ] ROAD-SUPERVISOR-QA-07: Inspect desktop layout
-   [ ] ROAD-SUPERVISOR-QA-08: Inspect mobile layout
-   [ ] ROAD-SUPERVISOR-QA-09: Trigger refresh and verify network/data
    update
-   [ ] ROAD-SUPERVISOR-QA-10: Open a case if permitted
-   [ ] ROAD-SUPERVISOR-QA-11: Verify correct case details
-   [ ] ROAD-SUPERVISOR-QA-12: Perform an authorized change
-   [ ] ROAD-SUPERVISOR-QA-13: Confirm success only after persistence
-   [ ] ROAD-SUPERVISOR-QA-14: Inspect failure feedback
-   [ ] ROAD-SUPERVISOR-QA-15: Return to queue and verify updated row
-   [ ] ROAD-SUPERVISOR-QA-16: Check keyboard focus
-   [ ] ROAD-SUPERVISOR-QA-17: Check reduced-motion mode
-   [ ] ROAD-SUPERVISOR-QA-18: Sign out and verify protected data is
    hidden \### Triage Desk
-   [ ] TRIAGE-DESK-QA-01: Open clean session
-   [ ] TRIAGE-DESK-QA-02: Sign in with correct demo account
-   [ ] TRIAGE-DESK-QA-03: Verify role identity
-   [ ] TRIAGE-DESK-QA-04: Inspect role-specific navigation
-   [ ] TRIAGE-DESK-QA-05: Verify forbidden resident-only items are
    absent for staff
-   [ ] TRIAGE-DESK-QA-06: Open role home page
-   [ ] TRIAGE-DESK-QA-07: Inspect desktop layout
-   [ ] TRIAGE-DESK-QA-08: Inspect mobile layout
-   [ ] TRIAGE-DESK-QA-09: Trigger refresh and verify network/data
    update
-   [ ] TRIAGE-DESK-QA-10: Open a case if permitted
-   [ ] TRIAGE-DESK-QA-11: Verify correct case details
-   [ ] TRIAGE-DESK-QA-12: Perform an authorized change
-   [ ] TRIAGE-DESK-QA-13: Confirm success only after persistence
-   [ ] TRIAGE-DESK-QA-14: Inspect failure feedback
-   [ ] TRIAGE-DESK-QA-15: Return to queue and verify updated row
-   [ ] TRIAGE-DESK-QA-16: Check keyboard focus
-   [ ] TRIAGE-DESK-QA-17: Check reduced-motion mode
-   [ ] TRIAGE-DESK-QA-18: Sign out and verify protected data is hidden
    \### Municipal Admin
-   [ ] MUNICIPAL-ADMIN-QA-01: Open clean session
-   [ ] MUNICIPAL-ADMIN-QA-02: Sign in with correct demo account
-   [ ] MUNICIPAL-ADMIN-QA-03: Verify role identity
-   [ ] MUNICIPAL-ADMIN-QA-04: Inspect role-specific navigation
-   [ ] MUNICIPAL-ADMIN-QA-05: Verify forbidden resident-only items are
    absent for staff
-   [ ] MUNICIPAL-ADMIN-QA-06: Open role home page
-   [ ] MUNICIPAL-ADMIN-QA-07: Inspect desktop layout
-   [ ] MUNICIPAL-ADMIN-QA-08: Inspect mobile layout
-   [ ] MUNICIPAL-ADMIN-QA-09: Trigger refresh and verify network/data
    update
-   [ ] MUNICIPAL-ADMIN-QA-10: Open a case if permitted
-   [ ] MUNICIPAL-ADMIN-QA-11: Verify correct case details
-   [ ] MUNICIPAL-ADMIN-QA-12: Perform an authorized change
-   [ ] MUNICIPAL-ADMIN-QA-13: Confirm success only after persistence
-   [ ] MUNICIPAL-ADMIN-QA-14: Inspect failure feedback
-   [ ] MUNICIPAL-ADMIN-QA-15: Return to queue and verify updated row
-   [ ] MUNICIPAL-ADMIN-QA-16: Check keyboard focus
-   [ ] MUNICIPAL-ADMIN-QA-17: Check reduced-motion mode
-   [ ] MUNICIPAL-ADMIN-QA-18: Sign out and verify protected data is
    hidden

## 35. Performance and runtime quality

-   Run production build and resolve new errors.
-   Run lint and resolve newly introduced errors.
-   Run type-check and resolve newly introduced errors.
-   Run unit and integration tests.
-   Inspect browser console.
-   Inspect failed network requests.
-   Ensure loading indicators terminate correctly.
-   Lazy-load below-fold 3D scenes.
-   Reserve image dimensions to avoid layout shift.
-   Optimize large assets using existing tools.
-   Clean up animation loops and listeners.
-   Prevent refresh from issuing overlapping requests.
-   Avoid unnecessary chart rerenders.
-   Keep sign-in responsive during animation.
-   Keep report submission responsive during upload.
-   Keep queues responsive with representative data.
-   Avoid freezing the UI during CSV export.
-   Document any unfixable environment limitation.

## 36. Implementation sequence

-   [ ] PHASE-01: Repository audit and baseline checks
-   [ ] PHASE-02: Role and permission audit
-   [ ] PHASE-03: Design tokens and shared primitives
-   [ ] PHASE-04: New logo and favicon
-   [ ] PHASE-05: Landing page redesign
-   [ ] PHASE-06: Sign-in and demo account dropdown
-   [ ] PHASE-07: FAQ and public content cleanup
-   [ ] PHASE-08: Issue taxonomy and electrical category
-   [ ] PHASE-09: Location privacy and image metadata
-   [ ] PHASE-10: Service ranking
-   [ ] PHASE-11: Resident report form
-   [ ] PHASE-12: Resident service discovery
-   [ ] PHASE-13: Resident notifications
-   [ ] PHASE-14: Shared queue refresh mechanism
-   [ ] PHASE-15: Shared case detail components
-   [ ] PHASE-16: Road Officer workflow
-   [ ] PHASE-17: Road Supervisor workflow and analytics
-   [ ] PHASE-18: Triage Desk workflow
-   [ ] PHASE-19: Municipal Admin workflow and analytics
-   [ ] PHASE-20: CSV export
-   [ ] PHASE-21: 3D and motion with fallbacks
-   [ ] PHASE-22: Telugu localization audit
-   [ ] PHASE-23: Footer and removed-section cleanup
-   [ ] PHASE-24: Automated tests
-   [ ] PHASE-25: Manual role QA
-   [ ] PHASE-26: Build, lint, type-check, regression verification
-   [ ] PHASE-27: Final truthful report

## 37. Definition of done

-   The landing page has a coherent custom identity and clear product
    promise.
-   Sign-in is redesigned and uses the new logo.
-   Demo accounts appear inside a button-triggered accessible surface,
    not under the form.
-   The site no longer looks like a generic template.
-   Relevant service appears first in service discovery.
-   Telugu copy is natural, consistent, and unclipped.
-   What Can You Report has coherent colours and functional categories.
-   Electrical issues flow through forms, filters, services,
    localization, and analytics where applicable.
-   Image previews do not unexpectedly expose location.
-   Geographic behavior is not hardcoded to Telugu states.
-   Questions is renamed FAQ and uses a working accessible accordion.
-   Seen Something Broken has a purposeful lightweight 3D/dimensional
    visual and fallback.
-   Your City animation, typography, and colours are redesigned.
-   Photograph section is removed with no dead anchors.
-   Standalone emergency section is removed while essential safety
    guidance remains contextually.
-   Footer uses exact copyright string and clearly highlights demo mode.
-   Resident report form is polished and functional.
-   Resident service items open accurate details.
-   Resident notifications are polished and functional.
-   Officer, supervisor, triage, and admin queues/cases are redesigned.
-   Staff roles do not show resident-only navigation items.
-   Refresh controls actually reload data.
-   CSV export creates a valid file and respects permissions.
-   3D and motion respect reduced-motion and have fallbacks.
-   Mobile and desktop layouts work.
-   Critical flows are keyboard accessible.
-   Tests are added and run.
-   No fake data or false municipal-success claims were introduced.

## 38. Final response requirements

-   Summarize work by public site, resident pages, staff workflows,
    analytics, localization, and design system.
-   List major files and components changed.
-   List database migrations and API changes if any.
-   List exact commands run and actual outcomes.
-   List manual QA performed.
-   Identify tests that could not be run and why.
-   List remaining blockers and the precise missing dependency/API/data.
-   Do not say "flawless" or "production-ready" without evidence.
-   Do not claim a feature works if it is only a mockup.
-   Distinguish implemented behavior from demo-only behavior.

## 39. Traceability matrix --- all reported issues

### ISSUE-01: Sign-in

Requirement: Complete visual redesign, seamless UI, motion, new logo,
demo accounts inside button-triggered surface. - \[ \]
ISSUE-01-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-01-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-01-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-01-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-01-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-01-CHECK-06: Add a regression test where practical. \### ISSUE-02:
Opening page Requirement: Complete custom, unique, responsive
redesign. - \[ \] ISSUE-02-CHECK-01: Inspect existing implementation. -
\[ \] ISSUE-02-CHECK-02: Change the real application, not only a
mockup. - \[ \] ISSUE-02-CHECK-03: Verify functionality with data and
permissions. - \[ \] ISSUE-02-CHECK-04: Verify responsive and accessible
behavior. - \[ \] ISSUE-02-CHECK-05: Verify error, empty, and loading
states. - \[ \] ISSUE-02-CHECK-06: Add a regression test where
practical. \### ISSUE-03: Where to go Requirement: Relevant service
ranked first with transparent matching. - \[ \] ISSUE-03-CHECK-01:
Inspect existing implementation. - \[ \] ISSUE-03-CHECK-02: Change the
real application, not only a mockup. - \[ \] ISSUE-03-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-03-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-03-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-03-CHECK-06: Add
a regression test where practical. \### ISSUE-04: Telugu Requirement:
Natural, consistent, readable localization. - \[ \] ISSUE-04-CHECK-01:
Inspect existing implementation. - \[ \] ISSUE-04-CHECK-02: Change the
real application, not only a mockup. - \[ \] ISSUE-04-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-04-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-04-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-04-CHECK-06: Add
a regression test where practical. \### ISSUE-05: What can you report
Requirement: Improve colour and layout; add electrical issues. - \[ \]
ISSUE-05-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-05-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-05-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-05-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-05-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-05-CHECK-06: Add a regression test where practical. \### ISSUE-06:
Reports and queues Requirement: Improve page design and purposeful 3D
motion where appropriate. - \[ \] ISSUE-06-CHECK-01: Inspect existing
implementation. - \[ \] ISSUE-06-CHECK-02: Change the real application,
not only a mockup. - \[ \] ISSUE-06-CHECK-03: Verify functionality with
data and permissions. - \[ \] ISSUE-06-CHECK-04: Verify responsive and
accessible behavior. - \[ \] ISSUE-06-CHECK-05: Verify error, empty, and
loading states. - \[ \] ISSUE-06-CHECK-06: Add a regression test where
practical. \### ISSUE-07: Graphics Requirement: Replace bleak visuals
with meaningful, consistent design. - \[ \] ISSUE-07-CHECK-01: Inspect
existing implementation. - \[ \] ISSUE-07-CHECK-02: Change the real
application, not only a mockup. - \[ \] ISSUE-07-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-07-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-07-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-07-CHECK-06: Add
a regression test where practical. \### ISSUE-08: Images and location
Requirement: Prevent unintended location exposure; avoid geographic
bias. - \[ \] ISSUE-08-CHECK-01: Inspect existing implementation. - \[
\] ISSUE-08-CHECK-02: Change the real application, not only a mockup. -
\[ \] ISSUE-08-CHECK-03: Verify functionality with data and
permissions. - \[ \] ISSUE-08-CHECK-04: Verify responsive and accessible
behavior. - \[ \] ISSUE-08-CHECK-05: Verify error, empty, and loading
states. - \[ \] ISSUE-08-CHECK-06: Add a regression test where
practical. \### ISSUE-09: Questions section Requirement: Rename to FAQ
and implement accessible disclosures. - \[ \] ISSUE-09-CHECK-01: Inspect
existing implementation. - \[ \] ISSUE-09-CHECK-02: Change the real
application, not only a mockup. - \[ \] ISSUE-09-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-09-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-09-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-09-CHECK-06: Add
a regression test where practical. \### ISSUE-10: Issue taxonomy
Requirement: Add electrical issue category throughout relevant
workflows. - \[ \] ISSUE-10-CHECK-01: Inspect existing implementation. -
\[ \] ISSUE-10-CHECK-02: Change the real application, not only a
mockup. - \[ \] ISSUE-10-CHECK-03: Verify functionality with data and
permissions. - \[ \] ISSUE-10-CHECK-04: Verify responsive and accessible
behavior. - \[ \] ISSUE-10-CHECK-05: Verify error, empty, and loading
states. - \[ \] ISSUE-10-CHECK-06: Add a regression test where
practical. \### ISSUE-11: Seen something broken Requirement: Add
lightweight 3D/dimensional visual and real CTA. - \[ \]
ISSUE-11-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-11-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-11-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-11-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-11-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-11-CHECK-06: Add a regression test where practical. \### ISSUE-12:
Your City Requirement: Redesign animation, type, colour; remove
photograph and standalone emergency sections. - \[ \] ISSUE-12-CHECK-01:
Inspect existing implementation. - \[ \] ISSUE-12-CHECK-02: Change the
real application, not only a mockup. - \[ \] ISSUE-12-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-12-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-12-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-12-CHECK-06: Add
a regression test where practical. \### ISSUE-13: Footer Requirement:
Exact 2026 copyright and prominent demo indicator. - \[ \]
ISSUE-13-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-13-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-13-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-13-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-13-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-13-CHECK-06: Add a regression test where practical. \### ISSUE-14:
Resident report Requirement: Polished guided form; preserve real
functionality. - \[ \] ISSUE-14-CHECK-01: Inspect existing
implementation. - \[ \] ISSUE-14-CHECK-02: Change the real application,
not only a mockup. - \[ \] ISSUE-14-CHECK-03: Verify functionality with
data and permissions. - \[ \] ISSUE-14-CHECK-04: Verify responsive and
accessible behavior. - \[ \] ISSUE-14-CHECK-05: Verify error, empty, and
loading states. - \[ \] ISSUE-14-CHECK-06: Add a regression test where
practical. \### ISSUE-15: Resident services Requirement: Interactive
service details with accurate information. - \[ \] ISSUE-15-CHECK-01:
Inspect existing implementation. - \[ \] ISSUE-15-CHECK-02: Change the
real application, not only a mockup. - \[ \] ISSUE-15-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-15-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-15-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-15-CHECK-06: Add
a regression test where practical. \### ISSUE-16: Resident notifications
Requirement: Substantial UI redesign with functional states. - \[ \]
ISSUE-16-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-16-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-16-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-16-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-16-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-16-CHECK-06: Add a regression test where practical. \### ISSUE-17:
Road Officer Requirement: Redesign case and queue; remove resident-only
navigation. - \[ \] ISSUE-17-CHECK-01: Inspect existing
implementation. - \[ \] ISSUE-17-CHECK-02: Change the real application,
not only a mockup. - \[ \] ISSUE-17-CHECK-03: Verify functionality with
data and permissions. - \[ \] ISSUE-17-CHECK-04: Verify responsive and
accessible behavior. - \[ \] ISSUE-17-CHECK-05: Verify error, empty, and
loading states. - \[ \] ISSUE-17-CHECK-06: Add a regression test where
practical. \### ISSUE-18: Road Supervisor Requirement: Redesign queue,
case actions, duplicates, analytics, target, CSV, refresh. - \[ \]
ISSUE-18-CHECK-01: Inspect existing implementation. - \[ \]
ISSUE-18-CHECK-02: Change the real application, not only a mockup. - \[
\] ISSUE-18-CHECK-03: Verify functionality with data and permissions. -
\[ \] ISSUE-18-CHECK-04: Verify responsive and accessible behavior. - \[
\] ISSUE-18-CHECK-05: Verify error, empty, and loading states. - \[ \]
ISSUE-18-CHECK-06: Add a regression test where practical. \### ISSUE-19:
Triage Desk Requirement: Redesign queue and case actions; fix refresh;
remove resident-only navigation. - \[ \] ISSUE-19-CHECK-01: Inspect
existing implementation. - \[ \] ISSUE-19-CHECK-02: Change the real
application, not only a mockup. - \[ \] ISSUE-19-CHECK-03: Verify
functionality with data and permissions. - \[ \] ISSUE-19-CHECK-04:
Verify responsive and accessible behavior. - \[ \] ISSUE-19-CHECK-05:
Verify error, empty, and loading states. - \[ \] ISSUE-19-CHECK-06: Add
a regression test where practical. \### ISSUE-20: Municipal Admin
Requirement: Redesign queue, case actions, analytics; remove
resident-only navigation. - \[ \] ISSUE-20-CHECK-01: Inspect existing
implementation. - \[ \] ISSUE-20-CHECK-02: Change the real application,
not only a mockup. - \[ \] ISSUE-20-CHECK-03: Verify functionality with
data and permissions. - \[ \] ISSUE-20-CHECK-04: Verify responsive and
accessible behavior. - \[ \] ISSUE-20-CHECK-05: Verify error, empty, and
loading states. - \[ \] ISSUE-20-CHECK-06: Add a regression test where
practical.

## 40. Expanded visual acceptance checklist

-   [ ] VISUAL-001: Logo consistent in header/sign-in/footer.
-   [ ] VISUAL-002: Wordmark legible at small size.
-   [ ] VISUAL-003: Favicon uses new identity.
-   [ ] VISUAL-004: Heading hierarchy consistent.
-   [ ] VISUAL-005: Body line length comfortable.
-   [ ] VISUAL-006: Primary buttons consistent.
-   [ ] VISUAL-007: Secondary actions subordinate.
-   [ ] VISUAL-008: Destructive actions semantically styled.
-   [ ] VISUAL-009: Inputs share sizing and focus behavior.
-   [ ] VISUAL-010: Validation placement consistent.
-   [ ] VISUAL-011: Cards have consistent padding.
-   [ ] VISUAL-012: Tables have readable spacing.
-   [ ] VISUAL-013: Badges consistent.
-   [ ] VISUAL-014: Dialogs consistent.
-   [ ] VISUAL-015: Dropdowns consistent.
-   [ ] VISUAL-016: Toasts consistent.
-   [ ] VISUAL-017: Empty states consistent.
-   [ ] VISUAL-018: Skeletons match content geometry.
-   [ ] VISUAL-019: Error distinct from empty.
-   [ ] VISUAL-020: Success distinct from info.
-   [ ] VISUAL-021: Page gutters consistent.
-   [ ] VISUAL-022: Content widths consistent.
-   [ ] VISUAL-023: Responsive breakpoints stable.
-   [ ] VISUAL-024: Contrast adequate.
-   [ ] VISUAL-025: Images preserve aspect ratio.
-   [ ] VISUAL-026: Alt text meaningful.
-   [ ] VISUAL-027: Decorations do not overlap text.
-   [ ] VISUAL-028: Motion timing consistent.
-   [ ] VISUAL-029: Reduced-motion fallback exists.
-   [ ] VISUAL-030: Hover does not shift layout.
-   [ ] VISUAL-031: Focus is not clipped.
-   [ ] VISUAL-032: Selected state visible.
-   [ ] VISUAL-033: Disabled state readable.
-   [ ] VISUAL-034: Status colours consistent.
-   [ ] VISUAL-035: Priority colours consistent.
-   [ ] VISUAL-036: Category icon mapping consistent.
-   [ ] VISUAL-037: Charts have readable labels.
-   [ ] VISUAL-038: Dashboard cards aligned logically.
-   [ ] VISUAL-039: Mobile order reflects importance.
-   [ ] VISUAL-040: Footer not crowded.
-   [ ] VISUAL-041: Demo badge visible but not distracting.

## 41. Expanded functional acceptance checklist

-   [ ] FUNCTION-001: Every link has a valid destination.
-   [ ] FUNCTION-002: Every button has a real handler.
-   [ ] FUNCTION-003: Every submit handles its request.
-   [ ] FUNCTION-004: Every loading state terminates.
-   [ ] FUNCTION-005: Every failed request has visible feedback.
-   [ ] FUNCTION-006: Every success follows a successful result.
-   [ ] FUNCTION-007: Every mutation updates relevant data.
-   [ ] FUNCTION-008: Every form preserves values after recoverable
    errors.
-   [ ] FUNCTION-009: Every dropdown opens and closes.
-   [ ] FUNCTION-010: Every modal manages focus.
-   [ ] FUNCTION-011: Every tab changes content.
-   [ ] FUNCTION-012: Every accordion expands and collapses.
-   [ ] FUNCTION-013: Every filter changes results.
-   [ ] FUNCTION-014: Every sort changes order.
-   [ ] FUNCTION-015: Every pagination control works.
-   [ ] FUNCTION-016: Every search updates results.
-   [ ] FUNCTION-017: Category selection reaches backend correctly.
-   [ ] FUNCTION-018: Every service card opens details.
-   [ ] FUNCTION-019: Every notification opens correct report.
-   [ ] FUNCTION-020: Every queue row opens correct case.
-   [ ] FUNCTION-021: Assignment persists.
-   [ ] FUNCTION-022: Category correction persists.
-   [ ] FUNCTION-023: Priority correction persists.
-   [ ] FUNCTION-024: Status transitions are validated.
-   [ ] FUNCTION-025: Refresh reloads data.
-   [ ] FUNCTION-026: CSV downloads a valid file.
-   [ ] FUNCTION-027: Analytics filters change data.
-   [ ] FUNCTION-028: Language selector changes content.
-   [ ] FUNCTION-029: Sign-out ends session.
-   [ ] FUNCTION-030: Protected route validates role.
-   [ ] FUNCTION-031: Unauthorized API call is rejected.
-   [ ] FUNCTION-032: Demo flow follows configuration.
-   [ ] FUNCTION-033: Image upload validates type and size.
-   [ ] FUNCTION-034: Location label reflects actual data.
-   [ ] FUNCTION-035: Duplicate candidate is not auto-merged.
-   [ ] FUNCTION-036: Missing target is handled honestly.
-   [ ] FUNCTION-037: Empty dataset has no fabricated values.
-   [ ] FUNCTION-038: Removed sections have no dead anchors.
-   [ ] FUNCTION-039: Electrical category works across taxonomy.

## 42. Expanded content and localization acceptance checklist

-   [ ] CONTENT-001: Landing headline accurately describes product.
-   [ ] CONTENT-002: Landing copy avoids overclaiming integration.
-   [ ] CONTENT-003: Sign-in instructions clear.
-   [ ] CONTENT-004: Demo copy clearly indicates demo mode.
-   [ ] CONTENT-005: FAQ title accurate.
-   [ ] CONTENT-006: FAQ answers match behavior.
-   [ ] CONTENT-007: Report instructions concise.
-   [ ] CONTENT-008: Validation actionable.
-   [ ] CONTENT-009: Service names consistent.
-   [ ] CONTENT-010: Service descriptions accurate.
-   [ ] CONTENT-011: Service coverage not invented.
-   [ ] CONTENT-012: Category labels consistent.
-   [ ] CONTENT-013: Electrical wording safe.
-   [ ] CONTENT-014: Location instructions explain user control.
-   [ ] CONTENT-015: Image privacy wording accurate.
-   [ ] CONTENT-016: Notification copy avoids false acknowledgement.
-   [ ] CONTENT-017: Case status matches backend.
-   [ ] CONTENT-018: Assignment wording matches actual action.
-   [ ] CONTENT-019: Forwarding wording matches actual event.
-   [ ] CONTENT-020: Resolution wording matches actual event.
-   [ ] CONTENT-021: Analytics titles explain metrics.
-   [ ] CONTENT-022: Metric units explicit.
-   [ ] CONTENT-023: Target definitions clear.
-   [ ] CONTENT-024: Illustrative data labelled.
-   [ ] CONTENT-025: CSV headers meaningful.
-   [ ] CONTENT-026: Copyright string exact.
-   [ ] CONTENT-027: Demo badge tied to environment.
-   [ ] CONTENT-028: English grammar reviewed.
-   [ ] CONTENT-029: Telugu natural and consistent.
-   [ ] CONTENT-030: Telugu font fallback works.
-   [ ] CONTENT-031: Telugu labels do not clip.
-   [ ] CONTENT-032: Translation fallback sensible.
-   [ ] CONTENT-033: Raw keys never shown.
-   [ ] CONTENT-034: Date formats locale-aware.
-   [ ] CONTENT-035: Number formats locale-aware.
-   [ ] CONTENT-036: Long strings wrap.
-   [ ] CONTENT-037: Screen-reader labels localized where feasible.
-   [ ] CONTENT-038: Regional examples not universalized.
-   [ ] CONTENT-039: Safety guidance preserved contextually.

## 43. Expanded role permission checklist

-   [ ] PERMISSION-001: Resident accesses own reports.
-   [ ] PERMISSION-002: Resident cannot access another private report.
-   [ ] PERMISSION-003: Resident can submit when enabled.
-   [ ] PERMISSION-004: Resident can browse services.
-   [ ] PERMISSION-005: Resident can access own notifications.
-   [ ] PERMISSION-006: Resident cannot access staff queue.
-   [ ] PERMISSION-007: Resident cannot assign cases.
-   [ ] PERMISSION-008: Resident cannot use staff-only priority
    correction.
-   [ ] PERMISSION-009: Officer accesses permitted queue.
-   [ ] PERMISSION-010: Officer opens permitted cases.
-   [ ] PERMISSION-011: Officer lacks resident-only navigation.
-   [ ] PERMISSION-012: Officer lacks unauthorized supervisor actions.
-   [ ] PERMISSION-013: Supervisor accesses permitted queue.
-   [ ] PERMISSION-014: Supervisor accesses permitted analytics.
-   [ ] PERMISSION-015: Supervisor performs authorized triage.
-   [ ] PERMISSION-016: Supervisor lacks resident-only navigation.
-   [ ] PERMISSION-017: Triage accesses triage queue.
-   [ ] PERMISSION-018: Triage performs authorized actions.
-   [ ] PERMISSION-019: Triage lacks resident-only navigation.
-   [ ] PERMISSION-020: Admin accesses authorized queue.
-   [ ] PERMISSION-021: Admin accesses authorized analytics.
-   [ ] PERMISSION-022: Admin lacks resident-only navigation.
-   [ ] PERMISSION-023: Role comes from authenticated identity.
-   [ ] PERMISSION-024: Client role edits do not grant server access.
-   [ ] PERMISSION-025: Direct routes follow permissions.
-   [ ] PERMISSION-026: API actions follow permissions.
-   [ ] PERMISSION-027: Exports follow permissions.
-   [ ] PERMISSION-028: Case images follow permissions.
-   [ ] PERMISSION-029: Notifications follow permissions.
-   [ ] PERMISSION-030: Caches cleared on sign-out.
-   [ ] PERMISSION-031: Caches cleared on account switch.
-   [ ] PERMISSION-032: Unauthorized response handled safely.
-   [ ] PERMISSION-033: Expired session handled.
-   [ ] PERMISSION-034: Demo mode does not bypass authorization.

## 44. Expanded motion acceptance checklist

-   [ ] MOTION-001: Animation supports section message.
-   [ ] MOTION-002: Animation does not obstruct text.
-   [ ] MOTION-003: Animation does not cover buttons.
-   [ ] MOTION-004: Animation does not prevent scrolling.
-   [ ] MOTION-005: Animation causes no horizontal overflow.
-   [ ] MOTION-006: Animation causes no layout shift.
-   [ ] MOTION-007: Static fallback exists.
-   [ ] MOTION-008: Reduced-motion works.
-   [ ] MOTION-009: Off-screen loops stop.
-   [ ] MOTION-010: Listeners cleaned up.
-   [ ] MOTION-011: Observers cleaned up.
-   [ ] MOTION-012: Animation frames cleaned up.
-   [ ] MOTION-013: WebGL not required for basic use.
-   [ ] MOTION-014: Essential information remains HTML.
-   [ ] MOTION-015: Mobile performance acceptable.
-   [ ] MOTION-016: Reduced-motion tested.
-   [ ] MOTION-017: Asset failure tested.
-   [ ] MOTION-018: Perspective and lighting coherent.
-   [ ] MOTION-019: Asset sizes reasonable.
-   [ ] MOTION-020: No false live municipal-response implication.
-   [ ] MOTION-021: No false live map implication.
-   [ ] MOTION-022: No endless attention-pulsing.
-   [ ] MOTION-023: Staff tables remain calm.
-   [ ] MOTION-024: Landing motion is purposeful.
-   [ ] MOTION-025: Interactive controls remain above visual layer.
-   [ ] MOTION-026: Animation does not steal focus.
-   [ ] MOTION-027: Animation does not change reading order.
-   [ ] MOTION-028: Animation does not block form submit.
-   [ ] MOTION-029: Animation does not block sign-in.
-   [ ] MOTION-030: Animation does not block CSV export.
-   [ ] MOTION-031: Metrics are not deceptively animated.
-   [ ] MOTION-032: Status does not look final before save.
-   [ ] MOTION-033: Fallback works without WebGL.
-   [ ] MOTION-034: Dependencies compatible.
-   [ ] MOTION-035: Dependencies justified.

## 45. Expanded privacy and geography acceptance checklist

-   [ ] PRIVACY-001: EXIF GPS not exposed by default.
-   [ ] PRIVACY-002: Public image derivative strips metadata when
    supported.
-   [ ] PRIVACY-003: Location shown only when appropriate.
-   [ ] PRIVACY-004: Location source clear when helpful.
-   [ ] PRIVACY-005: Approximate location not labelled exact.
-   [ ] PRIVACY-006: Exact coordinates hidden publicly by default.
-   [ ] PRIVACY-007: Permission requested after user action.
-   [ ] PRIVACY-008: Manual location fallback exists.
-   [ ] PRIVACY-009: Location correctable before submit.
-   [ ] PRIVACY-010: Image and location are separate.
-   [ ] PRIVACY-011: Language does not imply location.
-   [ ] PRIVACY-012: Role does not imply location.
-   [ ] PRIVACY-013: Image appearance does not imply location.
-   [ ] PRIVACY-014: Jurisdiction configured rather than hardcoded.
-   [ ] PRIVACY-015: Telugu-state examples not universal.
-   [ ] PRIVACY-016: Service coverage based on verified metadata.
-   [ ] PRIVACY-017: Unknown jurisdiction handled honestly.
-   [ ] PRIVACY-018: Geocoder failure does not block unrelated flows.
-   [ ] PRIVACY-019: Geolocation timeout has fallback.
-   [ ] PRIVACY-020: Private report location protected.
-   [ ] PRIVACY-021: CSV respects location privacy.
-   [ ] PRIVACY-022: Notifications do not leak restricted location.
-   [ ] PRIVACY-023: Alt text excludes private coordinates.
-   [ ] PRIVACY-024: Test fixtures are fictional.
-   [ ] PRIVACY-025: Logs avoid unnecessary complaint content.
-   [ ] PRIVACY-026: Demo content not presented as official data.

## 46. Expanded analytics and data acceptance checklist

-   [ ] DATA-001: Every metric has a source.
-   [ ] DATA-002: Every metric has a unit.
-   [ ] DATA-003: Every metric has a time scope.
-   [ ] DATA-004: Every target has a formula.
-   [ ] DATA-005: Missing target is not success.
-   [ ] DATA-006: Insufficient data is not success.
-   [ ] DATA-007: Unresolved cases not counted as resolved.
-   [ ] DATA-008: Missing timestamps handled safely.
-   [ ] DATA-009: Counts not duplicated unintentionally.
-   [ ] DATA-010: Category totals match data scope.
-   [ ] DATA-011: Filters apply to all relevant widgets.
-   [ ] DATA-012: Empty charts do not fabricate values.
-   [ ] DATA-013: Illustrative dashboards are labelled.
-   [ ] DATA-014: Live and sample data are not silently mixed.
-   [ ] DATA-015: Refresh reloads aggregates.
-   [ ] DATA-016: CSV reflects intended scope.
-   [ ] DATA-017: CSV headers stable.
-   [ ] DATA-018: CSV quotes escaped.
-   [ ] DATA-019: CSV commas escaped.
-   [ ] DATA-020: CSV newlines escaped.
-   [ ] DATA-021: CSV preserves Unicode.
-   [ ] DATA-022: CSV avoids formula injection where applicable.
-   [ ] DATA-023: CSV excludes unauthorized fields.
-   [ ] DATA-024: CSV failures visible.
-   [ ] DATA-025: CSV success not premature.
-   [ ] DATA-026: Target status computed from actual values.
-   [ ] DATA-027: Time-range label matches query.
-   [ ] DATA-028: Chart axes meaningful.
-   [ ] DATA-029: Rates include denominator context.
-   [ ] DATA-030: Metrics not deceptively animated.
-   [ ] DATA-031: Analytics role scope enforced.

## 47. Final pre-completion checks

-   [ ] FINAL-001: Inspect git diff for unintended changes.
-   [ ] FINAL-002: Inspect diff for accidentally removed functionality.
-   [ ] FINAL-003: Inspect diff for secrets.
-   [ ] FINAL-004: Inspect diff for dead imports.
-   [ ] FINAL-005: Inspect diff for dead styles.
-   [ ] FINAL-006: Search for old logo references.
-   [ ] FINAL-007: Search for removed-section anchors.
-   [ ] FINAL-008: Check staff menus for resident item leakage.
-   [ ] FINAL-009: Test demo account selector.
-   [ ] FINAL-010: Test sign-in validation.
-   [ ] FINAL-011: Inspect landing at desktop.
-   [ ] FINAL-012: Inspect landing at mobile.
-   [ ] FINAL-013: Review Telugu copy and fonts.
-   [ ] FINAL-014: Test category selection.
-   [ ] FINAL-015: Test electrical report.
-   [ ] FINAL-016: Test image/location privacy.
-   [ ] FINAL-017: Test service ranking.
-   [ ] FINAL-018: Open service detail.
-   [ ] FINAL-019: Test notification read/unread.
-   [ ] FINAL-020: Test officer refresh.
-   [ ] FINAL-021: Test supervisor refresh.
-   [ ] FINAL-022: Test triage refresh.
-   [ ] FINAL-023: Test admin refresh.
-   [ ] FINAL-024: Inspect supervisor analytics.
-   [ ] FINAL-025: Inspect admin analytics.
-   [ ] FINAL-026: Inspect target section.
-   [ ] FINAL-027: Open and validate CSV.
-   [ ] FINAL-028: Test assignment.
-   [ ] FINAL-029: Test category correction.
-   [ ] FINAL-030: Test priority correction.
-   [ ] FINAL-031: Test duplicate candidates.
-   [ ] FINAL-032: Test reduced motion.
-   [ ] FINAL-033: Test 3D fallback.
-   [ ] FINAL-034: Run formatter if configured.
-   [ ] FINAL-035: Run linter.
-   [ ] FINAL-036: Run type-check.
-   [ ] FINAL-037: Run unit tests.
-   [ ] FINAL-038: Run integration tests if configured.
-   [ ] FINAL-039: Run production build.
-   [ ] FINAL-040: Separate pre-existing failures from new failures.
-   [ ] FINAL-041: Write truthful completion report.
-   [ ] FINAL-042: List remaining blockers.

## 48. Cross-page QA expansion

### Landing page

-   [ ] PAGE-QA-LANDING-PAGE-01: Correct design tokens.
-   [ ] PAGE-QA-LANDING-PAGE-02: Correct page title.
-   [ ] PAGE-QA-LANDING-PAGE-03: Primary action works.
-   [ ] PAGE-QA-LANDING-PAGE-04: All buttons functional.
-   [ ] PAGE-QA-LANDING-PAGE-05: Links route correctly.
-   [ ] PAGE-QA-LANDING-PAGE-06: Loading state present.
-   [ ] PAGE-QA-LANDING-PAGE-07: Empty state distinct from error.
-   [ ] PAGE-QA-LANDING-PAGE-08: API errors handled safely.
-   [ ] PAGE-QA-LANDING-PAGE-09: Retry works where available.
-   [ ] PAGE-QA-LANDING-PAGE-10: Animation failure fallback works.
-   [ ] PAGE-QA-LANDING-PAGE-11: Reduced motion works.
-   [ ] PAGE-QA-LANDING-PAGE-12: Keyboard navigation works.
-   [ ] PAGE-QA-LANDING-PAGE-13: Focus visible.
-   [ ] PAGE-QA-LANDING-PAGE-14: Long labels wrap.
-   [ ] PAGE-QA-LANDING-PAGE-15: No mobile overflow.
-   [ ] PAGE-QA-LANDING-PAGE-16: No geographic assumption.
-   [ ] PAGE-QA-LANDING-PAGE-17: Private data protected.
-   [ ] PAGE-QA-LANDING-PAGE-18: Real or labelled data only.
-   [ ] PAGE-QA-LANDING-PAGE-19: No stale mock values.
-   [ ] PAGE-QA-LANDING-PAGE-20: No stale role cache.
-   [ ] PAGE-QA-LANDING-PAGE-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-LANDING-PAGE-22: Success follows persistence.
-   [ ] PAGE-QA-LANDING-PAGE-23: Back navigation sensible.
-   [ ] PAGE-QA-LANDING-PAGE-24: Browser back/forward work.
-   [ ] PAGE-QA-LANDING-PAGE-25: Direct route load works.
-   [ ] PAGE-QA-LANDING-PAGE-26: No console errors.
-   [ ] PAGE-QA-LANDING-PAGE-27: No permanent spinner.
-   [ ] PAGE-QA-LANDING-PAGE-28: 320px layout works.
-   [ ] PAGE-QA-LANDING-PAGE-29: 768px layout works.
-   [ ] PAGE-QA-LANDING-PAGE-30: 1280px layout works.
-   [ ] PAGE-QA-LANDING-PAGE-31: Brand consistency holds. \### Sign-in
-   [ ] PAGE-QA-SIGN-IN-01: Correct design tokens.
-   [ ] PAGE-QA-SIGN-IN-02: Correct page title.
-   [ ] PAGE-QA-SIGN-IN-03: Primary action works.
-   [ ] PAGE-QA-SIGN-IN-04: All buttons functional.
-   [ ] PAGE-QA-SIGN-IN-05: Links route correctly.
-   [ ] PAGE-QA-SIGN-IN-06: Loading state present.
-   [ ] PAGE-QA-SIGN-IN-07: Empty state distinct from error.
-   [ ] PAGE-QA-SIGN-IN-08: API errors handled safely.
-   [ ] PAGE-QA-SIGN-IN-09: Retry works where available.
-   [ ] PAGE-QA-SIGN-IN-10: Animation failure fallback works.
-   [ ] PAGE-QA-SIGN-IN-11: Reduced motion works.
-   [ ] PAGE-QA-SIGN-IN-12: Keyboard navigation works.
-   [ ] PAGE-QA-SIGN-IN-13: Focus visible.
-   [ ] PAGE-QA-SIGN-IN-14: Long labels wrap.
-   [ ] PAGE-QA-SIGN-IN-15: No mobile overflow.
-   [ ] PAGE-QA-SIGN-IN-16: No geographic assumption.
-   [ ] PAGE-QA-SIGN-IN-17: Private data protected.
-   [ ] PAGE-QA-SIGN-IN-18: Real or labelled data only.
-   [ ] PAGE-QA-SIGN-IN-19: No stale mock values.
-   [ ] PAGE-QA-SIGN-IN-20: No stale role cache.
-   [ ] PAGE-QA-SIGN-IN-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-SIGN-IN-22: Success follows persistence.
-   [ ] PAGE-QA-SIGN-IN-23: Back navigation sensible.
-   [ ] PAGE-QA-SIGN-IN-24: Browser back/forward work.
-   [ ] PAGE-QA-SIGN-IN-25: Direct route load works.
-   [ ] PAGE-QA-SIGN-IN-26: No console errors.
-   [ ] PAGE-QA-SIGN-IN-27: No permanent spinner.
-   [ ] PAGE-QA-SIGN-IN-28: 320px layout works.
-   [ ] PAGE-QA-SIGN-IN-29: 768px layout works.
-   [ ] PAGE-QA-SIGN-IN-30: 1280px layout works.
-   [ ] PAGE-QA-SIGN-IN-31: Brand consistency holds. \### FAQ
-   [ ] PAGE-QA-FAQ-01: Correct design tokens.
-   [ ] PAGE-QA-FAQ-02: Correct page title.
-   [ ] PAGE-QA-FAQ-03: Primary action works.
-   [ ] PAGE-QA-FAQ-04: All buttons functional.
-   [ ] PAGE-QA-FAQ-05: Links route correctly.
-   [ ] PAGE-QA-FAQ-06: Loading state present.
-   [ ] PAGE-QA-FAQ-07: Empty state distinct from error.
-   [ ] PAGE-QA-FAQ-08: API errors handled safely.
-   [ ] PAGE-QA-FAQ-09: Retry works where available.
-   [ ] PAGE-QA-FAQ-10: Animation failure fallback works.
-   [ ] PAGE-QA-FAQ-11: Reduced motion works.
-   [ ] PAGE-QA-FAQ-12: Keyboard navigation works.
-   [ ] PAGE-QA-FAQ-13: Focus visible.
-   [ ] PAGE-QA-FAQ-14: Long labels wrap.
-   [ ] PAGE-QA-FAQ-15: No mobile overflow.
-   [ ] PAGE-QA-FAQ-16: No geographic assumption.
-   [ ] PAGE-QA-FAQ-17: Private data protected.
-   [ ] PAGE-QA-FAQ-18: Real or labelled data only.
-   [ ] PAGE-QA-FAQ-19: No stale mock values.
-   [ ] PAGE-QA-FAQ-20: No stale role cache.
-   [ ] PAGE-QA-FAQ-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-FAQ-22: Success follows persistence.
-   [ ] PAGE-QA-FAQ-23: Back navigation sensible.
-   [ ] PAGE-QA-FAQ-24: Browser back/forward work.
-   [ ] PAGE-QA-FAQ-25: Direct route load works.
-   [ ] PAGE-QA-FAQ-26: No console errors.
-   [ ] PAGE-QA-FAQ-27: No permanent spinner.
-   [ ] PAGE-QA-FAQ-28: 320px layout works.
-   [ ] PAGE-QA-FAQ-29: 768px layout works.
-   [ ] PAGE-QA-FAQ-30: 1280px layout works.
-   [ ] PAGE-QA-FAQ-31: Brand consistency holds. \### Issue categories
-   [ ] PAGE-QA-ISSUE-CATEGORIES-01: Correct design tokens.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-02: Correct page title.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-03: Primary action works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-04: All buttons functional.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-05: Links route correctly.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-06: Loading state present.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-07: Empty state distinct from error.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-08: API errors handled safely.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-09: Retry works where available.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-10: Animation failure fallback works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-11: Reduced motion works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-12: Keyboard navigation works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-13: Focus visible.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-14: Long labels wrap.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-15: No mobile overflow.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-16: No geographic assumption.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-17: Private data protected.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-18: Real or labelled data only.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-19: No stale mock values.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-20: No stale role cache.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-22: Success follows persistence.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-23: Back navigation sensible.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-24: Browser back/forward work.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-25: Direct route load works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-26: No console errors.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-27: No permanent spinner.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-28: 320px layout works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-29: 768px layout works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-30: 1280px layout works.
-   [ ] PAGE-QA-ISSUE-CATEGORIES-31: Brand consistency holds. \###
    Electrical issue form
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-01: Correct design tokens.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-02: Correct page title.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-03: Primary action works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-04: All buttons functional.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-05: Links route correctly.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-06: Loading state present.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-08: API errors handled safely.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-09: Retry works where available.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-11: Reduced motion works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-12: Keyboard navigation works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-13: Focus visible.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-14: Long labels wrap.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-15: No mobile overflow.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-16: No geographic assumption.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-17: Private data protected.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-18: Real or labelled data only.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-19: No stale mock values.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-20: No stale role cache.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-22: Success follows persistence.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-23: Back navigation sensible.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-24: Browser back/forward work.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-25: Direct route load works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-26: No console errors.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-27: No permanent spinner.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-28: 320px layout works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-29: 768px layout works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-30: 1280px layout works.
-   [ ] PAGE-QA-ELECTRICAL-ISSUE-FORM-31: Brand consistency holds. \###
    Seen something broken
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-01: Correct design tokens.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-02: Correct page title.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-03: Primary action works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-04: All buttons functional.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-05: Links route correctly.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-06: Loading state present.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-08: API errors handled safely.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-09: Retry works where available.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-11: Reduced motion works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-12: Keyboard navigation works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-13: Focus visible.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-14: Long labels wrap.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-15: No mobile overflow.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-16: No geographic assumption.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-17: Private data protected.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-18: Real or labelled data only.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-19: No stale mock values.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-20: No stale role cache.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-22: Success follows persistence.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-23: Back navigation sensible.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-24: Browser back/forward work.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-25: Direct route load works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-26: No console errors.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-27: No permanent spinner.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-28: 320px layout works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-29: 768px layout works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-30: 1280px layout works.
-   [ ] PAGE-QA-SEEN-SOMETHING-BROKEN-31: Brand consistency holds. \###
    Your City animation
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-01: Correct design tokens.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-02: Correct page title.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-03: Primary action works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-04: All buttons functional.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-05: Links route correctly.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-06: Loading state present.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-07: Empty state distinct from error.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-08: API errors handled safely.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-09: Retry works where available.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-11: Reduced motion works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-12: Keyboard navigation works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-13: Focus visible.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-14: Long labels wrap.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-15: No mobile overflow.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-16: No geographic assumption.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-17: Private data protected.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-18: Real or labelled data only.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-19: No stale mock values.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-20: No stale role cache.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-22: Success follows persistence.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-23: Back navigation sensible.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-24: Browser back/forward work.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-25: Direct route load works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-26: No console errors.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-27: No permanent spinner.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-28: 320px layout works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-29: 768px layout works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-30: 1280px layout works.
-   [ ] PAGE-QA-YOUR-CITY-ANIMATION-31: Brand consistency holds. \###
    Report an Issue
-   [ ] PAGE-QA-REPORT-AN-ISSUE-01: Correct design tokens.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-02: Correct page title.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-03: Primary action works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-04: All buttons functional.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-05: Links route correctly.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-06: Loading state present.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-07: Empty state distinct from error.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-08: API errors handled safely.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-09: Retry works where available.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-10: Animation failure fallback works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-11: Reduced motion works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-12: Keyboard navigation works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-13: Focus visible.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-14: Long labels wrap.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-15: No mobile overflow.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-16: No geographic assumption.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-17: Private data protected.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-18: Real or labelled data only.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-19: No stale mock values.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-20: No stale role cache.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-22: Success follows persistence.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-23: Back navigation sensible.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-24: Browser back/forward work.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-25: Direct route load works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-26: No console errors.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-27: No permanent spinner.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-28: 320px layout works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-29: 768px layout works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-30: 1280px layout works.
-   [ ] PAGE-QA-REPORT-AN-ISSUE-31: Brand consistency holds. \### Find a
    Service
-   [ ] PAGE-QA-FIND-A-SERVICE-01: Correct design tokens.
-   [ ] PAGE-QA-FIND-A-SERVICE-02: Correct page title.
-   [ ] PAGE-QA-FIND-A-SERVICE-03: Primary action works.
-   [ ] PAGE-QA-FIND-A-SERVICE-04: All buttons functional.
-   [ ] PAGE-QA-FIND-A-SERVICE-05: Links route correctly.
-   [ ] PAGE-QA-FIND-A-SERVICE-06: Loading state present.
-   [ ] PAGE-QA-FIND-A-SERVICE-07: Empty state distinct from error.
-   [ ] PAGE-QA-FIND-A-SERVICE-08: API errors handled safely.
-   [ ] PAGE-QA-FIND-A-SERVICE-09: Retry works where available.
-   [ ] PAGE-QA-FIND-A-SERVICE-10: Animation failure fallback works.
-   [ ] PAGE-QA-FIND-A-SERVICE-11: Reduced motion works.
-   [ ] PAGE-QA-FIND-A-SERVICE-12: Keyboard navigation works.
-   [ ] PAGE-QA-FIND-A-SERVICE-13: Focus visible.
-   [ ] PAGE-QA-FIND-A-SERVICE-14: Long labels wrap.
-   [ ] PAGE-QA-FIND-A-SERVICE-15: No mobile overflow.
-   [ ] PAGE-QA-FIND-A-SERVICE-16: No geographic assumption.
-   [ ] PAGE-QA-FIND-A-SERVICE-17: Private data protected.
-   [ ] PAGE-QA-FIND-A-SERVICE-18: Real or labelled data only.
-   [ ] PAGE-QA-FIND-A-SERVICE-19: No stale mock values.
-   [ ] PAGE-QA-FIND-A-SERVICE-20: No stale role cache.
-   [ ] PAGE-QA-FIND-A-SERVICE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-FIND-A-SERVICE-22: Success follows persistence.
-   [ ] PAGE-QA-FIND-A-SERVICE-23: Back navigation sensible.
-   [ ] PAGE-QA-FIND-A-SERVICE-24: Browser back/forward work.
-   [ ] PAGE-QA-FIND-A-SERVICE-25: Direct route load works.
-   [ ] PAGE-QA-FIND-A-SERVICE-26: No console errors.
-   [ ] PAGE-QA-FIND-A-SERVICE-27: No permanent spinner.
-   [ ] PAGE-QA-FIND-A-SERVICE-28: 320px layout works.
-   [ ] PAGE-QA-FIND-A-SERVICE-29: 768px layout works.
-   [ ] PAGE-QA-FIND-A-SERVICE-30: 1280px layout works.
-   [ ] PAGE-QA-FIND-A-SERVICE-31: Brand consistency holds. \### Service
    detail
-   [ ] PAGE-QA-SERVICE-DETAIL-01: Correct design tokens.
-   [ ] PAGE-QA-SERVICE-DETAIL-02: Correct page title.
-   [ ] PAGE-QA-SERVICE-DETAIL-03: Primary action works.
-   [ ] PAGE-QA-SERVICE-DETAIL-04: All buttons functional.
-   [ ] PAGE-QA-SERVICE-DETAIL-05: Links route correctly.
-   [ ] PAGE-QA-SERVICE-DETAIL-06: Loading state present.
-   [ ] PAGE-QA-SERVICE-DETAIL-07: Empty state distinct from error.
-   [ ] PAGE-QA-SERVICE-DETAIL-08: API errors handled safely.
-   [ ] PAGE-QA-SERVICE-DETAIL-09: Retry works where available.
-   [ ] PAGE-QA-SERVICE-DETAIL-10: Animation failure fallback works.
-   [ ] PAGE-QA-SERVICE-DETAIL-11: Reduced motion works.
-   [ ] PAGE-QA-SERVICE-DETAIL-12: Keyboard navigation works.
-   [ ] PAGE-QA-SERVICE-DETAIL-13: Focus visible.
-   [ ] PAGE-QA-SERVICE-DETAIL-14: Long labels wrap.
-   [ ] PAGE-QA-SERVICE-DETAIL-15: No mobile overflow.
-   [ ] PAGE-QA-SERVICE-DETAIL-16: No geographic assumption.
-   [ ] PAGE-QA-SERVICE-DETAIL-17: Private data protected.
-   [ ] PAGE-QA-SERVICE-DETAIL-18: Real or labelled data only.
-   [ ] PAGE-QA-SERVICE-DETAIL-19: No stale mock values.
-   [ ] PAGE-QA-SERVICE-DETAIL-20: No stale role cache.
-   [ ] PAGE-QA-SERVICE-DETAIL-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-SERVICE-DETAIL-22: Success follows persistence.
-   [ ] PAGE-QA-SERVICE-DETAIL-23: Back navigation sensible.
-   [ ] PAGE-QA-SERVICE-DETAIL-24: Browser back/forward work.
-   [ ] PAGE-QA-SERVICE-DETAIL-25: Direct route load works.
-   [ ] PAGE-QA-SERVICE-DETAIL-26: No console errors.
-   [ ] PAGE-QA-SERVICE-DETAIL-27: No permanent spinner.
-   [ ] PAGE-QA-SERVICE-DETAIL-28: 320px layout works.
-   [ ] PAGE-QA-SERVICE-DETAIL-29: 768px layout works.
-   [ ] PAGE-QA-SERVICE-DETAIL-30: 1280px layout works.
-   [ ] PAGE-QA-SERVICE-DETAIL-31: Brand consistency holds. \### My
    Reports
-   [ ] PAGE-QA-MY-REPORTS-01: Correct design tokens.
-   [ ] PAGE-QA-MY-REPORTS-02: Correct page title.
-   [ ] PAGE-QA-MY-REPORTS-03: Primary action works.
-   [ ] PAGE-QA-MY-REPORTS-04: All buttons functional.
-   [ ] PAGE-QA-MY-REPORTS-05: Links route correctly.
-   [ ] PAGE-QA-MY-REPORTS-06: Loading state present.
-   [ ] PAGE-QA-MY-REPORTS-07: Empty state distinct from error.
-   [ ] PAGE-QA-MY-REPORTS-08: API errors handled safely.
-   [ ] PAGE-QA-MY-REPORTS-09: Retry works where available.
-   [ ] PAGE-QA-MY-REPORTS-10: Animation failure fallback works.
-   [ ] PAGE-QA-MY-REPORTS-11: Reduced motion works.
-   [ ] PAGE-QA-MY-REPORTS-12: Keyboard navigation works.
-   [ ] PAGE-QA-MY-REPORTS-13: Focus visible.
-   [ ] PAGE-QA-MY-REPORTS-14: Long labels wrap.
-   [ ] PAGE-QA-MY-REPORTS-15: No mobile overflow.
-   [ ] PAGE-QA-MY-REPORTS-16: No geographic assumption.
-   [ ] PAGE-QA-MY-REPORTS-17: Private data protected.
-   [ ] PAGE-QA-MY-REPORTS-18: Real or labelled data only.
-   [ ] PAGE-QA-MY-REPORTS-19: No stale mock values.
-   [ ] PAGE-QA-MY-REPORTS-20: No stale role cache.
-   [ ] PAGE-QA-MY-REPORTS-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-MY-REPORTS-22: Success follows persistence.
-   [ ] PAGE-QA-MY-REPORTS-23: Back navigation sensible.
-   [ ] PAGE-QA-MY-REPORTS-24: Browser back/forward work.
-   [ ] PAGE-QA-MY-REPORTS-25: Direct route load works.
-   [ ] PAGE-QA-MY-REPORTS-26: No console errors.
-   [ ] PAGE-QA-MY-REPORTS-27: No permanent spinner.
-   [ ] PAGE-QA-MY-REPORTS-28: 320px layout works.
-   [ ] PAGE-QA-MY-REPORTS-29: 768px layout works.
-   [ ] PAGE-QA-MY-REPORTS-30: 1280px layout works.
-   [ ] PAGE-QA-MY-REPORTS-31: Brand consistency holds. \###
    Notifications
-   [ ] PAGE-QA-NOTIFICATIONS-01: Correct design tokens.
-   [ ] PAGE-QA-NOTIFICATIONS-02: Correct page title.
-   [ ] PAGE-QA-NOTIFICATIONS-03: Primary action works.
-   [ ] PAGE-QA-NOTIFICATIONS-04: All buttons functional.
-   [ ] PAGE-QA-NOTIFICATIONS-05: Links route correctly.
-   [ ] PAGE-QA-NOTIFICATIONS-06: Loading state present.
-   [ ] PAGE-QA-NOTIFICATIONS-07: Empty state distinct from error.
-   [ ] PAGE-QA-NOTIFICATIONS-08: API errors handled safely.
-   [ ] PAGE-QA-NOTIFICATIONS-09: Retry works where available.
-   [ ] PAGE-QA-NOTIFICATIONS-10: Animation failure fallback works.
-   [ ] PAGE-QA-NOTIFICATIONS-11: Reduced motion works.
-   [ ] PAGE-QA-NOTIFICATIONS-12: Keyboard navigation works.
-   [ ] PAGE-QA-NOTIFICATIONS-13: Focus visible.
-   [ ] PAGE-QA-NOTIFICATIONS-14: Long labels wrap.
-   [ ] PAGE-QA-NOTIFICATIONS-15: No mobile overflow.
-   [ ] PAGE-QA-NOTIFICATIONS-16: No geographic assumption.
-   [ ] PAGE-QA-NOTIFICATIONS-17: Private data protected.
-   [ ] PAGE-QA-NOTIFICATIONS-18: Real or labelled data only.
-   [ ] PAGE-QA-NOTIFICATIONS-19: No stale mock values.
-   [ ] PAGE-QA-NOTIFICATIONS-20: No stale role cache.
-   [ ] PAGE-QA-NOTIFICATIONS-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-NOTIFICATIONS-22: Success follows persistence.
-   [ ] PAGE-QA-NOTIFICATIONS-23: Back navigation sensible.
-   [ ] PAGE-QA-NOTIFICATIONS-24: Browser back/forward work.
-   [ ] PAGE-QA-NOTIFICATIONS-25: Direct route load works.
-   [ ] PAGE-QA-NOTIFICATIONS-26: No console errors.
-   [ ] PAGE-QA-NOTIFICATIONS-27: No permanent spinner.
-   [ ] PAGE-QA-NOTIFICATIONS-28: 320px layout works.
-   [ ] PAGE-QA-NOTIFICATIONS-29: 768px layout works.
-   [ ] PAGE-QA-NOTIFICATIONS-30: 1280px layout works.
-   [ ] PAGE-QA-NOTIFICATIONS-31: Brand consistency holds. \### Road
    Officer queue
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-01: Correct design tokens.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-02: Correct page title.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-03: Primary action works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-04: All buttons functional.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-05: Links route correctly.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-06: Loading state present.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-07: Empty state distinct from error.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-08: API errors handled safely.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-09: Retry works where available.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-10: Animation failure fallback works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-11: Reduced motion works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-12: Keyboard navigation works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-13: Focus visible.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-14: Long labels wrap.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-15: No mobile overflow.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-16: No geographic assumption.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-17: Private data protected.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-18: Real or labelled data only.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-19: No stale mock values.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-20: No stale role cache.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-22: Success follows persistence.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-23: Back navigation sensible.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-24: Browser back/forward work.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-25: Direct route load works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-26: No console errors.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-27: No permanent spinner.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-28: 320px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-29: 768px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-30: 1280px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-QUEUE-31: Brand consistency holds. \###
    Road Officer case detail
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-01: Correct design tokens.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-02: Correct page title.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-03: Primary action works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-04: All buttons functional.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-05: Links route correctly.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-06: Loading state present.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-08: API errors handled safely.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-09: Retry works where
    available.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-11: Reduced motion works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-12: Keyboard navigation works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-13: Focus visible.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-14: Long labels wrap.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-15: No mobile overflow.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-16: No geographic assumption.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-17: Private data protected.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-18: Real or labelled data only.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-19: No stale mock values.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-20: No stale role cache.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-22: Success follows
    persistence.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-23: Back navigation sensible.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-24: Browser back/forward work.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-25: Direct route load works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-26: No console errors.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-27: No permanent spinner.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-28: 320px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-29: 768px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-30: 1280px layout works.
-   [ ] PAGE-QA-ROAD-OFFICER-CASE-DETAIL-31: Brand consistency holds.
    \### Road Supervisor queue
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-01: Correct design tokens.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-02: Correct page title.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-03: Primary action works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-04: All buttons functional.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-05: Links route correctly.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-06: Loading state present.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-08: API errors handled safely.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-09: Retry works where available.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-11: Reduced motion works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-12: Keyboard navigation works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-13: Focus visible.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-14: Long labels wrap.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-15: No mobile overflow.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-16: No geographic assumption.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-17: Private data protected.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-18: Real or labelled data only.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-19: No stale mock values.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-20: No stale role cache.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-22: Success follows persistence.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-23: Back navigation sensible.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-24: Browser back/forward work.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-25: Direct route load works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-26: No console errors.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-27: No permanent spinner.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-28: 320px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-29: 768px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-30: 1280px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-QUEUE-31: Brand consistency holds. \###
    Road Supervisor case detail
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-01: Correct design tokens.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-02: Correct page title.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-03: Primary action works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-04: All buttons functional.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-05: Links route correctly.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-06: Loading state present.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-07: Empty state distinct
    from error.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-08: API errors handled
    safely.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-09: Retry works where
    available.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-10: Animation failure
    fallback works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-11: Reduced motion works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-12: Keyboard navigation
    works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-13: Focus visible.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-14: Long labels wrap.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-15: No mobile overflow.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-16: No geographic
    assumption.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-17: Private data protected.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-18: Real or labelled data
    only.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-19: No stale mock values.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-20: No stale role cache.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-21: Error preserves input
    when appropriate.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-22: Success follows
    persistence.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-23: Back navigation
    sensible.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-24: Browser back/forward
    work.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-25: Direct route load works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-26: No console errors.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-27: No permanent spinner.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-28: 320px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-29: 768px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-30: 1280px layout works.
-   [ ] PAGE-QA-ROAD-SUPERVISOR-CASE-DETAIL-31: Brand consistency holds.
    \### Supervisor analytics
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-01: Correct design tokens.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-02: Correct page title.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-03: Primary action works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-04: All buttons functional.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-05: Links route correctly.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-06: Loading state present.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-08: API errors handled safely.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-09: Retry works where available.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-11: Reduced motion works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-12: Keyboard navigation works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-13: Focus visible.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-14: Long labels wrap.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-15: No mobile overflow.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-16: No geographic assumption.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-17: Private data protected.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-18: Real or labelled data only.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-19: No stale mock values.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-20: No stale role cache.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-22: Success follows persistence.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-23: Back navigation sensible.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-24: Browser back/forward work.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-25: Direct route load works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-26: No console errors.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-27: No permanent spinner.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-28: 320px layout works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-29: 768px layout works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-30: 1280px layout works.
-   [ ] PAGE-QA-SUPERVISOR-ANALYTICS-31: Brand consistency holds. \###
    Triage Desk queue
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-01: Correct design tokens.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-02: Correct page title.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-03: Primary action works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-04: All buttons functional.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-05: Links route correctly.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-06: Loading state present.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-07: Empty state distinct from error.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-08: API errors handled safely.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-09: Retry works where available.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-10: Animation failure fallback works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-11: Reduced motion works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-12: Keyboard navigation works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-13: Focus visible.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-14: Long labels wrap.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-15: No mobile overflow.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-16: No geographic assumption.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-17: Private data protected.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-18: Real or labelled data only.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-19: No stale mock values.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-20: No stale role cache.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-22: Success follows persistence.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-23: Back navigation sensible.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-24: Browser back/forward work.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-25: Direct route load works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-26: No console errors.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-27: No permanent spinner.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-28: 320px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-29: 768px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-30: 1280px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-QUEUE-31: Brand consistency holds. \###
    Triage Desk case detail
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-01: Correct design tokens.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-02: Correct page title.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-03: Primary action works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-04: All buttons functional.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-05: Links route correctly.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-06: Loading state present.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-08: API errors handled safely.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-09: Retry works where available.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-11: Reduced motion works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-12: Keyboard navigation works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-13: Focus visible.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-14: Long labels wrap.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-15: No mobile overflow.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-16: No geographic assumption.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-17: Private data protected.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-18: Real or labelled data only.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-19: No stale mock values.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-20: No stale role cache.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-22: Success follows persistence.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-23: Back navigation sensible.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-24: Browser back/forward work.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-25: Direct route load works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-26: No console errors.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-27: No permanent spinner.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-28: 320px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-29: 768px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-30: 1280px layout works.
-   [ ] PAGE-QA-TRIAGE-DESK-CASE-DETAIL-31: Brand consistency holds.
    \### Municipal Admin queue
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-01: Correct design tokens.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-02: Correct page title.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-03: Primary action works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-04: All buttons functional.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-05: Links route correctly.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-06: Loading state present.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-07: Empty state distinct from
    error.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-08: API errors handled safely.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-09: Retry works where available.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-10: Animation failure fallback
    works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-11: Reduced motion works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-12: Keyboard navigation works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-13: Focus visible.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-14: Long labels wrap.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-15: No mobile overflow.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-16: No geographic assumption.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-17: Private data protected.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-18: Real or labelled data only.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-19: No stale mock values.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-20: No stale role cache.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-22: Success follows persistence.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-23: Back navigation sensible.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-24: Browser back/forward work.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-25: Direct route load works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-26: No console errors.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-27: No permanent spinner.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-28: 320px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-29: 768px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-30: 1280px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-QUEUE-31: Brand consistency holds. \###
    Municipal Admin case detail
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-01: Correct design tokens.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-02: Correct page title.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-03: Primary action works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-04: All buttons functional.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-05: Links route correctly.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-06: Loading state present.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-07: Empty state distinct
    from error.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-08: API errors handled
    safely.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-09: Retry works where
    available.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-10: Animation failure
    fallback works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-11: Reduced motion works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-12: Keyboard navigation
    works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-13: Focus visible.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-14: Long labels wrap.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-15: No mobile overflow.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-16: No geographic
    assumption.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-17: Private data protected.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-18: Real or labelled data
    only.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-19: No stale mock values.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-20: No stale role cache.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-21: Error preserves input
    when appropriate.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-22: Success follows
    persistence.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-23: Back navigation
    sensible.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-24: Browser back/forward
    work.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-25: Direct route load works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-26: No console errors.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-27: No permanent spinner.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-28: 320px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-29: 768px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-30: 1280px layout works.
-   [ ] PAGE-QA-MUNICIPAL-ADMIN-CASE-DETAIL-31: Brand consistency holds.
    \### Admin analytics
-   [ ] PAGE-QA-ADMIN-ANALYTICS-01: Correct design tokens.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-02: Correct page title.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-03: Primary action works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-04: All buttons functional.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-05: Links route correctly.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-06: Loading state present.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-07: Empty state distinct from error.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-08: API errors handled safely.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-09: Retry works where available.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-10: Animation failure fallback works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-11: Reduced motion works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-12: Keyboard navigation works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-13: Focus visible.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-14: Long labels wrap.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-15: No mobile overflow.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-16: No geographic assumption.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-17: Private data protected.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-18: Real or labelled data only.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-19: No stale mock values.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-20: No stale role cache.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-22: Success follows persistence.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-23: Back navigation sensible.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-24: Browser back/forward work.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-25: Direct route load works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-26: No console errors.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-27: No permanent spinner.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-28: 320px layout works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-29: 768px layout works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-30: 1280px layout works.
-   [ ] PAGE-QA-ADMIN-ANALYTICS-31: Brand consistency holds. \### CSV
    export
-   [ ] PAGE-QA-CSV-EXPORT-01: Correct design tokens.
-   [ ] PAGE-QA-CSV-EXPORT-02: Correct page title.
-   [ ] PAGE-QA-CSV-EXPORT-03: Primary action works.
-   [ ] PAGE-QA-CSV-EXPORT-04: All buttons functional.
-   [ ] PAGE-QA-CSV-EXPORT-05: Links route correctly.
-   [ ] PAGE-QA-CSV-EXPORT-06: Loading state present.
-   [ ] PAGE-QA-CSV-EXPORT-07: Empty state distinct from error.
-   [ ] PAGE-QA-CSV-EXPORT-08: API errors handled safely.
-   [ ] PAGE-QA-CSV-EXPORT-09: Retry works where available.
-   [ ] PAGE-QA-CSV-EXPORT-10: Animation failure fallback works.
-   [ ] PAGE-QA-CSV-EXPORT-11: Reduced motion works.
-   [ ] PAGE-QA-CSV-EXPORT-12: Keyboard navigation works.
-   [ ] PAGE-QA-CSV-EXPORT-13: Focus visible.
-   [ ] PAGE-QA-CSV-EXPORT-14: Long labels wrap.
-   [ ] PAGE-QA-CSV-EXPORT-15: No mobile overflow.
-   [ ] PAGE-QA-CSV-EXPORT-16: No geographic assumption.
-   [ ] PAGE-QA-CSV-EXPORT-17: Private data protected.
-   [ ] PAGE-QA-CSV-EXPORT-18: Real or labelled data only.
-   [ ] PAGE-QA-CSV-EXPORT-19: No stale mock values.
-   [ ] PAGE-QA-CSV-EXPORT-20: No stale role cache.
-   [ ] PAGE-QA-CSV-EXPORT-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-CSV-EXPORT-22: Success follows persistence.
-   [ ] PAGE-QA-CSV-EXPORT-23: Back navigation sensible.
-   [ ] PAGE-QA-CSV-EXPORT-24: Browser back/forward work.
-   [ ] PAGE-QA-CSV-EXPORT-25: Direct route load works.
-   [ ] PAGE-QA-CSV-EXPORT-26: No console errors.
-   [ ] PAGE-QA-CSV-EXPORT-27: No permanent spinner.
-   [ ] PAGE-QA-CSV-EXPORT-28: 320px layout works.
-   [ ] PAGE-QA-CSV-EXPORT-29: 768px layout works.
-   [ ] PAGE-QA-CSV-EXPORT-30: 1280px layout works.
-   [ ] PAGE-QA-CSV-EXPORT-31: Brand consistency holds. \### Demo
    selector
-   [ ] PAGE-QA-DEMO-SELECTOR-01: Correct design tokens.
-   [ ] PAGE-QA-DEMO-SELECTOR-02: Correct page title.
-   [ ] PAGE-QA-DEMO-SELECTOR-03: Primary action works.
-   [ ] PAGE-QA-DEMO-SELECTOR-04: All buttons functional.
-   [ ] PAGE-QA-DEMO-SELECTOR-05: Links route correctly.
-   [ ] PAGE-QA-DEMO-SELECTOR-06: Loading state present.
-   [ ] PAGE-QA-DEMO-SELECTOR-07: Empty state distinct from error.
-   [ ] PAGE-QA-DEMO-SELECTOR-08: API errors handled safely.
-   [ ] PAGE-QA-DEMO-SELECTOR-09: Retry works where available.
-   [ ] PAGE-QA-DEMO-SELECTOR-10: Animation failure fallback works.
-   [ ] PAGE-QA-DEMO-SELECTOR-11: Reduced motion works.
-   [ ] PAGE-QA-DEMO-SELECTOR-12: Keyboard navigation works.
-   [ ] PAGE-QA-DEMO-SELECTOR-13: Focus visible.
-   [ ] PAGE-QA-DEMO-SELECTOR-14: Long labels wrap.
-   [ ] PAGE-QA-DEMO-SELECTOR-15: No mobile overflow.
-   [ ] PAGE-QA-DEMO-SELECTOR-16: No geographic assumption.
-   [ ] PAGE-QA-DEMO-SELECTOR-17: Private data protected.
-   [ ] PAGE-QA-DEMO-SELECTOR-18: Real or labelled data only.
-   [ ] PAGE-QA-DEMO-SELECTOR-19: No stale mock values.
-   [ ] PAGE-QA-DEMO-SELECTOR-20: No stale role cache.
-   [ ] PAGE-QA-DEMO-SELECTOR-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-DEMO-SELECTOR-22: Success follows persistence.
-   [ ] PAGE-QA-DEMO-SELECTOR-23: Back navigation sensible.
-   [ ] PAGE-QA-DEMO-SELECTOR-24: Browser back/forward work.
-   [ ] PAGE-QA-DEMO-SELECTOR-25: Direct route load works.
-   [ ] PAGE-QA-DEMO-SELECTOR-26: No console errors.
-   [ ] PAGE-QA-DEMO-SELECTOR-27: No permanent spinner.
-   [ ] PAGE-QA-DEMO-SELECTOR-28: 320px layout works.
-   [ ] PAGE-QA-DEMO-SELECTOR-29: 768px layout works.
-   [ ] PAGE-QA-DEMO-SELECTOR-30: 1280px layout works.
-   [ ] PAGE-QA-DEMO-SELECTOR-31: Brand consistency holds. \### Role
    navigation
-   [ ] PAGE-QA-ROLE-NAVIGATION-01: Correct design tokens.
-   [ ] PAGE-QA-ROLE-NAVIGATION-02: Correct page title.
-   [ ] PAGE-QA-ROLE-NAVIGATION-03: Primary action works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-04: All buttons functional.
-   [ ] PAGE-QA-ROLE-NAVIGATION-05: Links route correctly.
-   [ ] PAGE-QA-ROLE-NAVIGATION-06: Loading state present.
-   [ ] PAGE-QA-ROLE-NAVIGATION-07: Empty state distinct from error.
-   [ ] PAGE-QA-ROLE-NAVIGATION-08: API errors handled safely.
-   [ ] PAGE-QA-ROLE-NAVIGATION-09: Retry works where available.
-   [ ] PAGE-QA-ROLE-NAVIGATION-10: Animation failure fallback works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-11: Reduced motion works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-12: Keyboard navigation works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-13: Focus visible.
-   [ ] PAGE-QA-ROLE-NAVIGATION-14: Long labels wrap.
-   [ ] PAGE-QA-ROLE-NAVIGATION-15: No mobile overflow.
-   [ ] PAGE-QA-ROLE-NAVIGATION-16: No geographic assumption.
-   [ ] PAGE-QA-ROLE-NAVIGATION-17: Private data protected.
-   [ ] PAGE-QA-ROLE-NAVIGATION-18: Real or labelled data only.
-   [ ] PAGE-QA-ROLE-NAVIGATION-19: No stale mock values.
-   [ ] PAGE-QA-ROLE-NAVIGATION-20: No stale role cache.
-   [ ] PAGE-QA-ROLE-NAVIGATION-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-ROLE-NAVIGATION-22: Success follows persistence.
-   [ ] PAGE-QA-ROLE-NAVIGATION-23: Back navigation sensible.
-   [ ] PAGE-QA-ROLE-NAVIGATION-24: Browser back/forward work.
-   [ ] PAGE-QA-ROLE-NAVIGATION-25: Direct route load works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-26: No console errors.
-   [ ] PAGE-QA-ROLE-NAVIGATION-27: No permanent spinner.
-   [ ] PAGE-QA-ROLE-NAVIGATION-28: 320px layout works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-29: 768px layout works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-30: 1280px layout works.
-   [ ] PAGE-QA-ROLE-NAVIGATION-31: Brand consistency holds. \###
    Location picker
-   [ ] PAGE-QA-LOCATION-PICKER-01: Correct design tokens.
-   [ ] PAGE-QA-LOCATION-PICKER-02: Correct page title.
-   [ ] PAGE-QA-LOCATION-PICKER-03: Primary action works.
-   [ ] PAGE-QA-LOCATION-PICKER-04: All buttons functional.
-   [ ] PAGE-QA-LOCATION-PICKER-05: Links route correctly.
-   [ ] PAGE-QA-LOCATION-PICKER-06: Loading state present.
-   [ ] PAGE-QA-LOCATION-PICKER-07: Empty state distinct from error.
-   [ ] PAGE-QA-LOCATION-PICKER-08: API errors handled safely.
-   [ ] PAGE-QA-LOCATION-PICKER-09: Retry works where available.
-   [ ] PAGE-QA-LOCATION-PICKER-10: Animation failure fallback works.
-   [ ] PAGE-QA-LOCATION-PICKER-11: Reduced motion works.
-   [ ] PAGE-QA-LOCATION-PICKER-12: Keyboard navigation works.
-   [ ] PAGE-QA-LOCATION-PICKER-13: Focus visible.
-   [ ] PAGE-QA-LOCATION-PICKER-14: Long labels wrap.
-   [ ] PAGE-QA-LOCATION-PICKER-15: No mobile overflow.
-   [ ] PAGE-QA-LOCATION-PICKER-16: No geographic assumption.
-   [ ] PAGE-QA-LOCATION-PICKER-17: Private data protected.
-   [ ] PAGE-QA-LOCATION-PICKER-18: Real or labelled data only.
-   [ ] PAGE-QA-LOCATION-PICKER-19: No stale mock values.
-   [ ] PAGE-QA-LOCATION-PICKER-20: No stale role cache.
-   [ ] PAGE-QA-LOCATION-PICKER-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-LOCATION-PICKER-22: Success follows persistence.
-   [ ] PAGE-QA-LOCATION-PICKER-23: Back navigation sensible.
-   [ ] PAGE-QA-LOCATION-PICKER-24: Browser back/forward work.
-   [ ] PAGE-QA-LOCATION-PICKER-25: Direct route load works.
-   [ ] PAGE-QA-LOCATION-PICKER-26: No console errors.
-   [ ] PAGE-QA-LOCATION-PICKER-27: No permanent spinner.
-   [ ] PAGE-QA-LOCATION-PICKER-28: 320px layout works.
-   [ ] PAGE-QA-LOCATION-PICKER-29: 768px layout works.
-   [ ] PAGE-QA-LOCATION-PICKER-30: 1280px layout works.
-   [ ] PAGE-QA-LOCATION-PICKER-31: Brand consistency holds. \### Image
    preview
-   [ ] PAGE-QA-IMAGE-PREVIEW-01: Correct design tokens.
-   [ ] PAGE-QA-IMAGE-PREVIEW-02: Correct page title.
-   [ ] PAGE-QA-IMAGE-PREVIEW-03: Primary action works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-04: All buttons functional.
-   [ ] PAGE-QA-IMAGE-PREVIEW-05: Links route correctly.
-   [ ] PAGE-QA-IMAGE-PREVIEW-06: Loading state present.
-   [ ] PAGE-QA-IMAGE-PREVIEW-07: Empty state distinct from error.
-   [ ] PAGE-QA-IMAGE-PREVIEW-08: API errors handled safely.
-   [ ] PAGE-QA-IMAGE-PREVIEW-09: Retry works where available.
-   [ ] PAGE-QA-IMAGE-PREVIEW-10: Animation failure fallback works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-11: Reduced motion works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-12: Keyboard navigation works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-13: Focus visible.
-   [ ] PAGE-QA-IMAGE-PREVIEW-14: Long labels wrap.
-   [ ] PAGE-QA-IMAGE-PREVIEW-15: No mobile overflow.
-   [ ] PAGE-QA-IMAGE-PREVIEW-16: No geographic assumption.
-   [ ] PAGE-QA-IMAGE-PREVIEW-17: Private data protected.
-   [ ] PAGE-QA-IMAGE-PREVIEW-18: Real or labelled data only.
-   [ ] PAGE-QA-IMAGE-PREVIEW-19: No stale mock values.
-   [ ] PAGE-QA-IMAGE-PREVIEW-20: No stale role cache.
-   [ ] PAGE-QA-IMAGE-PREVIEW-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-IMAGE-PREVIEW-22: Success follows persistence.
-   [ ] PAGE-QA-IMAGE-PREVIEW-23: Back navigation sensible.
-   [ ] PAGE-QA-IMAGE-PREVIEW-24: Browser back/forward work.
-   [ ] PAGE-QA-IMAGE-PREVIEW-25: Direct route load works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-26: No console errors.
-   [ ] PAGE-QA-IMAGE-PREVIEW-27: No permanent spinner.
-   [ ] PAGE-QA-IMAGE-PREVIEW-28: 320px layout works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-29: 768px layout works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-30: 1280px layout works.
-   [ ] PAGE-QA-IMAGE-PREVIEW-31: Brand consistency holds. \### Telugu
    locale
-   [ ] PAGE-QA-TELUGU-LOCALE-01: Correct design tokens.
-   [ ] PAGE-QA-TELUGU-LOCALE-02: Correct page title.
-   [ ] PAGE-QA-TELUGU-LOCALE-03: Primary action works.
-   [ ] PAGE-QA-TELUGU-LOCALE-04: All buttons functional.
-   [ ] PAGE-QA-TELUGU-LOCALE-05: Links route correctly.
-   [ ] PAGE-QA-TELUGU-LOCALE-06: Loading state present.
-   [ ] PAGE-QA-TELUGU-LOCALE-07: Empty state distinct from error.
-   [ ] PAGE-QA-TELUGU-LOCALE-08: API errors handled safely.
-   [ ] PAGE-QA-TELUGU-LOCALE-09: Retry works where available.
-   [ ] PAGE-QA-TELUGU-LOCALE-10: Animation failure fallback works.
-   [ ] PAGE-QA-TELUGU-LOCALE-11: Reduced motion works.
-   [ ] PAGE-QA-TELUGU-LOCALE-12: Keyboard navigation works.
-   [ ] PAGE-QA-TELUGU-LOCALE-13: Focus visible.
-   [ ] PAGE-QA-TELUGU-LOCALE-14: Long labels wrap.
-   [ ] PAGE-QA-TELUGU-LOCALE-15: No mobile overflow.
-   [ ] PAGE-QA-TELUGU-LOCALE-16: No geographic assumption.
-   [ ] PAGE-QA-TELUGU-LOCALE-17: Private data protected.
-   [ ] PAGE-QA-TELUGU-LOCALE-18: Real or labelled data only.
-   [ ] PAGE-QA-TELUGU-LOCALE-19: No stale mock values.
-   [ ] PAGE-QA-TELUGU-LOCALE-20: No stale role cache.
-   [ ] PAGE-QA-TELUGU-LOCALE-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-TELUGU-LOCALE-22: Success follows persistence.
-   [ ] PAGE-QA-TELUGU-LOCALE-23: Back navigation sensible.
-   [ ] PAGE-QA-TELUGU-LOCALE-24: Browser back/forward work.
-   [ ] PAGE-QA-TELUGU-LOCALE-25: Direct route load works.
-   [ ] PAGE-QA-TELUGU-LOCALE-26: No console errors.
-   [ ] PAGE-QA-TELUGU-LOCALE-27: No permanent spinner.
-   [ ] PAGE-QA-TELUGU-LOCALE-28: 320px layout works.
-   [ ] PAGE-QA-TELUGU-LOCALE-29: 768px layout works.
-   [ ] PAGE-QA-TELUGU-LOCALE-30: 1280px layout works.
-   [ ] PAGE-QA-TELUGU-LOCALE-31: Brand consistency holds. \### Mobile
    navigation
-   [ ] PAGE-QA-MOBILE-NAVIGATION-01: Correct design tokens.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-02: Correct page title.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-03: Primary action works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-04: All buttons functional.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-05: Links route correctly.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-06: Loading state present.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-07: Empty state distinct from error.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-08: API errors handled safely.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-09: Retry works where available.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-10: Animation failure fallback works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-11: Reduced motion works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-12: Keyboard navigation works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-13: Focus visible.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-14: Long labels wrap.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-15: No mobile overflow.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-16: No geographic assumption.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-17: Private data protected.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-18: Real or labelled data only.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-19: No stale mock values.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-20: No stale role cache.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-21: Error preserves input when
    appropriate.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-22: Success follows persistence.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-23: Back navigation sensible.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-24: Browser back/forward work.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-25: Direct route load works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-26: No console errors.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-27: No permanent spinner.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-28: 320px layout works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-29: 768px layout works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-30: 1280px layout works.
-   [ ] PAGE-QA-MOBILE-NAVIGATION-31: Brand consistency holds. \###
    Footer
-   [ ] PAGE-QA-FOOTER-01: Correct design tokens.
-   [ ] PAGE-QA-FOOTER-02: Correct page title.
-   [ ] PAGE-QA-FOOTER-03: Primary action works.
-   [ ] PAGE-QA-FOOTER-04: All buttons functional.
-   [ ] PAGE-QA-FOOTER-05: Links route correctly.
-   [ ] PAGE-QA-FOOTER-06: Loading state present.
-   [ ] PAGE-QA-FOOTER-07: Empty state distinct from error.
-   [ ] PAGE-QA-FOOTER-08: API errors handled safely.
-   [ ] PAGE-QA-FOOTER-09: Retry works where available.
-   [ ] PAGE-QA-FOOTER-10: Animation failure fallback works.
-   [ ] PAGE-QA-FOOTER-11: Reduced motion works.
-   [ ] PAGE-QA-FOOTER-12: Keyboard navigation works.
-   [ ] PAGE-QA-FOOTER-13: Focus visible.
-   [ ] PAGE-QA-FOOTER-14: Long labels wrap.
-   [ ] PAGE-QA-FOOTER-15: No mobile overflow.
-   [ ] PAGE-QA-FOOTER-16: No geographic assumption.
-   [ ] PAGE-QA-FOOTER-17: Private data protected.
-   [ ] PAGE-QA-FOOTER-18: Real or labelled data only.
-   [ ] PAGE-QA-FOOTER-19: No stale mock values.
-   [ ] PAGE-QA-FOOTER-20: No stale role cache.
-   [ ] PAGE-QA-FOOTER-21: Error preserves input when appropriate.
-   [ ] PAGE-QA-FOOTER-22: Success follows persistence.
-   [ ] PAGE-QA-FOOTER-23: Back navigation sensible.
-   [ ] PAGE-QA-FOOTER-24: Browser back/forward work.
-   [ ] PAGE-QA-FOOTER-25: Direct route load works.
-   [ ] PAGE-QA-FOOTER-26: No console errors.
-   [ ] PAGE-QA-FOOTER-27: No permanent spinner.
-   [ ] PAGE-QA-FOOTER-28: 320px layout works.
-   [ ] PAGE-QA-FOOTER-29: 768px layout works.
-   [ ] PAGE-QA-FOOTER-30: 1280px layout works.
-   [ ] PAGE-QA-FOOTER-31: Brand consistency holds.

## 49. Requirement traceability matrix

### Sign-in

-   [ ] TRACE-01-01: Implementation exists in real app.
-   [ ] TRACE-01-02: Responsive behavior verified.
-   [ ] TRACE-01-03: Keyboard behavior verified.
-   [ ] TRACE-01-04: Reduced-motion verified.
-   [ ] TRACE-01-05: Loading state verified.
-   [ ] TRACE-01-06: Empty state verified.
-   [ ] TRACE-01-07: Error state verified.
-   [ ] TRACE-01-08: Permission scope verified.
-   [ ] TRACE-01-09: Data accuracy verified.
-   [ ] TRACE-01-10: Localization verified where applicable.
-   [ ] TRACE-01-11: Privacy reviewed.
-   [ ] TRACE-01-12: Regression test added where practical. \### Opening
    page
-   [ ] TRACE-02-01: Implementation exists in real app.
-   [ ] TRACE-02-02: Responsive behavior verified.
-   [ ] TRACE-02-03: Keyboard behavior verified.
-   [ ] TRACE-02-04: Reduced-motion verified.
-   [ ] TRACE-02-05: Loading state verified.
-   [ ] TRACE-02-06: Empty state verified.
-   [ ] TRACE-02-07: Error state verified.
-   [ ] TRACE-02-08: Permission scope verified.
-   [ ] TRACE-02-09: Data accuracy verified.
-   [ ] TRACE-02-10: Localization verified where applicable.
-   [ ] TRACE-02-11: Privacy reviewed.
-   [ ] TRACE-02-12: Regression test added where practical. \### Where
    to go
-   [ ] TRACE-03-01: Implementation exists in real app.
-   [ ] TRACE-03-02: Responsive behavior verified.
-   [ ] TRACE-03-03: Keyboard behavior verified.
-   [ ] TRACE-03-04: Reduced-motion verified.
-   [ ] TRACE-03-05: Loading state verified.
-   [ ] TRACE-03-06: Empty state verified.
-   [ ] TRACE-03-07: Error state verified.
-   [ ] TRACE-03-08: Permission scope verified.
-   [ ] TRACE-03-09: Data accuracy verified.
-   [ ] TRACE-03-10: Localization verified where applicable.
-   [ ] TRACE-03-11: Privacy reviewed.
-   [ ] TRACE-03-12: Regression test added where practical. \### Telugu
-   [ ] TRACE-04-01: Implementation exists in real app.
-   [ ] TRACE-04-02: Responsive behavior verified.
-   [ ] TRACE-04-03: Keyboard behavior verified.
-   [ ] TRACE-04-04: Reduced-motion verified.
-   [ ] TRACE-04-05: Loading state verified.
-   [ ] TRACE-04-06: Empty state verified.
-   [ ] TRACE-04-07: Error state verified.
-   [ ] TRACE-04-08: Permission scope verified.
-   [ ] TRACE-04-09: Data accuracy verified.
-   [ ] TRACE-04-10: Localization verified where applicable.
-   [ ] TRACE-04-11: Privacy reviewed.
-   [ ] TRACE-04-12: Regression test added where practical. \### What
    can you report
-   [ ] TRACE-05-01: Implementation exists in real app.
-   [ ] TRACE-05-02: Responsive behavior verified.
-   [ ] TRACE-05-03: Keyboard behavior verified.
-   [ ] TRACE-05-04: Reduced-motion verified.
-   [ ] TRACE-05-05: Loading state verified.
-   [ ] TRACE-05-06: Empty state verified.
-   [ ] TRACE-05-07: Error state verified.
-   [ ] TRACE-05-08: Permission scope verified.
-   [ ] TRACE-05-09: Data accuracy verified.
-   [ ] TRACE-05-10: Localization verified where applicable.
-   [ ] TRACE-05-11: Privacy reviewed.
-   [ ] TRACE-05-12: Regression test added where practical. \### Reports
    and queues
-   [ ] TRACE-06-01: Implementation exists in real app.
-   [ ] TRACE-06-02: Responsive behavior verified.
-   [ ] TRACE-06-03: Keyboard behavior verified.
-   [ ] TRACE-06-04: Reduced-motion verified.
-   [ ] TRACE-06-05: Loading state verified.
-   [ ] TRACE-06-06: Empty state verified.
-   [ ] TRACE-06-07: Error state verified.
-   [ ] TRACE-06-08: Permission scope verified.
-   [ ] TRACE-06-09: Data accuracy verified.
-   [ ] TRACE-06-10: Localization verified where applicable.
-   [ ] TRACE-06-11: Privacy reviewed.
-   [ ] TRACE-06-12: Regression test added where practical. \###
    Graphics
-   [ ] TRACE-07-01: Implementation exists in real app.
-   [ ] TRACE-07-02: Responsive behavior verified.
-   [ ] TRACE-07-03: Keyboard behavior verified.
-   [ ] TRACE-07-04: Reduced-motion verified.
-   [ ] TRACE-07-05: Loading state verified.
-   [ ] TRACE-07-06: Empty state verified.
-   [ ] TRACE-07-07: Error state verified.
-   [ ] TRACE-07-08: Permission scope verified.
-   [ ] TRACE-07-09: Data accuracy verified.
-   [ ] TRACE-07-10: Localization verified where applicable.
-   [ ] TRACE-07-11: Privacy reviewed.
-   [ ] TRACE-07-12: Regression test added where practical. \### Images
    and location
-   [ ] TRACE-08-01: Implementation exists in real app.
-   [ ] TRACE-08-02: Responsive behavior verified.
-   [ ] TRACE-08-03: Keyboard behavior verified.
-   [ ] TRACE-08-04: Reduced-motion verified.
-   [ ] TRACE-08-05: Loading state verified.
-   [ ] TRACE-08-06: Empty state verified.
-   [ ] TRACE-08-07: Error state verified.
-   [ ] TRACE-08-08: Permission scope verified.
-   [ ] TRACE-08-09: Data accuracy verified.
-   [ ] TRACE-08-10: Localization verified where applicable.
-   [ ] TRACE-08-11: Privacy reviewed.
-   [ ] TRACE-08-12: Regression test added where practical. \###
    Questions section
-   [ ] TRACE-09-01: Implementation exists in real app.
-   [ ] TRACE-09-02: Responsive behavior verified.
-   [ ] TRACE-09-03: Keyboard behavior verified.
-   [ ] TRACE-09-04: Reduced-motion verified.
-   [ ] TRACE-09-05: Loading state verified.
-   [ ] TRACE-09-06: Empty state verified.
-   [ ] TRACE-09-07: Error state verified.
-   [ ] TRACE-09-08: Permission scope verified.
-   [ ] TRACE-09-09: Data accuracy verified.
-   [ ] TRACE-09-10: Localization verified where applicable.
-   [ ] TRACE-09-11: Privacy reviewed.
-   [ ] TRACE-09-12: Regression test added where practical. \### Issue
    taxonomy
-   [ ] TRACE-10-01: Implementation exists in real app.
-   [ ] TRACE-10-02: Responsive behavior verified.
-   [ ] TRACE-10-03: Keyboard behavior verified.
-   [ ] TRACE-10-04: Reduced-motion verified.
-   [ ] TRACE-10-05: Loading state verified.
-   [ ] TRACE-10-06: Empty state verified.
-   [ ] TRACE-10-07: Error state verified.
-   [ ] TRACE-10-08: Permission scope verified.
-   [ ] TRACE-10-09: Data accuracy verified.
-   [ ] TRACE-10-10: Localization verified where applicable.
-   [ ] TRACE-10-11: Privacy reviewed.
-   [ ] TRACE-10-12: Regression test added where practical. \### Seen
    something broken
-   [ ] TRACE-11-01: Implementation exists in real app.
-   [ ] TRACE-11-02: Responsive behavior verified.
-   [ ] TRACE-11-03: Keyboard behavior verified.
-   [ ] TRACE-11-04: Reduced-motion verified.
-   [ ] TRACE-11-05: Loading state verified.
-   [ ] TRACE-11-06: Empty state verified.
-   [ ] TRACE-11-07: Error state verified.
-   [ ] TRACE-11-08: Permission scope verified.
-   [ ] TRACE-11-09: Data accuracy verified.
-   [ ] TRACE-11-10: Localization verified where applicable.
-   [ ] TRACE-11-11: Privacy reviewed.
-   [ ] TRACE-11-12: Regression test added where practical. \### Your
    City
-   [ ] TRACE-12-01: Implementation exists in real app.
-   [ ] TRACE-12-02: Responsive behavior verified.
-   [ ] TRACE-12-03: Keyboard behavior verified.
-   [ ] TRACE-12-04: Reduced-motion verified.
-   [ ] TRACE-12-05: Loading state verified.
-   [ ] TRACE-12-06: Empty state verified.
-   [ ] TRACE-12-07: Error state verified.
-   [ ] TRACE-12-08: Permission scope verified.
-   [ ] TRACE-12-09: Data accuracy verified.
-   [ ] TRACE-12-10: Localization verified where applicable.
-   [ ] TRACE-12-11: Privacy reviewed.
-   [ ] TRACE-12-12: Regression test added where practical. \### Footer
-   [ ] TRACE-13-01: Implementation exists in real app.
-   [ ] TRACE-13-02: Responsive behavior verified.
-   [ ] TRACE-13-03: Keyboard behavior verified.
-   [ ] TRACE-13-04: Reduced-motion verified.
-   [ ] TRACE-13-05: Loading state verified.
-   [ ] TRACE-13-06: Empty state verified.
-   [ ] TRACE-13-07: Error state verified.
-   [ ] TRACE-13-08: Permission scope verified.
-   [ ] TRACE-13-09: Data accuracy verified.
-   [ ] TRACE-13-10: Localization verified where applicable.
-   [ ] TRACE-13-11: Privacy reviewed.
-   [ ] TRACE-13-12: Regression test added where practical. \###
    Resident report
-   [ ] TRACE-14-01: Implementation exists in real app.
-   [ ] TRACE-14-02: Responsive behavior verified.
-   [ ] TRACE-14-03: Keyboard behavior verified.
-   [ ] TRACE-14-04: Reduced-motion verified.
-   [ ] TRACE-14-05: Loading state verified.
-   [ ] TRACE-14-06: Empty state verified.
-   [ ] TRACE-14-07: Error state verified.
-   [ ] TRACE-14-08: Permission scope verified.
-   [ ] TRACE-14-09: Data accuracy verified.
-   [ ] TRACE-14-10: Localization verified where applicable.
-   [ ] TRACE-14-11: Privacy reviewed.
-   [ ] TRACE-14-12: Regression test added where practical. \###
    Resident services
-   [ ] TRACE-15-01: Implementation exists in real app.
-   [ ] TRACE-15-02: Responsive behavior verified.
-   [ ] TRACE-15-03: Keyboard behavior verified.
-   [ ] TRACE-15-04: Reduced-motion verified.
-   [ ] TRACE-15-05: Loading state verified.
-   [ ] TRACE-15-06: Empty state verified.
-   [ ] TRACE-15-07: Error state verified.
-   [ ] TRACE-15-08: Permission scope verified.
-   [ ] TRACE-15-09: Data accuracy verified.
-   [ ] TRACE-15-10: Localization verified where applicable.
-   [ ] TRACE-15-11: Privacy reviewed.
-   [ ] TRACE-15-12: Regression test added where practical. \###
    Resident notifications
-   [ ] TRACE-16-01: Implementation exists in real app.
-   [ ] TRACE-16-02: Responsive behavior verified.
-   [ ] TRACE-16-03: Keyboard behavior verified.
-   [ ] TRACE-16-04: Reduced-motion verified.
-   [ ] TRACE-16-05: Loading state verified.
-   [ ] TRACE-16-06: Empty state verified.
-   [ ] TRACE-16-07: Error state verified.
-   [ ] TRACE-16-08: Permission scope verified.
-   [ ] TRACE-16-09: Data accuracy verified.
-   [ ] TRACE-16-10: Localization verified where applicable.
-   [ ] TRACE-16-11: Privacy reviewed.
-   [ ] TRACE-16-12: Regression test added where practical. \### Road
    Officer
-   [ ] TRACE-17-01: Implementation exists in real app.
-   [ ] TRACE-17-02: Responsive behavior verified.
-   [ ] TRACE-17-03: Keyboard behavior verified.
-   [ ] TRACE-17-04: Reduced-motion verified.
-   [ ] TRACE-17-05: Loading state verified.
-   [ ] TRACE-17-06: Empty state verified.
-   [ ] TRACE-17-07: Error state verified.
-   [ ] TRACE-17-08: Permission scope verified.
-   [ ] TRACE-17-09: Data accuracy verified.
-   [ ] TRACE-17-10: Localization verified where applicable.
-   [ ] TRACE-17-11: Privacy reviewed.
-   [ ] TRACE-17-12: Regression test added where practical. \### Road
    Supervisor
-   [ ] TRACE-18-01: Implementation exists in real app.
-   [ ] TRACE-18-02: Responsive behavior verified.
-   [ ] TRACE-18-03: Keyboard behavior verified.
-   [ ] TRACE-18-04: Reduced-motion verified.
-   [ ] TRACE-18-05: Loading state verified.
-   [ ] TRACE-18-06: Empty state verified.
-   [ ] TRACE-18-07: Error state verified.
-   [ ] TRACE-18-08: Permission scope verified.
-   [ ] TRACE-18-09: Data accuracy verified.
-   [ ] TRACE-18-10: Localization verified where applicable.
-   [ ] TRACE-18-11: Privacy reviewed.
-   [ ] TRACE-18-12: Regression test added where practical. \### Triage
    Desk
-   [ ] TRACE-19-01: Implementation exists in real app.
-   [ ] TRACE-19-02: Responsive behavior verified.
-   [ ] TRACE-19-03: Keyboard behavior verified.
-   [ ] TRACE-19-04: Reduced-motion verified.
-   [ ] TRACE-19-05: Loading state verified.
-   [ ] TRACE-19-06: Empty state verified.
-   [ ] TRACE-19-07: Error state verified.
-   [ ] TRACE-19-08: Permission scope verified.
-   [ ] TRACE-19-09: Data accuracy verified.
-   [ ] TRACE-19-10: Localization verified where applicable.
-   [ ] TRACE-19-11: Privacy reviewed.
-   [ ] TRACE-19-12: Regression test added where practical. \###
    Municipal Admin
-   [ ] TRACE-20-01: Implementation exists in real app.
-   [ ] TRACE-20-02: Responsive behavior verified.
-   [ ] TRACE-20-03: Keyboard behavior verified.
-   [ ] TRACE-20-04: Reduced-motion verified.
-   [ ] TRACE-20-05: Loading state verified.
-   [ ] TRACE-20-06: Empty state verified.
-   [ ] TRACE-20-07: Error state verified.
-   [ ] TRACE-20-08: Permission scope verified.
-   [ ] TRACE-20-09: Data accuracy verified.
-   [ ] TRACE-20-10: Localization verified where applicable.
-   [ ] TRACE-20-11: Privacy reviewed.
-   [ ] TRACE-20-12: Regression test added where practical.

## 50. Final command

Implement every feasible requirement directly in the existing project.
Treat each reported issue as a requirement, not optional inspiration.
Start with reconnaissance and baseline checks, then implement in a
coherent sequence. Do not stop after describing a plan. Do not replace
functional code with mockups. Do not invent data, integrations, metrics,
credentials, or success states. Preserve working behavior unless the
request explicitly changes it. Add tests, run quality checks, and verify
each role separately. Report exactly what was implemented, what was
tested, actual outcomes, and what remains blocked.

**End of master prompt.**
