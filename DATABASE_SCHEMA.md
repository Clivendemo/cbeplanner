# CBE Planner - MongoDB Atlas Database Schema

## Overview
This document provides the complete database schema for loading JSON files into MongoDB Atlas without conflicts.

---

## IMPORTANT: JSON Format for MongoDB Atlas Import

When importing JSON to Atlas, use **Extended JSON v2** format:
- ObjectId: `{"$oid": "507f1f77bcf86cd799439011"}`
- Date: `{"$date": "2026-01-25T15:37:00.757Z"}`
- Arrays: Standard JSON arrays `["item1", "item2"]`

---

## Collection Relationships Diagram

```
grades (12 docs)
    ↓ gradeIds[]
subjects (51 docs)
    ↓ subjectId
strands (86 docs)
    ↓ strandId
substrands (302 docs)
    ↓ substrandId
slos (1193 docs)
    ↓ sloId
slo_mappings (1246 docs) ←→ competencies, values, pcis, assessments
    ↓ substrandId
learning_activities (602 docs)
```

---

## Collection Schemas

### 1. GRADES
**Purpose:** Grade levels (PP1, PP2, Grade 1-10)
**Count:** 12 documents

```json
{
  "_id": {"$oid": "69a06c0be7927ae20e67b2ce"},
  "name": "Grade 7",
  "order": 7
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | "Grade 7", "PP1", etc. |
| order | Integer | Yes | Numeric order (1-12) |

---

### 2. SUBJECTS
**Purpose:** Subjects available per grade
**Count:** 51 documents

```json
{
  "_id": {"$oid": "69a06caa533e4a4d60370bbe"},
  "name": "Mathematics",
  "gradeIds": ["69a06c0be7927ae20e67b2ce", "69a06c0be7927ae20e67b2cf"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Subject name |
| gradeIds | Array\<String\> | Yes | Array of grade _id strings |

**Note:** `gradeIds` contains STRING representations of ObjectIds (not ObjectId type)

---

### 3. STRANDS
**Purpose:** Main curriculum topics within a subject
**Count:** 86 documents

```json
{
  "_id": {"$oid": "69a06caa533e4a4d60370c10"},
  "name": "Numbers",
  "subjectId": "69a06caa533e4a4d60370be8"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Strand name |
| subjectId | String | Yes | Reference to subjects._id (as string) |

**CRITICAL:** Strands are returned in INSERTION ORDER. Do not sort alphabetically.

---

### 4. SUBSTRANDS
**Purpose:** Sub-topics within a strand
**Count:** 302 documents

```json
{
  "_id": {"$oid": "69a06caa533e4a4d60370bd5"},
  "name": "Whole Numbers",
  "strandId": "69a06caa533e4a4d60370bbf"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Substrand name |
| strandId | String | Yes | Reference to strands._id (as string) |

---

### 5. SLOS (Specific Learning Outcomes)
**Purpose:** Learning objectives for each substrand
**Count:** 1193 documents

```json
{
  "_id": {"$oid": "69a06caa533e4a4d60370bc2"},
  "name": "Identify whole numbers up to 10,000,000",
  "description": "By the end of the lesson, the learner should be able to identify whole numbers up to 10,000,000",
  "substrandId": "69a06caa533e4a4d60370bc0"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Short SLO title |
| description | String | Yes | Full learning outcome description |
| substrandId | String | Yes | Reference to substrands._id (as string) |

---

### 6. SLO_MAPPINGS
**Purpose:** Links SLOs to competencies, values, PCIs, and assessments
**Count:** 1246 documents

```json
{
  "_id": {"$oid": "69a06bff5ea260e6510ed919"},
  "sloId": "69a06bff5ea260e6510ed8e9",
  "competencyIds": ["69a06bff5ea260e6510ed8ff", "69a06bff5ea260e6510ed900"],
  "valueIds": ["69a06bff5ea260e6510ed905", "69a06bff5ea260e6510ed907"],
  "pciIds": ["69a06bff5ea260e6510ed90c"],
  "assessmentIds": ["69a06bff5ea260e6510ed912", "69a06bff5ea260e6510ed913"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| sloId | String | Yes | Reference to slos._id (as string) |
| competencyIds | Array\<String\> | Yes | Array of competencies._id strings |
| valueIds | Array\<String\> | Yes | Array of values._id strings |
| pciIds | Array\<String\> | Yes | Array of pcis._id strings |
| assessmentIds | Array\<String\> | Yes | Array of assessments._id strings |

---

### 7. LEARNING_ACTIVITIES
**Purpose:** Detailed lesson activities for each substrand
**Count:** 602 documents

```json
{
  "_id": {"$oid": "69a2b6ad6ada55980692b841"},
  "substrandId": {"$oid": "69a2adfe0d3f0e48b4cbb54e"},
  "introduction_activities": [
    "Teacher introduces the concept by asking questions",
    "Learners share prior knowledge"
  ],
  "development_activities": [
    "Discuss with resource persons",
    "Group work on practical exercises"
  ],
  "conclusion_activities": [
    "Make class presentations",
    "Summarize key points"
  ],
  "extended_activities": [
    "Project: Survey and create a report",
    "Research and present findings"
  ],
  "learning_resources": [
    "Video clips",
    "Manila papers",
    "Textbooks"
  ],
  "assessment_methods": [
    "Written test",
    "Observation of learners",
    "Oral questions"
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| substrandId | ObjectId | Yes | Reference to substrands._id (as ObjectId!) |
| introduction_activities | Array\<String\> | Yes | Introduction phase activities |
| development_activities | Array\<String\> | Yes | Main lesson activities |
| conclusion_activities | Array\<String\> | Yes | Wrap-up activities |
| extended_activities | Array\<String\> | Yes | Homework/extension activities |
| learning_resources | Array\<String\> | Yes | Required materials |
| assessment_methods | Array\<String\> | Yes | Assessment strategies |

**Note:** `substrandId` here is ObjectId type (not string) - this is intentional

---

### 8. COMPETENCIES (Core Competencies)
**Purpose:** CBC Core Competencies
**Count:** 7 documents

```json
{
  "_id": {"$oid": "69a06bff5ea260e6510ed902"},
  "name": "Communication and Collaboration",
  "description": "Learners communicate effectively and work well with others"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Competency name |
| description | String | Yes | Full description |

**Standard Competencies:**
1. Communication and Collaboration
2. Critical Thinking and Problem Solving
3. Creativity and Imagination
4. Citizenship
5. Digital Literacy
6. Learning to Learn
7. Self-Efficacy

---

### 9. VALUES
**Purpose:** Core values to be instilled
**Count:** 8 documents

```json
{
  "_id": {"$oid": "69a06bff5ea260e6510ed908"},
  "name": "Unity",
  "description": "Learners work together harmoniously and support each other"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Value name |
| description | String | Yes | Full description |

**Standard Values:**
1. Unity
2. Love
3. Peace
4. Respect
5. Responsibility
6. Integrity
7. Patriotism
8. Social Justice

---

### 10. PCIS (Pertinent and Contemporary Issues)
**Purpose:** Cross-cutting issues in education
**Count:** 15 documents

```json
{
  "_id": {"$oid": "69a06bff5ea260e6510ed90f"},
  "name": "Health Education",
  "description": "Promoting healthy lifestyles and wellbeing"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | PCI name |
| description | String | Yes | Full description |

**Standard PCIs:**
1. Health Education
2. Environmental Education
3. Life Skills
4. Citizenship
5. Human Rights
6. Gender Issues
7. Safety and Security
8. Drug and Substance Abuse
9. Financial Literacy
10. Disaster Risk Reduction
11. Animal Welfare
12. Integrity
13. Community Service Learning
14. Education for Sustainable Development
15. Parental Empowerment and Engagement

---

### 11. ASSESSMENTS
**Purpose:** Assessment methods
**Count:** 7 documents

```json
{
  "_id": {"$oid": "69a06bff5ea260e6510ed914"},
  "name": "Group Activity Observation",
  "description": "Observe learners working collaboratively in groups"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| name | String | Yes | Assessment type name |
| description | String | Yes | Full description |

---

### 12. USERS
**Purpose:** User accounts
**Count:** 5 documents

```json
{
  "_id": {"$oid": "6976389c7842c9a39eddb902"},
  "firebaseUid": "WGXO4MILfMTzh5zWKTFOKT1JzPZ2",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "schoolName": "Sample School",
  "role": "teacher",
  "walletBalance": 100.0,
  "freeLessonUsed": false,
  "freeNotesUsed": false,
  "freeLessonsRemaining": 5,
  "createdAt": {"$date": "2026-01-25T15:37:00.757Z"}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Auto | Unique identifier |
| firebaseUid | String | Yes | Firebase Auth UID |
| email | String | Yes | User email |
| firstName | String | No | First name |
| lastName | String | No | Last name |
| schoolName | String | No | School name |
| role | String | Yes | "teacher" or "admin" |
| walletBalance | Float | Yes | Current wallet balance in KES |
| freeLessonUsed | Boolean | Yes | Deprecated - use freeLessonsRemaining |
| freeNotesUsed | Boolean | Yes | Whether free notes used |
| freeLessonsRemaining | Integer | Yes | Number of free lessons left (default: 5) |
| createdAt | DateTime | Yes | Account creation timestamp |

---

### 13. LESSON_PLANS
**Purpose:** Generated lesson plans
**Count:** 58 documents

```json
{
  "_id": {"$oid": "69886fd5022dd6c3f96b4bca"},
  "teacherId": "697638c27842c9a39eddb903",
  "teacherName": "John Doe",
  "schoolName": "Sample School",
  "duration": 40,
  "gradeId": "69886a9c022dd6c3f96b4bc6",
  "gradeName": "Grade 7",
  "subjectId": "69886dba734e50f34eb11ac1",
  "subjectName": "Mathematics",
  "strandId": "69886dba734e50f34eb11ac2",
  "strandName": "Numbers",
  "substrandId": "69886dba734e50f34eb11ac3",
  "substrandName": "Whole Numbers",
  "sloId": "69886dba734e50f34eb11ac4",
  "sloName": "Identify whole numbers",
  "sloDescription": "By the end of the lesson...",
  "knowledge": ["Understand whole numbers", "Recall key concepts"],
  "skills": ["Apply number concepts", "Demonstrate understanding"],
  "attitudes": ["Show curiosity", "Develop positive learning habits"],
  "learningResources": ["Textbooks", "Charts", "Number cards"],
  "competencies": ["Communication and Collaboration"],
  "values": ["Unity", "Responsibility"],
  "pcis": ["Life Skills"],
  "introduction": "Introduction text...",
  "lessonDevelopment": "Development text...",
  "extendedActivity": "Extended activity text...",
  "conclusion": "Conclusion text...",
  "assessment": "Assessment text...",
  "createdAt": {"$date": "2026-02-08T11:13:25.149Z"}
}
```

---

## JSON Import Templates

### Template: Adding a New Subject with Full Curriculum

```json
[
  {
    "_id": {"$oid": "NEW_SUBJECT_ID"},
    "name": "New Subject",
    "gradeIds": ["GRADE_7_ID", "GRADE_8_ID"]
  }
]
```

### Template: Adding Strands (maintain teaching order)

```json
[
  {
    "_id": {"$oid": "STRAND_1_ID"},
    "name": "First Strand (teach first)",
    "subjectId": "SUBJECT_ID"
  },
  {
    "_id": {"$oid": "STRAND_2_ID"},
    "name": "Second Strand (teach second)",
    "subjectId": "SUBJECT_ID"
  }
]
```

### Template: Adding SLOs with Mappings

**Step 1: Add SLO**
```json
{
  "_id": {"$oid": "NEW_SLO_ID"},
  "name": "Short title",
  "description": "By the end of the lesson, the learner should be able to...",
  "substrandId": "SUBSTRAND_ID"
}
```

**Step 2: Add SLO Mapping**
```json
{
  "_id": {"$oid": "NEW_MAPPING_ID"},
  "sloId": "NEW_SLO_ID",
  "competencyIds": ["COMPETENCY_ID_1", "COMPETENCY_ID_2"],
  "valueIds": ["VALUE_ID_1"],
  "pciIds": ["PCI_ID_1"],
  "assessmentIds": ["ASSESSMENT_ID_1"]
}
```

### Template: Adding Learning Activities

```json
{
  "_id": {"$oid": "NEW_ACTIVITY_ID"},
  "substrandId": {"$oid": "SUBSTRAND_ID"},
  "introduction_activities": [
    "Activity 1",
    "Activity 2"
  ],
  "development_activities": [
    "Activity 1",
    "Activity 2"
  ],
  "conclusion_activities": [
    "Activity 1"
  ],
  "extended_activities": [
    "Homework activity"
  ],
  "learning_resources": [
    "Resource 1",
    "Resource 2"
  ],
  "assessment_methods": [
    "Written test",
    "Observation"
  ]
}
```

---

## Generating New ObjectIds

Use MongoDB's ObjectId generator or this Python snippet:
```python
from bson import ObjectId
new_id = str(ObjectId())  # Generates: "507f1f77bcf86cd799439011"
```

Or in JavaScript:
```javascript
const { ObjectId } = require('mongodb');
const newId = new ObjectId().toString();
```

---

## Import Order (to avoid reference conflicts)

1. **grades** - No dependencies
2. **competencies** - No dependencies
3. **values** - No dependencies
4. **pcis** - No dependencies
5. **assessments** - No dependencies
6. **subjects** - Depends on grades
7. **strands** - Depends on subjects
8. **substrands** - Depends on strands
9. **slos** - Depends on substrands
10. **slo_mappings** - Depends on slos, competencies, values, pcis, assessments
11. **learning_activities** - Depends on substrands

---

## Common Pitfalls to Avoid

1. **Don't sort strands/substrands alphabetically** - They must stay in teaching order
2. **String vs ObjectId** - Most foreign keys are strings, but `learning_activities.substrandId` is ObjectId
3. **Duplicate subjects** - Check if subject exists before inserting (query by name + gradeIds)
4. **Missing slo_mappings** - Every SLO should have a corresponding mapping
5. **Empty arrays** - Always provide at least empty arrays `[]` for array fields
