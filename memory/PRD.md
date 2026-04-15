# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB (Motor async)
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Grade System (Canonical Names)
- PP1, PP2 — Pre-Primary
- Grade 1 through Grade 12 — Primary / Junior / Senior School
- Normalizer handles: "grade 1", "GRADE 1", "Grade One", "PP1", "Pre-Primary 1", "Form 1", "Class 5", "Junior School Grade 8"

## Seed Pipeline (v2)
- `scripts/ai_extractor.py` — Gemini 2.5 Flash extraction with strengthened grade detection
- `scripts/grade_utils.py` — Grade normalization + DB matching (27 test cases)
- `scripts/seed_script_generator.py` — Generates complete Python seed scripts with:
  - Populated SLO mappings (competencies, values, PCIs, assessments)
  - `get_or_create_*` helpers (case-insensitive, no duplicates)
  - Robust `get_or_create_grade` with normalisation + alias scan
  - `gradeIds` as list, `substrandId` as string, `number_of_lessons` as int

## Lesson SLO System
- `lesson_slo_service.py` — sync, auto-generate, CRUD
- `lesson_slos` collection (unique on substrandId + lessonNumber)
- Auto-sync on substrand create/update

## Scheme Draft Workflow
- Save draft → list/get → preview (free) → regenerate → download (KES 15)
- Re-downloads of paid drafts are free
- Generation prefers lesson_slo outcomes and inquiry questions

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
