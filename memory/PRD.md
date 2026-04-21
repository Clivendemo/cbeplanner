# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB (Motor async)
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Lesson SLO Slots System (Current)

### Data Model
- **Collection**: `lesson_slo_slots` (unique index on substrandId + slot_index)
- **Source of truth**: `substrand.number_of_lessons`
- **Slot fields**: outcome, description, key_inquiry_question (ONE per lesson), learning_activities, resources (structured), assessment_methods, competencies, values, pcis, is_customized

### Resource Format
```json
[
  {"type": "textbook", "title": "Planet Math Grade 4", "pages": "12-15", "display_text": "Planet Math Grade 4, pp. 12-15"},
  {"type": "material", "display_text": "Number charts"}
]
```

### Admin Panel (lesson-slots.tsx)
- New "Lesson SLOs" tab in admin bottom nav
- Cascade: Grade → Subject → Strand → Substrand
- Auto-displays N slots from number_of_lessons
- Each slot: edit modal (outcome, inquiry, activities, competencies, values, pcis) + resource modal (textbook with title/pages or material)
- Fallback/Customized badges, clear-to-fallback action

### Backend Endpoints
- `GET /api/admin/lesson-slots/{substrand_id}` — list + auto-generate
- `PUT /api/admin/lesson-slots/{substrand_id}/{slot_index}` — update
- `POST /api/admin/lesson-slots/{substrand_id}/{slot_index}/clear` — reset
- `POST /api/admin/lesson-slots/{substrand_id}/generate` — regenerate
- `GET /api/lesson-slots/{substrand_id}` — teacher read-only

### Integration
- Scheme generation uses slots as primary, parent SLO fallback
- Lesson plan generation uses slots with formatted resources
- Textbook: `format_resource_display()` handles structured resources

## Scheme Draft Workflow
- Save → list/get → preview (free) → regenerate → download (KES 15)

## Landing Page Redesign (Feb 2026)
Re-skin of `/app/frontend/app/auth/login.tsx` and `signup.tsx` — no marquee, 3-column desktop layout, KICD footer preserved.

- **New file `components/LandingLayout.tsx`** — single module exporting `LandingLayout` wrapper + `FeatureTiles` + 7 sidebar widgets (DidYouKnow, UpcomingEvents, TeacherQuote, UsefulLinks, TipOfDay, TermCalendar, Subjects, AdSlot).
- **Responsive via `useWindowDimensions`**:
  - ≥1024px: 3 columns (210px left + 500px center + 210px right) + 728×90 bottom banner
  - 768–1023px: 2 columns (hide left sidebar) + 468×60 bottom banner
  - <768px: single column, edge-to-edge auth card + 320×50 bottom banner
- **Widgets**:
  - Did You Know (5 CBC facts, rotate every 8s with dot indicator)
  - Upcoming Events (9 academic/co-curricular entries with colored date blocks & legend)
  - Teacher's Corner (3 quotes, rotate every 10s, purple left-border)
  - Useful Links (5 KE education links → `Linking.openURL`, new tab on web)
  - Lesson Planning Tip (day-of-week-based)
  - 2025 Term Calendar (Term 1 Past · Term 2 Current · Term 3 Upcoming, academic + co-curricular per term)
  - Subjects (9 pills)
  - Ad slots (placeholders with "Advertisement" label, ready for AdSense swap)
- **Feature preview tiles (clickable with auth check)**:
  - 📄 Generate Scheme of Work → `/(teacher)/schemes`
  - 📝 Generate Lesson Plan → `/(teacher)/home`
  - 📖 Generate Lesson Notes → `/(teacher)/notes`
  - 📥 Download CBC Past Papers → `/(teacher)/revision`
  - If user session is active → direct `router.push`. If not → friendly alert "Please sign in to access this feature. Your session may have expired." (stays on login).
- **Removed**:
  - Animated `Dimensions`/marquee text block + all its refs/imports from login.tsx
  - Full-width `SafeAreaView` + `ScrollView` wrappers (center-col handles sizing)
  - `useSafeAreaInsets`, `SafeAreaView`, `ScrollView`, `Animated`, `Dimensions` imports that were only used by the marquee/full-width layout
- **Preserved (untouched)**:
  - All auth logic (`signIn`, `signUp`, `resetPassword`, `rememberMe`, AuthContext)
  - Firebase integration, API calls, routing
  - All other teacher/admin screens
  - Password Reset modal, graduation cap logo, "KICD-Aligned / LEGIT LAB" footer
- **Primary color** updated to `#5B5BD6` (indigo, per spec) on buttons, dots, links, tile borders; previous `#6366F1` remains elsewhere for continuity.

