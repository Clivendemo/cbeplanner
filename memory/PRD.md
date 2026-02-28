# CBE Lesson Planner - Product Requirements Document

## Original Problem Statement
Build a production-ready Competency-Based Education (CBE) lesson planning system for Kenyan teachers with:
- M-Pesa wallet integration for payments
- 5 free lesson plans on signup, then KES 2 per plan
- Firebase authentication
- MongoDB Atlas database
- Deployment to Render (backend) and Vercel (frontend)

## What's Been Implemented

### Core Features (DONE)
- **User Authentication:** Firebase-based signup/login with JWT verification
- **Wallet System:** M-Pesa STK Push integration (SANDBOX mode)
- **Business Logic:** 5 free lessons on signup, KES 2 per subsequent plan
- **Lesson Plan Generator:** Duration-aware lesson plans (25-80 min) with Core Competencies, Core Values, and PCIs
- **Notes Generator:** Duration-aware teaching notes
- **Schemes of Work Generator:** Term-based curriculum planning
- **Admin Role:** Role-based access control for admin endpoints

### Curriculum Data (UPDATED - Dec 2025)
- **22 Subjects:** Literacy Activities, Mathematical Activities, Environmental Activities, English, Mathematics, Science and Technology, Social Studies, Chemistry, Computer Science, Community Service Learning, Fasihi ya Kiswahili, Kiswahili Lugha, Agriculture, Biology, Arabic, Aviation Technology, Building Construction, **Business Studies**, **Christian Religious Education (CRE)**, **Electrical Technology**, **Fine Arts**, **French**
- **60 Strands** across all subjects
- **235 Substrands** covering all curriculum areas
- **898 Specific Learning Outcomes (SLOs)**
- **89 Detailed Learning Activities** for lesson plan generation
- **7 Core Competencies:** Communication and Collaboration, Critical Thinking and Problem Solving, Creativity and Imagination, Citizenship, Digital Literacy, Learning to Learn, Self-Efficacy
- **8 Core Values:** Love, Responsibility, Respect, Unity, Peace, Patriotism, Social Justice, Integrity
- **15 PCIs:** Environmental Conservation, Safety and Security, Health Education, Life Skills, Financial Literacy, Citizenship Education, Gender Issues, Drug and Substance Abuse, Disaster Risk Reduction, Animal Welfare, Digital Citizenship, Climate Change, and more

#### New Subjects Added (Dec 2025):
1. **Business Studies** - 4 strands, 15 substrands, 79 SLOs, 11 activities
   - Business and Money Management
   - Business and Its Environment
   - Government and Global Influence in Business
   - Financial Records in Business

2. **Christian Religious Education (CRE)** - 4 strands, 23 substrands, 102 SLOs, 21 activities
   - The Old Testament
   - The New Testament
   - Church in Action
   - Christian Living Today

3. **Electrical Technology** - 4 strands, 13 substrands, 54 SLOs, 13 activities
   - Fundamentals of Electrical Technology
   - Electrical Machines
   - Electrical Installation
   - Electronics

4. **Fine Arts** - 3 strands, 11 substrands, 45 SLOs, 11 activities
   - Picture Making Techniques (2D Art)
   - Multimedia Arts (2D Art)
   - Indigenous Crafts (3D Art)

5. **French** - 4 strands, 19 substrands, 57 SLOs, 13 activities
   - Listening and Speaking
   - Reading
   - Writing
   - Grammar

### Database (DONE)
- MongoDB Atlas connection configured
- Wallet ledger for atomic, idempotent transactions
- Database indexes for performance

### Deployment Prep (DONE - Dec 2025)
- Dockerfile configured with `$PORT` environment variable (Render default: 10000)
- Health check endpoints: `GET /health` (simple) and `GET /api/health` (detailed)
- `.env.example` with all required variables documented
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- Clean requirements.txt with production-only dependencies (removed emergentintegrations and dev tools)

## Key Files
- `backend/server.py` - Main FastAPI application
- `backend/mpesa_service.py` - M-Pesa integration
- `backend/Dockerfile` - Production-ready Docker configuration for Render
- `frontend/app/(teacher)/home.tsx` - Main lesson generation UI
- `frontend/app/(teacher)/profile.tsx` - Wallet & M-Pesa UI

## Known Issues
1. **Expo Go Instability (P1):** User reported app crashes on mobile. May need further debugging.
2. **English PDF Data (P2):** English curriculum PDF extraction failed; data not imported.

## Important Notes
- **M-Pesa is in SANDBOX mode.** `MPESA_CALLBACK_URL` must be updated with production URL after deployment.
- Render sets `$PORT` automatically - Dockerfile is configured to use it.

## Render Deployment Steps
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Set environment variables in Render dashboard
5. Deploy (Render auto-detects Dockerfile)
6. Update `MPESA_CALLBACK_URL` with Render URL

## Next Steps / Backlog
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Test with production M-Pesa credentials
- [ ] Debug Expo Go stability issues (if still occurring)
- [ ] Import English curriculum data (requires OCR)
- [ ] Add more subjects from KICD curriculum PDFs as needed

## Admin Curriculum Management (DONE - Dec 2025)
The admin panel now includes a complete curriculum management interface:

**Features:**
- **Two View Modes:**
  - "All Data" - View and manage all entities in flat lists
  - "Navigate Hierarchy" - Drill down: Grade → Subject → Strand → Substrand → SLOs & Activities

- **Full CRUD for:**
  - Grades (name, order)
  - Subjects (name, linked to grades)
  - Strands (name, linked to subjects)
  - Substrands (name, linked to strands)
  - SLOs (name, description, linked to substrands)
  - Learning Activities (introduction, development, conclusion, extended activities)
  - Competencies, Values, PCIs

- **Learning Activities Management:**
  - Access via "Manage Learning Activities" button when viewing a substrand's SLOs
  - Add/edit/remove activities for each phase: Introduction, Development, Conclusion, Extended
  - Data saves directly to MongoDB and is immediately available for lesson plan generation

**API Endpoints Added:**
- `GET /api/admin/learning-activities` - List all or filter by substrandId
- `GET /api/admin/learning-activities/by-substrand/{id}` - Get activities for a substrand
- `PUT /api/admin/learning-activities/by-substrand/{id}` - Create or update (upsert)
- `POST /api/admin/learning-activities` - Create new
- `DELETE /api/admin/learning-activities/{id}` - Delete

## Seeding Scripts
- `backend/seed_new_subjects.py` - Seeds curriculum structure (subjects, strands, substrands, SLOs)
- `backend/seed_new_activities.py` - Seeds learning activities for lesson generation
- `backend/seed_curriculum_data.py` - Original seeding script
- `backend/seed_activities.py` - Original activities script
