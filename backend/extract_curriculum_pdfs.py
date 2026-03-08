#!/usr/bin/env python3
"""
Curriculum PDF Extractor
Extracts curriculum data from KICD PDF documents for Grades 8, 9, and 10.
Data is extracted EXACTLY as it appears in the PDFs - no AI-generated content.
"""

import fitz  # PyMuPDF
import re
import json
import os
from pathlib import Path

# PDF file mappings
PDF_FILES = {
    "G8.pdf": {
        "grade": "Grade 8",
        "path": "/app/backend/pdfs/new_uploads/G8.pdf"
    },
    "G9.pdf": {
        "grade": "Grade 9",
        "path": "/app/backend/pdfs/new_uploads/G9.pdf"
    },
    "G10.pdf": {
        "grade": "Grade 10",
        "path": "/app/backend/pdfs/new_uploads/G10.pdf"
    },
    "G102.pdf": {
        "grade": "Grade 10",
        "path": "/app/backend/pdfs/new_uploads/G102.pdf"
    },
    "G103.pdf": {
        "grade": "Grade 10",
        "path": "/app/backend/pdfs/new_uploads/G103.pdf"
    }
}


def clean_text(text):
    """Clean extracted text"""
    if not text:
        return ""
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def find_subject_boundaries(doc, subjects_to_find):
    """Find page boundaries for each subject in the document"""
    subject_pages = {}
    
    for page_num in range(len(doc)):
        page_text = doc[page_num].get_text().upper()
        
        for subject in subjects_to_find:
            subject_upper = subject.upper()
            # Look for subject title pages
            if subject_upper in page_text:
                if ("CURRICULUM DESIGN" in page_text or 
                    "ESSENCE STATEMENT" in page_text or
                    "GENERAL LEARNING OUTCOMES" in page_text):
                    if subject not in subject_pages:
                        subject_pages[subject] = {"start": page_num, "end": None}
                    else:
                        subject_pages[subject]["end"] = page_num
    
    return subject_pages


