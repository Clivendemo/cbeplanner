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
        "strand_name": "LISTENING AND SPEAKING",
        "substrand_name": "Comprehension Skills",
        "slo_name": "Identify the main idea in a spoken text",
        "slo_description": "By the end of the lesson, the learner should be able to identify the main idea in a spoken text",
        "introduction_activities": "Discuss what listening means; Ask learners about their favorite stories",
        "development_activities": "Listen to audio recordings; Identify key points; Group discussions",
        "conclusion_activities": "Summarize main ideas; Peer review",
        "extended_activities": "Listen to news broadcasts at home; Discuss with family",
        "competencies": "Communication and Collaboration; Critical Thinking and Problem Solving",
        "values": "Respect; Responsibility",
        "pcis": "Life Skills; Citizenship",
        "assessment_methods": "Oral questions; Observation; Peer assessment",
        "learning_resources": "Audio recordings; Charts; Textbooks"
    },
    {
        "strand_name": "LISTENING AND SPEAKING",
        "substrand_name": "Comprehension Skills",
        "slo_name": "Respond appropriately to oral instructions",
        "slo_description": "By the end of the lesson, the learner should be able to respond appropriately to oral instructions",
        "introduction_activities": "Play Simon Says game; Discuss importance of following instructions",
        "development_activities": "Give multi-step instructions; Learners demonstrate understanding",
        "conclusion_activities": "Review key points; Self-assessment",
        "extended_activities": "Practice following instructions at home",
        "competencies": "Communication and Collaboration; Self-Efficacy",
        "values": "Responsibility; Integrity",
        "pcis": "Life Skills; Safety and Security",
        "assessment_methods": "Practical demonstration; Observation",
        "learning_resources": "Instruction cards; Real objects"
    },
    {
        "strand_name": "LISTENING AND SPEAKING",
        "substrand_name": "Pronunciation and Fluency",
        "slo_name": "Pronounce words correctly in context",
        "slo_description": "By the end of the lesson, the learner should be able to pronounce words correctly in context",
        "introduction_activities": "Tongue twisters; Pronunciation warm-up exercises",
        "development_activities": "Read aloud exercises; Peer correction; Audio model listening",
        "conclusion_activities": "Record and playback; Self-evaluation",
        "extended_activities": "Practice with family members",
        "competencies": "Communication and Collaboration; Learning to Learn",
        "values": "Respect; Responsibility",
        "pcis": "Life Skills; Effective Communication",
        "assessment_methods": "Oral assessment; Observation; Recording analysis",
        "learning_resources": "Audio recordings; Textbooks; Charts"
    },
    {
        "strand_name": "READING",
        "substrand_name": "Reading Comprehension",
        "slo_name": "Identify the main idea in a written text",
        "slo_description": "By the end of the lesson, the learner should be able to identify the main idea in a written text",
        "introduction_activities": "Predict content from title and pictures; Activate prior knowledge",
        "development_activities": "Silent reading; Guided questions; Highlight key sentences",
        "conclusion_activities": "Summarize text; Discuss main points",
        "extended_activities": "Read similar texts at home",
        "competencies": "Critical Thinking and Problem Solving; Communication and Collaboration",
        "values": "Responsibility; Integrity",
        "pcis": "Life Skills; Education for Sustainable Development",
        "assessment_methods": "Written questions; Comprehension test; Oral retelling",
        "learning_resources": "Textbooks; Reading passages; Charts"
    },
    {
        "strand_name": "READING",
        "substrand_name": "Vocabulary Development",
        "slo_name": "Use context clues to determine word meanings",
        "slo_description": "By the end of the lesson, the learner should be able to use context clues to determine word meanings",
        "introduction_activities": "Word games; Discuss unfamiliar words",
        "development_activities": "Read passage with new words; Identify context clues; Dictionary practice",
        "conclusion_activities": "Create sentences with new words; Share with peers",
        "extended_activities": "Keep a vocabulary journal",
        "competencies": "Critical Thinking and Problem Solving; Learning to Learn",
        "values": "Responsibility; Respect",
        "pcis": "Life Skills; Effective Communication",
        "assessment_methods": "Vocabulary quiz; Oral questions; Written exercises",
        "learning_resources": "Dictionaries; Textbooks; Word cards"
    },
    {
        "strand_name": "WRITING",
        "substrand_name": "Creative Writing",
        "slo_name": "Write a short narrative with a clear structure",
        "slo_description": "By the end of the lesson, the learner should be able to write a short narrative with a clear structure",
        "introduction_activities": "Discuss story elements; Read sample narratives",
        "development_activities": "Plan story outline; Draft narrative; Peer feedback",
        "conclusion_activities": "Edit and revise; Share final draft",
        "extended_activities": "Write additional stories at home",
        "competencies": "Creativity and Imagination; Communication and Collaboration",
        "values": "Integrity; Responsibility",
        "pcis": "Life Skills; Cultural Heritage",
        "assessment_methods": "Writing rubric; Peer review; Portfolio assessment",
        "learning_resources": "Writing paper; Sample narratives; Checklist"
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
    
    for row in reader:
        row_num += 1
        cleaned_row = {}
        
        # Clean and validate each field
        strand = row.get('strand_name', '').strip()
        substrand = row.get('substrand_name', '').strip()
        slo = row.get('slo_name', '').strip()
        
        if not strand:
            errors.append(f"Row {row_num}: Missing strand_name")
            continue
        if not substrand:
            errors.append(f"Row {row_num}: Missing substrand_name")
            continue
        if not slo:
            errors.append(f"Row {row_num}: Missing slo_name")
            continue
        
        strands_found.add(strand)
        substrands_found.add(f"{strand}|{substrand}")
        
        # Build cleaned row
        cleaned_row = {
            "row_number": row_num,
            "strand_name": strand,
            "substrand_name": substrand,
            "slo_name": slo,
            "slo_description": row.get('slo_description', slo).strip(),
            "introduction_activities": parse_list_field(row.get('introduction_activities', '')),
            "development_activities": parse_list_field(row.get('development_activities', '')),
            "conclusion_activities": parse_list_field(row.get('conclusion_activities', '')),
            "extended_activities": parse_list_field(row.get('extended_activities', '')),
            "competencies": parse_list_field(row.get('competencies', '')),
            "values": parse_list_field(row.get('values', '')),
            "pcis": parse_list_field(row.get('pcis', '')),
            "assessment_methods": parse_list_field(row.get('assessment_methods', '')),
            "learning_resources": parse_list_field(row.get('learning_resources', ''))
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
