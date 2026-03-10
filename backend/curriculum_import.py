"""
Curriculum Data Import Module
Handles CSV upload and PDF extraction for bulk curriculum data import.
"""

import csv
import io
import re
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
import fitz  # PyMuPDF

router = APIRouter()

# ==================== DATA MODELS ====================

class CurriculumRow(BaseModel):
    strand_name: str
    substrand_name: str
    slo_name: str
    slo_description: Optional[str] = ""
    introduction_activities: Optional[str] = ""
    development_activities: Optional[str] = ""
    conclusion_activities: Optional[str] = ""
    extended_activities: Optional[str] = ""
    competencies: Optional[str] = ""
    values: Optional[str] = ""
    pcis: Optional[str] = ""
    assessment_methods: Optional[str] = ""
    learning_resources: Optional[str] = ""

class CurriculumImportPreview(BaseModel):
    rows: List[Dict[str, Any]]
    summary: Dict[str, int]
    errors: List[str]
    warnings: List[str]

class SaveImportRequest(BaseModel):
    subjectId: str
    rows: List[Dict[str, Any]]

# ==================== CSV TEMPLATE ====================

CSV_TEMPLATE_HEADERS = [
    "strand_name",
    "substrand_name", 
    "slo_name",
    "slo_description",
    "introduction_activities",
    "development_activities",
    "conclusion_activities",
    "extended_activities",
    "competencies",
    "values",
    "pcis",
    "assessment_methods",
    "learning_resources"
]

