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

### Admin Panel Enhancement (DONE - Dec 2025)
**New Features:**
1. **Move Items Feature (CASCADE)**
   - Move strands between subjects (all substrands, SLOs cascade automatically)
   - Move substrands between strands (all SLOs cascade automatically)
   - Move SLOs between substrands
   - Change subject grade assignments
   - Full hierarchy dropdown selectors for precise targeting

2. **Bulk Add Feature**
   - Text Input mode: Paste multiple items (one per line)
   - Table Input mode: Spreadsheet-style data entry with name + description
   - Supports strands, substrands, and SLOs bulk creation
   - Automatic SLO mapping creation for bulk SLOs

3. **Improved UI**
   - Action buttons row for each list item (Move, Edit, Delete)
   - Bulk Add button in header when parent is selected
   - Warning messages for cascade operations
   - Item count indicator in bulk add modal

**New Backend Endpoints:**
- `PUT /api/admin/strands/{id}/move` - Move strand with cascade
- `PUT /api/admin/substrands/{id}/move` - Move substrand with cascade
- `PUT /api/admin/slos/{id}/move` - Move SLO
- `PUT /api/admin/subjects/{id}/change-grade` - Reassign subject grade
- `POST /api/admin/strands/bulk` - Bulk create strands
- `POST /api/admin/substrands/bulk` - Bulk create substrands
- `POST /api/admin/slos/bulk` - Bulk create SLOs with mappings
- `GET /api/admin/curriculum-tree` - Full curriculum hierarchy for dropdowns
- `GET /api/admin/reference-data` - Get all competencies, values, PCIs
- `PUT /api/admin/slo-mappings/bulk` - Bulk update SLO mappings

### SLO Mapping Editor (DONE - Dec 2025)
**Features:**
1. **Per-SLO Mapping Editor**
   - Click "Link" button on any SLO to edit its mappings
   - Select Core Competencies (7 options)
   - Select Core Values (8 options)
   - Select PCIs (20+ options)
   - Shows current selection count

2. **Bulk SLO Mapping Editor**
   - Select multiple SLOs at once (Select All / Deselect All)
   - Apply same competencies, values, and PCIs to all selected
   - Useful for SLOs with similar characteristics

3. **User-Friendly Guides**
   - Each modal has clear instructions
   - Bulk add shows context-specific help for strands, substrands, SLOs
   - Step-by-step guidance in bulk mapping editor

### Production Readiness (DONE - Dec 2025)
- **Global Error Handler Middleware:** Catches unhandled exceptions and returns user-friendly messages
- **Security Headers Middleware:** Adds X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, etc.
- **Rate Limiting:** Prevents abuse of M-Pesa payment initiation (5 requests/min) and lesson generation (10 requests/min)
- **Idempotency Management:** Prevents duplicate payment initiations
- **Transaction Locking:** Prevents race conditions during lesson plan generation
- **Structured Logging:** ProductionLogger class for sanitized, structured logs
- **Input Validation:** Centralized phone number and amount validation
- **Frontend Error Handler:** Utility for mapping API errors to user-friendly messages

### Critical Fixes (Dec 2025)

#### PART 1: Curriculum Ordering Fixed
- **REMOVED all automatic sorting** from strands, substrands, and SLOs API endpoints
- Strands and substrands now return in **curriculum teaching order** (database insertion order)
- Only subjects are sorted alphabetically for user convenience
- No client-side sorting in frontend code

**Affected Endpoints:**
- `GET /api/strands` - NO SORT (curriculum order)
- `GET /api/substrands` - NO SORT (curriculum order)
- `GET /api/slos` - NO SORT (curriculum order)
- `GET /api/subjects` - SORTED alphabetically (user convenience)

#### PART 2: PCIs, Values, Core Competencies Fixed
**Root Cause:** Grade 7, 8, 9 SLOs were missing `slo_mappings` records that link them to PCIs, values, and competencies.

