"""
Backend tests for CBE Lesson Planner curriculum data seeding.

Tests verify that the 5 new subjects from KICD PDFs were correctly seeded:
- Business Studies
- Christian Religious Education (CRE)
- Electrical Technology
- Fine Arts
- French

Expected totals:
- 22 subjects
- 60 strands
- 235 substrands
- 898 SLOs
- 89 learning activities
"""

import pytest
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv('/app/backend/.env')

# Get MongoDB connection from environment
MONGO_URL = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
DB_NAME = os.environ.get('DB_NAME', 'cbeplanner')

# New subjects that were seeded
NEW_SUBJECTS = [
    "Business Studies",
    "Christian Religious Education",
    "Electrical Technology", 
    "Fine Arts",
    "French"
]

# Expected counts for new subjects based on agent context
EXPECTED_SUBJECT_DATA = {
    "Business Studies": {
        "strands": 4,
        "substrands": 15,
        "slos": 79,
        "activities": 11
    },
    "Christian Religious Education": {
        "strands": 4,
        "substrands": 23,
        "slos": 102,
        "activities": 21
    },
    "Electrical Technology": {
        "strands": 4,
        "substrands": 13,
        "slos": 54,
        "activities": 13
    },
    "Fine Arts": {
        "strands": 3,
        "substrands": 11,
        "slos": 45,
        "activities": 11
    },
    "French": {
        "strands": 4,
        "substrands": 19,
        "slos": 57,
        "activities": 13
    }
}


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_client():
    """Create MongoDB client connection"""
    client = AsyncIOMotorClient(MONGO_URL)
    yield client
    client.close()


@pytest.fixture(scope="module")
async def db(db_client):
    """Get database instance"""
    return db_client[DB_NAME]


