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

## Next Tasks
1. Frontend: Scheme draft workflow UI (save/preview/edit/download)
2. Firebase Admin SDK integration
3. Past Papers feature
4. Refactor server.py into route modules