**Fix Applied:**
1. Created 367 new SLO mappings for Grade 9 SLOs
2. Updated lesson plan generation to check multiple data sources:
   - First: Check `slo_mappings` collection (original format)
   - Second: Check `learning_activities` for embedded data (Grade 9 format)
   - Third: Use intelligent defaults if no data found
3. Lesson plans now include `inquiryQuestions` field
4. Total SLO mappings: 1,385

**Lesson Plan Generation Logic:**
```
1. Query slo_mappings by sloId
2. If found: fetch competencies, values, PCIs from reference collections
3. If not found: check learning_activities for embedded core_competencies, values, pci
4. If still missing: use subject-appropriate defaults
```

### Curriculum Data (UPDATED - Dec 2025)
- **Grades:** 12 (PP1, PP2, Grade 1-10)
- **Subjects:** ~50 unique subjects across all grades
- **Strands:** 90+ strands
- **Substrands:** 328+ substrands
- **SLOs:** 1,400+ Specific Learning Outcomes
- **SLO Mappings:** 1,600+ (linking SLOs to competencies/values/PCIs)
- **Learning Activities:** 602 detailed activity sets

### Grade 7 Complete Curriculum Data (UPDATED - Dec 2025)
**Seeding Script:** `/app/backend/seed_grade7_complete.py`

| Subject | Strands | Substrands | SLOs | SLO Mappings |
|---------|---------|------------|------|--------------|
| Mathematics | 5 | 18 | 78 | 78 |
| Integrated Science | 4 | 11 | 43 | 43 |
| English | 4 | 11 | 43 | 43 |
| Kiswahili | 4 | 8 | 32 | 32 |
| Social Studies | 5 | 8 | 32 | 32 |

**Mathematics Strands (Teaching Order):**
1. Numbers (Whole Numbers, Factors, Multiples, Fractions, Decimals, Squares and Square Roots)
2. Algebra (Algebraic Expressions, Linear Equations)
3. Measurements (Length, Area, Volume and Capacity, Mass, Time, Money)
4. Geometry (Lines and Angles, Plane Figures)
5. Data Handling and Probability (Data Collection and Organization, Probability)

**Integrated Science Strands (Teaching Order):**
1. Scientific Investigation (Introduction, Laboratory Safety, Apparatus and Instruments)
2. Mixtures, Elements and Compounds (Classification, Separation Methods)
3. Living Things and their Environment (Classification, Cell, Human Body Systems)
4. Force and Energy (Force, Pressure, Light)

**English Strands (Teaching Order):**
1. Listening and Speaking (Polite Language, Listening Comprehension, Oral Narratives)
2. Reading (Comprehension, Vocabulary Development, Literary Appreciation)
3. Grammar in Use (Parts of Speech, Sentence Structure, Tenses)
4. Writing (Creative Writing, Functional Writing)

**Kiswahili Strands (Teaching Order):**
1. Kusikiliza na Kuzungumza (Mazungumzo, Kusikiliza kwa Ufahamu)
2. Kusoma (Kusoma kwa Ufahamu, Fasihi Simulizi)
3. Kuandika (Insha za Ubunifu, Barua)
4. Sarufi (Ngeli za Nomino, Vitenzi)

**Social Studies Strands (Teaching Order):**
1. Social Studies and Career Development (Career Awareness)
2. Community Service-Learning (CSL Project)
3. People and Relationships (The Family, Population)
4. Natural and Historic Built Environments (Physical Features, Climate and Weather)
5. Political Developments and Governance (Government, Democracy and Human Rights)
- **7 Core Competencies:** Communication and Collaboration, Critical Thinking and Problem Solving, Creativity and Imagination, Citizenship, Digital Literacy, Learning to Learn, Self-Efficacy
- **8 Core Values:** Love, Responsibility, Respect, Unity, Peace, Patriotism, Social Justice, Integrity
- **15+ PCIs:** Environmental Conservation, Safety and Security, Health Education, Life Skills, Financial Literacy, Citizenship Education, and more
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
- `backend/server.py` - Main FastAPI application with production middleware
- `backend/app/production_utils.py` - Production utilities (logging, rate limiting, validation)
- `backend/mpesa_service.py` - M-Pesa integration
- `backend/Dockerfile` - Production-ready Docker configuration for Render
- `frontend/app/(teacher)/home.tsx` - Main lesson generation UI with error handling
- `frontend/app/(teacher)/profile.tsx` - Wallet & M-Pesa UI with error handling
- `frontend/utils/errorHandler.ts` - Centralized error handling utility

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

