"""
Extract Grade 10 curriculum data from PDFs for missing subjects:
- German (G103.pdf, page 253)
- Indigenous Language (G103.pdf, page 418)
- Mandarin (G10.pdf, page 90)
- Power Mechanics (G10.pdf, page 402)
"""

import fitz  # PyMuPDF
import re
import json
from datetime import datetime

def extract_text_from_pages(doc, start_page, end_page):
    """Extract text from a range of pages"""
    text = ""
    for page_num in range(start_page, min(end_page, len(doc))):
        text += doc[page_num].get_text() + "\n\n"
    return text

def extract_strands_and_substrands(text, subject_name):
    """Extract strands, sub-strands, SLOs, and learning activities"""
    strands = []
    
    # Different patterns for strand headers
    strand_patterns = [
        r'STRAND\s+(\d+\.?\d*)[:\s]*([A-Z][A-Z\s\-&,]+?)(?=\n|Sub[\s-]?strand)',
        r'(\d+\.0)\s+([A-Z][A-Z\s\-&,]+?)(?=\n)',
        r'STRAND\s*:\s*([A-Z][A-Z\s\-&,]+)',
    ]
    
    # Find all strands
    strand_matches = []
    for pattern in strand_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        if matches:
            strand_matches = matches
            break
    
    if not strand_matches:
        print(f"  Warning: No strands found for {subject_name}")
        return strands
    
    for i, match in enumerate(strand_matches):
        if len(match.groups()) >= 2:
            strand_num = match.group(1).strip()
            strand_name = match.group(2).strip()
        else:
            strand_num = str(i + 1)
            strand_name = match.group(1).strip()
        
        # Clean strand name
        strand_name = re.sub(r'\s+', ' ', strand_name).strip()
        if len(strand_name) < 3 or len(strand_name) > 100:
            continue
        
        # Get text for this strand (until next strand)
        start_pos = match.end()
        end_pos = strand_matches[i+1].start() if i+1 < len(strand_matches) else len(text)
        strand_text = text[start_pos:end_pos]
        
        # Extract sub-strands
        sub_strands = extract_substrands(strand_text, strand_num)
        
        if sub_strands:  # Only add strand if it has sub-strands
            strands.append({
                "strand_name": f"{strand_num} {strand_name}",
                "sub_strands": sub_strands
            })
    
    return strands

def extract_substrands(strand_text, strand_num):
    """Extract sub-strands from strand text"""
    sub_strands = []
    
    # Sub-strand patterns
    substrand_patterns = [
        r'Sub[\s-]?strand\s+(\d+\.\d+)[:\s]*([^\n]+)',
        r'(\d+\.\d+)\s+([A-Za-z][^:\n]{5,60})(?::|$)',
    ]
    
    substrand_matches = []
    for pattern in substrand_patterns:
        matches = list(re.finditer(pattern, strand_text, re.IGNORECASE | re.MULTILINE))
        if matches:
            substrand_matches = matches
            break
    
    for j, ss_match in enumerate(substrand_matches):
        ss_num = ss_match.group(1).strip()
        ss_name = ss_match.group(2).strip()
        
        # Clean substrand name
        ss_name = re.sub(r'\s+', ' ', ss_name).strip()
        if len(ss_name) < 3 or len(ss_name) > 100:
            continue
        
        # Get substrand text
        ss_start = ss_match.end()
        ss_end = substrand_matches[j+1].start() if j+1 < len(substrand_matches) else len(strand_text)
        ss_text = strand_text[ss_start:ss_end]
        
        # Extract SLOs
        slos = extract_slos(ss_text)
        
        # Extract learning activities
        activities = extract_learning_activities(ss_text)
        
        # Extract key inquiry questions
        inquiry_questions = extract_inquiry_questions(ss_text)
        
        # Extract competency mappings
        competency_mappings = extract_competency_mappings(ss_text)
        
        sub_strands.append({
            "sub_strand_name": f"{ss_num} {ss_name}",
            "specific_learning_outcomes": slos,
            "learning_activities": activities,
            "key_inquiry_questions": inquiry_questions,
            "competency_mappings": competency_mappings
        })
    
    return sub_strands

def extract_slos(text):
    """Extract Specific Learning Outcomes"""
    slos = []
    
    # Look for SLO section
    slo_section_match = re.search(r'Specific\s+Learning\s+Outcomes?(.+?)(?=Suggested\s+Learning|Key\s+Inquiry|Core\s+Competenc|$)', text, re.IGNORECASE | re.DOTALL)
    
    if slo_section_match:
        slo_text = slo_section_match.group(1)
        
        # Extract individual SLOs (a), b), c), etc. or numbered)
        slo_patterns = [
            r'([a-h])\)\s*([^a-h\)]+?)(?=[a-h]\)|$)',
            r'(\d+)\.\s*([^\d\.]+?)(?=\d+\.|$)',
        ]
        
        for pattern in slo_patterns:
            matches = re.findall(pattern, slo_text, re.DOTALL)
            if matches:
                for letter, content in matches:
                    content = re.sub(r'\s+', ' ', content).strip()
                    if len(content) > 10 and len(content) < 500:
                        slos.append(content)
                break
    
    # If no SLOs found, try alternative extraction
    if not slos:
        alt_matches = re.findall(r'By the end of[^,]+,\s*the\s+learner\s+should\s+be\s+able\s+to[:\s]*([^\.]+\.)', text, re.IGNORECASE)
        slos.extend([re.sub(r'\s+', ' ', m).strip() for m in alt_matches if len(m) > 10])
    
    return slos[:10]  # Limit to 10 SLOs per substrand