## Server.py Refactor — Phase 1 (Feb 2026)
- **Created `/app/backend/app/deps.py`** — shared core: MongoDB client, `verify_token`, `verify_admin`, `serialize_doc`, `validate_object_id`, `api_error`, `to_int`, constants (SCHEME_DOWNLOAD_COST, LESSON_PLAN_COST_KES, NOTES_DOWNLOAD_COST_KES, FREE_LESSONS_ON_SIGNUP, FIREBASE_*, JWT_SECRET, ADMIN_EMAILS), shared `api_router = APIRouter(prefix="/api")`.
- **Created `/app/backend/routes/schemes.py`** — all 7 scheme endpoints (`GET /schemes`, `GET /schemes/config/lessons-per-week`, `GET /schemes/topics/{subjectId}`, `GET /schemes/{id}`, `POST /schemes/generate-v2`, `DELETE /schemes/{id}`, `POST /schemes/{id}/download`) + scheme helpers (`_format_slo_for_scheme`, `generate_assessment_methods`, `validate_break`, `calculate_break_duration`) + `SchemeGenerateRequest` Pydantic model. 650 lines, clean imports.
- **Created `/app/backend/routes/__init__.py`** package marker.
- **server.py**: 6063 → 4501 lines (-1562 lines, 26% reduction). No longer defines shared core — imports from `app.deps`. Registers route modules via side-effect import: `from routes import schemes as _routes_schemes`.

## Dead Code Removed
**Backend (server.py)**:
- `POST /api/schemes/generate` (V1, superseded by generate-v2) — 210 lines
- `POST /api/schemes/preview` (exposed free full PDF — security risk) — 22 lines
- `POST /api/schemes/download` (accepted scheme_data in body, replaceable by owner-scoped `/schemes/{id}/download`) — 100 lines
- Full Scheme Draft Workflow block: `POST /schemes/save-draft`, `GET /schemes/drafts`, `GET /schemes/drafts/{id}`, `POST /schemes/drafts/{id}/regenerate`, `POST /schemes/drafts/{id}/preview`, `POST /schemes/drafts/{id}/download` (frontend never referenced them) — 230 lines
- Legacy Pydantic models: `BreakInput`, `SchemeOfWorkRequest`, `SchemeLesson`, `SchemeOfWork` — 52 lines
- Dead `scheme_drafts` index creation in startup

**Frontend (schemes.tsx)**: 2618 → 2151 lines (-467 lines)
- Dead handlers `handlePreview`, `handleDownload` (called removed endpoints)
- Dead components `renderPreviewStep`, `renderFundsModal`, `renderPdfPreviewModal`
- Dead state (`showPdfModal`, `pdfPreviewUrl`, `showFundsModal`, `pendingDownload`, `previewing`, `downloading`, `generatedScheme`)
- Dead imports (`WebView`, `Sharing`, `FileSystem`, `Platform`, `SafeAreaView`)
- Simplified `Step` type from 4-step to 3-step flow (no preview step — flow redirects straight to My Schemes)

## Phase 2 Refactor — PENDING
Admin endpoints (~2500 lines remaining in `server.py`) to be extracted:
- `routes/admin_curriculum.py` (grades/subjects/strands/substrands/slos CRUD, bulk, move, reorder, change-grade)
- `routes/admin_resources.py` (competencies/values/pcis/activities/mappings/assessments/reference-data/lesson-slos/lesson-slots)
- `routes/admin_import.py` (import/upload-curriculum/curriculum-jobs/seed/public-template)
- `routes/admin_ops.py` (wallet-reconciliation, repair, cleanup, clear-idempotency)
- `routes/lesson_plans.py`, `routes/notes.py`, `routes/payments.py`, `routes/auth_profile.py`, `routes/curriculum_public.py`

## My Schemes Module (Feb 2026 — aligned with My Lesson Plans)
Mirrors the Lesson Plan architecture end-to-end:

- **Generator** (`schemes.tsx`): form with grade/subject/term/weeks/topics/breaks/double-lesson. On Generate, backend persists scheme + inputs to `db.schemes` and returns `schemeId`. Frontend `router.replace`s to `/my-schemes`. No PDF is exposed post-generation.
- **List** (`my-schemes.tsx`): `GET /api/schemes` returns owner-scoped schemes. Cards show subject, grade, term/year, weeks × lessons/wk, school, created date, Preview Only / Downloaded badge. "Create New Scheme" CTA on top.
- **Detail** (`scheme-detail.tsx`): `GET /api/schemes/{id}` → rendered inline with `<SchemeDisplay>` component (no PDF exposed). Sticky action bar: Download PDF (KES 15) · Edit · Delete. Inline amber bar with "Top Up" deep-link when balance < KES 15. Handles legacy scheme schemas (string or array fields, `lessonNumber` or `lesson`).
- **SchemeDisplay component** (`components/SchemeDisplay.tsx`): Full PDF-like rendering — REPUBLIC OF KENYA header, meta block, horizontally scrollable scheme table (WK, LSN, Strand, Sub-strand, SLO, Key Inquiry, Learning Experiences, Learning Resources, Assessment, Ref.) with zebra rows, amber break rows, double-lesson badge.
- **Edit**: Navigates back to `/schemes?editId={id}`. Generator preloads inputs from saved scheme (grade, subject, term, year, weeks, LPW, selected topics, breaks, double-lesson, carry-over).
- **Secure Download** (`POST /api/schemes/{id}/download`): owner check → wallet guard → DEBIT ledger → atomic `$inc` deduction with `$gte` match → PDF from stored scheme → on failure, auto-refund (wallet + ledger rollback). Sets `isPaid=true`, `downloadCount++`, `lastDownloadedAt`.
- **Delete** (`DELETE /api/schemes/{id}`): owner-only.
- **Security**: PDF is never exposed pre-payment through a public/free route in the new flow. Preview is JSON-rendered in-app only.