CSV_TEMPLATE_EXAMPLE = [
    {
        "strand_name": "Listening & Speaking",
        "substrand_name": "Listening Comprehension",
        "slo_name": "Identify Arabic letters and their sounds for comprehension",
        "slo_description": "By the end of the lesson the learner should be able to identify Arabic letters and their sounds",
        "introduction_activities": "Warm-up: Play Arabic alphabet song; Discuss familiar Arabic words",
        "development_activities": "Identify Arabic letters and sounds; Match sounds with letters; Join syllables to form words; Listen to greetings audio",
        "conclusion_activities": "Summarize key letters learned; Quick oral quiz",
        "extended_activities": "Practice pronunciation at home with family; Use language apps",
        "competencies": "Communication & Collaboration; Self-efficacy",
        "values": "Respect; Cultural appreciation",
        "pcis": "Cultural awareness; Life skills",
        "assessment_methods": "Oral questions; Observation; Pronunciation check",
        "learning_resources": "Alphabet flashcards; Audio recordings; Charts"
    },
    {
        "strand_name": "Listening & Speaking",
        "substrand_name": "Listening Comprehension",
        "slo_name": "Combine syllables and sounds to form words",
        "slo_description": "By the end of the lesson the learner should be able to combine syllables and sounds to form meaningful words",
        "introduction_activities": "Review previous lesson; Warm-up with syllable clapping",
        "development_activities": "Join syllables to form meaningful words; Pronounce words from display charts; Syllable puzzles",
        "conclusion_activities": "Word-building competitions; Peer review",
        "extended_activities": "Digital vocabulary games at home; Practice with flashcards",
        "competencies": "Communication & Collaboration; Self-efficacy",
        "values": "Respect; Responsibility",
        "pcis": "Cultural awareness; Effective communication",
        "assessment_methods": "Oral assessment; Word formation test",
        "learning_resources": "Syllable cards; Word charts; Digital games"
    },
    {
        "strand_name": "Listening & Speaking",
        "substrand_name": "Oral Expression",
        "slo_name": "Greet appropriately in different contexts",
        "slo_description": "By the end of the lesson the learner should be able to greet appropriately in various social contexts",
        "introduction_activities": "Discuss importance of greetings; Share greetings from different cultures",
        "development_activities": "Role-play greetings in pairs; Practice formal and informal greetings; Listen to audio examples",
        "conclusion_activities": "Demonstrate greetings to class; Peer feedback",
        "extended_activities": "Greet family members in Arabic; Practice with neighbors",
        "competencies": "Communication & Collaboration; Citizenship",
        "values": "Respect; Unity; Social justice",
        "pcis": "Cultural awareness; Social cohesion",
        "assessment_methods": "Role-play observation; Peer assessment",
        "learning_resources": "Audio recordings; Role-play cards; Video clips"
    },
    {
        "strand_name": "Reading",
        "substrand_name": "Reading for Comprehension",
        "slo_name": "Identify Arabic letters in written text",
        "slo_description": "By the end of the lesson the learner should be able to identify and recognize Arabic letters in written text",
        "introduction_activities": "Display Arabic alphabet; Review letter sounds",
        "development_activities": "Display Arabic alphabet charts; Letter identification exercises; Reading letter patterns",
        "conclusion_activities": "Letter recognition quiz; Peer teaching",
        "extended_activities": "Read Arabic signs at home; Identify letters in books",
        "competencies": "Communication & Collaboration; Self-efficacy; Learning to learn",
        "values": "Respect; Responsibility",
        "pcis": "Cultural awareness; Life skills",
        "assessment_methods": "Written identification test; Observation",
        "learning_resources": "Alphabet charts; Flashcards; Textbooks"
    },
    {
        "strand_name": "Writing",
        "substrand_name": "Handwriting",
        "slo_name": "Write Arabic letters legibly",
        "slo_description": "By the end of the lesson the learner should be able to write Arabic letters legibly with correct formation",
        "introduction_activities": "Letter tracing warm-up; Discuss letter shapes",
        "development_activities": "Trace Arabic letters; Practice letter formation; Guided writing exercises",
        "conclusion_activities": "Letter writing assessment; Peer review",
        "extended_activities": "Practice writing at home; Complete worksheets",
        "competencies": "Communication & Collaboration; Self-efficacy",
        "values": "Responsibility; Discipline",
        "pcis": "Life skills",
        "assessment_methods": "Handwriting checklist; Letter formation assessment",
        "learning_resources": "Writing worksheets; Tracing guides; Writing boards"
    },
    {
        "strand_name": "Writing",
        "substrand_name": "Creative Writing",
        "slo_name": "Write simple sentences on familiar topics",
        "slo_description": "By the end of the lesson the learner should be able to write simple sentences in Arabic on familiar everyday topics",
        "introduction_activities": "Discuss familiar topics; Brainstorm vocabulary",
        "development_activities": "Guided sentence writing; Topic-based writing practice; Peer sharing",
        "conclusion_activities": "Share written sentences; Class feedback",
        "extended_activities": "Write sentences about daily activities; Keep a journal",
        "competencies": "Creativity & Imagination; Communication & Collaboration",
        "values": "Responsibility; Integrity",
        "pcis": "Self-expression; Life skills",
        "assessment_methods": "Sentence writing rubric; Content assessment",
        "learning_resources": "Topic cards; Sentence starters; Writing frames"
    }
]

