"""
Grade 10 Curriculum Extraction - Improved version
Handles tabular PDF structure with columns:
- Strand
- Sub Strand  
- Specific Learning Outcomes
- Suggested Learning Experiences
- Key Inquiry Questions
"""

import fitz
import re
import json
from datetime import datetime

def extract_tabular_curriculum(pdf_path, start_page, end_page, subject_name):
    """Extract curriculum from tabular PDF format"""
    print(f"\nExtracting {subject_name}")
    print(f"  Source: {pdf_path}, pages {start_page + 1}-{end_page}")
    
    doc = fitz.open(pdf_path)
    
    # Collect all text
    full_text = ""
    for page_num in range(start_page, min(end_page, len(doc))):
        full_text += doc[page_num].get_text() + "\n"
    doc.close()
    
    strands = []
    current_strand = None
    current_substrand = None
    
    # Split into sections by "By the end of the sub strand" which marks SLO sections
    slo_sections = re.split(r'(By the end of the sub[\s-]?strand[,\s]*the learner should be able to:)', full_text, flags=re.IGNORECASE)
    
    print(f"  Found {len(slo_sections)//2} SLO sections")
    
    # Process each SLO section
    for i in range(1, len(slo_sections), 2):
        if i >= len(slo_sections):
            break
            
        # Get the text before this SLO marker (contains strand/substrand info)
        pre_text = slo_sections[i-1] if i > 0 else ""
        # Get the SLO content
        slo_marker = slo_sections[i]
        slo_content = slo_sections[i+1] if i+1 < len(slo_sections) else ""
        
        # Find strand number (e.g., 1.1, 1.2, 2.1)
        strand_match = re.search(r'(\d+\.\d+)\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\n|\s+\d+\.\d+\.\d+)', pre_text[-500:])
        if strand_match:
            strand_num = strand_match.group(1)
            strand_name = strand_match.group(2).strip()
            
            # Check if this is a new strand
            if current_strand is None or not current_strand['strand_name'].startswith(strand_num):
                if current_strand and current_strand['sub_strands']:
                    strands.append(current_strand)
                current_strand = {
                    'strand_name': f"{strand_num} {strand_name}",
                    'sub_strands': []
                }
        
        # Find substrand number (e.g., 1.1.1, 1.1.2)
        substrand_match = re.search(r'(\d+\.\d+\.\d+)\s+([A-Za-z][^\n]+?)(?:\s*\(\d+\s*lessons?\))?(?:\s*\n|$)', pre_text[-800:], re.IGNORECASE)
        if substrand_match:
            ss_num = substrand_match.group(1)
            ss_name = re.sub(r'\s+', ' ', substrand_match.group(2)).strip()
            
            # Extract SLOs (a), b), c), d) patterns
            slos = []
            slo_text = slo_content[:2000]  # Look in first 2000 chars
            slo_items = re.findall(r'[a-h]\)\s*([^a-h\)]+?)(?=[a-h]\)|The learner is guided|$)', slo_text, re.DOTALL)
            for item in slo_items:
                item = re.sub(r'\s+', ' ', item).strip().rstrip(',.')
                if len(item) > 10 and len(item) < 500:
                    slos.append(item)
            
            # Extract learning activities (after "The learner is guided to:")
            activities = []
            activity_match = re.search(r'The learner is guided to:\s*(.+?)(?=(?:\d+\.\s*(?:How|Why|What))|Core [Cc]ompetenc|Values:|$)', slo_content, re.DOTALL | re.IGNORECASE)
            if activity_match:
                activity_text = activity_match.group(1)
                # Split by bullet points
                activity_items = re.findall(r'[•\-]\s*([^\n•\-]+)', activity_text)
                for item in activity_items:
                    item = re.sub(r'\s+', ' ', item).strip()
                    if len(item) > 15 and len(item) < 500:
                        activities.append(item)
            
            # Extract inquiry questions
            questions = []
            q_match = re.search(r'(\d+\.\s*(?:How|Why|What|When|Where|Which)[^?]+\?)', slo_content, re.IGNORECASE)
            if q_match:
                questions.append(q_match.group(1).strip())
            # Find more questions
            more_qs = re.findall(r'\d+\.\s*([A-Z][^?]{10,100}\?)', slo_content)
            questions.extend(more_qs[:3])
            
            # Extract competencies
            competencies = ""
            comp_match = re.search(r'Core [Cc]ompetenc(?:y|ies)[^:]*:\s*(.+?)(?=Values:|PCIs:|Pertinent|Link to|$)', slo_content, re.DOTALL | re.IGNORECASE)
            if comp_match:
                competencies = re.sub(r'\s+', ' ', comp_match.group(1)).strip()[:500]
            
            # Extract values
            values = ""
            val_match = re.search(r'Values:\s*(.+?)(?=PCIs:|Pertinent|Link to|Core|$)', slo_content, re.DOTALL | re.IGNORECASE)
            if val_match:
                values = re.sub(r'\s+', ' ', val_match.group(1)).strip()[:500]
            
            # Extract PCIs
            pcis = ""
            pci_match = re.search(r'(?:PCIs|Pertinent and Contemporary Issues)[^:]*:\s*(.+?)(?=Link to|Assessment|Core|Values|$)', slo_content, re.DOTALL | re.IGNORECASE)
            if pci_match:
                pcis = re.sub(r'\s+', ' ', pci_match.group(1)).strip()[:500]
            
            if current_strand:
                current_strand['sub_strands'].append({
                    'sub_strand_name': f"{ss_num} {ss_name}",
                    'specific_learning_outcomes': slos,
                    'learning_activities': activities,
                    'key_inquiry_questions': questions[:3],
                    'competency_mappings': {
                        'core_competencies': competencies,
                        'values': values,
                        'pcis': pcis
                    }
                })
    
    # Don't forget the last strand
    if current_strand and current_strand['sub_strands']:
        strands.append(current_strand)
    
    # Deduplicate strands by merging same strand numbers
    merged_strands = {}
    for strand in strands:
        strand_num = strand['strand_name'].split()[0] if strand['strand_name'] else ""
        if strand_num in merged_strands:
            merged_strands[strand_num]['sub_strands'].extend(strand['sub_strands'])
        else:
            merged_strands[strand_num] = strand
    
    strands = list(merged_strands.values())
    
    # Remove duplicate substrands
    for strand in strands:
        seen = set()
        unique_subs = []
        for ss in strand['sub_strands']:
            ss_key = ss['sub_strand_name']
            if ss_key not in seen:
                seen.add(ss_key)
                unique_subs.append(ss)
        strand['sub_strands'] = unique_subs
    
    # Stats
    total_substrands = sum(len(s['sub_strands']) for s in strands)
    total_slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in s['sub_strands']) for s in strands)
    total_activities = sum(sum(len(ss['learning_activities']) for ss in s['sub_strands']) for s in strands)
    
    print(f"  Results: {len(strands)} strands, {total_substrands} sub-strands, {total_slos} SLOs, {total_activities} activities")
    
    return {
        'subject_name': subject_name,
        'grade': 'Grade 10',
        'strands': strands
    }