### Data Import System (DONE - Dec 2025)
A comprehensive bulk data import system for curriculum data:

**Features:**
1. **CSV Upload (Primary Method)**
   - Download CSV template with all required columns
   - Upload filled CSV file for validation
   - Preview data before saving (shows strands, substrands, SLOs count)
   - Error and warning display
   - Grade/Subject selection before saving

2. **PDF Extraction Helper Tool**
   - Upload KICD curriculum PDFs
   - Automatic extraction of strands, substrands, SLOs
   - Generates downloadable CSV for review/editing
   - Handles varied PDF formats (STRAND 1.0, 1.0 Name patterns)

3. **Import History Tracking (NEW - Dec 2025)**
   - Records all data imports with filename, grade, subject
   - Shows stats: strands, substrands, SLOs created
   - Timestamp and user who imported
   - Refresh button to reload history

4. **CSV Column Support:**
   - strand_name (required)
   - substrand_name (required)
   - slo_name (required)
   - slo_description
   - introduction_activities
   - development_activities
   - conclusion_activities
   - extended_activities
   - competencies
   - values
   - pcis
   - assessment_methods
   - learning_resources

**Backend Endpoints:**
- `GET /api/admin/import/template` - Download CSV template
- `POST /api/admin/import/preview-csv` - Upload and parse CSV
- `POST /api/admin/import/extract-pdf` - Extract from PDF to CSV
- `POST /api/admin/import/save` - Save imported data to database
- `GET /api/admin/import/history` - Get import history records

**Frontend:**
- New admin tab: "Import" with cloud-upload icon
- `/app/frontend/app/(admin)/data-import.tsx` - Full import UI with history section

**Dependencies Added:**
- `expo-document-picker` - For file selection on mobile/web

### UI Improvements (DONE - Dec 2025)
1. **Login Footer:** "Developed by LEGIT LAB" centered in footer
2. **Dashboard Tiles:** Notes Generator, Schemes of Work, and Revision Papers marked as "Coming Soon"
3. **Quick Stats:** Updated to show Free Lesson status and Wallet Balance

