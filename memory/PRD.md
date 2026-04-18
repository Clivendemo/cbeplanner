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
