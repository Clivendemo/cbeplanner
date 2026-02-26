# CBE Lesson Planner 🎓

**Competency-Based Education (CBE) Lesson Planning System for Kenyan Teachers**

> Developed by **LEGIT LAB**

A production-ready, full-stack application that helps Kenyan teachers create KICD-aligned lesson plans, study notes, and schemes of work following the Competency-Based Curriculum (CBC).

## 🚀 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Expo (React Native) |
| **Database** | MongoDB Atlas |
| **Authentication** | Firebase Auth |
| **PDF Generation** | ReportLab, WeasyPrint |

---

## 📁 Project Structure

```
/
├── backend/
│   ├── Dockerfile          # Docker configuration
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template
│   └── seed_curriculum_data.py  # Data seeding script
├── frontend/
│   ├── app/                # Expo Router screens
│   ├── contexts/           # React Context (Auth)
│   ├── components/         # Reusable components
│   ├── firebaseConfig.ts   # Firebase setup
│   └── package.json        # Node dependencies
└── README.md
```

---

## 🔧 Backend Deployment (Railway)

### Prerequisites
- [Railway Account](https://railway.app/)
- [MongoDB Atlas Account](https://www.mongodb.com/atlas)
- [Firebase Project](https://console.firebase.google.com/)

### Step 1: Set Up MongoDB Atlas

1. Create a free cluster at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a database user with read/write permissions
3. Whitelist all IPs (`0.0.0.0/0`) for Railway access
4. Get your connection string (looks like: `mongodb+srv://user:pass@cluster.mongodb.net/`)

### Step 2: Deploy to Railway

1. **Connect Repository**
   ```bash
   # Push your code to GitHub first
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/cbe-planner.git
   git push -u origin main
   ```

2. **Create Railway Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set the **Root Directory** to `/backend`

3. **Configure Environment Variables**
   In Railway dashboard → Variables, add:
   ```
   MONGODB_URI=mongodb+srv://your-user:your-pass@cluster.mongodb.net/cbeplanner?retryWrites=true&w=majority
   DB_NAME=cbeplanner
   JWT_SECRET=your-secure-random-string-here
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_API_KEY=your-firebase-web-api-key
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Railway will automatically build using the Dockerfile
   - Your API will be available at: `https://your-app.up.railway.app`

### Step 3: Seed Initial Data

After deployment, seed the curriculum data:
```bash
# Using curl
curl -X POST https://your-app.up.railway.app/api/admin/seed

# Or run the seed script locally pointing to production DB
python seed_curriculum_data.py
```

---

## 🌐 Frontend Deployment (Vercel)

### For Web (Static Export)

1. **Build the Web App**
   ```bash
   cd frontend
   npx expo export -p web
   ```

2. **Deploy to Vercel**
   - Push the `frontend/dist` folder to a GitHub repo
   - Connect to [Vercel](https://vercel.com/)
   - Set build settings:
     - Framework: Other
     - Build Command: `npx expo export -p web`
     - Output Directory: `dist`

3. **Environment Variables**
   In Vercel dashboard, add:
   ```
   EXPO_PUBLIC_API_BASE_URL=https://your-backend.up.railway.app
   ```

### For Mobile (EAS Build)

1. **Install EAS CLI**
   ```bash
   npm install -g eas-cli
   eas login
   ```

2. **Configure eas.json**
   ```json
   {
     "build": {
       "production": {
         "env": {
           "EXPO_PUBLIC_API_BASE_URL": "https://your-backend.up.railway.app"
         }
       }
     }
   }
   ```

3. **Build for iOS/Android**
   ```bash
   # iOS
   eas build --platform ios --profile production
   
   # Android
   eas build --platform android --profile production
   ```

---

## 🔐 Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project named `cbeplanner`
3. Enable **Authentication** → **Email/Password** sign-in method

### 2. Get Configuration

1. Go to Project Settings → General
2. Scroll to "Your apps" → Add Web App
3. Copy the configuration values:
   - `apiKey` → `FIREBASE_API_KEY`
   - `projectId` → `FIREBASE_PROJECT_ID`

### 3. Update Frontend Config

Update `frontend/firebaseConfig.ts` with your Firebase credentials.

---

## 📱 Features

### For Teachers
- ✅ **Lesson Plan Generator** - Create CBC-aligned lesson plans (25-80 min)
- ✅ **Notes Generator** - Generate study notes for any topic
- ✅ **Schemes of Work** - Full term planning with breaks
- ✅ **PDF Export** - Download all documents as PDFs
- ✅ **Wallet System** - Pay-per-use with free trial

### For Admins
- ✅ **Curriculum Management** - CRUD for grades, subjects, strands
- ✅ **SLO Mapping** - Link outcomes to competencies & values
- ✅ **User Management** - View and manage teachers

---

## 🧪 Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
uvicorn server:app --reload --port 8001
```

### Frontend
```bash
cd frontend
yarn install
cp .env.example .env
# Edit .env with your backend URL
yarn start
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/verify` | Verify Firebase token |
| GET | `/api/grades` | List all grades |
| GET | `/api/subjects?gradeId=` | List subjects for grade |
| GET | `/api/strands?subjectId=` | List strands for subject |
| POST | `/api/lesson-plans/generate` | Generate lesson plan |
| POST | `/api/notes/generate` | Generate study notes |
| POST | `/api/schemes/generate` | Generate scheme of work |
| GET | `/api/health` | Health check |

---

## 📄 License

MIT License - Feel free to use and modify for educational purposes.

---

## 🤝 Support

For issues or questions, please open a GitHub issue or contact the development team.

---

**Developed with ❤️ by LEGIT LAB for Kenyan Teachers**

© 2025 LEGIT LAB. All rights reserved.