## Seed Pipeline (v2)
- Grade normalization (27 variants), populated SLO mappings, get_or_create helpers

## Pricing
- Lesson Plans: KES 2 (5 free), Notes: KES 1 (first free), Scheme: KES 15

## Admin Emails
- mail2clive@gmail.com (primary), testadmin2026@gmail.com (test)

## Kiswahili Localization (Feb 2026)
Scheme of Work generator + in-app preview fully localized for Kiswahili subjects:
- **Detection**: subject name contains "kiswahili" or "fasihi" → triggers Kiswahili mode
- **PDF** (`scheme_generator.py`): Cover page (MPANGO WA KAZI / MUHULA WA / Darasa / Somo / Mwaka), table headers (WIKI, SOM, MADA KUU, MADA NDOGO, MATOKEO MAALUM YA UJIFUNZAJI, SWALI IBUKA, SHUGHULI ZA UJIFUNZAJI, NYENZO ZA KUJIFUNZA, TATHMINI, TAFAK), Kiswahili inquiry-question stems, Kiswahili assessment methods, Kiswahili footer ("Imetengenezwa na …")
- **In-app preview** (`SchemeDisplay.tsx`): Cover (MPANGO WA KAZI / MUHULA WA), banner (JAMHURI YA KENYA, MTAALA WA UMILISI, MPANGO WA KAZI), meta labels (Shule/Darasa/Somo/Muhula/Muda), table headers (WIKI/SOM/Mada Kuu/Mada Ndogo/Matokeo Maalum ya Ujifunzaji/Swali Ibuka/Shughuli za Ujifunzaji/Nyenzo za Kujifunza/Tathmini/Tafak.), SLO preamble ("Kufikia mwisho wa somo, mwanafunzi aweze: …"), and Kiswahili footer
- English-subject output is unchanged

## App Shell / Persistent Sidebars (Feb 2026)
Post-login teacher pages now render inside a centered 1330px shell:
- **Left sidebar 180px**: MPesa Till card (compact 5-step reminder) + Today's Tip.
- **Main column 950px**: The existing Stack navigator (dashboard, home, notes, lessons, profile, schemes, my-schemes, scheme-detail, lesson-detail, revision) renders here — unchanged and isolated from the sidebar chrome.
- **Right sidebar 180px**: Teacher's Corner quote (auto-rotating), Useful Links, Support / Email Us.
- **Breakpoint**: Sidebars show only when `width >= 1280px`. Below that, the Stack renders full-bleed (mobile/tablet remain identical to before).
- **Background**: Soft indigo wash (`#EEF2FF` + radial gradients toward `#E0E7FF` / `#F5F3FF`) that harmonises with the app's `#6366F1` header.
- **Login page**: Unchanged — still uses `LandingLayout` with its own widget set.
- New file: `frontend/components/AppSidebars.tsx`. Wrapping done in `frontend/app/(teacher)/_layout.tsx`.

## Calendar Widget + Dashboard Reorder + MPesa Migration (Feb 2026)
- **Landing page left sidebar**: Removed the big `MPesaPaymentWidget` and replaced with a new interactive `CalendarWidget` (shows current month, prev/next month nav, today highlighted in indigo, event dates color-coded using the same `UPCOMING_EVENTS` palette, click an event-date → popover with the event titles, click the same date again or ✕ to close, empty dates are non-interactive). Placed above `UpcomingEventsWidget`.
- **Post-login left sidebar (every teacher page)**: Compact variant `CalendarWidgetCompact` persists on every page (dashboard, schemes, my-schemes, home, notes, lessons, profile, etc.). Same interactive behaviour as the landing calendar.
- **Scheme generation page only**: `MPesaTillCard` appears in the left sidebar on `/schemes` (rendered conditionally via `usePathname`). Removed from inline page content.
- **Dashboard tile reorder** (`dashboard.tsx`):
  - Left (4): Schemes of Work → Create Lesson Plan → Generate Notes → My Profile
  - Right (3): My Schemes → My Lesson Plans → Past Papers

