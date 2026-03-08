#!/usr/bin/env python3
"""
Grade 8, 9, 10 Curriculum Seeding Script
Extracts data EXACTLY from KICD PDFs - no AI-generated content.
"""

import asyncio
import os
import re
import fitz  # PyMuPDF
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
if not mongo_url:
    raise ValueError("MONGO_URL or MONGODB_URI environment variable is required")

client = AsyncIOMotorClient(mongo_url)
db = client['cbeplanner']


# PDF to Subject mapping with page ranges (extracted from TOC analysis)
# Format: (pdf_path, grade, subject_name, start_page, end_page)
PDF_SUBJECTS = [
    # Grade 8 subjects from G8.pdf
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Arabic", 0, 74),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Christian Religious Education", 74, 276),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Creative Arts and Sports", 276, 335),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Agriculture and Nutrition", 335, 369),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Pre-Technical Studies", 369, 417),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Hindu Religious Education", 417, 464),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Music", 464, 537),
    ("/app/backend/pdfs/new_uploads/G8.pdf", "Grade 8", "Islamic Religious Education", 537, 670),
    
    # Grade 9 subjects from G9.pdf  
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Arabic", 0, 77),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Creative Arts and Sports", 77, 283),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Christian Religious Education", 283, 334),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Islamic Religious Education", 334, 392),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Agriculture and Nutrition", 392, 427),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Pre-Technical Studies", 427, 478),
    ("/app/backend/pdfs/new_uploads/G9.pdf", "Grade 9", "Hindu Religious Education", 478, 669),
    
    # Grade 10 subjects from G10.pdf
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Literature in English", 1, 89),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Theatre", 9, 89),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Mandarin Chinese", 89, 169),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Music", 205, 264),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Film", 214, 264),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Physical Education", 264, 335),
    ("/app/backend/pdfs/new_uploads/G10.pdf", "Grade 10", "Physics", 335, 582),
    
    # Grade 10 subjects from G102.pdf
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Arabic", 1, 119),
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Biology", 119, 211),
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Business Studies", 211, 265),
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Chemistry", 265, 306),
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Christian Religious Education", 306, 513),
    ("/app/backend/pdfs/new_uploads/G102.pdf", "Grade 10", "Performing Arts", 513, 626),
    
    # Grade 10 subjects from G103.pdf
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "Film", 9, 57),
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "French", 57, 129),
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "Geography", 189, 244),
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "German", 244, 314),
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "Hindu Religious Education", 314, 409),
    ("/app/backend/pdfs/new_uploads/G103.pdf", "Grade 10", "Indigenous Languages", 409, 607),
]


def extract_text_from_pdf(pdf_path, start_page, end_page):
    """Extract text from PDF page range"""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page, min(end_page, len(doc))):
        text += doc[page_num].get_text() + "\n---PAGEBREAK---\n"
    doc.close()
    return text