def extract_power_mechanics(pdf_path, start_page, end_page):
    """Special extraction for Power Mechanics - different structure"""
    print(f"\nExtracting Power Mechanics")
    print(f"  Source: {pdf_path}, pages {start_page + 1}-{end_page}")
    
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(start_page, min(end_page, len(doc))):
        full_text += doc[page_num].get_text() + "\n"
    doc.close()
    
    strands = []
    
    # Power Mechanics uses STRAND pattern
    strand_pattern = re.compile(r'STRAND\s+(\d+)[:\s]+([A-Z][A-Z\s\-&]+?)(?=\n|Sub[\s-]?strand)', re.IGNORECASE)
    strand_matches = list(strand_pattern.finditer(full_text))
    
    print(f"  Found {len(strand_matches)} strand markers")
    
    for i, match in enumerate(strand_matches):
        strand_num = match.group(1)
        strand_name = match.group(2).strip()
        
        # Get strand text
        start_pos = match.end()
        end_pos = strand_matches[i+1].start() if i+1 < len(strand_matches) else len(full_text)
        strand_text = full_text[start_pos:end_pos]
        
        sub_strands = []
        
        # Find sub-strands
        substrand_pattern = re.compile(r'Sub[\s-]?strand\s+(\d+\.\d+)[:\s]*([^\n]+)', re.IGNORECASE)
        ss_matches = list(substrand_pattern.finditer(strand_text))
        
        for j, ss_match in enumerate(ss_matches):
            ss_num = ss_match.group(1)
            ss_name = ss_match.group(2).strip()
            
            # Get substrand text
            ss_start = ss_match.end()
            ss_end = ss_matches[j+1].start() if j+1 < len(ss_matches) else len(strand_text)
            ss_text = strand_text[ss_start:ss_end]
            
            # Extract SLOs
            slos = []
            slo_match = re.search(r'should be able to:\s*(.+?)(?=Suggested Learning|The learner|$)', ss_text, re.DOTALL | re.IGNORECASE)
            if slo_match:
                slo_text = slo_match.group(1)
                slo_items = re.findall(r'[a-h]\)\s*([^a-h\)]+?)(?=[a-h]\)|$)', slo_text, re.DOTALL)
                for item in slo_items:
                    item = re.sub(r'\s+', ' ', item).strip().rstrip(',.')
                    if len(item) > 10:
                        slos.append(item)
            
            # Extract activities
            activities = []
            act_match = re.search(r'(?:Suggested Learning|The learner is guided)[^:]*:\s*(.+?)(?=Key Inquiry|Assessment|Core Comp|$)', ss_text, re.DOTALL | re.IGNORECASE)
            if act_match:
                act_text = act_match.group(1)
                act_items = re.findall(r'[•\-]\s*([^\n•\-]+)', act_text)
                if not act_items:
                    act_items = re.split(r'\n\s*', act_text)
                for item in act_items:
                    item = re.sub(r'\s+', ' ', item).strip()
                    if len(item) > 15:
                        activities.append(item)
            
            sub_strands.append({
                'sub_strand_name': f"{strand_num}.{ss_num} {ss_name}",
                'specific_learning_outcomes': slos,
                'learning_activities': activities[:10],
                'key_inquiry_questions': [],
                'competency_mappings': {}
            })
        
        if sub_strands:
            strands.append({
                'strand_name': f"{strand_num} {strand_name}",
                'sub_strands': sub_strands
            })
    
    total_subs = sum(len(s['sub_strands']) for s in strands)
    total_slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in s['sub_strands']) for s in strands)
    total_acts = sum(sum(len(ss['learning_activities']) for ss in s['sub_strands']) for s in strands)
    
    print(f"  Results: {len(strands)} strands, {total_subs} sub-strands, {total_slos} SLOs, {total_acts} activities")
    
    return {
        'subject_name': 'Power Mechanics',
        'grade': 'Grade 10',
        'strands': strands
    }


