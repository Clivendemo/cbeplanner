"""
Grade 10 Missing Subjects - Final Extraction Script
Extracts: German, Indigenous Language, Mandarin, Power Mechanics
"""

import fitz
import re
import json
from datetime import datetime

def extract_slos_improved(text):
    """Extract SLOs handling multi-line items"""
    slos = []
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    pattern = r'([a-h])\)\s*(.+?)(?=\s*[a-h]\)|The learner|Core [Cc]omp|Values:|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for letter, content in matches:
        content = content.strip().rstrip(',.')
        if 10 < len(content) < 400:
            slos.append(content)
    return slos

def extract_activities_improved(text):
    """Extract learning activities"""
    activities = []
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    match = re.search(r'The learner is guided to:\s*(.+?)(?=\d+\.\s*(?:How|Why|What)|Core\s+[Cc]omp|Values:|PCIs|$)', text, re.IGNORECASE)
    if match:
        act_text = match.group(1)
        items = re.split(r'[•\-]\s*', act_text)
        for item in items:
            item = item.strip().rstrip(',.')
            if 15 < len(item) < 400:
                activities.append(item)
    return activities

def extract_standard_subject(pdf_path, start_page, end_page, subject_name):
    """Extract subjects with STRAND headers (German, Mandarin, Power Mechanics)"""
    print(f"\nExtracting: {subject_name}")
    
    doc = fitz.open(pdf_path)
    pages_text = []
    for page_num in range(start_page, min(end_page, len(doc))):
        pages_text.append(doc[page_num].get_text())
    doc.close()
    
    strands = []
    current_strand = None
    
    for page_text in pages_text:
        normalized = re.sub(r'\n+', ' ', page_text)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Check for STRAND header
        strand_match = re.search(r'STRAND\s+(\d+\.?\d*)[:\s]+([A-Z][A-Z\s\-&]+?)(?=Strand|Sub|Specific|\d+\.\d+)', normalized, re.IGNORECASE)
        if strand_match:
            if current_strand and current_strand['sub_strands']:
                strands.append(current_strand)
            
            strand_num = strand_match.group(1)
            strand_name = strand_match.group(2).strip()
            current_strand = {
                'strand_name': f"{strand_num} {strand_name}",
                'sub_strands': []
            }
        
        # Check for sub-strand with SLOs
        if 'should be able to:' in normalized.lower() or 'should be able to' in normalized.lower():
            ss_match = re.search(r'(\d+\.\d+)\s+([A-Za-z][^(]+?)(?:\s*\(\d+\s*lessons?\))?\s*(?:by the end|$)', normalized, re.IGNORECASE)
            
            if ss_match and current_strand:
                ss_num = ss_match.group(1)
                ss_name = ss_match.group(2).strip()
                
                slo_start = normalized.lower().find('should be able to:')
                if slo_start == -1:
                    slo_start = normalized.lower().find('should be able to')
                
                slo_text = normalized[slo_start:slo_start+2000]
                slos = extract_slos_improved(slo_text)
                activities = extract_activities_improved(normalized)
                questions = re.findall(r'(?:How|Why|What|When|Which)\s+[^?]+\?', normalized)
                questions = [q.strip() for q in questions[:3] if 10 < len(q) < 200]
                
                current_strand['sub_strands'].append({
                    'sub_strand_name': f"{ss_num} {ss_name}",
                    'specific_learning_outcomes': slos,
                    'learning_activities': activities[:10],
                    'key_inquiry_questions': questions,
                    'competency_mappings': {}
                })
    
    if current_strand and current_strand['sub_strands']:
        strands.append(current_strand)
    
    # Merge and dedupe
    merged = {}
    for strand in strands:
        key = strand['strand_name'].split()[0]
        if key in merged:
            merged[key]['sub_strands'].extend(strand['sub_strands'])
        else:
            merged[key] = strand
    
    strands = list(merged.values())
    for strand in strands:
        seen = set()
        unique = []
        for ss in strand['sub_strands']:
            if ss['sub_strand_name'] not in seen:
                seen.add(ss['sub_strand_name'])
                unique.append(ss)
        strand['sub_strands'] = unique
    
    total_ss = sum(len(s['sub_strands']) for s in strands)
    total_slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in s['sub_strands']) for s in strands)
    total_acts = sum(sum(len(ss['learning_activities']) for ss in s['sub_strands']) for s in strands)
    print(f"  {len(strands)} strands, {total_ss} sub-strands, {total_slos} SLOs, {total_acts} activities")
    
    return {'subject_name': subject_name, 'grade': 'Grade 10', 'strands': strands}