def extract_learning_activities(text):
    """Extract Suggested Learning Experiences/Activities"""
    activities = []
    
    # Look for activities section
    activities_match = re.search(r'Suggested\s+Learning\s+(?:Experiences?|Activities?)(.+?)(?=Key\s+Inquiry|Core\s+Competenc|Assessment|$)', text, re.IGNORECASE | re.DOTALL)
    
    if activities_match:
        activities_text = activities_match.group(1)
        
        # Split by bullet points, numbers, or newlines
        items = re.split(r'[\n•\-]\s*(?=[A-Z])', activities_text)
        
        for item in items:
            item = re.sub(r'\s+', ' ', item).strip()
            if len(item) > 15 and len(item) < 500:
                # Clean up the item
                item = re.sub(r'^[\d\.\)\s]+', '', item).strip()
                if item:
                    activities.append(item)
    
    return activities[:15]  # Limit to 15 activities

def extract_inquiry_questions(text):
    """Extract Key Inquiry Questions"""
    questions = []
    
    inquiry_match = re.search(r'Key\s+Inquiry\s+Questions?(.+?)(?=Core\s+Competenc|Values|Assessment|$)', text, re.IGNORECASE | re.DOTALL)
    
    if inquiry_match:
        inquiry_text = inquiry_match.group(1)
        
        # Find questions (ending with ?)
        q_matches = re.findall(r'([^?]+\?)', inquiry_text)
        for q in q_matches:
            q = re.sub(r'\s+', ' ', q).strip()
            if len(q) > 10 and len(q) < 300:
                questions.append(q)
    
    return questions[:5]

def extract_competency_mappings(text):
    """Extract Core Competencies, Values, and PCIs"""
    mappings = {
        "core_competencies": "",
        "values": "",
        "pcis": ""
    }
    
    # Core competencies
    cc_match = re.search(r'Core\s+Competenc(?:y|ies)[:\s]*(.+?)(?=Values|PCIs|Link|Assessment|$)', text, re.IGNORECASE | re.DOTALL)
    if cc_match:
        mappings["core_competencies"] = re.sub(r'\s+', ' ', cc_match.group(1)).strip()[:500]
    
    # Values
    val_match = re.search(r'Values[:\s]*(.+?)(?=PCIs|Link|Assessment|Core|$)', text, re.IGNORECASE | re.DOTALL)
    if val_match:
        mappings["values"] = re.sub(r'\s+', ' ', val_match.group(1)).strip()[:500]
    
    # PCIs
    pci_match = re.search(r'PCIs[:\s]*(.+?)(?=Link|Assessment|Core|Values|$)', text, re.IGNORECASE | re.DOTALL)
    if pci_match:
        mappings["pcis"] = re.sub(r'\s+', ' ', pci_match.group(1)).strip()[:500]
    
    return mappings

def extract_subject(pdf_path, start_page, end_page, subject_name, grade="Grade 10"):
    """Extract complete curriculum data for a subject"""
    print(f"\nExtracting {subject_name} from {pdf_path}")
    print(f"  Pages: {start_page + 1} to {end_page}")
    
    doc = fitz.open(pdf_path)
    text = extract_text_from_pages(doc, start_page, end_page)
    doc.close()
    
    strands = extract_strands_and_substrands(text, subject_name)
    
    # Count statistics
    total_substrands = sum(len(s["sub_strands"]) for s in strands)
    total_slos = sum(sum(len(ss["specific_learning_outcomes"]) for ss in s["sub_strands"]) for s in strands)
    total_activities = sum(sum(len(ss["learning_activities"]) for ss in s["sub_strands"]) for s in strands)
    
    print(f"  Strands: {len(strands)}")
    print(f"  Sub-strands: {total_substrands}")
    print(f"  SLOs: {total_slos}")
    print(f"  Learning Activities: {total_activities}")
    
    return {
        "subject_name": subject_name,
        "grade": grade,
        "strands": strands
    }

def main():
    subjects_config = [
        {
            "name": "German",
            "pdf": "pdfs/new_uploads/G103.pdf",
            "start_page": 252,
            "end_page": 417
        },
        {
            "name": "Indigenous Language",
            "pdf": "pdfs/new_uploads/G103.pdf",
            "start_page": 417,
            "end_page": 607
        },
        {
            "name": "Mandarin",
            "pdf": "pdfs/new_uploads/G10.pdf",
            "start_page": 89,
            "end_page": 401
        },
        {
            "name": "Power Mechanics",
            "pdf": "pdfs/new_uploads/G10.pdf",
            "start_page": 401,
            "end_page": 582
        }
    ]
    
    all_subjects = []
    
    for config in subjects_config:
        subject_data = extract_subject(
            config["pdf"],
            config["start_page"],
            config["end_page"],
            config["name"]
        )
        all_subjects.append(subject_data)
    
    # Save to JSON
    output = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "subjects": all_subjects
    }
    
    output_file = "extracted_grade10_missing_subjects.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Extraction complete! Saved to {output_file}")
    print(f"Total subjects: {len(all_subjects)}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    for subject in all_subjects:
        strands = len(subject["strands"])
        substrands = sum(len(s["sub_strands"]) for s in subject["strands"])
        slos = sum(sum(len(ss["specific_learning_outcomes"]) for ss in s["sub_strands"]) for s in subject["strands"])
        activities = sum(sum(len(ss["learning_activities"]) for ss in s["sub_strands"]) for s in subject["strands"])
        
        status = "COMPLETE" if strands > 0 and substrands > 0 and slos > 0 else "INCOMPLETE"
        print(f"  {subject['subject_name']}: {strands} strands, {substrands} sub-strands, {slos} SLOs, {activities} activities - {status}")

if __name__ == "__main__":
    main()