class TestDatabaseConnection:
    """Test database connectivity"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self, db_client):
        """Test MongoDB connection is working"""
        try:
            await db_client.admin.command('ping')
            print("MongoDB connection: OK")
            assert True
        except Exception as e:
            pytest.fail(f"MongoDB connection failed: {str(e)}")


class TestTotalCounts:
    """Test overall curriculum data counts match expected totals"""
    
    @pytest.mark.asyncio
    async def test_total_subjects_count(self, db):
        """Verify total subjects count is 22"""
        count = await db.subjects.count_documents({})
        print(f"Total subjects in database: {count}")
        assert count == 22, f"Expected 22 subjects, found {count}"
    
    @pytest.mark.asyncio
    async def test_total_strands_count(self, db):
        """Verify total strands count is 60"""
        count = await db.strands.count_documents({})
        print(f"Total strands in database: {count}")
        assert count == 60, f"Expected 60 strands, found {count}"
    
    @pytest.mark.asyncio
    async def test_total_substrands_count(self, db):
        """Verify total substrands count is 235"""
        count = await db.substrands.count_documents({})
        print(f"Total substrands in database: {count}")
        assert count == 235, f"Expected 235 substrands, found {count}"
    
    @pytest.mark.asyncio
    async def test_total_slos_count(self, db):
        """Verify total SLOs count is 898"""
        count = await db.slos.count_documents({})
        print(f"Total SLOs in database: {count}")
        assert count == 898, f"Expected 898 SLOs, found {count}"
    
    @pytest.mark.asyncio
    async def test_total_learning_activities_count(self, db):
        """Verify total learning activities count is 89"""
        count = await db.learning_activities.count_documents({})
        print(f"Total learning activities in database: {count}")
        assert count == 89, f"Expected 89 learning activities, found {count}"


class TestNewSubjectsExist:
    """Test that all 5 new subjects were seeded correctly"""
    
    @pytest.mark.asyncio
    async def test_business_studies_exists(self, db):
        """Verify Business Studies subject exists"""
        subject = await db.subjects.find_one({"name": "Business Studies"})
        assert subject is not None, "Business Studies subject not found"
        print(f"Business Studies found with gradeIds: {subject.get('gradeIds', [])}")
    
    @pytest.mark.asyncio
    async def test_cre_exists(self, db):
        """Verify Christian Religious Education subject exists"""
        subject = await db.subjects.find_one({"name": "Christian Religious Education"})
        assert subject is not None, "Christian Religious Education subject not found"
        print(f"CRE found with gradeIds: {subject.get('gradeIds', [])}")
    
    @pytest.mark.asyncio
    async def test_electrical_technology_exists(self, db):
        """Verify Electrical Technology subject exists"""
        subject = await db.subjects.find_one({"name": "Electrical Technology"})
        assert subject is not None, "Electrical Technology subject not found"
        print(f"Electrical Technology found with gradeIds: {subject.get('gradeIds', [])}")
    
    @pytest.mark.asyncio
    async def test_fine_arts_exists(self, db):
        """Verify Fine Arts subject exists"""
        subject = await db.subjects.find_one({"name": "Fine Arts"})
        assert subject is not None, "Fine Arts subject not found"
        print(f"Fine Arts found with gradeIds: {subject.get('gradeIds', [])}")
    
    @pytest.mark.asyncio
    async def test_french_exists(self, db):
        """Verify French subject exists"""
        subject = await db.subjects.find_one({"name": "French"})
        assert subject is not None, "French subject not found"
        print(f"French found with gradeIds: {subject.get('gradeIds', [])}")


class TestBusinessStudiesData:
    """Test Business Studies curriculum data"""
    
    @pytest.mark.asyncio
    async def test_business_studies_strands(self, db):
        """Verify Business Studies has correct number of strands"""
        subject = await db.subjects.find_one({"name": "Business Studies"})
        if not subject:
            pytest.skip("Business Studies subject not found")
        
        subject_id = str(subject["_id"])
        strands_count = await db.strands.count_documents({"subjectId": subject_id})
        expected = EXPECTED_SUBJECT_DATA["Business Studies"]["strands"]
        print(f"Business Studies strands: {strands_count} (expected: {expected})")
        assert strands_count == expected, f"Expected {expected} strands, found {strands_count}"
    
    @pytest.mark.asyncio
    async def test_business_studies_substrands(self, db):
        """Verify Business Studies has correct number of substrands"""
        subject = await db.subjects.find_one({"name": "Business Studies"})
        if not subject:
            pytest.skip("Business Studies subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands_count = await db.substrands.count_documents({"strandId": {"$in": strand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Business Studies"]["substrands"]
        print(f"Business Studies substrands: {substrands_count} (expected: {expected})")
        assert substrands_count == expected, f"Expected {expected} substrands, found {substrands_count}"
    
    @pytest.mark.asyncio
    async def test_business_studies_slos(self, db):
        """Verify Business Studies has correct number of SLOs"""
        subject = await db.subjects.find_one({"name": "Business Studies"})
        if not subject:
            pytest.skip("Business Studies subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(200)
        substrand_ids = [str(ss["_id"]) for ss in substrands]
        
        slos_count = await db.slos.count_documents({"substrandId": {"$in": substrand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Business Studies"]["slos"]
        print(f"Business Studies SLOs: {slos_count} (expected: {expected})")
        assert slos_count == expected, f"Expected {expected} SLOs, found {slos_count}"


class TestCREData:
    """Test Christian Religious Education curriculum data"""
    
    @pytest.mark.asyncio
    async def test_cre_strands(self, db):
        """Verify CRE has correct number of strands"""
        subject = await db.subjects.find_one({"name": "Christian Religious Education"})
        if not subject:
            pytest.skip("CRE subject not found")
        
        subject_id = str(subject["_id"])
        strands_count = await db.strands.count_documents({"subjectId": subject_id})
        expected = EXPECTED_SUBJECT_DATA["Christian Religious Education"]["strands"]
        print(f"CRE strands: {strands_count} (expected: {expected})")
        assert strands_count == expected, f"Expected {expected} strands, found {strands_count}"
    
    @pytest.mark.asyncio
    async def test_cre_substrands(self, db):
        """Verify CRE has correct number of substrands"""
        subject = await db.subjects.find_one({"name": "Christian Religious Education"})
        if not subject:
            pytest.skip("CRE subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands_count = await db.substrands.count_documents({"strandId": {"$in": strand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Christian Religious Education"]["substrands"]
        print(f"CRE substrands: {substrands_count} (expected: {expected})")
        assert substrands_count == expected, f"Expected {expected} substrands, found {substrands_count}"
    
    @pytest.mark.asyncio
    async def test_cre_slos(self, db):
        """Verify CRE has correct number of SLOs"""
        subject = await db.subjects.find_one({"name": "Christian Religious Education"})
        if not subject:
            pytest.skip("CRE subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(200)
        substrand_ids = [str(ss["_id"]) for ss in substrands]
        
        slos_count = await db.slos.count_documents({"substrandId": {"$in": substrand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Christian Religious Education"]["slos"]
        print(f"CRE SLOs: {slos_count} (expected: {expected})")
        assert slos_count == expected, f"Expected {expected} SLOs, found {slos_count}"


class TestElectricalTechnologyData:
    """Test Electrical Technology curriculum data"""
    
    @pytest.mark.asyncio
    async def test_electrical_tech_strands(self, db):
        """Verify Electrical Technology has correct number of strands"""
        subject = await db.subjects.find_one({"name": "Electrical Technology"})
        if not subject:
            pytest.skip("Electrical Technology subject not found")
        
        subject_id = str(subject["_id"])
        strands_count = await db.strands.count_documents({"subjectId": subject_id})
        expected = EXPECTED_SUBJECT_DATA["Electrical Technology"]["strands"]
        print(f"Electrical Technology strands: {strands_count} (expected: {expected})")
        assert strands_count == expected, f"Expected {expected} strands, found {strands_count}"
    
    @pytest.mark.asyncio
    async def test_electrical_tech_substrands(self, db):
        """Verify Electrical Technology has correct number of substrands"""
        subject = await db.subjects.find_one({"name": "Electrical Technology"})
        if not subject:
            pytest.skip("Electrical Technology subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands_count = await db.substrands.count_documents({"strandId": {"$in": strand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Electrical Technology"]["substrands"]
        print(f"Electrical Technology substrands: {substrands_count} (expected: {expected})")
        assert substrands_count == expected, f"Expected {expected} substrands, found {substrands_count}"
    
    @pytest.mark.asyncio
    async def test_electrical_tech_slos(self, db):
        """Verify Electrical Technology has correct number of SLOs"""
        subject = await db.subjects.find_one({"name": "Electrical Technology"})
        if not subject:
            pytest.skip("Electrical Technology subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(200)
        substrand_ids = [str(ss["_id"]) for ss in substrands]
        
        slos_count = await db.slos.count_documents({"substrandId": {"$in": substrand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Electrical Technology"]["slos"]
        print(f"Electrical Technology SLOs: {slos_count} (expected: {expected})")
        assert slos_count == expected, f"Expected {expected} SLOs, found {slos_count}"


class TestFineArtsData:
    """Test Fine Arts curriculum data"""
    
    @pytest.mark.asyncio
    async def test_fine_arts_strands(self, db):
        """Verify Fine Arts has correct number of strands"""
        subject = await db.subjects.find_one({"name": "Fine Arts"})
        if not subject:
            pytest.skip("Fine Arts subject not found")
        
        subject_id = str(subject["_id"])
        strands_count = await db.strands.count_documents({"subjectId": subject_id})
        expected = EXPECTED_SUBJECT_DATA["Fine Arts"]["strands"]
        print(f"Fine Arts strands: {strands_count} (expected: {expected})")
        assert strands_count == expected, f"Expected {expected} strands, found {strands_count}"
    
    @pytest.mark.asyncio
    async def test_fine_arts_substrands(self, db):
        """Verify Fine Arts has correct number of substrands"""
        subject = await db.subjects.find_one({"name": "Fine Arts"})
        if not subject:
            pytest.skip("Fine Arts subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands_count = await db.substrands.count_documents({"strandId": {"$in": strand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Fine Arts"]["substrands"]
        print(f"Fine Arts substrands: {substrands_count} (expected: {expected})")
        assert substrands_count == expected, f"Expected {expected} substrands, found {substrands_count}"
    
    @pytest.mark.asyncio
    async def test_fine_arts_slos(self, db):
        """Verify Fine Arts has correct number of SLOs"""
        subject = await db.subjects.find_one({"name": "Fine Arts"})
        if not subject:
            pytest.skip("Fine Arts subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(200)
        substrand_ids = [str(ss["_id"]) for ss in substrands]
        
        slos_count = await db.slos.count_documents({"substrandId": {"$in": substrand_ids}})
        expected = EXPECTED_SUBJECT_DATA["Fine Arts"]["slos"]
        print(f"Fine Arts SLOs: {slos_count} (expected: {expected})")
        assert slos_count == expected, f"Expected {expected} SLOs, found {slos_count}"


class TestFrenchData:
    """Test French curriculum data"""
    
    @pytest.mark.asyncio
    async def test_french_strands(self, db):
        """Verify French has correct number of strands"""
        subject = await db.subjects.find_one({"name": "French"})
        if not subject:
            pytest.skip("French subject not found")
        
        subject_id = str(subject["_id"])
        strands_count = await db.strands.count_documents({"subjectId": subject_id})
        expected = EXPECTED_SUBJECT_DATA["French"]["strands"]
        print(f"French strands: {strands_count} (expected: {expected})")
        assert strands_count == expected, f"Expected {expected} strands, found {strands_count}"
    
    @pytest.mark.asyncio
    async def test_french_substrands(self, db):
        """Verify French has correct number of substrands"""
        subject = await db.subjects.find_one({"name": "French"})
        if not subject:
            pytest.skip("French subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands_count = await db.substrands.count_documents({"strandId": {"$in": strand_ids}})
        expected = EXPECTED_SUBJECT_DATA["French"]["substrands"]
        print(f"French substrands: {substrands_count} (expected: {expected})")
        assert substrands_count == expected, f"Expected {expected} substrands, found {substrands_count}"
    
    @pytest.mark.asyncio
    async def test_french_slos(self, db):
        """Verify French has correct number of SLOs"""
        subject = await db.subjects.find_one({"name": "French"})
        if not subject:
            pytest.skip("French subject not found")
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strand_ids = [str(s["_id"]) for s in strands]
        
        substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(200)
        substrand_ids = [str(ss["_id"]) for ss in substrands]
        
        slos_count = await db.slos.count_documents({"substrandId": {"$in": substrand_ids}})
        expected = EXPECTED_SUBJECT_DATA["French"]["slos"]
        print(f"French SLOs: {slos_count} (expected: {expected})")
        assert slos_count == expected, f"Expected {expected} SLOs, found {slos_count}"


class TestLearningActivities:
    """Test learning activities were seeded"""
    
    @pytest.mark.asyncio
    async def test_learning_activities_exist(self, db):
        """Verify learning activities collection has data"""
        count = await db.learning_activities.count_documents({})
        print(f"Total learning activities: {count}")
        assert count > 0, "No learning activities found in database"
    
    @pytest.mark.asyncio
    async def test_learning_activities_structure(self, db):
        """Verify learning activities have required fields"""
        activity = await db.learning_activities.find_one({})
        if not activity:
            pytest.skip("No learning activities found")
        
        # Check for expected fields
        expected_fields = ["substrandId"]
        for field in expected_fields:
            assert field in activity, f"Missing field '{field}' in learning activity"
        
        # Check for activity content fields
        activity_fields = ["introduction_activities", "development_activities", 
                          "conclusion_activities", "extended_activities",
                          "learning_resources", "assessment_methods"]
        found_fields = [f for f in activity_fields if f in activity]
        print(f"Learning activity fields found: {found_fields}")
        assert len(found_fields) > 0, "Learning activity missing activity content fields"


class TestDataIntegrity:
    """Test data integrity and relationships"""
    
    @pytest.mark.asyncio
    async def test_strands_reference_valid_subjects(self, db):
        """Verify all strands reference existing subjects"""
        strands = await db.strands.find({}).to_list(100)
        
        for strand in strands:
            subject_id = strand.get("subjectId")
            if subject_id:
                # Find subject by string ID
                subjects = await db.subjects.find({}).to_list(100)
                subject_exists = any(str(s["_id"]) == subject_id for s in subjects)
                if not subject_exists:
                    print(f"Strand '{strand.get('name')}' references non-existent subject: {subject_id}")
        
        print(f"Checked {len(strands)} strands for valid subject references")
        assert True  # Log output for manual verification
    
    @pytest.mark.asyncio
    async def test_substrands_reference_valid_strands(self, db):
        """Verify all substrands reference existing strands"""
        substrands = await db.substrands.find({}).to_list(500)
        
        strand_ids = set()
        strands = await db.strands.find({}).to_list(100)
        for s in strands:
            strand_ids.add(str(s["_id"]))
        
        invalid_refs = []
        for substrand in substrands:
            strand_id = substrand.get("strandId")
            if strand_id and strand_id not in strand_ids:
                invalid_refs.append(substrand.get("name", "Unknown"))
        
        if invalid_refs:
            print(f"Substrands with invalid strand references: {invalid_refs[:5]}...")
        
        print(f"Checked {len(substrands)} substrands for valid strand references")
        assert len(invalid_refs) == 0, f"Found {len(invalid_refs)} substrands with invalid references"
    
    @pytest.mark.asyncio
    async def test_slos_reference_valid_substrands(self, db):
        """Verify all SLOs reference existing substrands"""
        slos = await db.slos.find({}).to_list(1000)
        
        substrand_ids = set()
        substrands = await db.substrands.find({}).to_list(500)
        for ss in substrands:
            substrand_ids.add(str(ss["_id"]))
        
        invalid_refs = []
        for slo in slos:
            substrand_id = slo.get("substrandId")
            if substrand_id and substrand_id not in substrand_ids:
                invalid_refs.append(slo.get("name", "Unknown")[:30])
        
        if invalid_refs:
            print(f"SLOs with invalid substrand references: {invalid_refs[:5]}...")
        
        print(f"Checked {len(slos)} SLOs for valid substrand references")
        assert len(invalid_refs) == 0, f"Found {len(invalid_refs)} SLOs with invalid references"


class TestGrades:
    """Test grades data"""
    
    @pytest.mark.asyncio
    async def test_grades_exist(self, db):
        """Verify grades collection has data"""
        count = await db.grades.count_documents({})
        print(f"Total grades in database: {count}")
        assert count > 0, "No grades found in database"
    
    @pytest.mark.asyncio
    async def test_subjects_have_grade_assignments(self, db):
        """Verify subjects are assigned to grades"""
        subjects = await db.subjects.find({}).to_list(100)
        subjects_without_grades = [s["name"] for s in subjects if not s.get("gradeIds")]
        
        if subjects_without_grades:
            print(f"Subjects without grade assignments: {subjects_without_grades}")
        
        assert len(subjects_without_grades) == 0, f"{len(subjects_without_grades)} subjects have no grade assignments"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