def extract_indigenous_language(pdf_path, start_page, end_page):
    """Special extraction for Indigenous Language (tabular format)"""
    print(f"\nExtracting: Indigenous Language")
    
    doc = fitz.open(pdf_path)
    pages_text = []
    for page_num in range(start_page, min(end_page, len(doc))):
        pages_text.append(doc[page_num].get_text())
    doc.close()
    
    strands = {}
    strand_names = {
        '1.1': 'Listening and Speaking', '1.2': 'Reading', '1.3': 'Writing',
        '2.1': 'Listening and Speaking', '2.2': 'Reading', '2.3': 'Writing',
        '3.1': 'Listening and Speaking', '3.2': 'Reading', '3.3': 'Writing'
    }
    
    for page_text in pages_text:
        normalized = re.sub(r'\n+', ' ', page_text)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        ss_match = re.search(r'(\d+\.\d+\.\d+)\s+([A-Za-z][^(]+?)(?:\s*\(\d+\s*lessons?\))', normalized)
        
        if ss_match and 'should be able to' in normalized.lower():
            ss_num = ss_match.group(1)
            ss_name = ss_match.group(2).strip()
            strand_num = '.'.join(ss_num.split('.')[:2])
            strand_name = strand_names.get(strand_num, f"Strand {strand_num}")
            
            if strand_num not in strands:
                strands[strand_num] = {'strand_name': f"{strand_num} {strand_name}", 'sub_strands': []}
            
            slo_start = normalized.lower().find('should be able to:')
            if slo_start == -1:
                slo_start = normalized.lower().find('should be able to')
            
            if slo_start >= 0:
                slo_text = normalized[slo_start:slo_start+1500]
                slos = extract_slos_improved(slo_text)
                activities = extract_activities_improved(normalized)
                questions = re.findall(r'(?:How|Why|What|When)\s+[^?]+\?', normalized)
                questions = [q.strip() for q in questions[:3] if 10 < len(q) < 200]
                
                strands[strand_num]['sub_strands'].append({
                    'sub_strand_name': f"{ss_num} {ss_name}",
                    'specific_learning_outcomes': slos,
                    'learning_activities': activities[:10],
                    'key_inquiry_questions': questions,
                    'competency_mappings': {}
                })
    
    strand_list = []
    for strand_num in sorted(strands.keys()):
        strand = strands[strand_num]
        seen = set()
        unique_subs = []
        for ss in strand['sub_strands']:
            if ss['sub_strand_name'] not in seen:
                seen.add(ss['sub_strand_name'])
                unique_subs.append(ss)
        strand['sub_strands'] = unique_subs
        if unique_subs:
            strand_list.append(strand)
    
    total_ss = sum(len(s['sub_strands']) for s in strand_list)
    total_slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in s['sub_strands']) for s in strand_list)
    total_acts = sum(sum(len(ss['learning_activities']) for ss in s['sub_strands']) for s in strand_list)
    print(f"  {len(strand_list)} strands, {total_ss} sub-strands, {total_slos} SLOs, {total_acts} activities")
    
    return {'subject_name': 'Indigenous Language', 'grade': 'Grade 10', 'strands': strand_list}

def main():
    all_subjects = []
    
    # German
    german = extract_standard_subject('pdfs/new_uploads/G103.pdf', 253, 417, 'German')
    all_subjects.append(german)
    
    # Indigenous Language (special format)
    indigenous = extract_indigenous_language('pdfs/new_uploads/G103.pdf', 420, 607)
    all_subjects.append(indigenous)
    
    # Mandarin
    mandarin = extract_standard_subject('pdfs/new_uploads/G10.pdf', 95, 401, 'Mandarin')
    all_subjects.append(mandarin)
    
    # Power Mechanics
    power_mech = extract_standard_subject('pdfs/new_uploads/G10.pdf', 409, 582, 'Power Mechanics')
    all_subjects.append(power_mech)
    
    # Save
    output = {'extraction_date': datetime.now().strftime('%Y-%m-%d'), 'subjects': all_subjects}
    with open('extracted_grade10_missing_subjects.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETE - SUMMARY")
    print("="*70)
    
    for s in all_subjects:
        strands = len(s['strands'])
        subs = sum(len(st['sub_strands']) for st in s['strands'])
        slos = sum(sum(len(ss['specific_learning_outcomes']) for ss in st['sub_strands']) for st in s['strands'])
        acts = sum(sum(len(ss['learning_activities']) for ss in st['sub_strands']) for st in s['strands'])
        status = "COMPLETE" if strands > 0 and subs > 0 and slos > 0 else "INCOMPLETE"
        print(f"\n{s['subject_name']}:")
        print(f"  Strands: {strands}")
        print(f"  Sub-strands: {subs}")
        print(f"  SLOs: {slos}")
        print(f"  Learning Activities: {acts}")
        print(f"  Status: {status}")
    
    print(f"\nSaved to: extracted_grade10_missing_subjects.json")

if __name__ == "__main__":
    main()