def main():
    all_subjects = []
    
    # Extract German
    german = extract_tabular_curriculum('pdfs/new_uploads/G103.pdf', 252, 417, 'German')
    all_subjects.append(german)
    
    # Extract Indigenous Language
    indigenous = extract_tabular_curriculum('pdfs/new_uploads/G103.pdf', 417, 607, 'Indigenous Language')
    all_subjects.append(indigenous)
    
    # Extract Mandarin
    mandarin = extract_tabular_curriculum('pdfs/new_uploads/G10.pdf', 89, 401, 'Mandarin')
    all_subjects.append(mandarin)
    
    # Extract Power Mechanics (different format)
    power_mech = extract_power_mechanics('pdfs/new_uploads/G10.pdf', 401, 582)
    all_subjects.append(power_mech)
    
    # Save to JSON
    output = {
        'extraction_date': datetime.now().strftime('%Y-%m-%d'),
        'subjects': all_subjects
    }
    
    with open('extracted_grade10_missing_subjects.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETE")
    print("="*70)
    
    for subject in all_subjects:
        strands = len(subject['strands'])
        substrands = sum(len(s['sub_strands']) for s in subject['strands'])
        slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in s['sub_strands']) for s in subject['strands'])
        activities = sum(sum(len(ss['learning_activities']) for ss in s['sub_strands']) for s in subject['strands'])
        
        status = "COMPLETE" if strands > 0 and substrands > 0 and slos > 0 else "NEEDS REVIEW"
        print(f"\n{subject['subject_name']}:")
        print(f"  Strands: {strands}")
        print(f"  Sub-strands: {substrands}")
        print(f"  SLOs: {slos}")
        print(f"  Learning Activities: {activities}")
        print(f"  Status: {status}")


if __name__ == "__main__":
    main()
