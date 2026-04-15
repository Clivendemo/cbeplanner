# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB (Motor async)
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Lesson SLO Slots System (Current — April 14, 2026)

### Data Model
- **Collection**: `lesson_slo_slots` (unique index on substrandId + slot_index)
- **Source of truth**: `substrand.number_of_lessons` — NEVER inferred from SLO count
- **Slot structure**: outcome, description, key_inquiry_question (ONE per lesson), learning_activities, resources (structured with textbook support), assessment_methods, competencies, values, pcis, is_customized flag

### Resource Format
```json
[
  {"type": "textbook", "title": "Planet Math Grade 4", "pages": "12-15", "display_text": "Planet Math Grade 4, pp. 12-15"},
  {"type": "material", "display_text": "Number charts"}
]
```

### Endpoints
- `GET /api/admin/lesson-slots/{substrand_id}` — list + auto-generate
- `PUT /api/admin/lesson-slots/{substrand_id}/{slot_index}` — update (marks customized)
- `POST /api/admin/lesson-slots/{substrand_id}/{slot_index}/clear` — reset to fallback
- `POST /api/admin/lesson-slots/{substrand_id}/generate` — regenerate (preserves customized)
- `GET /api/lesson-slots/{substrand_id}` — teacher read-only

### Integration
- **Scheme generation** (`generate_scheme_v2`): Uses slots as primary source, parent SLO fallback
- **Lesson plan generation**: Uses `get_slot_for_scheme()` for slot data with formatted resources
- **Textbook rendering**: `format_resource_display()` handles structured resources

## Scheme Draft Workflow
- Save draft → list/get → preview (free) → regenerate → download (KES 15)
- Re-downloads of paid drafts are free

## Seed Pipeline (v2)
- Grade normalization (27 variants supported)
- Populated SLO mappings (competencies, values, PCIs, assessments)
- `get_or_create_*` helpers prevent duplicates

## Pricing
- Lesson Plans: KES 2 (5 free on signup)
- Notes Download: KES 1 (first free)
- Scheme Download: KES 15

## Admin Emails
- mail2clive@gmail.com (primary)
- testadmin2026@gmail.com (test)

## Next Tasks
1. **Phase 4**: Admin panel frontend for lesson slot management
2. Frontend: Scheme draft workflow UI
3. Firebase Admin SDK integration
4. Past Papers feature
5. Refactor server.py into route modules
