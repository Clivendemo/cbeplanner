# CBE Lesson Planner

**Competency-Based Education (CBE) Lesson Planning System for Kenyan Teachers**

> Developed by **LEGIT LAB**

A production-ready, full-stack application that helps Kenyan teachers create KICD-aligned lesson plans, study notes, and schemes of work following the Competency-Based Curriculum (CBC).

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Expo (React Native) |
| **Database** | MongoDB |
| **Authentication** | Firebase Auth |
| **PDF Generation** | ReportLab, WeasyPrint |
| **Payment** | M-Pesa Integration |

---

## Project Structure

```
/
├── backend/
│   ├── server.py               # FastAPI application
│   ├── curriculum_import.py    # CSV/PDF/Word import utilities
│   ├── seed_curriculum.py      # Database seeding script
│   ├── requirements.txt        # Python dependencies
│   └── curriculum_data/        # Extracted curriculum JSON files
├── frontend/
│   ├── app/
│   │   ├── (admin)/            # Admin panel screens
│   │   ├── (teacher)/          # Teacher screens
│   │   └── auth/               # Authentication screens
│   ├── contexts/               # React Context (Auth)
│   └── components/             # Reusable components
├── memory/
│   └── PRD.md                  # Product Requirements Document
└── README.md
```

---

## Features

### For Teachers
- **Lesson Plan Generator** - Create CBC-aligned lesson plans (25-80 min)
- **Notes Generator** - Generate study notes for any topic
- **Schemes of Work** - Full term planning with breaks
- **PDF Export** - Download all documents as PDFs
- **Wallet System** - Pay-per-use with M-Pesa integration

### For Admins
- **Curriculum Management** - Full CRUD for grades, subjects, strands, sub-strands, and SLOs
- **Hierarchy Navigation** - Navigate curriculum structure with breadcrumbs and back buttons
- **Auto-refresh** - Automatic data refresh after add/edit/delete/reorder operations
- **Bulk Operations** - Bulk add, edit, delete, and mapping for efficient data management
- **Data Import** - Import curriculum from:
  - CSV files (recommended for bulk data)
  - PDF extraction (KICD curriculum documents)
  - Word documents (.docx) - NEW
- **SLO Mapping** - Link outcomes to competencies, values, and PCIs

---

## Data Import Capabilities

### CSV Upload
- Download template with all curriculum columns
- Upload filled CSV with strands, sub-strands, SLOs, activities
- Preview and validate before import

### PDF Extraction
- Upload KICD curriculum design PDFs
- AI extracts strands, sub-strands, SLOs, and activities
- Review and download as CSV for editing

### Word Document Extraction (NEW)
- Upload Word documents (.docx) with curriculum data
- Extracts from both paragraphs and tables
- Same extraction patterns as PDF

---

## Database Seeding

Pre-extracted curriculum data is available in `/backend/curriculum_data/`:

```bash
# Seed all available curriculum data
cd backend
python seed_curriculum.py --all

# Seed specific file
python seed_curriculum.py --file curriculum_data/grade1_curriculum_complete.json
```

### Available Data:
- **Grade 1**: Mathematics, Environmental Activities, Creative Activities, CRE
- **Grade 10**: French, German, Indigenous Language, Mandarin, Power Mechanics

---

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/verify` | Verify Firebase token |
| GET | `/api/grades` | List all grades |
| GET | `/api/subjects?gradeId=` | List subjects for grade |
| GET | `/api/strands?subjectId=` | List strands for subject |
| POST | `/api/lesson-plans/generate` | Generate lesson plan |
| POST | `/api/admin/import/extract-pdf` | Extract curriculum from PDF |
| POST | `/api/admin/import/extract-docx` | Extract curriculum from Word doc |
| GET | `/api/health` | Health check |

---

## License

MIT License - Feel free to use and modify for educational purposes.

---

**Developed with love by LEGIT LAB for Kenyan Teachers**

© 2025 LEGIT LAB. All rights reserved.