## Admin-Controlled Calendar + Term Calendar (Feb 2026)
- **Backend** (`routes/calendar.py`):
  - Public `GET /api/calendar/events`, `GET /api/calendar/terms` (no auth — landing page consumes them).
  - Admin `POST/PUT/DELETE /api/admin/calendar/events[/id]`, `…/terms[/id]`.
  - `POST /api/admin/calendar/seed` (idempotent) + auto-seed on server startup inserts the previous hardcoded values so nothing regresses visually.
  - Events store ISO `YYYY-MM-DD` + category (`academic` / `cocurricular` / `exam`). Backend returns a display palette for each.
  - Terms store name, period, status (`past` / `current` / `upcoming`), year, academic milestones, co-curricular milestones.
- **Admin panel**: New "Calendar" tab (`app/(admin)/calendar.tsx`) between Lesson SLOs and Import. Two sub-tabs (Upcoming Events / Term Calendar), each with list rows (coloured strip + title + meta) and ✏️ edit / 🗑️ delete. Modal editors with category/status chips, inline activity editors for term milestones.
- **Frontend data layer** (`components/useCalendarData.ts`): Shared hook with 5-min in-memory cache. Exposes `DisplayEvent[]` (with `date`, `day`, `palette`) and `DisplayTerm[]`. `invalidateCalendarCache()` is called after any admin CRUD so other tabs pick up changes on next mount.
- **LandingLayout widgets** (`UpcomingEventsWidget`, `TermCalendarWidget`, `CalendarWidgetBase`) all now read from the hook — no hardcoded arrays anywhere.

## Responsive Layout + Mobile Sidebar Stacking (Feb 2026)
- **LandingLayout**: On mobile (`< 768px`), the center card covers the whole width and the sidebars are rendered *below* it in a vertically-stacked block — users simply scroll down past the main card to reveal Calendar, Upcoming Events, Teacher's Corner, Useful Links, Term Calendar, Subjects, etc.
- **Ad relocation**: The previous 728×90 / 468×60 / 320×50 bottom-of-page ad has been removed from below the middle column and now anchors the **end of the left-sidebar stack** (appropriately sized for each breakpoint).
- **Teacher shell** (`(teacher)/_layout.tsx`): Below the 1180px breakpoint, the Stack now renders at full viewport height in an outer ScrollView with the `AppLeftSidebar` + `AppRightSidebar` widgets stacked below. Users can scroll past the main app content to see the sidebars on tablets/phones.
- Desktop layouts remain centered and untouched.

## Premium Chrome: Background + News Strip + Footer (Feb 2026)
- **Premium background** (in `+html.tsx` body CSS): soft purple → white → lavender gradient (radial + diagonal) layered on a fixed `body` with a slow 22-second `::before` radial glow that drifts across the viewport. Non-intrusive, low-contrast, sits behind everything via `z-index: 0`.
- **News-strip marquee** (`components/AppChrome.tsx` `NewsStrip`): thin strip at the very top (height auto-adapts). Dark-to-light purple gradient (`#4C1D95 → #8B5CF6`) with a **"lazy gleam"** (`::after` diagonal light streak animated 14s via `@keyframes cbepl-gleam`). Content scrolls right-to-left via pure CSS `@keyframes cbepl-scroll`, pauses on hover, 55s desktop / 40s mobile. Items are fetched from `GET /api/calendar/events` and mixed with 3 default items; `DEFAULT_NEWS` array is easy to update.
- **Global footer** (`GlobalFooter`): minimal centered "© {year} CBE Planner. All rights reserved." — year auto-generated via `new Date().getFullYear()`. Soft gray text, frosted white backdrop with `backdrop-filter: blur`. Purple link to cbeplanner.com.
- **Reusable pattern**: `AppChrome` wraps the root `<Stack>` in `app/_layout.tsx` with `showStrip` / `showFooter` props for per-page opt-out later. Web-only — returns children directly on native so RN layouts stay untouched.
- **Responsive**: 640px breakpoint shrinks marquee text & speeds up scroll; footer stacks cleanly; background scales via `background-attachment: fixed`.
- **Existing layouts untouched**: `contentStyle: transparent` on the root Stack lets the body gradient show through; all `(teacher)` / `(admin)` / landing layouts continue to work.

## Next Tasks
1. AppLayout sidebar redesign across all post-login dashboard pages
2. Continue `server.py` modularization (extract `/auth`, `/wallet`, `/admin` into `routes/`)
3. Past Papers feature
4. Firebase Admin SDK integration
5. Android APK build + Play Store signing