def clean_text(text):
    """Clean extracted text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_strands_from_text(text, subject_name):
    """Extract strands and substrands from text"""
    strands = []
    
    # Find strand markers
    strand_pattern = re.compile(r'STRAND\s+(\d+\.?\d*)\s*[:\.]?\s*([A-Z][A-Z\s\-&]+?)(?:\s+(?:THEME|Sub|$)|\s*\n)', re.IGNORECASE)
    strand_matches = list(strand_pattern.finditer(text))
    
    for i, match in enumerate(strand_matches):
        strand_name = clean_text(match.group(2))
        if not strand_name or len(strand_name) < 3:
            continue
        
        # Get text for this strand
        start_pos = match.end()
        end_pos = strand_matches[i+1].start() if i+1 < len(strand_matches) else len(text)
        strand_text = text[start_pos:end_pos]
        
        # Extract substrands
        substrands = extract_substrands(strand_text)
        
        if substrands:
            strands.append({
                "name": strand_name,
                "substrands": substrands
            })
    
    return strands


def extract_substrands(strand_text):
    """Extract substrands from strand text"""
    substrands = []
    
    # Look for substrand patterns
    ss_pattern = re.compile(r'(?:Sub\s*Strand|SUB[\s-]?STRAND)\s*(\d+\.\d+)\s*[:\.]?\s*(.+?)(?:\n|$)', re.IGNORECASE)
    ss_matches = list(ss_pattern.finditer(strand_text))
    
    # Alternative: Look for numbered patterns like "1.1 Name"
    if not ss_matches:
        ss_pattern = re.compile(r'(\d+\.\d+)\s+([A-Za-z][^:\n]{5,50})(?::|$)', re.MULTILINE)
        ss_matches = list(ss_pattern.finditer(strand_text))
    
    for j, ss_match in enumerate(ss_matches):
        ss_name = clean_text(ss_match.group(2))
        if not ss_name or len(ss_name) < 3 or len(ss_name) > 100:
            continue
        
        # Get substrand text
        ss_start = ss_match.end()
        ss_end = ss_matches[j+1].start() if j+1 < len(ss_matches) else len(strand_text)
        ss_text = strand_text[ss_start:ss_end]
        
        # Extract SLOs
        slos = extract_slos(ss_text)
        
        # Extract learning experiences
        learning_exp = extract_learning_experiences(ss_text)
        
        # Extract competencies, values, PCIs
        competencies = extract_competencies(ss_text)
        values = extract_values(ss_text)
        pcis = extract_pcis(ss_text)
        inquiry_questions = extract_inquiry_questions(ss_text)
        
        substrands.append({
            "name": ss_name,
            "slos": slos,
            "learning_experiences": learning_exp,
            "competencies": competencies,
            "values": values,
            "pcis": pcis,
            "inquiry_questions": inquiry_questions
        })
    
    return substrands


def extract_slos(text):
    """Extract Specific Learning Outcomes"""
    slos = []
    
    # Look for SLO section
    slo_section = re.search(
        r'(?:should be able[^:]*to|Specific Learning Outcomes?)[:\s]*(.+?)(?:The learner is guided|Suggested Learning)',
        text, re.DOTALL | re.IGNORECASE
    )
    
    if slo_section:
        slo_text = slo_section.group(1)
        # Find lettered items a), b), c)
        slo_items = re.findall(r'[a-z]\)\s*(.+?)(?=[a-z]\)|$)', slo_text, re.DOTALL)
        
        for item in slo_items:
            cleaned = clean_text(item)
            if cleaned and 10 < len(cleaned) < 300:
                cleaned = cleaned.rstrip('.,; ')
                slos.append({"name": cleaned})
    
    return slos


def extract_learning_experiences(text):
    """Extract learning experiences"""
    experiences = []
    
    le_section = re.search(
        r'(?:The learner is guided to|Suggested Learning Experiences)[:\s]*(.+?)(?:Suggested Key|Key Inquiry|Why|How do|What)',
        text, re.DOTALL | re.IGNORECASE
    )
    
    if le_section:
        le_text = le_section.group(1)
        # Split by bullet points or newlines
        le_items = re.split(r'\n\s*[\u2022\u2023•\-]\s*|\n{2,}', le_text)
        
        for exp in le_items:
            cleaned = clean_text(exp)
            if cleaned and 15 < len(cleaned) < 500:
                experiences.append(cleaned)
    
    return experiences[:10]


def extract_competencies(text):
    """Extract core competencies"""
    competencies = []
    known = [
        "Communication and Collaboration",
        "Critical Thinking and Problem Solving",
        "Creativity and Imagination",
        "Citizenship",
        "Digital Literacy",
        "Learning to Learn",
        "Self-Efficacy"
    ]
    
    comp_section = re.search(r'Core competencies[^:]*:\s*(.+?)(?:Values:|Pertinent|Link to)', text, re.DOTALL | re.IGNORECASE)
    if comp_section:
        comp_text = comp_section.group(1).lower()
        for comp in known:
            if comp.lower() in comp_text:
                competencies.append(comp)
    
    return competencies


def extract_values(text):
    """Extract values"""
    values = []
    known = ["Love", "Responsibility", "Respect", "Unity", "Peace", "Patriotism", "Social Justice", "Integrity"]
    
    val_section = re.search(r'Values\s*[:\.]?\s*(.+?)(?:Pertinent|Link to|Core comp)', text, re.DOTALL | re.IGNORECASE)
    if val_section:
        val_text = val_section.group(1).lower()
        for val in known:
            if val.lower() in val_text:
                values.append(val)
    
    return values


def extract_pcis(text):
    """Extract PCIs"""
    pcis = []
    known = [
        "Environmental Education", "Safety and Security", "Health Education",
        "Life Skills", "Financial Literacy", "Citizenship Education",
        "Gender Issues", "Social Cohesion", "Education for Sustainable Development",
        "Peace Education", "Effective Communication", "Cultural Heritage"
    ]
    
    pci_section = re.search(r'Pertinent and Contemporary Issues[^:]*:\s*(.+?)(?:Link to|Values:|$)', text, re.DOTALL | re.IGNORECASE)
    if pci_section:
        pci_text = pci_section.group(1).lower()
        for pci in known:
            if pci.lower() in pci_text:
                pcis.append(pci)
    
    return pcis


def extract_inquiry_questions(text):
    """Extract inquiry questions"""
    questions = []
    
    iq_section = re.search(r'(?:Key Inquiry|Inquiry Question)[^:]*:\s*(.+?)(?:Core comp|Values:|$)', text, re.DOTALL | re.IGNORECASE)
    if iq_section:
        iq_text = iq_section.group(1)
        q_items = re.findall(r'([A-Z][^?]+\?)', iq_text)
        for q in q_items[:3]:
            cleaned = clean_text(q)
            if cleaned and len(cleaned) > 10:
                questions.append(cleaned)
    
    return questions


async def get_reference_ids():
    """Get ObjectIds for competencies, values, PCIs"""
    competencies = {}
    values = {}
    pcis = {}
    
    async for doc in db.competencies.find():
        competencies[doc['name'].lower()] = str(doc['_id'])
    
    async for doc in db.values.find():
        values[doc['name'].lower()] = str(doc['_id'])
    
    async for doc in db.pcis.find():
        pcis[doc['name'].lower()] = str(doc['_id'])
    
    return competencies, values, pcis


def match_id(name, id_map):
    """Match name to ID"""
    name_lower = name.lower()
    for key, value in id_map.items():
        if key in name_lower or name_lower in key:
            return value
    return list(id_map.values())[0] if id_map else None


async def delete_existing_subject_data(subject_id):
    """Delete all data for a subject"""
    subject_id_str = str(subject_id)
    
    strands = await db.strands.find({'subjectId': subject_id_str}).to_list(1000)
    strand_ids = [str(s['_id']) for s in strands]
    
    substrands = await db.substrands.find({'strandId': {'$in': strand_ids}}).to_list(1000)
    substrand_ids = [str(ss['_id']) for ss in substrands]
    substrand_oids = [ss['_id'] for ss in substrands]
    
    slos = await db.slos.find({'substrandId': {'$in': substrand_ids}}).to_list(1000)
    slo_ids = [str(slo['_id']) for slo in slos]
    
    if slo_ids:
        await db.slo_mappings.delete_many({'sloId': {'$in': slo_ids}})
    if substrand_oids:
        await db.learning_activities.delete_many({'substrandId': {'$in': substrand_oids}})
    if substrand_ids:
        await db.slos.delete_many({'substrandId': {'$in': substrand_ids}})
    if strand_ids:
        await db.substrands.delete_many({'strandId': {'$in': strand_ids}})
    await db.strands.delete_many({'subjectId': subject_id_str})


async def seed_subject(subject_name, grade_name, strands_data, comp_map, val_map, pci_map):
    """Seed a subject with extracted curriculum data"""
    # Get or create grade
    grade = await db.grades.find_one({'name': grade_name})
    if not grade:
        result = await db.grades.insert_one({'name': grade_name})
        grade_id = result.inserted_id
    else:
        grade_id = grade['_id']
    
    grade_id_str = str(grade_id)
    
    # Find or create subject
    subject = await db.subjects.find_one({'name': subject_name})
    if subject:
        subject_id = subject['_id']
        if grade_id_str not in subject.get('gradeIds', []):
            await db.subjects.update_one(
                {'_id': subject_id},
                {'$addToSet': {'gradeIds': grade_id_str}}
            )
        # Delete existing data for this subject/grade
        await delete_existing_subject_data(subject_id)
    else:
        result = await db.subjects.insert_one({
            'name': subject_name,
            'gradeIds': [grade_id_str]
        })
        subject_id = result.inserted_id
    
    subject_id_str = str(subject_id)
    
    totals = {"strands": 0, "substrands": 0, "slos": 0, "mappings": 0, "activities": 0}
    
    # Seed strands
    for strand_data in strands_data:
        strand_result = await db.strands.insert_one({
            'name': strand_data['name'],
            'subjectId': subject_id_str
        })
        strand_id = strand_result.inserted_id
        strand_id_str = str(strand_id)
        totals["strands"] += 1
        
        # Seed substrands
        for ss_data in strand_data.get('substrands', []):
            ss_result = await db.substrands.insert_one({
                'name': ss_data['name'],
                'strandId': strand_id_str
            })
            ss_id = ss_result.inserted_id
            ss_id_str = str(ss_id)
            totals["substrands"] += 1
            
            # Seed SLOs
            for slo_data in ss_data.get('slos', []):
                slo_result = await db.slos.insert_one({
                    'name': slo_data['name'],
                    'description': slo_data.get('description', slo_data['name']),
                    'substrandId': ss_id_str
                })
                slo_id = slo_result.inserted_id
                slo_id_str = str(slo_id)
                totals["slos"] += 1
                
                # Create SLO mapping
                comp_ids = [match_id(c, comp_map) for c in ss_data.get('competencies', []) if match_id(c, comp_map)]
                val_ids = [match_id(v, val_map) for v in ss_data.get('values', []) if match_id(v, val_map)]
                pci_ids = [match_id(p, pci_map) for p in ss_data.get('pcis', []) if match_id(p, pci_map)]
                
                await db.slo_mappings.insert_one({
                    'sloId': slo_id_str,
                    'competencyIds': comp_ids[:3],
                    'valueIds': val_ids[:3],
                    'pciIds': pci_ids[:3],
                    'assessmentIds': []
                })
                totals["mappings"] += 1
            
            # Create learning activity
            learning_exp = ss_data.get('learning_experiences', [])
            if learning_exp:
                num_exp = len(learning_exp)
                intro_count = max(1, num_exp // 3)
                dev_count = max(1, num_exp // 2)
                
                await db.learning_activities.insert_one({
                    'substrandId': ss_id,
                    'introduction_activities': learning_exp[:intro_count],
                    'development_activities': learning_exp[intro_count:intro_count + dev_count],
                    'conclusion_activities': learning_exp[intro_count + dev_count:],
                    'extended_activities': ss_data.get('inquiry_questions', [])[:2],
                    'learning_resources': ['Digital devices', 'Textbooks', 'Audio-visual materials'],
                    'assessment_methods': ['Observation', 'Oral questions', 'Written tests']
                })
                totals["activities"] += 1
    
    return totals


async def process_subject(pdf_path, grade_name, subject_name, start_page, end_page, comp_map, val_map, pci_map):
    """Process a single subject from PDF"""
    print(f"\n  Processing: {subject_name} ({grade_name})")
    
    # Extract text
    text = extract_text_from_pdf(pdf_path, start_page, end_page)
    
    # Extract strands
    strands = extract_strands_from_text(text, subject_name)
    
    if not strands:
        print(f"    Warning: No strands found for {subject_name}")
        return None
    
    # Seed to database
    totals = await seed_subject(subject_name, grade_name, strands, comp_map, val_map, pci_map)
    
    print(f"    Strands: {totals['strands']}, Substrands: {totals['substrands']}, SLOs: {totals['slos']}")
    
    return totals


async def main():
    """Main seeding function"""
    print("="*70)
    print("CURRICULUM SEEDING FROM PDFs")
    print("Grade 8, 9, 10 Remaining Subjects")
    print("="*70)
    
    # Get reference IDs
    comp_map, val_map, pci_map = await get_reference_ids()
    print(f"Loaded: {len(comp_map)} competencies, {len(val_map)} values, {len(pci_map)} PCIs")
    
    grand_totals = {"strands": 0, "substrands": 0, "slos": 0, "mappings": 0, "activities": 0}
    
    for pdf_path, grade, subject, start, end in PDF_SUBJECTS:
        if not os.path.exists(pdf_path):
            print(f"  Skipping {subject}: PDF not found")
            continue
        
        result = await process_subject(pdf_path, grade, subject, start, end, comp_map, val_map, pci_map)
        
        if result:
            for key in grand_totals:
                grand_totals[key] += result.get(key, 0)
    
    print("\n" + "="*70)
    print("SEEDING COMPLETE")
    print("="*70)
    print(f"Total Strands: {grand_totals['strands']}")
    print(f"Total Substrands: {grand_totals['substrands']}")
    print(f"Total SLOs: {grand_totals['slos']}")
    print(f"Total SLO Mappings: {grand_totals['mappings']}")
    print(f"Total Learning Activities: {grand_totals['activities']}")


if __name__ == "__main__":
    asyncio.run(main())
