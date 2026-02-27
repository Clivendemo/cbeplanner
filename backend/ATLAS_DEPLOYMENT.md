# MongoDB Atlas Deployment Guide
## CBE Lesson Planner Database

---

## 📊 Database Summary

| Collection | Documents | Description |
|------------|-----------|-------------|
| `grades` | 12 | Grade 1-12 |
| `subjects` | 11 | Chemistry, Math, English, etc. |
| `strands` | 22 | Curriculum strands per subject |
| `substrands` | 80 | Sub-strands per strand |
| `slos` | 320 | Specific Learning Outcomes |
| `competencies` | 6 | Core competencies (CBC) |
| `values` | 7 | Core values (CBC) |
| `pcis` | 6 | Pertinent & Contemporary Issues |
| `assessments` | 7 | Assessment methods |
| `activities` | 13 | Learning activities |
| `slo_mappings` | 9 | SLO to competencies/values mapping |
| `users` | 4 | User accounts |
| `lesson_plans` | 14 | Generated lesson plans |
| `notes` | 1 | Generated notes |
| `schemes` | 3 | Schemes of work |
| `wallet_transactions` | 1 | M-Pesa transactions |

---

## 🚀 MongoDB Atlas Setup Steps

### Step 1: Create Atlas Account & Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up / Log in
3. Click **"Build a Database"**
4. Choose **FREE** tier (M0 Sandbox)
5. Select a cloud provider and region (recommend AWS, closest to Kenya)
6. Name your cluster (e.g., `cbeplanner-cluster`)
7. Click **"Create"**

### Step 2: Configure Database Access

1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Set:
   - Username: `cbeplanner_admin`
   - Password: (generate a strong password)
   - Role: **Atlas Admin**
4. Click **"Add User"**

### Step 3: Configure Network Access

1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (or add specific IPs)
   - This sets `0.0.0.0/0` for Railway/Vercel deployment
4. Click **"Confirm"**

### Step 4: Get Connection String

1. Go to **Database** (left sidebar)
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Select **Driver: Python** and **Version: 3.12 or later**
5. Copy the connection string:

```
mongodb+srv://cbeplanner_admin:<password>@cbeplanner-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

6. Replace `<password>` with your actual password

---

## 📥 Import Data to Atlas

### Method 1: Using MongoDB Compass (Recommended)

1. Download [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. Connect using your Atlas connection string
3. Create database: `cbeplanner`
4. For each collection:
   - Click **"Create Collection"**
   - Name it (e.g., `grades`)
   - Click **"Add Data" → "Import File"**
   - Select the JSON file from `db_export/`
   - Click **"Import"**

### Method 2: Using mongoimport CLI

```bash
# Install MongoDB Database Tools
# https://www.mongodb.com/try/download/database-tools

# Set your connection string
ATLAS_URI="mongodb+srv://cbeplanner_admin:YOUR_PASSWORD@cbeplanner-cluster.xxxxx.mongodb.net/cbeplanner"

# Import each collection
mongoimport --uri "$ATLAS_URI" --collection grades --file db_export/grades.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection subjects --file db_export/subjects.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection strands --file db_export/strands.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection substrands --file db_export/substrands.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection slos --file db_export/slos.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection competencies --file db_export/competencies.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection values --file db_export/values.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection pcis --file db_export/pcis.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection assessments --file db_export/assessments.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection activities --file db_export/activities.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection slo_mappings --file db_export/slo_mappings.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection users --file db_export/users.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection lesson_plans --file db_export/lesson_plans.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection notes --file db_export/notes.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection schemes --file db_export/schemes.json --jsonArray
mongoimport --uri "$ATLAS_URI" --collection wallet_transactions --file db_export/wallet_transactions.json --jsonArray
```

---

## ⚙️ Backend Environment Configuration

Update your backend `.env` file:

```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://cbeplanner_admin:YOUR_PASSWORD@cbeplanner-cluster.xxxxx.mongodb.net/cbeplanner?retryWrites=true&w=majority

# Database Name
DB_NAME=cbeplanner

# Other settings remain the same
JWT_SECRET=your-secure-jwt-secret
FIREBASE_PROJECT_ID=cbeplanner
FIREBASE_API_KEY=your-firebase-api-key
MPESA_CONSUMER_KEY=your-mpesa-key
MPESA_CONSUMER_SECRET=your-mpesa-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://your-backend.up.railway.app/api/payments/mpesa/callback
MPESA_ENV=sandbox
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

---

## 🔧 Railway Deployment

1. Push code to GitHub
2. Create new project in Railway
3. Connect your GitHub repo
4. Set root directory to `/backend`
5. Add environment variables (from above)
6. Deploy!

Your backend will be at: `https://your-app.up.railway.app`

---

## ✅ Verify Connection

Test your Atlas connection:

```python
from motor.motor_asyncio import AsyncIOMotorClient

uri = "mongodb+srv://cbeplanner_admin:PASSWORD@cluster.mongodb.net/cbeplanner"
client = AsyncIOMotorClient(uri)
db = client.cbeplanner

# Test
import asyncio
async def test():
    grades = await db.grades.count_documents({})
    print(f"Connected! Found {grades} grades")

asyncio.run(test())
```

---

## 📁 Exported Data Files Location

All data has been exported to: `/app/backend/db_export/`

Files:
- `grades.json` (12 documents)
- `subjects.json` (11 documents)
- `strands.json` (22 documents)
- `substrands.json` (80 documents)
- `slos.json` (320 documents)
- `competencies.json` (6 documents)
- `values.json` (7 documents)
- `pcis.json` (6 documents)
- `assessments.json` (7 documents)
- `activities.json` (13 documents)
- `slo_mappings.json` (9 documents)
- `users.json` (4 documents)
- `lesson_plans.json` (14 documents)
- `notes.json` (1 document)
- `schemes.json` (3 documents)
- `wallet_transactions.json` (1 document)

---

**Developed by LEGIT LAB**
