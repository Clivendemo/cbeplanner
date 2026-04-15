# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB (Motor async)
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Seed Pipeline (v2 — April 14, 2026)

### Data Model
```
Subject (gradeIds as list)
  └── Strands
       └── Substrands (number_of_lessons: int)
            ├── learning_activities (substrandId: string)
            │    ├── introduction_activities, development_activities
            │    ├── conclusion_activities, extended_activities
            │    ├── learning_resources, assessment_methods
            └── SLOs (substrandId: string, order: int)
                 └── slo_mappings
                      ├── competencyIds (populated, not empty)
                      ├── valueIds (populated)
                      ├── pciIds (populated)
                      └── assessmentIds (populated)
```

### Key Features
- `get_or_create_*` helpers prevent duplicate competencies/values/PCIs/assessments
- SLO mappings are fully populated (not empty arrays)
- `gradeIds` stored as list
- `substrandId` consistently string
- Safe reseeding (deletes only subject-scoped data, preserves globals)
- `lesson_slos` cleaned up on reseed
- SLO-level overrides supported (per-SLO competencies if extractor provides them)

## Lesson SLO System
- **Service**: `lesson_slo_service.py` — sync, auto-generate, CRUD
- **Collection**: `lesson_slos` (unique on substrandId + lessonNumber)
- Auto-sync on substrand create/update
- Admin can edit (marks isDraft=False, protected from regeneration)

## Scheme Draft Workflow
- Save draft → list/get → preview (free) → regenerate → download (KES 15)
- Re-downloads of paid drafts are free
- Scheme generation prefers lesson_slo outcomes and inquiry questions

## Collections
- `users`, `wallets`, `wallet_ledger`, `wallet_transactions`
- `grades`, `subjects`, `strands`, `substrands`, `slos`
- `slo_mappings`, `learning_activities`, `competencies`, `values`, `pcis`
- `assessment_methods`
- `substrand_lessons` (legacy), `lesson_slos` (current)
- `lesson_plans`, `schemes`, `scheme_drafts`

## Pricing
- Lesson Plans: KES 2 each (5 free on signup)
- Notes Download: KES 1 each (first one free)
- Scheme Download: KES 15
- Previews: Free

## Admin Emails
- mail2clive@gmail.com (primary)
- testadmin2026@gmail.com (test account)

## Next Tasks
1. Frontend admin panel: Lesson SLO cards in substrand view
2. Frontend: Scheme draft workflow UI
3. Firebase Admin SDK integration
4. Past Papers feature
5. Refactor server.py into route modules