## Next Steps / Backlog
- [x] Production-readiness middleware (error handling, security headers, rate limiting) - DONE Dec 2025
- [x] Play Store preparation (app.json, eas.json, privacy policy, listing) - DONE Dec 2025
- [x] Fix admin panel subjects not displaying after add - DONE Dec 2025
- [x] Sync admin panel subjects with teacher view (removed KICD whitelist filter) - DONE Dec 2025
- [x] Seed Grade 7, 8, 9 curriculum data from KICD rationalized PDFs - DONE Dec 2025
- [x] Data Import System (CSV upload + PDF extraction helper) - DONE Dec 2025
- [x] Import History Tracking feature - DONE Dec 2025
- [x] Center "Developed by LEGIT LAB" text - DONE Dec 2025
- [x] Mark Notes/Schemes as Coming Soon - DONE Dec 2025
- [ ] User verification of M-Pesa MPESA_CALLBACK_URL configuration on Render
- [ ] User verification of mobile app stability (Expo Go back button issues)
- [ ] Deploy backend to Render (https://cbeplanner.onrender.com)
- [ ] Deploy frontend to Vercel (web)
- [ ] Build Android AAB using `eas build --platform android --profile production`
- [ ] Submit to Google Play Store
- [ ] Test with production M-Pesa credentials
- [ ] Debug Expo Go stability issues (if still occurring)
- [ ] Grade 8 data audit against source PDF
- [ ] Full codebase audit to remove dead code

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
- `backend/seed_junior_secondary.py` - Seeds Grade 7, 8, 9 curriculum data (NEW)
- `backend/parse_kicd_pdfs.py` - Parses KICD rationalized curriculum PDFs and seeds database (NEW)

## Junior Secondary Curriculum Data (DONE - Dec 2025)
Successfully downloaded and processed KICD rationalized curriculum designs from arena.co.ke:

**Downloaded PDFs (in `/app/backend/pdfs/`):**
- Grade 7: mathematics.pdf, integrated_science.pdf, social_studies.pdf, pre_technical_studies.pdf, english.pdf, agriculture.pdf
- Grade 8: Same subjects
- Grade 9: Same subjects

**Seeded Data for Grades 7, 8, 9:**
| Subject | Strands | Substrands | SLOs |
|---------|---------|------------|------|
| Mathematics | 5 | 22 | 69 |
| Integrated Science | 5 | 19 | 59 |
| Social Studies | 5 | 16 | 48 |
| Pre-Technical Studies | 5 | 14 | 56 |

**Database Totals After Seeding:**
- Grades: 12
- Subjects: 147
- Strands: 93
- Substrands: 335
- SLOs: 1,248
- Learning Activities: 134

## Grade 8 Complete Curriculum Data (DONE - Dec 2025)
User uploaded official KICD Grade 8 curriculum design PDFs (April 2024 formatted versions).

**PDFs Processed:**
- Mathematics-Grade-8-Design-Formatted-April-2024.pdf
- Integrated-Science-Grade-8-Design-Formatted-April-2024.pdf
- Social-Studies-Grade-8-Formatted-April-2024.pdf
- English-Grade-8-Design-Formatted-April-2024.pdf
- Kiswahili-Grade-8-.pdf

**Grade 8 Data Seeded (with full learning experiences):**
| Subject | Strands | Substrands | SLOs | Activity Sets |
|---------|---------|------------|------|---------------|
| Mathematics | 5 | 27 | 82 | 27 |
| Integrated Science | 3 | 8 | 30 | 8 |
| Social Studies | 4 | 9 | 31 | 9 |
| English | 4 | 8 | 24 | 8 |
| Kiswahili | 4 | 8 | 17 | 8 |

**Learning Activities Include:**
- Introduction activities
- Development activities  
- Conclusion activities
- Inquiry Questions
- Core Competencies
- Values
- PCIs (Pertinent and Contemporary Issues)

**Updated Database Totals:**
- Grades: 12
- Subjects: 147
- Strands: 95
- Substrands: 331
- SLOs: 1,195
- Learning Activities: 194

## Grade 9 Complete Curriculum Data (DONE - Dec 2025)
User uploaded official KICD Grade 9 curriculum design PDFs. Data extracted **directly from PDFs** - no AI-generated content.

**PDFs Processed:**
- GRADE.9.ENGLISH.pdf
- GRADE.9.MATHEMATICS.pdf  
- GRADE.9.INTEGRATED.SCIENCE.pdf
- Kiswahili-Grade-9.pdf
- Social-Studies-Grade-9-Design-Formatted-April-2024.pdf

**Grade 9 Data Seeded (with full learning experiences from actual PDFs):**
| Subject | Strands | Substrands | SLOs | Activity Sets |
|---------|---------|------------|------|---------------|
| Mathematics | 5 | 19 | 117 | 117 |
| Integrated Science | 3 | 9 | 46 | 46 |
| Social Studies | 5 | 18 | 86 | 86 |
| English | 5 | 15 | 50 | 50 |
| Kiswahili | 4 | 10 | 36 | 36 |

**Mathematics Strands (from PDF):**
1. Numbers (Integers, Cubes and Cube Roots, Indices and Logarithms, Compound Proportions)
2. Algebra (Matrices, Equations of a Straight Line, Linear Inequalities)
3. Measurements (Area, Volume, Mass/Weight/Density, Time/Distance/Speed, Money, Approximations)
4. Geometry (Coordinates and Graphs, Scale Drawing, Similarity and Enlargement, Trigonometry)
5. Data Handling and Probability (Grouped Data, Probability)

**Social Studies Strands (from PDF):**
1. Social Studies and Career Development (Pathway Choices, Pre-career Support Systems)
2. Community Service-Learning (CSL Project)
3. People and Relationships (Early Humans, Indigenous Knowledge, Poverty, Population, Conflict Resolution, Relationships)
4. Natural and Historic Built Environments (Topographical Maps, Internal Land Forming, River Projects, Conservation, Heritage Sites)
5. Political Developments and Governance (Constitution of Kenya, Civic Engagement, Bill of Rights, Cultural Globalization)

**Learning Activities Include (exactly as in PDFs):**
- Learning experiences (Introduction, Development, Conclusion)
- Key Inquiry Questions
- Core Competencies
- Values  
- PCIs (Pertinent and Contemporary Issues)

**Seeding Script:** `/app/backend/seed_grade9_accurate.py`
- Extracts data directly from PDFs (no hallucinated content)
- Links to existing subjects (no duplicates)
- Uses ObjectId for all relationships (fixed previous string ID issue)

**Updated Database Totals After Grade 9 Seeding:**
- Total Grade 9 Strands: 22
- Total Grade 9 Substrands: 71
- Total Grade 9 SLOs: 335
- Total Grade 9 Learning Activities: 335

## Grade 10 Complete Curriculum Data (DONE - Dec 2025)
User uploaded official KICD Grade 10 curriculum design PDFs for 5 subjects.

**PDFs Processed:**
- Agriculture.pdf
- Computer_Science.pdf
- Fasihi_ya_Kiswahili.pdf
- History_and_Citizenship.pdf
- Home_Science.pdf

**Grade 10 Data Seeded (with full learning experiences, SLO mappings):**
| Subject | Strands | Substrands | SLOs | SLO Mappings | Learning Activities |
|---------|---------|------------|------|--------------|---------------------|
| Agriculture | 3 | 17 | 54 | 54 | 17 |
| Computer Science | 3 | 17 | 60 | 60 | 17 |
| Fasihi ya Kiswahili | 3 | 8 | 16 | 16 | 8 |
| History and Citizenship | 4 | 15 | 30 | 30 | 15 |
| Home Science | 3 | 12 | 25 | 25 | 12 |
| **TOTAL** | **16** | **69** | **185** | **185** | **69** |

**Agriculture Strands (Teaching Order):**
1. Crop Production (7 substrands: Agricultural Land, Properties of Soil, Land Preparation, Field Management Practices, Growing Selected Crops, Crop Protection, General Crop Harvesting)
2. Animal Production (5 substrands: Breeds of Livestock, Animal Handling and Safety, General Animal Health, Bee Keeping, Animal Rearing Project)
3. Agricultural Technologies and Entrepreneurship (5 substrands: Tools and Equipment, Product Processing and Value Addition, Establishing Agricultural Enterprise, Marketing Agricultural Produce, Composting Techniques)

**Computer Science Strands (Teaching Order):**
1. Foundation of Computer Science (7 substrands: Evolution and Development of Computers, Computer Organisation and Architecture, Input/Output Devices, Computer Storage, CPU, Operating System, Computer Setup)
2. Computer Networking (4 substrands: Data Communication, Data Transmission Media, Computer Network Elements, Network Topologies)
3. Software Development (6 substrands: Computer Programming Concepts, Program Development, Identifiers and Operators, Control Structures, Subprograms, Problem Solving)

**Fasihi ya Kiswahili Strands (Teaching Order):**
1. Fasihi Simulizi (Oral Literature)
2. Ushairi (Poetry)
3. Bunilizi (Creative Writing)

**History and Citizenship Strands (Teaching Order):**
1. Themes in Kenyan History and Citizenship
2. Themes in African History and Citizenship
3. International Themes in History and Citizenship
4. Contemporary Themes in History and Citizenship

**Home Science Strands (Teaching Order):**
1. Foods and Nutrition (4 substrands: Introduction to Foods and Nutrition, Meal Planning, Cooking Methods, Food Preservation)
2. Home Management (5 substrands: Hygiene During Puberty, Home Safety and First Aid, Housing the Family, Budgeting, Consumer Education)
3. Clothing and Textiles (3 substrands: Sewing Tools and Equipment, Textile Fibres, Clothing Construction)

**SLO Mappings Include:**
- Competency IDs (linked to Core Competencies)
- Value IDs (linked to Core Values)
- PCI IDs (linked to Pertinent and Contemporary Issues)

**Seeding Script:** `/app/backend/seed_grade10_complete.py`
- Extracts data from the script (curriculum data hardcoded from PDFs)
- Properly deletes existing data before re-seeding (idempotent)
- Links to existing subjects or creates new ones
- Preserves curriculum teaching order

**Updated Database Totals After Grade 10 Seeding:**
- Total Grades: 12
- Total Subjects: 52+
- Total Strands: 100+
- Total Substrands: 400+
- Total SLOs: 1,400+
- Total SLO Mappings: 1,600+
- Total Learning Activities: 600+

## Grade 8, 9, 10 Additional Subjects (DONE - Dec 2025)
User uploaded 5 additional PDF files containing curriculum for remaining subjects:
- G8.pdf (Grade 8 subjects)
- G9.pdf (Grade 9 subjects)
- G10.pdf, G102.pdf, G103.pdf (Grade 10 subjects)

**Seeding Script:** `/app/backend/seed_remaining_subjects.py`

**NEWLY SEEDED SUBJECTS:**

| Subject                       | Grades | Strands | Substrands | SLOs |
|-------------------------------|--------|---------|------------|------|
| Agriculture and Nutrition     | 2      | 4       | 20         | 12   |
| Arabic                        | 7      | 4       | 36         | 15   |
| Biology                       | 1      | 7       | 69         | 21   |
| Business Studies              | 1      | 3       | 24         | 54   |
| Chemistry                     | 1      | 2       | 12         | 8    |
| Christian Religious Education | 10     | 4       | 22         | 22   |
| Creative Arts and Sports      | 2      | 9       | 152        | 122  |
| Film                          | 1      | 3       | 47         | 39   |
| Geography                     | 1      | 3       | 40         | 19   |
| Hindu Religious Education     | 10     | 6       | 92         | 73   |
| Islamic Religious Education   | 10     | 1       | 6          | 11   |
| Mandarin Chinese              | 7      | 4       | 38         | 36   |
| Physical Education            | 1      | 3       | 56         | 22   |
| Physics                       | 1      | 16      | 200        | 127  |
| Pre-Technical Studies         | 3      | 5       | 42         | 28   |

**FINAL DATABASE TOTALS (Dec 2025):**
- Total Subjects: 57
- Total Strands: 147
- Total Substrands: 1,195
- Total SLOs: 1,503
- Total SLO Mappings: 1,616
- Total Learning Activities: 831

**Subjects with Missing/Incomplete Data (Require Manual Review):**
- Literature in English (different strand format in PDF)
- Theatre (merged with Literature in PDF)
- Performing Arts (merged with Creative Arts)
- French, German (G103.pdf - different extraction patterns needed)
- Indigenous Languages (G103.pdf)

**Data Extraction Notes:**
- PDFs use varied formats (STRAND 1.0: vs 1.0 Strand Name)
- Some subjects are combined in PDF sections
- Senior School (Grade 10) PDFs have different curriculum structure