def generate_csv_template() -> str:
    """Generate a CSV template with headers and example rows"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_TEMPLATE_HEADERS)
    writer.writeheader()
    for row in CSV_TEMPLATE_EXAMPLE:
        writer.writerow(row)
    return output.getvalue()

# ==================== CSV PARSING ====================

def parse_csv_content(content: str) -> CurriculumImportPreview:
    """Parse CSV content and validate"""
    rows = []
    errors = []
    warnings = []
    
    try:
        # Try to detect delimiter
        dialect = csv.Sniffer().sniff(content[:2048], delimiters=',;\t')
        reader = csv.DictReader(io.StringIO(content), dialect=dialect)
    except:
        # Default to comma
        reader = csv.DictReader(io.StringIO(content))
    
    row_num = 1
    strands_found = set()
    substrands_found = set()
    
    # Column name mappings (aliases)
    COLUMN_ALIASES = {
        'strand_name': ['strand_name', 'strand', 'Strand'],
        'substrand_name': ['substrand_name', 'substrand', 'sub-strand', 'Sub-strand', 'sub_strand', 'Sub_strand'],
        'slo_name': ['slo_name', 'slo', 'Specific Learning Outcome (SLO)', 'Specific Learning Outcome', 'SLO'],
        'slo_description': ['slo_description', 'description', 'Description'],
        'competencies': ['competencies', 'core_competencies', 'Core Competencies', 'Core_Competencies'],
        'values': ['values', 'Values'],
        'pcis': ['pcis', 'PCIs', 'pci', 'PCI'],
        'introduction_activities': ['introduction_activities', 'Introduction Activities'],
        'development_activities': ['development_activities', 'Development Activities', 'Teaching & Learning Activities', 'Teaching and Learning Activities', 'activities', 'Activities'],
        'conclusion_activities': ['conclusion_activities', 'Conclusion Activities'],
        'extended_activities': ['extended_activities', 'Extended Activities', 'Additional Activities'],
        'assessment_methods': ['assessment_methods', 'Assessment Methods', 'assessment'],
        'learning_resources': ['learning_resources', 'Learning Resources', 'resources', 'Resources']
    }
    
    def get_field(row, field_name):
        """Get field value using aliases"""
        aliases = COLUMN_ALIASES.get(field_name, [field_name])
        for alias in aliases:
            if alias in row and row[alias]:
                return row[alias].strip()
        return ''
    
    for row in reader:
        row_num += 1
        cleaned_row = {}
        
        # Clean and validate each field using aliases
        strand = get_field(row, 'strand_name')
        substrand = get_field(row, 'substrand_name')
        slo = get_field(row, 'slo_name')
        
        if not strand:
            errors.append(f"Row {row_num}: Missing strand_name (or 'Strand' column)")
            continue
        if not substrand:
            errors.append(f"Row {row_num}: Missing substrand_name (or 'Sub-strand' column)")
            continue
        if not slo:
            errors.append(f"Row {row_num}: Missing slo_name (or 'Specific Learning Outcome (SLO)' column)")
            continue
        
        strands_found.add(strand)
        substrands_found.add(f"{strand}|{substrand}")
        
        # Get activities - if only one activities column exists, use it for development
        activities_text = get_field(row, 'development_activities')
        
        # Build cleaned row
        cleaned_row = {
            "row_number": row_num,
            "strand_name": strand,
            "substrand_name": substrand,
            "slo_name": slo,
            "slo_description": get_field(row, 'slo_description') or slo,
            "introduction_activities": parse_list_field(get_field(row, 'introduction_activities')),
            "development_activities": parse_list_field(activities_text),
            "conclusion_activities": parse_list_field(get_field(row, 'conclusion_activities')),
            "extended_activities": parse_list_field(get_field(row, 'extended_activities')),
            "competencies": parse_list_field(get_field(row, 'competencies')),
            "values": parse_list_field(get_field(row, 'values')),
            "pcis": parse_list_field(get_field(row, 'pcis')),
            "assessment_methods": parse_list_field(get_field(row, 'assessment_methods')),
            "learning_resources": parse_list_field(get_field(row, 'learning_resources'))
        }
        
        # Warnings for missing optional fields
        if not cleaned_row["competencies"]:
            warnings.append(f"Row {row_num}: No competencies specified")
        if not cleaned_row["values"]:
            warnings.append(f"Row {row_num}: No values specified")
        if not cleaned_row["introduction_activities"] and not cleaned_row["development_activities"]:
            warnings.append(f"Row {row_num}: No learning activities specified")
        
        rows.append(cleaned_row)
    
    summary = {
        "total_rows": len(rows),
        "strands": len(strands_found),
        "substrands": len(substrands_found),
        "slos": len(rows),
        "errors": len(errors),
        "warnings": len(warnings)
    }
    
    return CurriculumImportPreview(
        rows=rows,
        summary=summary,
        errors=errors[:20],  # Limit errors shown
        warnings=warnings[:20]  # Limit warnings shown
    )

def parse_list_field(value: str) -> List[str]:
    """Parse a field that may contain multiple items separated by ; or newlines"""
    if not value:
        return []
    
    # Split by semicolon or newline
    items = re.split(r'[;\n]', value)
    # Clean and filter empty items
    return [item.strip() for item in items if item.strip()]

# ==================== PDF EXTRACTION ====================

def extract_curriculum_from_pdf(pdf_content: bytes) -> CurriculumImportPreview:
    """Extract curriculum data from PDF and convert to CSV format"""
    rows = []
    errors = []
    warnings = []
    
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
    except Exception as e:
        errors.append(f"Failed to open PDF: {str(e)}")
        return CurriculumImportPreview(rows=[], summary={}, errors=errors, warnings=[])
    
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n---PAGE---\n"
    
    doc.close()
    
    # Extract strands
    strand_pattern = re.compile(r'STRAND\s+(\d+\.?\d*)\s*[:\.]?\s*([A-Z][A-Z\s\-&]+?)(?:\s+(?:THEME|Sub|$)|\s*\n)', re.IGNORECASE)
    strand_matches = list(strand_pattern.finditer(full_text))
    
    if not strand_matches:
        # Try alternative pattern
        strand_pattern = re.compile(r'(\d+\.0)\s+([A-Z][A-Z\s\-&]+?)(?:\n|$)', re.IGNORECASE)
        strand_matches = list(strand_pattern.finditer(full_text))
    
    if not strand_matches:
        warnings.append("No strands found in PDF. The document may have a different format.")
    
    strands_found = set()
    substrands_found = set()
    
    for i, strand_match in enumerate(strand_matches):
        strand_name = strand_match.group(2).strip().upper()
        if len(strand_name) < 3:
            continue
        
        strands_found.add(strand_name)
        
        # Get text for this strand
        start_pos = strand_match.end()
        end_pos = strand_matches[i+1].start() if i+1 < len(strand_matches) else len(full_text)
        strand_text = full_text[start_pos:end_pos]
        
        # Find substrands
        substrand_pattern = re.compile(r'(?:Sub[\s-]?Strand|SUB[\s-]?STRAND)\s*(\d+\.\d+)\s*[:\.]?\s*(.+?)(?:\n|$)', re.IGNORECASE)
        substrand_matches = list(substrand_pattern.finditer(strand_text))
        
        if not substrand_matches:
            # Try numbered pattern
            substrand_pattern = re.compile(r'(\d+\.\d+)\s+([A-Za-z][^:\n]{5,60})(?::|$)', re.MULTILINE)
            substrand_matches = list(substrand_pattern.finditer(strand_text))
        
        for j, ss_match in enumerate(substrand_matches):
            substrand_name = ss_match.group(2).strip()
            if len(substrand_name) < 3 or len(substrand_name) > 100:
                continue
            
            # Clean substrand name
            substrand_name = re.sub(r'\s+', ' ', substrand_name)
            substrands_found.add(f"{strand_name}|{substrand_name}")
            
            # Get substrand text
            ss_start = ss_match.end()
            ss_end = substrand_matches[j+1].start() if j+1 < len(substrand_matches) else len(strand_text)
            ss_text = strand_text[ss_start:ss_end]
            
            # Extract SLOs
            slos = extract_slos_from_text(ss_text)
            
            # Extract learning activities
            activities = extract_activities_from_text(ss_text)
            
            # Extract competencies, values, PCIs
            competencies = extract_competencies_from_text(ss_text)
            values = extract_values_from_text(ss_text)
            pcis = extract_pcis_from_text(ss_text)
            assessment = extract_assessment_from_text(ss_text)
            resources = extract_resources_from_text(ss_text)
            
            # If no SLOs found, create one generic row
            if not slos:
                slos = [{"name": f"Complete {substrand_name} activities", "description": ""}]
                warnings.append(f"No SLOs found for {substrand_name}")
            
            for slo in slos:
                row = {
                    "row_number": len(rows) + 1,
                    "strand_name": strand_name,
                    "substrand_name": substrand_name,
                    "slo_name": slo["name"],
                    "slo_description": slo.get("description", slo["name"]),
                    "introduction_activities": activities.get("introduction", []),
                    "development_activities": activities.get("development", []),
                    "conclusion_activities": activities.get("conclusion", []),
                    "extended_activities": activities.get("extended", []),
                    "competencies": competencies,
                    "values": values,
                    "pcis": pcis,
                    "assessment_methods": assessment,
                    "learning_resources": resources
                }
                rows.append(row)
    
    summary = {
        "total_rows": len(rows),
        "strands": len(strands_found),
        "substrands": len(substrands_found),
        "slos": len(rows),
        "errors": len(errors),
        "warnings": len(warnings)
    }
    
    return CurriculumImportPreview(
        rows=rows,
        summary=summary,
        errors=errors[:20],
        warnings=warnings[:20]
    )

def extract_slos_from_text(text: str) -> List[Dict[str, str]]:
    """Extract SLOs from text"""
    slos = []
    
    # Look for SLO section
    slo_section = re.search(
        r'(?:should be able[^:]*to|Specific Learning Outcomes?)[:\s]*(.+?)(?:The learner is guided|Suggested Learning|Key Inquiry)',
        text, re.DOTALL | re.IGNORECASE
    )
    
    if slo_section:
        slo_text = slo_section.group(1)
        # Find lettered items
        slo_items = re.findall(r'[a-z]\)\s*(.+?)(?=[a-z]\)|$)', slo_text, re.DOTALL)
        
        for item in slo_items:
            cleaned = re.sub(r'\s+', ' ', item).strip().rstrip('.,; ')
            if cleaned and 10 < len(cleaned) < 300:
                slos.append({"name": cleaned, "description": cleaned})
    
    return slos[:10]  # Limit to 10 SLOs per substrand

def extract_activities_from_text(text: str) -> Dict[str, List[str]]:
    """Extract learning activities from text"""
    activities = {
        "introduction": [],
        "development": [],
        "conclusion": [],
        "extended": []
    }
    
    # Look for learning experiences section
    le_section = re.search(
        r'(?:The learner is guided to|Suggested Learning Experiences|Learning Activities)[:\s]*(.+?)(?:Key Inquiry|Assessment|Core competencies|Values:)',
        text, re.DOTALL | re.IGNORECASE
    )
    
    if le_section:
        le_text = le_section.group(1)
        # Split by bullet points or newlines
        items = re.split(r'[\u2022\u2023\u25E6•\-]\s*|\n{2,}', le_text)
        
        cleaned_items = []
        for item in items:
            cleaned = re.sub(r'\s+', ' ', item).strip()
            if cleaned and 15 < len(cleaned) < 300:
                cleaned_items.append(cleaned)
        
        # Distribute activities
        n = len(cleaned_items)
        if n > 0:
            intro_count = max(1, n // 4)
            dev_count = max(1, n // 2)
            activities["introduction"] = cleaned_items[:intro_count]
            activities["development"] = cleaned_items[intro_count:intro_count + dev_count]
            activities["conclusion"] = cleaned_items[intro_count + dev_count:]
    
    return activities

def extract_competencies_from_text(text: str) -> List[str]:
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
    
    section = re.search(r'Core competencies[^:]*:\s*(.+?)(?:Values:|Pertinent|Link to|$)', text, re.DOTALL | re.IGNORECASE)
    if section:
        section_text = section.group(1).lower()
        for comp in known:
            if comp.lower() in section_text:
                competencies.append(comp)
    
    return competencies if competencies else ["Critical Thinking and Problem Solving", "Communication and Collaboration"]

def extract_values_from_text(text: str) -> List[str]:
    """Extract core values"""
    values = []
    known = ["Love", "Responsibility", "Respect", "Unity", "Peace", "Patriotism", "Social Justice", "Integrity"]
    
    section = re.search(r'Values\s*[:\.]?\s*(.+?)(?:Pertinent|Link to|Core comp|$)', text, re.DOTALL | re.IGNORECASE)
    if section:
        section_text = section.group(1).lower()
        for val in known:
            if val.lower() in section_text:
                values.append(val)
    
    return values if values else ["Responsibility", "Respect"]

def extract_pcis_from_text(text: str) -> List[str]:
    """Extract PCIs"""
    pcis = []
    known = [
        "Environmental Education", "Safety and Security", "Health Education",
        "Life Skills", "Financial Literacy", "Citizenship Education",
        "Gender Issues", "Social Cohesion", "Education for Sustainable Development",
        "Peace Education", "Effective Communication", "Cultural Heritage"
    ]
    
    section = re.search(r'Pertinent and Contemporary Issues[^:]*:\s*(.+?)(?:Link to|Values:|$)', text, re.DOTALL | re.IGNORECASE)
    if section:
        section_text = section.group(1).lower()
        for pci in known:
            if pci.lower() in section_text:
                pcis.append(pci)
    
    return pcis if pcis else ["Life Skills", "Citizenship Education"]

def extract_assessment_from_text(text: str) -> List[str]:
    """Extract assessment methods"""
    methods = []
    known = [
        "Observation", "Oral questions", "Written tests", "Practical assessment",
        "Portfolio", "Project work", "Peer assessment", "Self-assessment",
        "Checklist", "Rating scale", "Rubric"
    ]
    
    section = re.search(r'(?:Assessment|Suggested.*Assessment)[^:]*:\s*(.+?)(?:Learning Resources|Link to|$)', text, re.DOTALL | re.IGNORECASE)
    if section:
        section_text = section.group(1).lower()
        for method in known:
            if method.lower() in section_text:
                methods.append(method)
    
    return methods if methods else ["Observation", "Oral questions"]

def extract_resources_from_text(text: str) -> List[str]:
    """Extract learning resources"""
    resources = []
    known = [
        "Textbooks", "Charts", "Pictures", "Audio recordings", "Video clips",
        "Digital devices", "Realia", "Flashcards", "Worksheets", "Models",
        "Maps", "Globes", "Laboratory equipment", "Art materials"
    ]
    
    section = re.search(r'(?:Learning Resources|Resources)[^:]*:\s*(.+?)(?:Assessment|Link to|$)', text, re.DOTALL | re.IGNORECASE)
    if section:
        section_text = section.group(1).lower()
        for resource in known:
            if resource.lower() in section_text:
                resources.append(resource)
    
    return resources if resources else ["Textbooks", "Charts", "Digital devices"]

def rows_to_csv(rows: List[Dict[str, Any]]) -> str:
    """Convert rows back to CSV format for download"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_TEMPLATE_HEADERS)
    writer.writeheader()
    
    for row in rows:
        csv_row = {
            "strand_name": row.get("strand_name", ""),
            "substrand_name": row.get("substrand_name", ""),
            "slo_name": row.get("slo_name", ""),
            "slo_description": row.get("slo_description", ""),
            "introduction_activities": "; ".join(row.get("introduction_activities", [])),
            "development_activities": "; ".join(row.get("development_activities", [])),
            "conclusion_activities": "; ".join(row.get("conclusion_activities", [])),
            "extended_activities": "; ".join(row.get("extended_activities", [])),
            "competencies": "; ".join(row.get("competencies", [])),
            "values": "; ".join(row.get("values", [])),
            "pcis": "; ".join(row.get("pcis", [])),
            "assessment_methods": "; ".join(row.get("assessment_methods", [])),
            "learning_resources": "; ".join(row.get("learning_resources", []))
        }
        writer.writerow(csv_row)
    
    return output.getvalue()