def extract_subject_text(doc, start_page, max_pages=120):
    """Extract text for a subject section"""
    text_blocks = []
    
    for page_num in range(start_page, min(start_page + max_pages, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        text_blocks.append(text)
    
    return "\n---PAGEBREAK---\n".join(text_blocks)


def parse_strand_data(text, subject_name):
    """Parse strands, substrands, and SLOs from extracted text"""
    strands = []
    
    # Split by strand markers
    strand_pattern = re.compile(r'STRAND\s+(\d+\.?\d*)\s*[:\.]?\s*([A-Z][A-Z\s]+)', re.IGNORECASE)
    substrand_pattern = re.compile(r'(?:SUB[\s-]?STRAND|Sub\s*Strand)\s+(\d+\.?\d*)\s*[:\.]?\s*(.+?)(?:\n|$)', re.IGNORECASE)
    
    # Find all strands
    strand_matches = list(strand_pattern.finditer(text))
    
    for i, match in enumerate(strand_matches):
        strand_name = clean_text(match.group(2))
        if not strand_name or len(strand_name) < 3:
            continue
            
        # Get text until next strand
        start_pos = match.end()
        end_pos = strand_matches[i + 1].start() if i + 1 < len(strand_matches) else len(text)
        strand_text = text[start_pos:end_pos]
        
        strand_data = {
            "name": strand_name,
            "substrands": []
        }
        
        # Find substrands within this strand's text
        substrand_matches = list(substrand_pattern.finditer(strand_text))
        
        for j, ss_match in enumerate(substrand_matches):
            substrand_name = clean_text(ss_match.group(2))
            if not substrand_name or len(substrand_name) < 3:
                continue
            
            # Get substrand content
            ss_start = ss_match.end()
            ss_end = substrand_matches[j + 1].start() if j + 1 < len(substrand_matches) else len(strand_text)
            substrand_text = strand_text[ss_start:ss_end]
            
            # Extract SLOs
            slos = extract_slos(substrand_text)
            
            # Extract learning experiences
            learning_exp = extract_learning_experiences(substrand_text)
            
            # Extract core competencies
            competencies = extract_competencies(substrand_text)
            
            # Extract values
            values = extract_values(substrand_text)
            
            # Extract PCIs
            pcis = extract_pcis(substrand_text)
            
            # Extract inquiry questions
            inquiry_questions = extract_inquiry_questions(substrand_text)
            
            substrand_data = {
                "name": substrand_name,
                "slos": slos,
                "learning_experiences": learning_exp,
                "competencies": competencies,
                "values": values,
                "pcis": pcis,
                "inquiry_questions": inquiry_questions
            }
            
            strand_data["substrands"].append(substrand_data)
        
        if strand_data["substrands"]:
            strands.append(strand_data)
    
    return strands


def extract_slos(text):
    """Extract Specific Learning Outcomes from text"""
    slos = []
    
    # Pattern for SLOs - typically in format "a) ...", "b) ...", etc.
    # Or "By the end of the Sub Strand, the learner should be able to:"
    
    # Look for the SLO section
    slo_section = re.search(r'(?:By the end of|Specific Learning|should be able)[^:]*:\s*(.+?)(?:Suggested Learning|The learner is guided)', text, re.DOTALL | re.IGNORECASE)
    
    if slo_section:
        slo_text = slo_section.group(1)
        # Find individual SLOs
        slo_items = re.findall(r'[a-z]\)\s*(.+?)(?=[a-z]\)|$)', slo_text, re.DOTALL | re.IGNORECASE)
        
        for item in slo_items:
            cleaned = clean_text(item)
            if cleaned and len(cleaned) > 10:
                slos.append({"name": cleaned})
    
    return slos


def extract_learning_experiences(text):
    """Extract suggested learning experiences"""
    experiences = []
    
    # Look for learning experiences section
    le_section = re.search(r'(?:Suggested Learning Experiences|The learner is guided to)\s*[:\.]?\s*(.+?)(?:Suggested Key Inquiry|Key Inquiry|Core competencies)', text, re.DOTALL | re.IGNORECASE)
    
    if le_section:
        le_text = le_section.group(1)
        # Split by bullet points or numbered items
        items = re.split(r'[\u2022\u2023\u25E6\u2043\u2219]|\n\s*[•\-\*]\s*|\n\s*\d+[\.\)]\s*', le_text)
        
        for item in items:
            cleaned = clean_text(item)
            if cleaned and len(cleaned) > 10:
                experiences.append(cleaned)
    
    return experiences


def extract_competencies(text):
    """Extract core competencies"""
    competencies = []
    
    comp_section = re.search(r'Core competencies[^:]*:\s*(.+?)(?:Values:|Pertinent|Link to Other|$)', text, re.DOTALL | re.IGNORECASE)
    
    if comp_section:
        comp_text = comp_section.group(1)
        # Known competency names
        known_competencies = [
            "Communication and Collaboration",
            "Critical Thinking and Problem Solving",
            "Creativity and Imagination",
            "Citizenship",
            "Digital Literacy",
            "Learning to Learn",
            "Self-Efficacy",
            "Self-efficacy"
        ]
        
        for comp in known_competencies:
            if comp.lower() in comp_text.lower():
                competencies.append(comp)
    
    return competencies


def extract_values(text):
    """Extract values from text"""
    values = []
    
    val_section = re.search(r'Values\s*[:\.]?\s*(.+?)(?:Pertinent|Link to Other|Core competencies|$)', text, re.DOTALL | re.IGNORECASE)
    
    if val_section:
        val_text = val_section.group(1)
        # Known values
        known_values = [
            "Love", "Responsibility", "Respect", "Unity", 
            "Peace", "Patriotism", "Social Justice", "Integrity"
        ]
        
        for val in known_values:
            if val.lower() in val_text.lower():
                values.append(val)
    
    return values


def extract_pcis(text):
    """Extract Pertinent and Contemporary Issues"""
    pcis = []
    
    pci_section = re.search(r'Pertinent and Contemporary Issues[^:]*:\s*(.+?)(?:Link to Other|Values:|Core competencies|$)', text, re.DOTALL | re.IGNORECASE)
    
    if pci_section:
        pci_text = pci_section.group(1)
        # Known PCIs
        known_pcis = [
            "Environmental Education", "Safety and Security", "Health Education",
            "Life Skills", "Financial Literacy", "Citizenship Education",
            "Gender Issues", "Social Cohesion", "Education for Sustainable Development",
            "Peace Education", "Effective Communication", "Cultural Heritage",
            "Human Rights", "Child Rights", "Animal Welfare"
        ]
        
        for pci in known_pcis:
            if pci.lower() in pci_text.lower():
                pcis.append(pci)
    
    return pcis


def extract_inquiry_questions(text):
    """Extract key inquiry questions"""
    questions = []
    
    iq_section = re.search(r'(?:Key Inquiry|Inquiry Question)[^:]*:\s*(.+?)(?:Core competencies|Values:|$)', text, re.DOTALL | re.IGNORECASE)
    
    if iq_section:
        iq_text = iq_section.group(1)
        # Find questions
        q_items = re.findall(r'[A-Z][^?]+\?', iq_text)
        
        for q in q_items:
            cleaned = clean_text(q)
            if cleaned and len(cleaned) > 10:
                questions.append(cleaned)
    
    return questions


def process_pdf(pdf_path, grade_name):
    """Process a single PDF file and extract all subjects"""
    print(f"\nProcessing: {pdf_path}")
    print(f"Grade: {grade_name}")
    
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    
    # List of subjects to look for
    all_subjects = [
        "Arabic", "French", "German", "Mandarin Chinese",
        "Christian Religious Education", "Islamic Religious Education", 
        "Hindu Religious Education", "Agriculture and Nutrition",
        "Pre-Technical Studies", "Creative Arts and Sports",
        "Indigenous Languages", "Visual Arts", "Performing Arts",
        "Business Studies", "Geography", "History and Citizenship",
        "Home Science", "Computer Science", "Biology", "Chemistry", 
        "Physics", "Mathematics", "English", "Kiswahili",
        "Literature in English", "Fasihi ya Kiswahili",
        "Music", "Theatre", "Film", "Physical Education",
        "Kenya Sign Language"
    ]
    
    extracted_data = {
        "grade": grade_name,
        "source_file": pdf_path,
        "subjects": []
    }
    
    # Find subject boundaries
    subject_pages = find_subject_boundaries(doc, all_subjects)
    print(f"Found {len(subject_pages)} subjects")
    
    for subject_name, pages in subject_pages.items():
        print(f"  - {subject_name}: starts at page {pages['start']}")
        
        # Extract text for this subject
        subject_text = extract_subject_text(doc, pages['start'])
        
        # Parse the curriculum structure
        strands = parse_strand_data(subject_text, subject_name)
        
        if strands:
            subject_data = {
                "name": subject_name,
                "strands": strands
            }
            extracted_data["subjects"].append(subject_data)
            
            # Print summary
            total_substrands = sum(len(s["substrands"]) for s in strands)
            total_slos = sum(len(ss["slos"]) for s in strands for ss in s["substrands"])
            print(f"    Strands: {len(strands)}, Substrands: {total_substrands}, SLOs: {total_slos}")
    
    doc.close()
    return extracted_data


def main():
    """Main extraction function"""
    print("=" * 70)
    print("CURRICULUM PDF EXTRACTOR")
    print("=" * 70)
    
    all_data = []
    
    for filename, info in PDF_FILES.items():
        if os.path.exists(info["path"]):
            data = process_pdf(info["path"], info["grade"])
            all_data.append(data)
        else:
            print(f"File not found: {info['path']}")
    
    # Save extracted data to JSON
    output_path = "/app/backend/extracted_curriculum_data.json"
    with open(output_path, "w") as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Extraction complete. Data saved to: {output_path}")
    print("=" * 70)
    
    return all_data


if __name__ == "__main__":
    main()
